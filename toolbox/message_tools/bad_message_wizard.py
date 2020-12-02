import base64
import json
import math
from contextlib import suppress
from json import JSONDecodeError

import requests
import re
from termcolor import colored

from toolbox.config import Config

ITEMS_PER_PAGE = 20


def main():
    show_splash()

    actions = (
        {'description': 'List bad messages', 'action': show_bad_message_list},
        {'description': 'Get bad message from hash', 'action': show_bad_message_metadata},
        {'description': 'Get quarantined messages', 'action': show_quarantined_messages},
        {'description': 'Quarantine all bad messages', 'action': show_quarantine_all_bad_messages},
        {'description': 'Reset bad message cache', 'action': reset_bad_message_cache},
        {'description': 'Filter bad messages', 'action': filter_bad_messages }
    )

    while True:

        #input(f'press {colored("ENTER", "cyan")} to continue')
        print('')
        print(colored('Actions:', 'cyan', attrs=['underline']))

        for index, action in enumerate(actions, 1):
            print(f'  {colored(f"{index}.", "cyan")} {action["description"]}')
        print('')

        raw_selection = input(colored('Choose an action: ', 'cyan'))
        valid_selection = validate_integer_input_range(raw_selection, 1, len(actions))

        if not valid_selection:
            continue
        else:
            actions[valid_selection - 1]['action']()


def get_quarantined_message_list():
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/skippedmessages')
    response.raise_for_status()
    return response.json()


def pretty_print_quarantined_message(message_hash, metadata, formatted_payload):
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print(colored('Message Hash: ', 'green'), message_hash)
    print(colored('Reports: ', 'green'))

    for index, report in enumerate(metadata, 1):
        print(f"  {colored(index, 'blue')}:  ")
        for k, v in report.items():
            print(colored(f'    {k}: ', 'green'), v)

    print(colored('Message Payload: ', 'green'), formatted_payload)
    print(colored('-------------------------------------------------------------------------------------', 'green'))


def show_all_quarantined_messages(quarantined_messages):
    for index, (message_hash, metadata) in enumerate(quarantined_messages.items(), 1):
        message_payload = base64.b64decode(metadata[0]['messagePayload']).decode()
        for report in metadata:
            report.pop('messagePayload')

        if len(quarantined_messages) > 1:
            print(f'  {colored(index, "blue")}:')

        # Try to JSON decode it, otherwise default to bare un-formatted text
        with suppress(JSONDecodeError):
            pretty_print_quarantined_message(message_hash, metadata, json.dumps(json.loads(message_payload), indent=2))
            print('')
            continue

        pretty_print_quarantined_message(message_hash, metadata, message_payload)
        print('')


def show_quarantined_messages():
    quarantined_messages = get_quarantined_message_list()
    print('')
    print(colored(f'There are currently {len(quarantined_messages)} quarantined messages:', 'cyan'))
    print('')
    show_all_quarantined_messages(quarantined_messages)


def confirm_quarantine_all_bad_messages(bad_messages):
    print('')
    confirmation = input("Confirm by responding with '" +
                         colored(f"I confirm I wish to quarantine all {len(bad_messages)} bad messages", 'red') +
                         "' exactly: ")

    if confirmation == f'I confirm I wish to quarantine all {len(bad_messages)} bad messages':
        print('')
        print(colored(f'Confirmed, quarantining all {len(bad_messages)} messages', 'yellow'))
        for bad_message in bad_messages:
            quarantine_bad_message(bad_message)
        print(colored('Successfully quarantined all bad messages', 'green'))
        print('')
    else:
        print('')
        print(colored('Aborted', 'red'))
        print('')


def show_quarantine_all_bad_messages():
    bad_messages = get_bad_message_list()

    if not bad_messages:
        show_no_bad_messages()
        return

    print(colored(
        f'There are currently {len(bad_messages)} bad messages, continuing will quarantine them all', 'yellow'))
    print('')
    print(colored('1.', 'cyan'), 'Continue')
    print(colored('2.', 'cyan'), 'Cancel')
    print('')

    raw_selection = input(colored('Choose an action: ', 'cyan'))
    valid_selection = validate_integer_input_range(raw_selection, 1, 2)

    if not valid_selection:
        return

    elif valid_selection == 1:
        confirm_quarantine_all_bad_messages(bad_messages)
    else:
        print('')
        print(colored('Aborted', 'red'))
        print('')


def confirm_quarantine_bad_message(message_hash):
    confirmation = input(f'Confirm you want to quarantine the message by responding "{colored("yes", "cyan")}": ')

    if confirmation == 'yes':
        quarantine_bad_message(message_hash)
        print('')
        print(colored(f'Quarantining {message_hash}', 'green'))
        print('')
        return True
    else:
        print(colored('Aborted', 'red'))
        return False


def quarantine_bad_message(message_hash):
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/skipmessage/{message_hash}')
    response.raise_for_status()


def reset_bad_message_cache():
    confirmation = input(f'Confirm you want to reset '
                         f'the exception manager cache by responding "{colored("yes", "cyan")}": ')
    if confirmation == 'yes':
        print(colored('Resetting bad message cache', 'yellow'))
        response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/reset')
        response.raise_for_status()
        print(colored('Successfully reset bad message cache', 'green'))
        print('')
    else:
        print(colored('Aborted', 'red'))
        print('')


def get_queue_names_and_counts(bad_messages):
    queue_name_dict = {}
    for bad_message in bad_messages:
        for queue in bad_message['affectedQueues']:
            if queue not in queue_name_dict:
                queue_name_dict[queue] = 1
            else:
                queue_name_dict[queue] += 1
    return queue_name_dict


def filter_bad_messages():
    filter_by_text = input(colored('Filter By Text: ', 'cyan'))

    all_message_summaries: list = get_message_summaries()

    all_message_summaries = filter_msgs(all_message_summaries, filter_by_text)

    if not all_message_summaries:
        print('No messages match your filter')
        return

    bad_message_summaries = get_bad_message_summaries(all_message_summaries)
    if not bad_message_summaries:
        show_no_bad_messages()
        return

    print(f'There are currently {len(bad_message_summaries)} bad messages matching your filter:')
    paginate_messages(bad_message_summaries)

    return


def filter_msgs(all_message_summaries, filter_by_text):
    filtered_msgs = []

    for msg in all_message_summaries:
        message_hash = msg['messageHash']
        message_metadata = get_bad_message_metadata(message_hash)

        for (k, v) in message_metadata[0].items():
            for item in v.values():
                if re.search(filter_by_text, str(item)):
                    if msg not in filtered_msgs:
                        filtered_msgs.append(msg)

    return filtered_msgs


def show_bad_message_list():
    all_message_summaries: list = get_message_summaries()

    bad_message_summaries = get_bad_message_summaries(all_message_summaries)
    if not bad_message_summaries:
        show_no_bad_messages()
        return

    bad_message_summaries = sort_bad_messages(bad_message_summaries)
    print('')
    print(f'There are currently {len(bad_message_summaries)} bad messages:')

    if len(bad_message_summaries) > ITEMS_PER_PAGE:
        paginate_messages(bad_message_summaries)
    else:
        display_messages(bad_message_summaries, 0)


def get_bad_message_summaries(all_message_summaries):
    bad_message_summaries = [summary for summary in all_message_summaries if not summary['quarantined']]
    return bad_message_summaries


def sort_bad_messages(bad_message_summaries):
    print(colored('Actions:', 'cyan', attrs=['underline']))
    print(colored('  1.', 'cyan'), 'View Bad Messages By First Seen')
    print(colored('  2.', 'cyan'), 'View Bad Messages By Last Seen')
    print(colored('  3.', 'cyan'), 'View Bad Messages Grouped By Queue')
    print('')

    raw_selection = input(colored('Choose an action: ', 'cyan'))
    valid_selection = validate_integer_input_range(raw_selection, 1, 3)
    group_by = 'firstSeen'

    if valid_selection == 2:
        group_by = 'lastSeen'
    elif valid_selection == 3:
        bad_message_summaries = group_messages_by_queue(bad_message_summaries)

    bad_message_summaries.sort(key=lambda message: message[group_by])
    return bad_message_summaries


def group_messages_by_queue(bad_message_summaries):
    bad_message_queue_counts = get_queue_names_and_counts(bad_message_summaries)
    column_widths = get_group_by_queue_widths(bad_message_queue_counts)

    print(column_widths["queueName"])
    print(column_widths["messageCount"])

    header = get_group_by_queue_headers(column_widths)
    print('')
    print(header)
    print(f'   ---|{"-" * (column_widths["queueName"] + 2)}'
          f'|{"-" * (column_widths["messageCount"] + 2)}')

    for i, (queue, q_count) in enumerate(bad_message_queue_counts.items(), 1):
        print(f'   {colored((str(i) + ".").ljust(3), color="cyan")}'
              f'| {queue} {" " * (column_widths["queueName"] - len(queue))}'
              f'| {q_count} ')
    queue_num = int(input('Select a queue by number: '))
    selected_queue = list(bad_message_queue_counts.keys())[queue_num - 1]
    bad_message_summaries = [summary for summary in bad_message_summaries if
                             selected_queue in summary['affectedQueues']]
    return bad_message_summaries


def get_group_by_queue_headers(column_widths):
    header = (f'      | {colored("Queue Name".ljust(column_widths["queueName"]), color="cyan")} '
              f'| {colored("Message Count".ljust(column_widths["messageCount"]), color="cyan")} ')
    return header


def get_group_by_queue_widths(bad_message_queue_counts):
    column_widths = {
        'queueName': max(len(queue_name) for queue_name in bad_message_queue_counts.keys()),
        'messageCount': max(queue_item for queue_item in bad_message_queue_counts.values()),
    }

    return column_widths


def display_messages(bad_message_summaries, start_index):
    pretty_print_bad_message_summaries(bad_message_summaries, start_index)
    print('')
    raw_selection = input(
        colored(
            f'Select a message ({start_index + 1} to {start_index + len(bad_message_summaries)}), Quarantine all with q or cancel with ENTER: ',
            'cyan'))
    print('')

    if raw_selection.lower() == 'q':
        confirm_quarantine_all_bad_messages(bad_message_summaries)
        return

    valid_selection = validate_integer_input_range(raw_selection, start_index + 1,
                                                   start_index + len(bad_message_summaries))
    if not valid_selection:
        return

    valid_selection = valid_selection - start_index
    message_hash = bad_message_summaries[valid_selection - 1]['messageHash']
    show_bad_message_metadata_for_hash(message_hash)
    in_message_context = True

    while in_message_context:
        in_message_context = show_bad_message_options(message_hash)


def paginate_messages(bad_message_summaries):
    start_index = 0
    page_num = 1
    page_max = math.ceil(len(bad_message_summaries) / ITEMS_PER_PAGE)

    while True:
        print(f'You are on page {str(page_num)} of {page_max}')

        display_messages(bad_message_summaries[start_index:start_index + ITEMS_PER_PAGE], start_index)
        page_num = input(colored(f"Please enter the page you would like to see 1 - {page_max} or ENTER to exit: ", color="cyan"))

        if not page_num:
            return

        validate_integer_input_range(page_num, 1, page_max)
        start_index = (int(page_num) * ITEMS_PER_PAGE) - ITEMS_PER_PAGE


def get_message_summaries():
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/badmessages/summary?minimumSeenCount=2')
    response.raise_for_status()
    return response.json()


def get_bad_message_list():
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/badmessages')
    response.raise_for_status()
    return response.json()


# Not current used but could be useful to display to actually bulk quarantine
def pretty_print_bad_message_summaries_with_exception_msg(bad_message_summaries, start_index):

    for msg in bad_message_summaries:
        message_hash = msg['messageHash']
        message_metadata = get_bad_message_metadata(message_hash)

        for (k, v) in message_metadata[0].items():
            if k == 'exceptionReport':
                for (key, value) in v.items():
                    if key == 'exceptionClass':
                        msg['exceptionClass'] = value
    print(bad_message_summaries)
    column_widths = {
        'exceptionClass':  max(len(str(summary['exceptionClass'])) for summary in bad_message_summaries),
        'firstSeen': max(len(str(summary['firstSeen'])) for summary in bad_message_summaries),
        'queues': max(len(', '.join(summary['affectedQueues'])) for summary in bad_message_summaries),
    }
    print('')
    header = (f'      | {colored("Exception Class".ljust(column_widths["exceptionClass"]), color="cyan")} '
              f'| {colored("First Seen".ljust(column_widths["firstSeen"]), color="cyan")} '
              f'| {colored("Queues".ljust(column_widths["queues"]), color="cyan")}')
    print(header)
    print(f'   ---|{"-" * (column_widths["exceptionClass"] + 2)}'
          f'|{"-" * (column_widths["firstSeen"] + 2)}'
          f'|{"-" * (column_widths["queues"] + 2)}')

    for index, summary in enumerate(bad_message_summaries, start_index + 1):
        print(f'   {colored((str(index) + ".").ljust(3), color="cyan")}'
              f'| {summary["exceptionClass"]} {" " * (column_widths["exceptionClass"] - len(summary["exceptionClass"]))}'
              f'| {summary["firstSeen"]} '
              f'| {", ".join(summary["affectedQueues"])}')


def pretty_print_bad_message_summaries(bad_message_summaries, start_index):
    column_widths = get_bad_msg_column_widths(bad_message_summaries)
    print('')
    header = get_headers_for_bad_msgs(column_widths)
    print(header)
    print(f'   ---|{"-" * (column_widths["messageHash"] + 2)}'
          f'|{"-" * (column_widths["firstSeen"] + 2)}'
          f'|{"-" * (column_widths["queues"] + 2)}')

    for index, summary in enumerate(bad_message_summaries, start_index + 1):
        print(f'   {colored((str(index) + ".").ljust(3), color="cyan")}'
              f'| {summary["messageHash"]} '
              f'| {summary["firstSeen"]} '
              f'| {", ".join(summary["affectedQueues"])}')


def get_headers_for_bad_msgs(column_widths):
    header = (f'      | {colored("Message Hash".ljust(column_widths["messageHash"]), color="cyan")} '
              f'| {colored("First Seen".ljust(column_widths["firstSeen"]), color="cyan")} '
              f'| {colored("Queues".ljust(column_widths["queues"]), color="cyan")}')
    return header


def get_bad_msg_column_widths(bad_message_summaries):
    column_widths = {
        'messageHash': len(bad_message_summaries[0]['messageHash']),
        'firstSeen': max(len(str(summary['firstSeen'])) for summary in bad_message_summaries),
        'queues': max(len(', '.join(summary['affectedQueues'])) for summary in bad_message_summaries),
    }
    return column_widths


def show_no_bad_messages():
    print('')
    print(colored('There are currently no bad messages known to the exception manager', 'green'))
    print('')


def pretty_print_bad_message(message_hash, body, message_format):
    print('')
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print(colored('Message Hash:', 'green'), message_hash)
    print(colored('Detected Format:', 'green'), message_format)
    print(colored('Body:', 'green'), body)
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print('')


def show_bad_message_body(message_hash):
    print(colored(f'Fetching bad message {message_hash}', 'yellow'))
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/peekmessage/{message_hash}')
    response.raise_for_status()

    # Try to JSON decode it, otherwise default to bare un-formatted text
    with suppress(JSONDecodeError):
        pretty_print_bad_message(message_hash, json.dumps(response.json(), indent=2), 'json')
        return
    pretty_print_bad_message(message_hash, response.text, 'text')


def show_bad_message_metadata():
    message_hash = input('Message hash: ')
    show_bad_message_metadata_for_hash(message_hash)
    in_message_context = True
    while in_message_context:
        in_message_context = show_bad_message_options(message_hash)


def show_bad_message_metadata_for_hash(message_hash):
    selected_bad_message_metadata = get_bad_message_metadata(message_hash)

    if not selected_bad_message_metadata:
        print(colored('Message not found', 'red'))
        print('')
        return

    pretty_print_bad_message_metadata(message_hash, selected_bad_message_metadata)


def show_bad_message_options(message_hash):
    print(colored('Current message hash:', 'cyan'), message_hash)
    print(colored('Actions:', 'cyan', attrs=['underline']))
    print(colored('  1.', 'cyan'), 'View message')
    print(colored('  2.', 'cyan'), 'Quarantine message')
    print(colored('  3.', 'cyan'), 'Cancel')
    print('')

    raw_selection = input(colored('Choose an action: ', 'cyan'))
    valid_selection = validate_integer_input_range(raw_selection, 1, 3)
    stay_in_menu = True

    if valid_selection == 1:
        show_bad_message_body(message_hash)
    elif valid_selection == 2:
        stay_in_menu = not confirm_quarantine_bad_message(message_hash)
    elif valid_selection == 3:
        stay_in_menu = False
    return stay_in_menu


def pretty_print_bad_message_metadata(message_hash, selected_bad_message_metadata):
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print(colored('Message Hash:', 'green'), message_hash)
    print(colored('Reports: ', 'green'))

    for index, report in enumerate(selected_bad_message_metadata, 1):
        if len(report) > 1:
            print(f'  {colored(index, "blue")}:')
        print(f"{colored('    Exception Report', 'green')}:")
        for k, v in report['exceptionReport'].items():
            print(f'      {colored(k, "green")}: {v}')
        print(f"{colored('    Stats', 'green')}:")
        for k, v in report['stats'].items():
            print(f'      {colored(k, "green")}: {v}')
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print('')


def get_bad_message_metadata(message_hash):
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/badmessage/{message_hash}')

    if response.status_code == 404:
        return None
    response.raise_for_status()
    response_json = response.json()

    if not response_json:
        return None

    return response_json


def validate_integer_input_range(selection, minimum, maximum):
    try:
        int_selection = int(selection)
    except ValueError:
        if selection:
            print(colored(f'{selection} is not a valid integer', 'red'))
        return

    if not minimum <= int_selection <= maximum:
        print(colored(f'{selection} is not in the valid range [{minimum, maximum}]', 'red'))
        return

    return int_selection


def show_splash():
    print('=========================================================================================================')
    print(colored(''' ___   _   ___    __  __ ___ ___ ___   _   ___ ___  __      _____ ____  _   ___ ___
| _ ) /_\ |   \  |  \/  | __/ __/ __| /_\ / __| __| \ \    / /_ _|_  / /_\ | _ \   \      |￣￣￣￣￣￣|
| _ \/ _ \| |) | | |\/| | _|\__ \__ \/ _ \ (_ | _|   \ \/\/ / | | / / / _ \|   / |) |     |    BAD     |
|___/_/ \_\___/  |_|  |_|___|___/___/_/ \_\___|___|   \_/\_/ |___/___/_/ \_\_|_\___/      |   RABBIT   |
                                                                                          |＿＿＿＿＿＿|
                                                                                        (\__/) ||
                                                                                        (•ㅅ•) ||
   Exit with CTRL+C                                                                     / 　 づ
''', 'cyan'))  # noqa: W605
    print('=========================================================================================================')
    print('')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('')
        print('')
        print(colored('✨ Goodbye ✨', 'green'))

import base64
import json
from contextlib import suppress
from json import JSONDecodeError

import requests
from termcolor import colored

from config import Config


def main():
    show_splash()

    actions = (
        {'description': 'List bad messages', 'action': show_bad_message_list},
        {'description': 'Get bad message from hash', 'action': show_bad_message_metadata},
        {'description': 'Get quarantined messages', 'action': show_quarantined_messages},
        {'description': 'Quarantine all bad messages', 'action': show_quarantine_all_bad_messages},
        {'description': 'Reset bad message cache', 'action': reset_bad_message_cache},
    )

    while True:

        input(f'press {colored("ENTER", "cyan")} to continue')
        print('')
        print(colored('Actions:', 'cyan', attrs=['underline']))
        for index, action in enumerate(actions):
            print(f'  {colored(f"{index + 1}.", "cyan")} {action["description"]}')
        print('')

        raw_selection = input(colored('Choose an action: ', 'cyan'))
        valid_selection = validate_integer_input_range(raw_selection, 1, 5)

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
    for index, report in enumerate(metadata):
        print(f"  {colored(index + 1, 'blue')}:  ")
        for k, v in report.items():
            print(colored(f'    {k}: ', 'green'), v)
    print(colored('Message Payload: ', 'green'), formatted_payload)
    print(colored('-------------------------------------------------------------------------------------', 'green'))


def show_all_quarantined_messages(quarantined_messages):
    for index, (message_hash, metadata) in enumerate(quarantined_messages.items()):
        message_payload = base64.b64decode(metadata[0]['messagePayload']).decode()
        for report in metadata:
            report.pop('messagePayload')
        if len(quarantined_messages) > 1:
            print(f'  {colored(index + 1, "blue")}:')
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
    bad_messages = get_message_summaries()
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


def show_bad_message_list():
    all_message_summaries: list = get_message_summaries()
    bad_message_summaries = [summary for summary in all_message_summaries if not summary['quarantined']]
    if not bad_message_summaries:
        show_no_bad_messages()
        return
    bad_message_summaries.sort(key=lambda message: message['firstSeen'])
    print('')
    print(f'There are currently {len(bad_message_summaries)} bad messages:')
    if len(bad_message_summaries) > 20:
        print('Showing only the oldest 20')
        bad_message_summaries = bad_message_summaries[:20]

    pretty_print_bad_message_summaries(bad_message_summaries)
    print('')

    raw_selection = input(
        colored(f'Select a message (1 to {len(bad_message_summaries)}) or cancel with ENTER: ', 'cyan'))
    print('')

    valid_selection = validate_integer_input_range(raw_selection, 1, len(bad_message_summaries))
    if not valid_selection:
        return

    message_hash = bad_message_summaries[valid_selection - 1]['messageHash']
    show_bad_message_metadata_for_hash(message_hash)
    in_message_context = True
    while in_message_context:
        in_message_context = show_bad_message_options(message_hash)


def get_message_summaries():
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/badmessages/summary')
    response.raise_for_status()
    return response.json()


def pretty_print_bad_message_summaries(bad_message_summaries):
    column_widths = {
        'messageHash': len(bad_message_summaries[0]['messageHash']),
        'firstSeen': max(len(str(summary['firstSeen'])) for summary in bad_message_summaries),
        'queues': max(len(', '.join(summary['affectedQueues'])) for summary in bad_message_summaries),
    }
    print('')
    header = (f'      | {colored("Message Hash".ljust(column_widths["messageHash"]), color="cyan")} '
              f'| {colored("First Seen".ljust(column_widths["firstSeen"]), color="cyan")} '
              f'| {colored("Queues".ljust(column_widths["queues"]), color="cyan")}')
    print(header)
    print(f'   ---|{"-" * (column_widths["messageHash"] + 2)}'
          f'|{"-" * (column_widths["firstSeen"] + 2)}'
          f'|{"-" * (column_widths["queues"] + 2)}')
    for index, summary in enumerate(bad_message_summaries, 1):
        print(f'   {colored((str(index) + ".").ljust(3), color="cyan")}'
              f'| {summary["messageHash"]} '
              f'| {summary["firstSeen"]} '
              f'| {", ".join(summary["affectedQueues"])}')


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
        print(colored(f'Message not found', 'red'))
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
    for index, report in enumerate(selected_bad_message_metadata):
        if len(report) > 1:
            print(f'  {colored(index + 1, "blue")}:')
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

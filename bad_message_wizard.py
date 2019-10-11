import base64
import json
import xml
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

        input(f'press {colored("ENTER", "white")} to continue')
        print('')
        print(colored('Actions:', 'white', attrs=['underline']))
        for index, action in enumerate(actions):
            print(f'  {colored(f"{index + 1}.", "white")} {action["description"]}')
        print('')

        raw_selection = input(colored('Choose an action: ', 'white'))
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
    print(colored('Message Hash: ', 'green'), colored(message_hash, 'white'))
    print(colored('Reports:', 'green'))
    for index, report in enumerate(metadata):
        print(f"  {colored(index + 1, 'green')}: ")
        for k, v in report.items():
            print(colored(f'    {k}:', 'green'), colored(v, 'white'))
    print(colored('Message Payload: ', 'green'))
    print(colored(formatted_payload, 'white'))
    print(colored('-------------------------------------------------------------------------------------', 'green'))


def show_all_quarantined_messages(quarantined_messages):
    for index, (message_hash, metadata) in enumerate(quarantined_messages.items()):
        message_payload = base64.b64decode(metadata[0]['messagePayload']).decode()
        for report in metadata:
            report.pop('messagePayload')
        print(colored(f'Message {index + 1}', 'white') + ':')
        with suppress(JSONDecodeError):
            pretty_print_quarantined_message(message_hash, metadata, json.dumps(json.loads(message_payload), indent=2))
            print('')
            continue
        with suppress(Exception):
            pretty_print_quarantined_message(
                message_hash, metadata, xml.dom.minidom.parseString(message_payload).toprettyxml())
            print('')
            continue
        pretty_print_quarantined_message(message_hash, metadata, message_payload)
        print('')


def show_quarantined_messages():
    quarantined_messages = get_quarantined_message_list()
    print('')
    print(colored(f'There are currently {len(quarantined_messages)} quarantined messages:', 'white'))
    print('')
    show_all_quarantined_messages(quarantined_messages)


def confirm_quarantine_all_bad_messages(bad_messages):
    print('')
    confirmation = input(colored("Confirm by responding with '", 'white') +
                         colored(f"I confirm I wish to quarantine all {len(bad_messages)} bad messages", 'red') +
                         colored("' exactly: ", 'white'))
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
    bad_messages = list_bad_messages()
    if not bad_messages:
        show_no_bad_messages()
        return
    print(colored(
        f'There are currently {len(bad_messages)} bad messages, continuing will quarantine them all', 'yellow'))
    print('')
    print(colored('1.', 'white'), 'Continue')
    print(colored('2.', 'white'), 'Cancel')
    print('')

    raw_selection = input(colored('Choose an action: ', 'white'))
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
    confirmation = input(colored('Confirm you want to quarantine the message by responding "yes": ', 'white'))
    if confirmation == 'yes':
        print(colored(f'Quarantining message {message_hash}', 'yellow'))
        quarantine_bad_message(message_hash)
        print(colored(f'Successfully quarantined {message_hash}', 'green'))
        print('')
    else:
        print(colored('Aborted', 'red'))


def quarantine_bad_message(message_hash):
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/skipmessage/{message_hash}')
    response.raise_for_status()


def reset_bad_message_cache():
    print('')
    print(colored('Resetting bad message cache', 'yellow'))
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/reset')
    response.raise_for_status()
    print(colored('Successfully reset bad message cache', 'green'))
    print('')


def show_bad_message_list():
    bad_messages = list_bad_messages()
    if not bad_messages:
        show_no_bad_messages()
        return
    print('')
    print(f'There are currently {len(bad_messages)} bad messages:')
    if len(bad_messages) > 20:
        print('Showing only the first 20')
        bad_messages = bad_messages[:20]

    for index, bad_message in enumerate(bad_messages):
        print(f'  {colored(f"{index + 1}.", "white")} {bad_message}')
    print('')

    raw_selection = input(colored(f'Select a message (1 to {len(bad_messages)}) for more options: ', 'white'))
    print('')

    valid_selection = validate_integer_input_range(raw_selection, 1, len(bad_messages))
    if not valid_selection:
        return

    show_bad_message_metadata_for_hash(bad_messages[valid_selection - 1])


def show_no_bad_messages():
    print('')
    print(colored('There are currently no bad messages known to the exception manager', 'green'))
    print('')


def pretty_print_bad_message(message_hash, body, format):
    print('')
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print(colored('Message Hash: ', 'green'), colored(message_hash, 'white'))
    print(colored('Detected Format: ', 'green'), colored(format, 'white'))
    print(f"{colored('Body: ', 'green')}\n{colored(body, 'white')}")
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print('')


def show_bad_message_body(message_hash):
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/peekmessage/{message_hash}')
    response.raise_for_status()

    with suppress(JSONDecodeError):
        pretty_print_bad_message(message_hash, json.dumps(response.json(), indent=2), 'json')
        return

    with suppress(Exception):
        pretty_print_bad_message(message_hash, xml.dom.minidom.parseString(response.text).toprettyxml(), 'xml')
        return

    pretty_print_bad_message(message_hash, response.text, 'text')


def show_bad_message_metadata():
    message_hash = input('Message hash: ')
    in_message_context = True
    while in_message_context:
        in_message_context = show_bad_message_metadata_for_hash(message_hash)


def show_bad_message_metadata_for_hash(message_hash):
    selected_bad_message_metadata = get_bad_message_metadata(message_hash)
    if not selected_bad_message_metadata:
        print(colored(f'Message not found', 'red'))
        print('')
        return
    pretty_print_bad_message_metadata(message_hash, selected_bad_message_metadata)
    print(colored('Actions:', 'white', attrs=['underline']))
    print(colored('1.', 'white'), 'View message')
    print(colored('2.', 'white'), 'Quarantine message')
    print('')

    raw_selection = input(f'Choose an action: ')
    valid_selection = validate_integer_input_range(raw_selection, 1, 2)
    if not valid_selection:
        return True
    elif valid_selection == 1:
        show_bad_message_body(message_hash)
        return True
    elif valid_selection == 2:
        confirm_quarantine_bad_message(message_hash)
        return False


def pretty_print_bad_message_metadata(message_hash, selected_bad_message_metadata):
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print(colored('Message Hash:', 'green'), colored(message_hash, 'white'))
    print(colored('Stats:', 'green'))
    for k, v in selected_bad_message_metadata['exceptionStats'].items():
        print(f'  {colored(k, "green")}: {colored(v, "white")}')
    print(colored('Exception Reports:', 'green'))
    for index, report in enumerate(selected_bad_message_metadata['exceptionReports']):
        print(colored(f'  {index + 1}:', 'green'))
        for k, v in report.items():
            print(f'    {colored(k, "green")}: {colored(v, "white")}')
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print('')


def list_bad_messages():
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/badmessages')
    response.raise_for_status()
    return response.json()


def get_bad_message_metadata(message_hash):
    response = requests.get(f'{Config.EXCEPTIONMANAGER_URL}/badmessage/{message_hash}')
    if response.status_code == 404:
        return None
    response.raise_for_status()
    response_json = response.json()
    if not response_json['exceptionStats']:
        return None
    return response_json


def validate_integer_input_range(selection, minimum, maximum):
    try:
        int_selection = int(selection)
    except ValueError:
        if selection:
            print(colored(f'{selection} is not a valid integer', 'red'))
        else:
            print(colored(f"'' is not a valid integer", 'red'))
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

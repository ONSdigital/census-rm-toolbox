import json
from json import JSONDecodeError
from pprint import pprint

import requests

from config import Config


def get_quarantined_message_list():
    response = requests.get(f'{Config.MESSAGE_EXCEPTION_URL}/skippedmessages')
    response.raise_for_status()
    return response.json()


def show_quarantined_messages():
    quarantined_messages = get_quarantined_message_list()
    print('')
    print('Quarantined messages: ')
    print('')
    pprint(quarantined_messages)
    print('')
    input('Press ENTER to continue')
    print('')


def main():
    print('=====================')
    print('Bad Message Wizard 🧙')
    print('Exit with CTRL+C')
    print('=====================')

    while True:

        print('')
        print('Actions:')
        print('1. List bad messages')
        print('2. Get bad message from hash')
        print('3. List all quarantined messages')
        print('4. Quarantine all bad messages')
        print('5. Reset bad message cache')
        print('')

        raw_selection = input('Choose an action: ')
        valid_selection = validate_integer_input_range(raw_selection, 1, 4)

        if not valid_selection:
            continue

        elif valid_selection == 1:
            print('')
            show_bad_message_list()

        elif valid_selection == 2:
            message_hash = input('Message hash: ')
            show_bad_message_metadata(message_hash)

        elif valid_selection == 3:
            show_quarantined_messages()

        elif valid_selection == 4:
            show_quarantine_all_bad_messages()

        elif valid_selection == 5:
            reset_bad_message_cache()


def confirm_quarantine_all_bad_messages(bad_messages):
    print('')
    print(f'Confirm you wish to quarantine all {len(bad_messages)}')
    confirmation = input(f"Confirm by responding with 'I confirm I wish to quarantine all {len(bad_messages)} bad messages' exactly: ")
    if confirmation == f'I confirm I wish to quarantine all {len(bad_messages)} bad messages':
        print('')
        print(f'Confirmed, quarantining all {len(bad_messages)} messages')
        print('')
        for bad_message in bad_messages:
            quarantine_bad_message(bad_message)
        print('Quarantined all bad messages')
        print('')
        input('Press ENTER to continue')
        print('')
    else:
        print('')
        print('Aborted')
        print('')
        input('Press ENTER to continue')
        print('')


def show_quarantine_all_bad_messages():
    bad_messages = list_bad_messages()
    print(f'There are currently {len(bad_messages)} bad messages, continuing will quarantine them all')
    print('')
    print(f'1. Continue')
    print(f'2. Cancel')
    print('')

    raw_selection = input('Choose an action: ')
    valid_selection = validate_integer_input_range(raw_selection, 1, 2)
    if not valid_selection:
        return

    elif valid_selection == 1:
        confirm_quarantine_all_bad_messages(bad_messages)
    else:
        print('')
        print('Aborted')
        print('')
        input('Press ENTER to continue')
        print('')


def reset_bad_message_cache():
    print('')
    print('Reseting bad message cache')
    response = requests.get(f'{Config.MESSAGE_EXCEPTION_URL}/reset')
    response.raise_for_status()
    print('Successfully reset bad message cache')


def show_bad_message_list():
    bad_messages = list_bad_messages()
    print(f'There are currently {len(bad_messages)} bad messages:')
    if len(bad_messages) > 20:
        print('Showing the first 20')
        bad_messages = bad_messages[:20]

    for index, bad_message in enumerate(bad_messages):
        print(f'{index + 1}. {bad_message}')
    print('')

    raw_selection = input(f'Select a message with 1 to {len(bad_messages)} for more options: ')
    print('')

    valid_selection = validate_integer_input_range(raw_selection, 1, len(bad_messages))
    if not valid_selection:
        return

    show_bad_message_metadata(bad_messages[valid_selection - 1])


def show_bad_message_body(message_hash):
    response = requests.get(f'{Config.MESSAGE_EXCEPTION_URL}/peekmessage/{message_hash}')
    response.raise_for_status()
    print('')
    print('=======================================================================================')
    print(f'Message hash: {message_hash}')
    print(f'Message payload:')
    print('---------------------------------------------------------------------------------------')
    print('')
    try:
        print(json.dumps(response.json(), indent=4, sort_keys=True))
    except JSONDecodeError as e:
        print(e)
        pprint(response.text)
    print('')
    print('=======================================================================================')
    print('')


def quarantine_bad_message(message_hash):
    response = requests.get(f'{Config.MESSAGE_EXCEPTION_URL}/skipmessage/{message_hash}')
    response.raise_for_status()


def show_bad_message_metadata(message_hash):
    selected_bad_message_metadata = get_bad_message_metadata(message_hash)
    print(f'Stats for message {message_hash}:')
    print('')
    print('Stats:')
    pprint(selected_bad_message_metadata['exceptionStats'], indent=2)
    print('')
    print('Exception Reports:')
    pprint(selected_bad_message_metadata['exceptionReports'], indent=2)
    print('')
    print('Actions:')
    print('1. View message')
    print('2. Quarantine message')
    print('')

    raw_selection = input(f'Choose an action: ')
    valid_selection = validate_integer_input_range(raw_selection, 1, 2)
    if not valid_selection:
        return
    elif valid_selection == 1:
        show_bad_message_body(message_hash)
    elif valid_selection == 2:
        confirm_quarantine_bad_message(message_hash)


def confirm_quarantine_bad_message(message_hash):
    confirmation = input('Confirm you want to quarantine the message by responding "yes": ')
    if confirmation == 'yes':
        print(f'Quarantining message {message_hash}')
        quarantine_bad_message(message_hash)
        print(f'Successfully quarantined {message_hash}')
    else:
        print('Aborting')


def list_bad_messages():
    response = requests.get(f'{Config.MESSAGE_EXCEPTION_URL}/badmessages')
    response.raise_for_status()
    return response.json()


def get_bad_message_metadata(message_hash):
    response = requests.get(f'{Config.MESSAGE_EXCEPTION_URL}/badmessage/{message_hash}')
    response.raise_for_status()
    return response.json()


def validate_integer_input_range(selection, minimum, maximum):
    try:
        int_selection = int(selection)
    except ValueError:
        print(f'{selection} is not a valid integer')
        return

    if not minimum <= int_selection <= maximum:
        print(f'{selection} is not in the valid range [{minimum, maximum}]')
        return

    return int_selection


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('')
        print('')
        print('✨ Goodbye ✨')

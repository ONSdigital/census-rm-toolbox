import argparse
import json

from google.cloud import pubsub_v1
from termcolor import colored


def main(subscription_name, subscription_project_id, search_term, number_messages, id_search, action):
    subscriber = pubsub_v1.SubscriberClient()
    response = []

    subscription_path = subscriber.subscription_path(
        subscription_project_id, subscription_name)
    for _ in range(number_messages):
        message = subscriber.pull(subscription_path, max_messages=1, return_immediately=True)
        if not message.received_messages:
            break
        response.extend(message.received_messages)
    if not response:
        print(colored('No messages on pubsub ', 'red'))
        return
    if search_term:
        print_messages(msg for msg in response if search_term.lower() in msg.message.data.decode('utf-8').lower())
    elif id_search:
        matching_id_messages = [msg for msg in response if id_search == msg.message.message_id]
        message_id = matching_id_messages[0].message.message_id
        if action == 'DELETE':
            subscriber.acknowledge(subscription_path, (msg.ack_id for msg in matching_id_messages))
            print(colored(f'Deleted message from pubsub: {message_id}', 'red'))
        else:
            print_messages(matching_id_messages)
    else:
        print_messages(response)


def print_messages(response):
    for msg in response:
        print(colored('-------------------------------------------------------------------------------------',
                      'green'))
        try:
            parsed_json = json.loads((msg.message.data.decode('utf-8')))
            print(colored('Json message:\n', 'green'),
                  colored(json.dumps(parsed_json, sort_keys=True, indent=4), 'white'))
        except json.decoder.JSONDecodeError as e:
            print(colored(msg.message.data.decode('utf-8'), 'white'))
            print(colored('ERROR: invalid JSON', 'red'))
            print(colored(e, 'red'))
        if msg.message.attributes:
            print(colored('attributes:', 'green'), colored(msg.message.attributes, 'white'))
        print(colored("message_id:", "green"), colored(msg.message.message_id, "white"))
        print(colored("ack_id:", "green"), colored(msg.ack_id, "white"))
        print(colored('-------------------------------------------------------------------------------------',
                      'green'))
        print('\n')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Various Rabbit queue manipulation tools.')
    parser.add_argument('source_subscription_name', help='source subscription name', type=str)
    parser.add_argument('source_subscription_project_ID', help='source subscription id', type=str)
    parser.add_argument('-s', '--search', help='message body search', type=str, default=None, nargs='?')
    parser.add_argument('-l', '--limit', help='message limit', type=int, default=100, nargs='?')
    parser.add_argument('message_id_search', help='message id search', type=str, default=None, nargs='?')

    parser.add_argument('action', help='action to perform', type=str, default=None, nargs='?',
                        choices=['DELETE'])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    main(args.source_subscription_name, args.source_subscription_project_ID, args.search, args.limit,
         args.message_id_search,
         args.action)

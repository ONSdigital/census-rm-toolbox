import argparse
import functools
import hashlib
import json
import xml.dom.minidom

from termcolor import colored

from utilities.rabbit_context import RabbitContext

SEEN_MESSAGES = 0
FOUND_MESSAGES = 0


def message_callback_function(ch, method, _properties, body, message_limit, message_body_search, action,
                              destination_queue_name, message_hash_search):
    global SEEN_MESSAGES
    global FOUND_MESSAGES
    SEEN_MESSAGES = SEEN_MESSAGES + 1

    if message_body_search:
        if message_body_search.lower() in body.decode('utf-8').lower():
            FOUND_MESSAGES = FOUND_MESSAGES + 1
            print_message(_properties, body)
    elif message_hash_search:
        if hashlib.sha256(body).hexdigest() == message_hash_search:
            FOUND_MESSAGES = FOUND_MESSAGES + 1
            if action == 'DELETE':
                print(colored('Deleted message', 'red'))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            elif action == 'MOVE':
                with RabbitContext(queue_name=destination_queue_name) as rabbit:
                    rabbit.publish_message(body, _properties.content_type, _properties.headers)
                    print(colored(f'Moved message to {destination_queue_name}', 'red'))
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            elif action == 'VIEW':
                print_message(_properties, body)
    else:
        print_message(_properties, body)

    if action != 'DELETE' and action != 'MOVE':
        ch.basic_nack(delivery_tag=method.delivery_tag)

    if SEEN_MESSAGES == message_limit:
        ch.stop_consuming()


def print_message(_properties, body):
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print(colored('Content type: ', 'green'), colored(_properties.content_type, 'white'))
    print(colored('Headers: ', 'green'), colored(_properties.headers, 'white'))
    if _properties.content_type == 'application/json':
        print(colored('Body: ', 'green'))
        try:
            parsed_json = json.loads(body.decode('utf-8'))
            print(colored(json.dumps(parsed_json, sort_keys=True, indent=4), 'white'))
        except json.decoder.JSONDecodeError as e:
            print(colored(body.decode('utf-8'), 'white'))
            print(colored('ERROR: invalid JSON', 'red'))
            print(colored(e.msg, 'red'))
    elif _properties.content_type == 'application/xml':
        try:
            dom = xml.dom.minidom.parseString(body.decode('utf-8'))
            print(dom.toprettyxml())
        except xml.parsers.expat.ExpatError as e:
            print(colored(body.decode('utf-8'), 'white'))
            print(colored('ERROR: invalid XML', 'red'))
            print(colored(e, 'red'))
    else:
        print(colored('Body: ', 'green'), colored(body.decode('utf-8'), 'white'))
    print(colored('Message hash: ', 'green'), colored(hashlib.sha256(body).hexdigest(), 'white'))
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print('\n')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Various Rabbit queue manipulation tools.')
    parser.add_argument('source_queue_name', help='source queue name', type=str)
    parser.add_argument('-l', '--limit', help='message limit', type=int, default=100)
    parser.add_argument('-s', '--search', help='message body search', type=str, default=None, nargs='?')
    parser.add_argument('-t', '--timeout', help='Search timeout', type=int, default=30)
    parser.add_argument('message_hash_search', help='message hash search', type=str, default=None, nargs='?')
    parser.add_argument('action', help='action to perform', type=str, default=None, nargs='?',
                        choices=['DELETE', 'MOVE', 'VIEW'])
    parser.add_argument('destination_queue_name', help='destination queue name', type=str, default=None, nargs='?')
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.action == 'MOVE' and args.destination_queue_name is None:
        print(colored(f'ERROR: Must specify destination queue name', 'red'))
        return

    if args.message_hash_search and args.search:
        print(colored(f'ERROR: Cannot mix message search and specific message actions', 'red'))
        return

    if args.message_hash_search and args.action is None:
        print(colored(f'ERROR: Must specify an action for specific message: DELETE, MOVE or VIEW', 'red'))
        return

    with RabbitContext(queue_name=args.source_queue_name) as rabbit:

        queue_qty = rabbit.get_queue_message_qty()
        message_limit = min(queue_qty, args.limit)

        if queue_qty == 0:
            print(colored(f'Queue is empty', 'red'))
            return

        rabbit.start_listening_for_messages(functools.partial(message_callback_function, message_limit=message_limit,
                                                              message_body_search=args.search, action=args.action,
                                                              destination_queue_name=args.destination_queue_name,
                                                              message_hash_search=args.message_hash_search), timeout=args.timeout)

    global FOUND_MESSAGES

    if args.message_hash_search and FOUND_MESSAGES == 0:
        print(colored(f'ERROR: Could not find specified message', 'red'))

    if args.search and FOUND_MESSAGES == 0:
        print(colored(f'ERROR: Could not find any messages containing "{args.search}"', 'red'))

    print(colored('==============================================', 'yellow'))
    print(colored('====== ', 'yellow'), colored('QUEUE TOTAL MESSAGES: ', 'green'), colored(queue_qty, 'white'))
    print(colored('====== ', 'yellow'), colored('FOUND MESSAGES: ', 'green'), colored(FOUND_MESSAGES, 'white'))
    print(colored('====== ', 'yellow'), colored('SEEN MESSAGES: ', 'green'), colored(SEEN_MESSAGES, 'white'))
    print(colored('==============================================', 'yellow'))


if __name__ == "__main__":
    main()

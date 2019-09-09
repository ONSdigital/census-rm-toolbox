import argparse
import functools
import hashlib
import json
import pprint
import xml.dom.minidom

from termcolor import colored

from utilities.rabbit_context import RabbitContext
from utilities.rabbit_helper import init_rabbit, start_listening_for_messages, get_queue_qty

seen_messages = 0
found_messages = 0


def message_callback_function(ch, method, _properties, body, message_limit, message_body_search, action,
                              destination_queue_name, message_hash_search):
    global seen_messages
    global found_messages
    seen_messages = seen_messages + 1

    if message_body_search:
        if message_body_search.lower() in body.decode('utf-8').lower():
            found_messages = found_messages + 1
            print_message(_properties, body)
    elif message_hash_search:
        if hashlib.sha256(body).hexdigest() == message_hash_search:
            found_messages = found_messages + 1
            if action == 'DELETE':
                print(colored('Deleted message', 'red'))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            elif action == 'MOVE':
                with RabbitContext(queue_name=destination_queue_name) as rabbit:
                    rabbit.publish_message(body, _properties.content_type)
                    print(colored(f'Moved message to {destination_queue_name}', 'red'))
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print_message(_properties, body)
    else:
        print_message(_properties, body)

    if action != 'DELETE' and action != 'MOVE' :
        ch.basic_nack(delivery_tag=method.delivery_tag)

    if seen_messages == message_limit:
        ch.stop_consuming()


def print_message(_properties, body):
    print(colored('-------------------------------------------------------------------------------------', 'green'))
    print(colored('Content type: ', 'green'), colored(_properties.content_type, 'white'))
    print(colored('Headers: ', 'green'), colored(_properties.headers, 'white'))
    if _properties.content_type == 'application/json':
        print(colored('Body: ', 'green'))
        pprint.pprint(json.loads(body.decode('utf-8')))
    elif _properties.content_type == 'application/xml':
        print(colored('Body: ', 'green'))
        dom = xml.dom.minidom.parseString(body.decode('utf-8'))
        print(dom.toprettyxml())
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
    parser.add_argument('message_hash_search', help='message hash search', type=str, default=None, nargs='?')
    parser.add_argument('action', help='action to perform', type=str, default=None, nargs='?',
                        choices=['DELETE', 'MOVE'])
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
        print(colored(f'ERROR: Must specify an action for specific message', 'red'))
        return

    init_rabbit(args.source_queue_name)
    queue_qty = get_queue_qty()
    message_limit = min(queue_qty, args.limit)

    if queue_qty == 0:
        print(colored(f'Queue is empty', 'red'))
        return

    start_listening_for_messages(args.source_queue_name,
                                 functools.partial(message_callback_function, message_limit=message_limit,
                                                   message_body_search=args.search, action=args.action,
                                                   destination_queue_name=args.destination_queue_name,
                                                   message_hash_search=args.message_hash_search))

    global found_messages

    if args.message_hash_search and found_messages == 0:
        print(colored(f'ERROR: Could not find specified message', 'red'))

    if args.search and found_messages == 0:
        print(colored(f'ERROR: Could not find any messages containing "{args.search}"', 'red'))

    print(colored('==============================================', 'yellow'))
    print(colored('====== ', 'yellow'), colored('QUEUE TOTAL MESSAGES: ', 'green'), colored(queue_qty, 'white'))
    print(colored('====== ', 'yellow'), colored('FOUND MESSAGES: ', 'green'), colored(found_messages, 'white'))
    print(colored('====== ', 'yellow'), colored('SEEN MESSAGES: ', 'green'), colored(seen_messages, 'white'))
    print(colored('==============================================', 'yellow'))


if __name__ == "__main__":
    main()

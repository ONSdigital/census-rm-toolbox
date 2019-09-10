import argparse

from google.cloud import pubsub_v1


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

    if search_term:
        for msg in response:
            if search_term.lower() in msg.message.data.decode('utf-8').lower():
                print('Found message:', msg)
    elif id_search:
        if action == 'DELETE':
            print('Attempting to delete: ', id_search)
            subscriber.acknowledge(subscription_path, [msg.ack_id for msg in response if id_search == msg.message.message_id])
    else:
        for msg in response:
            print("Received message:", msg)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Various Rabbit queue manipulation tools.')
    parser.add_argument('source_subscription_name', help='source subscription name', type=str)
    parser.add_argument('source_subscription_ID', help='source subscription id', type=str)
    parser.add_argument('-s', '--search', help='message body search', type=str, default=None, nargs='?')
    parser.add_argument('-l', '--limit', help='message limit', type=str, default=10, nargs='?')
    parser.add_argument('message_id_search', help='message id search', type=str, default=None, nargs='?')

    parser.add_argument('action', help='action to perform', type=str, default=None, nargs='?',
                        choices=['DELETE'])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    main(args.source_subscription_name, args.source_subscription_ID, args.search, args.limit, args.message_id_search,
         args.action)

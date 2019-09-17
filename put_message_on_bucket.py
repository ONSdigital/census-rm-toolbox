import argparse
import json

from google.cloud import pubsub_v1, storage
from termcolor import colored


def main(subscription_name, project_id, number_messages, id_search, action, bucket_name):
    subscriber = pubsub_v1.SubscriberClient()
    response = []

    subscription_path = subscriber.subscription_path(
        project_id, subscription_name)
    for _ in range(number_messages):
        message = subscriber.pull(subscription_path, max_messages=1, return_immediately=True)
        if not message.received_messages:
            break
        response.extend(message.received_messages)
    if not response:
        print(colored('No messages on pubsub ', 'red'))
        return
    elif id_search:
        matching_id_messages = [msg for msg in response if id_search == msg.message.message_id]
        if matching_id_messages:
            if action == 'MOVE':
                client = storage.Client()
                bucket = client.get_bucket(bucket_name)
                pubsub_dict = {'message_id': matching_id_messages[0].message.message_id,
                               'data': matching_id_messages[0].message.data.decode()}
                bucket.blob(f'{subscription_name}-{matching_id_messages[0].message.message_id}')\
                    .upload_from_string(json.dumps(pubsub_dict), content_type='application/json')
                print(colored('uploaded message: ', 'red'), colored(f'{matching_id_messages[0].message.message_id}', 'white'))
                subscriber.acknowledge(subscription_path, (msg.ack_id for msg in matching_id_messages))
        else:
            print('No messages found')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Various Rabbit queue manipulation tools.')
    parser.add_argument('source_subscription_name', help='source subscription name', type=str)
    parser.add_argument('source_subscription_project_ID', help='source subscription id', type=str)
    parser.add_argument('message_id_search', help='message id search', type=str, default=None, nargs='?')
    parser.add_argument('-l', '--limit', help='message limit', type=int, default=10, nargs='?')
    parser.add_argument('action', help='action to perform', type=str, default=None, nargs='?',
                        choices=['MOVE'])
    parser.add_argument('bucket', help='bucket name', type=str, default=None, nargs='?')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    main(args.source_subscription_name, args.source_subscription_project_ID, args.limit,
         args.message_id_search,
         args.action, args.bucket)

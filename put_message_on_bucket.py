import argparse
import json

from google.cloud import pubsub_v1, storage
from termcolor import colored


def main(subscription_name, project_id, number_messages, message_id, bucket_name):
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
    matched_message = [msg for msg in response if message_id == msg.message.message_id]
    if matched_message:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        pubsub_dict = {'message_id': matched_message[0].message.message_id,
                       'data': json.loads(matched_message[0].message.data)}
        bucket.blob(f'{subscription_name}-{matched_message[0].message.message_id}')\
            .upload_from_string(json.dumps(pubsub_dict), content_type='application/json')
        print(colored('uploaded message: ', 'red'), colored(f'{matched_message[0].message.message_id}', 'white'))
        subscriber.acknowledge(subscription_path, (msg.ack_id for msg in matched_message))
    else:
        print('No messages found')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Pubsub tool to move a message to a GCS bucket')
    parser.add_argument('source_subscription_name', help='source subscription name', type=str)
    parser.add_argument('source_subscription_project_ID', help='source subscription id', type=str)
    parser.add_argument('bucket', help='bucket name', type=str)
    parser.add_argument('message_id', help='message id ', type=str)
    parser.add_argument('-l', '--limit', help='message limit', type=int, default=100, nargs='?')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    main(args.source_subscription_name, args.source_subscription_project_ID, args.limit,
         args.message_id, args.bucket)

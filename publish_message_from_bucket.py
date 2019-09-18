import argparse
import json

from google.cloud import pubsub_v1, storage
from termcolor import colored


def main(topic_name, project_id,  blob, bucket_name):
    string_to_publish = download_blob(bucket_name, blob)
    json_message = json.loads(string_to_publish)
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    future = publisher.publish(topic_path, json.dumps(json_message['data']).encode('utf-8'))
    print(colored(f'Published message to {topic_name}: ', 'green'), colored(future.result(), 'white'))


def download_blob(bucket_name, source_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    return blob.download_as_string()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to publish a message onto a pubsub topic from a GCS bucket. ')
    parser.add_argument('source_topic_name', help='source topic name', type=str)
    parser.add_argument('source_topic_project_ID', help='source topic id', type=str)
    parser.add_argument('message_blob', help='message blob', type=str, default=None, nargs='?')
    parser.add_argument('bucket', help='bucket name', type=str, default=None, nargs='?')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    main(args.source_topic_name, args.source_topic_project_ID,
         args.message_blob, args.bucket)

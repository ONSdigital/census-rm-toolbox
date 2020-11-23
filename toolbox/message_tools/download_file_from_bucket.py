import argparse
from pathlib import Path

from google.cloud import storage
from termcolor import colored


def main(bucket_name, file_name, file_destination_path):
    client = storage.Client()

    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)

    file_path = Path(file_destination_path).joinpath(file_name)
    blob.download_to_filename(file_path)

    print(colored(f'Downloaded file {file_name} from gcp bucket {bucket_name}', 'green'))


def parse_arguments():
    parser = argparse.ArgumentParser(description='Script to retrieve a file from a GCS bucket')
    parser.add_argument('bucket', help='Bucket name', type=str)
    parser.add_argument('file_name', help='Name of file to retrieve', type=str)
    parser.add_argument('destination_file_path', help='Directory to move published input files to', type=str)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(args.bucket, args.file_name, args.destination_file_path)

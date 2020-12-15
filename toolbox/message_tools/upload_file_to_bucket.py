import argparse
from pathlib import Path

from google.cloud import storage


def upload_file_to_bucket(file_name, project_name, bucket_name):
    file_path = Path(file_name)

    client = storage.Client(project=project_name)
    bucket = client.get_bucket(bucket_name)
    print(f'Copying file to GCS bucket {bucket.name}')
    bucket.blob(file_path.name).upload_from_filename(filename=str(file_path))
    print(f'File successfully written to {bucket.name}')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Upload a file to a bucket')
    parser.add_argument('file_name', help='name of the file', type=str)
    parser.add_argument('project_name', help='project name', type=str)
    parser.add_argument('bucket_name', help='bucket name', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    upload_file_to_bucket(args.file_name, args.project_name, args.bucket_name)


if __name__ == "__main__":
    main()

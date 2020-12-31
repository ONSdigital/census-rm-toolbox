import argparse
from pathlib import Path

from google.cloud import storage


def put_audit_files_to_bucket(audit_files_folder, project_name, bucket_name):
    audit_folders = [folder for folder in audit_files_folder.iterdir() if folder.is_dir()]
    for folder in audit_folders:
        log_files = list(folder.glob('*.log'))  # TODO: this doesn't exclude SQL logs at the moment
        if log_files:
            for log_file in log_files:
                client = storage.Client(project=project_name)
                bucket = client.get_bucket(bucket_name)
                print(f'Copying {log_file} to GCS bucket {bucket.name}')
                bucket.blob(f'{log_file.parent.name}/{log_file.name}').upload_from_filename(filename=log_file)
                print(f'File successfully written {log_file} to {bucket.name}')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Upload a file to a bucket')
    parser.add_argument('audit_files_folder', help='Location of audit files', type=Path)
    parser.add_argument('project_name', help='project name', type=str)
    parser.add_argument('bucket_name', help='bucket name', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    put_audit_files_to_bucket(args.audit_files_folder, args.project_name, args.bucket_name)


if __name__ == "__main__":
    main()
import argparse
import csv
from pathlib import Path

import requests
from google.cloud import storage
from requests import HTTPError

from toolbox.config import Config


def generate_bulk_invalid_address_file(file_to_process):
    address_delta_file = Path(f'invalid_addresses_{file_to_process.stem}.csv')
    error = False

    with open(file_to_process, encoding="utf-8") as open_file_to_process:
        file_reader = csv.DictReader(open_file_to_process, delimiter=',')

        with open(address_delta_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["case_id", "reason"])

            for line_number, row in enumerate(file_reader, 1):
                case_id_list = get_case_id_from_case_api(row['UPRN'], line_number)
                if case_id_list:
                    for case_id in case_id_list:
                        writer.writerow([case_id, 'ADDRESS_DELTA'])
                else:
                    error = True

            if error:
                address_delta_file.unlink()
                return None

    return address_delta_file


def get_case_id_from_case_api(uprn, line_number):
    response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/cases/uprn/{uprn}')
    try:
        response.raise_for_status()
    except HTTPError as e:
        if response.status_code == 404:
            print(f'Error 404: Cannot find the UPRN {uprn} on line {line_number}, Error {e}')
        else:
            print(f'Network or Internal Server Error on line {line_number}, Error {e}')
        return None

    result = response.json()

    return [case['id'] for case in result]


def upload_file_to_bucket(file_path: Path):
    client = storage.Client(project=Config.BULK_INVALID_ADDRESS_PROJECT_ID)
    bucket = client.get_bucket(Config.BULK_INVALID_ADDRESS_BUCKET_NAME)
    print(f'Copying files to GCS bucket {bucket.name}')
    bucket.blob(file_path.name).upload_from_filename(filename=str(file_path))
    print(f'All files successfully written to {bucket.name}')

    file_path.unlink()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to find invalid address case IDs by UPRNs')
    parser.add_argument('file_to_process', help='File to process', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    address_delta_file = generate_bulk_invalid_address_file(Path(args.file_to_process))

    if not address_delta_file:
        exit(1)
    upload_file_to_bucket(address_delta_file)


if __name__ == '__main__':
    main()

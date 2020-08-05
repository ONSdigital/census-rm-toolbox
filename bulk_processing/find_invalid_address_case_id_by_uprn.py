import argparse
import csv
import os
from pathlib import Path

import requests
import sys
from google.cloud import storage
from requests import HTTPError

from config import Config


def generate_bulk_invalid_address_file(file_to_process):
    address_delta_file = Path(f'invalid_addresses_{file_to_process.stem}.csv')
    address_delta_file.write_text('case_id,reason\n')

    with open(file_to_process, encoding="utf-8") as open_file_to_process:
        file_reader = csv.DictReader(open_file_to_process, delimiter=',')

        for line_number, row in enumerate(file_reader, 1):
            case_id_list = get_case_id_from_case_api(row['UPRN'], line_number, file_to_process)
            for case_id in case_id_list:
                write_invalid_addresses_case_id_file(case_id, address_delta_file)

    upload_file_to_bucket(address_delta_file)


def get_case_id_from_case_api(uprn, line_number, file_to_process):
    response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/cases/uprn/{uprn}')
    try:
        response.raise_for_status()
    except HTTPError as e:
        if response.status_code == 404:
            print(f'Error 404: Cannot find the UPRN {uprn} on line {line_number}, Error {e}')
        else:
            print(f'Network or Internal Server Error on line {line_number}, Error {e}')
        os.remove(Path(f'invalid_addresses_{file_to_process.stem}.csv'))
        sys.exit(1)

    result = response.json()

    return [case['id'] for case in result]


def write_invalid_addresses_case_id_file(case_id, address_delta_file):
    file = open(address_delta_file, 'a')
    file.write(f'{case_id}, ADDRESS_DELTA')
    file.write('\n')


def upload_file_to_bucket(file_path: Path):
    client = storage.Client(project=Config.BULK_INVALID_ADDRESS_PROJECT_ID)
    bucket = client.get_bucket(Config.BULK_INVALID_ADDRESS_BUCKET_NAME)
    print(f'Copying files to GCS bucket {bucket.name}')
    bucket.blob(f'{file_path.name}').upload_from_filename(filename=str(file_path))
    print(f'All files successfully written to {bucket.name}')

    file_path.unlink()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to find invalid address case IDs by UPRNs')
    parser.add_argument('file_to_process', help='File to process', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    generate_bulk_invalid_address_file(Path(args.file_to_process))


if __name__ == '__main__':
    main()

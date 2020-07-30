import argparse
import csv
from pathlib import Path

import requests
from google.cloud import storage
from requests import HTTPError

from config import Config


def read_invalid_address_uprn_file(file_to_process, project_id):
    case_id_list = []
    with open(file_to_process, encoding="utf-8") as open_file_to_process:
        file_reader = csv.DictReader(open_file_to_process, delimiter=',')
        print(file_reader)

        for line_number, row in enumerate(file_reader, 1):
            case_id_list.extend(get_case_id_from_case_api(row['UPRN']))

    address_delta_file = write_invalid_addresses_case_id_file(case_id_list, Path(file_to_process))
    upload_file_to_bucket(address_delta_file, project_id)


def get_case_id_from_case_api(uprn):
    response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/cases/uprn/{uprn}')
    try:
        response.raise_for_status()
    except HTTPError:
        print('Error: invalid or non-existent UPRN')
        return

    result = response.json()

    case_id_list = [case['id'] for case in result]
    return case_id_list


def write_invalid_addresses_case_id_file(case_id_list, file_to_process):
    address_delta_file = Path(f'invalid_addresses_{file_to_process.stem}.csv')

    with open(address_delta_file, 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['case_id', 'reason'])
        for case in case_id_list:
            csv_out.writerow([case, 'ADDRESS_DELTA'])
    return address_delta_file


def upload_file_to_bucket(file_path: Path, project_id):
    client = storage.Client(project=project_id)
    bucket = client.get_bucket(f'{client.project}-bulk-invalid-address')
    print(f'Copying files to GCS bucket {bucket.name}')
    bucket.blob(f'{file_path.name}').upload_from_filename(filename=str(file_path))
    print(f'All files successfully written to {bucket.name}')

    file_path.unlink()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to find invalid address case IDs by UPRNs')
    parser.add_argument('project_id', help='Target project ID', type=str)
    parser.add_argument('file_to_process', help='File to process', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    read_invalid_address_uprn_file(args.file_to_process, args.project_id)


if __name__ == '__main__':
    main()
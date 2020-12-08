import argparse
import csv
from copy import copy
from pathlib import Path

import requests
from requests import HTTPError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from toolbox.bulk_processing.address_update_processor import AddressUpdateProcessor
from toolbox.config import Config


def generate_address_update_file(file_to_process: Path):
    output_address_update_file = Path(f'{Config.BULK_ADDRESS_UPDATE_FILE_PREFIX}{file_to_process.stem}.csv')

    case_id_fieldname = 'CASE_ID'
    address_update_fieldnames = list(AddressUpdateProcessor.schema.keys())
    expected_input_fields = set(address_update_fieldnames)
    expected_input_fields.remove(case_id_fieldname)
    fields_to_copy = copy(expected_input_fields)

    # There are columns that are on the sample file but not address update,
    # we expect to see them but ignore the values here
    expected_input_fields.update({'REGION', 'ADDRESS_TYPE', 'ADDRESS_LEVEL'})

    with open(file_to_process) as open_file_to_process:
        file_reader = csv.DictReader(open_file_to_process, delimiter=',')
        actual_fieldnames = set(file_reader.fieldnames)
        if actual_fieldnames != expected_input_fields:
            output_address_update_file.unlink()
            raise ValueError(f'Invalid header, '
                             f'missing field names: {expected_input_fields.difference(actual_fieldnames)}, '
                             f'unexpected fieldnames: {actual_fieldnames.difference(expected_input_fields)}')

        with open(output_address_update_file, 'w') as open_output_file:
            output_writer = csv.DictWriter(open_output_file, fieldnames=address_update_fieldnames)
            output_writer.writeheader()

            for line_number, row in enumerate(file_reader, 1):
                try:
                    case_id = get_case_id_from_case_api(row['UPRN'], line_number)
                except Exception:
                    output_address_update_file.unlink()
                    raise
                address_update_row = {k: row[k] for k in fields_to_copy}
                address_update_row[case_id_fieldname] = case_id
                output_writer.writerow(address_update_row)
                if line_number % 1000 == 0:
                    print(f'Processed {line_number} rows')

    print(f'Finished processing all {line_number} rows')
    print(f'Output written to {str(output_address_update_file)}')
    return output_address_update_file


@retry(wait=wait_exponential(multiplier=1, min=1, max=4), stop=stop_after_attempt(10),
       retry=retry_if_exception_type(HTTPError),
       reraise=True)
def get_case_id_from_case_api(uprn, line_number):
    response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/cases/uprn/{uprn}')
    try:
        response.raise_for_status()
    except HTTPError as e:
        if response.status_code == 404:
            raise ValueError(f'Error 404: Cannot find the UPRN {uprn} on line {line_number}')
        raise HTTPError(f'Network or Internal Server Error on line {line_number}') from e

    result = response.json()
    case_ids = [case['id'] for case in result]
    if len(case_ids) > 1:
        raise ValueError(f'UPRN {uprn} matches multiple case IDs, line {line_number}')
    return case_ids[0]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Tool to build an address update file from a sample file"
                    " by looking up the UPRN's in the case API")
    parser.add_argument('file_to_process', help='File to process', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    generate_address_update_file(Path(args.file_to_process))


if __name__ == '__main__':
    main()

import argparse
import csv
from copy import copy
from pathlib import Path

from toolbox.bulk_processing.address_update_processor import AddressUpdateProcessor
from toolbox.config import Config
from toolbox.utilities import db_helper


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

        with open(output_address_update_file,
                  'w') as open_output_file, db_helper.connect_to_read_replica_pool() as conn_pool:
            output_writer = csv.DictWriter(open_output_file, fieldnames=address_update_fieldnames)
            output_writer.writeheader()

            for line_number, row in enumerate(file_reader, 1):
                try:
                    case_id = get_case_id_from_uprn(row['UPRN'], line_number, conn_pool=conn_pool)
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


def get_case_id_from_uprn(uprn, line_number, conn_pool):
    result = db_helper.execute_in_connection_pool('SELECT case_id FROM casev2.cases WHERE uprn = %s', (uprn,),
                                                  conn_pool=conn_pool)
    case_ids = [row[0] for row in result]
    if len(case_ids) < 1:
        raise ValueError(f'UPRN {uprn} does not match any cases, line {line_number}')
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

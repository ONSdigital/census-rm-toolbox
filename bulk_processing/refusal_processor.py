import json
from typing import Collection

from bulk_processing.bulk_processor import BulkProcessor
from bulk_processing.processor_interface import Processor


class RefusalProcessor(Processor):
    # TODO: actual logic
    #  This is example code, non functional

    def check_for_files_to_process(self) -> Collection[str]:
        return ['Example_1.csv', 'Example_completely_invalid.csv', 'Example_bad_row.csv']

    def validate_file(self, file) -> (bool, str):
        if file == 'Example_completely_invalid.csv':
            return False, 'Missing column: "Example"'
        return True, None

    def validate_row(self, row) -> (bool, str):
        if row == {'example': 'bad'}:
            return False, f'Row failed validation, '
        return True, None

    def get_fieldnames(self) -> Collection[str]:
        return ['case_id', 'refusal_type']

    def build_event_message(self, row) -> str:
        row['eventType'] = 'REFUSAL_RECEIVED'
        return json.dumps(row)


class BulkRefusalProcessor(BulkProcessor, RefusalProcessor):
    """Inject RefusalProcessor into BulkProcessor"""
    pass


if __name__ == '__main__':
    BulkRefusalProcessor(
        file_name_format='Example_*.csv',
        bucket_name='path_to_gcp_bucket',
        routing_key='event.example'
    ).run()

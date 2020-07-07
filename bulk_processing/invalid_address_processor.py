import json
import uuid
from typing import Collection

from bulk_processing.bulk_processor import BulkProcessor
from bulk_processing.processor_interface import Processor


class InvalidAddressProcessor(Processor):
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
        return ['case_ref']

    def build_event_message(self, row) -> str:
        return json.dumps({
            'eventType': 'ADDRESS_INVALID',
            'case_id': str(self.get_case_id_by_case_ref('placeholder')),  #  row['case_ref'])),
        })

    def get_case_id_by_case_ref(self, case_ref):
        # definitely works
        return uuid.uuid4()


class BulkInvalidAddressProcessor(BulkProcessor, InvalidAddressProcessor):
    """Inject InvalidAddressProcessor into BulkProcessor"""
    pass


if __name__ == '__main__':
    BulkInvalidAddressProcessor(
        file_name_format='Example_*.csv',
        bucket_name='path_to_gcp_bucket',
        routing_key='event.example'
    ).run()

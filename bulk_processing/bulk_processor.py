import csv
import json
from pathlib import Path

from google.cloud import storage

from bulk_processing.processor_interface import Processor
from utilities.rabbit_context import RabbitContext


class BulkProcessor:
    def __init__(self, processor: Processor):
        # TODO make configurable
        self.working_dir = Path('bulk_refusals')
        self.bucket_name = 'census-rm-adamhawtin-perf1-bulk-test'

        self.processor = processor
        self.storage_client = storage.Client()
        self.storage_bucket = self.storage_client.bucket(self.bucket_name)

    def process_file(self, file_to_process, success_file, failure_file, failure_reasons_file):
        try:
            with open(file_to_process, encoding="utf-8") as open_file_to_process:
                file_reader = csv.DictReader(open_file_to_process, delimiter=',')
                format_validation_failures = self.processor.find_format_validation_failures(file_reader.fieldnames)
                if format_validation_failures:
                    return [format_validation_failures]
                return self.process_rows(file_reader, success_file, failure_file, failure_reasons_file)
        except UnicodeDecodeError as err:
            self.write_file_encoding_error_files(err, failure_file, failure_reasons_file, file_to_process)

    def write_file_encoding_error_files(self, err, failure_file, failure_reasons_file, file_to_process):
        failure_blob = self.storage_bucket.blob(failure_file.name)
        failure_blob.upload_from_filename(file_to_process)
        failure_reasons_blob = self.storage_bucket.blob(failure_reasons_file.name)
        failure_reasons_blob.upload_from_string(f'Invalid file encoding, requires utf-8, error: {err}')

    def process_rows(self, file_reader, success_file, failure_file, failure_reasons_file):
        failure_count = 0
        success_count = 0
        with RabbitContext() as rabbit:
            for line_number, row in enumerate(file_reader, 2):
                row_failures = self.processor.find_row_validation_failures(line_number, row)
                if row_failures:
                    failure_count += len(row_failures)
                    self.write_row_failures_to_files(row, row_failures, failure_file, failure_reasons_file)
                else:
                    success_count += 1
                    event_messages = self.processor.build_event_messages(row)
                    self.publish_messages(event_messages, rabbit)
                    self.write_row_success_to_file(row, success_file)
        print(f"Validation progress: {str(line_number).rjust(8)} lines processed, "
              f"Failures: {failure_count}")
        return success_count, failure_count

    def build_file_paths(self, file_to_process_name):
        success_file = self.working_dir.joinpath(f'succeeded_{file_to_process_name}')
        failure_file = self.working_dir.joinpath(f'failed_{file_to_process_name}')
        failure_reasons_file = self.working_dir.joinpath(f'failure_reasons_{file_to_process_name}')
        return success_file, failure_file, failure_reasons_file

    def write_row_failures_to_files(self, failed_row, failures, failure_file, failure_reasons_file):
        with open(failure_file, 'a') as append_failure_file:
            append_failure_file.write(','.join(failed_row.values()))
            append_failure_file.write('\n')
        with open(failure_reasons_file, 'a') as append_failure_reasons_file:
            append_failure_reasons_file.write(', '.join(str(failure.description) for failure in failures))
            append_failure_reasons_file.write('\n')

    def write_row_success_to_file(self, succeeded_row, success_file):
        with open(success_file, 'a') as append_success_file:
            append_success_file.write(','.join(succeeded_row.values()))
            append_success_file.write('\n')

    def publish_messages(self, messages, rabbit):
        for message in messages:
            rabbit.publish_message(json.dumps(message), 'application/json', None, exchange=self.processor.EXCHANGE,
                                   routing_key=self.processor.ROUTING_KEY)

    def run(self):
        blobs_to_process = self.storage_client.list_blobs(self.bucket_name, prefix=self.processor.FILE_PREFIX)
        for blob_to_process in blobs_to_process:
            file_to_process = self.working_dir.joinpath(blob_to_process.name)
            with open(file_to_process, 'wb') as open_file_to_process:
                self.storage_client.download_blob_to_file(blob_to_process, open_file_to_process)
            success_file, failure_file, failure_reasons_file = self.build_file_paths(file_to_process.name)
            successes, failures = self.process_file(file_to_process, success_file, failure_file, failure_reasons_file)
            files_to_upload = []
            if successes:
                files_to_upload.append(success_file)
            if failures:
                files_to_upload.append(failure_file)
                files_to_upload.append(failure_reasons_file)

            self.upload_files_to_bucket(files_to_upload)
            blob_to_process.delete()

    def upload_files_to_bucket(self, files):
        for file in files:
            file_blob = self.storage_bucket.blob(file.name)
            file_blob.upload_from_filename(str(file))

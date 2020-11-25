import csv
import json
import shutil
from pathlib import Path
from typing import Collection

from google.cloud import storage

from toolbox.bulk_processing.processor_interface import Processor
from toolbox.bulk_processing.validators import header_equal, Invalid, ValidationFailure
from toolbox.config import Config
from toolbox.utilities import db_helper
from toolbox.utilities.rabbit_context import RabbitContext


class BulkProcessor:
    def __init__(self, processor: Processor):
        self.working_dir = Config.BULK_WORKING_DIRECTORY

        self.processor = processor
        self.storage_client = storage.Client(project=self.processor.project_id)
        self.storage_bucket = self.storage_client.bucket(self.processor.bucket_name)
        self.rabbit = None
        self.db_connection_pool = None

    def run(self):
        print(f'Checking for files in bucket {repr(self.processor.bucket_name)}'
              f' with prefix {repr(self.processor.file_prefix)}')
        with db_helper.connect_to_read_replica_pool() as self.db_connection_pool, RabbitContext() as self.rabbit:
            blobs_to_process = self.storage_client.list_blobs(self.processor.bucket_name,
                                                              prefix=self.processor.file_prefix)

            for blob_to_process in blobs_to_process:
                self.process_bulk_file_from_bucket(blob_to_process)

    def process_bulk_file_from_bucket(self, blob_to_process):
        print(f'Processing file: {blob_to_process.name}')
        file_to_process = self.download_file_to_process(blob_to_process)
        success_file, error_file, error_detail_file = self.initialise_results_files(file_to_process.name)
        successes, errors = self.process_file(file_to_process, success_file, error_file,
                                              error_detail_file)

        print(f'Uploading results from processing file: {blob_to_process.name}')
        self.upload_results(successes, errors, success_file, error_file, error_detail_file)

        print(f'Deleting remote file: {blob_to_process.name}')
        blob_to_process.delete()

        self.delete_local_files((file_to_process, success_file, error_file, error_detail_file))
        print(f'Finished processing file: {blob_to_process.name}')

    def process_file(self, file_to_process, success_file, error_file, error_detail_file):
        try:
            with open(file_to_process, encoding="utf-8") as open_file_to_process:

                file_reader = csv.DictReader(open_file_to_process, delimiter=',')
                header_validation_failures = self.find_header_validation_errors(file_reader.fieldnames)

                if header_validation_failures:
                    print(f'File: {file_to_process.name}, header row is invalid')
                    shutil.copy(file_to_process, error_file)
                    self.write_error_details_to_file([header_validation_failures], error_detail_file)
                    return 0, 1  # success_count, error_count

                self.write_header_ok_to_file(error_detail_file)

                return self.process_rows(file_reader, success_file, error_file, error_detail_file)

        except UnicodeDecodeError as err:
            self.write_file_encoding_error_files(err, error_file, error_detail_file, file_to_process)
            return 0, 1  # success_count, error_count

    @staticmethod
    def write_file_encoding_error_files(err, error_file, error_detail_file, file_to_process):
        shutil.copy(file_to_process, error_file)
        error_detail_file.write_text(f'Invalid file encoding, requires utf-8, error: {err}')

    def process_rows(self, file_reader, success_file, error_file, error_detail_file):
        error_count = 0
        success_count = 0
        for line_number, row in enumerate(file_reader, 1):
            row_errors = self.find_row_validation_errors(line_number, row)
            if row_errors:
                error_count += len(row_errors)
                self.write_row_errors_to_files(row, row_errors, error_file, error_detail_file)
            else:
                success_count += 1
                event_messages = self.processor.build_event_messages(row)
                self.publish_messages(event_messages, self.rabbit)
                self.write_row_success_to_file(row, success_file)
        print(f'Processing results: {line_number} rows processed, '
              f'Failures: {error_count}')
        return success_count, error_count

    def initialise_results_files(self, file_to_process_name):
        header_row = ','.join(column for column in self.processor.schema.keys()) + '\n'
        success_file = self.working_dir.joinpath(f'PROCESSED_{file_to_process_name}')
        success_file.write_text(header_row)
        error_file = self.working_dir.joinpath(f'ERROR_{file_to_process_name}')
        error_file.write_text(header_row)
        error_detail_file = self.working_dir.joinpath(f'ERROR_DETAIL_{file_to_process_name}')
        error_detail_file.touch()
        return success_file, error_file, error_detail_file

    def find_header_validation_errors(self, header):
        try:
            header_equal(self.processor.schema.keys())(header)
        except Invalid as invalid:
            return ValidationFailure(line_number=1, column=None, description=str(invalid))

    def find_row_validation_errors(self, line_number, row):
        errors = []
        for column, validators in self.processor.schema.items():
            for validator in validators:
                try:
                    validator(row[column], row=row, db_connection_pool=self.db_connection_pool, column=column)
                except Invalid as invalid:
                    errors.append(ValidationFailure(line_number, column, invalid))
        return errors

    def write_row_errors_to_files(self, errored_row, errors, error_file, error_detail_file):
        with open(error_file, 'a') as append_error_file:
            append_error_file.write(','.join(errored_row.values()))
            append_error_file.write('\n')
        self.write_error_details_to_file(errors, error_detail_file)

    @staticmethod
    def write_error_details_to_file(errors, error_detail_file):
        with open(error_detail_file, 'a') as append_error_detail_file:
            append_error_detail_file.write(
                ' | '.join(f"[Column: {error.column}, Error: {str(error.description)}]" for error in errors))
            append_error_detail_file.write('\n')

    @staticmethod
    def write_header_ok_to_file(error_detail_file):
        with open(error_detail_file, 'a') as append_error_detail_file:
            append_error_detail_file.write('Header row is valid\n')

    @staticmethod
    def write_row_success_to_file(succeeded_row, success_file):
        with open(success_file, 'a') as append_success_file:
            append_success_file.write(','.join(succeeded_row.values()))
            append_success_file.write('\n')

    def publish_messages(self, messages, rabbit):
        for message in messages:
            rabbit.publish_message(
                message=json.dumps(message),
                content_type='application/json',
                headers=None,
                exchange=self.processor.exchange,
                routing_key=self.processor.routing_key
            )

    def download_file_to_process(self, blob_to_process):
        file_to_process = self.working_dir.joinpath(blob_to_process.name)

        with open(file_to_process, 'wb') as open_file_to_process:
            self.storage_client.download_blob_to_file(blob_to_process, open_file_to_process)
        return file_to_process

    def upload_results(self, successes, errors, success_file, error_file, error_detail_file):
        # Only upload files which contain data, we don't want to make empty error or success files
        files_to_upload = []
        if successes:
            files_to_upload.append(success_file)
        if errors:
            files_to_upload.append(error_file)
            files_to_upload.append(error_detail_file)
        self.upload_files_to_bucket(files_to_upload)

    def upload_files_to_bucket(self, files: Collection[Path]):
        for file_to_upload in files:
            file_blob = self.storage_bucket.blob(file_to_upload.name)
            file_blob.upload_from_filename(str(file_to_upload))

    @staticmethod
    def delete_local_files(files_to_delete: Collection[Path]):
        print(f'Deleting local files: {files_to_delete}')
        for file_to_delete in files_to_delete:
            file_to_delete.unlink()

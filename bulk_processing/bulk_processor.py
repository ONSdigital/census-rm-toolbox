from bulk_processing.processor_interface import Processor


class BulkProcessor(Processor):
    # TODO: actual logic
    #  This is example code for demonstration, non functional

    def __init__(self, bucket_name: str = None, file_name_format: str = None, routing_key: str = None):
        self.bucket_name = bucket_name
        self.file_name_format = file_name_format
        self.routing_key = routing_key

    def process_file(self, file):
        file_csv = self.read_file(file)
        for i, row in enumerate(file_csv):
            # Example bad row
            if file == 'Example_bad_row.csv' and i == 1:
                row = {'example': 'bad'}
            row_ok, error_detail = super().validate_row(row)
            if not row_ok:
                self.write_error_row(row, error_detail)
            self.send_event_message(super().build_event_message(row))
            self.write_success_row(row)
        self.remove_original_file(file)

    def read_file(self, file):
        """Return an example that quacks like a csv dict reader"""
        field_names = super().get_fieldnames()
        return [
            {
                field_name: str(i) + f'_{file}_example_data_{field_name}' for field_name in
                field_names
            }
            for i in range(10)
        ]

    def write_error_row(self, row, error_detail):
        print(f'writing to error file, row: {row}, detail: {error_detail}')

    def write_success_row(self, row):
        print(f'writing to success file: {row}')

    def send_event_message(self, event_message):
        print(f'sending message, routing: {self.routing_key}, message: {event_message}')

    def remove_original_file(self, file):
        print(f'deleting file: {file}')

    def run(self):
        files_to_process = super().check_for_files_to_process()
        print(f'Picking up files to process: {files_to_process}')
        for file in files_to_process:
            print(f'Processing file: {file}')
            file_ok, error_detail = super().validate_file(file)
            if not file_ok:
                self.write_error_row(None, error_detail)
                continue
            self.process_file(file)

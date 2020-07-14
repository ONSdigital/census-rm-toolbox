import argparse
import csv
from collections import namedtuple

from bulk_processing.validators import set_equal, Invalid, in_set, case_exists_by_id

ValidationFailure = namedtuple('ValidationFailure', ('line_number', 'column', 'description'))


class RefusalProcessor:

    def __init__(self):
        self.schema = {"case_id": [case_exists_by_id()],
                       "refusal_type": [in_set({"HARD_REFUSAL", "EXTRAORDINARY_REFUSAL"})]
                       }

    def find_header_validation_failures(self, header):
        valid_header = set(self.schema.keys())
        try:
            set_equal(valid_header)(header)
        except Invalid as invalid:
            return ValidationFailure(line_number=1, column=None, description=str(invalid))

    def find_refusal_validation_failures(self, refusal_file_reader) -> list:
        failures = []
        for line_number, row in enumerate(refusal_file_reader, 2):
            failures.extend(self.find_row_validation_failures(line_number, row))
            if not line_number % 10000:
                print(f"Validation progress: {str(line_number).rjust(8)} lines checked, "
                      f"Failures: {len(failures)}", end='\r', flush=True)
        print(f"Validation progress: {str(line_number).rjust(8)} lines checked, "
              f"Failures: {len(failures)}")
        return failures

    def find_row_validation_failures(self, line_number, row):
        failures = []
        for column, validators in self.schema.items():
            for validator in validators:
                try:
                    validator(row[column], row=row)
                except Invalid as invalid:
                    failures.append(ValidationFailure(line_number, column, invalid))
        return failures

    def validate(self, refusal_file_path):
        try:
            with open(refusal_file_path, encoding="utf-8") as refusal_file:
                refusal_file_reader = csv.DictReader(refusal_file, delimiter=',')
                header_failures = self.find_header_validation_failures(refusal_file_reader.fieldnames)
                if header_failures:
                    return [header_failures]
                return self.find_refusal_validation_failures(refusal_file_reader)
        except UnicodeDecodeError as err:
            return [
                ValidationFailure(line_number=None, column=None,
                                  description=f'Invalid file encoding, requires utf-8, error: {err}')]


def print_failures(failures, print_limit=20):
    print(f'{len(failures)} validation failure(s):')
    if len(failures) > print_limit:
        print_failures_summary(failures, print_limit)
    else:
        for failure in failures:
            print(build_failure_log(failure))


def build_failure_log(failure):
    return (f'line: {failure.line_number}, column: {failure.column}, description: {failure.description}'
            if failure.column else
            f'line: Header, description: {failure.description}'
            if failure.line_number else
            failure.description)


def print_failures_summary(failures, print_limit):
    for failure in failures[:print_limit]:
        print(build_failure_log(failure))
    response = input(f'Showing first {print_limit} of {len(failures)}. '
                     f'Show remaining {len(failures) - print_limit} [Y/n]?\n')
    if response.lower() in {'y', 'yes'}:
        for failure in failures[print_limit:]:
            print(build_failure_log(failure))


def parse_arguments():
    parser = argparse.ArgumentParser(description='Load a sample file into response management.')
    parser.add_argument('refusal_file_path', help='path to the refusal file', type=str)
    return parser.parse_args()


def main():
    args = parse_arguments()
    failures = RefusalProcessor().validate(args.refusal_file_path)
    if failures:
        print_failures(failures)
        print(f'{args.refusal_file_path} is not valid ❌')
    print(f'Success! {args.refusal_file_path} passed validation ✅')


if __name__ == "__main__":
    main()

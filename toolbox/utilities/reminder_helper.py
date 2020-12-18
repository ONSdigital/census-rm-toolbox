import csv


def get_lsoas_from_file(lsoa_file_path):
    with open(lsoa_file_path) as lsoa_file:
        lsoa_file_reader = csv.reader(lsoa_file, delimiter=',')
        return [lsoa[0] for lsoa in lsoa_file_reader]


def check_lsoas(lsoas):
    errors = []
    for row, lsoa in enumerate(lsoas, 1):
        errors.extend(check_lsoa(row, lsoa))
    if errors:
        print('INVALID FILE, EXITING')
        for error in errors:
            print(error)
        exit(1)


def check_lsoa(row, lsoa):
    row_errors = []
    if not lsoa.isalnum():
        row_errors.append(f'Row: {row}, LSOA {repr(lsoa)} is not alphanumeric')
    if len(lsoa) > 9:
        row_errors.append(f'Row: {row}, LSOA {repr(lsoa)} is too long')
    return row_errors

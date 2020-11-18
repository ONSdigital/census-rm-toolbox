import csv


def get_lsoas_from_file(lsoa_file_path):
    with open(lsoa_file_path) as lsoa_file:
        lsoa_file_reader = csv.reader(lsoa_file, delimiter=',')
        return [lsoa[0] for lsoa in lsoa_file_reader]


def check_lsoas(lsoas):
    if not all(check_lsoa(row, lsoa) for row, lsoa in enumerate(lsoas, 1)):
        print('INVALID FILE, EXITING')
        exit(1)


def check_lsoa(row, lsoa):
    if not lsoa.isalnum():
        print(f'Row: {row}, LSOA {repr(lsoa)} is not alphanumeric')
        return False
    if len(lsoa) != 9:
        print(f'Row: {row}, LSOA {repr(lsoa)} is not 9 characters long')
        return False
    return True

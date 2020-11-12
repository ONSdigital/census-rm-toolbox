import csv


def get_lsoas_from_file(lsoa_file_path):
    with open(lsoa_file_path) as lsoa_file:
        lsoa_file_reader = csv.reader(lsoa_file, delimiter=',')
        return [lsoa[0] for lsoa in lsoa_file_reader]

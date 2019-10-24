import csv
import argparse
import os
import requests
import qid_checksum_validator
from config import Config


def validate_sample_file(sample_file_path):
    try:
        with open(sample_file_path, encoding="utf-8") as sample_file: #open() opens CSV as text file
            return load_sample(sample_file)
    except UnicodeDecodeError as err:
        print(f'Invalid file encoding, requires utf-8, error: {err}')
        exit(-1)


def load_sample(sample_file):
    sample_file_reader = csv.DictReader(sample_file, delimiter=',', fieldnames=['case_ref', 'qid']) #DictReader() reads CSV data directly into a dictionary / delimiter specifies character used to separate each field
    validate_and_submit_questionnaire_links(sample_file_reader)


#argparse makes it easier to write user-friendly command-line interfaces
#also automatically generates help/usage messages/issues errors when users give the program invalid arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Load a sample file into response management.')
    parser.add_argument('sample_file_path', help='path to the sample file', type=str)
    return parser.parse_args()


args = parse_arguments()
error_count = 0


def validate_and_submit_questionnaire_links(sample_file_reader):
    for line_number, questionnaire_link in enumerate(sample_file_reader, 1): #remove whitespace
        for i in questionnaire_link:
            questionnaire_link[i] = questionnaire_link[i].replace(" ", "")
        if (not validate_case_ref(line_number, questionnaire_link["case_ref"])
                or not validate_qid(line_number, questionnaire_link["qid"])):
            continue
        validate_case_id(line_number, questionnaire_link["case_ref"])


def validate_case_ref(line_number, case_ref):
    if len(case_ref) != 8 or not case_ref.isdigit():
        print(f'Error: Either wrong length or type located on case_ref {case_ref}, line {line_number}')
        return False
    return True


def validate_qid(line_number, qid):
    if len(qid) != 16 or not qid.isdigit():
        print(f'Error: Either wrong length or type located on qid {qid}, line {line_number}')
    elif qid[2] != "2":
        print(f'QID number {qid}, line {line_number} tranche identifier must be 2')
    elif not qid_checksum_validator.validate(qid, int(os.getenv('QID_MODULUS')), int(os.getenv('QID_FACTOR')))[0]:
        print(f'QID check digits incorrect at QID {qid}, line {line_number}')
    else:
        return True
    return False


def validate_case_id(line_number, case_ref):
    response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/cases/ref/{case_ref}')
    if response.status_code == 404:
        print(f'Error: Case_ref {case_ref}, line {line_number} does not exist')
        return None
    response.raise_for_status()
    return response.json()["id"]


def main():
    validate_sample_file(args.sample_file_path)
    if error_count == 0:
        print(f'Sample file is OK.')
    else:
        print(f'{error_count} error(s) found in sample file')
        exit(-1)


if __name__ == "__main__":
    main()
import csv
import argparse
import requests
import qid_checksum_validator
from config import Config
from datetime import datetime
import uuid
import json
from utilities.rabbit_context import RabbitContext


def validate_qid_link_file(qid_link_file_path):
    try:
        with open(qid_link_file_path, encoding="utf-8") as qid_link_file:
            return qid_file(qid_link_file)
    except UnicodeDecodeError as err:
        print(f'Invalid file encoding, requires utf-8, error: {err}')
        exit(-1)


def qid_file(qid_link_file):
    qid_link_file_reader = csv.DictReader(qid_link_file, delimiter=',', fieldnames=['case_ref', 'qid'])
    validate_and_submit_questionnaire_links(qid_link_file_reader)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Load a QID Link file into response management.')
    parser.add_argument('qid_link_file_path', help='path to the QID Link file', type=str)
    return parser.parse_args()


args = parse_arguments()
error_count = 0


def validate_and_submit_questionnaire_links(qid_link_file_reader):
    global error_count
    for line_number, questionnaire_link in enumerate(qid_link_file_reader, 1):
        error_count = 0
        for i in questionnaire_link:
            questionnaire_link[i] = questionnaire_link[i].replace(" ", "")
        validate_qid_len_and_type(line_number, questionnaire_link["qid"])
        validate_qid_third_digit(line_number, questionnaire_link["qid"])
        validate_check_digits(line_number, questionnaire_link["qid"])
        case_id = validate_case_ref(line_number, questionnaire_link["case_ref"])

        if error_count > 0:
            print(f'Error: {questionnaire_link} on line {line_number} have FAILED')
        else:
            post_message_to_queue(case_id, questionnaire_link["qid"], line_number)
        print("\n")


def validate_case_ref(line_number, case_ref):
    global error_count
    if len(case_ref) != 8 or not case_ref.isdigit():
        print(f'Error: Either wrong length or type located on Case Reference {case_ref}, line {line_number}')
        error_count += 1
    if error_count == 0:
        response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/cases/ref/{case_ref}')
        if response.status_code == 404:
            print(f'Error: Case Reference {case_ref} on line {line_number} does not exist')
            error_count += 1
            return None
        response.raise_for_status()
        return response.json()["id"]


def validate_qid_len_and_type(line_number, qid):
    global error_count
    if len(qid) != 16 or not qid.isdigit():
        print(f'Error: Either wrong length or type located on QID {qid}, line {line_number}')
        error_count += 1


def validate_qid_third_digit(line_number, qid):
    global error_count
    if qid[2] != "2":
        print(f'Error: QID {qid}, line {line_number} tranche identifier must be 2')
        error_count += 1


def validate_check_digits(line_number, qid):
    global error_count
    if not qid_checksum_validator.validate(qid, int(Config.QID_MODULUS), int(Config.QID_FACTOR))[0]:
        print(f'Error: Check Digits incorrect for QID {qid}, line {line_number}')
        error_count += 1


def post_message_to_queue(case_id, qid, line_number):
    message = {
        "event": {
            "type": "QUESTIONNAIRE_LINKED",
            "source": "RM",
            "channel": "RM",
            "dateTime": datetime.utcnow().isoformat() + 'Z',
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "uac": {
                "questionnaireId": qid,
                "caseId": case_id,
            }
        }
    }
    with RabbitContext() as rabbit:
        rabbit.publish_message(json.dumps(message), "application/json", None, exchange='events',
                               routing_key='event.questionnaire.update')
        print(f'Case ID {case_id} and QID {qid} on line {line_number} have PASSED')


def main():
    validate_qid_link_file(args.qid_link_file_path)


if __name__ == "__main__":
    main()

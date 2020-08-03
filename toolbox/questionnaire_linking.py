import argparse
import csv
import json
import uuid
from datetime import datetime

import requests
from pika import BasicProperties
from pika.spec import PERSISTENT_DELIVERY_MODE

from toolbox import qid_checksum_validator
from toolbox.config import Config
from toolbox.utilities.rabbit_context import RabbitContext

CASE_REF_ERROR_COUNT = 0
QID_ERROR_COUNT = 0


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
    parser = argparse.ArgumentParser(description='Load a QID Link file into response management')
    parser.add_argument('qid_link_file_path', help='path to the QID Link file', type=str)
    return parser.parse_args()


def validate_and_submit_questionnaire_links(qid_link_file_reader):
    global CASE_REF_ERROR_COUNT
    global QID_ERROR_COUNT
    for line_number, questionnaire_link in enumerate(qid_link_file_reader, 1):
        CASE_REF_ERROR_COUNT = 0
        QID_ERROR_COUNT = 0
        for i in questionnaire_link:
            questionnaire_link[i] = questionnaire_link[i].replace(" ", "")
        validate_qid_len_and_type(line_number, questionnaire_link["qid"])
        validate_qid_third_digit(line_number, questionnaire_link["qid"])
        validate_check_digits(line_number, questionnaire_link["qid"])
        case_id = validate_case_ref(line_number, questionnaire_link["case_ref"])

        if CASE_REF_ERROR_COUNT or QID_ERROR_COUNT:
            print(f'Error: Line {line_number}: {questionnaire_link} has FAILED')
        else:
            post_message_to_queue(case_id, questionnaire_link["qid"], line_number)
        print("\n")


def validate_case_ref(line_number, case_ref):
    global CASE_REF_ERROR_COUNT
    if len(case_ref) != 8:
        print(f'Error: Line {line_number}: Incorrect length of Case Reference {case_ref}. Expected length is 8 digits')
        CASE_REF_ERROR_COUNT += 1
    if not case_ref.isdigit():
        print(f'Error: Line {line_number}: Incorrect type of Case Reference {case_ref}. Case Reference MUST be numeric')
        CASE_REF_ERROR_COUNT += 1
    if CASE_REF_ERROR_COUNT == 0:
        response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/cases/ref/{case_ref}')
        if response.status_code == 404:
            print(f'Error: Line {line_number}: Case Reference {case_ref} does not exist')
            CASE_REF_ERROR_COUNT += 1
            return None
        response.raise_for_status()
        return response.json()["id"]


def validate_qid_len_and_type(line_number, qid):
    global QID_ERROR_COUNT
    if len(qid) != 16:
        print(f'Error: Line {line_number}: Incorrect length of QID {qid}. Expected length is 16 digits')
        QID_ERROR_COUNT += 1
    if not qid.isdigit():
        print(f'Error: Line {line_number}: Incorrect type of QID {qid}. QID MUST be numeric')
        QID_ERROR_COUNT += 1


def validate_qid_third_digit(line_number, qid):
    global QID_ERROR_COUNT
    if len(qid) >= 3 and qid[2] != "2":
        print(f'Error: Line {line_number}: QID {qid} tranche identifier must be 2')
        QID_ERROR_COUNT += 1
    elif len(qid) < 3:
        print(f'Error: Line {line_number}: QID {qid} must have a minimum of 3 digits for Tranche ID to be checked')
        QID_ERROR_COUNT += 1


def validate_check_digits(line_number, qid):
    global QID_ERROR_COUNT
    if len(qid) >= 3 and not qid_checksum_validator.validate(qid, int(Config.QID_MODULUS), int(Config.QID_FACTOR))[0]:
        print(f'Error: Line {line_number}: Check Digits incorrect in QID {qid}')
        QID_ERROR_COUNT += 1
    elif len(qid) < 3:
        print(f'Error: Line {line_number}: QID {qid} length is not long enough for Check Digits to be validated')
        QID_ERROR_COUNT += 1


def post_message_to_queue(case_id, qid, line_number):
    properties = BasicProperties(content_type='application/json', delivery_mode=PERSISTENT_DELIVERY_MODE)
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
        rabbit.channel.basic_publish(exchange='events', routing_key='event.questionnaire.update',
                                     body=json.dumps(message), properties=properties, mandatory=True)
        print(f"Success: Line {line_number}: Case ID {case_id} and QID {qid} have PASSED and have been LINKED")


def main():
    args = parse_arguments()
    validate_qid_link_file(args.qid_link_file_path)


if __name__ == "__main__":
    main()

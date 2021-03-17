import json
import uuid
from datetime import datetime

import requests
from requests import HTTPError

from toolbox.config import Config
from toolbox.qid_checksum_validator import validate
from toolbox.utilities.db_helper import execute_parametrized_sql_query
from toolbox.utilities.rabbit_context import RabbitContext


def create_questionnaire_linked_message():
    print('Ok, Im gonna link a questionnaire')
    print('Whats the QID?')
    qid = input()

    print('Whats the CaseID?')
    case_id = input()

    response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/cases/{case_id}')

    try:
        response.raise_for_status()
    except HTTPError:
        print('Error: invalid or non-existent Case ID')
        return

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

    print('Here is the generated message:')
    print(json.dumps(message, sort_keys=True, indent=4))
    print('Do you want to publish it?')
    do_publish = input()

    if do_publish != 'yes':
        print('Not publishing')
        return

    with RabbitContext() as rabbit:
        rabbit.publish_message(json.dumps(message), 'application/json', None, exchange='events',
                               routing_key='event.questionnaire.update')
        print('Successfully published')


def create_refusal_message():
    print('Ok, I am creating a Refusal message for you')
    print('What type of refusal do you want?')
    print('1. SOFT_REFUSAL')
    print('2. HARD_REFUSAL')
    print('3. EXTRAORDINARY_REFUSAL')
    refusal_type_number = input()

    if refusal_type_number == '1':
        refusal_type = 'SOFT_REFUSAL'
    elif refusal_type_number == '2':
        refusal_type = 'HARD_REFUSAL'
    elif refusal_type_number == '3':
        refusal_type = 'EXTRAORDINARY_REFUSAL'
    else:
        print('Error: you must choose a valid option')
        return

    print('What case ID?')
    case_id = input()

    response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/cases/{case_id}')

    try:
        response.raise_for_status()
    except HTTPError:
        print('Error: invalid or non-existent Case ID')
        return

    print('What is the reason for this refusal?')
    reason = input()

    message = {
        "event": {
            "type": "REFUSAL_RECEIVED",
            "source": "RM",
            "channel": "RM",
            "dateTime": datetime.utcnow().isoformat() + 'Z',
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "refusal": {
                "type": refusal_type,
                "report": reason,
                "collectionCase": {
                    "id": case_id
                }
            }
        }
    }

    print('Here is the generated message:')
    print(json.dumps(message, sort_keys=True, indent=4))
    print('Do you want to publish it?')
    do_publish = input()

    if do_publish != 'yes':
        print('Not publishing')
        return

    with RabbitContext() as rabbit:
        rabbit.publish_message(json.dumps(message), 'application/json', None, exchange='events',
                               routing_key='event.respondent.refusal')
        print('Successfully published')


def check_uac_qid_pair_exist(uac, qid):
    result = execute_parametrized_sql_query("SELECT qid FROM uacqid.uac_qid WHERE uac = %s", (uac,))
    if not result:
        raise ValueError('ERROR: UAC not found in uac qid database')

    found_qid = result[0][0]
    if found_qid != qid:
        raise ValueError(f'ERROR: UAC exists but is linked to a different QID: {found_qid}')


def create_rm_uac_created_message():
    print('!!! WARNING !!!')
    print('You must be absolutely sure this UAC/QID pair is genuine, it MUST exist in the uacqid service database '
          'but NOT already exist in our UAC QID link table')
    speed_bump_response = input('Are you sure you wish to proceed? (y/n): ')
    if speed_bump_response.lower() not in {'yes', 'y'}:
        return
    print('Ok, generating an RM UAC CREATED message.')
    print('Whats the QID?')
    qid = input()

    if not validate(qid, int(Config.QID_MODULUS), int(Config.QID_FACTOR)):
        raise ValueError('ERROR: Bad QID, checksum invalid')

    qid_check_response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/qids/{qid}')
    if qid_check_response.status_code != 404:
        raise ValueError('ERROR: This QID already exists in the uac qid link table')

    print('What is the UAC?')
    uac = input()
    if len(uac) != 16:
        raise ValueError('Bad UAC, wrong length. Message not sent.')

    if not uac.isalnum():
        raise ValueError('Bad UAC, bad characters. Message not sent.')

    check_uac_qid_pair_exist(uac, qid)

    print('Whats the CaseID?')
    case_id = input()

    case_check_response = requests.get(f'http://{Config.CASEAPI_HOST}:{Config.CASEAPI_PORT}/cases/{case_id}')

    try:
        case_check_response.raise_for_status()
    except HTTPError:
        raise ValueError('Error: invalid or non-existent Case ID. Message not sent.')

    message = {
        "event": {
            "type": "RM_UAC_CREATED",
            "source": "RM",
            "channel": "RM",
            "dateTime": datetime.utcnow().isoformat() + 'Z',
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "uacQidCreated": {
                "caseId": case_id,
                "qid": qid,
                "uac": uac
            }
        }
    }

    print('Here is the generated message:')
    print(json.dumps(message, sort_keys=True, indent=4))
    print('Do you want to publish it?')
    do_publish = input()

    if do_publish != 'yes':
        print('Not publishing')
        return

    with RabbitContext(queue_name='case.uac-qid-created') as rabbit:
        rabbit.publish_message(json.dumps(message), 'application/json', None, routing_key='case.uac-qid-created')
        print('Successfully published')


def main():
    print('What type of message do you want?')
    print('1. Refusal')
    print('2. Questionnaire Linked')
    print('3. RM UAC CREATED')
    message_type = input()

    if message_type == '1':
        create_refusal_message()
    elif message_type == '2':
        create_questionnaire_linked_message()
    elif message_type == '3':
        create_rm_uac_created_message()
    else:
        print('Error: you must choose a valid option')


if __name__ == "__main__":
    main()

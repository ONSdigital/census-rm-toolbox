import json
import uuid
from datetime import datetime

import requests
from requests import HTTPError

from toolbox.utilities.rabbit_context import RabbitContext
from toolbox.config import Config


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


def main():
    print('What type of message do you want?')
    print('1. Refusal')
    print('2. Questionnaire Linked')
    message_type = input()

    if message_type == '1':
        create_refusal_message()
    elif message_type == '2':
        create_questionnaire_linked_message()
    else:
        print('Error: you must choose a valid option')


if __name__ == "__main__":
    main()

import os
from pathlib import Path


class Config:
    RABBITMQ_HOST = os.getenv('RABBITMQ_SERVICE_HOST', 'localhost')
    RABBITMQ_PORT = os.getenv('RABBITMQ_SERVICE_PORT', '6672')
    RABBITMQ_HTTP_PORT = os.getenv('RABBITMQ_HTTP_PORT', '16672')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_HOST_WRITE = os.getenv('DB_HOST_RW', 'localhost')
    DB_HOST_ACTION = os.getenv('DB_HOST_ACTION', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '6432')
    DB_PORT_WRITE = os.getenv('DB_PORT_RW', '6432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_NAME_WRITE = os.getenv('DB_NAME_RW', 'postgres')
    DB_USESSL = os.getenv('DB_USESSL', '')
    DB_ACTION_CERTIFICATES = os.getenv('DB_ACTION_CERTIFICATES',
                                       (" sslmode=verify-ca sslrootcert=/home/toolbox/.postgresql-action/root.crt "
                                        "sslcert=/home/toolbox/.postgresql-action/postgresql.crt "
                                        "sslkey=/home/toolbox/.postgresql-action/postgresql.key"))
    CASEAPI_HOST = os.getenv('CASEAPI_HOST', 'localhost')
    CASEAPI_PORT = os.getenv('CASEAPI_PORT', '8161')
    EXCEPTIONMANAGER_HOST = os.getenv('EXCEPTIONMANAGER_HOST', 'localhost')
    EXCEPTIONMANAGER_PORT = os.getenv('EXCEPTIONMANAGER_PORT', '8666')
    EXCEPTIONMANAGER_URL = f'http://{EXCEPTIONMANAGER_HOST}:{EXCEPTIONMANAGER_PORT}'
    QID_MODULUS = os.getenv('QID_MODULUS', '1')
    QID_FACTOR = os.getenv('QID_FACTOR', '1')

    BULK_WORKING_DIRECTORY = Path(os.getenv('BULK_WORKING_DIRECTORY', '/tmp'))

    BULK_REFUSAL_FILE_PREFIX = os.getenv('BULK_REFUSAL_FILE_PREFIX', 'refusals_')
    BULK_REFUSAL_BUCKET_NAME = os.getenv('BULK_REFUSAL_BUCKET_NAME')
    BULK_REFUSAL_PROJECT_ID = os.getenv('BULK_REFUSAL_PROJECT_ID')
    REFUSAL_EVENT_ROUTING_KEY = os.getenv('REFUSAL_EVENT_ROUTING_KEY', 'event.respondent.refusal')

    BULK_NEW_ADDRESS_FILE_PREFIX = os.getenv('BULK_NEW_ADDRESS_FILE_PREFIX', 'new_addresses_')
    BULK_NEW_ADDRESS_BUCKET_NAME = os.getenv('BULK_NEW_ADDRESS_BUCKET_NAME')
    BULK_NEW_ADDRESS_PROJECT_ID = os.getenv('BULK_NEW_ADDRESS_PROJECT_ID')
    NEW_ADDRESS_EVENT_ROUTING_KEY = os.getenv('NEW_ADDRESS_EVENT_ROUTING_KEY', 'case.sample.inbound')
    COLLECTION_EXERCISE_ID = os.getenv('COLLECTION_EXERCISE_ID')
    ACTION_PLAN_ID = os.getenv('ACTION_PLAN_ID')
    ENVIRONMENT = os.getenv('ENVIRONMENT')

    BULK_INVALID_ADDRESS_FILE_PREFIX = os.getenv('BULK_INVALID_ADDRESS_FILE_PREFIX', 'invalid_addresses_')
    BULK_INVALID_ADDRESS_BUCKET_NAME = os.getenv('BULK_INVALID_ADDRESS_BUCKET_NAME')
    BULK_INVALID_ADDRESS_PROJECT_ID = os.getenv('BULK_INVALID_ADDRESS_PROJECT_ID')
    INVALID_ADDRESS_EVENT_ROUTING_KEY = os.getenv('INVALID_ADDRESS_EVENT_ROUTING_KEY', 'event.case.address.update')

    BULK_DEACTIVATE_UAC_FILE_PREFIX = os.getenv('BULK_DEACTIVATE_UAC_FILE_PREFIX', 'deactivate_uac_')
    BULK_DEACTIVATE_UAC_BUCKET_NAME = os.getenv('BULK_DEACTIVATE_UAC_BUCKET_NAME')
    BULK_DEACTIVATE_UAC_PROJECT_ID = os.getenv('BULK_DEACTIVATE_UAC_PROJECT_ID')
    DEACTIVATE_UAC_EVENT_ROUTING_KEY = os.getenv('DEACTIVATE_UAC_EVENT_ROUTING_KEY', 'case.deactivate-uac')

    EVENTS_EXCHANGE = os.getenv('EVENTS_EXCHANGE', 'events')


class TestConfig(Config):
    COLLECTION_EXERCISE_ID = os.getenv('COLLECTION_EXERCISE_ID', '88960972-38a5-438f-b543-cd9bb464f49a')
    ACTION_PLAN_ID = os.getenv('ACTION_PLAN_ID', '88960972-38a5-438f-b543-cd9bb464f49a')


if Config.ENVIRONMENT == 'TEST':
    Config = TestConfig

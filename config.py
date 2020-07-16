import os


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
    DB_ACTION_CERTIFICATES = (" sslmode=verify-ca sslrootcert=/home/toolbox/.postgresql-action/root.crt "
                              "sslcert=/home/toolbox/.postgresql-action/postgresql.crt "
                              "sslkey=/home/toolbox/.postgresql-action/postgresql.key")
    CASEAPI_HOST = os.getenv('CASEAPI_HOST', 'localhost')
    CASEAPI_PORT = os.getenv('CASEAPI_PORT', '8161')
    EXCEPTIONMANAGER_HOST = os.getenv('EXCEPTIONMANAGER_HOST', 'localhost')
    EXCEPTIONMANAGER_PORT = os.getenv('EXCEPTIONMANAGER_PORT', '8666')
    EXCEPTIONMANAGER_URL = f'http://{EXCEPTIONMANAGER_HOST}:{EXCEPTIONMANAGER_PORT}'
    QID_MODULUS = os.getenv('QID_MODULUS', '1')
    QID_FACTOR = os.getenv('QID_FACTOR', '1')

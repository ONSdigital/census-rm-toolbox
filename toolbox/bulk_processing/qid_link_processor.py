import logging
import uuid
from datetime import datetime

from structlog import wrap_logger

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.processor_interface import Processor
from toolbox.bulk_processing.validators import case_exists_by_id, is_uuid, qid_exists
from toolbox.config import Config
from toolbox.logger import logger_initial_config


class QidLinkProcessor(Processor):
    file_prefix = Config.BULK_QID_LINK_FILE_PREFIX
    routing_key = Config.BULK_QID_LINK_ROUTING_KEY
    exchange = Config.EVENTS_EXCHANGE
    bucket_name = Config.BULK_QID_LINK_BUCKET_NAME
    project_id = Config.BULK_QID_LINK_PROJECT_ID
    schema = {
        "case_id": [is_uuid(), case_exists_by_id()],
        "qid": [qid_exists()]
    }

    def build_event_messages(self, row):
        return [{
            "event": {
                "type": "QUESTIONNAIRE_LINKED",
                "source": "RM_QID_LINK_PROCESSOR",
                "channel": "RM",
                "dateTime": datetime.utcnow().isoformat() + 'Z',
                "transactionId": str(uuid.uuid4())
            },
            "payload": {
                "uac": {
                    "questionnaireId": row['qid'],
                    "caseId": row['case_id']
                }
            }
        }]


def main():
    logger_initial_config()
    logger = wrap_logger(logging.getLogger(__name__))
    logger.info('Started bulk processing qid linking', app_log_level=Config.LOG_LEVEL, environment=Config.ENVIRONMENT)
    BulkProcessor(QidLinkProcessor()).run()


if __name__ == "__main__":
    main()

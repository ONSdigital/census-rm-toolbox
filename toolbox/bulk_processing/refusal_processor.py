import logging
import uuid
from datetime import datetime

from structlog import wrap_logger

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.processor_interface import Processor
from toolbox.bulk_processing.validators import in_set, case_exists_by_id, is_uuid
from toolbox.config import Config
from toolbox.logger import logger_initial_config


class RefusalProcessor(Processor):
    file_prefix = Config.BULK_REFUSAL_FILE_PREFIX
    routing_key = Config.REFUSAL_EVENT_ROUTING_KEY
    exchange = Config.EVENTS_EXCHANGE
    bucket_name = Config.BULK_REFUSAL_BUCKET_NAME
    project_id = Config.BULK_REFUSAL_PROJECT_ID
    schema = {
        "case_id": [is_uuid(), case_exists_by_id()],
        "refusal_type": [in_set({"HARD_REFUSAL", "EXTRAORDINARY_REFUSAL"}, label='refusal types')]
    }

    def build_event_messages(self, row):
        return [{
            "event": {
                "type": "REFUSAL_RECEIVED",
                "source": "RM_BULK_REFUSAL_PROCESSOR",
                "channel": "RM",
                "dateTime": datetime.utcnow().isoformat() + 'Z',
                "transactionId": str(uuid.uuid4())
            },
            "payload": {
                "refusal": {
                    "type": row['refusal_type'],
                    "collectionCase": {
                        "id": row['case_id']
                    }
                }
            }
        }]


def main():
    logger_initial_config()
    logger = wrap_logger(logging.getLogger(__name__))
    logger.info('Started bulk processing refusals', app_log_level=Config.LOG_LEVEL, environment=Config.ENVIRONMENT)
    BulkProcessor(RefusalProcessor()).run()


if __name__ == "__main__":
    main()

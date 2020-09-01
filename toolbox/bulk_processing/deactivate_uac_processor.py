import uuid
from datetime import datetime

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.processor_interface import Processor
from toolbox.bulk_processing.validators import qid_exists
from toolbox.config import Config


class DeactivateUacProcessor(Processor):
    file_prefix = Config.BULK_DEACTIVATE_UAC_FILE_PREFIX
    routing_key = Config.DEACTIVATE_UAC_EVENT_ROUTING_KEY
    exchange = ''
    bucket_name = Config.BULK_DEACTIVATE_UAC_BUCKET_NAME
    project_id = Config.BULK_DEACTIVATE_UAC_PROJECT_ID

    schema = {
        "qid": [qid_exists()]
    }

    def build_event_messages(self, row):
        return [{
            "event": {
                "type": "DEACTIVATE_UAC",
                "source": "RM_BULK_DEACTIVATE_UAC_PROCESSOR",
                "channel": "RM",
                "dateTime": datetime.utcnow().isoformat() + 'Z',
                "transactionId": str(uuid.uuid4())
            },
            "payload": {
                "uac": {
                    "questionnaireId": row['qid']
                }
            }
        }]


def main():
    BulkProcessor(DeactivateUacProcessor()).run()


if __name__ == "__main__":
    main()

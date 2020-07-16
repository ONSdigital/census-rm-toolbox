import os
import uuid
from datetime import datetime

from bulk_processing.bulk_processor import BulkProcessor
from bulk_processing.processor_interface import Processor
from bulk_processing.validators import in_set, case_exists_by_id


class RefusalProcessor(Processor):
    file_prefix = os.getenv('BULK_REFUSAL_FILE_PREFIX', 'refusal_')
    routing_key = os.getenv('REFUSAL_EVENT_ROUTING_KEY', 'event.respondent.refusal')
    exchange = os.getenv('EVENTS_EXCHANGE', 'events')
    bucket_name = os.getenv('BULK_REFUSAL_BUCKET_NAME')
    project_id = os.getenv('PROJECT_ID')
    schema = {
        "case_id": [case_exists_by_id()],
        "refusal_type": [in_set({"HARD_REFUSAL", "EXTRAORDINARY_REFUSAL"})]
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
    BulkProcessor(RefusalProcessor()).run()


if __name__ == "__main__":
    main()

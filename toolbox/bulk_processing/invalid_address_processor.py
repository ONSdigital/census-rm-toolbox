import uuid
from datetime import datetime

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.processor_interface import Processor
from toolbox.bulk_processing.validators import case_exists_by_id, is_uuid, max_length, mandatory
from toolbox.config import Config


class InvalidAddressProcessor(Processor):
    file_prefix = Config.BULK_INVALID_ADDRESS_FILE_PREFIX
    routing_key = Config.INVALID_ADDRESS_EVENT_ROUTING_KEY
    exchange = Config.EVENTS_EXCHANGE
    bucket_name = Config.BULK_INVALID_ADDRESS_BUCKET_NAME
    project_id = Config.BULK_INVALID_ADDRESS_PROJECT_ID
    schema = {
        "case_id": [is_uuid(), case_exists_by_id()],
        "reason": [mandatory(), max_length(255)]
    }

    def build_event_messages(self, row):
        address_resolution = "AR"
        return [{
            "event": {
                "type": "ADDRESS_NOT_VALID",
                "source": "RM_BULK_INVALID_ADDRESS_PROCESSOR",
                "channel": address_resolution,
                "dateTime": datetime.utcnow().isoformat() + 'Z',
                "transactionId": str(uuid.uuid4())
            },
            "payload": {
                "invalidAddress": {
                    "reason": row['reason'],
                    "collectionCase": {
                        "id": row['case_id']
                    }
                }
            }
        }]


def main():
    BulkProcessor(InvalidAddressProcessor()).run()


if __name__ == "__main__":
    main()

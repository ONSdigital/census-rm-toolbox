import uuid
from datetime import datetime

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.processor_interface import Processor
from toolbox.bulk_processing.validators import case_exists_by_id, is_uuid
from toolbox.config import Config


class UnInvalidateAddressProcessor(Processor):
    file_prefix = Config.BULK_UNINVALIDATED_ADDRESS_FILE_PREFIX
    routing_key = Config.UNINVALIDATED_ADDRESS_EVENT_ROUTING_KEY
    exchange = ''
    bucket_name = Config.BULK_UNINVALIDATED_ADDRESS_BUCKET_NAME
    project_id = Config.BULK_UNINVALIDATED_ADDRESS_PROJECT_ID
    schema = {
        "CASE_ID": [is_uuid(), case_exists_by_id()]
    }

    def build_event_messages(self, row):
        address_resolution = "AR"
        return [{
            "event": {
                "type": "RM_UNINVALIDATE_ADDRESS",
                "source": "RM_UNINVALIDATE_ADDRESS_PROCESSOR",
                "channel": address_resolution,
                "dateTime": datetime.utcnow().isoformat() + 'Z',
                "transactionId": str(uuid.uuid4())
            },
            "payload": {
                "rmUnInvalidateAddress": {
                    "caseId": row['CASE_ID']
                }
            }
        }]


def main():
    BulkProcessor(UnInvalidateAddressProcessor()).run()


if __name__ == "__main__":
    main()

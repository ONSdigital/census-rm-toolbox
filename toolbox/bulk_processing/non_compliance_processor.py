import uuid
from datetime import datetime

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.processor_interface import Processor
from toolbox.bulk_processing.validators import alphanumeric_plus_hyphen_field_values, hh_case_exists_by_id, \
    in_set, is_uuid, max_length, no_padding_whitespace, no_pipe_character
from toolbox.config import Config


class NonComplianceProcessor(Processor):
    file_prefix = Config.BULK_NON_COMPLIANCE_FILE_PREFIX
    routing_key = Config.BULK_NON_COMPLIANCE_ROUTING_KEY
    exchange = ''
    bucket_name = Config.BULK_NON_COMPLIANCE_BUCKET_NAME
    project_id = Config.BULK_NON_COMPLIANCE_PROJECT_ID
    schema = {
        "CASE_ID": [is_uuid(), hh_case_exists_by_id()],
        "NC_STATUS": [in_set({"NCL", "NCF"}, label='non-compliance status')],
        "FIELDCOORDINATOR_ID": [max_length(10), no_padding_whitespace(), no_pipe_character(),
                                alphanumeric_plus_hyphen_field_values()],
        "FIELDOFFICER_ID": [max_length(13), no_padding_whitespace(), no_pipe_character(),
                            alphanumeric_plus_hyphen_field_values()]
    }

    def build_event_messages(self, row):
        return [{
            "event": {
                "type": "SELECTED_FOR_NON_COMPLIANCE",
                "source": "NON_COMPLIANCE",
                "channel": "NC",
                "dateTime": datetime.utcnow().isoformat() + 'Z',
                "transactionId": str(uuid.uuid4())
            },
            "payload": {
                "collectionCase": {
                    "id": row['CASE_ID'],
                    "fieldCoordinatorId": row['FIELDCOORDINATOR_ID'],
                    "fieldOfficerId": row['FIELDOFFICER_ID'],
                    "nonComplianceStatus": row['NC_STATUS'],
                }
            }
        }]


def main():
    BulkProcessor(NonComplianceProcessor()).run()


if __name__ == "__main__":
    main()

import argparse
import json
import os
import uuid
from datetime import datetime

from bulk_processing.bulk_processor import BulkProcessor
from bulk_processing.processor_interface import Processor
from bulk_processing.validators import set_equal, Invalid, in_set, case_exists_by_id, ValidationFailure


class RefusalProcessor(Processor):
    file_prefix = os.getenv('BULK_REFUSAL_FILE_PREFIX', 'refusal_')
    routing_key = os.getenv('REFUSAL_EVENT_ROUTING_KEY', 'event.respondent.refusal')
    exchange = os.getenv('EVENTS_EXCHANGE', 'events')
    bucket_name = os.getenv('BULK_REFUSAL_BUCKET_NAME', 'census-rm-adamhawtin-perf1-bulk-test')
    schema = {
        "case_id": [case_exists_by_id()],
        "refusal_type": [in_set({"HARD_REFUSAL", "EXTRAORDINARY_REFUSAL"})]
    }

    def build_event_messages(self, row):
        return [{
            "event": {
                "type": "REFUSAL_RECEIVED",
                "source": "RM",
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

    def publish_event_messages(self, event_messages, rabbit):
        for message in event_messages:
            rabbit.publish_message(json.dumps(message), 'application/json', None, exchange=self.EXCHANGE,
                                   routing_key=self.ROUTING_KEY)
            print('Successfully published')


def print_failures(failures, print_limit=20):
    print(f'{len(failures)} validation failure(s):')
    if len(failures) > print_limit:
        print_failures_summary(failures, print_limit)
    else:
        for failure in failures:
            print(build_failure_log(failure))


def build_failure_log(failure):
    return (f'line: {failure.line_number}, column: {failure.column}, description: {failure.description}'
            if failure.column else
            f'line: Header, description: {failure.description}'
            if failure.line_number else
            failure.description)


def print_failures_summary(failures, print_limit):
    for failure in failures[:print_limit]:
        print(build_failure_log(failure))
    response = input(f'Showing first {print_limit} of {len(failures)}. '
                     f'Show remaining {len(failures) - print_limit} [Y/n]?\n')
    if response.lower() in {'y', 'yes'}:
        for failure in failures[print_limit:]:
            print(build_failure_log(failure))


# def parse_arguments():
#     parser = argparse.ArgumentParser(description='Load a sample file into response management.')
#     parser.add_argument('refusal_file_path', help='path to the refusal file', type=str)
#     return parser.parse_args()


def main():
    # args = parse_arguments()
    # failures = BulkProcessor(RefusalProcessor()).test_run(args.refusal_file_path)
    BulkProcessor(RefusalProcessor()).run()
    # if failures:
    #     print_failures(failures)
    #     print(f'{args.refusal_file_path} is not valid ❌')
    # print(f'Success! {args.refusal_file_path} passed validation ✅')


if __name__ == "__main__":
    main()

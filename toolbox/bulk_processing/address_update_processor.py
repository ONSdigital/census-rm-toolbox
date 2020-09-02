import uuid
from datetime import datetime

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.processor_interface import Processor
from toolbox.bulk_processing.validators import mandatory, max_length, numeric, no_padding_whitespace,\
    no_pipe_character, alphanumeric_postcode, latitude_longitude, in_set, latitude_longitude_range, case_exists_by_id, \
    mandatory_after_update, cant_be_deleted, check_delete_keyword, \
    numeric_2_digit_or_delete, optional_in_set
from toolbox.config import Config

address_resolution = 'AR'


class AddressUpdateProcessor(Processor):
    file_prefix = Config.BULK_ADDRESS_UPDATE_FILE_PREFIX
    routing_key = Config.BULK_ADDRESS_UPDATE_ROUTING_KEY
    exchange = ''
    bucket_name = Config.BULK_ADDRESS_UPDATE_BUCKET_NAME
    project_id = Config.BULK_ADDRESS_UPDATE_PROJECT_ID
    schema = {
        'CASE_ID': [mandatory(), case_exists_by_id()],
        'UPRN': [max_length(13), numeric(), no_padding_whitespace(), cant_be_deleted(),
                 mandatory_after_update('uprn')],
        'ESTAB_UPRN': [max_length(13), numeric(), no_padding_whitespace(), cant_be_deleted(),
                       mandatory_after_update('estab_uprn')],
        'ESTAB_TYPE': [mandatory(), in_set(Config.ESTAB_TYPES, label='ESTAB_TYPE')],
        'ABP_CODE': [max_length(6), no_padding_whitespace(), no_pipe_character(), cant_be_deleted(),
                     mandatory_after_update('abp_code')],
        'ORGANISATION_NAME': [max_length(60), no_padding_whitespace(), no_pipe_character(), check_delete_keyword()],
        'ADDRESS_LINE1': [max_length(60), no_padding_whitespace(), no_pipe_character(),
                          cant_be_deleted(),
                          mandatory_after_update('address_line1')],
        'ADDRESS_LINE2': [max_length(60), no_padding_whitespace(), no_pipe_character(), check_delete_keyword()],
        'ADDRESS_LINE3': [max_length(60), no_padding_whitespace(), no_pipe_character(), check_delete_keyword()],
        'TOWN_NAME': [max_length(30), no_padding_whitespace(), no_pipe_character(), cant_be_deleted(),
                      mandatory_after_update('town_name')],
        'POSTCODE': [max_length(8), no_padding_whitespace(), cant_be_deleted(),
                     alphanumeric_postcode(), no_pipe_character(), mandatory_after_update('postcode')],
        'LATITUDE': [mandatory(), latitude_longitude(max_scale=7, max_precision=9), cant_be_deleted(),
                     no_padding_whitespace(), no_pipe_character(), latitude_longitude_range()],
        'LONGITUDE': [mandatory(), latitude_longitude(max_scale=7, max_precision=8), cant_be_deleted(),
                      no_padding_whitespace(), no_pipe_character(), latitude_longitude_range()],
        'OA': [mandatory(), max_length(9), no_padding_whitespace(), no_pipe_character(), cant_be_deleted()],
        'LSOA': [mandatory(), max_length(9), no_padding_whitespace(), no_pipe_character(), cant_be_deleted()],
        'MSOA': [mandatory(), max_length(9), no_padding_whitespace(), no_pipe_character(), cant_be_deleted()],
        'LAD': [mandatory(), max_length(9), no_padding_whitespace(), no_pipe_character(), cant_be_deleted()],
        'HTC_WILLINGNESS': [in_set({'0', '1', '2', '3', '4', '5'}, label='HTC_WILLINGNESS'),
                            mandatory_after_update('htc_willingness')],
        'HTC_DIGITAL': [in_set({'0', '1', '2', '3', '4', '5'}, label='HTC_DIGITAL'),
                        mandatory_after_update('htc_digital')],
        'TREATMENT_CODE': [mandatory(), in_set(Config.TREATMENT_CODES, label='TREATMENT_CODE')],
        'FIELDCOORDINATOR_ID': [mandatory(), max_length(10), no_padding_whitespace(), no_pipe_character(),
                                cant_be_deleted()],
        'FIELDOFFICER_ID': [mandatory(), max_length(13), no_padding_whitespace(), no_pipe_character(),
                            cant_be_deleted()],
        'CE_EXPECTED_CAPACITY': [numeric(), max_length(4), no_padding_whitespace()],
        'CE_SECURE': [optional_in_set({'0', '1'}, label='CE_SECURE'),
                      no_padding_whitespace()],
        'PRINT_BATCH': [no_padding_whitespace(), numeric_2_digit_or_delete(), check_delete_keyword()]
    }

    def build_event_messages(self, row):
        event_message = {
            "event": {
                "type": "RM_CASE_UPDATED",
                "source": "RM_BULK_ADDRESS_UPDATE_PROCESSOR",
                "channel": address_resolution,
                "dateTime": datetime.utcnow().isoformat() + 'Z',
                "transactionId": str(uuid.uuid4())
            },
            "payload": {
                "rmCaseUpdated": {
                    # Set the mandatory values up front
                    'caseId': row['CASE_ID'],
                    'treatmentCode': row['TREATMENT_CODE'],
                    'estabType': row['ESTAB_TYPE'],
                    'oa': row['OA'],
                    'lsoa': row['LSOA'],
                    'msoa': row['MSOA'],
                    'lad': row['LAD'],
                    'fieldCoordinatorId': row['FIELDCOORDINATOR_ID'],
                    'fieldOfficerId': row['FIELDOFFICER_ID'],
                    'latitude': row['LATITUDE'],
                    'longitude': row['LONGITUDE'],
                }
            }
        }

        # Set the optional values if present
        event_message = set_optional_values_if_present(row, event_message)

        # Set the deletable fields
        event_message = set_deleteable_fields(row, event_message)

        return [event_message]


def set_optional_values_if_present(row, event_message):
    if row['ADDRESS_LINE1']:
        event_message['payload']['rmCaseUpdated']['addressLine1'] = row['ADDRESS_LINE1']
    if row['TOWN_NAME']:
        event_message['payload']['rmCaseUpdated']['townName'] = row['TOWN_NAME']
    if row['POSTCODE']:
        event_message['payload']['rmCaseUpdated']['postcode'] = row['POSTCODE']
    if row['UPRN']:
        event_message['payload']['rmCaseUpdated']['uprn'] = row['UPRN']
    if row['ESTAB_UPRN']:
        event_message['payload']['rmCaseUpdated']['estabUprn'] = row['ESTAB_UPRN']
    if row['ABP_CODE']:
        event_message['payload']['rmCaseUpdated']['abpCode'] = row['ABP_CODE']
    if row['HTC_WILLINGNESS']:
        event_message['payload']['rmCaseUpdated']['htcWillingness'] = row['HTC_WILLINGNESS']
    if row['HTC_DIGITAL']:
        event_message['payload']['rmCaseUpdated']['htcDigital'] = row['HTC_DIGITAL']
    if row['CE_EXPECTED_CAPACITY']:
        event_message['payload']['rmCaseUpdated']['ceExpectedCapacity'] = row['CE_EXPECTED_CAPACITY']

    if row['CE_SECURE'] == '0':
        event_message['payload']['rmCaseUpdated']['secureEstablishment'] = False
    elif row['CE_SECURE'] == '1':
        event_message['payload']['rmCaseUpdated']['secureEstablishment'] = True

    return event_message


def set_deleteable_fields(row, event_message):
    if is_delete_keyword(row['ORGANISATION_NAME']):
        event_message['payload']['rmCaseUpdated']['organisationName'] = None
    elif row['ORGANISATION_NAME']:
        event_message['payload']['rmCaseUpdated']['organisationName'] = row['ORGANISATION_NAME']

    if is_delete_keyword(row['ADDRESS_LINE2']):
        event_message['payload']['rmCaseUpdated']['addressLine2'] = None
    elif row['ADDRESS_LINE2']:
        event_message['payload']['rmCaseUpdated']['addressLine2'] = row['ADDRESS_LINE2']

    if is_delete_keyword(row['ADDRESS_LINE3']):
        event_message['payload']['rmCaseUpdated']['addressLine3'] = None
    elif row['ADDRESS_LINE3']:
        event_message['payload']['rmCaseUpdated']['addressLine3'] = row['ADDRESS_LINE3']

    if is_delete_keyword(row['PRINT_BATCH']):
        event_message['payload']['rmCaseUpdated']['printBatch'] = None
    elif row['PRINT_BATCH']:
        event_message['payload']['rmCaseUpdated']['printBatch'] = row['PRINT_BATCH']

    return event_message


def is_delete_keyword(value: str):
    return value == '-----'


def main():
    BulkProcessor(AddressUpdateProcessor()).run()


if __name__ == '__main__':
    main()

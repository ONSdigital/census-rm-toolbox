from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.processor_interface import Processor
from toolbox.bulk_processing.validators import mandatory, max_length, numeric, \
    no_padding_whitespace, latitude_longitude, \
    in_set, region_matches_treatment_code, ce_u_has_expected_capacity, ce_e_has_expected_capacity, \
    alphanumeric_postcode, no_pipe_character, latitude_longitude_range, alphanumeric_plus_hyphen_field_values
from toolbox.config import Config


class NewAddressProcessor(Processor):
    file_prefix = Config.BULK_NEW_ADDRESS_FILE_PREFIX
    routing_key = Config.NEW_ADDRESS_EVENT_ROUTING_KEY
    exchange = ''
    bucket_name = Config.BULK_NEW_ADDRESS_BUCKET_NAME
    project_id = Config.BULK_NEW_ADDRESS_PROJECT_ID
    schema = {
        'UPRN': [mandatory(), max_length(13), numeric(), no_padding_whitespace()],
        'ESTAB_UPRN': [mandatory(), max_length(13), numeric(), no_padding_whitespace()],
        'ADDRESS_TYPE': [mandatory(), in_set({'HH', 'CE', 'SPG'}, label='ADDRESS_TYPE'),
                         no_padding_whitespace()],
        'ESTAB_TYPE': [mandatory(), in_set(Config.ESTAB_TYPES, label='ESTAB_TYPE')],
        'ADDRESS_LEVEL': [mandatory(), in_set({'E', 'U'}, label='ADDRESS_LEVEL'),
                          no_padding_whitespace()],
        'ABP_CODE': [mandatory(), max_length(6), no_padding_whitespace(), no_pipe_character()],
        'ORGANISATION_NAME': [max_length(60), no_padding_whitespace(), no_pipe_character()],
        'ADDRESS_LINE1': [mandatory(), max_length(60), no_padding_whitespace(), no_pipe_character()],
        'ADDRESS_LINE2': [max_length(60), no_padding_whitespace(), no_pipe_character()],
        'ADDRESS_LINE3': [max_length(60), no_padding_whitespace(), no_pipe_character()],
        'TOWN_NAME': [mandatory(), max_length(30), no_padding_whitespace(), no_pipe_character()],
        'POSTCODE': [mandatory(), max_length(8), no_padding_whitespace(),
                     alphanumeric_postcode(), no_pipe_character()],
        'LATITUDE': [mandatory(), latitude_longitude(max_scale=7, max_precision=9),
                     no_padding_whitespace(), no_pipe_character(), latitude_longitude_range()],
        'LONGITUDE': [mandatory(), latitude_longitude(max_scale=7, max_precision=8),
                      no_padding_whitespace(), no_pipe_character(), latitude_longitude_range()],
        'OA': [mandatory(), max_length(9), no_padding_whitespace(), no_pipe_character()],
        'LSOA': [mandatory(), max_length(9), no_padding_whitespace(), no_pipe_character()],
        'MSOA': [mandatory(), max_length(9), no_padding_whitespace(), no_pipe_character()],
        'LAD': [mandatory(), max_length(9), no_padding_whitespace(), no_pipe_character()],
        'REGION': [mandatory(), max_length(9), no_padding_whitespace(),
                   region_matches_treatment_code(), no_pipe_character()],
        'HTC_WILLINGNESS': [mandatory(), in_set({'0', '1', '2', '3', '4', '5'}, label='HTC_WILLINGNESS')],
        'HTC_DIGITAL': [mandatory(), in_set({'0', '1', '2', '3', '4', '5'}, label='HTC_DIGITAL')],
        'TREATMENT_CODE': [mandatory(), in_set(Config.TREATMENT_CODES, label='TREATMENT_CODE')],
        'FIELDCOORDINATOR_ID': [mandatory(), max_length(10), no_padding_whitespace(), no_pipe_character(),
                                alphanumeric_plus_hyphen_field_values()],
        'FIELDOFFICER_ID': [mandatory(), max_length(13), no_padding_whitespace(), no_pipe_character(),
                            alphanumeric_plus_hyphen_field_values()],
        'CE_EXPECTED_CAPACITY': [numeric(), max_length(4), no_padding_whitespace(),
                                 ce_u_has_expected_capacity(), ce_e_has_expected_capacity()],
        'CE_SECURE': [mandatory(), in_set({'0', '1'}, label='CE_SECURE'),
                      no_padding_whitespace()],
        'PRINT_BATCH': [numeric(), max_length(2), no_padding_whitespace()]
    }
    collection_exercise_id = Config.COLLECTION_EXERCISE_ID
    action_plan_id = Config.ACTION_PLAN_ID

    def __init__(self, **kwargs):
        if kwargs.get('action_plan_id'):
            self.action_plan_id = kwargs.get('action_plan_id')
        if not self.action_plan_id:
            raise RuntimeError('Missing ACTION_PLAN_ID configuration')

        if kwargs.get('collection_exercise_id'):
            self.collection_exercise_id = kwargs.get('collection_exercise_id')
        if not self.collection_exercise_id:
            raise RuntimeError('Missing COLLECTION_EXERCISE_ID configuration')

    def build_event_messages(self, row):
        return [{'uprn': row['UPRN'], 'estabUprn': row['ESTAB_UPRN'],
                 'addressType': row['ADDRESS_TYPE'], 'estabType': row['ESTAB_TYPE'],
                 'addressLevel': row['ADDRESS_LEVEL'], 'abpCode': row['ABP_CODE'],
                 'organisationName': row['ORGANISATION_NAME'],
                 'addressLine1': row['ADDRESS_LINE1'], 'addressLine2': row['ADDRESS_LINE2'],
                 'addressLine3': row['ADDRESS_LINE3'], 'townName': row['TOWN_NAME'],
                 'postcode': row['POSTCODE'], 'latitude': row['LATITUDE'],
                 'longitude': row['LONGITUDE'], 'oa': row['OA'],
                 'lsoa': row['LSOA'], 'msoa': row['MSOA'],
                 'lad': row['LAD'], 'region': row['REGION'],
                 'htcWillingness': row['HTC_WILLINGNESS'], 'htcDigital': row['HTC_DIGITAL'],
                 'fieldCoordinatorId': row['FIELDCOORDINATOR_ID'],
                 'fieldOfficerId': row['FIELDOFFICER_ID'],
                 'treatmentCode': row['TREATMENT_CODE'],
                 'ceExpectedCapacity': row['CE_EXPECTED_CAPACITY'],
                 'secureEstablishment': row['CE_SECURE'],
                 'printBatch': row['PRINT_BATCH'],
                 'collectionExerciseId': self.collection_exercise_id,
                 'actionPlanId': self.action_plan_id,
                 'bulkProcessed': True}]


def main():
    BulkProcessor(NewAddressProcessor()).run()


if __name__ == "__main__":
    main()

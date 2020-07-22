from bulk_processing.bulk_processor import BulkProcessor
from bulk_processing.processor_interface import Processor
from bulk_processing.validators import mandatory, max_length, numeric, no_padding_whitespace, latitude_longitude, \
    in_set, region_matches_treatment_code, ce_u_has_expected_capacity
from config import Config


class NewAddressProcessor(Processor):
    TREATMENT_CODES = {
        'HH_LF2R1E', 'HH_LF2R2E', 'HH_LF2R3AE', 'HH_LF2R3BE', 'HH_LF3R1E', 'HH_LF3R2E', 'HH_LF3R3AE', 'HH_LF3R3BE',
        'HH_LFNR1E', 'HH_LFNR2E', 'HH_LFNR3AE', 'HH_LFNR3BE', 'HH_LF2R1W', 'HH_LF2R2W', 'HH_LF2R3AW', 'HH_LF2R3BW',
        'HH_LF3R1W', 'HH_LF3R2W', 'HH_LF3R3AW', 'HH_LF3R3BW', 'HH_LFNR1W', 'HH_LFNR2W', 'HH_LFNR3AW', 'HH_LFNR3BW',
        'HH_1LSFN', 'HH_2LEFN', 'HH_QF2R1E', 'HH_QF2R2E', 'HH_QF2R3AE', 'HH_QF3R1E', 'HH_QF3R2E', 'HH_QF3R3AE',
        'HH_QFNR1E', 'HH_QFNR2E', 'HH_QFNR3AE', 'HH_QF2R1W', 'HH_QF2R2W', 'HH_QF2R3AW', 'HH_QF3R1W', 'HH_QF3R2W',
        'HH_QF3R3AW', 'HH_QFNR1W', 'HH_QFNR2W', 'HH_QFNR3AW', 'HH_3QSFN', 'SPG_QDHSE', 'SPG_QDHSW', 'SPG_LPHUE',
        'SPG_QDHUE', 'SPG_VDNEE', 'CE_QDIEE', 'SPG_VDNEW', 'CE_QDIEW', 'SPG_LPHUW', 'SPG_QDHUW', 'CE_LDIUE', 'CE_LDIUW'}

    ESTAB_TYPES = {'HALL OF RESIDENCE', 'CARE HOME', 'HOSPITAL', 'HOSPICE', 'MENTAL HEALTH HOSPITAL',
                   'MEDICAL CARE OTHER', 'BOARDING SCHOOL', 'LOW/MEDIUM SECURE MENTAL HEALTH',
                   'HIGH SECURE MENTAL HEALTH', 'HOTEL', 'YOUTH HOSTEL', 'HOSTEL', 'MILITARY SLA', 'MILITARY US',
                   'RELIGIOUS COMMUNITY', 'RESIDENTIAL CHILDRENS HOME', 'EDUCATION OTHER', 'PRISON',
                   'IMMIGRATION REMOVAL CENTRE', 'APPROVED PREMISES', 'ROUGH SLEEPER', 'STAFF ACCOMMODATION',
                   'CAMPHILL', 'HOLIDAY PARK', 'HOUSEHOLD', 'SHELTERED ACCOMMODATION', 'RESIDENTIAL CARAVAN',
                   'RESIDENTIAL BOAT', 'GATED APARTMENTS', 'MOD HOUSEHOLDS', 'FOREIGN OFFICES', 'CASTLES', 'GRT SITE',
                   'MILITARY SFA', 'EMBASSY', 'ROYAL HOUSEHOLD', 'CARAVAN SITE', 'MARINA', 'TRAVELLING PERSONS',
                   'TRANSIENT PERSONS'}

    file_prefix = Config.BULK_NEW_ADDRESS_FILE_PREFIX
    routing_key = Config.NEW_ADDRESS_EVENT_ROUTING_KEY
    exchange = ''
    bucket_name = Config.BULK_NEW_ADDRESS_BUCKET_NAME
    project_id = Config.BULK_NEW_ADDRESS_PROJECT_ID
    schema = {

        'UPRN': [mandatory(), max_length(12), numeric(), no_padding_whitespace()],
        'ESTAB_UPRN': [mandatory(), max_length(12), numeric(), mandatory(), no_padding_whitespace()],
        'ADDRESS_TYPE': [mandatory(), in_set({'HH', 'CE', 'SPG'}, label='address_types'), no_padding_whitespace()],
        'ESTAB_TYPE': [mandatory(), in_set(ESTAB_TYPES, label='estab types'), max_length(255), no_padding_whitespace()],
        'ADDRESS_LEVEL': [mandatory(), in_set({'E', 'U'}, label='address levels'), no_padding_whitespace()],
        'ABP_CODE': [mandatory(), max_length(6), no_padding_whitespace()],
        'ORGANISATION_NAME': [max_length(60), no_padding_whitespace()],
        'ADDRESS_LINE1': [mandatory(), max_length(60), no_padding_whitespace()],
        'ADDRESS_LINE2': [max_length(60), no_padding_whitespace()],
        'ADDRESS_LINE3': [max_length(60), no_padding_whitespace()],
        'TOWN_NAME': [mandatory(), max_length(30), no_padding_whitespace()],
        'POSTCODE': [mandatory(), max_length(8), no_padding_whitespace()],
        'LATITUDE': [mandatory(), latitude_longitude(max_scale=7, max_precision=9), no_padding_whitespace()],
        'LONGITUDE': [mandatory(), latitude_longitude(max_scale=7, max_precision=10), no_padding_whitespace()],
        'OA': [mandatory(), max_length(9), no_padding_whitespace()],
        'LSOA': [mandatory(), max_length(9), no_padding_whitespace()],
        'MSOA': [mandatory(), max_length(9), no_padding_whitespace()],
        'LAD': [mandatory(), max_length(9), no_padding_whitespace()],
        'REGION': [mandatory(), max_length(9), no_padding_whitespace(), region_matches_treatment_code()],
        'HTC_WILLINGNESS': [mandatory(), in_set({'0', '1', '2', '3', '4', '5'}, label='HTC_WILLINGNESS'),
                            no_padding_whitespace()],
        'HTC_DIGITAL': [mandatory(), in_set({'0', '1', '2', '3', '4', '5'}, label='htc digital'),
                        no_padding_whitespace()],
        'TREATMENT_CODE': [mandatory(), in_set(TREATMENT_CODES, label='treatment codes'), no_padding_whitespace()],
        'FIELDCOORDINATOR_ID': [max_length(10), no_padding_whitespace()],
        'FIELDOFFICER_ID': [max_length(13), no_padding_whitespace()],
        'CE_EXPECTED_CAPACITY': [numeric(), max_length(4), no_padding_whitespace(), ce_u_has_expected_capacity()],
        'CE_SECURE': [mandatory(), in_set({'0', '1'}, label='CE Secure'), no_padding_whitespace()],
        'PRINT_BATCH': [numeric(), max_length(2), no_padding_whitespace()]
    }
    collection_exercise_id = Config.COLLECTION_EXERCISE_ID
    action_plan_id = Config.ACTION_PLAN_ID

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

from collections import OrderedDict

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.new_address_processor import NewAddressProcessor
from toolbox.config import Config

new_address_row = OrderedDict(
    [('UPRN', '25058243579'), ('ESTAB_UPRN', '46170434880'), ('ADDRESS_TYPE', 'HH'), ('ESTAB_TYPE', 'HOUSEHOLD'),
     ('ADDRESS_LEVEL', 'U'), ('ABP_CODE', 'RD02'), ('ORGANISATION_NAME', ''),
     ('ADDRESS_LINE1', '200 Wannabe Dill Road'), ('ADDRESS_LINE2', ''), ('ADDRESS_LINE3', ''),
     ('TOWN_NAME', 'Rehydrate City'), ('POSTCODE', 'DM9 5PN'), ('LATITUDE', '76.6502'), ('LONGITUDE', '172.2746'),
     ('OA', 'N26259372'), ('LSOA', 'N12305708'), ('MSOA', 'N83847423'), ('LAD', 'N20125510'), ('REGION', 'N36046073'),
     ('HTC_WILLINGNESS', '3'), ('HTC_DIGITAL', '2'), ('TREATMENT_CODE', 'HH_1LSFN'), ('FIELDCOORDINATOR_ID', ''),
     ('FIELDOFFICER_ID', ''), ('CE_EXPECTED_CAPACITY', '0'), ('CE_SECURE', '0'), ('PRINT_BATCH', '35')])

file_headers = ['UPRN', 'ESTAB_UPRN', 'ADDRESS_TYPE', 'ESTAB_TYPE', 'ADDRESS_LEVEL', 'ABP_CODE', 'ORGANISATION_NAME',
                'ADDRESS_LINE1',
                'ADDRESS_LINE2', 'ADDRESS_LINE3', 'TOWN_NAME', 'POSTCODE', 'LATITUDE', 'LONGITUDE', 'OA', 'LSOA',
                'MSOA', 'LAD', 'REGION',
                'HTC_WILLINGNESS', 'HTC_DIGITAL', 'TREATMENT_CODE', 'FIELDCOORDINATOR_ID', 'FIELDOFFICER_ID',
                'CE_EXPECTED_CAPACITY', 'CE_SECURE', 'PRINT_BATCH']

file_headers_errors = ['ARID', 'ESTAB_UPRN', 'ADDRESS_TYPE', 'ESTAB_TYPE', 'ADDRESS_LEVEL', 'ABP_CODE',
                       'ORGANISATION_NAME',
                       'ADDRESS_LINE1',
                       'ADDRESS_LINE2', 'ADDRESS_LINE3', 'TOWN_NAME', 'POSTCODE', 'LATITUDE', 'LONGITUDE', 'OA', 'LSOA',
                       'MSOA', 'LAD', 'REGION',
                       'HTC_WILLINGNESS', 'HTC_DIGITAL', 'TREATMENT_CODE', 'FIELDCOORDINATOR_ID', 'FIELDOFFICER_ID',
                       'CE_EXPECTED_CAPACITY', 'CE_SECURE', 'PRINT_BATCH']


def test_new_address_processor_build_event_messages():
    # Given
    new_address_processor = NewAddressProcessor()

    # When
    events = new_address_processor.build_event_messages(new_address_row)

    # Then
    assert len(events) == 1, 'Should build one and only 1 create sample event message'
    assert events[0]['bulkProcessed'] is True
    assert events[0]['collectionExerciseId'] == Config.COLLECTION_EXERCISE_ID


def test_new_address_validation(patch_storage):
    result = BulkProcessor(NewAddressProcessor()).find_header_validation_errors(file_headers)

    assert result is None


def test_new_address_validation_errors_doesnt_match(patch_storage):
    result = BulkProcessor(NewAddressProcessor()).find_header_validation_errors(file_headers_errors)

    # ARID is no longer a column so using it as an example of causing the validation to fail.
    assert 'ARID' in result.description
    assert 'UPRN' in result.description


def test_new_address_validation_headers_empty(patch_storage):
    result = BulkProcessor(NewAddressProcessor()).find_header_validation_errors({})

    assert 'UPRN' in result.description
    assert 'Header row does not match expected' in result.description

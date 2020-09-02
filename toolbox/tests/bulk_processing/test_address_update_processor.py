from unittest.mock import patch

from toolbox.bulk_processing.address_update_processor import AddressUpdateProcessor
from toolbox.tests import unittest_helper


@patch('toolbox.bulk_processing.address_update_processor.datetime')
@patch('toolbox.bulk_processing.address_update_processor.uuid')
def test_build_event_messages_maximum_values(patched_uuid, patched_datetime):
    # Given
    datetime_value = 'some_date'
    patched_datetime.utcnow.return_value.isoformat.return_value = datetime_value

    transaction_id = 'test_id'
    patched_uuid.uuid4.return_value = transaction_id
    address_update_processor = AddressUpdateProcessor()

    row = {
        'CASE_ID': 'foo_case_id',
        'UPRN': 'foo_uprn',
        'ESTAB_UPRN': 'foo_estab_uprn',
        'ESTAB_TYPE': 'foo_ESTAB_TYPE',
        'ABP_CODE': 'foo_abp',
        'ORGANISATION_NAME': 'foo_incorporated',
        'ADDRESS_LINE1': 'foo flat1',
        'ADDRESS_LINE2': 'foo some road',
        'ADDRESS_LINE3': 'foo somewhere',
        'TOWN_NAME': 'foo some town',
        'POSTCODE': 'F00 BAR',
        'LATITUDE': '0.0',
        'LONGITUDE': '127.0',
        'OA': 'foo_1',
        'LSOA': 'foo_2',
        'MSOA': 'foo_3',
        'LAD': 'foo_4',
        'HTC_WILLINGNESS': '5',
        'HTC_DIGITAL': '3',
        'TREATMENT_CODE': 'FOO_CODE',
        'FIELDCOORDINATOR_ID': 'ABC123',
        'FIELDOFFICER_ID': 'XYZ999',
        'CE_EXPECTED_CAPACITY': '10',
        'CE_SECURE': '1',
        'PRINT_BATCH': '99',
    }

    event_message = address_update_processor.build_event_messages(row)

    unittest_helper.assertEqual(
        [{
            "event": {
                "type": "RM_CASE_UPDATED",
                "source": "RM_BULK_ADDRESS_UPDATE_PROCESSOR",
                "channel": 'AR',
                "dateTime": datetime_value + 'Z',
                "transactionId": transaction_id
            },
            "payload": {
                "rmCaseUpdated": {
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
                    'secureEstablishment': True,
                    'printBatch': row['PRINT_BATCH'],
                    'ceExpectedCapacity': row['CE_EXPECTED_CAPACITY'],
                    'htcWillingness': row['HTC_WILLINGNESS'],
                    'htcDigital': row['HTC_DIGITAL'],
                    'uprn': row['UPRN'],
                    'estabUprn': row['ESTAB_UPRN'],
                    'addressLine1': row['ADDRESS_LINE1'],
                    'addressLine2': row['ADDRESS_LINE2'],
                    'addressLine3': row['ADDRESS_LINE3'],
                    'abpCode': row['ABP_CODE'],
                    'organisationName': row['ORGANISATION_NAME'],
                    'postcode': row['POSTCODE'],
                    'townName': row['TOWN_NAME']
                }
            }
        }],
        event_message
    )


@patch('toolbox.bulk_processing.address_update_processor.datetime')
@patch('toolbox.bulk_processing.address_update_processor.uuid')
def test_build_event_messages_minimum_values(patched_uuid, patched_datetime):
    # Given
    datetime_value = 'some_date'
    patched_datetime.utcnow.return_value.isoformat.return_value = datetime_value

    transaction_id = 'test_id'
    patched_uuid.uuid4.return_value = transaction_id
    address_update_processor = AddressUpdateProcessor()

    row = {
        'CASE_ID': 'foo_case_id',
        'UPRN': '',
        'ESTAB_UPRN': '',
        'ESTAB_TYPE': '',
        'ABP_CODE': '',
        'ORGANISATION_NAME': '',
        'ADDRESS_LINE1': '',
        'ADDRESS_LINE2': '',
        'ADDRESS_LINE3': '',
        'TOWN_NAME': '',
        'POSTCODE': '',
        'LATITUDE': '0.0',
        'LONGITUDE': '127.0',
        'OA': 'foo_1',
        'LSOA': 'foo_2',
        'MSOA': 'foo_3',
        'LAD': 'foo_4',
        'HTC_WILLINGNESS': '',
        'HTC_DIGITAL': '',
        'TREATMENT_CODE': 'FOO_CODE',
        'FIELDCOORDINATOR_ID': 'ABC123',
        'FIELDOFFICER_ID': 'XYZ999',
        'CE_EXPECTED_CAPACITY': '',
        'CE_SECURE': '',
        'PRINT_BATCH': '',
    }

    event_message = address_update_processor.build_event_messages(row)

    unittest_helper.assertEqual(
        [{
            "event": {
                "type": "RM_CASE_UPDATED",
                "source": "RM_BULK_ADDRESS_UPDATE_PROCESSOR",
                "channel": 'AR',
                "dateTime": datetime_value + 'Z',
                "transactionId": transaction_id
            },
            "payload": {
                "rmCaseUpdated": {
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
        }],
        event_message
    )


@patch('toolbox.bulk_processing.address_update_processor.datetime')
@patch('toolbox.bulk_processing.address_update_processor.uuid')
def test_build_event_messages_all_deletable_values(patched_uuid, patched_datetime):
    # Given
    datetime_value = 'some_date'
    patched_datetime.utcnow.return_value.isoformat.return_value = datetime_value

    transaction_id = 'test_id'
    patched_uuid.uuid4.return_value = transaction_id
    address_update_processor = AddressUpdateProcessor()

    row = {
        'ORGANISATION_NAME': '-----',
        'ADDRESS_LINE2': '-----',
        'ADDRESS_LINE3': '-----',
        'PRINT_BATCH': '-----',
        'CASE_ID': 'foo_case_id',
        'UPRN': '',
        'ESTAB_UPRN': '',
        'ESTAB_TYPE': '',
        'ABP_CODE': '',
        'ADDRESS_LINE1': '',
        'TOWN_NAME': '',
        'POSTCODE': '',
        'LATITUDE': '0.0',
        'LONGITUDE': '127.0',
        'OA': 'foo_1',
        'LSOA': 'foo_2',
        'MSOA': 'foo_3',
        'LAD': 'foo_4',
        'HTC_WILLINGNESS': '',
        'HTC_DIGITAL': '',
        'TREATMENT_CODE': 'FOO_CODE',
        'FIELDCOORDINATOR_ID': 'ABC123',
        'FIELDOFFICER_ID': 'XYZ999',
        'CE_EXPECTED_CAPACITY': '',
        'CE_SECURE': '',
    }

    event_message = address_update_processor.build_event_messages(row)

    unittest_helper.assertEqual(
        [{
            "event": {
                "type": "RM_CASE_UPDATED",
                "source": "RM_BULK_ADDRESS_UPDATE_PROCESSOR",
                "channel": 'AR',
                "dateTime": datetime_value + 'Z',
                "transactionId": transaction_id
            },
            "payload": {
                "rmCaseUpdated": {
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
                    'organisationName': None,
                    'addressLine2': None,
                    'addressLine3': None,
                    'printBatch': None,
                }
            }
        }],
        event_message
    )


@patch('toolbox.bulk_processing.address_update_processor.datetime')
@patch('toolbox.bulk_processing.address_update_processor.uuid')
def test_build_event_messages_ce_secure_false(patched_uuid, patched_datetime):
    # Given
    datetime_value = 'some_date'
    patched_datetime.utcnow.return_value.isoformat.return_value = datetime_value

    transaction_id = 'test_id'
    patched_uuid.uuid4.return_value = transaction_id
    address_update_processor = AddressUpdateProcessor()

    row = {
        'CE_SECURE': '0',
        'CASE_ID': 'foo_case_id',
        'UPRN': '',
        'ESTAB_UPRN': '',
        'ESTAB_TYPE': '',
        'ABP_CODE': '',
        'ORGANISATION_NAME': '',
        'ADDRESS_LINE1': '',
        'ADDRESS_LINE2': '',
        'ADDRESS_LINE3': '',
        'TOWN_NAME': '',
        'POSTCODE': '',
        'LATITUDE': '0.0',
        'LONGITUDE': '127.0',
        'OA': 'foo_1',
        'LSOA': 'foo_2',
        'MSOA': 'foo_3',
        'LAD': 'foo_4',
        'HTC_WILLINGNESS': '',
        'HTC_DIGITAL': '',
        'TREATMENT_CODE': 'FOO_CODE',
        'FIELDCOORDINATOR_ID': 'ABC123',
        'FIELDOFFICER_ID': 'XYZ999',
        'CE_EXPECTED_CAPACITY': '',
        'PRINT_BATCH': '',
    }

    event_message = address_update_processor.build_event_messages(row)

    unittest_helper.assertEqual(
        [{
            "event": {
                "type": "RM_CASE_UPDATED",
                "source": "RM_BULK_ADDRESS_UPDATE_PROCESSOR",
                "channel": 'AR',
                "dateTime": datetime_value + 'Z',
                "transactionId": transaction_id
            },
            "payload": {
                "rmCaseUpdated": {
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
                    'secureEstablishment': False,
                }
            }
        }],
        event_message
    )

import uuid
from unittest.mock import patch

import pytest

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.invalid_address_processor import InvalidAddressProcessor


@pytest.mark.parametrize('case_id,reason',
                         [('test_case_id', 'TEST'),
                          (uuid.uuid4(), 'DEMOLISHED'),
                          (uuid.uuid4(), 'DOES_NOT_EXIST'),
                          ('anything', 'BLAH'), ])
def test_build_event_messages(case_id, reason):
    # Given
    invalid_address_processor = InvalidAddressProcessor()

    # When
    event_message = invalid_address_processor.build_event_messages({'case_id': case_id, 'reason': reason})

    # Then
    assert len(event_message) == 1, 'Should build one and only 1 invalid address event message'
    assert event_message[0]['event']['type'] == 'ADDRESS_NOT_VALID'
    assert event_message[0]['event']['transactionId'] is not None
    assert event_message[0]['event']['dateTime'] is not None
    assert event_message[0]['payload']['invalidAddress']['reason'] == reason
    assert event_message[0]['payload']['invalidAddress']['collectionCase']['id'] == case_id


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_invalid_address_validation_headers(_patched_storage_client):
    invalid_address_headers = ["case_id", "reason"]

    result = BulkProcessor(InvalidAddressProcessor()).find_header_validation_errors(invalid_address_headers)

    assert result is None


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_invalid_address_validation_headers_fails_invalid_address_reason(_patched_storage_client):
    invalid_address_headers = ["case_id", "r3ason"]

    result = BulkProcessor(InvalidAddressProcessor()).find_header_validation_errors(invalid_address_headers)

    assert result.line_number == 1
    assert "r3ason" in result.description
    assert "reason" in result.description


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_invalid_address_validation_headers_fails_case_id(_patched_storage_client):
    invalid_address_headers = ["not_a_case_id", "reason"]

    result = BulkProcessor(InvalidAddressProcessor()).find_header_validation_errors(invalid_address_headers)

    assert result.line_number == 1
    assert "not_a_case_id" in result.description
    assert "case_id" in result.description


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_invalid_address_validation_headers_fails_empty(_patched_storage_client):
    result = BulkProcessor(InvalidAddressProcessor()).find_header_validation_errors({})

    assert result.line_number == 1
    assert "reason" in result.description
    assert "case_id" in result.description

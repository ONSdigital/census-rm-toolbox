from unittest.mock import patch

import pytest

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.uninvalidate_address_processor import UnInvalidateAddressProcessor


@pytest.mark.parametrize('case_id',
                         [('test_case_id', 'TEST'),
                          ('anything', 'BLAH'), ])
def test_build_event_messages(case_id):
    # Given
    uninvalidate_address_processor = UnInvalidateAddressProcessor()

    # When
    event_message = uninvalidate_address_processor.build_event_messages({'case_id': case_id})

    # Then
    assert len(event_message) == 1, 'Should build one and only 1 invalid address event message'
    assert event_message[0]['event']['type'] == 'RM_UNINVALIDATE_ADDRESS'
    assert event_message[0]['event']['transactionId'] is not None
    assert event_message[0]['event']['dateTime'] is not None
    assert event_message[0]['payload']['rmUnInvalidateAddress']['id'] == case_id


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_uninvalidate_address_validation_headers(_patched_storage_client):
    invalid_address_headers = ["case_id"]

    result = BulkProcessor(UnInvalidateAddressProcessor()).find_header_validation_errors(invalid_address_headers)

    assert result is None


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_uninvalidate_address_validation_headers_fails_case_id(_patched_storage_client):
    invalid_address_headers = ["not_a_case_id"]

    result = BulkProcessor(UnInvalidateAddressProcessor()).find_header_validation_errors(invalid_address_headers)

    assert result.line_number == 1
    assert "not_a_case_id" in result.description
    assert "case_id" in result.description


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_uninvalidate_address_validation_headers_fails_empty(_patched_storage_client):
    result = BulkProcessor(UnInvalidateAddressProcessor()).find_header_validation_errors({})

    assert result.line_number == 1
    assert "case_id" in result.description

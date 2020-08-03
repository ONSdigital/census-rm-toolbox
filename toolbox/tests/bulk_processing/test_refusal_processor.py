import uuid
from unittest.mock import patch

import pytest

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.refusal_processor import RefusalProcessor


@pytest.mark.parametrize('case_id,refusal_type',
                         [('test_case_id', 'TEST'),
                          (uuid.uuid4(), 'HARD_REFUSAL'),
                          (uuid.uuid4(), 'EXTRAORDINARY_REFUSAL'),
                          ('anything', 'BLAH'), ])
def test_build_event_messages(case_id, refusal_type):
    # Given
    refusal_processor = RefusalProcessor()

    # When
    event_messages = refusal_processor.build_event_messages({'case_id': case_id, 'refusal_type': refusal_type})

    # Then
    assert len(event_messages) == 1, 'Should build one and only 1 refusal event message'
    assert event_messages[0]['event']['type'] == 'REFUSAL_RECEIVED'
    assert event_messages[0]['event']['transactionId'] is not None
    assert event_messages[0]['event']['dateTime'] is not None
    assert event_messages[0]['payload']['refusal']['type'] == refusal_type
    assert event_messages[0]['payload']['refusal']['collectionCase']['id'] == case_id


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_refusal_validation_headers(_patched_storage_client):
    refusal_headers = ["case_id", "refusal_type"]

    result = BulkProcessor(RefusalProcessor()).find_header_validation_errors(refusal_headers)

    assert result is None


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_refusal_validation_headers_fails_refusal_type(_patched_storage_client):
    refusal_headers = ["case_id", "refusal_pyte"]

    result = BulkProcessor(RefusalProcessor()).find_header_validation_errors(refusal_headers)

    assert result.line_number == 1
    assert "refusal_pyte" in result.description
    assert "refusal_type" in result.description


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_refusal_validation_headers_fails_case_id(_patched_storage_client):
    refusal_headers = ["not_a_case_id", "refusal_type"]

    result = BulkProcessor(RefusalProcessor()).find_header_validation_errors(refusal_headers)

    assert result.line_number == 1
    assert "not_a_case_id" in result.description
    assert "case_id" in result.description


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_refusal_validation_headers_fails_empty(_patched_storage_client):
    result = BulkProcessor(RefusalProcessor()).find_header_validation_errors({})

    assert result.line_number == 1
    assert "refusal_type" in result.description
    assert "case_id" in result.description

from unittest.mock import patch

from bulk_processing.bulk_processor import BulkProcessor
from bulk_processing.refusal_processor import RefusalProcessor


@patch('bulk_processing.bulk_processor.storage')
def test_refusal_validation_headers(_patched_storage_client):
    refusal_headers = {"case_id", "refusal_type"}

    result = BulkProcessor(RefusalProcessor()).find_header_validation_failures(refusal_headers)

    assert result is None


@patch('bulk_processing.bulk_processor.storage')
def test_refusal_validation_headers_fails_refusal_type(_patched_storage_client):
    refusal_headers = {"case_id", "refusal_pyte"}

    result = BulkProcessor(RefusalProcessor()).find_header_validation_failures(refusal_headers)

    assert result.line_number == 1
    assert "refusal_pyte" in result.description
    assert "refusal_type" in result.description


@patch('bulk_processing.bulk_processor.storage')
def test_refusal_validation_headers_fails_case_id(_patched_storage_client):
    refusal_headers = {"not_a_case_id", "refusal_type"}

    result = BulkProcessor(RefusalProcessor()).find_header_validation_failures(refusal_headers)

    assert result.line_number == 1
    assert "not_a_case_id" in result.description
    assert "case_id" in result.description


@patch('bulk_processing.bulk_processor.storage')
def test_refusal_validation_headers_fails_empty(_patched_storage_client ):
    result = BulkProcessor(RefusalProcessor()).find_header_validation_failures({})

    assert result.line_number == 1
    assert "refusal_type" in result.description
    assert "case_id" in result.description

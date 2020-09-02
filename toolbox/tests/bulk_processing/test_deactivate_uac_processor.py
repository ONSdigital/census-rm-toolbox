from unittest.mock import patch

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.deactivate_uac_processor import DeactivateUacProcessor


def test_build_event_messages():
    # Given
    deactivate_uac_processor = DeactivateUacProcessor()

    # When
    event_messages = deactivate_uac_processor.build_event_messages({'qid': 'test_qid'})

    # Then
    assert len(event_messages) == 1, 'Should build one and only 1 qid deactived event message'
    assert event_messages[0]['event']['type'] == 'DEACTIVATE_UAC'
    assert event_messages[0]['event']['transactionId'] is not None
    assert event_messages[0]['event']['dateTime'] is not None
    assert event_messages[0]['payload']['uac']['questionnaireId'] == 'test_qid'


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_deactivate_uac_validation_headers(_patched_storage_client):
    deactivate_uac_headers = ["qid"]

    result = BulkProcessor(DeactivateUacProcessor()).find_header_validation_errors(deactivate_uac_headers)

    assert result is None


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_deactivate_uac_validation_headers_fails(_patched_storage_client):
    deactivate_uac_headers = ["quid pro quo"]

    result = BulkProcessor(DeactivateUacProcessor()).find_header_validation_errors(deactivate_uac_headers)

    assert result.line_number == 1
    assert "qid" in result.description
    assert "quid pro quo" in result.description


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_deactivate_uac_validation_headers_fails_empty(_patched_storage_client):
    result = BulkProcessor(DeactivateUacProcessor()).find_header_validation_errors({})

    assert result.line_number == 1
    assert "qid" in result.description

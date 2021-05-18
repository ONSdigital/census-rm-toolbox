import uuid
from unittest.mock import patch

import pytest

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.qid_link_processor import QidLinkProcessor


@pytest.mark.parametrize('case_id,qid',
                         [('test_case_id', 'TEST'),
                          (uuid.uuid4(), '1234'), ])
def test_build_event_messages(case_id, qid):
    # Given
    qid_link_processor = QidLinkProcessor()

    # When
    event_messages = qid_link_processor.build_event_messages({'case_id': case_id, 'qid': qid})

    # Then
    assert len(event_messages) == 1, 'Should build one and only 1 QID link event message'
    assert event_messages[0]['event']['type'] == 'QUESTIONNAIRE_LINKED'
    assert event_messages[0]['event']['transactionId'] is not None
    assert event_messages[0]['event']['dateTime'] is not None
    assert event_messages[0]['payload']['uac']['caseId'] == case_id
    assert event_messages[0]['payload']['uac']['questionnaireId'] == qid


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_qid_link_validation_headers(_patched_storage_client):
    refusal_headers = ["case_id", "qid"]

    result = BulkProcessor(QidLinkProcessor()).find_header_validation_errors(refusal_headers)

    assert result is None


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_qid_link_validation_headers_fails_case_id(_patched_storage_client):
    refusal_headers = ["notcaseid", "qid"]

    result = BulkProcessor(QidLinkProcessor()).find_header_validation_errors(refusal_headers)

    assert result.line_number == 1
    assert "notcaseid" in result.description
    assert "case_id" in result.description


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_qid_link_validation_headers_fails_qid(_patched_storage_client):
    refusal_headers = ["case_id", "notqid"]

    result = BulkProcessor(QidLinkProcessor()).find_header_validation_errors(refusal_headers)

    assert result.line_number == 1
    assert "notqid" in result.description
    assert "qid" in result.description


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_qid_link_validation_headers_fails_empty(_patched_storage_client):
    result = BulkProcessor(QidLinkProcessor()).find_header_validation_errors({})

    assert result.line_number == 1
    assert "case_id" in result.description
    assert "qid" in result.description

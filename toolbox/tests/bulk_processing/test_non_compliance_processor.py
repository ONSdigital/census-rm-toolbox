import uuid
from unittest.mock import patch

import pytest

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.non_compliance_processor import NonComplianceProcessor


@pytest.mark.parametrize('case_id,nc_status,fieldcoordinator_id,fieldofficer_id',
                         [('test_case_id', 'TEST', 'ABC123', 'XYZ321'),
                          (uuid.uuid4(), 'NCL', '', ''),
                          (uuid.uuid4(), 'NCF', '123', '321'),
                          ('anything', 'BLAH', 'DE', 'BLAH'), ])
def test_build_event_messages(case_id, nc_status, fieldcoordinator_id, fieldofficer_id):
    # Given
    non_compliance_processor = NonComplianceProcessor()

    # When
    event_messages = non_compliance_processor.build_event_messages(
        {'CASE_ID': case_id, 'NC_STATUS': nc_status, 'FIELDCOORDINATOR_ID': fieldcoordinator_id,
         'FIELDOFFICER_ID': fieldofficer_id})

    # Then
    assert len(event_messages) == 1, 'Should build one and only 1 refusal event message'
    assert event_messages[0]['event']['type'] == 'SELECTED_FOR_NON_COMPLIANCE'
    assert event_messages[0]['event']['transactionId'] is not None
    assert event_messages[0]['event']['dateTime'] is not None
    assert event_messages[0]['payload']['collectionCase']['id'] == case_id
    assert event_messages[0]['payload']['collectionCase']['fieldCoordinatorId'] == fieldcoordinator_id
    assert event_messages[0]['payload']['collectionCase']['fieldOfficerId'] == fieldofficer_id
    assert event_messages[0]['payload']['collectionCase']['nonComplianceStatus'] == nc_status


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_non_compliance_validation_headers(_patched_storage_client):
    refusal_headers = ["CASE_ID", "NC_STATUS", "FIELDCOORDINATOR_ID", "FIELDOFFICER_ID"]

    result = BulkProcessor(NonComplianceProcessor()).find_header_validation_errors(refusal_headers)

    assert result is None


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_non_compliance_validation_headers_fail(_patched_storage_client):
    refusal_headers = ["ID", "NC_STAT", "FIELDCOORDINATORID", "FIELDOFFICERID"]

    result = BulkProcessor(NonComplianceProcessor()).find_header_validation_errors(refusal_headers)

    assert result.line_number == 1
    assert "ID" in result.description
    assert "CASE_ID" in result.description
    assert "NC_STAT" in result.description
    assert "FIELDCOORDINATORID" in result.description
    assert "FIELDOFFICERID" in result.description


@patch('toolbox.bulk_processing.bulk_processor.storage')
def test_non_compliance_validation_headers_fails_empty(_patched_storage_client):
    result = BulkProcessor(NonComplianceProcessor()).find_header_validation_errors({})

    assert result.line_number == 1
    assert "CASE_ID" in result.description
    assert "NC_STATUS" in result.description

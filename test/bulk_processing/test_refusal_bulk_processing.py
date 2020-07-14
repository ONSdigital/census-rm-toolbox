from unittest.mock import patch

import pytest

from bulk_processing.refusal_bulk_processing import RefusalProcessor


def test_refusal_validation_headers():
    refusal_headers = {"case_id", "refusal_type"}

    result = RefusalProcessor().find_header_validation_failures(refusal_headers)

    assert result is None


def test_refusal_validation_headers_fails():
    refusal_headers = {"case_id", "refusal_pyte"}

    result = RefusalProcessor().find_header_validation_failures(refusal_headers)

    assert result.line_number == 1
    assert "refusal_pyte" in result.description
    assert "refusal_type" in result.description


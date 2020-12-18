from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from toolbox.tests import unittest_helper
from toolbox.utilities.reminder_helper import check_lsoa, get_lsoas_from_file, check_lsoas


@patch("builtins.open", new_callable=mock_open, read_data="E00000001\nE00000002")
def test_get_lsoas_list(_mock_csv_data):
    # Given
    mock_file = Path('lsoas.csv')
    expected_lsoas = ['E00000001', 'E00000002']

    # When
    actual_lsoas = get_lsoas_from_file(mock_file)

    # Then
    unittest_helper.assertEqual(actual_lsoas, expected_lsoas,
                                'Generated LSOAs should match expected')


def test_check_lsoas_exit():
    # Given
    lsoas = ["E00000001", "'E00000002'"]

    # When, Then
    with pytest.raises(SystemExit):
        check_lsoas(lsoas)


def test_check_lsoa_is_valid():
    unittest_helper.assertEqual([], check_lsoa(1, "E00000001"))


def test_check_lsoa_invalid_format():
    expected_error = ['Row: 1, LSOA "E1000000\'" is not alphanumeric']
    unittest_helper.assertEqual(expected_error, check_lsoa(1, "E1000000'"))


def test_check_lsoa_invalid_length():
    expected_error = ["Row: 1, LSOA 'E000000001' is too long"]
    unittest_helper.assertEqual(expected_error, check_lsoa(1, "E000000001"))


def test_check_lsoa_invalid_format_and_length():
    expected_error = [
        'Row: 1, LSOA "\'E000000001\'" is not alphanumeric',
        'Row: 1, LSOA "\'E000000001\'" is too long'
    ]
    unittest_helper.assertEqual(expected_error, check_lsoa(1, "'E000000001'"))

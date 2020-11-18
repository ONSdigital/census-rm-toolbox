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


def test_check_lsoas_():
    unittest_helper.assertTrue(check_lsoa(1, "E00000001"))


def test_check_lsoa_is_valid():
    unittest_helper.assertTrue(check_lsoa(1, "E00000001"))


def test_check_lsoa_invalid_format():
    unittest_helper.assertFalse(check_lsoa(1, "'E100000001'"))


def test_check_lsoa_invalid_length():
    unittest_helper.assertFalse(check_lsoa(1, "E0000001"))

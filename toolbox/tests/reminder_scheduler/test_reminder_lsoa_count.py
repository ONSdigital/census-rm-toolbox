import uuid
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from toolbox.reminder_scheduler import reminder_lsoa_count
from toolbox.tests import unittest_helper

TEST_ACTION_PLAN_ID = uuid.UUID('6597821B-4D6A-48C4-B249-45C010A57EB1')


@patch('toolbox.reminder_scheduler.reminder_lsoa_count.db_helper')
@patch("builtins.open", new_callable=mock_open, read_data="E00000001")
def test_main(_mock_csv_data, patch_db_helper):
    # Given
    mock_file = Path('lsoas.csv')

    # When
    reminder_lsoa_count.main(mock_file, TEST_ACTION_PLAN_ID)

    # Then
    patch_db_helper.execute_parametrized_sql_query.assert_called_once()


def test_build_lsoas_count_query():
    # Given
    lsoas = ['E00000001', 'E00000002']

    expected_count_query = "SELECT COUNT(*) " \
                           "FROM actionv2.cases " \
                           "WHERE action_plan_id = %s " \
                           "AND receipt_received = 'f' " \
                           "AND address_invalid = 'f' " \
                           "AND skeleton = 'f' " \
                           "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL' " \
                           "AND case_type = 'HH' " \
                           "AND lsoa IN %s; "

    expected_count_values = (str(TEST_ACTION_PLAN_ID), ('E00000001', 'E00000002'))

    # When
    actual_count_query, actual_query_values = reminder_lsoa_count.build_lsoas_count_query(TEST_ACTION_PLAN_ID, lsoas)

    # Then
    unittest_helper.assertEqual(actual_count_query, expected_count_query,
                                'Generated count query should match expected')
    unittest_helper.assertEqual(actual_query_values, expected_count_values,
                                'Generated count values match expected')


@patch('toolbox.reminder_scheduler.reminder_lsoa.db_helper')
@patch("builtins.open", new_callable=mock_open, read_data="'E00000001'")
def test_main_invalid_lsoa_causes_exit(_mock_csv_data, patch_db_helper):
    # Given
    mock_file = Path('lsoas.csv')

    # When
    with pytest.raises(SystemExit):
        reminder_lsoa_count.main(mock_file, TEST_ACTION_PLAN_ID)

    patch_db_helper.execute_parametrized_sql_query.assert_not_called()

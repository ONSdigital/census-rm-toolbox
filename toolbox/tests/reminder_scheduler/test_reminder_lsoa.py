import uuid
from pathlib import Path
from unittest.mock import patch, mock_open, ANY

import pytest
import rfc3339

from toolbox.reminder_scheduler import reminder_lsoa
from toolbox.tests import unittest_helper

TEST_DATE_TIME = rfc3339.parse_datetime('2020-06-26T06:39:34+00:00')
TEST_ACTION_PLAN_ID = uuid.UUID('6597821B-4D6A-48C4-B249-45C010A57EB1')


@patch('toolbox.reminder_scheduler.reminder_lsoa.db_helper')
@patch("builtins.open", new_callable=mock_open, read_data="E00000001")
def test_main_without_db_insert_rule(_mock_csv_data, patch_db_helper):
    # Given
    mock_file = Path('lsoas.csv')

    # When
    reminder_lsoa.main(mock_file, "P_RD_RNP41", TEST_ACTION_PLAN_ID)

    # Then
    patch_db_helper.execute_sql_query_with_write.assert_not_called()


@patch('toolbox.reminder_scheduler.reminder_lsoa.db_helper')
@patch('toolbox.reminder_scheduler.reminder_lsoa.input')
@patch("builtins.open", new_callable=mock_open, read_data="E00000001")
def test_main_with_db_insert_rule(_mock_csv_data, patch_input, patch_db_helper):
    # Given
    patch_input.return_value = 'Y'
    mock_file = Path('lsoas.csv')

    # When
    reminder_lsoa.main(mock_file, "P_RD_RNP41", TEST_ACTION_PLAN_ID, insert_rule=True, trigger_date_time=TEST_DATE_TIME)

    # Then
    patch_input.assert_called_once()
    patch_db_helper.execute_sql_query_with_write.assert_called_once_with(ANY, ANY, ANY, suppress_sql_print=True)


@patch('toolbox.reminder_scheduler.reminder_lsoa.db_helper')
@patch('toolbox.reminder_scheduler.reminder_lsoa.input')
@patch("builtins.open", new_callable=mock_open, read_data="E00000001")
def test_main_with_db_insert_rule_backout(_mock_csv_data, patch_input, patch_db_helper):
    # Given
    patch_input.return_value = 'n'
    mock_file = Path('lsoas.csv')

    # When
    reminder_lsoa.main(mock_file, "P_RD_RNP41", TEST_ACTION_PLAN_ID, insert_rule=True, trigger_date_time=TEST_DATE_TIME)

    # Then
    patch_input.assert_called_once()
    patch_db_helper.open_write_cursor.assert_not_called()
    patch_db_helper.execute_sql_query_with_write.assert_not_called()


def test_build_action_rule_classifiers():
    # Given
    lsoas = ['E00000001', 'E00000002']
    expected_classifiers = "case_type = 'HH' " \
                           "AND lsoa IN ('E00000001', 'E00000002')"

    # When
    action_rule_classifiers = reminder_lsoa.build_action_rule_classifiers(lsoas)

    # Then
    unittest_helper.assertEqual(action_rule_classifiers, expected_classifiers,
                                'Generated classifiers should match expected')


@patch('toolbox.reminder_scheduler.reminder_lsoa.db_helper')
@patch("builtins.open", new_callable=mock_open, read_data="'E00000001'")
def test_main_invalid_lsoa_causes_exit(_mock_csv_data, patch_db_helper):
    # Given
    mock_file = Path('lsoas.csv')

    # When
    with pytest.raises(SystemExit):
        reminder_lsoa.main(mock_file, "P_RD_RNP41", TEST_ACTION_PLAN_ID, insert_rule=True,
                           trigger_date_time=TEST_DATE_TIME)

    patch_db_helper.open_write_cursor.assert_not_called()
    patch_db_helper.execute_sql_query_with_write.assert_not_called()


def test_generate_action_rules():
    # Given
    action_plan_id = 'test_action_plan_id'
    action_type = 'DUMMY_TEST'
    action_rule_classifiers = "lsoa IN ('E00000001', 'E00000002')"

    # When
    action_rules = reminder_lsoa.generate_action_rule(action_type, action_rule_classifiers, action_plan_id,
                                                      TEST_DATE_TIME)

    action_rule_id = list(action_rules)[1][0]
    expected_action_rules = (
        "INSERT INTO actionv2.action_rule "
        "(id, action_type, classifiers_clause, trigger_date_time, action_plan_id, has_triggered) "
        "VALUES (%s, %s, %s, %s, %s, %s);",
        (action_rule_id, action_type, action_rule_classifiers, TEST_DATE_TIME, action_plan_id, False)
    )

    # Then
    unittest_helper.assertEqual(expected_action_rules, action_rules,
                                'The generated action rule should match expected')

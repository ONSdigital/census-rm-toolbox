import uuid
from unittest.mock import patch

import pytest
import rfc3339

from toolbox.reminder_scheduler import reminder_batch
from toolbox.tests import unittest_helper

TEST_CASES = [
    # starting_batch, expected_number_of_batches, max_cases, count_per_batch
    (0, 0, 1, 2),
    (0, 1, 10, 10),
    (0, 2, 25, 10),
    (1, 3, 30, 10),
    (10, 10, 100, 10),
    (1, 99, 1000, 10),
    (1, 24, 2500000, 100001),
    (1, 12, 2500000, 200000),
    (50, 12, 2500000, 200000),
    (1, 0, 2500000, 2500001),
    (50, 0, 2500000, 2500001),
]
TEST_DATE_TIME = rfc3339.parse_datetime('2020-06-26T06:39:34+00:00')
TEST_ACTION_PLAN_ID = uuid.UUID('6597821B-4D6A-48C4-B249-45C010A57EB1')
TEST_BATCH_COUNT = "','".join([str(i) for i in range(1, 99)])


@pytest.mark.parametrize(
    'starting_batch, expected_number_of_batches, max_cases, count_per_batch', TEST_CASES)
@patch('toolbox.reminder_scheduler.reminder_batch.db_helper')
def test_main(patch_db_helper, starting_batch, expected_number_of_batches, max_cases, count_per_batch):
    # Given
    patch_db_helper.execute_parametrized_sql_query.return_value = ((count_per_batch,),)
    expected_number_of_database_counts = get_expected_number_of_database_counts(expected_number_of_batches)

    # When
    reminder_batch.main(1, starting_batch, max_cases, TEST_ACTION_PLAN_ID)

    # Then
    unittest_helper.assertEqual(expected_number_of_database_counts,
                                patch_db_helper.execute_parametrized_sql_query.call_count)
    patch_db_helper.execute_sql_query_with_write.assert_not_called()


@pytest.mark.parametrize(
    'starting_batch, expected_number_of_batches, max_cases, count_per_batch', TEST_CASES)
@patch('toolbox.reminder_scheduler.reminder_batch.db_helper')
@patch('toolbox.reminder_scheduler.reminder_batch.input')
def test_main_insert_rules(patch_input, patch_db_helper, starting_batch, expected_number_of_batches, max_cases,
                           count_per_batch):
    # Given
    patch_db_helper.execute_parametrized_sql_query.return_value = ((count_per_batch,),)
    patch_input.return_value = 'Y'
    expected_number_of_database_counts = get_expected_number_of_database_counts(expected_number_of_batches)

    # When
    reminder_batch.main(1, starting_batch, max_cases, TEST_ACTION_PLAN_ID, insert_rules=True,
                        trigger_date_time=TEST_DATE_TIME)

    # Then
    unittest_helper.assertEqual(expected_number_of_database_counts,
                                patch_db_helper.execute_parametrized_sql_query.call_count)
    if expected_number_of_batches:
        patch_input.assert_called_once()
        unittest_helper.assertEqual(2, patch_db_helper.execute_sql_query_with_write.call_count)


@pytest.mark.parametrize('confirmation_string', ['n', 'N', '', 'no', "STOP"])
@patch('toolbox.reminder_scheduler.reminder_batch.db_helper')
@patch('toolbox.reminder_scheduler.reminder_batch.input')
def test_main_insert_rules_backout(patch_input, patch_db_helper, confirmation_string):
    # Given
    patch_db_helper.execute_parametrized_sql_query.return_value = ((1,),)
    patch_input.return_value = confirmation_string

    # When
    reminder_batch.main(1, 1, 1, TEST_ACTION_PLAN_ID, insert_rules=True, trigger_date_time=TEST_DATE_TIME)

    # Then
    patch_input.assert_called_once()
    patch_db_helper.open_write_cursor.assert_not_called()
    patch_db_helper.execute_sql_query_with_write.assert_not_called()


@pytest.mark.parametrize(
    'starting_batch, expected_number_of_batches, max_cases, count_per_batch', TEST_CASES)
@patch('toolbox.reminder_scheduler.reminder_batch.db_helper.execute_parametrized_sql_query')
def test_select_batches(patch_execute_sql, starting_batch, expected_number_of_batches, max_cases, count_per_batch):
    # Given
    # Mock the database to return a constant count
    patch_execute_sql.return_value = ((count_per_batch,),)

    # We can use empty classifiers because the DB bit is mocked
    empty_classifiers = ""

    expected_batches = [str(batch) for batch in
                        list(range(starting_batch, starting_batch + expected_number_of_batches))]

    expected_number_of_database_counts = get_expected_number_of_database_counts(expected_number_of_batches)

    # When
    selected_batches = reminder_batch.select_batches(starting_batch, empty_classifiers, max_cases, TEST_ACTION_PLAN_ID)

    # Then
    for count in selected_batches.values():
        unittest_helper.assertEqual(count_per_batch, count,
                                    'The correct batch count should be stored for each selected batch')

    unittest_helper.assertEqual(expected_batches, list(selected_batches.keys()),
                                'The selected print batches should be every value between our expected first and last'
                                ' (as strings)')

    unittest_helper.assertEqual(expected_number_of_database_counts, patch_execute_sql.call_count,
                                'The number of database counts should match our expectation')


@pytest.mark.parametrize('batch, wave_classifiers, expected_query, expected_params', [
    # Test cases
    # Simple treatment code classifier
    (1, "treatment_code IN ('HH_DUMMY1', 'HH_DUMMY2')",
     ("SELECT COUNT(*) FROM actionv2.cases "
      "WHERE receipt_received = 'f' AND address_invalid = 'f' AND skeleton = 'f' "
      "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL' "
      "AND case_type != 'HI' "
      "AND action_plan_id = %s "
      "AND treatment_code IN ('HH_DUMMY1', 'HH_DUMMY2') "
      "AND print_batch = %s;"),
     (str(TEST_ACTION_PLAN_ID), '1'),
     ),

    # Classifier with just one value
    (10, "survey_launched IN ('f')",
     ("SELECT COUNT(*) FROM actionv2.cases "
      "WHERE receipt_received = 'f' AND address_invalid = 'f' AND skeleton = 'f' "
      "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL' "
      "AND case_type != 'HI' "
      "AND action_plan_id = %s "
      "AND survey_launched IN ('f') "
      "AND print_batch = %s;"),
     (str(TEST_ACTION_PLAN_ID), '10')),

    # Mix of classifiers
    (99, "treatment_code in ('HH_DUMMY1', 'HH_DUMMY2') AND survey_launched IN ('f')",
     ("SELECT COUNT(*) FROM actionv2.cases "
      "WHERE receipt_received = 'f' AND address_invalid = 'f' AND skeleton = 'f' "
      "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL' "
      "AND case_type != 'HI' "
      "AND action_plan_id = %s "
      "AND treatment_code in ('HH_DUMMY1', 'HH_DUMMY2') "
      "AND survey_launched IN ('f') "
      "AND print_batch = %s;"),
     (str(TEST_ACTION_PLAN_ID), '99')),
])
def test_build_batch_count_query(batch, wave_classifiers, expected_query, expected_params):
    actual_query, actual_params = reminder_batch.build_batch_count_query(batch, wave_classifiers, TEST_ACTION_PLAN_ID)
    unittest_helper.assertEqual(expected_query, actual_query, 'Generated batch query should match expectation')
    unittest_helper.assertEqual(expected_params, actual_params,
                                'Generated batch query parameters should match expectation')


@pytest.mark.parametrize('wave, print_batches, expected_classifiers', [
    (1, ['1', '2'], {
        'P_RL_1RL1_1': "case_type != 'HI' AND treatment_code IN ('HH_LP1E', 'HH_LP2E')"
                       " AND survey_launched = 'f' AND print_batch IN ('1','2')",
        'P_RL_1RL2B_1': "case_type != 'HI' AND treatment_code IN ('HH_LP1W', 'HH_LP2W')"
                        " AND survey_launched = 'f' AND print_batch IN ('1','2')"
    }),
    (2, ['1'], {
        'P_RL_2RL1': "case_type != 'HI' AND treatment_code IN ('HH_LP1E', 'HH_LP2E')"
                     " AND survey_launched = 'f' AND print_batch IN ('1')",
        'P_RL_2RL2B': "case_type != 'HI' AND treatment_code IN ('HH_LP1W', 'HH_LP2W')"
                      " AND survey_launched = 'f' AND print_batch IN ('1')"
    })
])
def test_build_action_rule_classifiers(wave, print_batches, expected_classifiers):
    action_rule_classifiers = reminder_batch.build_action_rule_classifiers(wave, print_batches)

    unittest_helper.assertEqual(action_rule_classifiers, expected_classifiers,
                                'Generated classifiers should match expected')


def test_generate_action_rules():
    # Given
    action_plan_id = 'test_action_plan_id'
    action_type = 'DUMMY_TEST'
    action_rule_classifiers = {action_type: "treatment_code IN ('DUMMY1', 'DUMMY2')"}

    # When
    action_rules = reminder_batch.generate_action_rules(action_rule_classifiers, action_plan_id, TEST_DATE_TIME)

    action_rule_id = list(action_rules.values())[0][1][0]
    expected_action_rules = {action_type: (
        "INSERT INTO actionv2.action_rule "
        "(id, action_type, classifiers_clause, trigger_date_time, action_plan_id, has_triggered) "
        "VALUES (%s, %s, %s, %s, %s, %s);",
        (action_rule_id, action_type, action_rule_classifiers[action_type], TEST_DATE_TIME, action_plan_id, False)
    )}

    # Then
    unittest_helper.assertEqual(expected_action_rules, action_rules,
                                'The generated action rules should match our expectations')


def get_expected_number_of_database_counts(expected_number_of_batches):
    expected_number_of_database_counts = expected_number_of_batches
    # Unless all batches will be checked add one for the batch that tips over the max c
    if expected_number_of_batches < 99:
        expected_number_of_database_counts += 1
    return expected_number_of_database_counts

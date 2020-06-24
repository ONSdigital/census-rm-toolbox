import json

import pytest

from reminder_batch_scheduler import reminder_batch
from test import test_helper


@pytest.mark.parametrize('wave_classifiers, expected_query', [
    # Test cases
    # Simple treatment code classifier
    ({'treatment_code': ['HH_DUMMY1', 'HH_DUMMY2']},
     ("SELECT COUNT(*) FROM actionv2.cases "
      "WHERE receipt_received = 'f' AND address_invalid = 'f' AND skeleton = 'f' "
      "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL'"
      "AND case_type != 'HI' "
      "AND treatment_code IN ('HH_DUMMY1', 'HH_DUMMY2');")),

    # Classifier with just one value
    ({'survey_launched': ['f']},
     ("SELECT COUNT(*) FROM actionv2.cases "
      "WHERE receipt_received = 'f' AND address_invalid = 'f' AND skeleton = 'f' "
      "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL'"
      "AND case_type != 'HI' "
      "AND survey_launched = 'f';")),

    # Mix of classifiers
    ({'treatment_code': ['HH_DUMMY1', 'HH_DUMMY2'],
      'survey_launched': ['f']},
     ("SELECT COUNT(*) FROM actionv2.cases "
      "WHERE receipt_received = 'f' AND address_invalid = 'f' AND skeleton = 'f' "
      "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL'"
      "AND case_type != 'HI' "
      "AND treatment_code IN ('HH_DUMMY1', 'HH_DUMMY2') AND survey_launched = 'f';")),
])
def test_build_batch_count_query(wave_classifiers, expected_query):
    actual_query = reminder_batch.build_batch_count_query(wave_classifiers)
    test_helper.assertEqual(actual_query, expected_query, 'Generated batch query should match expectation')


@pytest.mark.parametrize('wave, print_batches, expected_classifiers', [
    (1, ['1', '2', '3'], {
        'P_RL_1RL1_1': json.dumps({
            'treatment_code': [
                'HH_LP1E', 'HH_LP2E'
            ],
            'survey_launched': [
                'f'
            ],
            'print_batch': ['1', '2', '3'],
        }),
        'P_RL_1RL2B_1': json.dumps({
            'treatment_code': [
                'HH_LP1W', 'HH_LP2W'
            ],
            'survey_launched': [
                'f'
            ],
            'print_batch': ['1', '2', '3'],
        })
    }),
    (2, ['1'], {
        'P_RL_2RL1': json.dumps({
            'treatment_code': [
                'HH_LP1E', 'HH_LP2E'
            ],
            'survey_launched': [
                'f'
            ],
            'print_batch': ['1'],
        }),
        'P_RL_2RL2B': json.dumps({
            'treatment_code': [
                'HH_LP1W', 'HH_LP2W'
            ],
            'survey_launched': [
                'f'
            ],
            'print_batch': ['1'],
        })
    }),
    (3, list(range(1, 99)), {
        'P_QU_H1': json.dumps({
            'treatment_code': [
                'HH_LP1E'
            ],
            'print_batch': list(range(1, 99)),
        }),
        'P_QU_H2': json.dumps({
            'treatment_code': [
                'HH_LP1W'
            ],
            'print_batch': list(range(1, 99)),
        })
    }),
])
def test_build_action_rule_classifiers(wave, print_batches, expected_classifiers):
    action_rule_classifiers = reminder_batch.build_action_rule_classifiers(wave, print_batches)

    test_helper.assertEqual(action_rule_classifiers, expected_classifiers,
                            'Generated classifiers should match expected')

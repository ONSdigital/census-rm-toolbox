import argparse
import json
import uuid

import rfc3339
from termcolor import colored

from reminder_batch_scheduler import constants
from utilities import db_helper


def main(wave: int, starting_batch: int, max_cases: int, insert_rules: bool = False, action_plan_id: uuid.UUID = None):
    wave_classifiers = constants.WAVE_CLASSIFIERS[wave]
    selected_batches = select_batches(starting_batch, wave_classifiers, max_cases)
    action_rule_classifiers = build_action_rule_classifiers(wave, list(selected_batches.keys()))

    print('Selected batch counts:')
    for batch, count in selected_batches.items():
        print('batch:', batch, 'count:', count)
    print('Total:', sum(selected_batches.values()))
    print('Final batch included:', selected_batches.keys()[-1])
    print('Classifiers for each action type:')
    for action_type, action_type_classifiers in action_rule_classifiers.items():
        print("action_type:", action_type, "classifiers:", action_type_classifiers)

    if insert_rules:
        action_rules = generate_action_rules(action_rule_classifiers, action_plan_id)
        print('Generated action rules:')
        for action_rule in action_rules.values():
            print(action_rule)
        confirm_insert_rules()
        insert_action_rules(action_rules)
        print("All action rules inserted")


def count_batch_cases(batch, wave_classifiers):
    wave_classifiers['print_batch'] = [str(batch)]

    batch_count_query, query_values = build_batch_count_query(wave_classifiers)
    result = db_helper.execute_parametrized_sql_query(batch_count_query, query_values)
    return result[0][0]


def build_batch_count_query(wave_classifiers):
    classifier_sql_filters = ['']
    query_param_values = []
    for classifier, values in wave_classifiers.items():
        classifier_sql_filters.append(f" {classifier} IN %s")
        query_param_values.append(tuple(values))
    classifiers_query_filters = ' AND'.join(classifier_sql_filters)

    return ("SELECT COUNT(*) FROM actionv2.cases "
            "WHERE receipt_received = 'f' "
            "AND address_invalid = 'f' "
            "AND skeleton = 'f' "
            "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL'"
            "AND case_type != 'HI'"
            f"{classifiers_query_filters};"), tuple(query_param_values)


def build_action_rule_classifiers(wave, selected_batches):
    action_rule_classifiers = {}
    for action_type in constants.ACTION_TYPES_FOR_WAVE[wave]:
        classifiers = constants.ACTION_TYPE_CLASSIFIERS[action_type]
        classifiers['print_batch'] = selected_batches
        action_rule_classifiers[action_type] = json.dumps(classifiers)
    return action_rule_classifiers


def select_batches(starting_batch, wave_classifiers, max_cases):
    total_cases = 0
    selected_batches = {}

    batch = starting_batch

    while batch <= 99:
        batch_case_count = count_batch_cases(batch, wave_classifiers)
        if total_cases + batch_case_count > max_cases:
            break
        total_cases += batch_case_count
        selected_batches[str(batch)] = batch_case_count
        batch += 1

    return selected_batches


def confirm_insert_rules():
    confirmation = input(
        colored('WARNING: Inserting rules will write the the action rules to the database, '
                'resulting in materials being sent for print. \nContinue? [Y/n] ', color='red'))
    if confirmation != 'Y' and confirmation.lower() != 'yes':
        print('Aborting')
        exit(1)


def generate_action_rules(action_rule_classifiers, action_plan_id):
    action_rules = {}
    for action_type, classifiers in action_rule_classifiers.items():
        raw_trigger_date_time = input(f'Input trigger date time for action type {action_type} (RFC3339): ')
        trigger_date_time = rfc3339.parse_datetime(raw_trigger_date_time)
        action_rules[action_type] = (
            "INSERT INTO actionv2.action_rule "
            "(id, action_type, classifiers, trigger_date_time, action_plan_id, has_triggered) "
            "VALUES (%s, %s, %s, %s, %s, %s);",
            (str(uuid.uuid4()), action_type, classifiers, trigger_date_time, str(action_plan_id), False)
        )
    return action_rules


def insert_action_rules(action_rules):
    with db_helper.open_write_cursor() as db_cursor:
        for action_type, action_rule in action_rules.items():
            print("Inserting action rule for", action_type)
            db_helper.execute_sql_query_with_write(db_cursor, action_rule[0], action_rule[1])


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Count cases for today's reminder batches to determine the batches we can schedule")
    parser.add_argument('-w', '--wave',
                        help='The reminder wave of contact',
                        required=True,
                        type=int,
                        choices=constants.WAVE_CLASSIFIERS.keys())
    parser.add_argument('-b', '--starting_batch',
                        help='The batch number to start counting at',
                        required=True,
                        type=int,
                        choices=range(1, 100))
    parser.add_argument('--max_cases',
                        help='Maximum number cases which would be included in the rules (default 2,500,000)',
                        type=int,
                        default=2500000,
                        required=False)
    parser.add_argument('--insert_rules',
                        help='!!! Insert the generated rules into the action database !!!',
                        required=False,
                        action='store_true')
    parser.add_argument('--action_plan_id',
                        help='Action plan ID, only required when inserting action rules',
                        required=False,
                        default=None,
                        type=uuid.UUID)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    if args.insert_rules and not args.action_plan_id:
        print("Cannot run with insert action rules option without an action plan ID")
        exit(1)
    main(args.wave, args.starting_batch, args.max_cases, args.insert_rules, args.action_plan_id)

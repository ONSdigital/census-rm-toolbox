import argparse
import json

from reminder_batch_scheduler import constants
from utilities.db_helper import execute_sql_query


def main(wave: int, starting_batch: int, max_cases: int, create_rules: bool = False):
    wave_classifiers = constants.WAVE_CLASSIFIERS[wave]
    selected_batches = select_batches(starting_batch, wave_classifiers, max_cases)
    action_rule_classifiers = build_action_rule_classifiers(wave, list(selected_batches.keys()))

    print('Selected batch counts:')
    for batch, count in selected_batches.items():
        print('batch:', batch, 'count:', count)
    print('Total:', sum(selected_batches.values()))
    print('Classifiers for each action type:')
    for action_type, action_type_classifiers in action_rule_classifiers.items():
        print("action_type:", action_type, "classifiers:", action_type_classifiers)

    action_rules = generate_action_rules(wave, selected_batches)
    if create_rules:
        insert_action_rules(action_rules)


def count_batch_cases(batch, wave_classifiers):
    wave_classifiers['print_batch'] = [batch]

    batch_count_query = build_batch_count_query(wave_classifiers)
    result = execute_sql_query(batch_count_query)
    return result[0][0]


def build_batch_count_query(wave_classifiers):
    classifier_sql_filters = ['']
    for classifier, values in wave_classifiers.items():
        if len(values) > 1:
            classifier_sql_filters.append(f" {classifier} IN {tuple(values)}")
        else:
            classifier_sql_filters.append(f" {classifier} = '{values[0]}'")
    classifiers_query_filters = ' AND'.join(classifier_sql_filters)

    return ("SELECT COUNT(*) FROM actionv2.cases "
            "WHERE receipt_received = 'f' "
            "AND address_invalid = 'f' "
            "AND skeleton = 'f' "
            "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL'"
            "AND case_type != 'HI'"
            f"{classifiers_query_filters};")


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


def confirm_create_rules(create_rules):
    if create_rules:
        confirmation = input('WARNING: Create rules will write the the action rules to the database. Continue? [Y/n] ')
        if confirmation != 'Y' or confirmation.lower() != 'yes':
            print('Aborting')
            exit(1)


def generate_action_rules(wave, selected_batches):
    # TODO
    pass


def insert_action_rules(action_rules):
    # TODO
    pass


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
                        choices=range(0, 100))
    parser.add_argument('--create_rules',
                        help='!!! Set up the action rules !!!',
                        required=False,
                        action='store_true')
    parser.add_argument('--max_cases',
                        help='Maximum number cases which would be included in the rules (default 2,500,000)',
                        type=int,
                        default=2500000,
                        required=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    confirm_create_rules(args.create_rules)
    main(args.wave, args.starting_batch, args.max_cases, args.create_rules)

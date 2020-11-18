import argparse
import uuid
from datetime import datetime

import rfc3339
from termcolor import colored

from toolbox.config import Config
from toolbox.reminder_scheduler import constants
from toolbox.utilities import db_helper


def main(wave: int, starting_batch: int, max_cases: int, action_plan_id: uuid.UUID, insert_rules: bool = False,
         trigger_date_time: datetime = None):
    wave_classifiers = constants.WAVE_CLASSIFIERS[wave]
    selected_batches = select_batches(starting_batch, wave_classifiers, max_cases, action_plan_id)
    action_rule_classifiers = build_action_rule_classifiers(wave, list(selected_batches.keys()))

    print()
    if not selected_batches:
        print('The starting batch was too big, cannot fit any batches in the limit of', max_cases)
        return

    final_batch = list(selected_batches.keys())[-1]
    total_cases = sum(selected_batches.values())
    print()
    print(f'Selected print batches: {starting_batch} - {final_batch}')
    print('Current total cases:', total_cases)
    print('Classifiers for each action type:')
    for action_type, action_type_classifiers in action_rule_classifiers.items():
        print()
        print(f'Action type: {action_type}')
        print('Classifiers clause:')
        print(action_type_classifiers)

    if insert_rules:
        action_rules = generate_action_rules(action_rule_classifiers, action_plan_id, trigger_date_time)
        print()
        print('Generated action rules:')
        for action_rule in action_rules.values():
            print(action_rule)
        print('')
        print('About to insert action rules for:')
        print('Reminder wave:', colored(wave, "red"))
        print('Action types:', colored(constants.ACTION_TYPES_FOR_WAVE[wave], "red"))
        print('Print batches:', colored(f'{starting_batch} - {final_batch}', 'red'))
        print('Trigger date time:', colored(trigger_date_time.isoformat(), 'red'))
        print('Current total cases:', colored(total_cases, "red"))
        if not confirm_insert_rules():
            print(colored('ABORTING', 'red'))
            return
        insert_action_rules(action_rules)
        print()
        print(colored("All action rules inserted", 'green'))


def count_batch_cases(batch, wave_classifiers, action_plan_id):
    batch_count_query, query_values = build_batch_count_query(batch, wave_classifiers, action_plan_id)
    result = db_helper.execute_parametrized_sql_query(batch_count_query, query_values, Config.DB_HOST_ACTION,
                                                      Config.DB_ACTION_CERTIFICATES)
    return result[0][0]


def build_batch_count_query(batch, wave_classifiers, action_plan_id):
    query_param_values = (str(action_plan_id), str(batch))
    classifiers_query_filters = f"AND {wave_classifiers}"

    return ("SELECT COUNT(*) FROM actionv2.cases "
            "WHERE receipt_received = 'f' "
            "AND address_invalid = 'f' "
            "AND skeleton = 'f' "
            "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL' "
            "AND case_type != 'HI' "
            "AND action_plan_id = %s "
            f"{classifiers_query_filters} "
            f"AND print_batch = %s;"), query_param_values


def build_action_rule_classifiers(wave, selected_batches):
    action_rule_classifiers = {}
    for action_type in constants.ACTION_TYPES_FOR_WAVE[wave]:
        select_batch = "','".join(selected_batches)
        classifiers = f"case_type != 'HI' AND {constants.ACTION_TYPE_CLASSIFIERS[action_type]} " \
                      f"AND print_batch IN ('{select_batch}')"
        action_rule_classifiers[action_type] = classifiers
    return action_rule_classifiers


def select_batches(starting_batch, wave_classifiers, max_cases, action_plan_id):
    total_cases = 0
    selected_batches = {}

    # NB: The max print batch number is 99, range excludes the stop value
    for batch in range(starting_batch, 100):
        batch_case_count = count_batch_cases(batch, wave_classifiers, action_plan_id)
        print(f'Batch: {batch}, Count: {batch_case_count}')
        if total_cases + batch_case_count > max_cases:
            break
        total_cases += batch_case_count
        selected_batches[str(batch)] = batch_case_count

    return selected_batches


def confirm_insert_rules():
    confirmation = input(
        colored('WARNING: You are about to write the the action rules to the database, '
                'resulting in materials being sent for print. \nContinue? [Y/n] ', color='red'))
    if confirmation != 'Y' and confirmation.lower() != 'yes':
        return False
    return True


def generate_action_rules(action_rule_classifiers, action_plan_id, trigger_date_time: datetime):
    action_rules = {}
    for action_type, classifiers in action_rule_classifiers.items():
        action_rules[action_type] = (
            "INSERT INTO actionv2.action_rule "
            "(id, action_type, classifiers_clause, trigger_date_time, action_plan_id, has_triggered) "
            "VALUES (%s, %s, %s, %s, %s, %s);",
            (str(uuid.uuid4()), action_type, classifiers, trigger_date_time, str(action_plan_id), False)
        )
    return action_rules


def insert_action_rules(action_rules):
    with db_helper.open_write_cursor(Config.DB_HOST_ACTION, Config.DB_ACTION_CERTIFICATES) as db_cursor:
        for action_type, action_rule in action_rules.items():
            print("Inserting action rule for", action_type)
            db_helper.execute_sql_query_with_write(db_cursor, action_rule[0], action_rule[1])


def parse_trigger_date_time(trigger_date_time):
    if trigger_date_time:
        return rfc3339.parse_datetime(args.trigger_date_time)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Count cases for today's reminder batches to determine the batches we can schedule")
    parser.add_argument('-w', '--wave',
                        help='The reminder wave of contact',
                        required=True,
                        type=int,
                        choices=constants.WAVE_CLASSIFIERS.keys())
    parser.add_argument('-b', '--starting-batch',
                        help='The batch number to start counting at',
                        required=True,
                        type=int,
                        choices=range(0, 100))
    parser.add_argument('-a', '--action-plan-id',
                        help='Action plan UUID',
                        required=True,
                        type=uuid.UUID)
    parser.add_argument('--max-cases',
                        help='Maximum number cases which would be included in the rules (default 2,500,000)',
                        type=int,
                        default=2500000,
                        required=False)
    parser.add_argument('--insert-rules',
                        help='!!! Insert the generated rules into the action database !!!',
                        required=False,
                        action='store_true')
    parser.add_argument('--trigger-date-time',
                        help='Action rules trigger date time in RFC3339 format (required when inserting action rules)',
                        required=False,
                        default=None)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    if args.insert_rules and not args.trigger_date_time:
        print("Cannot insert action rules without '--trigger-date-time' try '-h' for help")
        exit(1)
    try:
        parsed_trigger_date_time = parse_trigger_date_time(args.trigger_date_time)
    except Exception:
        print('Trigger date time must be RFC3339 format')
        raise

    main(args.wave,
         args.starting_batch,
         args.max_cases,
         action_plan_id=args.action_plan_id,
         insert_rules=args.insert_rules,
         trigger_date_time=parsed_trigger_date_time)

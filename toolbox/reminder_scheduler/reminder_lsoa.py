import argparse
import uuid
from datetime import datetime
from pathlib import Path

import rfc3339
from termcolor import colored

from toolbox.config import Config
from toolbox.reminder_scheduler import constants
from toolbox.utilities.reminder_helper import get_lsoas_from_file, check_lsoas
from toolbox.utilities import db_helper


def main(lsoa_file_path: Path, reminder_action_type: str, action_plan_id: uuid.UUID, insert_rule: bool = False,
         trigger_date_time: datetime = None):
    lsoas = get_lsoas_from_file(lsoa_file_path)
    check_lsoas(lsoas)
    action_rule_classifiers = build_action_rule_classifiers(lsoas)

    print()
    print(f'Reminder Action type: {reminder_action_type}')
    print(f'Count of LSOAs to use in classifiers clause: {len(lsoas)}')

    if insert_rule:
        action_rule = generate_action_rule(reminder_action_type, action_rule_classifiers, action_plan_id,
                                           trigger_date_time)
        print()
        print('About to insert action rule for:')
        print('Action type:', colored(reminder_action_type, "red"))
        print('Action Plan ID:', colored(action_plan_id, "red"))
        print('Number of LSOAs from file:', colored(str(len(lsoas)), "red"))
        print('Trigger date time:', colored(trigger_date_time.isoformat(), 'red'))
        if not confirm_insert_rule():
            print(colored('ABORTING', 'red'))
            return
        insert_action_rule(action_rule)
        print()
        print(colored("Action rule inserted", 'green'))


def build_action_rule_classifiers(lsoas):
    lsoa_classifier_clause = "', '".join(lsoas)
    return f"case_type = 'HH' " \
           f"AND lsoa IN ('{lsoa_classifier_clause}')"


def confirm_insert_rule():
    confirmation = input(
        colored('WARNING: You are about to write the the action rule to the database, '
                'resulting in materials being sent for print. \nContinue? [Y/n] ', color='red'))
    if confirmation != 'Y' and confirmation.lower() != 'yes':
        return False
    return True


def generate_action_rule(action_type, action_rule_classifiers, action_plan_id, trigger_date_time: datetime):
    action_rule = (
        "INSERT INTO actionv2.action_rule "
        "(id, action_type, classifiers_clause, trigger_date_time, action_plan_id, has_triggered) "
        "VALUES (%s, %s, %s, %s, %s, %s);",
        (str(uuid.uuid4()), action_type, action_rule_classifiers, trigger_date_time, str(action_plan_id), False)
    )
    return action_rule


def insert_action_rule(action_rule):
    with db_helper.open_write_cursor(Config.DB_HOST_ACTION, Config.DB_ACTION_CERTIFICATES) as db_cursor:
        print("Inserting action rule")
        db_helper.execute_sql_query_with_write(db_cursor, action_rule[0], action_rule[1], suppress_sql_print=True)


def parse_trigger_date_time(trigger_date_time):
    if trigger_date_time:
        return rfc3339.parse_datetime(args.trigger_date_time)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Insert action rule from a provided list of LSOAs")
    parser.add_argument('lsoa_file_path',
                        help='Path to the LSOAs file',
                        type=str)
    parser.add_argument('-r', '--reminder-action-type',
                        help='The response driven reminder Action Type',
                        required=True,
                        type=str,
                        choices=constants.ACTION_TYPES_FOR_RESPONSE_DRIVEN_REMINDER)
    parser.add_argument('-a', '--action-plan-id',
                        help='Action plan UUID',
                        required=True,
                        type=uuid.UUID)
    parser.add_argument('--insert-rule',
                        help='!!! Insert the generated rule into the action database !!!',
                        required=False,
                        action='store_true')
    parser.add_argument('--trigger-date-time',
                        help='Action rule trigger date time in RFC3339 format (required when inserting action rule)',
                        required=False,
                        default=None)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    if args.insert_rule and not args.trigger_date_time:
        print("Cannot insert action rule without '--trigger-date-time' try '-h' for help")
        exit(1)
    try:
        parsed_trigger_date_time = parse_trigger_date_time(args.trigger_date_time)
    except Exception:
        print('Trigger date time must be RFC3339 format')
        raise

    main(args.lsoa_file_path,
         args.reminder_action_type,
         args.action_plan_id,
         args.insert_rule,
         parsed_trigger_date_time)

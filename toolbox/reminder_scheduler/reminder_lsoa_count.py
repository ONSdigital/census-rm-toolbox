import argparse
import uuid
from pathlib import Path

from toolbox.config import Config
from toolbox.utilities.reminder_helper import get_lsoas_from_file, check_lsoas
from toolbox.utilities import db_helper


def main(lsoa_file_path: Path, action_plan_id: uuid.UUID):
    lsoas = get_lsoas_from_file(lsoa_file_path)
    check_lsoas(lsoas)
    case_count = count_cases(action_plan_id, lsoas)

    print()
    print('Case count:')
    print(case_count)


def build_lsoas_count_query(action_plan_id, lsoas):
    query_param_values = (str(action_plan_id), tuple(lsoas))

    return ("SELECT COUNT(*) FROM actionv2.cases "
            "WHERE action_plan_id = %s "
            "AND receipt_received = 'f' "
            "AND address_invalid = 'f' "
            "AND skeleton = 'f' "
            "AND refusal_received IS DISTINCT FROM 'EXTRAORDINARY_REFUSAL' "
            "AND case_type = 'HH' "
            "AND lsoa IN %s; "), query_param_values


def count_cases(action_plan_id, lsoas):
    count_query, query_values = build_lsoas_count_query(action_plan_id, lsoas)
    result = db_helper.execute_parametrized_sql_query(count_query, query_values,
                                                      Config.DB_HOST_ACTION,
                                                      Config.DB_ACTION_CERTIFICATES)
    return result[0][0]


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Get a count of cases for response-driven reminders from a CSV file of LSOAs")
    parser.add_argument('lsoa_file_path',
                        help='Path to the LSOAs file',
                        type=str)
    parser.add_argument('-a', '--action-plan-id',
                        help='Action plan UUID',
                        required=True,
                        type=uuid.UUID)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    main(args.lsoa_file_path,
         args.action_plan_id)

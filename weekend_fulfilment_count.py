import argparse
import csv
from datetime import datetime, timedelta
from getpass import getpass

import psycopg2
from dateutil.rrule import rrule, DAILY

from config import Config


def fulfilment_query(username, password):
    weekend_dates = list(rrule(DAILY, dtstart=datetime.today().replace(hour=15, minute=0, second=0) - timedelta(3),
                               until=datetime.today().replace(hour=15, minute=0, second=0)))

    sql_query = """SELECT event_payload ->> 'fulfilmentCode' AS fulfilment_code,
     count(*)
     FROM casev2.event
      WHERE rm_event_processed BETWEEN %s AND %s
      AND event_type = 'FULFILMENT_REQUESTED'
      AND event_payload ->> 'fulfilmentCode' LIKE 'P_%%'
      GROUP BY event_payload ->> 'fulfilmentCode';
      """

    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{username}' host='{Config.DB_HOST}' "
                            f"password='{password}' port='{Config.DB_PORT}'{Config.DB_USESSL}")
    cur = conn.cursor()
    for index, _ in enumerate(weekend_dates):
        if index == 3:
            break
        execute_query(cur, weekend_dates, index, sql_query)


def execute_query(cur, dates, index, sql_query):
    cur.execute(sql_query, (f"{str(dates[index].date())}T16:00:00+01:00".replace(' ', ''),
                            f"{str(dates[index + 1].date())}T16:00:00+01:00".replace(' ', '')))
    db_result = cur.fetchall()

    with open(f'fulfilment-{dates[index + 1].date()}.csv', 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['treatment_code', 'count'])
        for row in db_result:
            csv_out.writerow(row)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to get fulfilment counts ')
    parser.add_argument('username', help='Username to connect to database', type=str)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    password = getpass()
    fulfilment_query(args.username, password)

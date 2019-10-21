import argparse
import datetime
import csv
import psycopg2

from config import Config


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to publish a message onto a pubsub topic from a GCS bucket. ')
    parser.add_argument('Fulfilment_date_begin', help='Fulfilment_date_begin 2019-XX-XXT16:00:00+01:00', type=str)
    parser.add_argument('Fulfilment_date_end', help='Fulfilment_date_begin 2019-XX-XXT16:00:00+01:00', type=str)

    return parser.parse_args()


def fulfilment_query(Fulfilment_date_begin, Fulfilment_date_end):
    sql_query = """SELECT event_payload ->> 'fulfilmentCode' AS fulfilment_code,
     count(*) 
     FROM casev2.event
      WHERE rm_event_processed BETWEEN %s AND %s 
      AND event_type = 'FULFILMENT_REQUESTED' 
      AND event_payload ->> 'fulfilmentCode' LIKE 'P_%%'
      GROUP BY event_payload ->> 'fulfilmentCode';
      """
    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{Config.DB_USERNAME}' host='{Config.DB_HOST}' "
                            f"password='{Config.DB_PASSWORD}' port='{Config.DB_PORT}'{Config.DB_USESSL}")
    cur = conn.cursor()
    cur.execute(sql_query, (Fulfilment_date_begin, Fulfilment_date_end,))
    db_result = cur.fetchall()
    print(db_result)

    with open(f'fulfilment-{datetime.datetime.now().date()}.csv', 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['treatment_code', 'count'])
        for row in db_result:
            csv_out.writerow(row)


if __name__ == "__main__":
    args = parse_arguments()

    fulfilment_query(args.Fulfilment_date_begin, args.Fulfilment_date_end)

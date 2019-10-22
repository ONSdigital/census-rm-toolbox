import argparse
import csv
import psycopg2

from config import Config


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool to get fulfilment counts ')
    parser.add_argument('fulfilment_date_from', help='From date e.g. 2019-XX-XXT16:00:00+01:00', type=str)
    parser.add_argument('fulfilment_date_to', help='To date e.g. 2019-XX-XXT16:00:00+01:00', type=str)

    return parser.parse_args()


def fulfilment_query(fulfilment_date_from, fulfilment_date_to):
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
    cur.execute(sql_query, (fulfilment_date_from, fulfilment_date_to,))
    db_result = cur.fetchall()

    with open(f'fulfilment-{fulfilment_date_to[:10]}.csv', 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['treatment_code', 'count'])
        for row in db_result:
            csv_out.writerow(row)


if __name__ == "__main__":
    args = parse_arguments()

    fulfilment_query(args.fulfilment_date_from, args.fulfilment_date_to)

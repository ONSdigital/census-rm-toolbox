import json

import psycopg2

from config import Config

if __name__ == "__main__":
    sql_query = """
select event_times.event_type, avg(event_times.timediff)
from (select event_type,
             event_date,
             rm_event_processed,
             ((DATE_PART('day', rm_event_processed::timestamp - event_date::timestamp) * 24 +
               DATE_PART('hour', rm_event_processed::timestamp - event_date::timestamp)) * 60 +
              DATE_PART('minute', rm_event_processed::timestamp - event_date::timestamp)) * 60 +
             DATE_PART('second', rm_event_processed::timestamp - event_date::timestamp) as timediff
      from casev2.event
      where event_type in ('RESPONSE_RECEIVED',
                           'REFUSAL_RECEIVED',
                           'FULFILMENT_REQUESTED',
                           'QUESTIONNAIRE_LINKED',
                           'RM_UAC_CREATED',
                           'ADDRESS_NOT_VALID',
                           'ADDRESS_MODIFIED',
                           'ADDRESS_TYPE_CHANGED',
                           'NEW_ADDRESS_REPORTED',
                           'SURVEY_LAUNCHED',
                           'RESPONDENT_AUTHENTICATED',
                           'UNDELIVERED_MAIL_REPORTED')
        and rm_event_processed between now() - interval '1 minutes' and now()) as event_times
      group by event_times.event_type;
        """

    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{Config.DB_USERNAME}' host='{Config.DB_HOST}' "
                            f"password='{Config.DB_PASSWORD}' port='{Config.DB_PORT}'{Config.DB_USESSL}")
    cur = conn.cursor()
    cur.execute(sql_query)

    db_result = cur.fetchall()

    for one_result in db_result:
        print(json.dumps({'event_type': one_result[0], 'average_time': one_result[1]}))

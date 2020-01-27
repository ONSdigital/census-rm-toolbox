import json

from utilities.db_helper import execute_sql_query

if __name__ == "__main__":
    sql_query = """
select event_times.event_type, event_times.event_channel, avg(event_times.timediff), count(*)
from (select event_type,
             event_channel,
             event_date,
             rm_event_processed,
             ((DATE_PART('day', rm_event_processed::timestamp - message_timestamp::timestamp) * 24 +
               DATE_PART('hour', rm_event_processed::timestamp - message_timestamp::timestamp)) * 60 +
              DATE_PART('minute', rm_event_processed::timestamp - message_timestamp::timestamp)) * 60 +
             DATE_PART('second', rm_event_processed::timestamp - message_timestamp::timestamp) as timediff
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
                           'UNDELIVERED_MAIL_REPORTED',
                           'CCS_ADDRESS_LISTED')
        and rm_event_processed between now() - interval '1 minutes' and now()) as event_times
      group by event_times.event_type, event_times.event_channel;
        """

    db_result = execute_sql_query(sql_query)

    for one_result in db_result:
        print(json.dumps({'event_type': one_result[0], 'event_channel': one_result[1], 'average_time': one_result[2],
                          'count': one_result[3]}))

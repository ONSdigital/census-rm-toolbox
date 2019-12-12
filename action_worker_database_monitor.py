import json

from utilities.db_helper import execute_sql_query

if __name__ == "__main__":
    sql_query = 'SELECT COUNT(*) FROM actionv2.case_to_process;'

    db_result = execute_sql_query(sql_query)

    print(json.dumps({'case_to_process_count': db_result[0][0]}))

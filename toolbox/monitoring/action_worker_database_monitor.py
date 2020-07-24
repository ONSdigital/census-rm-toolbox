import json

from toolbox.config import Config
from toolbox.utilities import execute_sql_query

if __name__ == "__main__":
    sql_query = 'SELECT COUNT(*) FROM actionv2.case_to_process;'

    db_result = execute_sql_query(sql_query, Config.DB_HOST_ACTION, Config.DB_ACTION_CERTIFICATES)

    print(json.dumps({'case_to_process_count': db_result[0][0]}))

import contextlib

import psycopg2
from psycopg2 import pool

from termcolor import colored

from retrying import retry

from toolbox.config import Config


def execute_sql_query(sql_query, db_host=Config.DB_HOST, extra_options=""):
    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{Config.DB_USERNAME}' host='{db_host}' "
                            f"password='{Config.DB_PASSWORD}' port='{Config.DB_PORT}'{Config.DB_USESSL}{extra_options}")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    result = cursor.fetchall()
    conn.close()
    return result


@contextlib.contextmanager
def connect_to_read_replica_pool():
    conn_pool = None

    try:
        conn_pool = pool.SimpleConnectionPool(1, 2, user=Config.DB_USERNAME,
                                              password=Config.DB_PASSWORD,
                                              host=Config.DB_HOST,
                                              port=Config.DB_PORT,
                                              database=Config.DB_NAME)
        yield conn_pool
    finally:
        if conn_pool:
            conn_pool.closeall()


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=10)
def execute_in_connection_pool(*args, conn_pool):
    try:
        conn = conn_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(*args)
        return cursor.fetchall()
    finally:
        conn_pool.putconn(conn)


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=10)
def execute_in_connection_pool_with_column_names(*args, conn_pool):
    try:
        conn = conn_pool.getconn()
        """NOTE: only use with 'SELECT * FROM' queries"""
        cursor = conn.cursor()
        cursor.execute(*args)
        colnames = [desc[0] for desc in cursor.description]
        return [dict(zip(colnames, row)) for row in cursor.fetchall()]
    finally:
        conn_pool.putconn(conn)


def execute_parametrized_sql_query(sql_query, values: tuple, db_host=Config.DB_HOST, extra_options=""):
    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{Config.DB_USERNAME}' host='{db_host}' "
                            f"password='{Config.DB_PASSWORD}' port='{Config.DB_PORT}'{Config.DB_USESSL}{extra_options}")
    cursor = conn.cursor()
    cursor.execute(sql_query, values)
    result = cursor.fetchall()
    conn.close()
    return result


def execute_sql_query_with_write(cursor, sql_query, values: tuple, suppress_sql_print=False):
    sanity_checked_sql = cursor.mogrify(sql_query, values)
    if not suppress_sql_print:
        print(colored(f'RUNNING SQL WITH WRITE: {sanity_checked_sql}', 'red'))
    cursor.execute(sanity_checked_sql)


@contextlib.contextmanager
def open_write_cursor(db_host=Config.DB_HOST, extra_options=""):
    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{Config.DB_USERNAME}' host='{db_host}' "
                            f"password='{Config.DB_PASSWORD}' port='{Config.DB_PORT}'{Config.DB_USESSL}{extra_options}")
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

import contextlib

import psycopg2
from termcolor import colored

from config import Config


def execute_sql_query(sql_query):
    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{Config.DB_USERNAME}' host='{Config.DB_HOST}' "
                            f"password='{Config.DB_PASSWORD}' port='{Config.DB_PORT}'{Config.DB_USESSL}")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    return cursor.fetchall()


def connect_to_read_replica():
    return psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{Config.DB_USERNAME}' host='{Config.DB_HOST}' "
                            f"password='{Config.DB_PASSWORD}' port='{Config.DB_PORT}'{Config.DB_USESSL}")


def execute_in_connection(*args, conn=None):
    cursor = conn.cursor()
    cursor.execute(*args)
    return cursor.fetchall()


def execute_parametrized_sql_query(sql_query, values: tuple):
    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{Config.DB_USERNAME}' host='{Config.DB_HOST}' "
                            f"password='{Config.DB_PASSWORD}' port='{Config.DB_PORT}'{Config.DB_USESSL}")
    cursor = conn.cursor()
    cursor.execute(sql_query, values)
    return cursor.fetchall()


def execute_sql_query_with_write(cursor, sql_query, values: tuple):
    sanity_checked_sql = cursor.mogrify(sql_query, values)
    print(colored(f'RUNNING SQL WITH WRITE: {sanity_checked_sql}', 'red'))
    cursor.execute(sanity_checked_sql)


@contextlib.contextmanager
def open_write_cursor():
    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{Config.DB_USERNAME}' host='{Config.DB_HOST_WRITE}' "
                            f"password='{Config.DB_PASSWORD}' port='{Config.DB_PORT_WRITE}'{Config.DB_USESSL}")
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

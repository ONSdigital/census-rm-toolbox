from unittest.mock import patch, Mock, call

import pytest
from tenacity import wait_none

from toolbox.utilities import db_helper


@patch('toolbox.utilities.db_helper.psycopg2')
def test_write_context_commits_on_success(patched_pg):
    with db_helper.open_write_cursor():
        pass

    patched_pg.connect.return_value.commit.assert_called_once()
    patched_pg.connect.return_value.close.assert_called_once()


@patch('toolbox.utilities.db_helper.psycopg2')
def test_write_context_rolls_back_and_re_raises(patched_pg):
    with pytest.raises(ValueError):
        with db_helper.open_write_cursor():
            raise ValueError('TEST')

    patched_pg.connect.return_value.commit.assert_not_called()
    patched_pg.connect.return_value.rollback.assert_called_once()
    patched_pg.connect.return_value.close.assert_called_once()


def test_execute_in_connection_pool_replaces_connection_happy_path():
    mock_conn_pool = Mock()
    mock_conn = mock_conn_pool.getconn.return_value

    db_helper.execute_in_connection_pool('foo', conn_pool=mock_conn_pool)

    mock_conn_pool.putconn.assert_called_once_with(mock_conn)


def test_execute_in_connection_pool_replaces_connection_on_error():
    # Turn the retries wait to zero for the test
    db_helper.execute_in_connection_pool.retry.wait = wait_none()

    mock_conn_pool = Mock()
    mock_conn = mock_conn_pool.getconn.return_value

    # Simulate an error by raising an exception on the call to get a cursor
    error_message = 'Test error on cursor'
    mock_conn.cursor.side_effect = Exception(error_message)

    with pytest.raises(Exception) as e:
        db_helper.execute_in_connection_pool('foo', conn_pool=mock_conn_pool)

    # Check the cause was our simulated error
    assert str(e.value) == error_message

    putconn_calls = mock_conn_pool.putconn.call_args_list
    assert all(actual_call == call(mock_conn) for actual_call in putconn_calls)

    # Check it was retried
    assert len(putconn_calls) > 1


def test_execute_in_connection_pool_with_column_names_replaces_connection_happy_path():
    mock_conn_pool = Mock()
    mock_conn = mock_conn_pool.getconn.return_value

    # Mock some gubbins that need to be iterable
    mock_conn.cursor.return_value.description = []
    mock_conn.cursor.return_value.fetchall.return_value = []

    db_helper.execute_in_connection_pool_with_column_names('foo', conn_pool=mock_conn_pool)

    mock_conn_pool.putconn.assert_called_once_with(mock_conn)


def test_execute_in_connection_pool_with_column_names_replaces_connection_on_error():
    # Turn the retries wait to zero for the test
    db_helper.execute_in_connection_pool_with_column_names.retry.wait = wait_none()

    mock_conn_pool = Mock()
    mock_conn = mock_conn_pool.getconn.return_value

    # Mock some gubbins that need to be iterable
    mock_conn.cursor.return_value.description = []
    mock_conn.cursor.return_value.fetchall.return_value = []

    # Simulate an error by raising an exception on the call to get a cursor
    error_message = 'Test error on cursor'
    mock_conn.cursor.side_effect = Exception(error_message)

    with pytest.raises(Exception) as e:
        db_helper.execute_in_connection_pool_with_column_names('foo', conn_pool=mock_conn_pool)

    # Check the cause was our simulated error
    assert str(e.value) == error_message

    putconn_calls = mock_conn_pool.putconn.call_args_list
    assert all(actual_call == call(mock_conn) for actual_call in putconn_calls)

    # Check it was retried
    assert len(putconn_calls) > 1

from unittest.mock import patch

import pytest

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

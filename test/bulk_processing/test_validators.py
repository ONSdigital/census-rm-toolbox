from unittest.mock import patch

import pytest

from bulk_processing import validators


def test_in_set_valid():
    # Given
    in_set_validator = validators.in_set({'a', 'b', 'c'})

    # When
    in_set_validator('a')
    in_set_validator('b')
    in_set_validator('c')

    # Then no invalid exception is raised


def test_in_set_invalid():
    # Given
    in_set_validator = validators.in_set({'a'})

    # When, then raises
    with pytest.raises(validators.Invalid):
        in_set_validator('abc')


def test_set_equal_valid():
    # Given
    set_equal_validator = validators.set_equal({'a', 'b', 'c'})

    # When
    set_equal_validator(['a', 'b', 'c'])

    # Then no invalid exception is raised


def test_set_equal_invalid():
    # Given
    set_equal_validator = validators.set_equal({'a', 'b', 'c'})

    # When, then raises
    with pytest.raises(validators.Invalid):
        set_equal_validator(['a', 'b', 'c', 'blah'])


@patch('bulk_processing.validators.execute_parametrized_sql_query')
def test_case_exists_by_id_succeeds(mock_execute_method):
    # Given
    mock_execute_method.return_value = [(1,)]
    # When
    case_exists_validator = validators.case_exists_by_id()

    case_exists_validator("valid_uuid")

    # Then no invalid exception is raised


@patch('bulk_processing.validators.execute_parametrized_sql_query')
def test_case_exists_by_id_fails(mock_execute_method):
    # Given
    mock_execute_method.return_value = []
    # When, then raises
    with pytest.raises(validators.Invalid) as exc:
        case_exists_validator = validators.case_exists_by_id()
        case_exists_validator("invalid_uuid")

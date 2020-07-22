import uuid
from unittest.mock import patch

import pytest

from bulk_processing import validators

test_label = 'test label'


def test_in_set_valid():
    # Given
    in_set_validator = validators.in_set({'a', 'b', 'c'}, label=test_label)

    # When
    in_set_validator('a')
    in_set_validator('b')
    in_set_validator('c')

    # Then no invalid exception is raised


def test_in_set_invalid():
    # Given
    in_set_validator = validators.in_set({'a'}, label=test_label)

    # When, then raises
    with pytest.raises(validators.Invalid):
        in_set_validator('abc')


@pytest.mark.parametrize('expected_header,header', [
    (['a', 'b', 'c'], ['a', 'b', 'c']),
    (['a', 'b', 'c'], ('a', 'b', 'c')),
    (['a', 'b', 'c'], {'a': 'foo', 'b': 'bar', 'c': 'spam'}.keys()),
    (['2', '1'], ('2', '1')),
])
def test_header_equal_valid(expected_header, header):
    # Given
    set_equal_validator = validators.header_equal(expected_header)

    # When
    set_equal_validator(header)

    # Then no invalid exception is raised


@pytest.mark.parametrize('expected_header,header', [
    (['a', 'b', 'c'], ['a', 'b', 'c', 'blah']),
    (['a', 'b', 'c'], ['a', 'c', 'b']),
    (['a', 'b', 'c'], []),
    (['a', 'b', 'c'], ['foo']),
    ([], ['foo'])
])
def test_header_equal_invalid(expected_header, header):
    # Given
    set_equal_validator = validators.header_equal(expected_header)

    # When, then raises
    with pytest.raises(validators.Invalid):
        set_equal_validator(header)


@patch('bulk_processing.validators.execute_in_connection')
def test_case_exists_by_id_succeeds(mock_execute_method):
    # Given
    mock_execute_method.return_value = [(1,)]
    # When
    case_exists_validator = validators.case_exists_by_id()

    case_exists_validator("valid_uuid", db_connection='db_connection')

    # Then no invalid exception is raised


@patch('bulk_processing.validators.execute_in_connection')
def test_case_exists_by_id_fails(mock_execute_method):
    # Given
    mock_execute_method.return_value = []
    # When, then raises
    with pytest.raises(validators.Invalid):
        case_exists_validator = validators.case_exists_by_id()
        case_exists_validator("invalid_uuid", db_connection='db_connection')


@pytest.mark.parametrize('value,is_valid', [
    (str(uuid.uuid4()), True),
    ('559eea4d-5251-4b4b-b36f-5beaaf48c5f3', True),
    ('definitely_not_a_uuid', False)])
def test_is_uuid(value, is_valid):
    is_uuid_validator = validators.is_uuid()
    if is_valid:
        # No exception should be raised
        is_uuid_validator(value)
    else:
        with pytest.raises(validators.Invalid):
            is_uuid_validator(value)

import uuid
from unittest.mock import patch

import pytest

from toolbox.bulk_processing import validators

test_label = 'tests label'


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


@patch('toolbox.bulk_processing.validators.execute_in_connection')
def test_case_exists_by_id_succeeds(mock_execute_method):
    # Given
    mock_execute_method.return_value = [(1,)]
    # When
    case_exists_validator = validators.case_exists_by_id()

    case_exists_validator("valid_uuid", db_connection='db_connection')

    # Then no invalid exception is raised


@patch('toolbox.bulk_processing.validators.execute_in_connection')
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


def test_max_length_valid():
    # Given
    max_length_validator = validators.max_length(10)

    # When
    max_length_validator('a' * 9)

    # Then no invalid exception is raised


def test_max_length_invalid():
    # Given
    max_length_0_validator = validators.max_length(10)

    # When, then raises
    with pytest.raises(validators.Invalid):
        max_length_0_validator('a' * 11)


def test_mandatory_valid():
    # Given
    mandatory_validator = validators.mandatory()

    # When
    mandatory_validator('a')

    # Then no invalid exception is raised


def test_mandatory_invalid():
    # Given
    mandatory_validator = validators.mandatory()

    # When, then raises
    with pytest.raises(validators.Invalid) as exc:
        mandatory_validator('', column='test_column')

    assert 'Empty mandatory value: test_column' in exc.value.args[0]


def test_numeric_valid():
    # Given
    numeric_validator = validators.numeric()

    # When
    numeric_validator('0123456789')

    # Then no invalid exception is raised


def test_numeric_invalid():
    # Given
    numeric_validator = validators.numeric()

    # When, then raises
    with pytest.raises(validators.Invalid):
        numeric_validator('a')

    with pytest.raises(validators.Invalid):
        numeric_validator('1.1')

    with pytest.raises(validators.Invalid):
        numeric_validator('_')


def test_lat_long_valid():
    # Given
    lat_long_validator = validators.latitude_longitude(max_scale=5, max_precision=10)

    # When
    lat_long_validator('1234.5678')

    # Then no invalid exception is raised


def test_lat_long_invalid_format():
    # Given
    lat_long_validator = validators.latitude_longitude(max_scale=5, max_precision=10)

    # When, then raises
    with pytest.raises(validators.Invalid):
        lat_long_validator('foo')


def test_lat_long_invalid_scale():
    # Given
    lat_long_validator = validators.latitude_longitude(max_scale=5, max_precision=10)

    # When, then raises
    with pytest.raises(validators.Invalid):
        lat_long_validator('1.567889')


def test_lat_long_invalid_precision():
    # Given
    lat_long_validator = validators.latitude_longitude(max_scale=10, max_precision=5)

    # When, then raises
    with pytest.raises(validators.Invalid):
        lat_long_validator('123456.7')


def test_no_padding_whitespace_check_valid():
    # Given
    no_padding_whitespace_validator = validators.no_padding_whitespace()

    # When
    no_padding_whitespace_validator('')

    # Then no invalid exception is raised


def test_no_padding_whitespace_check_invalid():
    # Given
    no_padding_whitespace_validator = validators.no_padding_whitespace()

    # When, then raises
    with pytest.raises(validators.Invalid):
        no_padding_whitespace_validator('  ')


def test_no_pipe_character_check_valid():
    # Given
    no_pipe_character_validator = validators.no_pipe_character()

    # When, then raises
    no_pipe_character_validator('test')

    # Then no invalid exception is raised


def test_no_pipe_character_check_invalid():
    # Given
    no_pipe_character_validator = validators.no_pipe_character()

    # When, then raises
    with pytest.raises(validators.Invalid):
        no_pipe_character_validator('|')


def test_region_matches_treatment_code_valid():
    # Given
    region_matches_treatment_code_validator = validators.region_matches_treatment_code()

    # When
    region_matches_treatment_code_validator('E0000', row={'TREATMENT_CODE': 'HH_TESTE'})

    # Then no invalid exception is raised


def test_region_matches_treatment_code_invalid():
    # Given
    region_matches_treatment_code_validator = validators.region_matches_treatment_code()

    # When, then raises
    with pytest.raises(validators.Invalid):
        region_matches_treatment_code_validator('N0000', row={'TREATMENT_CODE': 'HH_TESTE'})


def test_ce_u_has_expected_capacity_valid():
    # Given
    ce_u_has_expected_capacity_validator = validators.ce_u_has_expected_capacity()

    # When
    ce_u_has_expected_capacity_validator('5', row={'ADDRESS_TYPE': 'CE', 'ADDRESS_LEVEL': 'U'})

    # Then no invalid exception is raised


def test_ce_u_has_expected_capacity_invalid():
    # Given
    ce_u_has_expected_capacity_validator = validators.ce_u_has_expected_capacity()

    # When, then raises
    with pytest.raises(validators.Invalid):
        ce_u_has_expected_capacity_validator('a', row={'ADDRESS_TYPE': 'CE', 'ADDRESS_LEVEL': 'U'})


def test_ce_e_has_expected_capacity_valid():
    # Given
    ce_e_has_expected_capacity_validator = validators.ce_e_has_expected_capacity()

    # When
    ce_e_has_expected_capacity_validator('5', row={'ADDRESS_TYPE': 'CE', 'ADDRESS_LEVEL': 'E',
                                                   'TREATMENT_CODE': 'CE_TESTE'})

    # Then no invalid exception is raised


def test_ce_e_has_expected_capacity_invalid():
    # Given
    ce_e_has_expected_capacity_validator = validators.ce_e_has_expected_capacity()

    # When, then raises
    with pytest.raises(validators.Invalid):
        ce_e_has_expected_capacity_validator('0', row={'ADDRESS_TYPE': 'CE', 'ADDRESS_LEVEL': 'E',
                                                       'TREATMENT_CODE': 'CE_TESTE'})


def test_alphanumeric_postcode_valid():
    # Given
    alphanumeric_postcode_validator = validators.alphanumeric_postcode()

    # When
    alphanumeric_postcode_validator('TE25 5TE')

    # Then no invalid exception is raised


def test_alphanumeric_postcode_invalid():
    # Given
    alphanumeric_postcode_validator = validators.alphanumeric_postcode()

    # When, then raises
    with pytest.raises(validators.Invalid):
        alphanumeric_postcode_validator('TE5 5TE!')

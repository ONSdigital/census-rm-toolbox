import uuid
from collections import namedtuple
from typing import Sequence

from toolbox.utilities.db_helper import execute_in_connection

ValidationFailure = namedtuple('ValidationFailure', ('line_number', 'column', 'description'))


class Invalid(Exception):
    pass


def in_set(valid_value_set: set, label: str):
    def validate(value, **_kwargs):
        if value not in valid_value_set:
            raise Invalid(f'Value "{value}" is not in the valid set of {label}: {valid_value_set}')

    return validate


def header_equal(expected_fieldnames: list):
    def validate(value: Sequence[str], **_kwargs) -> None:
        if list(value) != list(expected_fieldnames):
            raise Invalid(f'Header row does not match expected. Expected: {expected_fieldnames}, Got: {value}')

    return validate


def is_uuid():
    def validate(value, **_kwargs):
        try:
            uuid.UUID(value, version=4)
        except Exception:
            raise Invalid(f'Case ID {value} does not exist, it is not a valid UUID')

    return validate


def case_exists_by_id():
    def validate(case_id, **kwargs):
        try:
            case_id_exists = execute_in_connection("SELECT 1 FROM casev2.cases WHERE case_id = %s LIMIT 1",
                                                   (case_id,), conn=kwargs['db_connection'])
        except Exception as e:
            print(f'Error looking up case ID: {case_id}, Error: {e}')
            raise Invalid(f'Error looking up case ID: {case_id}')
        if not case_id_exists:
            raise Invalid(f'Case ID "{case_id}" does not exist in RM')

    return validate


def max_length(max_len: int):
    def validate(value, **_kwargs):
        if len(value) > max_len:
            raise Invalid(f'Value has length {len(value)}, exceeds max of {max_len}')

    return validate


def mandatory():
    def validate(value, **_kwargs):
        if not value or value.replace(" ", "") == '':
            raise Invalid(f'Empty mandatory value: {_kwargs["column"]}')

    return validate


def numeric():
    def validate(value, **_kwargs):
        if value and value.replace(" ", "") == '':
            pass
        elif value and not value.replace(" ", "").isnumeric():
            raise Invalid(f'Value "{value}" is non numeric')

    return validate


def latitude_longitude(max_precision: int, max_scale: int):
    def validate(value, **_kwargs):
        try:
            float(value)
        except ValueError:
            raise Invalid(f'Value "{value}" is not a valid float')
        integer, decimal = value.split('.')
        integer = integer.strip('-')
        scale = len(decimal)
        precision = len(integer) + len(decimal)
        errors = []
        if precision > max_precision:
            errors.append(f'Precision {precision} exceeds max of {max_precision}')
        if scale > max_scale:
            errors.append(f'Scale {scale} exceeds max of {max_scale}')
        if errors:
            raise Invalid(f'{", ".join(errors)}, Value = "{value}"')

    return validate


def no_padding_whitespace():
    def validate(value, **_kwargs):
        if value != value.strip():
            raise Invalid(f'Value "{value}" contains padding whitespace')

    return validate


def no_pipe_character():
    def validate(value, **_kwargs):
        if str('|') in value:
            raise Invalid(f'Value "{value}" contains pipe character')

    return validate


def region_matches_treatment_code():
    def validate(region, **kwargs):
        if region[0] != kwargs['row']['TREATMENT_CODE'][-1]:
            raise Invalid(
                f'Region "{region}" does not match region in treatment code "{kwargs["row"]["TREATMENT_CODE"]}"')

    return validate


def ce_u_has_expected_capacity():
    def validate(expected_capacity, **kwargs):
        if kwargs['row']['ADDRESS_TYPE'] == 'CE' and kwargs['row']['ADDRESS_LEVEL'] == 'U' \
                and (not expected_capacity.isdigit() or int(expected_capacity) == 0):
            raise Invalid(
                f'CE Unit Expected Capacity "{expected_capacity}" cannot be null, blank or zero')

    return validate


def ce_e_has_expected_capacity():
    def validate(expected_capacity, **kwargs):
        if kwargs['row']['ADDRESS_TYPE'] == 'CE' and kwargs['row']['ADDRESS_LEVEL'] == 'E' and (
                kwargs['row']['TREATMENT_CODE'] not in {'CE_LDCEE', 'CE_LDCEW'}) and (
                not expected_capacity.isdigit() or int(expected_capacity) == 0):
            raise Invalid(
                f'CE Estab Expected Capacity "{expected_capacity}" with Treatment Code '
                f'{kwargs["row"]["TREATMENT_CODE"]} other than CE_LDCEE/CE_LDCEW cannot be null, blank or zero')

    return validate


def alphanumeric_postcode():
    def validate(postcode, **_kwargs):
        stripped_postcode = postcode.replace(" ", "")
        if not stripped_postcode.isalnum():
            raise Invalid(f'Postcode "{postcode}" is non alphanumeric')

    return validate


def latitude_longitude_range():
    def validate(value, **_kwargs):
        try:
            lat_long_float = float(value)
        except ValueError:
            raise Invalid(f'Value "{value}" is not a valid float')
        if not -180 <= lat_long_float <= 180:
            raise Invalid(f'Latitude/Longitude value "{value}" is not in a range between -180 and 180')

    return validate

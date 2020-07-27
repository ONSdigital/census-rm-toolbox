import uuid
from collections import namedtuple
from typing import Sequence

from utilities.db_helper import execute_in_connection

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


def max_length(max_len: int):
    def validate(value, **_kwargs):
        if len(value) > max_len:
            raise Invalid(f'Value has length {len(value)}, exceeds max of {max_len}')

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

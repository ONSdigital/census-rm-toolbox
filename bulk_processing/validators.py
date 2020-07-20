import uuid
from collections import namedtuple
from typing import Iterable

from utilities.db_helper import execute_in_connection

ValidationFailure = namedtuple('ValidationFailure', ('line_number', 'column', 'description'))


class Invalid(Exception):
    pass


def in_set(valid_value_set: set, label: str):
    def validate(value, **_kwargs):
        if value not in valid_value_set:
            raise Invalid(f'Value "{value}" is not in the valid set of {label}: {valid_value_set}')

    return validate


def set_equal(expected_set: set, label: str):
    def validate(value: Iterable, **_kwargs) -> None:
        value_as_set = set(value)
        if value_as_set != expected_set:
            raise Invalid((f"Values don't match expected set of {label}, "
                           f'missing values: {expected_set.difference(value_as_set)}, '
                           f'unexpected values: {value_as_set.difference(expected_set)}'))

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

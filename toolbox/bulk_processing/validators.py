import uuid
from collections import namedtuple
from typing import Sequence

from toolbox.utilities.db_helper import execute_in_connection_pool, execute_in_connection_pool_with_column_names

ValidationFailure = namedtuple('ValidationFailure', ('line_number', 'column', 'description'))


class Invalid(Exception):
    pass


def in_set(valid_value_set: set, label: str):
    def validate(value, **_kwargs):
        if value not in valid_value_set:
            raise Invalid(f'Value "{value}" is not in the valid set of {label}: {valid_value_set}')

    return validate


def optional_in_set(valid_value_set: set, label: str):
    def validate(value, **_kwargs):
        if value and value not in valid_value_set:
            raise Invalid(f'Value "{value}" is not empty and not in the valid set of {label}: {valid_value_set}')

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
            case_id_exists = execute_in_connection_pool("SELECT 1 FROM casev2.cases WHERE case_id = %s",
                                                        (case_id,), conn_pool=kwargs['db_connection_pool'])
        except Exception as e:
            print(f'Error looking up case ID: {case_id}, Error: {e}')
            raise Invalid(f'Error looking up case ID: {case_id}')
        if not case_id_exists:
            raise Invalid(f'Case ID "{case_id}" does not exist in RM')

    return validate


def hh_case_exists_by_id():
    def validate(case_id, **kwargs):
        try:
            query = "SELECT 1 FROM casev2.cases WHERE case_id = %s AND case_type = 'HH'"
            case_id_exists = execute_in_connection_pool(query, (case_id,), conn_pool=kwargs['db_connection_pool'])
        except Exception as e:
            print(f'Error looking up case ID: {case_id}, Error: {e}')
            raise Invalid(f'Error looking up case ID: {case_id}')
        if not case_id_exists:
            raise Invalid(f'HH Case does not exist in RM for Case ID "{case_id}"')

    return validate


def qid_exists():
    def validate(qid, **kwargs):
        try:
            qid_exists_in_db = execute_in_connection_pool("SELECT 1 FROM casev2.uac_qid_link WHERE qid = %s LIMIT 1",
                                                          (qid,), conn_pool=kwargs['db_connection_pool'])
        except Exception as e:
            print(f'Error looking up qid {qid}, Error: {e}')
            raise Invalid(f'Error looking up case ID: {qid}')
        if not qid_exists_in_db:
            raise Invalid(f'qid "{qid}" does not exist in RM')

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
        try:
            integer, decimal = value.split('.')
        except ValueError:
            raise Invalid(f'Malformed decimal, Value = "{value}"')
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
        if region.strip() and kwargs['row']['TREATMENT_CODE'].strip() and \
                region[0] != kwargs['row']['TREATMENT_CODE'][-1]:
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
        if stripped_postcode and not stripped_postcode.isalnum():
            raise Invalid(f'Postcode "{postcode}" is non alphanumeric')

    return validate


def alphanumeric_plus_hyphen_field_values():
    def validate(value, **_kwargs):
        stripped_field_value = value.replace("-", "")
        if not stripped_field_value.isalnum():
            raise Invalid(f'Value "{value}" contains invalid characters')

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


def mandatory_after_update(column_name):
    """Field must be present either on the case or the update row"""

    def validate(value, **kwargs):
        if value:
            return

        case_id = kwargs['row']['CASE_ID']
        try:
            case = execute_in_connection_pool_with_column_names("SELECT * FROM casev2.cases WHERE case_id = %s",
                                                                (case_id,), conn_pool=kwargs['db_connection_pool'])[0]
        except Exception as e:
            print(f'Error looking up case ID: {case_id}, Error: {e}')
            raise Invalid(f'Error looking up case ID: {case_id}')

        if not case[column_name]:
            raise Invalid('Mandatory field not given in update file or present on the case')

    return validate


def cant_be_deleted():
    def validate(value: str, **_kwargs):
        check_no_dodgy_hyphen_lookalikes(value)
        if value.count('-') >= 5 or (value in {'----', '---', '--', '-'}):
            raise Invalid(
                f'Found 5 or more "-" characters in value {value}, this field cannot be deleted')

    return validate


def check_delete_keyword():
    def validate(value: str, **_kwargs):
        check_no_dodgy_hyphen_lookalikes(value)
        if (value.count('-') >= 5 and value != '-----') or (value in {'----', '---', '--', '-'}):
            raise Invalid(
                f'Found unexpected "-" characters in value {value}, ambiguous attempt to delete')

    return validate


def check_no_dodgy_hyphen_lookalikes(value):
    for hyphen_lookalike in ('‒', '–', '—', '―', '¯', 'ˉ', 'ˍ', '˗', '‐', '‑', '‒', '‾', '⁃', '⁻', '₋', '−',
                             '⎯', '⏤', '─', '➖', '𐆑'):
        if hyphen_lookalike in value:
            raise Invalid(f"Value {value} contains things which look like hyphens but aren't")


def numeric_2_digit_or_delete():
    def validate(value: str, **_kwargs):
        if not (value == '-----' or not value or (value.isnumeric() and len(value) <= 2)):
            raise Invalid(f'Value {value} must be either a whole number between 0 and 99 or delete keyword "-----"')

    return validate

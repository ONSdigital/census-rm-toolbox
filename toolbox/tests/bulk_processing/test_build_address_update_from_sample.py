from pathlib import Path
from unittest.mock import patch

import pytest

from toolbox.bulk_processing.build_address_update_from_sample import generate_address_update_file

RESOURCE_PATH = Path(__file__).parent.joinpath('resources')
TEST_SAMPLE_FILE = RESOURCE_PATH.joinpath('sample_file_for_address_update.csv')


@patch('toolbox.bulk_processing.build_address_update_from_sample.db_helper')
def test_happy_path(patch_db_helper):
    patch_db_helper.execute_in_connection_pool.return_value = [('583c3098-42f9-43ca-8b8f-10e37066300b',)]

    address_update_file = generate_address_update_file(TEST_SAMPLE_FILE)

    assert address_update_file.read_text() == RESOURCE_PATH.joinpath(
        'excepted_address_update_from_sample.csv').read_text()

    address_update_file.unlink()


@patch('toolbox.bulk_processing.build_address_update_from_sample.db_helper')
def test_raises_if_uprn_is_invalid(patch_db_helper):
    patch_db_helper.execute_in_connection_pool.return_value = []

    with pytest.raises(ValueError) as expected_error:
        generate_address_update_file(TEST_SAMPLE_FILE)

    assert 'does not match any cases' in str(expected_error.value)


@patch('toolbox.bulk_processing.build_address_update_from_sample.db_helper')
def test_raises_if_uprn_has_multiple_cases(patch_db_helper):
    patch_db_helper.execute_in_connection_pool.return_value = [('583c3098-42f9-43ca-8b8f-10e37066300b',),
                                                               ('a1ea5579-9691-426d-9352-9eb22e5d6297',)]

    with pytest.raises(ValueError) as expected_error:
        generate_address_update_file(TEST_SAMPLE_FILE)

    assert 'matches multiple case IDs' in str(expected_error.value)

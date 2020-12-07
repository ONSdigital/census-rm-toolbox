from pathlib import Path
from unittest.mock import patch

import pytest
from requests import HTTPError
from tenacity import wait_none

from toolbox.bulk_processing.build_address_update_from_sample import generate_address_update_file, \
    get_case_id_from_case_api

RESOURCE_PATH = Path(__file__).parent.joinpath('resources')
TEST_SAMPLE_FILE = RESOURCE_PATH.joinpath('sample_file_for_address_update.csv')


# use decorator of patch
@patch('toolbox.bulk_processing.build_address_update_from_sample.requests')
def test_happy_path(patch_requests):
    patch_requests.get.return_value.json.return_value = [{'id': '583c3098-42f9-43ca-8b8f-10e37066300b'}]

    address_update_file = generate_address_update_file(TEST_SAMPLE_FILE)

    assert address_update_file.read_text() == RESOURCE_PATH.joinpath(
        'excepted_address_update_from_sample.csv').read_text()

    address_update_file.unlink()


@patch('toolbox.bulk_processing.build_address_update_from_sample.requests')
def test_raises_if_uprn_is_invalid(patch_requests):
    patch_requests.get.return_value.raise_for_status.side_effect = HTTPError()

    patch_requests.get.return_value.status_code = 404

    with pytest.raises(ValueError):
        generate_address_update_file(TEST_SAMPLE_FILE)

    patch_requests.get.assert_called_once()


@patch('toolbox.bulk_processing.build_address_update_from_sample.requests')
def test_raises_unknown_error(patch_requests):
    # Turn the retry waits down to zero for the unit test
    get_case_id_from_case_api.retry.wait = wait_none()

    patch_requests.get.return_value.raise_for_status.side_effect = HTTPError()

    patch_requests.get.return_value.status_code = 500

    with pytest.raises(HTTPError):
        generate_address_update_file(TEST_SAMPLE_FILE)

    # Check the call was retried
    assert patch_requests.get.call_count > 1


@patch('toolbox.bulk_processing.build_address_update_from_sample.requests')
def test_raises_if_uprn_has_multiple_cases(patch_requests):
    patch_requests.get.return_value.json.return_value = [{'id': 'foo'},
                                                         {'id': 'blah'}]

    with pytest.raises(ValueError):
        generate_address_update_file(TEST_SAMPLE_FILE)

    patch_requests.get.assert_called_once()

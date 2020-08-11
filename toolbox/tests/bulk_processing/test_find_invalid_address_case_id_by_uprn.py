from pathlib import Path
from unittest.mock import patch

from requests import HTTPError

from toolbox.bulk_processing.find_invalid_address_case_id_by_uprn import generate_bulk_invalid_address_file

RESOURCE_PATH = Path(__file__).parent.joinpath('resources')


# use decorator of patch
@patch('toolbox.bulk_processing.find_invalid_address_case_id_by_uprn.requests')
def test_address_delta_happy_path(patch_requests):
    uprn_test_file = RESOURCE_PATH.joinpath('address_delta_uprn_file.csv')

    patch_requests.get.return_value.json.return_value = [{'id': 'd81af5c3-1802-4a3e-98ee-fb41ad590296'}]

    address_delta_file = generate_bulk_invalid_address_file(uprn_test_file)

    assert address_delta_file.read_text() == ('case_id,reason\n'
                                              'd81af5c3-1802-4a3e-98ee-fb41ad590296,ADDRESS_DELTA\n')

    address_delta_file.unlink()


@patch('toolbox.bulk_processing.find_invalid_address_case_id_by_uprn.requests')
def test_address_delta_file_not_created_if_uprn_is_invalid(patch_requests):
    uprn_test_file = RESOURCE_PATH.joinpath('address_delta_uprn_file.csv')

    patch_requests.get.return_value.raise_for_status.side_effect = HTTPError()

    patch_requests.get.return_value.status_code = 404

    address_delta_file = generate_bulk_invalid_address_file(uprn_test_file)

    assert address_delta_file is None

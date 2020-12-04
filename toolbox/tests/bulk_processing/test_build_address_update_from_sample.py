import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from requests import HTTPError

from toolbox.bulk_processing.build_address_update_from_sample import generate_address_update_file

RESOURCE_PATH = Path(__file__).parent.joinpath('resources')
TEST_SAMPLE_FILE = RESOURCE_PATH.joinpath('sample_file_for_address_update.csv')


# use decorator of patch
@patch('toolbox.bulk_processing.build_address_update_from_sample.requests')
def test_happy_path(patch_requests):
    case_id = uuid.uuid4()
    patch_requests.get.return_value.json.return_value = [{'id': case_id}]

    address_update_file = generate_address_update_file(TEST_SAMPLE_FILE)

    assert address_update_file.read_text() == (
        'CASE_ID,UPRN,ESTAB_UPRN,ESTAB_TYPE,ABP_CODE,ORGANISATION_NAME,ADDRESS_LINE1,ADDRESS_LINE2,ADDRESS_LINE3,TOWN_NAME,POSTCODE,LATITUDE,LONGITUDE,OA,LSOA,MSOA,LAD,HTC_WILLINGNESS,HTC_DIGITAL,TREATMENT_CODE,FIELDCOORDINATOR_ID,FIELDOFFICER_ID,CE_EXPECTED_CAPACITY,CE_SECURE,PRINT_BATCH\n'
        f'{case_id},16758681217,47502848454,HOUSEHOLD,RD06,,239 Subfloor Answering Lane,Fossilmere,Wakeby,Diligent Town,IH4 1DZ,-47.5344,1.1E-10,W29441168,W42795527,W45627351,W71087559,1,4,HH_LP1W,QM-QMR6-XW,IR-GSB3-EW-48,0,0,37\n'
    )

    address_update_file.unlink()


@patch('toolbox.bulk_processing.build_address_update_from_sample.requests')
def test_raises_if_uprn_is_invalid(patch_requests):
    patch_requests.get.return_value.raise_for_status.side_effect = HTTPError()

    patch_requests.get.return_value.status_code = 404

    with pytest.raises(ValueError):
        generate_address_update_file(TEST_SAMPLE_FILE)


@patch('toolbox.bulk_processing.build_address_update_from_sample.requests')
def test_raises_unknown_error(patch_requests):
    patch_requests.get.return_value.raise_for_status.side_effect = HTTPError()

    patch_requests.get.return_value.status_code = 500

    with pytest.raises(HTTPError):
        generate_address_update_file(TEST_SAMPLE_FILE)


@patch('toolbox.bulk_processing.build_address_update_from_sample.requests')
def test_rasises_if_uprn_has_multiple_cases(patch_requests):
    patch_requests.get.return_value.json.return_value = [{'id': 'foo'},
                                                         {'id': 'blah'}]

    with pytest.raises(ValueError):
        generate_address_update_file(TEST_SAMPLE_FILE)

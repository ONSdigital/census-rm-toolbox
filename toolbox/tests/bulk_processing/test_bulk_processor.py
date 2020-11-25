import json
from functools import partial
from pathlib import Path
from unittest.mock import Mock, call

from toolbox.bulk_processing.bulk_processor import BulkProcessor
from toolbox.bulk_processing.processor_interface import Processor
from toolbox.bulk_processing.validators import Invalid

RESOURCE_PATH = Path(__file__).parent.joinpath('resources')
HEADER_IS_VALID = 'Header row is valid\n'


def test_process_file_successful(patch_storage, patch_rabbit, tmp_path):
    schema = {'header_1': [], 'header_2': []}
    header = ','.join(key for key in schema.keys())
    mock_processor = setup_mock_processor(schema, None)
    mock_processor.build_event_messages.side_effect = lambda row: [row]
    bulk_processor = BulkProcessor(mock_processor)
    bulk_processor.working_dir = tmp_path
    bulk_processor.rabbit = patch_rabbit
    test_file = RESOURCE_PATH.joinpath('bulk_test_file_success.csv')

    success_file, error_file, error_detail_file = bulk_processor.initialise_results_files(test_file.name)
    success_count, failure_count = bulk_processor.process_file(test_file, success_file, error_file,
                                                               error_detail_file)

    assert not failure_count, 'Should have no processing errors'
    assert success_count == 1, 'Should successfully process one row'

    assert success_file.read_text() == test_file.read_text()
    assert error_file.read_text() == header + '\n'
    assert error_detail_file.read_text() == HEADER_IS_VALID

    patch_rabbit.publish_message.assert_called_once_with(
        message=json.dumps({'header_1': 'foo', 'header_2': 'bar'}),
        content_type='application/json',
        headers=None,
        exchange=mock_processor.exchange,
        routing_key=mock_processor.routing_key)


def test_process_file_success_failure_mix(patch_storage, patch_rabbit, tmp_path):
    error_message_description = 'tests value invalid failure message'
    error_detail_message = '[Column: header_1, Error: tests value invalid failure message]'

    schema = {'header_1': [no_invalid_validator(message=error_message_description)], 'header_2': []}
    header = ','.join(key for key in schema.keys())
    mock_processor = setup_mock_processor(schema, None)
    mock_processor.build_event_messages.side_effect = lambda row: [row]
    bulk_processor = BulkProcessor(mock_processor)
    bulk_processor.working_dir = tmp_path
    bulk_processor.rabbit = patch_rabbit
    test_file = RESOURCE_PATH.joinpath('bulk_test_file_success_failure_mix.csv')

    success_file, error_file, error_detail_file = bulk_processor.initialise_results_files(test_file.name)
    success_count, failure_count = bulk_processor.process_file(test_file, success_file, error_file,
                                                               error_detail_file)

    assert failure_count == 1, 'Should fail to process one row'
    assert success_count == 1, 'Should successfully process one row'

    assert success_file.read_text() == header + '\n' + 'foo,bar' + '\n'
    assert error_file.read_text() == header + '\n' + 'invalid,bar' + '\n'
    assert error_detail_file.read_text() == HEADER_IS_VALID + error_detail_message + '\n'

    patch_rabbit.publish_message.assert_called_once_with(
        message=json.dumps({'header_1': 'foo', 'header_2': 'bar'}),
        content_type='application/json',
        headers=None,
        exchange=mock_processor.exchange,
        routing_key=mock_processor.routing_key)


def test_process_file_header_failure(patch_storage, patch_rabbit, tmp_path):
    schema = {'header_1': [], 'header_2': []}
    header = ','.join(key for key in schema.keys())
    mock_processor = setup_mock_processor(schema, None)
    bulk_processor = BulkProcessor(mock_processor)
    bulk_processor.working_dir = tmp_path
    test_file = RESOURCE_PATH.joinpath('bulk_test_file_header_failure.csv')

    success_file, error_file, error_detail_file = bulk_processor.initialise_results_files(test_file.name)
    success_count, failure_count = bulk_processor.process_file(test_file, success_file, error_file,
                                                               error_detail_file)

    assert failure_count == 1, 'Should fail to process one row'
    assert not success_count, 'Should not successfully process any rows'

    assert success_file.read_text() == header + '\n'
    assert error_file.read_text() == test_file.read_text()
    assert 'header_2' in error_detail_file.read_text()

    patch_rabbit.publish_message.assert_not_called()


def test_process_file_encoding_failure(patch_storage, patch_rabbit, tmp_path):
    schema = {'header_1': [], 'header_2': []}
    header = ','.join(key for key in schema.keys())
    mock_processor = setup_mock_processor(schema, None)
    bulk_processor = BulkProcessor(mock_processor)
    bulk_processor.working_dir = tmp_path
    test_file = RESOURCE_PATH.joinpath('bulk_test_file_encoding_failure.csv')

    success_file, error_file, error_detail_file = bulk_processor.initialise_results_files(test_file.name)
    success_count, failure_count = bulk_processor.process_file(test_file, success_file, error_file,
                                                               error_detail_file)

    assert failure_count == 1, 'Should have one failure when it tries to decode the file'
    assert not success_count, 'Should not successfully process any rows'

    assert success_file.read_text() == header + '\n'
    assert 'Invalid file encoding, requires utf-8' in error_detail_file.read_text()
    patch_rabbit.publish_message.assert_not_called()


def test_run_validation_successful(patch_storage, patch_rabbit, patch_db_helper, tmp_path):
    # Given
    test_message = {"test_message": "blah"}
    mock_processor = setup_mock_processor({'header_1': [], 'header_2': []}, test_message)
    bulk_processor = BulkProcessor(mock_processor)
    bulk_processor.working_dir = tmp_path
    mock_blob = Mock()
    mock_blob.name = 'mock_blob_name'
    patch_storage.Client.return_value.list_blobs.return_value = [mock_blob]

    patch_storage.Client.return_value.download_blob_to_file.side_effect = partial(mock_download_blob,
                                                                                  mock_data=(b'header_1,header_2\n'
                                                                                             b'value1,value2\n'))

    # When
    bulk_processor.run()

    # Then
    mock_upload_to_bucket = patch_storage.Client.return_value.bucket.return_value.blob.return_value \
        .upload_from_filename
    mock_upload_to_bucket.assert_called_once_with(str(tmp_path.joinpath('PROCESSED_mock_blob_name')))
    patch_rabbit.return_value.__enter__.return_value.publish_message.assert_called_once_with(
        message=json.dumps(test_message),
        content_type='application/json', headers=None,
        exchange=mock_processor.exchange, routing_key=mock_processor.routing_key)
    patch_db_helper.connect_to_read_replica_pool.assert_called_once()
    assert_no_left_over_files(tmp_path)


def test_run_header_validation_fails(patch_storage, patch_rabbit, patch_db_helper, tmp_path):
    # Given
    mock_processor = setup_mock_processor({'header': []}, None)
    bulk_processor = BulkProcessor(mock_processor)
    bulk_processor.working_dir = tmp_path
    mock_blob = Mock()
    mock_blob.name = 'mock_blob_name'
    patch_storage.Client.return_value.list_blobs.return_value = [mock_blob]

    patch_storage.Client.return_value.download_blob_to_file.side_effect = partial(mock_download_blob,
                                                                                  mock_data=b'invalid_header\n')

    # When
    bulk_processor.run()

    # Then
    mock_upload_to_bucket = patch_storage.Client.return_value.bucket.return_value.blob.return_value \
        .upload_from_filename
    mock_upload_calls = mock_upload_to_bucket.call_args_list
    assert len(mock_upload_calls) == 2, 'Upload to bucket should be called twice'
    assert call(str(tmp_path.joinpath('ERROR_mock_blob_name'))) in mock_upload_calls
    assert call(str(tmp_path.joinpath('ERROR_DETAIL_mock_blob_name'))) in mock_upload_calls
    patch_rabbit.return_value.__enter__.return_value.publish_message.assert_not_called()
    patch_db_helper.connect_to_read_replica_pool.assert_called_once()

    assert_no_left_over_files(tmp_path)


def test_run_success_failure_mix(patch_storage, patch_rabbit, patch_db_helper, tmp_path):
    # Given
    test_message = {"test_message": "blah"}

    mock_processor = setup_mock_processor({'header': [no_invalid_validator()]}, test_message)
    bulk_processor = BulkProcessor(mock_processor)
    bulk_processor.working_dir = tmp_path
    mock_blob = Mock()
    mock_blob.name = 'mock_blob_name'
    patch_storage.Client.return_value.list_blobs.return_value = [mock_blob]

    patch_storage.Client.return_value.download_blob_to_file.side_effect = partial(mock_download_blob,
                                                                                  mock_data=(b'header\n'
                                                                                             b'value\n'
                                                                                             b'invalid'))
    # When
    bulk_processor.run()

    # Then
    mock_upload_to_bucket = patch_storage.Client.return_value.bucket.return_value.blob.return_value. \
        upload_from_filename
    mock_upload_calls = mock_upload_to_bucket.call_args_list
    assert len(mock_upload_calls) == 3, 'Upload to bucket should be called twice'
    assert call(str(tmp_path.joinpath('PROCESSED_mock_blob_name'))) in mock_upload_calls
    assert call(str(tmp_path.joinpath('ERROR_mock_blob_name'))) in mock_upload_calls
    assert call(str(tmp_path.joinpath('ERROR_DETAIL_mock_blob_name'))) in mock_upload_calls

    patch_rabbit.return_value.__enter__.return_value.publish_message.assert_called_once_with(
        message=json.dumps(test_message),
        content_type='application/json', headers=None,
        exchange=mock_processor.exchange, routing_key=mock_processor.routing_key)
    patch_db_helper.connect_to_read_replica_pool.assert_called_once()
    assert_no_left_over_files(tmp_path)


def setup_mock_processor(schema, test_message):
    mock_processor = Mock(spec=Processor)
    mock_processor.schema = schema
    mock_processor.build_event_messages.return_value = [test_message]
    mock_processor.exchange = "events"
    mock_processor.routing_key = 'tests.mctest'
    return mock_processor


def mock_download_blob(_source_blob, destination_file, mock_data):
    destination_file.write(mock_data)


def assert_no_left_over_files(tmp_path):
    assert len([working_file for working_file in tmp_path.iterdir()]) == 0, \
        'No working files should be left over'


def no_invalid_validator(message='Invalid'):
    def validate(value, **_):
        if value == 'invalid':
            raise Invalid(message)

    return validate

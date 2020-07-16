import json
from functools import partial
from unittest.mock import Mock, call

from bulk_processing.bulk_processor import BulkProcessor
from bulk_processing.processor_interface import Processor
from bulk_processing.validators import Invalid


def test_run_validation_successful(patching_storage, patching_rabbit, tmp_path):
    # Given
    test_message = {"test_message": "blah"}
    mock_processor = setup_mock_processor({'header_1': [], 'header_2': []}, test_message)
    bulk_processor = BulkProcessor(mock_processor)
    bulk_processor.working_dir = tmp_path
    mock_blob = Mock()
    mock_blob.name = 'mock_blob_name'
    patching_storage.Client.return_value.list_blobs.return_value = [mock_blob]

    patching_storage.Client.return_value.download_blob_to_file.side_effect = partial(mock_download_blob,
                                                                                     mock_data=(b'header_1,header_2\n'
                                                                                                b'value1,value2\n'))

    # When
    bulk_processor.run()

    # Then
    mock_upload_to_bucket = patching_storage.Client.return_value.bucket.return_value.blob.return_value \
        .upload_from_filename
    mock_upload_to_bucket.assert_called_once_with(str(tmp_path.joinpath('processed_mock_blob_name')))
    patching_rabbit.return_value.__enter__.return_value.publish_message.assert_called_once_with(
        message=json.dumps(test_message),
        content_type='application/json', headers=None,
        exchange=mock_processor.exchange, routing_key=mock_processor.routing_key)
    assert_no_left_over_files(tmp_path)


def test_run_header_validation_fails(patching_storage, patching_rabbit, tmp_path):
    # Given
    mock_processor = Mock(spec=Processor)
    mock_processor.schema = {'header': []}
    mock_processor.build_event_messages.return_value = []
    bulk_processor = BulkProcessor(mock_processor)
    bulk_processor.working_dir = tmp_path
    mock_blob = Mock()
    mock_blob.name = 'mock_blob_name'
    patching_storage.Client.return_value.list_blobs.return_value = [mock_blob]

    patching_storage.Client.return_value.download_blob_to_file.side_effect = partial(mock_download_blob,
                                                                                     mock_data=b'invalid_header\n')

    # When
    bulk_processor.run()

    # Then
    mock_upload_to_bucket = patching_storage.Client.return_value.bucket.return_value.blob.return_value \
        .upload_from_filename
    mock_upload_calls = mock_upload_to_bucket.call_args_list
    assert len(mock_upload_calls) == 2, 'Upload to bucket should be called twice'
    assert call(str(tmp_path.joinpath('failed_mock_blob_name'))) in mock_upload_calls
    assert call(str(tmp_path.joinpath('failure_reasons_mock_blob_name'))) in mock_upload_calls
    patching_rabbit.return_value.__enter__.return_value.publish_message.assert_not_called()

    assert_no_left_over_files(tmp_path)


def test_run_success_failure_mix(patching_storage, patching_rabbit, tmp_path):
    # Given

    def no_invalid(value, **_):
        if value == 'invalid':
            raise Invalid("Value cannot be 'invalid'")

    test_message = {"test_message": "blah"}

    mock_processor = setup_mock_processor({'header': [no_invalid]}, test_message)
    bulk_processor = BulkProcessor(mock_processor)
    bulk_processor.working_dir = tmp_path
    mock_blob = Mock()
    mock_blob.name = 'mock_blob_name'
    patching_storage.Client.return_value.list_blobs.return_value = [mock_blob]

    patching_storage.Client.return_value.download_blob_to_file.side_effect = partial(mock_download_blob,
                                                                                     mock_data=(b'header\n'
                                                                                                b'value\n'
                                                                                                b'invalid'))
    # When
    bulk_processor.run()

    # Then
    mock_upload_to_bucket = patching_storage.Client.return_value.bucket.return_value.blob.return_value. \
        upload_from_filename
    mock_upload_calls = mock_upload_to_bucket.call_args_list
    assert len(mock_upload_calls) == 3, 'Upload to bucket should be called twice'
    assert call(str(tmp_path.joinpath('processed_mock_blob_name'))) in mock_upload_calls
    assert call(str(tmp_path.joinpath('failed_mock_blob_name'))) in mock_upload_calls
    assert call(str(tmp_path.joinpath('failure_reasons_mock_blob_name'))) in mock_upload_calls

    patching_rabbit.return_value.__enter__.return_value.publish_message.assert_called_once_with(
        message=json.dumps(test_message),
        content_type='application/json', headers=None,
        exchange=mock_processor.exchange, routing_key=mock_processor.routing_key)
    assert_no_left_over_files(tmp_path)


def setup_mock_processor(schema, test_message):
    mock_processor = Mock(spec=Processor)
    mock_processor.schema = schema
    mock_processor.build_event_messages.return_value = [test_message]
    mock_processor.exchange = "events"
    mock_processor.routing_key = 'test.mctest'
    return mock_processor


def mock_download_blob(_source_blob, destination_file, mock_data):
    destination_file.write(mock_data)


def assert_no_left_over_files(tmp_path):
    assert len([working_file for working_file in tmp_path.iterdir()]) == 0, \
        'No working files should be left over'

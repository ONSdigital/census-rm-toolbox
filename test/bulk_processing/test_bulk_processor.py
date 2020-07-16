from unittest.mock import Mock

from bulk_processing.bulk_processor import BulkProcessor
from bulk_processing.processor_interface import Processor


def test_process_file():
    # Given
    mock_processor = Mock(spec=Processor)
    bulk_processor = BulkProcessor(mock_processor)

    # When
    bulk_processor.process_file()
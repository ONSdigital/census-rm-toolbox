from unittest.mock import patch

import pytest


@pytest.fixture
def patching_rabbit():
    with patch('bulk_processing.bulk_processor.RabbitContext') as patch_rabbit:
        yield patch_rabbit


@pytest.fixture
def patching_storage():
    with patch('bulk_processing.bulk_processor.storage') as patch_storage:
        yield patch_storage

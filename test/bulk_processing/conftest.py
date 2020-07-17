from unittest.mock import patch

import pytest


@pytest.fixture
def patch_rabbit():
    with patch('bulk_processing.bulk_processor.RabbitContext') as patched_rabbit:
        yield patched_rabbit


@pytest.fixture
def patch_storage():
    with patch('bulk_processing.bulk_processor.storage') as patched_storage:
        yield patched_storage

from unittest.mock import patch

import pytest


@pytest.fixture
def patch_rabbit():
    with patch('toolbox.bulk_processing.bulk_processor.RabbitContext') as patched_rabbit:
        yield patched_rabbit


@pytest.fixture
def patch_storage():
    with patch('toolbox.bulk_processing.bulk_processor.storage') as patched_storage:
        yield patched_storage


@pytest.fixture
def patch_db_helper():
    with patch('toolbox.bulk_processing.bulk_processor.db_helper') as patched_db_helper:
        yield patched_db_helper

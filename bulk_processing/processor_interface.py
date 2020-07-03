from abc import ABC
from typing import Collection


class Processor(ABC):
    """Abstract base class for processors"""

    def check_for_files_to_process(self) -> Collection[str]:
        pass

    def get_fieldnames(self) -> Collection[str]:
        pass

    def validate_file(self, file) -> (bool, str):
        pass

    def validate_row(self, row) -> (bool, str):
        pass

    def build_event_message(self, row) -> str:
        pass

from abc import ABC, abstractmethod
from typing import Collection


class Processor(ABC):
    """Abstract base class for processors"""

    @abstractmethod
    def check_for_files_to_process(self) -> Collection[str]:
        pass

    @abstractmethod
    def get_fieldnames(self) -> Collection[str]:
        pass

    @abstractmethod
    def validate_file(self, file) -> (bool, str):
        pass

    @abstractmethod
    def validate_row(self, row) -> (bool, str):
        pass

    @abstractmethod
    def build_event_message(self, row) -> str:
        pass

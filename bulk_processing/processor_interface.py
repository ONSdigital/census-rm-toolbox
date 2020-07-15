from abc import ABC, abstractmethod


class Processor(ABC):
    EXCHANGE = None
    ROUTING_KEY = None
    FILE_PREFIX = None

    @abstractmethod
    def find_format_validation_failures(self, header):
        pass

    @abstractmethod
    def find_row_validation_failures(self, line_number, row):
        pass

    @abstractmethod
    def build_event_messages(self, row):
        pass


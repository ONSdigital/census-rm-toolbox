from abc import ABC, abstractmethod


class Processor(ABC):
    """An abstract base class for processor implementations to inherit
    Will raise a TypeError if any of it's children do not overwrite all of it's abstract methods or properties"""

    @property
    @abstractmethod
    def schema(self): pass

    @property
    @abstractmethod
    def file_prefix(self): pass

    @property
    @abstractmethod
    def routing_key(self): pass

    @property
    @abstractmethod
    def exchange(self): pass

    @property
    @abstractmethod
    def bucket_name(self): pass

    @abstractmethod
    def build_event_messages(self, row): pass

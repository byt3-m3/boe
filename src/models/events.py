from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Event(ABC):
    @abstractmethod
    def handle(self, **kwargs):
        pass

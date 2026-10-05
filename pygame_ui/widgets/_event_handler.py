from abc import ABC, abstractmethod


class EventHandler(ABC):
    @abstractmethod
    def update(self, event) -> None:
        pass

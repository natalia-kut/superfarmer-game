from abc import ABC, abstractmethod
from typing import Optional

from pygame.event import Event
from pygame.surface import Surface

from .theme import Theme


class View(ABC):
    def __init__(self, screen: Surface, theme: Theme) -> None:
        self._screen: Surface = screen
        self._theme: Theme = theme

    @abstractmethod
    def render(self) -> None:
        pass

    @abstractmethod
    def update(self, event: Event) -> Optional["View"]:
        pass

    @property
    def screen(self) -> Surface:
        return self._screen

    @property
    def theme(self) -> Theme:
        return self._theme

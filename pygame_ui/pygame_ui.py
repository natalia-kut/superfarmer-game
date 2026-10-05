from typing import Final, Optional

import pygame
from pygame import display
from pygame.surface import Surface

from .theme import Theme
from .view import View
from .views.main_menu_view import MainMenuView

pygame.init()

_WINDOW_HEIGHT: Final[int] = 500
_WINDOW_WIDTH: Final[int] = 800
_WINDOW_TITLE: Final[str] = "Superfarmer"


class PygameUI:
    def __init__(self) -> None:
        self._screen: Surface = display.set_mode((_WINDOW_WIDTH, _WINDOW_HEIGHT))

        display.set_caption(_WINDOW_TITLE)

        self._quit: bool = False
        self._theme: Theme = Theme()
        self._view: Optional[View] = MainMenuView(self._screen, self._theme)
        self._view_stack: list[View] = []

    def update(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit = True
                return

            if (next_view := self._view.update(event)) is None:
                self._view = self._view_stack.pop() if self._view_stack else None
            elif next_view is not self._view:
                self._view_stack.append(self._view)
                self._view = next_view

        if self._view is None:
            self._quit = True
            return

        self._view.render()

        display.flip()

    @property
    def quit(self) -> None:
        return self._quit

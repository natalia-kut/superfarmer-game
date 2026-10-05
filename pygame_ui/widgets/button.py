from collections.abc import Callable

import pygame
from pygame import mouse
from pygame.event import Event

from ._event_handler import EventHandler
from ._rectful_widget_mixin import RectfulWidgetMixin
from ._stateful_widget_mixin import StatefulWidgetMixin


class Button(EventHandler, RectfulWidgetMixin, StatefulWidgetMixin):
    Action = Callable[[], None]

    def __init__(self, label: str, action: Action) -> None:

        self.action: Button.Action = action
        self.label: str = label
        self.icon = None

    @property
    def text(self) -> str:
        return self.label

    def update(self, event: Event) -> None:
        if self.is_disabled:
            return

        if event.type == pygame.KEYDOWN and self.is_selected:
            if event.key == pygame.K_ESCAPE:
                self.idle()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if self.collides(mouse.get_pos()):
                    self.action()
        elif event.type == pygame.MOUSEMOTION:
            if self.collides(mouse.get_pos()):
                self.hover()
            else:
                self.idle()

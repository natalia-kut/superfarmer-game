from typing import Optional

import pygame
from pygame import mouse
from pygame.event import Event

from ._event_handler import EventHandler
from ._rectful_widget_mixin import RectfulWidgetMixin
from ._stateful_widget_mixin import StatefulWidgetMixin


class TextField(EventHandler, RectfulWidgetMixin, StatefulWidgetMixin):
    def __init__(self, text: str = "", maximal_text_length: Optional[int] = None) -> None:
        self.text: str = text
        self.maximal_text_length: Optional[int] = maximal_text_length

        self._text_buffer: str = ""

    def update(self, event: Event) -> None:
        if self.is_disabled:
            return

        if event.type == pygame.KEYDOWN and self.is_selected:
            if event.key == pygame.K_ESCAPE:
                self.text = self._text_buffer
                self.idle()
            else:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.idle()
                else:
                    self.text += event.unicode
                    self.text = self.text[: self.maximal_text_length or len(self.text)]
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if self.collides(mouse.get_pos()):
                    self._text_buffer = self.text
                    self.select()
                else:
                    self.idle()
        elif event.type == pygame.MOUSEMOTION and not self.is_selected:
            if self.collides(mouse.get_pos()):
                self.hover()
            else:
                self.idle()

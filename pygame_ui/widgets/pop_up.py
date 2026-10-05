from collections.abc import Sequence
from pygame.event import Event
from ._event_handler import EventHandler
from .button import Button


class PopUp(EventHandler):
    def __init__(self, buttons: Sequence[Button]) -> None:
        self._buttons: Sequence[Button] = buttons

    def update(self, event: Event) -> None:
        for button in self._buttons:
            button.update(event)

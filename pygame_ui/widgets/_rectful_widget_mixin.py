from typing import Optional

from pygame import Rect


class RectfulWidgetMixin:
    def collides(self, point: tuple[int, int]) -> bool:
        if self.rect is None:
            return False

        return self.rect.collidepoint(point)

    @property
    def rect(self) -> Optional[Rect]:
        return getattr(self, "_rect", None)

    @rect.setter
    def rect(self, rect: Rect) -> None:
        self._rect = rect

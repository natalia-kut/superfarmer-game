from .herd import Herd


class Player:
    def __init__(self, name: str):
        self._name = name
        self._herd = Herd()
        self._can_trade = False
        self._is_active = True

    @property
    def herd(self) -> Herd:
        return self._herd

    @property
    def name(self) -> str:
        return self._name

    @property
    def can_trade(self) -> bool:
        return self._can_trade

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self._is_active = value

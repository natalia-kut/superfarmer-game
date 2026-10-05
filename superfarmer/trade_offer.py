from typing import Optional

from .player import Player
from .species import Species


class TradeOffer:
    def __init__(self) -> None:
        self.trade_from: dict[Species, int] = {}
        self.trade_to: dict[Species, int] = {}
        self.trade_to_player: Optional[Player] = None

    def __bool__(self) -> bool:
        return bool(self.trade_from) and bool(self.trade_to)

    def clear(self) -> None:
        self.trade_from.clear()
        self.trade_to.clear()
        self.trade_to_player = None

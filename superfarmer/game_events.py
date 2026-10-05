from typing import Final, Optional

from .dice import Dice
from .event import Event
from .herd import Herd
from .player import Player
from .trade_offer import TradeOffer


class BreedingEndsEvent(Event):
    ID: Final[str] = __qualname__

    def __init__(self) -> None:
        super().__init__(__class__.ID)


class DiceRollEvent(Event):
    ID: Final[str] = __qualname__

    def __init__(self, items: tuple[Dice.Item]) -> None:
        super().__init__(__class__.ID)
        self._items: tuple[Dice.Item] = items

    @property
    def items(self) -> tuple[Dice.Item]:
        return self._items


class MainHerdChangesEvent(Event):
    ID: Final[str] = __qualname__

    def __init__(self):
        super().__init__(__class__.ID)


class _PlayerEvent(Event):
    def __init__(self, event_id: str, player: Player) -> None:
        super().__init__(event_id)
        self._player = player

    @property
    def player(self) -> Player:
        return self._player


class PlayerChangesEvent(_PlayerEvent):
    ID: Final[str] = __qualname__

    def __init__(self, player: Player) -> None:
        super().__init__(__class__.ID, player)


class PlayerWinsEvent(_PlayerEvent):
    ID: Final[str] = __qualname__

    def __init__(self, player: Player) -> None:
        super().__init__(__class__.ID, player)


class PlayerHerdChangesEvent(_PlayerEvent):
    ID: Final[str] = __qualname__

    def __init__(self, player: Player):
        super().__init__(__class__.ID, player)


class TradeBeginsEvent(Event):
    ID: Final[str] = __qualname__

    def __init__(self) -> None:
        super().__init__(__class__.ID)
        self.main_herd: Optional[Herd] = None
        self.trade_offer: TradeOffer = TradeOffer()
        self.trade_to_players: list[Player] = []


class WaitingForDiceRollEvent(Event):
    ID: Final[str] = __qualname__

    def __init__(self) -> None:
        super().__init__(__class__.ID)

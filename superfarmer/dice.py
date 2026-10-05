from collections.abc import Sequence
from random import choices
from typing import Any


class Dice:
    Item = Any
    ItemWeight = float

    def __init__(self, items: Sequence[Item], weights: Sequence[ItemWeight]) -> None:
        if len(items) != len(weights):
            raise ValueError(items, weights)  # TODO

        self._items: Sequence[Dice.Item] = items
        self._weights: Sequence[Dice.ItemWeight] = weights

    def roll(self) -> Item:
        return choices(self._items, weights=self._weights)[0]

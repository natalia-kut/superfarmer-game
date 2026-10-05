from functools import wraps
from typing import Optional

from .species import Species


def _update_herd_value(method):
    @wraps(method)
    def updater(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self._herd_value = (
            sum(
                self.get_animal_count(species) * self._exchange_rate.get(species, 0)
                for species in self.get_animal_species()
            )
            if self._exchange_rate
            else 0
        )
        return result

    return updater


class Herd:
    @_update_herd_value
    def __init__(
        self,
        herd: Optional[dict[Species, int]] = None,
        exchange_rate: Optional[dict[Species, int]] = None,
    ) -> None:
        self._herd = herd if herd is not None else {}
        self._herd_value = 0
        self._exchange_rate = exchange_rate

    @property
    def exchange_rate(self) -> dict[Species, int]:
        return self._exchange_rate

    @exchange_rate.setter
    @_update_herd_value
    def exchange_rate(self, exchange_rate: Optional[dict[Species, int]]) -> None:
        self._exchange_rate = exchange_rate

    @property
    def herd_value(self) -> int:
        return self._herd_value

    @_update_herd_value
    def add_animal(self, species: Species, count: int) -> None:
        if count < 0:
            raise ValueError(count)  # TODO

        self._herd[species] = self.get_animal_count(species) + count

    @_update_herd_value
    def clear(self) -> dict[Species, int]:
        herd = self._herd.copy()
        self._herd = {}

        return herd

    def get_animal_count(self, species: Species) -> int:
        return self._herd.get(species, 0)

    def get_animal_species(self) -> set[Species]:
        return sorted(
            set(
                species
                for species in self._herd.keys()
                if self.get_animal_count(species) > 0
            )
        )

    @_update_herd_value
    def remove_animal(self, species: Species, count: Optional[int] = None) -> int:
        if count is None:
            count = self.get_animal_count(species)
        elif count < 0:
            raise ValueError(count)  # TODO

        animal_count = self.get_animal_count(species)
        remove_count = min(animal_count, count)

        self._herd[species] = animal_count - remove_count

        return remove_count

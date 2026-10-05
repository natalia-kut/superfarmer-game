from collections.abc import Generator, Sequence
from itertools import cycle

from .dice import Dice
from .event import Event
from .game_events import (
    BreedingEndsEvent,
    DiceRollEvent,
    MainHerdChangesEvent,
    PlayerChangesEvent,
    PlayerHerdChangesEvent,
    PlayerWinsEvent,
    TradeBeginsEvent,
    WaitingForDiceRollEvent,
)
from .herd import Herd
from .player import Player
from .species import WILD_ANIMALS, Species
from .trade_offer import TradeOffer


class Game:
    def __init__(self, players: Sequence[Player]) -> None:
        self._players = tuple(players)
        self._exchange_rate = {
            Species.RABBIT: 1,
            Species.SHEEP: 6,
            Species.PIG: 12,
            Species.COW: 36,
            Species.HORSE: 108,
            Species.SMALL_DOG: 6,
            Species.BIG_DOG: 36,
        }
        self._main_herd = Herd(
            {
                Species.RABBIT: 60,
                Species.SHEEP: 24,
                Species.PIG: 20,
                Species.COW: 12,
                Species.HORSE: 6,
                Species.SMALL_DOG: 4,
                Species.BIG_DOG: 2,
            },
            self._exchange_rate,
        )
        for player in self._players:
            player.herd.exchange_rate = self._exchange_rate
        self._minimal_trade_value = 6
        self._green_dice = Dice(
            [
                Species.RABBIT,
                Species.SHEEP,
                Species.PIG,
                Species.COW,
                Species.WOLF,
            ],
            [6, 3, 1, 1, 1],
        )
        self._red_dice = Dice(
            [
                Species.RABBIT,
                Species.SHEEP,
                Species.PIG,
                Species.HORSE,
                Species.FOX,
            ],
            [6, 2, 2, 1, 1],
        )

    @property
    def main_herd(self) -> Herd:
        return self._main_herd

    @property
    def players(self) -> tuple[Player]:
        return self._players

    def play(self) -> Generator[Event, Event, None]:
        for player in cycle(self._players):
            if not player.is_active:
                continue

            yield PlayerChangesEvent(player)
            yield from self._trade_animals(player)
            yield from self._breed_animals(player)

    def _check_is_winner(self, player: Player) -> bool:
        return not any(
            player.herd.get_animal_count(species) == 0
            for species in (
                Species.RABBIT,
                Species.SHEEP,
                Species.PIG,
                Species.COW,
                Species.HORSE,
            )
        )

    def _check_can_trade(self, player: Player) -> bool:
        return self._check_is_tradable(player.herd)

    def _check_is_tradable(self, herd: Herd) -> bool:
        return herd.herd_value >= self._minimal_trade_value

    def _breed_animals(self, player: Player) -> Generator[Event, None, None]:
        yield WaitingForDiceRollEvent()

        green_roll_species: Species = self._green_dice.roll()
        red_roll_species: Species = self._red_dice.roll()

        yield DiceRollEvent((green_roll_species, red_roll_species))

        is_player_herd_changed = False

        if green_roll_species == Species.WOLF:
            if player.herd.get_animal_count(Species.BIG_DOG) > 0:
                self._main_herd.add_animal(
                    Species.BIG_DOG, player.herd.remove_animal(Species.BIG_DOG, 1)
                )

                is_player_herd_changed = True
            else:
                for species in (
                    Species.RABBIT,
                    Species.SHEEP,
                    Species.PIG,
                    Species.COW,
                ):
                    remove_animal_count = player.herd.remove_animal(species)
                    self._main_herd.add_animal(species, remove_animal_count)
                    is_player_herd_changed = remove_animal_count > 0

        if red_roll_species == Species.FOX:
            if player.herd.get_animal_count(Species.SMALL_DOG) > 0:
                self._main_herd.add_animal(
                    Species.SMALL_DOG, player.herd.remove_animal(Species.SMALL_DOG, 1)
                )

                is_player_herd_changed = True
            else:
                remove_animal_count = player.herd.remove_animal(Species.RABBIT)
                self._main_herd.add_animal(Species.RABBIT, remove_animal_count)

                is_player_herd_changed = remove_animal_count > 0

        def update_player_herd(species: Species, new_animal_count: int) -> None:
            if species in WILD_ANIMALS:
                return

            brood_size = (player.herd.get_animal_count(species) + new_animal_count) // 2
            brood_size = self._main_herd.remove_animal(species, brood_size)

            if brood_size == 0:
                return

            player.herd.add_animal(species, brood_size)

            nonlocal is_player_herd_changed
            is_player_herd_changed = True

        if green_roll_species == red_roll_species:
            update_player_herd(green_roll_species, 2)
        else:
            update_player_herd(green_roll_species, 1)
            update_player_herd(red_roll_species, 1)

        if is_player_herd_changed:
            yield MainHerdChangesEvent()
            yield PlayerHerdChangesEvent(player)

        if self._check_is_winner(player):
            yield PlayerWinsEvent(player)

        yield BreedingEndsEvent()

    def _trade_animals(self, player: Player) -> Generator[Event, None, None]:
        if not self._check_can_trade(player):
            return

        event = TradeBeginsEvent()

        if self._check_is_tradable(self.main_herd):
            event.main_herd = self.main_herd

        for trade_to_player in self._players:
            if trade_to_player.name != player.name and self._check_can_trade(
                trade_to_player
            ):
                event.trade_to_players.append(trade_to_player)

        while not event.trade_offer:
            yield event

            if event.trade_offer:
                yield from self._try_accept_or_reject_trade_offer(
                    player, event.trade_offer
                )

                # The trade offer was rejected; wait for another one.
                if not event.trade_offer:
                    continue

                if self._check_is_winner(player):
                    yield PlayerWinsEvent(player)
                elif (
                    trade_to_player := event.trade_offer.trade_to_player
                ) is not None and self._check_is_winner(trade_to_player):
                    yield PlayerWinsEvent(trade_to_player)
            else:
                # The player didn't make a trade offer, which means they do not
                # want to trade.
                break

    def _try_accept_or_reject_trade_offer(
        self, player: Player, trade_offer: TradeOffer
    ) -> Generator[Event, None, None]:
        def reject_trade_offer() -> None:
            trade_offer.clear()

        if not (len(trade_offer.trade_from) == 1 or len(trade_offer.trade_to) == 1):
            print("trade odrzucony, 1:N lub N:1")
            reject_trade_offer()
            return

        target_herd: Herd = (
            self._main_herd
            if trade_offer.trade_to_player is None
            else trade_offer.trade_to_player.herd
        )

        for species, count in trade_offer.trade_to.items():
            if target_herd.get_animal_count(species) < count:
                print("trade odrzucony, nie ma tylu zwierzat w docelowym herd")
                reject_trade_offer()
                return

        for species, count in trade_offer.trade_from.items():
            if player.herd.get_animal_count(species) < count:
                print("trade odrzucony, klamiesz ze masz tyle zwierzat")
                reject_trade_offer()
                return

        trade_from_value = Herd(trade_offer.trade_from, self._exchange_rate).herd_value
        trade_to_value = Herd(trade_offer.trade_to, self._exchange_rate).herd_value

        if trade_from_value != trade_to_value:
            print("trade odrzucony, za tyle to nie")
            reject_trade_offer()
            return

        if trade_offer.trade_to_player is not None:
            # TODO: ask for permission,
            pass

        for species, count in trade_offer.trade_from.items():
            target_herd.add_animal(species, player.herd.remove_animal(species, count))

        for species, count in trade_offer.trade_to.items():
            player.herd.add_animal(species, target_herd.remove_animal(species, count))

        yield PlayerHerdChangesEvent(player)
        yield (
            MainHerdChangesEvent()
            if trade_offer.trade_to_player is None
            else PlayerHerdChangesEvent(trade_offer.trade_to_player)
        )

from superfarmer.game_events import (
    DiceRollEvent,
    MainHerdChangesEvent,
    PlayerChangesEvent,
    PlayerHerdChangesEvent,
    PlayerWinsEvent,
    TradeEvent,
    WaitingForDiceRollEvent,
)
from superfarmer.herd import Herd
from superfarmer.trade_offer import TradeOffer


class CLIUserInterface:
    def __init__(self):
        self._player_name: str = ""

    @staticmethod
    def format_herd(herd: Herd) -> str:
        return ", ".join(
            f"{species} x{herd.get_animal_count(species)}"
            for species in herd.get_animal_species()
        )

    def update(self, event):
        match event.event_id:
            case PlayerChangesEvent.ID:
                self._player_name = event.player.name
                print(f"{self._player_name}'s turn.")
                print(
                    f"{self._player_name}, your farm: [{self.format_herd(event.player.herd)}]"
                )
            case PlayerWinsEvent.ID:
                print(f"{self._player_name}, you win!")
            case WaitingForDiceRollEvent.ID:
                print(f"{self._player_name}, press enter to roll the dice...")
                input()
            case DiceRollEvent.ID:
                print(
                    "{}, you've rolled {} and {}.".format(
                        self._player_name, *event.items
                    )
                )
            case TradeEvent.ID:
                print("Available farms to trade:")
                for player in event.trade_to_players:
                    print(f"{player.name}'s farm: [{self.format_herd(player.herd)}]")
                print(f"Main herd: [{self.format_herd(event.main_herd)}]")
                trade_will = input(
                    f"{self._player_name}, do you want to trade your animals? Y/N "
                )
                if trade_will.upper() == "Y":
                    trade_offer = TradeOffer()
                    for i, player in enumerate(event.trade_to_players):
                        print(f"Press {i} to select {player.name}")
                    print("To select main herd select MH")
                    chosen_herd = input("")
                    if chosen_herd.upper() == "MH":
                        trade_offer.trade_to_player = None
                    else:
                        trade_offer.trade_to_player = event.trade_to_players[
                            chosen_herd
                        ]
                    print(chosen_herd)
                    available_animals = list(
                        enumerate(event.player.herd.get_animal_species())
                    )
                    for i, species in available_animals:
                        print(f"Press {i} to select {species}.")
                    print("To finish selecting animals press F.")
                    choice = input("")
                    if choice.upper() != "F":
                        chosen_species = available_animals[int(choice)][1]
                        chosen_number = int(
                            input(f"How many {chosen_species} do you want to trade? ")
                        )
                        if (
                            chosen_number
                            > event.player.herd.get_animal_count(chosen_species)
                            or chosen_number < 0
                        ):
                            chosen_number = input(
                                f"You do not have that many {chosen_species} on your farm. Select again, how many {chosen_species} do you want to trade? "
                            )
                        trade_offer.trade_from[chosen_species] = chosen_number
                    # event.start_trade()
                # else:

                # print()
            case PlayerHerdChangesEvent.ID:
                print(f"{self._player_name}, your farm has changed.")
                print(
                    f"{self._player_name}, your farm: [{self.format_herd(event.player.herd)}]"
                )
                pass
            case MainHerdChangesEvent.ID:
                # print("Zwierzaki wracaja do sklepu")
                pass

from functools import partial
from typing import Optional

from pygame import Rect, Surface
from pygame.event import Event

from superfarmer.game_events import TradeBeginsEvent
from superfarmer.herd import Herd
from superfarmer.player import Player

from ..theme import LIGHT_GRAY, Theme
from ..view import View
from ..widgets import Button
from .trade_offer_view import TradeOfferView


class TradeToMenuView(View):

    def __init__(
        self,
        screen: Surface,
        theme: Theme,
        player: Player,
        trade_begins_event: TradeBeginsEvent,
    ) -> None:
        super().__init__(screen, theme)

        self._is_trade_offer_view_shown: bool = False
        self._next_view: Optional[View] = self

        self._player: Player = player
        self._trade_begins_event: TradeBeginsEvent = trade_begins_event

        self._trade_target_buttons: tuple[Button] = (
            *(
                (
                    Button(
                        "Main Herd",
                        partial(
                            self._on_trade_target_button_action,
                            trade_begins_event.main_herd,
                            None,
                        ),
                    ),
                )
                if trade_begins_event.main_herd
                else ()
            ),
            *(
                Button(
                    player.name,
                    partial(self._on_trade_target_button_action, player.herd, player),
                )
                for player in trade_begins_event.trade_to_players
            ),
        )
        self._back_button: Button = Button("Back", self._on_back_button_action)
        self._buttons: tuple[Button] = (*self._trade_target_buttons, self._back_button)

    def render(self) -> None:
        self.screen.fill(LIGHT_GRAY)

        screen_height: int = self.screen.get_height()
        half_screen_height: int = screen_height // 2
        screen_width: int = self.screen.get_width()
        half_screen_width: int = screen_width // 2

        button_height: int = 40
        button_width: int = 200
        half_button_width: int = button_width // 2

        button_horizontal_position: int = half_screen_width - half_button_width
        button_vertical_offset: int = 18

        button_count: int = len(self._trade_target_buttons) or 1
        button_column_height = (
            button_count * button_height + (button_count - 1) * button_vertical_offset
        )

        button_vertical_position: int = half_screen_height - button_column_height // 2

        for button in self._trade_target_buttons:
            button.rect = Rect(
                button_horizontal_position,
                button_vertical_position,
                button_width,
                button_height,
            )
            self.theme.draw_button(self.screen, button)

            button_vertical_position += button_height + button_vertical_offset

        button_horizontal_padding_size: int = 22
        button_vertical_padding_size: int = 18

        self._back_button.rect = Rect(
            button_horizontal_padding_size,
            screen_height - button_vertical_padding_size - button_height,
            button_width,
            button_height,
        )
        self.theme.draw_button(self.screen, self._back_button)

    def update(self, event: Event) -> Optional[View]:
        if self._is_trade_offer_view_shown:
            return None

        for button in self._buttons:
            button.update(event)

        return self._next_view

    def _on_back_button_action(self) -> None:
        self._next_view = None

    def _on_trade_target_button_action(
        self, trade_to_herd: Herd, trade_to_player: Optional[Player]
    ) -> None:
        self._is_trade_offer_view_shown = True
        self._trade_begins_event.trade_offer.trade_to_player = trade_to_player
        self._next_view = TradeOfferView(
            self.screen,
            self.theme,
            self._player,
            self._trade_begins_event.trade_offer,
            trade_to_herd,
        )

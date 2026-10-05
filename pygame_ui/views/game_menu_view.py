from itertools import chain
from typing import Final, Optional

from pygame import Rect, Surface
from pygame.event import Event

from superfarmer.game import Game
from superfarmer.player import Player

from ..theme import BLACK, Theme
from ..view import View
from ..widgets import Button, TextField
from .game_view import GameView

_MAXIMAL_PLAYER_COUNT: Final[int] = 6
_MINIMAL_PLAYER_COUNT: Final[int] = 2
_MAXIMAL_PLAYER_NAME_LENGTH: Final[int] = 12


class GameMenuView(View):

    def __init__(self, screen: Surface, theme: Theme):
        super().__init__(screen, theme)

        self._next_view: Optional[View] = self

        self._decrease_button: Button = Button("-", self._on_decrease_button_action)
        self._increase_button: Button = Button("+", self._on_increase_button_action)
        self._back_button: Button = Button("Back", self._on_back_button_action)
        self._play_button: Button = Button("Play", self._on_play_button_action)
        self._buttons: tuple[Button] = (
            self._decrease_button,
            self._increase_button,
            self._back_button,
            self._play_button,
        )
        self._player_count: int = 0
        self._update_player_count()
        self._player_name_text_fields: list[TextField] = []
        self._update_player_name_text_fields()

    def render(self) -> None:
        self._theme.draw_background(self._screen)

        screen_width: int = self.screen.get_width()
        screen_height: int = self.screen.get_height()
        screen_half_width: int = screen_width // 2

        # Title
        title_surface: Surface = self._theme.font.render(
            "Player Selection", True, BLACK
        )
        title_rect: Rect = title_surface.get_rect(center=(screen_half_width, 60))
        self._screen.blit(title_surface, title_rect)

        # Number of players selector
        player_count_text: Surface = self._theme.small_font.render(
            f"Number of players: {self._player_count}", True, BLACK
        )
        self._screen.blit(player_count_text, (screen_half_width - 150, 120))

        self._decrease_button.rect = Rect(screen_half_width + 80, 120, 30, 30)
        self._theme.draw_button(self._screen, self._decrease_button)

        self._increase_button.rect = Rect(screen_half_width + 120, 120, 30, 30)
        self._theme.draw_button(self._screen, self._increase_button)

        for player_index in range(self._player_count):
            text_field: TextField = self._player_name_text_fields[player_index]
            input_rect: Rect = Rect(
                screen_half_width - 150, 180 + player_index * 50, 300, 35
            )
            text_field.rect = input_rect
            self.theme.draw_text_field(
                self._screen, self._player_name_text_fields[player_index]
            )

        button_height: int = 40
        button_width: int = 200
        button_horizontal_padding_size: int = 22
        button_vertical_padding_size: int = 18
        button_vertical_position: int = (
            screen_height - button_vertical_padding_size - button_height
        )

        self._back_button.rect = Rect(
            button_horizontal_padding_size,
            button_vertical_position,
            button_width,
            button_height,
        )
        self._theme.draw_button(self._screen, self._back_button)

        self._play_button.rect = Rect(
            screen_width - button_horizontal_padding_size - button_width,
            button_vertical_position,
            button_width,
            button_height,
        )
        self._theme.draw_button(self._screen, self._play_button)

    def update(self, event: Event) -> Optional[View]:
        self._next_view = self

        for widget in chain(self._buttons, self._player_name_text_fields):
            widget.update(event)

        return self._next_view

    def _update_player_count(self) -> None:
        self._player_count = max(
            _MINIMAL_PLAYER_COUNT,
            min(_MAXIMAL_PLAYER_COUNT, self._player_count),
        )

    def _update_player_name_text_fields(self) -> None:
        if (
            text_field_count := len(self._player_name_text_fields)
        ) < self._player_count:
            for text_field_index in range(text_field_count, self._player_count):
                self._player_name_text_fields.append(
                    TextField(
                        text=f"Player {text_field_index + 1}",
                        maximal_text_length=_MAXIMAL_PLAYER_NAME_LENGTH,
                    )
                )

        for text_field in self._player_name_text_fields[: self._player_count]:
            if text_field.is_disabled:
                text_field.idle()

        for text_field in self._player_name_text_fields[self._player_count :]:
            text_field.disable()

    def _on_back_button_action(self) -> None:
        self._next_view = None

    def _on_decrease_button_action(self) -> None:
        self._player_count -= 1
        self._update_player_count()
        self._update_player_name_text_fields()

    def _on_increase_button_action(self) -> None:
        self._player_count += 1
        self._update_player_count()
        self._update_player_name_text_fields()

    def _on_play_button_action(self) -> None:
        self._next_view = GameView(
            self.screen,
            self.theme,
            Game(
                players=(
                    Player(self._player_name_text_fields[player_index].text)
                    for player_index in range(self._player_count)
                )
            ),
        )

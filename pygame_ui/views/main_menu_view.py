from typing import Final, Optional

from pygame import Rect, Surface
from pygame.event import Event

from ..theme import BLACK, Theme
from ..view import View
from ..widgets.button import Button
from .game_menu_view import GameMenuView

_MAIN_MENU_TITLE: Final[str] = "SpoKo Farmer"


class MainMenuView(View):
    def __init__(self, screen: Surface, theme: Theme):
        super().__init__(screen, theme)

        self._next_view: Optional[View] = self

        self._start_game_button: Button = Button(
            "Start Game", self._on_start_game_button_action
        )
        self._exit_button: Button = Button("Exit", self._on_exit_button_action)
        self._buttons: tuple[Button] = (self._start_game_button, self._exit_button)

    def render(self) -> None:
        self.theme.draw_background(self._screen)

        screen_height: int = self.screen.get_height()
        half_screen_height: int = screen_height // 2
        screen_width: int = self.screen.get_width()
        half_screen_width: int = screen_width // 2

        title_vertical_position: int = self._screen.get_height() // 4
        title_surface: Surface = self.theme.font.render(_MAIN_MENU_TITLE, True, BLACK)
        title_rect: Rect = title_surface.get_rect(
            center=(half_screen_width, title_vertical_position)
        )
        self._screen.blit(title_surface, title_rect)

        button_height: int = 40
        button_width: int = 200
        half_button_width: int = button_width // 2

        button_horizontal_position: int = half_screen_width - half_button_width
        button_vertical_offset: int = 18
        button_vertical_position: int = (
            title_vertical_position + 2 * button_vertical_offset
        )

        button_count = len(self._buttons) or 1
        button_column_height = (
            button_count * button_height + (button_count - 1) * button_vertical_offset
        )

        button_vertical_position: int = half_screen_height - button_column_height // 2

        for button in self._buttons:
            button.rect = Rect(
                button_horizontal_position,
                button_vertical_position,
                button_width,
                button_height,
            )

            button_vertical_position += button_height + button_vertical_offset

            self.theme.draw_button(self._screen, button)

    def update(self, event: Event) -> Optional[View]:
        self._next_view = self

        for button in self._buttons:
            button.update(event)

        return self._next_view

    def _on_exit_button_action(self) -> None:
        self._next_view = None

    def _on_start_game_button_action(self) -> None:
        self._next_view = GameMenuView(self._screen, self.theme)

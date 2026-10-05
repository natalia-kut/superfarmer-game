from collections.abc import Callable, Generator
from typing import Optional

import pygame
from pygame import Rect, Surface
from pygame.event import Event

from superfarmer.event import Event as GameEvent
from superfarmer.game import Game
from superfarmer.game_events import (
    BreedingEndsEvent,
    DiceRollEvent,
    MainHerdChangesEvent,
    PlayerChangesEvent,
    PlayerHerdChangesEvent,
    PlayerWinsEvent,
    TradeBeginsEvent,
    WaitingForDiceRollEvent,
)
from superfarmer.player import Player

from ..assets import Assets
from ..theme import BLACK, WHITE, Theme
from ..view import View
from ..widgets import Button, TextField
from .trade_to_menu_view import TradeToMenuView


class GameView(View):
    POPUP_WIDTH = 500
    POPUP_HEIGHT = 200
    POPUP_BUTTON_WIDTH = 80
    POPUP_BUTTON_HEIGHT = 30
    POPUP_BUTTON_Y_OFFSET = 60

    def __init__(self, screen: Surface, theme: Theme, game: Game):
        super().__init__(screen, theme)

        self._next_view: Optional[View] = self

        self._game: Game = game
        self._game_event: Optional[GameEvent] = None
        self._game_event_generator: Optional[Generator[GameEvent, None, None]] = None
        self._is_trading: bool = False
        self._player: Optional[Player] = None

        self._exit_button = Button("Exit", self._on_exit_button_action)
        self._next_event_button = Button("Play", self._on_next_event_button_action)
        self._pop_up_close_button = Button("Close", self._on_pop_up_close_button_action)
        self._trade_pop_up_yes_button: Button = Button(
            "Yes", self._on_trade_pop_up_yes_button_action
        )
        self._trade_pop_up_no_button: Button = Button(
            "No", self._on_trade_pop_up_no_button_action
        )
        self._buttons: tuple[Button] = (
            self._exit_button,
            self._next_event_button,
            self._pop_up_close_button,
            self._trade_pop_up_no_button,
            self._trade_pop_up_yes_button,
        )
        self._player_text_field: TextField = TextField()
        self._pop_up: Optional[Callable[[__class__], None]] = None

        self._player_farm_background = Assets().player_farm_background.convert()
        pygame.mixer.music.load("sounds/funnycountry.mp3")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        self._animal_images_roll = Assets().animal_images_roll
        self._animal_images_herd = Assets().animal_images_herd
        self._dice_icon = Assets().dice_icon
        self._dice_icon = pygame.transform.smoothscale(self._dice_icon, (24, 24))
        self._dice_sound = Assets().dice_sound

        self._win_sound = Assets().win_sound

        self._update_game_event()
        self._handle_game_event()

    def render(self) -> None:
        self._theme.draw_background(self._screen)

        screen_height: int = self.screen.get_height()
        screen_width: int = self.screen.get_width()
        player_count = len(self._game.players)
        player_column_width = screen_width // (player_count + 1)
        for player_index in range(player_count + 1):
            column_x = player_index * player_column_width
            input_rect = pygame.Rect(
                column_x,
                0,
                player_column_width,
                self.screen.get_height(),
            )
            scaled_bg = pygame.transform.scale(
                self._player_farm_background,
                (player_column_width, self.screen.get_height()),
            )
            self.screen.blit(scaled_bg, (column_x, 0))
            # pygame.draw.rect(self.screen, WHITE, input_rect, border_radius=5)
            pygame.draw.rect(
                self.screen, BLACK, input_rect, 2, border_radius=5
            )  # Border

            if player_index == player_count:
                title_text = "Main herd"
            else:
                title_text = f"{self._game.players[player_index]._name}"

            max_width = player_column_width - 20
            font = self.theme.font
            title_text_trimmed = title_text
            font_size = font.get_height()
            min_font_size = 10
            rendered = font.render(title_text_trimmed, True, BLACK)
            while rendered.get_width() > max_width and font_size > min_font_size:
                font_size -= 1
                font = pygame.font.Font(None, font_size)
                rendered = font.render(title_text_trimmed, True, BLACK)
            title = rendered

            title_rect = title.get_rect(
                center=(column_x + player_column_width // 2, 60)
            )
            self.screen.blit(title, title_rect)

            if player_index == player_count:
                herd = self._game._main_herd
            else:
                herd = self._game.players[player_index].herd

            icon_size = 32
            animal_y = 100
            line_height = 40

            for species in herd.get_animal_species():
                count = herd.get_animal_count(species)
                if count == 0:
                    continue

                icon = pygame.transform.scale(
                    self._animal_images_herd[species], (icon_size, icon_size)
                )
                icon_x = column_x + player_column_width // 2 - icon_size // 2 - 20

                self.screen.blit(icon, (icon_x, animal_y))

                count_text = self.theme.font.render(str(count), True, BLACK)
                count_rect = count_text.get_rect(
                    midleft=(icon_x + icon_size + 10, animal_y + icon_size // 2)
                )
                self.screen.blit(count_text, count_rect)

                animal_y += line_height

        button_height: int = 40
        button_width: int = 200
        button_horizontal_padding_size: int = 22
        button_vertical_padding_size: int = 18
        button_vertical_position: int = (
            screen_height - button_vertical_padding_size - button_height
        )

        self._exit_button.rect = Rect(
            button_horizontal_padding_size,
            button_vertical_position,
            button_width,
            button_height,
        )
        self._theme.draw_button(self._screen, self._exit_button)

        self._player_text_field.rect = Rect(
            screen_width // 2 - button_width // 2,
            button_vertical_position,
            button_width,
            button_height,
        )
        self._player_text_field.text = self._player.name
        self.theme.draw_text_field(self.screen, self._player_text_field)

        self._next_event_button.rect = Rect(
            screen_width - button_horizontal_padding_size - button_width,
            button_vertical_position,
            button_width,
            button_height,
        )
        self._theme.draw_button(self._screen, self._next_event_button)

        if self._pop_up is not None:
            self._pop_up()

    def update(self, event: Event) -> Optional[View]:
        self._next_view = self

        if self._is_trading:
            self._handle_trade()
        else:
            for button in self._buttons:
                button.update(event)

        return self._next_view

    def _handle_game_event(self) -> None:
        print("Obecny game event:", self._game_event)
        self._next_event_button.icon = None

        if self._game_event is None:
            return

        if self._game_event.event_id == BreedingEndsEvent.ID:
            pass
        elif self._game_event.event_id == DiceRollEvent.ID:
            self._dice_sound.play()
            self._next_event_button.label = "..."
            self._next_event_button.disable()
            self._pop_up = self._render_dice_popup
            self._pop_up_close_button.idle()
        elif self._game_event.event_id == MainHerdChangesEvent.ID:
            self._handle_herd_changes_event()
        elif self._game_event.event_id == PlayerChangesEvent.ID:
            self._next_event_button.label = "..."
            self._next_event_button.disable()
            self._player = self._game_event.player
            self._pop_up = self._render_player_change_popup
            self._pop_up_close_button.idle()
        elif self._game_event.event_id == PlayerHerdChangesEvent.ID:
            self._handle_herd_changes_event()
        elif self._game_event.event_id == PlayerWinsEvent.ID:
            self._next_event_button.label = "Finish Game"
            self._next_event_button.action = self._on_finish_game_button_action
        elif self._game_event.event_id == TradeBeginsEvent.ID:
            self._handle_trade_begins_event()
        elif self._game_event.event_id == WaitingForDiceRollEvent.ID:
            self._next_event_button.icon = self._dice_icon
            self._next_event_button.label = "Roll Dice"

    def _handle_herd_changes_event(self) -> None:
        self.render()
        self._update_game_event()
        self._handle_game_event()

    def _handle_trade(self) -> None:
        self._is_trading = False
        if self._game_event.trade_offer:
            self._update_game_event()
            self._handle_game_event()
        else:
            self._handle_trade_begins_event()

    def _handle_trade_begins_event(self) -> None:
        self._next_event_button.label = "..."
        self._next_event_button.disable()
        self._pop_up = self._render_trade_question_popup
        self._trade_pop_up_no_button.idle()
        self._trade_pop_up_yes_button.idle()

    def _on_exit_button_action(self) -> None:
        pygame.mixer.music.stop()
        self._next_view = None

    def _on_finish_game_button_action(self) -> None:
        self._win_sound.play()
        self._next_event_button.disable()
        self._next_event_button.label = "..."
        self._pop_up = self._render_player_wins_popup
        self._pop_up_close_button.idle()

    def _on_next_event_button_action(self) -> None:
        self._update_game_event()
        self._handle_game_event()

    def _on_pop_up_close_button_action(self) -> None:
        self._next_event_button.idle()
        self._pop_up = None
        self._pop_up_close_button.disable()

        if self._game_event is not None:
            if self._game_event.event_id == DiceRollEvent.ID:
                self._next_event_button.label = "End Turn"
                self._update_game_event()
                self._handle_game_event()
            elif self._game_event.event_id == PlayerChangesEvent.ID:
                self._next_event_button.label = "Done"
            elif self._game_event.event_id == PlayerWinsEvent.ID:
                self._next_event_button.disable()

    def _on_trade_pop_up_no_button_action(self) -> None:
        self._next_event_button.idle()
        self._pop_up = None
        self._trade_pop_up_no_button.disable()
        self._trade_pop_up_yes_button.disable()
        self._update_game_event()
        self._handle_game_event()

    def _on_trade_pop_up_yes_button_action(self) -> None:
        self._is_trading = True
        self._next_event_button.idle()
        self._next_view = TradeToMenuView(
            self.screen, self.theme, self._player, self._game_event
        )
        self._pop_up = None
        self._trade_pop_up_no_button.disable()
        self._trade_pop_up_yes_button.disable()

    def _update_game_event(self):
        if self._game_event_generator is None:
            self._game_event_generator = self._game.play()

        try:
            self._game_event = next(self._game_event_generator)
        except StopIteration:
            self._game_event = None  # TODO

    def _render_dice_popup(self) -> None:
        box_width, box_height = self.POPUP_WIDTH, self.POPUP_HEIGHT
        box_x = self.screen.get_width() // 2 - box_width // 2
        box_y = self.screen.get_height() // 2 - box_height // 2
        pygame.draw.rect(
            self.screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=10
        )
        pygame.draw.rect(
            self.screen,
            BLACK,
            (box_x, box_y, box_width, box_height),
            2,
            border_radius=10,
        )
        title = self.theme.small_font.render(
            f"{self._player.name}, you rolled:", True, BLACK
        )
        title_rect = title.get_rect(center=(box_x + box_width // 2, box_y + 40))
        self.screen.blit(title, title_rect)

        icon_size = 48
        spacing = 60
        dice_items = self._game_event.items
        start_x = box_x + (box_width - (len(dice_items) * spacing)) // 2
        y = box_y + 70

        for i, item in enumerate(dice_items):
            img = pygame.transform.scale(
                self._animal_images_roll[item], (icon_size, icon_size)
            )
            self.screen.blit(img, (start_x + i * spacing, y))

        self._pop_up_close_button.rect = Rect(
            box_x + box_width // 2 - self.POPUP_BUTTON_WIDTH // 2,
            box_y + box_height - self.POPUP_BUTTON_Y_OFFSET,
            self.POPUP_BUTTON_WIDTH,
            self.POPUP_BUTTON_HEIGHT,
        )
        self.theme.draw_button(self.screen, self._pop_up_close_button)

    def _render_player_change_popup(self) -> None:
        box_width, box_height = self.POPUP_WIDTH, self.POPUP_HEIGHT
        box_x = self.screen.get_width() // 2 - box_width // 2
        box_y = self.screen.get_height() // 2 - box_height // 2

        pygame.draw.rect(
            self.screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=10
        )
        pygame.draw.rect(
            self.screen,
            BLACK,
            (box_x, box_y, box_width, box_height),
            2,
            border_radius=10,
        )

        text = self.theme.small_font.render(
            f"{self._player.name}, your turn. Check your herd!", True, BLACK
        )
        text_rect = text.get_rect(center=(box_x + box_width // 2, box_y + 60))
        self.screen.blit(text, text_rect)

        self._pop_up_close_button.rect = Rect(
            box_x + box_width // 2 - self.POPUP_BUTTON_WIDTH // 2,
            box_y + box_height - self.POPUP_BUTTON_Y_OFFSET,
            self.POPUP_BUTTON_WIDTH,
            self.POPUP_BUTTON_HEIGHT,
        )
        self.theme.draw_button(self.screen, self._pop_up_close_button)

    def _render_player_wins_popup(self) -> None:
        box_width, box_height = self.POPUP_WIDTH, self.POPUP_HEIGHT
        box_x = self.screen.get_width() // 2 - box_width // 2
        box_y = self.screen.get_height() // 2 - box_height // 2

        pygame.draw.rect(
            self.screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=10
        )
        pygame.draw.rect(
            self.screen,
            BLACK,
            (box_x, box_y, box_width, box_height),
            2,
            border_radius=10,
        )

        text = self.theme.small_font.render(
            f"{self._game_event.player.name}, you win!", True, BLACK
        )
        text_rect = text.get_rect(center=(box_x + box_width // 2, box_y + 60))
        self.screen.blit(text, text_rect)

        self._pop_up_close_button.rect = Rect(
            box_x + box_width // 2 - self.POPUP_BUTTON_WIDTH // 2,
            box_y + box_height - self.POPUP_BUTTON_Y_OFFSET,
            self.POPUP_BUTTON_WIDTH,
            self.POPUP_BUTTON_HEIGHT,
        )
        self.theme.draw_button(self.screen, self._pop_up_close_button)

    def _render_trade_question_popup(self):
        box_width, box_height = self.POPUP_WIDTH, self.POPUP_HEIGHT
        box_x = self.screen.get_width() // 2 - box_width // 2
        box_y = self.screen.get_height() // 2 - box_height // 2
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (box_x, box_y, box_width, box_height),
            border_radius=10,
        )
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (box_x, box_y, box_width, box_height),
            2,
            border_radius=10,
        )
        text = self.theme.small_font.render(
            f"{self._player.name}, do you want to trade?", True, (0, 0, 0)
        )
        text_rect = text.get_rect(center=(box_x + box_width // 2, box_y + 60))
        self.screen.blit(text, text_rect)

        self._trade_pop_up_yes_button.rect = Rect(
            box_x + box_width // 2 - 100,
            box_y + box_height - self.POPUP_BUTTON_Y_OFFSET,
            80,
            30,
        )
        self.theme.draw_button(self.screen, self._trade_pop_up_yes_button)

        self._trade_pop_up_no_button.rect = Rect(
            box_x + box_width // 2 + 20,
            box_y + box_height - self.POPUP_BUTTON_Y_OFFSET,
            80,
            30,
        )
        self.theme.draw_button(self.screen, self._trade_pop_up_no_button)

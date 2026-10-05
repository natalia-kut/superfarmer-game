from functools import partial
from itertools import chain
from typing import Optional

import pygame
from pygame import Rect, Surface
from pygame.event import Event

from superfarmer.herd import Herd
from superfarmer.player import Player
from superfarmer.species import Species
from superfarmer.trade_offer import TradeOffer

from ..assets import Assets
from ..theme import BLACK, LIGHT_GRAY, WHITE, Theme
from ..view import View
from ..widgets.button import Button


class TradeOfferView(View):

    def __init__(
        self,
        screen: Surface,
        theme: Theme,
        player: Player,
        trade_offer: TradeOffer,
        trade_to_herd: Herd,
    ):
        super().__init__(screen, theme)

        self._next_view: Optional[View] = self
        self._show_trade_offer_pop_up: bool = False
        self._show_exhange_rate_pop_up: bool = False
        self._show_trade_to_player_view: bool = False

        self._player: Player = player
        self._trade_offer: TradeOffer = trade_offer
        self._trade_to_herd: Herd = trade_to_herd

        self._assets: Assets = Assets()

        self._trade_from: dict[Species, int] = {
            species: self._player.herd.get_animal_count(species)
            for species in self._player.herd.get_animal_species()
        }
        self._trade_offer.trade_from = {species: 0 for species in self._trade_from}
        self._trade_from_decrease_buttons: tuple[Button] = tuple(
            Button("-", partial(self._on_trade_from_decrease_button_action, species))
            for species in self._trade_from
        )
        self._trade_from_increase_buttons: tuple[Button] = tuple(
            Button("+", partial(self._on_trade_from_increase_button_action, species))
            for species in self._trade_from
        )

        self._trade_to: dict[Species, int] = {
            species: self._trade_to_herd.get_animal_count(species)
            for species in self._trade_to_herd.get_animal_species()
        }
        self._trade_offer.trade_to = {species: 0 for species in self._trade_to}
        self._trade_to_decrease_buttons: tuple[Button] = tuple(
            Button("-", partial(self._on_trade_to_decrease_button_action, species))
            for species in self._trade_to
        )
        self._trade_to_increase_buttons: tuple[Button] = tuple(
            Button("+", partial(self._on_trade_to_increase_button_action, species))
            for species in self._trade_to
        )

        self._trade_offer_trade_from_value: int = 0
        self._trade_offer_trade_to_value: int = 0

        self._update_decrease_button_state()
        self._update_increase_button_state()

        self._cancel_button = Button("Cancel", self._on_cancel_button_action)
        self._exchange_rate_button = Button(
            "Exchange rate", self._on_exchange_rate_button_action
        )
        self._accept_button = Button("Accept", self._on_accept_button_action)

        self._update_accept_button_state()

        self._pop_up_button: Button = Button(
            "Close", self._on_exchange_rate_pop_up_button_action
        )
        self._reject_trade_offer_button = Button(
            "Reject", self._on_reject_trade_offer_button_action
        )
        self._accept_trade_offer_button = Button(
            "Accept", self._on_accept_trade_offer_button_action
        )

        self._buttons: tuple[Button] = (
            *self._trade_from_decrease_buttons,
            *self._trade_from_increase_buttons,
            *self._trade_to_decrease_buttons,
            *self._trade_to_increase_buttons,
            self._cancel_button,
            self._exchange_rate_button,
            self._accept_button,
            self._pop_up_button,
            self._reject_trade_offer_button,
            self._accept_trade_offer_button,
        )

    def update(self, event: Event) -> Optional[View]:
        self._next_view = self

        for button in self._buttons:
            button.update(event)

        return self._next_view

    def render(self):
        self.screen.fill(LIGHT_GRAY)

        screen_height: int = self.screen.get_height()
        screen_width: int = self.screen.get_width()

        button_height: int = 40
        button_width: int = 200

        button_horizontal_padding_size: int = 22
        button_vertical_padding_size: int = 18
        button_vertical_position: int = (
            screen_height - button_vertical_padding_size - button_height
        )

        if self._show_trade_to_player_view:
            self._reject_trade_offer_button.rect = Rect(
                screen_width - 2 * button_horizontal_padding_size - 2 * button_width,
                button_vertical_position,
                button_width,
                button_height,
            )
            self.theme.draw_button(self.screen, self._reject_trade_offer_button)

            self._accept_trade_offer_button.rect = Rect(
                screen_width - button_horizontal_padding_size - button_width,
                button_vertical_position,
                button_width,
                button_height,
            )
            self.theme.draw_button(self._screen, self._accept_trade_offer_button)
        else:
            self._cancel_button.rect = Rect(
                button_horizontal_padding_size,
                button_vertical_position,
                button_width,
                button_height,
            )
            self.theme.draw_button(self.screen, self._cancel_button)

            self._exchange_rate_button.rect = Rect(
                screen_width // 2 - button_width // 2,
                button_vertical_position,
                button_width,
                button_height,
            )
            self.theme.draw_button(self.screen, self._exchange_rate_button)

            self._accept_button.rect = Rect(
                screen_width - button_horizontal_padding_size - button_width,
                button_vertical_position,
                button_width,
                button_height,
            )
            self.theme.draw_button(self._screen, self._accept_button)

        column_count: int = 2
        column_horizontal_padding_size: int = button_horizontal_padding_size
        column_width: int = (
            screen_width - 4 * column_horizontal_padding_size
        ) // column_count
        column_horizontal_positions: tuple[int] = tuple(
            (column_index + 1) * column_horizontal_padding_size
            + (column_width + column_horizontal_padding_size) * column_index
            for column_index in range(column_count)
        )

        column_vertical_padding_size: int = button_vertical_padding_size
        column_vertical_position: int = column_vertical_padding_size

        small_button_width: int = 40
        small_button_vertical_padding_size: int = 18
        small_button_height: int = 40
        small_button_horizontal_padding_size: int = 18

        column_species: tuple[dict[Species, int]] = (self._trade_from, self._trade_to)
        column_trade_offer_species: tuple[dict[Species, int]] = (
            self._trade_offer.trade_from,
            self._trade_offer.trade_to,
        )
        column_decrease_buttons: tuple[tuple[Button]] = (
            self._trade_from_decrease_buttons,
            self._trade_to_decrease_buttons,
        )
        column_inncrease_buttons: tuple[tuple[Button]] = (
            self._trade_from_increase_buttons,
            self._trade_to_increase_buttons,
        )
        for column_index in range(column_count):
            small_button_y: int = (
                column_vertical_position + small_button_vertical_padding_size
            )
            small_button_horizontal_offset: int = (
                small_button_width + small_button_horizontal_padding_size
            )

            for species_index, (species, animal_count) in enumerate(
                column_species[column_index].items()
            ):
                small_button_x: int = (
                    column_horizontal_positions[column_index]
                    + small_button_horizontal_padding_size
                )

                if icon := self._assets.animal_images_herd[species]:
                    self.screen.blit(
                        pygame.transform.scale(
                            icon, (small_button_width, small_button_height)
                        ),
                        (small_button_x, small_button_y),
                    )

                small_button_x += small_button_horizontal_offset

                self.screen.blit(
                    animal_count_surface := self.theme.small_font.render(
                        f"{animal_count}", True, (0, 0, 0)
                    ),
                    animal_count_surface.get_rect(
                        center=(
                            small_button_x + small_button_width // 2,
                            small_button_y + small_button_height // 2,
                        )
                    ),
                )

                small_button_x += small_button_horizontal_offset

                if not self._show_trade_to_player_view:
                    column_decrease_button: Button = column_decrease_buttons[
                        column_index
                    ][species_index]
                    column_decrease_button.rect = Rect(
                        small_button_x,
                        small_button_y,
                        small_button_width,
                        small_button_height,
                    )
                    self.theme.draw_button(self.screen, column_decrease_button)

                small_button_x += small_button_horizontal_offset

                if not self._show_trade_to_player_view:
                    column_inncrease_button: Button = column_inncrease_buttons[
                        column_index
                    ][species_index]
                    column_inncrease_button.rect = Rect(
                        small_button_x,
                        small_button_y,
                        small_button_width,
                        small_button_height,
                    )
                    self.theme.draw_button(self.screen, column_inncrease_button)

                small_button_x += small_button_horizontal_offset

                trade_offer_animal_count: int = column_trade_offer_species[
                    column_index
                ][species]
                self.screen.blit(
                    trade_offer_animal_count_surface := self.theme.small_font.render(
                        f"{trade_offer_animal_count}", True, (0, 0, 0)
                    ),
                    trade_offer_animal_count_surface.get_rect(
                        center=(
                            small_button_x + small_button_width // 2,
                            small_button_y + small_button_height // 2,
                        )
                    ),
                )

                small_button_y += (
                    small_button_vertical_padding_size + small_button_height
                )

        if self._show_exhange_rate_pop_up:
            self._render_exchange_rate_popup()
        elif self._show_trade_offer_pop_up:
            self._render_trade_offer_popup()

    def _on_accept_button_action(self) -> None:
        if self._trade_offer.trade_to_player:
            self._accept_button.disable()
            self._cancel_button.disable()
            self._exchange_rate_button.disable()
            self._pop_up_button.action = self._on_trade_offer_pop_up_button_action
            self._pop_up_button.label = "Show"
            self._pop_up_button.idle()
            self._show_trade_offer_pop_up = True
            for button in self._trade_from_decrease_buttons:
                button.disable()
            for button in self._trade_from_increase_buttons:
                button.disable()
            for button in self._trade_to_decrease_buttons:
                button.disable()
            for button in self._trade_to_increase_buttons:
                button.disable()
        else:
            self._validate_trade_offer()
            self._next_view = None

    def _on_exchange_rate_button_action(self) -> None:
        self._accept_button.disable()
        self._cancel_button.disable()
        self._exchange_rate_button.disable()
        self._pop_up_button.action = self._on_exchange_rate_pop_up_button_action
        self._pop_up_button.label = "Close"
        self._pop_up_button.idle()
        self._show_exhange_rate_pop_up = True
        for button in self._trade_from_decrease_buttons:
            button.disable()
        for button in self._trade_from_increase_buttons:
            button.disable()
        for button in self._trade_to_decrease_buttons:
            button.disable()
        for button in self._trade_to_increase_buttons:
            button.disable()

    def _on_exchange_rate_pop_up_button_action(self) -> None:
        self._cancel_button.idle()
        self._exchange_rate_button.idle()
        self._pop_up_button.disable()
        self._show_exhange_rate_pop_up = False
        self._update_accept_button_state()
        self._update_decrease_button_state()
        self._update_increase_button_state()

    def _on_cancel_button_action(self) -> None:
        self._trade_offer.clear()
        self._next_view = None

    def _on_accept_trade_offer_button_action(self) -> None:
        self._accept_button.idle()
        self._accept_trade_offer_button.disable()
        self._cancel_button.idle()
        self._exchange_rate_button.idle()
        self._reject_trade_offer_button.disable()
        self._show_trade_to_player_view = False
        self._update_accept_button_state()
        self._update_decrease_button_state()
        self._update_increase_button_state()

        self._validate_trade_offer()
        self._next_view = None

    def _on_reject_trade_offer_button_action(self) -> None:
        self._accept_button.idle()
        self._accept_trade_offer_button.disable()
        self._cancel_button.idle()
        self._exchange_rate_button.idle()
        self._reject_trade_offer_button.disable()
        self._show_trade_to_player_view = False
        self._update_accept_button_state()
        self._update_decrease_button_state()
        self._update_increase_button_state()

    def _on_trade_from_decrease_button_action(self, species: Species) -> None:
        if self._trade_offer.trade_from[species] <= 0:
            return

        self._trade_offer.trade_from[species] -= 1
        self._trade_from[species] += 1

        self._trade_offer_trade_from_value -= self._trade_to_herd.exchange_rate.get(
            species, 0
        )

        self._update_accept_button_state()
        self._update_decrease_button_state()
        self._update_increase_button_state()

    def _on_trade_from_increase_button_action(self, species: Species) -> None:
        if self._trade_from[species] <= 0:
            return

        self._trade_from[species] -= 1
        self._trade_offer.trade_from[species] += 1

        self._trade_offer_trade_from_value += self._trade_to_herd.exchange_rate.get(
            species, 0
        )

        self._update_accept_button_state()
        self._update_decrease_button_state()
        self._update_increase_button_state()

    def _on_trade_to_decrease_button_action(self, species: Species) -> None:
        if self._trade_offer.trade_to[species] <= 0:
            return

        self._trade_offer.trade_to[species] -= 1
        self._trade_to[species] += 1

        self._trade_offer_trade_to_value -= self._trade_to_herd.exchange_rate.get(
            species, 0
        )

        self._update_accept_button_state()
        self._update_decrease_button_state()
        self._update_increase_button_state()

    def _on_trade_to_increase_button_action(self, species: Species) -> None:
        if self._trade_to[species] <= 0:
            return

        self._trade_to[species] -= 1
        self._trade_offer.trade_to[species] += 1

        self._trade_offer_trade_to_value += self._trade_to_herd.exchange_rate.get(
            species, 0
        )

        self._update_accept_button_state()
        self._update_decrease_button_state()
        self._update_increase_button_state()

    def _on_trade_offer_pop_up_button_action(self) -> None:
        self._accept_trade_offer_button.idle()
        self._reject_trade_offer_button.idle()
        self._pop_up_button.disable()
        self._show_trade_offer_pop_up = False
        self._show_trade_to_player_view = True

    def _render_exchange_rate_popup(self) -> None:
        box_width: int = 500
        box_height: int = 400
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

        self._assets.pricelist_img = pygame.transform.scale(
            self._assets.pricelist_img, (box_width - 20, box_height - 120)
        )
        self.screen.blit(
            self._assets.pricelist_img,
            (box_x + 10, box_y + 10),
        )

        button_width: int = 150
        button_height: int = 40
        button_vertical_padding: int = 20

        self._pop_up_button.rect = Rect(
            box_x + box_width // 2 - button_width // 2,
            box_y + box_height - button_vertical_padding - button_height,
            button_width,
            button_height,
        )
        self.theme.draw_button(self.screen, self._pop_up_button)

    def _render_trade_offer_popup(self) -> None:
        box_width: int = 500
        box_height: int = 200
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
            f"{self._trade_offer.trade_to_player.name}, check trade offer from {self._player.name}!",
            True,
            BLACK,
        )
        text_rect = text.get_rect(center=(box_x + box_width // 2, box_y + 60))
        self.screen.blit(text, text_rect)

        button_width: int = 150
        button_height: int = 40
        button_vertical_padding: int = 20

        self._pop_up_button.rect = Rect(
            box_x + box_width // 2 - button_width // 2,
            box_y + box_height - button_vertical_padding - button_height,
            button_width,
            button_height,
        )
        self.theme.draw_button(self.screen, self._pop_up_button)

    def _update_accept_button_state(self) -> None:
        if (
            self._trade_offer_trade_from_value != self._trade_offer_trade_to_value
        ) or all(
            animal_count == 0
            for animal_count in chain(
                self._trade_offer.trade_from.values(),
                self._trade_offer.trade_to.values(),
            )
        ):
            self._accept_button.disable()
        else:
            self._accept_button.idle()

    def _update_decrease_button_state(self) -> None:
        for animal_count, button in zip(
            self._trade_offer.trade_from.values(), self._trade_from_decrease_buttons
        ):
            if animal_count > 0:
                button.idle()
            else:
                button.disable()

        for animal_count, button in zip(
            self._trade_offer.trade_to.values(), self._trade_to_decrease_buttons
        ):
            if animal_count > 0:
                button.idle()
            else:
                button.disable()

    def _update_increase_button_state(self) -> None:
        trade_offer_trade_from_species: tuple[Species] = tuple(
            species
            for species, animal_count in self._trade_offer.trade_from.items()
            if animal_count > 0
        )
        trade_offer_trade_to_species: tuple[Species] = tuple(
            species
            for species, animal_count in self._trade_offer.trade_to.items()
            if animal_count > 0
        )

        if (
            len(trade_offer_trade_from_species) > 1
            and len(trade_offer_trade_to_species) > 1
        ):
            for button in self._trade_from_increase_buttons:
                button.disable()
            for button in self._trade_to_increase_buttons:
                button.disable()

        for (species, animal_count), button in zip(
            self._trade_from.items(), self._trade_from_increase_buttons
        ):
            if self._trade_offer.trade_to.get(species, 0) == 0 and animal_count > 0:
                if (
                    len(trade_offer_trade_to_species) > 1
                    and len(trade_offer_trade_from_species) == 1
                    and species not in trade_offer_trade_from_species
                ):
                    button.disable()
                else:
                    button.idle()
            else:
                button.disable()

        for (species, animal_count), button in zip(
            self._trade_to.items(), self._trade_to_increase_buttons
        ):
            if self._trade_offer.trade_from.get(species, 0) == 0 and (
                animal_count > 0
                and self._trade_offer_trade_to_value
                + self._trade_to_herd.exchange_rate.get(species, 0)
                <= self._trade_offer_trade_from_value
            ):
                if (
                    len(trade_offer_trade_from_species) > 1
                    and len(trade_offer_trade_to_species) == 1
                    and species not in trade_offer_trade_to_species
                ):
                    button.disable()
                else:
                    button.idle()
            else:
                button.disable()

    def _validate_trade_offer(self) -> None:
        self._trade_offer.trade_from = {
            species: animal_count
            for species, animal_count in self._trade_offer.trade_from.items()
            if animal_count > 0
        }
        self._trade_offer.trade_to = {
            species: animal_count
            for species, animal_count in self._trade_offer.trade_to.items()
            if animal_count > 0
        }

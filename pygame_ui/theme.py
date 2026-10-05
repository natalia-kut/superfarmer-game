from typing import Final

from pygame import draw, font
from pygame.color import Color
from pygame.font import Font
from pygame.rect import Rect
from pygame.surface import Surface

from .widgets import Button, TextField

font.init()


WHITE: Color = Color(255, 255, 255)
BLACK: Color = Color(0, 0, 0)
GRAY: Color = Color(100, 100, 100)
LIGHT_GRAY: Color = Color(211, 211, 211)
BLUE: Color = Color(0, 0, 255)
GREEN: Color = Color(34, 139, 34)
SKY_BLUE: Color = Color(135, 206, 250)
LIGHT_GREEN: Color = Color(144, 238, 144)


_FONT_SIZE: Final[int] = 50
_SMALL_FONT_SIZE: Final[int] = 32

_BUTTON_BORDER_COLOR: Final[Color] = BLACK
_BUTTON_BORDER_RADIUS: Final[int] = 10
_BUTTON_BORDER_WIDTH: Final[int] = 2
_BUTTON_COLOR_DISABLED: Final[Color] = GRAY
_BUTTON_COLOR_IDLE: Final[Color] = LIGHT_GRAY
_BUTTON_COLOR_SELECTED: Final[Color] = SKY_BLUE
_BUTTON_TEXT_COLOR: Final[Color] = BLACK
_TEXT_FIELD_BORDER_COLOR: Final[Color] = BLACK
_TEXT_FIELD_BORDER_RADIUS: Final[int] = 10
_TEXT_FIELD_BORDER_WIDTH: Final[int] = 2
_TEXT_FIELD_COLOR_IDLE: Final[Color] = WHITE
_TEXT_FIELD_COLOR_SELECTED: Final[Color] = LIGHT_GREEN
_TEXT_FIELD_TEXT_COLOR: Final[Color] = BLACK


class Theme:
    def __init__(self) -> None:
        self._font: Font = Font(None, _FONT_SIZE)
        self._small_font: Font = Font(None, _SMALL_FONT_SIZE)

    def draw_background(self, screen: Surface) -> None:
        screen_half_height: int = screen.get_height() // 2
        screen.fill(SKY_BLUE)
        screen.fill(
            GREEN, (0, screen_half_height, screen.get_width(), screen_half_height)
        )

    def draw_button(self, screen: Surface, button: Button) -> None:
        if button.is_disabled:
            self._draw_button_disabled(screen, button)
        elif button.is_hovered:
            self._draw_button_hovered(screen, button)
        else:
            self._draw_button_idle(screen, button)

    def draw_text_field(self, screen: Surface, text_field: TextField) -> None:
        if text_field.is_selected or text_field.is_hovered:
            self._draw_text_field_selected(screen, text_field)
        else:
            self._draw_text_field_idle(screen, text_field)

    @property
    def font(self) -> Font:
        return self._font

    @property
    def small_font(self) -> Font:
        return self._small_font

    def _draw_button_disabled(self, screen: Surface, button: Button) -> None:
        self._draw_rectangle(
            screen,
            button.rect,
            _BUTTON_COLOR_DISABLED,
            _BUTTON_BORDER_COLOR,
            _BUTTON_BORDER_RADIUS,
            _BUTTON_BORDER_WIDTH,
            button.text,
            _BUTTON_TEXT_COLOR,
            getattr(button, "icon", None),
        )

    def _draw_button_idle(self, screen: Surface, button: Button) -> None:
        self._draw_rectangle(
            screen,
            button.rect,
            _BUTTON_COLOR_IDLE,
            _BUTTON_BORDER_COLOR,
            _BUTTON_BORDER_RADIUS,
            _BUTTON_BORDER_WIDTH,
            button.text,
            _BUTTON_TEXT_COLOR,
            getattr(button, "icon", None),
        )

    def _draw_button_hovered(self, screen: Surface, button: Button) -> None:
        self._draw_rectangle(
            screen,
            button.rect,
            _BUTTON_COLOR_SELECTED,
            _BUTTON_BORDER_COLOR,
            _BUTTON_BORDER_RADIUS,
            _BUTTON_BORDER_WIDTH,
            button.text,
            _BUTTON_TEXT_COLOR,
        )

    def _draw_rectangle(
        self,
        screen: Surface,
        rect: Rect,
        color: Color,
        border_color: Color,
        border_radius: int,
        border_width: int,
        text: str,
        text_color: Color,
        icon=None,
    ) -> None:
        draw.rect(screen, color, rect, border_radius=border_radius)
        draw.rect(
            screen,
            border_color,
            rect,
            border_radius=border_radius,
            width=border_width,
        )
        if icon is not None:
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)
        else:
            screen.blit(
                text_surface := self.small_font.render(text, True, text_color),
                text_surface.get_rect(center=rect.center),
            )

    def _draw_text_field_idle(self, screen: Surface, text_field: TextField) -> None:
        self._draw_rectangle(
            screen,
            text_field.rect,
            _TEXT_FIELD_COLOR_IDLE,
            _TEXT_FIELD_BORDER_COLOR,
            _TEXT_FIELD_BORDER_RADIUS,
            _TEXT_FIELD_BORDER_WIDTH,
            text_field.text,
            _TEXT_FIELD_TEXT_COLOR,
        )

    def _draw_text_field_selected(self, screen: Surface, text_field: TextField) -> None:
        self._draw_rectangle(
            screen,
            text_field.rect,
            _TEXT_FIELD_COLOR_SELECTED,
            _TEXT_FIELD_BORDER_COLOR,
            _TEXT_FIELD_BORDER_RADIUS,
            _TEXT_FIELD_BORDER_WIDTH,
            text_field.text,
            _TEXT_FIELD_TEXT_COLOR,
        )

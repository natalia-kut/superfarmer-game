from enum import Enum, auto


class WidgetState(Enum):
    DISABLED = auto()
    HOVERED = auto()
    IDLE = auto()
    SELECTED = auto()

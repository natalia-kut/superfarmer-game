from ..widget_state import WidgetState


class StatefulWidgetMixin:

    def disable(self) -> None:
        self.state = WidgetState.DISABLED

    def hover(self) -> None:
        self.state = WidgetState.HOVERED

    def idle(self) -> None:
        self.state = WidgetState.IDLE

    @property
    def is_disabled(self) -> bool:
        return self.state == WidgetState.DISABLED

    @property
    def is_hovered(self) -> bool:
        return self.state == WidgetState.HOVERED

    @property
    def is_idle(self) -> bool:
        return self.state == WidgetState.IDLE

    @property
    def is_selected(self) -> bool:
        return self.state == WidgetState.SELECTED

    def select(self) -> None:
        self.state = WidgetState.SELECTED

    @property
    def state(self) -> WidgetState:
        if not hasattr(self, "_state"):
            self._state = WidgetState.IDLE

        return self._state

    @state.setter
    def state(self, state: WidgetState) -> None:
        self._state = state

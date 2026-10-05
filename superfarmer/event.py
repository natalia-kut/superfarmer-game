class Event:
    def __init__(self, event_id: str):
        self._event_id = event_id

    @property
    def event_id(self) -> str:
        return self._event_id

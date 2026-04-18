from abc import ABC, abstractmethod
from typing import Callable


class MouseProvider(ABC):
    @abstractmethod
    def get_position(self) -> tuple[int, int]:
        raise NotImplementedError

    @abstractmethod
    def start_listener(self, on_click: Callable[[int, int, object, bool], None]) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_listener(self) -> None:
        raise NotImplementedError

from pynput import mouse

from ...domain.ports.mouse_provider import MouseProvider


class PynputMouseProvider(MouseProvider):
    def __init__(self):
        self._controller = mouse.Controller()
        self._listener = None

    def get_position(self) -> tuple[int, int]:
        x, y = self._controller.position
        return int(x), int(y)

    def start_listener(self, on_click):
        self._listener = mouse.Listener(on_click=on_click)
        self._listener.start()

    def stop_listener(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

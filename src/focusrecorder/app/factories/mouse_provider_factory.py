from ...domain.ports.mouse_provider import MouseProvider
from ...infrastructure.input.pynput_mouse_provider import PynputMouseProvider


def create_mouse_provider() -> MouseProvider:
    return PynputMouseProvider()

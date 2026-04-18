def recording_zoom_to_ui(zoom: float) -> int:
    return int(zoom * 10)


def ui_zoom_to_recording(ui_value: int) -> float:
    return ui_value / 10.0


def recording_suavidad_to_ui(suavidad: float) -> int:
    return int(suavidad * 100)


def ui_suavidad_to_recording(ui_value: int) -> float:
    return ui_value / 100.0

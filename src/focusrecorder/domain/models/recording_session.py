from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FrameSample:
    frame: Any
    mouse_x: int
    mouse_y: int
    is_clicking: bool
    timestamp: float

    def as_tuple(self):
        return (self.frame, self.mouse_x, self.mouse_y, self.is_clicking, self.timestamp)


@dataclass
class RecordingSessionState:
    is_recording: bool = False
    is_clicking: bool = False
    start_time: float = 0.0
    raw_data: list[tuple[Any, int, int, bool, float]] = field(default_factory=list)

    def reset(self, start_time: float) -> None:
        self.is_recording = True
        self.is_clicking = False
        self.start_time = start_time
        self.raw_data = []

    def stop(self) -> None:
        self.is_recording = False

    def set_clicking(self, pressed: bool) -> None:
        self.is_clicking = pressed

    def append_sample(self, sample: FrameSample) -> None:
        self.raw_data.append(sample.as_tuple())

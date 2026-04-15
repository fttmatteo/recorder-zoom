import time
import pytest
from unittest.mock import MagicMock
import numpy as np

import focusrecorder.recorder as recorder_module
from focusrecorder.recorder import FocusRecorder


def test_recorder_start_and_stop(monkeypatch, tmp_path):
    monkeypatch.setattr(recorder_module.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(recorder_module.pyautogui, "size", lambda: (640, 480))
    rec = FocusRecorder(config={"zoom": 2.0, "suavidad": 0.5, "fps": 30})

    class MockListener:
        def __init__(self, on_click=None):
            self.on_click = on_click
            self.started = False
            self.stopped = False
        def start(self): 
            self.started = True
        def stop(self):
            self.stopped = True

    monkeypatch.setattr(recorder_module.mouse, "Listener", MockListener)

    monkeypatch.setattr(rec, "_render_adaptive_video", lambda *args, **kwargs: None)
    
    def fake_loop():
        time.sleep(0.05)

    monkeypatch.setattr(rec, "_record_loop", fake_loop)
    
    rec.start()
    assert rec.is_recording
    assert rec.listener.started

    rec._on_click(10, 10, None, True)
    assert rec.is_clicking is True
    rec._on_click(10, 10, None, False)
    assert rec.is_clicking is False

    rec.stop()
    assert not rec.is_recording
    assert rec.listener.stopped


def test_record_loop_windows_branch(monkeypatch, tmp_path):
    monkeypatch.setattr(recorder_module.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(recorder_module.pyautogui, "size", lambda: (640, 480))
    
    rec = FocusRecorder(config={})
    rec.is_windows = True
    rec.start_time = time.perf_counter()
    rec.is_recording = True
    
    mock_camera = MagicMock()
    frame_return_count = [0]
    def get_frame():
        frame_return_count[0] += 1
        if frame_return_count[0] > 2:
            rec.is_recording = False
            return None
        return np.zeros((480, 640, 3), dtype=np.uint8)
        
    mock_camera.get_latest_frame.side_effect = get_frame
    rec.camera = mock_camera
    
    monkeypatch.setattr(recorder_module.pyautogui, "position", lambda: (100, 100))

    rec.is_windows = True
    recorder_module.dxcam = MagicMock()
    rec._record_loop()
    
    assert len(rec.raw_data) > 0


def test_record_loop_linux_branch(monkeypatch, tmp_path):
    monkeypatch.setattr(recorder_module.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(recorder_module.pyautogui, "size", lambda: (640, 480))
    
    rec = FocusRecorder(config={})
    rec.is_windows = False
    rec.start_time = time.perf_counter()
    rec.is_recording = True
    
    # Fake MSS
    class FakeMSSContext:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        
    class FakeMSS(FakeMSSContext):
        monitors = [{}]
        def grab(self, monitor):
            rec.is_recording = False
            return np.zeros((100, 100, 4), dtype=np.uint8)
            
    monkeypatch.setattr(recorder_module.mss, "mss", FakeMSS)
    monkeypatch.setattr(recorder_module.pyautogui, "position", lambda: (100, 100))
    monkeypatch.setattr(time, "sleep", lambda x: None)

    rec._record_loop()
    
    assert len(rec.raw_data) == 1
    assert rec.raw_data[0][1] == 100
    assert rec.raw_data[0][2] == 100


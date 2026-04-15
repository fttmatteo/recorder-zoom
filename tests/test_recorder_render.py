import os
import numpy as np
import cv2
from unittest.mock import MagicMock

from focusrecorder.recorder import FocusRecorder
import focusrecorder.recorder as recorder_module

def test_recorder_full_rendering_workflow(monkeypatch, tmp_path):
    monkeypatch.setattr(recorder_module.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(recorder_module.pyautogui, "size", lambda: (640, 480))
    
    config = {"zoom": 2.0, "suavidad": 0.5, "fps": 10}
    rec = FocusRecorder(config=config)
    
    def fake_reencode(path):
        assert os.path.exists(path)
        None

    monkeypatch.setattr(rec, "_reencode_h264", fake_reencode)

    blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    rec.raw_data = [
        (blank_frame.copy(), 320, 240, False, 0.0),
        (blank_frame.copy(), 320, 240, True, 1.0),
        (blank_frame.copy(), 100, 100, False, 2.0),
    ]
    
    writer_calls = []
    class FakeVideoWriter:
        def __init__(self, filename, fourcc, fps, frameSize):
            self.filename = filename
            writer_calls.append(("init", filename, fps, frameSize))
        def write(self, frame):
            writer_calls.append(("write", id(self)))
        def release(self):
            writer_calls.append(("release", id(self)))
            with open(self.filename, 'w') as f:
                f.write("mockvideo")

    monkeypatch.setattr(cv2, "VideoWriter", FakeVideoWriter)
    monkeypatch.setattr(cv2, "VideoWriter_fourcc", lambda *args: "mp4v")

    emitted_progress = []
    
    rec._render_adaptive_video(callback_progress=emitted_progress.append, export_mode="both")
    
    assert len(writer_calls) > 0
    assert len(emitted_progress) > 0
    assert emitted_progress[-1] == 100


def test_recorder_full_various_modes(monkeypatch, tmp_path):
    monkeypatch.setattr(recorder_module.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(recorder_module.pyautogui, "size", lambda: (640, 480))
    rec = FocusRecorder(config={"zoom": 2.0, "suavidad": 0.5, "fps": 10})
    
    def fake_reencode(path):
        pass # dont simulate true ffmpeg encode here
    monkeypatch.setattr(rec, "_reencode_h264", fake_reencode)
    monkeypatch.setattr(cv2, "VideoWriter", MagicMock())
    monkeypatch.setattr(cv2, "VideoWriter_fourcc", lambda *args: "mp4v")    
    
    # 0 length raw data
    rec.raw_data = []
    rec._render_adaptive_video(None, "both")
    
    blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    rec.raw_data = [
        (blank_frame.copy(), 320, 240, False, 0.0),
        (blank_frame.copy(), 320, 240, True, 1.0)
    ]
    
    # mode full only
    rec._render_adaptive_video(None, "full")
    # mode tiktok only
    rec._render_adaptive_video(None, "tiktok")

def test_recorder_reencode_fails_gracefully(monkeypatch, tmp_path):
    monkeypatch.setattr(recorder_module.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(recorder_module.pyautogui, "size", lambda: (640, 480))
    rec = FocusRecorder(config={"zoom": 2.0, "suavidad": 0.5, "fps": 10})
    
    def mock_run(*args, **kwargs):
        pass
    monkeypatch.setattr(recorder_module.subprocess, "run", mock_run)
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    monkeypatch.setattr(os.path, "getsize", lambda path: 100)
    
    # simulate fallback if tmp_path is missing but size > 0
    rec._reencode_h264("fake_path.mp4")
    
    monkeypatch.setattr(os.path, "getsize", lambda path: 0)
    rec._reencode_h264("fake_path2.mp4")

def test_recorder_os_logic(monkeypatch, tmp_path):
    import sys
    monkeypatch.setattr(recorder_module.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(recorder_module.pyautogui, "size", lambda: (640, 480))
    
    # Test IS_WINDOWS branch
    monkeypatch.setattr(recorder_module, "IS_WINDOWS", False)
    rec = FocusRecorder(config={"zoom": 2.0, "suavidad": 0.5, "fps": 10})
    assert rec.sct is None
from unittest.mock import MagicMock

def test_recorder_stop_no_listener(monkeypatch, tmp_path):
    monkeypatch.setattr(recorder_module.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(recorder_module.pyautogui, "size", lambda: (640, 480))
    rec = FocusRecorder(config={"zoom": 2.0, "suavidad": 0.5, "fps": 10})
    rec.is_recording = True
    rec.thread = MagicMock()
    rec._render_adaptive_video = MagicMock()
    # Call stop before start so it has no listener
    rec.stop(None, "full")
    rec._render_adaptive_video.assert_called_once()

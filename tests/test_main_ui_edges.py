import sys
from unittest.mock import patch, MagicMock

import PyQt6.QtWidgets as QtWidgets
import focusrecorder.main as main_module


def test_main_run_function(monkeypatch):
    calls = []

    class DummyQApplication:
        def __init__(self, argv):
            calls.append("QApplication")
            self.argv = argv
        def exec(self):
            calls.append("exec")
            return 0

    class DummyFocusApp:
        def __init__(self):
            calls.append("FocusApp")
        def show(self):
            calls.append("show")

    monkeypatch.setattr(main_module, "QApplication", DummyQApplication)
    monkeypatch.setattr(main_module, "FocusApp", DummyFocusApp)
    monkeypatch.setattr(sys, "exit", lambda code: calls.append("exit"))

    main_module.run()

    assert calls == ["QApplication", "FocusApp", "show", "exec", "exit"]


def test_main_toggle_stops_recording_and_renders(monkeypatch, qtbot):
    app = main_module.FocusApp()
    qtbot.addWidget(app)

    app.recorder = MagicMock()
    app.recorder.is_recording = True
    
    app.radio_tiktok.setChecked(True)

    with patch.object(main_module, "RenderThread") as mock_thread_class:
        mock_thread_instance = MagicMock()
        mock_thread_class.return_value = mock_thread_instance
        
        app.toggle()

        assert not app.btn.isEnabled()
        mock_thread_class.assert_called_once_with(app.recorder, export_mode="tiktok")
        mock_thread_instance.start.assert_called_once()
        assert "TikTok" in app.status.text()
    
    app.on_finished("", "")
    assert "GRAB" in app.btn.text().upper()

def test_main_toggle_starts_recording(monkeypatch, qtbot):
    app = main_module.FocusApp()
    qtbot.addWidget(app)
    
    app.recorder = None
    
    with patch.object(main_module, "FocusRecorder") as mock_recorder_class:
        mock_recorder_instance = MagicMock()
        mock_recorder_instance.filename = "test_video.mp4"
        mock_recorder_instance.is_recording = False
        mock_recorder_class.return_value = mock_recorder_instance
        
        app.toggle()
        
        mock_recorder_instance.start.assert_called_once()
        assert "DETENER" in app.btn.text()

def test_main_render_thread():
    with patch('focusrecorder.main.QThread'):
        mock_recorder = MagicMock()
        mock_recorder.filename = "test.mp4"
        
        # Modo full
        thread = main_module.RenderThread(mock_recorder, "full")
        thread.progress = MagicMock()
        thread.finished = MagicMock()
        
        thread.run()
        mock_recorder.stop.assert_called_once()
        thread.finished.emit.assert_called_with("test.mp4", "")

def test_main_on_finished_with_paths(qtbot):
    app = main_module.FocusApp()
    qtbot.addWidget(app)
    
    app.on_finished("/path/to/full_video.mp4", "/path/to/tiktok_video.mp4")
    
    assert "full_video.mp4" in app.status.text()
    assert "tiktok_video.mp4" in app.status.text()

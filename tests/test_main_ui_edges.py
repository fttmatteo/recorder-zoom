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

    monkeypatch.setattr(QtWidgets, "QApplication", DummyQApplication)
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
    assert "Grabación" in app.btn.text()

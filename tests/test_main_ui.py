import focusrecorder.main as main_module
from focusrecorder.main import FocusApp


def test_get_export_mode_mapping(qtbot):
    app = FocusApp()
    qtbot.addWidget(app)

    app.radio_full.setChecked(True)
    assert app._get_export_mode() == "full"

    app.radio_tiktok.setChecked(True)
    assert app._get_export_mode() == "tiktok"

    app.radio_both.setChecked(True)
    assert app._get_export_mode() == "both"


class DummyRecorder:
    def __init__(self, config):
        self.config = config
        self.is_recording = False
        self.filename = "C:/tmp/video_7.mp4"
        self.started = False

    def start(self):
        self.is_recording = True
        self.started = True



def test_toggle_start_updates_ui_and_config(monkeypatch, qtbot):
    monkeypatch.setattr(main_module, "FocusRecorder", DummyRecorder)

    app = FocusApp()
    qtbot.addWidget(app)

    app.zoom_spin.setValue(20)
    app.smooth_slider.setValue(5)
    app.fps_spin.setValue(30)

    app.toggle()

    assert isinstance(app.recorder, DummyRecorder)
    assert app.recorder.started
    assert app.recorder.config == {"zoom": 2.0, "suavidad": 0.05, "fps": 30}
    assert app.btn.text() == "DETENER Y PROCESAR"
    assert "Grabando" in app.status.text()
    assert not app.zoom_spin.isEnabled()
    assert not app.smooth_slider.isEnabled()
    assert not app.fps_spin.isEnabled()


def test_on_finished_shows_filenames_and_resets_controls(qtbot):
    app = FocusApp()
    qtbot.addWidget(app)

    app.progress_bar.setVisible(True)
    app._set_controls_enabled(False)

    app.on_finished("C:/tmp/video_1.mp4", "C:/tmp/video_1_tiktok.mp4")

    status_text = app.status.text()
    assert "video_1.mp4" in status_text
    assert "video_1_tiktok.mp4" in status_text
    assert app.btn.text() == "INICIAR GRABACIÓN"
    assert not app.progress_bar.isVisible()
    assert app.zoom_spin.isEnabled()
    assert app.smooth_slider.isEnabled()
    assert app.fps_spin.isEnabled()

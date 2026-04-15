from pathlib import Path

import focusrecorder.recorder as recorder_module
from focusrecorder.recorder import FocusRecorder


def make_recorder(monkeypatch, tmp_path):
    monkeypatch.setattr(recorder_module.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(recorder_module.pyautogui, "size", lambda: (1920, 1080))
    return FocusRecorder(config={"zoom": 1.8, "suavidad": 0.05, "fps": 30})


def test_get_video_directory_uses_user_home(monkeypatch, tmp_path):
    rec = make_recorder(monkeypatch, tmp_path)
    assert rec.output_dir == str(tmp_path / "video-focussee")


def test_get_next_filename_increments_index(monkeypatch, tmp_path):
    video_dir = tmp_path / "video-focussee"
    video_dir.mkdir(parents=True, exist_ok=True)
    (video_dir / "video_1.mp4").write_bytes(b"dummy")

    rec = make_recorder(monkeypatch, tmp_path)
    assert Path(rec.filename).name == "video_2.mp4"


def test_reencode_h264_replaces_input_file(monkeypatch, tmp_path):
    rec = make_recorder(monkeypatch, tmp_path)

    source = tmp_path / "sample.mp4"
    source.write_bytes(b"old")
    encoded = tmp_path / "sample_h264.mp4"

    calls = []

    def fake_run(cmd, stdout=None, stderr=None):
        calls.append(cmd)
        encoded.write_bytes(b"new")
        return 0

    monkeypatch.setattr(recorder_module.imageio_ffmpeg, "get_ffmpeg_exe", lambda: "ffmpeg-bin")
    monkeypatch.setattr(recorder_module.subprocess, "run", fake_run)

    rec._reencode_h264(str(source))

    assert calls, "Se esperaba invocación de ffmpeg"
    assert calls[0][0] == "ffmpeg-bin"
    assert source.exists()
    assert source.read_bytes() == b"new"
    assert not encoded.exists()


def test_render_adaptive_video_no_data_returns_without_progress(monkeypatch, tmp_path):
    rec = make_recorder(monkeypatch, tmp_path)
    rec.raw_data = []

    progress = []
    rec._render_adaptive_video(callback_progress=progress.append, export_mode="full")

    assert progress == []

from focusrecorder.main import RenderThread


class DummyRecorder:
    def __init__(self, filename="C:/tmp/video_10.mp4"):
        self.filename = filename
        self.calls = []

    def stop(self, callback_progress=None, export_mode="full"):
        self.calls.append(export_mode)
        if callback_progress:
            callback_progress(50)


def test_render_thread_full_mode_emits_paths(qtbot):
    recorder = DummyRecorder()
    thread = RenderThread(recorder, "full")

    finished_payload = []
    thread.finished.connect(lambda full, tiktok: finished_payload.append((full, tiktok)))

    thread.run()

    assert recorder.calls == ["full"]
    assert finished_payload == [("C:/tmp/video_10.mp4", "")]


def test_render_thread_both_mode_emits_both_paths(qtbot):
    recorder = DummyRecorder("C:/tmp/video_12.mp4")
    thread = RenderThread(recorder, "both")

    finished_payload = []
    thread.finished.connect(lambda full, tiktok: finished_payload.append((full, tiktok)))

    thread.run()

    assert recorder.calls == ["both"]
    assert finished_payload == [("C:/tmp/video_12.mp4", "C:/tmp/video_12_tiktok.mp4")]

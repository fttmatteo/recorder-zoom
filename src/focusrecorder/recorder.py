import threading
import time
import os
from pathlib import Path
from .config.config import coerce_recording_settings
from .app.factories.capture_backend_factory import create_capture_backend
from .app.factories.mouse_provider_factory import create_mouse_provider
from .app.factories.renderer_factory import create_renderer
from .application.errors import RecordingEnvironmentError
from .domain.ports.capture_backend import CaptureBackend
from .domain.ports.mouse_provider import MouseProvider
from .domain.models.recording_session import FrameSample, RecordingSessionState
from .config.settings import RecordingSettings
from .infrastructure.filesystem.file_naming import get_next_filename

# Importación condicional según el sistema operativo
import platform
IS_WINDOWS = platform.system() == "Windows"



class FocusRecorder:
    def __init__(self, config=None):
        self.is_windows = IS_WINDOWS
        self.settings = coerce_recording_settings(config)
        self.capture_backend = self._build_capture_backend()
        self.mouse_provider = self._build_mouse_provider()
        self.renderer = self._build_renderer()
        self.session = RecordingSessionState()
        self.sw, self.sh = self._get_screen_size()

        # Determinar la carpeta de salida según el sistema operativo
        self.output_dir = self._get_video_directory()
        
        os.makedirs(self.output_dir, exist_ok=True)
        self.filename = get_next_filename(self.output_dir, prefix="video")

    def _get_video_directory(self):
        """
        Obtiene la carpeta de videos apropiada según la plataforma.
        Guarda en una carpeta compartida del workspace para que los archivos sean
        accesibles también desde Windows cuando se trabaja sobre /d.
        """
        return str(self.settings.output_dir)

    def _on_click(self, x, y, button, pressed):
        self.session.set_clicking(pressed)

    def _build_capture_backend(self) -> CaptureBackend:
        return create_capture_backend(is_windows=self.is_windows)

    def _build_mouse_provider(self) -> MouseProvider:
        return create_mouse_provider()

    def _build_renderer(self):
        return create_renderer()

    def _get_screen_size(self):
        return self.capture_backend.get_screen_size()

    def _get_mouse_position(self):
        return self.mouse_provider.get_position()

    def _validate_capture_backend(self):
        try:
            self.capture_backend.validate()
        except Exception as exc:
            backend_name = type(self.capture_backend).__name__
            message = (
                f"No se pudo iniciar la captura de pantalla con {backend_name}. "
                "El entorno actual no parece ser compatible con el backend de captura seleccionado."
            )
            raise RecordingEnvironmentError(message) from exc

    def start(self):
        self._validate_capture_backend()
        self.session.reset(time.perf_counter())
        self.mouse_provider.start_listener(self._on_click)
        self.thread = threading.Thread(target=self._record_loop)
        self.thread.start()

    def stop(self, callback_progress=None, export_mode="full"):
        self.session.stop()
        self.mouse_provider.stop_listener()
        self.thread.join()
        self._render_adaptive_video(callback_progress, export_mode)

    def _record_loop(self):
        self.capture_backend.start()
        try:
            while self.session.is_recording:
                frame = self.capture_backend.capture_frame()
                if frame is None:
                    continue

                mx, my = self._get_mouse_position()
                ts = time.perf_counter() - self.session.start_time
                self.session.append_sample(
                    FrameSample(
                        frame=frame.copy(),
                        mouse_x=mx,
                        mouse_y=my,
                        is_clicking=self.session.is_clicking,
                        timestamp=ts,
                    )
                )

                if self.is_windows:
                    time.sleep(0.001)
                else:
                    time.sleep(0.01)
        finally:
            self.capture_backend.stop()

    def _render_adaptive_video(self, callback_progress, export_mode):
        self.renderer.render(
            raw_data=self.session.raw_data,
            settings=self.settings,
            screen_size=(self.sw, self.sh),
            output_filename=self.filename,
            callback_progress=callback_progress,
            export_mode=export_mode,
        )

    @property
    def is_recording(self):
        return self.session.is_recording

    @is_recording.setter
    def is_recording(self, value):
        self.session.is_recording = value

    @property
    def is_clicking(self):
        return self.session.is_clicking

    @is_clicking.setter
    def is_clicking(self, value):
        self.session.is_clicking = value

    @property
    def start_time(self):
        return self.session.start_time

    @start_time.setter
    def start_time(self, value):
        self.session.start_time = value

    @property
    def raw_data(self):
        return self.session.raw_data

    @raw_data.setter
    def raw_data(self, value):
        self.session.raw_data = value

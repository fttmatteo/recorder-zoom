import platform
from pathlib import Path

from ...config.constants import DEFAULT_OUTPUT_FOLDER_NAME


def get_config_directory() -> Path:
    system = platform.system()

    if system == "Windows":
        base = Path.home() / "AppData" / "Roaming"
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"

    config_dir = base / "FocusRecorder"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_default_output_dir() -> Path:
    return Path.home() / "Desktop" / DEFAULT_OUTPUT_FOLDER_NAME

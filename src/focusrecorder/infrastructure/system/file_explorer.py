import os
import platform
import subprocess
from pathlib import Path


def open_folder_in_explorer(folder_path: Path | str) -> None:
    folder_path = Path(folder_path)

    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)

    folder_str = str(folder_path.resolve())
    system = platform.system()

    try:
        if system == "Windows":
            os.startfile(folder_str)  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.Popen(["open", folder_str])
        else:
            subprocess.Popen(["xdg-open", folder_str])
    except Exception as exc:
        print(f"No se pudo abrir la carpeta: {exc}")


def open_file_location(file_path: Path | str) -> None:
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"El archivo no existe: {file_path}")
        return

    system = platform.system()
    file_str = str(file_path.resolve())

    try:
        if system == "Windows":
            subprocess.Popen(["explorer", "/select,", file_str])
        elif system == "Darwin":
            subprocess.Popen(["open", "-R", file_str])
        else:
            open_folder_in_explorer(file_path.parent)
    except Exception as exc:
        print(f"No se pudo abrir la ubicación del archivo: {exc}")
        open_folder_in_explorer(file_path.parent)

"""Utilidades para manejo de archivos y carpetas."""
import os
import platform
import subprocess
from pathlib import Path


def open_folder_in_explorer(folder_path: Path | str) -> None:
    """
    Abre la carpeta en el explorador de archivos del sistema operativo.
    
    Multiplataforma: funciona en Windows, macOS y Linux.
    
    Args:
        folder_path: Ruta de la carpeta a abrir
    """
    folder_path = Path(folder_path)
    
    # Asegurar que la carpeta existe
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)
    
    # Convertir a string absoluto
    folder_str = str(folder_path.resolve())
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows: usar explorer
            os.startfile(folder_str)  # type: ignore[attr-defined]  # Solo existe en Windows
        elif system == "Darwin":
            # macOS: usar open
            subprocess.Popen(["open", folder_str])
        else:
            # Linux: usar xdg-open
            subprocess.Popen(["xdg-open", folder_str])
    except Exception as e:
        print(f"No se pudo abrir la carpeta: {e}")


def open_file_location(file_path: Path | str) -> None:
    """
    Abre la carpeta que contiene el archivo y lo selecciona si es posible.
    
    Args:
        file_path: Ruta del archivo
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"El archivo no existe: {file_path}")
        return
    
    system = platform.system()
    file_str = str(file_path.resolve())
    
    try:
        if system == "Windows":
            # Windows: usar explorer con /select para seleccionar el archivo
            subprocess.Popen(["explorer", "/select,", file_str])
        elif system == "Darwin":
            # macOS: usar open -R para revelar el archivo
            subprocess.Popen(["open", "-R", file_str])
        else:
            # Linux: abrir la carpeta padre (no hay estándar para seleccionar)
            open_folder_in_explorer(file_path.parent)
    except Exception as e:
        print(f"No se pudo abrir la ubicación del archivo: {e}")
        # Fallback: abrir la carpeta padre
        open_folder_in_explorer(file_path.parent)

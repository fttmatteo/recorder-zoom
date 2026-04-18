"""Compat wrappers around filesystem/system modules."""

from ..infrastructure.filesystem.file_naming import get_next_filename
from ..infrastructure.system.file_explorer import (
    open_file_location,
    open_folder_in_explorer,
)

import runpy
import sys
from unittest.mock import patch
import pytest

import focusrecorder
import focusrecorder.main

def test_script_execution():
    with patch.object(focusrecorder.main, "run") as mock_run:
        with patch.object(sys, "argv", ["__main__.py"]):
            runpy.run_module("focusrecorder.__main__", run_name="__main__")
            mock_run.assert_called_once()

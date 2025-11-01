import importlib


def test_import_main_window_module():
    # Smoke test: importing the GUI module should not raise ImportError
    importlib.import_module('opk.ui.main_window')


import sys

import app


def test_app_package_is_importable():
    assert app.__name__ == "app"


def test_runs_on_python_311():
    assert sys.version_info[:2] == (3, 11)

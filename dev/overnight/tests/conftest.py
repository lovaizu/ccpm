"""What overnight's cases share: the folder of overnight's code on the import path, as its command
puts `scripts/` there, and this folder, where the double of claude lies, as the type checker finds
each there; the system's temporary folder and the home of each case, empty; and the double of claude
first on the PATH."""

from __future__ import annotations

import os
import sys
import tempfile
from collections.abc import Iterator
from typing import Any

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PLUGIN = os.path.join(TOP, "plugins", "overnight")
SCRIPTS = os.path.join(PLUGIN, "scripts")
for folder in (SCRIPTS, HERE):
    if folder not in sys.path:
        sys.path.insert(0, folder)

from claude import claude_double


@pytest.fixture(autouse=True)
def temp(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """The system's temporary folder of the case, empty."""
    folder = os.path.join(str(tmp_path), "system-temp")
    os.makedirs(folder)
    monkeypatch.setattr(tempfile, "tempdir", folder)
    yield folder


@pytest.fixture(autouse=True)
def home(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """The home of the case, empty, which `~` names."""
    folder = os.path.join(str(tmp_path), "home")
    os.makedirs(folder)
    monkeypatch.setenv("HOME", folder)
    return folder


@pytest.fixture
def double(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> claude_double.Double:
    """The double of claude, first on the PATH, which answers nothing until a case gives it
    answers."""
    double = claude_double.Double(os.path.join(str(tmp_path), "claude"))
    monkeypatch.setenv("PATH", double.path + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv(claude_double.FOLDER, double.folder)
    return double


@pytest.fixture
def work_dir(tmp_path: Any) -> str:
    """The folder that the case's work runs in, empty."""
    folder = os.path.join(str(tmp_path), "shop")
    os.makedirs(folder)
    return folder

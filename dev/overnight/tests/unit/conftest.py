"""What overnight's unit cases share: the folder of overnight's code on the import path, as resume's
`__main__.py` puts `scripts/` there, and this folder, where the double of Claude Code lies, as the
type checker finds each there; and the folders and the double of claude that each case sets up."""

from __future__ import annotations

import os
import sys
from typing import Any

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
SCRIPTS = os.path.join(TOP, "plugins", "overnight", "scripts")
for folder in (SCRIPTS, HERE):
    if folder not in sys.path:
        sys.path.insert(0, folder)

# The double lies in HERE, which the loop above puts on the import path.
import claude_double


@pytest.fixture
def project(tmp_path: Any) -> str:
    """The folder that the session ran in."""
    folder = os.path.join(str(tmp_path), "project")
    os.makedirs(folder)
    return folder


@pytest.fixture
def claude(tmp_path: Any) -> str:
    """The path of the double of claude."""
    return claude_double.install(os.path.join(str(tmp_path), "bin"))


@pytest.fixture
def sessions(tmp_path: Any) -> str:
    """The folder of the session's transcript."""
    return os.path.join(str(tmp_path), "projects")

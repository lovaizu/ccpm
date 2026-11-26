"""What rn's unit cases share: the system's temporary folder of each case, empty."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def temp(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """The system's temporary folder of the case, empty."""
    folder = os.path.join(str(tmp_path), "system-temp")
    os.makedirs(folder)
    monkeypatch.setattr(tempfile, "tempdir", folder)
    yield folder

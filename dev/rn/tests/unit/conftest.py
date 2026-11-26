"""What rn's unit cases share: the system's temporary folder of each case, empty; a host that runs
git for real and gh from its records, with its state in the case's own folder."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from typing import Any

import pytest
from gh import gh_double


@pytest.fixture(autouse=True)
def temp(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """The system's temporary folder of the case, empty, in a session that herdr doesn't run, as
    rn's developers may run the cases in herdr."""
    folder = os.path.join(str(tmp_path), "system-temp")
    os.makedirs(folder)
    monkeypatch.setattr(tempfile, "tempdir", folder)
    monkeypatch.delenv("HERDR_ENV", raising=False)
    yield folder


@pytest.fixture
def gh_state(tmp_path: Any) -> str:
    """The folder of the double of gh's state."""
    return os.path.join(str(tmp_path), "gh")


@pytest.fixture
def host(gh_state: str) -> Any:
    """A host that runs git for real and gh from its records, keeping each command it ran in its
    `ran`."""
    return gh_double.host(gh_state)

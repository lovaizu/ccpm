"""What overnight's unit cases share: the bench of the user's folders, with the walkthrough's
prompts, folders of work, and queue file written, on which most interfaces are tried."""

from __future__ import annotations

from typing import Any

import pytest
from overnight_bench import Bench, bench, walkthrough


@pytest.fixture
def b(tmp_path: Any, monkeypatch: Any) -> Bench:
    """The bench, with the walkthrough's queue file and what it names written."""
    the = bench(str(tmp_path), monkeypatch)
    walkthrough(the)
    return the

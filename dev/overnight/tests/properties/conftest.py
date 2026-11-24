"""What overnight's property-based tests share: no deadline, as a property that runs the stand-in of
Claude Code or writes records takes longer on a busy machine; the stand-in first on the PATH, and
each runner whose run it made ended once the case ends; and the clock in place of the runner's, as
`overnight_stand_ins` says. Each property sets the clock and the stand-in's plays anew for each
input, so that what one input leaves never reaches the next."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import overnight_stand_ins
import pytest
from hypothesis import settings
from overnight_stand_ins import Clock

settings.register_profile("overnight", deadline=None)
settings.load_profile("overnight")


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    """The runner's clock, which moves only as it waits."""
    return overnight_stand_ins.clock_in_place(monkeypatch)


@pytest.fixture
def stand_in(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """The folder of the state of the stand-in of Claude Code, which comes first on the PATH."""
    state = overnight_stand_ins.stand_in_first(str(tmp_path), monkeypatch)
    yield state
    overnight_stand_ins.end_runners(state)

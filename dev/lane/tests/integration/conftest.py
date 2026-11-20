"""What Lane's integration cases share: a bench for each case; Lane's modules kept out of the case's
process, so that each hook that the double runs imports the bench's copy, as a new process of Python
would; and a guard that ends in a traceback failing the case where it ends.

guard.answer refuses nothing, as its contract says, so a traceback of the guard is a fault of Lane
on any event. Claude Code reads a hook that fails with no onFailure as no answer at all, which the
double gives as an answer that stops nothing, so a case that checks that a move goes through would
pass on a guard that never ran. The case fails at the traceback in its place."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import lane_bench
import pytest


@pytest.fixture(autouse=True)
def guard_of_the_bench() -> Iterator[None]:
    """Has each hook that the double runs import the bench's copy of Lane, and each run of Lane's
    guard that ends in a traceback fail the case with it, as lane_bench.guard_of_the_bench says."""
    with lane_bench.guard_of_the_bench():
        yield


@pytest.fixture
def b(tmp_path: Any) -> lane_bench.Bench:
    """The bench: Lane, `log`, and its repository."""
    return lane_bench.bench(str(tmp_path))

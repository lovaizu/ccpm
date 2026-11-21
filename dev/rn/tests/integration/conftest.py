"""What rn's integration cases share: a bench for each case, and rn's modules kept out of the case's
process, so that each script that the double of Claude Code runs imports the bench's copy, as a new
process of Python would."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
import rn_bench


@pytest.fixture(autouse=True)
def rn_of_the_bench() -> Iterator[None]:
    """Has each script that the double runs import the bench's copy of rn."""
    with rn_bench.rn_of_the_bench():
        yield


@pytest.fixture
def b(tmp_path: Any) -> rn_bench.Bench:
    """The bench: rn, Lane, and invoicer's repository with its remote."""
    return rn_bench.bench(str(tmp_path))

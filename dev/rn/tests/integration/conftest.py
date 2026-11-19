"""What rn's integration cases share: a bench for each case, and rn's modules kept out of the case's
process, so that each script that the double runs imports the bench's copy, as a new process of
Python would."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import fresh_imports
import pytest
import rn_bench

# rn's own modules, by name, as plugins/rn/domain/ holds them.
RN_MODULES = ("fault", "schemas", "tree", "check", "template")


@pytest.fixture(autouse=True)
def fresh_modules() -> Iterator[None]:
    """Takes each of rn's modules out of the process for the case, and puts back those it held
    before."""
    with fresh_imports.without(RN_MODULES):
        yield


@pytest.fixture
def b(tmp_path: Any) -> rn_bench.Bench:
    """The bench of the walkthrough, with the plan signed off."""
    return rn_bench.bench(str(tmp_path))

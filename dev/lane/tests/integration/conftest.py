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

import claude_code
import fresh_imports
import lane_bench
import pytest

# Lane's own modules, by name, as plugins/lane/hooks/lane/ holds them.
LANE_MODULES = (
    "guard",
    "place",
    "record",
    "report",
    "rules",
    "plugin",
    "adapters",
    "routes",
    "lanes",
)


class GuardFailed(Exception):
    """Lane's guard ended in a traceback, given whole."""


@pytest.fixture(autouse=True)
def fresh_modules() -> Iterator[None]:
    """Takes each of Lane's modules out of the process for the case, and puts back those it held
    before."""
    with fresh_imports.without(LANE_MODULES):
        yield


@pytest.fixture(autouse=True)
def guard_never_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """Has each run of Lane's guard that ends in a traceback fail the case with it."""
    run_python = claude_code.run_python

    def checked(script: str, args: list[str], stdin: str, env: dict[str, str], cwd: str) -> Any:
        code, out, err = run_python(script, args, stdin, env, cwd)
        if script.endswith("/hooks/lane/guard.py") and "Traceback" in err:
            raise GuardFailed(err)
        return code, out, err

    monkeypatch.setattr(claude_code, "run_python", checked)


@pytest.fixture
def b(tmp_path: Any) -> lane_bench.Bench:
    """The bench: Lane, `log`, and its repository."""
    return lane_bench.bench(str(tmp_path))

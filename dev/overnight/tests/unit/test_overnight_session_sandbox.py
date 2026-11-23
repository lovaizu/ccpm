"""The unit cases of session/sandbox.py, whether Claude Code's sandbox can hold a task's commands:
`can_hold`, on macOS, on Windows, and on Linux, where WSL2 runs too, with bubblewrap and socat on
the PATH, and without either, as the documentation says the sandbox needs."""

from __future__ import annotations

import os
import platform
import sys
from typing import Any

import claude_double
import pytest
from session.sandbox import can_hold

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

RUNS = claude_double.line(claude_double.DOCUMENTATION, "the sandbox runs on macOS, Linux, and WSL2")
NEEDS = claude_double.line(
    claude_double.DOCUMENTATION, "the sandbox on Linux and WSL2 needs bubblewrap and socat"
)


def computer(tmp_path: Any, monkeypatch: Any, system: str, programs: list[str]) -> None:
    """Makes the computer the system's, `Darwin`, `Windows`, or `Linux`, with only the programs on
    its PATH."""
    monkeypatch.setattr(
        sys, "platform", {"Darwin": "darwin", "Windows": "win32"}.get(system, "linux")
    )
    monkeypatch.setattr(platform, "system", lambda: system)
    folder = os.path.join(str(tmp_path), "bin")
    os.makedirs(folder)
    for name in programs:
        path = os.path.join(folder, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\nexit 0\n")
        os.chmod(path, 0o755)
    monkeypatch.setenv("PATH", folder)


@pytest.mark.supports("test_a_writing_task_where_the_sandbox_cant_run_is_refused_at_stacking")
@pytest.mark.parametrize(
    ("system", "programs", "holds"),
    [
        ("Darwin", [], True),
        ("Windows", ["bwrap", "socat"], False),
        ("Linux", ["bwrap", "socat"], True),
        ("Linux", ["socat"], False),
        ("Linux", ["bwrap"], False),
    ],
    ids=["macOS", "Windows", "Linux", "Linux without bubblewrap", "Linux without socat"],
)
def test_the_sandbox_holds_where_claude_code_runs_it(
    tmp_path: Any, monkeypatch: Any, system: str, programs: list[str], holds: bool
):
    """Given macOS; Windows outside WSL2; or Linux, where WSL2 runs too, with bubblewrap and socat,
    without bubblewrap, or without socat
    When whether a writing task can be held to its dir is found
    Then it can on macOS and on Linux with both, and not otherwise"""
    assert "macOS, Linux, and WSL2" in RUNS["shows"] and "bubblewrap and socat" in NEEDS["shows"]
    computer(tmp_path, monkeypatch, system, programs)

    assert can_hold() is holds

"""The unit cases of session/claude.py, how overnight runs the program `claude`: `claude`, of a run
that answers, of one that ends with another exit code and what it said, and of no `claude` on the
PATH, each with a `claude` written for the case first on the PATH."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import pytest
from session.claude import claude

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def on_the_path(tmp_path: Any, monkeypatch: Any, code: int) -> str:
    """Writes a `claude` first on the PATH that prints its arguments and folder, says `said` on its
    standard error, and ends with the exit code, and gives the folder to run it in."""
    folder = os.path.join(str(tmp_path), "bin")
    os.makedirs(folder)
    path = os.path.join(folder, "claude")
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            f"#!{sys.executable}\n"
            "import json, os, sys\n"
            "print(json.dumps([sys.argv[1:], os.getcwd()]))\n"
            "sys.stderr.write('said\\n')\n"
            f"sys.exit({code})\n"
        )
    os.chmod(path, 0o755)
    monkeypatch.setenv("PATH", folder + os.pathsep + os.environ.get("PATH", ""))
    work = os.path.join(str(tmp_path), "work here")
    os.makedirs(work)
    return work


@pytest.mark.supports(
    "test_each_task_runs_in_its_own_folder_with_its_prompt",
    "test_the_tasks_go_on_after_the_stacking_session_ends",
)
@pytest.mark.parametrize("code", [0, 1, 3])
def test_a_run_of_claude_gives_its_exit_code_and_what_it_printed(
    tmp_path: Any, monkeypatch: Any, code: int
):
    """Given a `claude` on the PATH that ends with 0, 1, or 3
    When it runs with a prompt of quotes and a line break, in a folder whose name holds a space
    Then it gives that exit code, its standard output naming each argument as given and that
    folder, and its standard error"""
    work = on_the_path(tmp_path, monkeypatch, code)
    arguments = ["-p", 'say "done"\nthen stop', "--verbose"]

    given = claude(arguments, work)

    named, folder = json.loads(given.out)
    assert (given.code, named, os.path.realpath(folder), given.err) == (
        code,
        arguments,
        os.path.realpath(work),
        "said\n",
    )


@pytest.mark.supports("test_each_task_runs_in_its_own_folder_with_its_prompt")
def test_no_claude_on_the_path_is_refused(tmp_path: Any, monkeypatch: Any):
    """Given a PATH that holds no `claude`
    When it runs
    Then it refuses with FileNotFoundError"""
    monkeypatch.setenv("PATH", str(tmp_path))

    with pytest.raises(FileNotFoundError):
        claude(["-p", "x"], str(tmp_path))

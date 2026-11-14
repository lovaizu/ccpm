"""The unit cases of throwaway.py, where a deliverable's commands run, through `copy`, `run`, and
`main`, on a worktree of the test's own."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any

import pytest
from rn_example import HINTS, write
from rn_parts import NAME, RUN
from throwaway import USAGE, copy, main, run
from tree.rounds import Tried

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


@pytest.fixture
def worktree(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """A worktree holding invoicer/__init__.py, a change not yet committed, and the hints' round 1,
    with the system's temporary folder the test's own."""
    root = os.path.join(str(tmp_path), "worktree")
    write(root, "invoicer/__init__.py", '"""invoicer, typed."""\n')
    os.makedirs(os.path.join(root, RUN, "rounds", "invoicer--", "1"))
    monkeypatch.setattr(tempfile, "tempdir", os.path.join(str(tmp_path), "tmp"))
    os.makedirs(tempfile.tempdir or "")
    return root


@pytest.mark.supports("test_a_try_runs_the_command_in_a_copy_and_keeps_it_in_the_rounds_try_record")
def test_copy_holds_the_worktrees_files_as_they_stand_in_the_temporary_folder(worktree: str):
    """Given the worktree with a change not yet committed
    When a throwaway copy is made
    Then it lies under <temp>/rn/<run>/, holds the change, and its home beside it is empty"""
    where, home = copy(worktree, NAME)
    assert where.startswith(os.path.join(tempfile.gettempdir(), "rn", NAME, ""))
    with open(os.path.join(where, "invoicer", "__init__.py"), encoding="utf-8") as f:
        assert f.read() == '"""invoicer, typed."""\n'
    assert os.listdir(home) == []


@pytest.mark.supports("test_a_try_runs_the_command_in_a_copy_and_keeps_it_in_the_rounds_try_record")
def test_each_copy_is_fresh(worktree: str):
    """Given a copy in which a try wrote made-by-try
    When another copy is made
    Then it holds no made-by-try"""
    first, _ = copy(worktree, NAME)
    write(first, "made-by-try", "")
    second, _ = copy(worktree, NAME)
    assert second != first and not os.path.exists(os.path.join(second, "made-by-try"))


@pytest.mark.supports("test_a_try_changes_no_file_of_the_worktree_nor_of_the_users_home")
def test_run_runs_in_the_copy_with_its_home_and_gives_the_exit_code_and_output(worktree: str):
    """Given a copy and its home
    When `pwd && echo "$HOME" && exit 3` runs
    Then it gives 3, with the copy and the home printed"""
    where, home = copy(worktree, NAME)
    tried = run('pwd && echo "$HOME" && exit 3', where, home, os.environ)
    assert tried == Tried('pwd && echo "$HOME" && exit 3', 3, f"{where}\n{home}\n")


@pytest.mark.supports("test_a_try_changes_no_file_of_the_worktree_nor_of_the_users_home")
def test_run_leaves_the_rest_of_the_environment_as_it_is(worktree: str):
    """Given a copy, and RN_SEEN=1 in the environment
    When `echo "$RN_SEEN"` runs
    Then it prints 1"""
    where, home = copy(worktree, NAME)
    assert run('echo "$RN_SEEN"', where, home, dict(os.environ, RN_SEEN="1")).output == "1\n"


@pytest.mark.supports("test_a_try_runs_the_command_in_a_copy_and_keeps_it_in_the_rounds_try_record")
def test_main_runs_the_try_and_keeps_it_in_the_rounds_try_record(worktree: str):
    """Given the hints' round 1
    When `throwaway.py try <run> invoicer/ 1 'echo typed'` runs
    Then it gives 0 with `typed`, and the round's try.json holds the command"""
    code, out, _ = main(["try", RUN, HINTS, "1", "echo typed"], os.environ, worktree)
    with open(
        os.path.join(worktree, RUN, "rounds", "invoicer--", "1", "try.json"), encoding="utf-8"
    ) as f:
        kept = json.load(f)
    assert (code, out) == (0, "typed\n") and kept["tried"][-1]["command"] == "echo typed"


@pytest.mark.supports("test_a_try_runs_the_command_in_a_copy_and_keeps_it_in_the_rounds_try_record")
def test_main_gives_the_commands_own_exit_code(worktree: str):
    """Given the hints' round 1
    When a try of `exit 5` runs
    Then throwaway.py gives 5"""
    assert main(["try", RUN, HINTS, "1", "exit 5"], os.environ, worktree)[0] == 5


@pytest.mark.parametrize(
    ("deliverable", "number"), [("README.md", "1"), (HINTS, "2"), (HINTS, "one")]
)
@pytest.mark.supports("test_a_try_runs_the_command_in_a_copy_and_keeps_it_in_the_rounds_try_record")
def test_main_refuses_a_deliverable_or_round_the_run_hasnt(
    worktree: str, deliverable: str, number: str
):
    """Given the hints' round 1 alone
    When a try of README.md, of the hints' round 2, or of round `one` runs
    Then throwaway.py gives 1, and runs nothing"""
    code, out, _ = main(["try", RUN, deliverable, number, "touch ran"], os.environ, worktree)
    assert code == 1 and out == ""


@pytest.mark.parametrize("argv", [[], ["try", RUN, HINTS, "1"], ["run", RUN, HINTS, "1", "ls"]])
@pytest.mark.supports("test_a_try_runs_the_command_in_a_copy_and_keeps_it_in_the_rounds_try_record")
def test_main_of_no_try_of_four_gives_2_with_the_usage(worktree: str, argv: list[str]):
    """Given the worktree
    When throwaway.py runs with no argument, without the command, or with `run`
    Then it gives 2 with the usage"""
    assert main(argv, os.environ, worktree) == (2, "", USAGE + "\n")

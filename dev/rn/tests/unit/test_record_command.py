"""The unit cases of record/command.py, record.py's command line, through `main`: the exit code,
what it prints, and what it does for each command, on a run that tree.py began in a repository of
the test's own. The commands' own decisions lie in the modules each case of theirs names; these
cases try what the command line adds: its arguments, its output, and its exit codes."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from record.command import USAGE, main
from rn_example import RN, WORDS
from rn_parts import environ, repository
from tree.command import main as tree

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


class Run:
    """The walkthrough's run that tree.py began in a repository of the test's own, with its worktree
    and its folder from there."""

    def __init__(self, base: str):
        root, _ = repository(base)
        self.env = environ(base)
        code, out, err = tree(["begin", WORDS], self.env, root)
        assert code == 0, err
        self.worktree = out.strip()
        self.folder = os.path.join(".rn", os.path.basename(self.worktree).removeprefix("rn-"))

    def record(self, *argv: str) -> tuple[int, str, str]:
        """record.py with the arguments, in the run's worktree."""
        return main(list(argv), self.worktree, RN)


@pytest.fixture
def run(tmp_path: Any) -> Run:
    return Run(str(tmp_path))


@pytest.mark.parametrize("argv", [[], ["start"], ["add", "r", "generator", "1"], ["check"]])
@pytest.mark.supports("test_record_refuses_an_id_that_is_neither_a_step_nor_a_practice")
def test_arguments_of_no_command_give_2_with_the_usage(run: Run, argv: list[str]):
    """Given no argument, an unknown command, or a command short of its arguments
    When record.py runs
    Then it gives 2 with the usage"""
    assert run.record(*argv) == (2, "", USAGE)


@pytest.mark.supports("test_record_refuses_an_id_that_is_neither_a_step_nor_a_practice")
def test_add_gives_0_and_1_by_whether_the_entry_is_in_its_form(run: Run):
    """Given the walkthrough's run
    When `record.py add` adds step 1, and then `step-one`
    Then the first gives 0, and the second 1"""
    record = os.path.join(run.folder, "records", "tree-keeper-1.json")
    assert run.record("add", record, "tree-keeper", "1", "Read.")[0] == 0
    assert run.record("add", record, "tree-keeper", "step-one", "Read.")[0] == 1


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_check_gives_1_with_each_fault_and_2_where_it_cant_check(run: Run):
    """Given the walkthrough's run, the tree-keeper's cut, and its record holding no step
    When `record.py check tree-keeper done <cut>` runs, and then with a cut that isn't there
    Then the first gives 1 naming step 1, and the second 2"""
    printed = tree(["cut", run.folder, "tree-keeper"], run.env, run.worktree)[1]
    cut = json.loads(printed)["cut"]
    code, _, err = run.record("check", "tree-keeper", "done", cut)
    assert code == 1 and "step 1" in err
    assert run.record("check", "tree-keeper", "done", "nowhere.json")[0] == 2

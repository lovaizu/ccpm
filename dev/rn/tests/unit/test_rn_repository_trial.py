"""The unit cases of repository/trial.py: `folder`, its path under the system's temporary folder,
the same at each call and none made; and `starting_state`, a clone of the work's branch with the
worktree's files as they stand, a change, a new file, and a removal not committed among them,
without .rn/, made anew over what an earlier trial left, and the refusal of a folder that can't be
made."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import CantRun
from repo_files import git
from repository.place import RunPlace
from repository.trial import folder, starting_state
from rn_runs import NAME, changed, made_run
from rounds.files import Round


def a_round(run: RunPlace, deliverable: str, stage: str = "content", number: int = 1) -> Round:
    """The Round of the run's deliverable, by its folder in the run's Rounds."""
    run_folder = rn_files.folder_of(run.repository, run.name)
    at = rn_files.round_of(run_folder, deliverable, stage, number)
    return Round(at, deliverable, stage, number)


def same(path: str, expected: str) -> bool:
    """Whether the path names the expected folder, with or without its closing `/`."""
    return os.path.normpath(path) == os.path.normpath(expected)


def test_a_rounds_folder_lies_in_the_temporary_folder_by_run_and_round(temp: str):
    """Given the run 20261120-invoices, and the command's Round content-1
    When folder is asked twice
    Then each gives <temporary folder>/rn-trial-20261120-invoices-invoicer%2F__main__.py-content-1,
    and no folder is made"""
    run = RunPlace("/work/invoicer", NAME)
    given = folder(run, a_round(run, rn_files.COMMAND))
    expected = os.path.join(temp, f"rn-trial-{NAME}-invoicer%2F__main__.py-content-1")
    assert same(given, expected)
    assert folder(run, a_round(run, rn_files.COMMAND)) == given
    assert os.listdir(temp) == []


def files_under(top: str) -> set[str]:
    """Each file under the folder, by its path from it, leaving out git's own."""
    found = set()
    for at, folders, files in os.walk(top):
        folders[:] = [each for each in folders if each != ".git"]
        found |= {os.path.relpath(os.path.join(at, each), top) for each in files if each != ".git"}
    return found


def test_the_starting_state_holds_the_branch_as_its_people_get_it(tmp_path: Any, host: Any):
    """Given a run whose worktree holds a new command, a changed docs/product-vision.md, and
    lines.py removed, none committed, and its design tree and a Round under .rn/
    When starting_state is made for the command's Round content-1
    Then it gives the folder that `folder` names, a clone on the branch rn-<name> holding each file
    of the worktree as it stands, the command and the change to docs/product-vision.md in, lines.py
    out, and nothing of .rn/"""
    run = made_run(str(tmp_path))
    round_ = a_round(run, rn_files.COMMAND)
    os.makedirs(round_.folder)
    changed(run, {rn_files.COMMAND: "print('invoice')\n", "docs/product-vision.md": "# New\n"})
    worktree = rn_files.worktree_of(run.repository, run.name)
    os.remove(os.path.join(worktree, "invoicer", "lines.py"))
    given = starting_state(run, round_, host)
    assert given == folder(run, round_)
    expected = files_under(worktree) - {f for f in files_under(worktree) if f.startswith(".rn")}
    assert files_under(given) == expected
    assert "invoicer/lines.py" not in expected
    with open(os.path.join(given, "docs", "product-vision.md"), encoding="utf-8") as f:
        assert f.read() == "# New\n"
    with open(os.path.join(given, rn_files.COMMAND), encoding="utf-8") as f:
        assert f.read() == "print('invoice')\n"
    assert git(given, "branch", "--show-current").strip() == f"rn-{run.name}"


def test_the_starting_state_is_made_anew_over_what_an_earlier_trial_left(tmp_path: Any, host: Any):
    """Given a run, and the Round's folder of the people's starting state holding a file an
    earlier trial wrote
    When starting_state is made for the Round
    Then that file is gone, and the worktree's files are there"""
    run = made_run(str(tmp_path))
    round_ = a_round(run, rn_files.COMMAND)
    left = folder(run, round_)
    os.makedirs(left)
    with open(os.path.join(left, "lines.csv"), "w", encoding="utf-8") as f:
        f.write("Hosting;40.00;1\n")
    given = starting_state(run, round_, host)
    assert not os.path.exists(os.path.join(given, "lines.csv"))
    assert os.path.isfile(os.path.join(given, "invoicer", "lines.py"))


def test_a_folder_that_cant_be_made_cant_run(tmp_path: Any, host: Any, temp: str):
    """Given a run, and a system's temporary folder that may not be written
    When starting_state is made for a Round
    Then CantRun is raised"""
    run = made_run(str(tmp_path))
    os.chmod(temp, 0o555)
    try:
        with pytest.raises(CantRun):
            starting_state(run, a_round(run, rn_files.COMMAND), host)
    finally:
        os.chmod(temp, 0o755)

"""The unit cases of repository/trial.py: `folder`, its path under the system's temporary folder for
a first Round and a later one, its deliverable's path percent-encoded, the same at each call
and none made, and apart for each Round, each run, and two paths alike but for a slash; and
`starting_state`, a clone of the work's branch with the worktree's files as they stand, a change, a
new file, and a removal not committed among them, without .rn/, made anew over what an earlier
trial left, and the refusal of a folder that can't be made."""

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


@pytest.mark.supports("test_the_evaluators_try_writes_only_in_the_peoples_folder")
def test_a_rounds_folder_lies_in_the_temporary_folder_by_run_and_round(temp: str):
    """Given the run 20261120-invoices, and the command's Round content-1
    When folder is asked
    Then it's <temporary folder>/rn-trial-20261120-invoices-invoicer%2F__main__.py-content-1, and no
    folder is made"""
    run = RunPlace("/work/invoicer", NAME)
    given = folder(run, a_round(run, rn_files.COMMAND))
    expected = os.path.join(temp, f"rn-trial-{NAME}-invoicer%2F__main__.py-content-1")
    assert same(given, expected)
    assert os.listdir(temp) == []


@pytest.mark.supports("test_the_evaluators_try_writes_only_in_the_peoples_folder")
def test_a_later_rounds_folder_names_its_stage_and_number(temp: str):
    """Given the run 20261120-invoices, and the guide's Round content-2
    When folder is asked
    Then it's <temporary folder>/rn-trial-20261120-invoices-docs%2Fguide.md-content-2"""
    run = RunPlace("/work/invoicer", NAME)
    given = folder(run, a_round(run, rn_files.GUIDE, "content", 2))
    assert same(given, os.path.join(temp, f"rn-trial-{NAME}-docs%2Fguide.md-content-2"))


@pytest.mark.supports("test_the_evaluators_try_writes_only_in_the_peoples_folder")
def test_a_rounds_folder_is_the_same_at_each_call_and_apart_for_each_round_and_run(temp: str):
    """Given two runs, and two Rounds of one deliverable: content-1 and content-2
    When folder is asked twice of each Round of each run
    Then each call of the same run and Round gives the same folder, and no two others give the
    same one"""
    runs = [RunPlace("/work/invoicer", NAME), RunPlace("/work/invoicer", "20261121-invoices")]
    rounds = [("content", 1), ("content", 2)]
    given = {}
    for run in runs:
        for stage, number in rounds:
            first = folder(run, a_round(run, rn_files.COMMAND, stage, number))
            assert folder(run, a_round(run, rn_files.COMMAND, stage, number)) == first
            given[(run.name, stage, number)] = os.path.normpath(first)
    assert len(set(given.values())) == len(runs) * len(rounds)


@pytest.mark.supports("test_the_evaluators_try_writes_only_in_the_peoples_folder")
def test_two_paths_alike_but_for_a_slash_get_folders_apart(temp: str):
    """Given the run 20261120-invoices, and Round content-1 of docs/guide.md and of docs-guide.md
    When folder is asked of each
    Then they're <temporary folder>/rn-trial-20261120-invoices-docs%2Fguide.md-content-1 and
    .../rn-trial-20261120-invoices-docs-guide.md-content-1, two folders"""
    run = RunPlace("/work/invoicer", NAME)
    slashed = folder(run, a_round(run, "docs/guide.md"))
    dashed = folder(run, a_round(run, "docs-guide.md"))
    assert same(slashed, os.path.join(temp, f"rn-trial-{NAME}-docs%2Fguide.md-content-1"))
    assert same(dashed, os.path.join(temp, f"rn-trial-{NAME}-docs-guide.md-content-1"))


def files_under(top: str) -> set[str]:
    """Each file under the folder, by its path from it, leaving out git's own."""
    found = set()
    for at, folders, files in os.walk(top):
        folders[:] = [each for each in folders if each != ".git"]
        found |= {os.path.relpath(os.path.join(at, each), top) for each in files if each != ".git"}
    return found


@pytest.mark.supports("test_the_people_start_from_the_branch_without_rns_folder")
def test_the_starting_state_holds_the_branch_as_its_people_get_it(tmp_path: Any, host: Any):
    """Given a run whose worktree holds a new command, a changed README, and lines.py removed, none
    committed, and its design tree and a Round under .rn/
    When starting_state is made for the command's Round content-1
    Then it gives the folder that `folder` names, a clone on the branch rn-<name> holding each file
    of the worktree as it stands, the command and the README's change in, lines.py out, and nothing
    of .rn/"""
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


@pytest.mark.supports("test_the_people_start_from_the_branch_without_rns_folder")
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


@pytest.mark.supports("test_the_people_start_from_the_branch_without_rns_folder")
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

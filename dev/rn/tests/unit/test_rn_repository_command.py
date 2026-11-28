"""The unit cases of repository/command.py, repository's command line as the orchestrator and each
role run it: `new` printing the work's folder at the top of the worktree it runs in, `works`
printing each piece of work with something left to do there, `stop`, `trial` printing what its
module gives, a refusal given as its exit code, and arguments of another form."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import pytest
import rn_files
from repo_files import write_files
from repository.command import USAGE, main

SLUG = "invoice-from-statement"


@pytest.fixture
def repo(tmp_path: Any) -> str:
    """The user's repository, with origin holding its default branch."""
    made = rn_files.repository(str(tmp_path / "accounting"))
    rn_files.with_origin(made, str(tmp_path / "origin.git"))
    return made


def started(repo: str, host: Any) -> str:
    """Makes the work by `new` in a worktree beside the repository, from a folder inside it,
    commits its steering, writes the command, and gives its folder."""
    worktree = rn_files.worktree_of(
        repo, os.path.join(os.path.dirname(repo), "invoices"), "invoices"
    )
    inner = os.path.join(worktree, "docs")
    os.makedirs(inner)
    name = f"{date.today():%Y%m%d}-{SLUG}"
    folder = os.path.join(worktree, ".rn", name)
    assert main(["new", SLUG], inner, rn_files.RN, host) == (0, f"{folder}\n", "")
    rn_files.committed_steering(worktree, name, rn_files.steering())
    write_files(worktree, {rn_files.COMMAND: "print('invoice')\n"})
    return folder


def test_new_prints_the_folder_of_the_work_and_works_lists_it(repo: str, host: Any) -> None:
    """Given the user's repository and a worktree of it.
    When the work is made in the worktree by `new`, its steering committed, and `works` runs.
    Then `new` prints the folder, and `works` prints it again."""
    work_folder = started(repo, host)
    worktree = os.path.dirname(os.path.dirname(work_folder))
    assert main(["works"], worktree, rn_files.RN, host) == (0, f"{work_folder}\n", "")


def test_trial_prints_the_folder_its_module_makes(repo: str, host: Any, temp: str) -> None:
    """Given the work with its command written.
    When `trial` runs on it.
    Then it gives 0 with the trial's folder."""
    work_folder = started(repo, host)
    round_ = os.path.join(work_folder, "tasks", "001", "01-content")
    trial = main(["trial", work_folder, round_], repo, rn_files.RN, host)
    assert trial[0] == 0 and trial[1].startswith(os.path.join(temp, "rn-trial-"))


def test_a_refusal_gives_its_exit_code_with_what_is_wrong(repo: str, host: Any) -> None:
    """Given a repository.
    When `trial` is given a folder outside rn's work, and `new` runs outside git.
    Then each gives 1, saying what's wrong."""
    code, _, err = main(["trial", "docs", "docs"], repo, rn_files.RN, host)
    assert (code, err.startswith("repository: ")) == (1, True)
    code, _, err = main(["new", SLUG], "/", rn_files.RN, host)
    assert (code, "lies in no git worktree" in err) == (1, True)


@pytest.mark.parametrize("argv", [[], ["make"], ["new"], ["trial", "a"]])
def test_arguments_of_another_form_give_the_usage(argv: list[str], host: Any) -> None:
    """Given no subcommand, one that isn't repository's, or the wrong count of arguments.
    When repository runs.
    Then it gives 2 with the usage."""
    assert main(argv, "/", rn_files.RN, host) == (2, "", USAGE)

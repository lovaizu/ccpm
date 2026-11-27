"""The unit cases of repository/command.py, repository's command line as the orchestrator and each
role run it: `new` printing the work's folder in the worktree it's given, `works` printing each
piece of work with something left to do, `stop`, `cancel` printing what it removed on GitHub and
saying what it couldn't, `trial` printing what its module gives, a refusal given as its exit code,
and arguments of another form."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import pytest
import rn_files
from gh import gh_double
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
    """Makes the work by `new` in a worktree beside the repository, commits its steering, writes the
    command, and gives its folder."""
    worktree = rn_files.worktree_of(
        repo, os.path.join(os.path.dirname(repo), "invoices"), "invoices"
    )
    name = f"{date.today():%Y%m%d}-{SLUG}"
    folder = os.path.join(worktree, ".rn", name)
    assert main(["new", SLUG, "../invoices", "made"], repo, rn_files.RN, host) == (
        0,
        f"{folder}\n",
        "",
    )
    rn_files.committed_steering(worktree, name, rn_files.steering())
    write_files(worktree, {rn_files.COMMAND: "print('invoice')\n"})
    return folder


def test_new_prints_the_folder_of_the_work_and_works_lists_it(repo: str, host: Any) -> None:
    """Given the user's repository and a worktree of it.
    When the work is made in the worktree by `new`, its steering committed, and `works` runs.
    Then `new` prints the folder, and `works` prints it again."""
    work_folder = started(repo, host)
    assert main(["works"], repo, rn_files.RN, host) == (0, f"{work_folder}\n", "")


def test_each_subcommand_on_the_work_prints_what_its_module_gives(
    repo: str, host: Any, temp: str
) -> None:
    """Given the work with its command written.
    When `trial` and `stop` run on it.
    Then each gives 0: the trial's folder, and the hash pushed."""
    work_folder = started(repo, host)
    round_ = os.path.join(work_folder, "rounds", "1", "invoice", "content-1")
    trial = main(["trial", work_folder, round_], repo, rn_files.RN, host)
    assert trial[0] == 0 and trial[1].startswith(os.path.join(temp, "rn-trial-"))
    code, out, _ = main(["stop", work_folder], repo, rn_files.RN, host)
    assert (code, len(out.strip())) == (0, 40)


def test_a_refusal_gives_its_exit_code_with_what_is_wrong(repo: str, host: Any) -> None:
    """Given a repository.
    When `stop` is given a folder outside rn's work.
    Then it gives 1, saying what's wrong."""
    code, _, err = main(["stop", "docs"], repo, rn_files.RN, host)
    assert (code, err.startswith("repository: ")) == (1, True)
    code, _, err = main(["new", SLUG, "../invoices", "mine"], repo, rn_files.RN, host)
    assert (code, "give made or users" in err) == (1, True)


def test_cancel_prints_what_it_removed_and_says_what_it_couldnt(
    repo: str, host: Any, gh_state: str
) -> None:
    """Given the work pushed by `stop`, and gh unable to reach GitHub.
    When `cancel` runs on it.
    Then it gives 0, printing origin's branch deleted, and saying on stderr that it can't remove
    the pull request, and the work's worktree is gone."""
    work_folder = started(repo, host)
    main(["stop", work_folder], repo, rn_files.RN, host)
    gh_double.unreached(gh_state)
    code, out, err = main(["cancel", work_folder], repo, rn_files.RN, host)
    assert (code, out) == (0, "origin/invoices\n")
    assert err.startswith("repository: can't remove the pull request of invoices on GitHub")
    assert not os.path.exists(work_folder)


@pytest.mark.parametrize("argv", [[], ["make"], ["new", SLUG], ["stop", "a", "b"]])
def test_arguments_of_another_form_give_the_usage(argv: list[str], host: Any) -> None:
    """Given no subcommand, one that isn't repository's, or the wrong count of arguments.
    When repository runs.
    Then it gives 2 with the usage."""
    assert main(argv, "/", rn_files.RN, host) == (2, "", USAGE)

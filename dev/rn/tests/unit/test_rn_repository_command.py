"""The unit cases of repository/command.py, repository's command line as the orchestrator and each
role run it: `new` printing the run's folder, `runs` printing each run with work left and what it
couldn't check, `stop`, `cancel` printing what it removed on GitHub and saying
what it couldn't, `put-up`, `trial`, `diff`, and `ci` each printing what its module gives, a
refusal given as its exit code, and arguments of another form."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import pytest
import rn_files
from gh import gh_double
from repo_files import git, write_files
from repository.command import USAGE, main

SLUG = "invoice-from-statement"


@pytest.fixture
def repo(tmp_path: Any) -> str:
    """The user's repository, with origin holding its default branch."""
    made = rn_files.repository(str(tmp_path / "accounting"))
    rn_files.with_origin(made, str(tmp_path / "origin.git"))
    return made


def folder() -> str:
    """The run's folder from the repository's top, named by today and the slug."""
    name = f"{date.today():%Y%m%d}-{SLUG}"
    return f".claude/worktrees/rn-{name}/.rn/{name}"


def started(repo: str, host: Any) -> str:
    """Makes the run by `new`, commits its steering, writes the command, and gives its folder."""
    assert main(["new", SLUG], repo, rn_files.RN, host) == (0, f"{folder()}\n", "")
    worktree = os.path.join(repo, folder().split("/.rn/")[0])
    rn_files.committed_steering(worktree, folder().rsplit("/", 1)[1], rn_files.steering())
    write_files(worktree, {rn_files.COMMAND: "print('invoice')\n"})
    return folder()


def test_new_prints_the_runs_folder_and_runs_lists_it(repo: str, host: Any) -> None:
    """Given the user's repository.
    When a run is made by `new`, its steering committed, and `runs` runs.
    Then `new` prints the folder, and `runs` prints it again with nothing unchecked."""
    run_folder = started(repo, host)
    assert main(["runs"], repo, rn_files.RN, host) == (0, f"{run_folder}\n", "")


def test_runs_says_what_it_couldnt_check(repo: str, host: Any) -> None:
    """Given a repository whose origin is gone, and no run.
    When `runs` runs.
    Then it prints no run, and says on stderr what it couldn't check."""
    git(repo, "remote", "set-url", "origin", os.path.join(repo, "gone"))
    code, out, err = main(["runs"], repo, rn_files.RN, host)
    assert (code, out, err.startswith("repository: can't check the runs on GitHub")) == (
        0,
        "",
        True,
    )


def test_each_subcommand_on_a_run_prints_what_its_module_gives(
    repo: str, host: Any, temp: str
) -> None:
    """Given a run with its command written.
    When `put-up`, `trial`, `diff`, and `stop` run on it.
    Then each gives 0: the command's link, the trial's folder, the diff, and the hash pushed."""
    run_folder = started(repo, host)
    code, out, _ = main(["put-up", run_folder, rn_files.COMMAND], repo, rn_files.RN, host)
    assert (code, out.startswith("http://github.com/owner/repo/blob/")) == (0, True)
    round_ = f"{run_folder}/rounds/1/invoice/content-1"
    trial = main(["trial", run_folder, round_], repo, rn_files.RN, host)
    assert trial[0] == 0 and trial[1].startswith(os.path.join(temp, "rn-trial-"))
    assert f"+++ b/{rn_files.COMMAND}" in main(["diff", run_folder], repo, rn_files.RN, host)[1]
    code, out, _ = main(["stop", run_folder], repo, rn_files.RN, host)
    assert (code, len(out.strip())) == (0, 40)


def test_a_refusal_gives_its_exit_code_with_what_is_wrong(repo: str, host: Any) -> None:
    """Given a run with its command written.
    When `put-up` is given a path that no step names.
    Then it gives 1, saying what's wrong."""
    run_folder = started(repo, host)
    code, _, err = main(["put-up", run_folder, "docs/other.md"], repo, rn_files.RN, host)
    assert (code, err.startswith("repository: no step names the deliverable")) == (1, True)


def test_cancel_prints_what_it_removed_and_says_what_it_couldnt(
    repo: str, host: Any, gh_state: str
) -> None:
    """Given a run pushed by `stop`, and gh unable to reach GitHub.
    When `cancel` runs on it.
    Then it gives 0, printing origin's branch deleted, and saying on stderr that it can't remove
    the pull request, and the run's worktree is gone."""
    run_folder = started(repo, host)
    main(["stop", run_folder], repo, rn_files.RN, host)
    gh_double.unreached(gh_state)
    code, out, err = main(["cancel", run_folder], repo, rn_files.RN, host)
    branch = run_folder.split("/")[2]
    assert (code, out) == (0, f"origin/{branch}\n")
    assert err.startswith(f"repository: can't remove the pull request of {branch} on GitHub")
    assert not os.path.exists(os.path.join(repo, run_folder))


@pytest.mark.parametrize("argv", [[], ["make"], ["new"], ["stop", "a", "b"]])
def test_arguments_of_another_form_give_the_usage(argv: list[str], host: Any) -> None:
    """Given no subcommand, one that isn't repository's, or the wrong count of arguments.
    When repository runs.
    Then it gives 2 with the usage."""
    assert main(argv, "/", rn_files.RN, host) == (2, "", USAGE)

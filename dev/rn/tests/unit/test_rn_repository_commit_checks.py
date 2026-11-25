"""The unit cases of repository/commit_checks.py's `findings`: a repository that sets no check, a
check that passes, one that fails with one line and with several, one set by core.hooksPath, the
files given alone checked beside another changed file and beside another staged one, none, one, and
several files, the worktree's index left as it was, and each refusal: a file outside the worktree, a
file that doesn't exist, and a check whose program is missing."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import CantRun, Wrong
from repo_files import git
from repository.commit_checks import findings
from rn_runs import changed, head, hook, made_run

# A check that prints each file a commit would hold, one a line, and fails.
NAMES = "git diff --cached --name-only\nexit 1\n"


def staged(run: Any) -> list[str]:
    """Each file staged in the run's worktree."""
    worktree = rn_files.worktree_of(run.repository, run.name)
    return git(worktree, "diff", "--cached", "--name-only").split()


def test_a_repository_with_no_check_gives_none_and_stages_nothing(tmp_path: Any, host: Any):
    """Given a run whose repository sets no pre-commit check, and the command written
    When findings is asked of the command
    Then it gives none, nothing is staged in the worktree, and the branch's head is as it was"""
    run = made_run(str(tmp_path))
    changed(run, {rn_files.COMMAND: "print()\n"})
    before = head(rn_files.worktree_of(run.repository, run.name))
    assert findings(run, [rn_files.COMMAND], host) == []
    assert staged(run) == []
    assert head(rn_files.worktree_of(run.repository, run.name)) == before


def test_a_check_that_passes_gives_none(tmp_path: Any, host: Any):
    """Given a run whose repository's pre-commit check prints a line and passes
    When findings is asked of the command
    Then it gives none"""
    run = made_run(str(tmp_path))
    hook(run.repository, "echo 'all good'\nexit 0\n")
    changed(run, {rn_files.COMMAND: "print()\n"})
    assert findings(run, [rn_files.COMMAND], host) == []


def test_a_check_that_fails_gives_its_one_line(tmp_path: Any, host: Any):
    """Given a run whose repository's pre-commit check fails saying one line
    When findings is asked of the command
    Then it gives that line, and the branch's head is as it was"""
    run = made_run(str(tmp_path))
    hook(run.repository, "echo 'invoicer/__main__.py: no tests'\nexit 1\n")
    changed(run, {rn_files.COMMAND: "print()\n"})
    before = head(rn_files.worktree_of(run.repository, run.name))
    assert findings(run, [rn_files.COMMAND], host) == ["invoicer/__main__.py: no tests"]
    assert head(rn_files.worktree_of(run.repository, run.name)) == before


def test_a_check_that_fails_gives_each_of_its_lines_in_order(tmp_path: Any, host: Any):
    """Given a run whose repository's pre-commit check fails saying three lines, one on stderr
    When findings is asked of the command
    Then it gives each of the three lines, in the order printed"""
    run = made_run(str(tmp_path))
    hook(run.repository, "echo first\necho second >&2\necho third\nexit 1\n")
    changed(run, {rn_files.COMMAND: "print()\n"})
    assert findings(run, [rn_files.COMMAND], host) == ["first", "second", "third"]


def test_a_check_set_by_core_hookspath_runs(tmp_path: Any, host: Any):
    """Given a repository whose checks are committed on main in hooks/, set by core.hooksPath,
    one failing on each commit of the command, and a run made from it
    When findings is asked of the command
    Then it gives the failing check's line"""
    refuses = (
        "git diff --cached --name-only | grep -qx 'invoicer/__main__.py' || exit 0\n"
        "echo 'from hooksPath'\nexit 1\n"
    )
    run = made_run(str(tmp_path), hooks={"pre-commit": refuses})
    changed(run, {rn_files.COMMAND: "print()\n"})
    assert findings(run, [rn_files.COMMAND], host) == ["from hooksPath"]


def test_the_check_reads_the_files_given_alone(tmp_path: Any, host: Any):
    """Given a run whose command and guide are written, and whose check prints each file a commit
    would hold and fails
    When findings is asked of the command alone
    Then it gives the command alone, and nothing is staged in the worktree"""
    run = made_run(str(tmp_path))
    hook(run.repository, NAMES)
    changed(run, {rn_files.COMMAND: "print()\n", rn_files.GUIDE: "# Guide\n"})
    assert findings(run, [rn_files.COMMAND], host) == [rn_files.COMMAND]
    assert staged(run) == []


def test_the_check_reads_the_files_given_alone_beside_another_staged(tmp_path: Any, host: Any):
    """Given a run whose command and guide are written, the guide staged in the worktree, and whose
    check prints each file a commit would hold and fails
    When findings is asked of the command alone
    Then it gives the command alone, and the worktree's index holds the guide alone, as it was"""
    run = made_run(str(tmp_path))
    hook(run.repository, NAMES)
    changed(run, {rn_files.COMMAND: "print()\n", rn_files.GUIDE: "# Guide\n"})
    git(rn_files.worktree_of(run.repository, run.name), "add", "--", rn_files.GUIDE)
    assert findings(run, [rn_files.COMMAND], host) == [rn_files.COMMAND]
    assert staged(run) == [rn_files.GUIDE]


def test_the_check_reads_each_of_several_files(tmp_path: Any, host: Any):
    """Given a run whose command and guide are written, and whose check prints each file a commit
    would hold and fails
    When findings is asked of both
    Then it gives both, in git's order"""
    run = made_run(str(tmp_path))
    hook(run.repository, NAMES)
    changed(run, {rn_files.COMMAND: "print()\n", rn_files.GUIDE: "# Guide\n"})
    given = findings(run, [rn_files.GUIDE, rn_files.COMMAND], host)
    assert given == [rn_files.GUIDE, rn_files.COMMAND]


def test_no_file_gives_none_and_stages_nothing(tmp_path: Any, host: Any):
    """Given a run whose command is written, and whose check prints each file a commit would hold
    and fails
    When findings is asked of no file
    Then it gives none, and nothing is staged"""
    run = made_run(str(tmp_path))
    hook(run.repository, NAMES)
    changed(run, {rn_files.COMMAND: "print()\n"})
    assert findings(run, [], host) == []
    assert staged(run) == []


@pytest.mark.parametrize("outside", ["../outside.py", "/etc/hostname"])
def test_a_file_outside_the_worktree_is_refused(tmp_path: Any, host: Any, outside: str):
    """Given a run
    When findings is asked of a file outside its worktree
    Then Wrong is raised, naming it, and nothing is staged"""
    run = made_run(str(tmp_path))
    with pytest.raises(Wrong, match=outside.replace(".", r"\.")):
        findings(run, [outside], host)
    assert staged(run) == []


def test_a_file_that_doesnt_exist_is_refused(tmp_path: Any, host: Any):
    """Given a run with no file invoicer/cli.py
    When findings is asked of it beside the command
    Then Wrong is raised, naming invoicer/cli.py"""
    run = made_run(str(tmp_path))
    changed(run, {rn_files.COMMAND: "print()\n"})
    with pytest.raises(Wrong, match="invoicer/cli.py"):
        findings(run, [rn_files.COMMAND, "invoicer/cli.py"], host)


def test_a_check_whose_program_is_missing_cant_run(tmp_path: Any, host: Any):
    """Given a run whose repository's pre-commit check runs a program that isn't there
    When findings is asked of the command
    Then CantRun is raised, with what was said of the program"""
    run = made_run(str(tmp_path))
    path = os.path.join(run.repository, ".git", "hooks", "pre-commit")
    with open(path, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env no-such-check-program\n")
    os.chmod(path, 0o755)
    changed(run, {rn_files.COMMAND: "print()\n"})
    with pytest.raises(CantRun, match="no-such-check-program"):
        findings(run, [rn_files.COMMAND], host)

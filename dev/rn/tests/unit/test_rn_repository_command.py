"""The unit cases of repository/command.py's `main`, repository's command line: each subcommand
with what it prints and its exit code, `new` with the context it writes, `find` of no run and with
GitHub out of reach, `pause`, `cancel` of a run whose branch and pull request it removes on GitHub,
of one where gh can't ask GitHub, and of a worktree that can't be removed, `put-up` printing a link
of each of the deliverable's paths, marking the deliverable's last Round, making done one at a step
that the user doesn't check, leaving open one at a step the user checks and one done already, put
up again after a Fix, as it is, and leaving the run as it stood where the push is refused, `diff`,
`ci`, `trial`, and each fault by its exit code: 2 with the
usage for arguments of another form, 1 with `repository: ` for an input that is Wrong and for
something Missing, and 2 for what CantRun."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import pytest
import rn_files
from gh import gh_double
from repo_files import git
from repository.command import USAGE, main
from repository.place import RunPlace
from rn_runs import NAME, branch_run, changed, head, made_run

RUN = f".claude/worktrees/rn-{NAME}/.rn/{NAME}"
PR = "http://github.com/owner/repo/pull/1"


def command_link(run: RunPlace, ref: str = "HEAD") -> str:
    """The line that put-up prints of the command's file at the commit of the run's worktree that
    the ref names."""
    worktree = rn_files.worktree_of(run.repository, NAME)
    return f"http://github.com/owner/repo/blob/{head(worktree, ref)}/{rn_files.COMMAND}\n"


def test_new_prints_the_new_runs_folder_from_the_repositorys_top(tmp_path: Any, host: Any):
    """Given invoicer's repository with a remote
    When repository new is given the walkthrough's slug and its languages
    Then it gives 0 printing the run's folder, named by today and the slug, from the top, as a
    line; the run's design tree holds the goal open, for the pruner to write, and its context
    holds rn's version as its plugin.json gives it and the languages, English as the
    deliverables' and Japanese as the conversation's"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    name = f"{date.today():%Y%m%d}-{rn_files.NAMED}"
    folder = f".claude/worktrees/rn-{name}/.rn/{name}"
    argv = ["new", rn_files.NAMED, "English", "Japanese"]
    given = main(argv, repo, rn_files.RN, host)
    assert given == (0, folder + "\n", "")
    tree = rn_files.read_json(os.path.join(repo, folder, "design-tree.json"))
    assert tree["goal"] == {"decided": None}
    plugin = rn_files.read_json(os.path.join(rn_files.RN, ".claude-plugin", "plugin.json"))
    assert tree["context"] == {
        "rn": plugin["version"],
        "languages": {"deliverables": "English", "conversation": "Japanese"},
        "issues": {"closes": [], "refs": []},
        "pr": None,
    }


def test_new_of_other_than_a_slug_says_the_form_it_takes(tmp_path: Any, host: Any):
    """Given invoicer's repository with a remote
    When repository new is given the user's words as typed in place of the slug
    Then it gives 1 with `repository: ` and the form that a slug takes on stderr, and makes no
    worktree"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    code, out, err = main(["new", rn_files.WORDS, *rn_files.LANGUAGES], repo, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository: ") and "lower-case English words joined by -" in err
    assert not os.path.exists(os.path.join(repo, ".claude", "worktrees"))


def test_find_of_no_run_prints_nothing(tmp_path: Any, host: Any):
    """Given invoicer's repository with a remote and no run
    When repository find is run
    Then it gives 0 printing nothing"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    assert main(["find"], repo, rn_files.RN, host) == (0, "", "")


def test_find_with_github_out_of_reach_says_so_on_stderr(tmp_path: Any, host: Any):
    """Given invoicer's repository with one run with work left, whose origin git can't reach
    When repository find is run
    Then it gives 0 printing the run's folder as a line, and on stderr `repository: can't
    check the runs on GitHub, as git can't ask origin: ` with what git said, as one line"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    git(repo, "remote", "add", "origin", str(tmp_path / "gone.git"))
    branch_run(repo, NAME, rn_files.walkthrough_tree(NAME))
    code, out, err = main(["find"], repo, rn_files.RN, host)
    assert (code, out) == (0, f"{RUN}\n")
    prefix = "repository: can't check the runs on GitHub, as git can't ask origin: fatal: "
    assert err.startswith(prefix) and err.endswith("exists.\n") and err.count("\n") == 1


def test_pause_prints_the_hash_the_remote_holds(tmp_path: Any, host: Any):
    """Given a run whose design tree is changed
    When repository pause is given the run's folder
    Then it gives 0 printing the hash of origin's rn-<name> as a line"""
    run = made_run(str(tmp_path))
    changed(run, {f".rn/{NAME}/design-tree.json": "{}\n"})
    code, out, err = main(["pause", RUN], run.repository, rn_files.RN, host)
    assert (code, out, err) == (0, head(str(tmp_path / "origin.git"), f"rn-{NAME}") + "\n", "")


def test_pause_with_no_origin_says_what_is_missing(tmp_path: Any, host: Any):
    """Given a run whose repository has no remote
    When repository pause is given the run's folder
    Then it gives 1 with `repository: ` and what's missing on stderr"""
    run = made_run(str(tmp_path), origin=False)
    code, out, err = main(["pause", RUN], run.repository, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository: ")


def test_cancel_removes_the_run_and_prints_what_it_removed_on_github(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose branch is pushed to origin with its pull request open
    When repository cancel is given the run's folder
    Then it gives 0 printing the pull request and origin/rn-<name>, a line each, with nothing on
    stderr; the run's worktree and its local branch are gone; and origin holds no branch
    rn-<name>"""
    run = made_run(str(tmp_path))
    git(run.worktree, "push", "-q", "-u", "origin", f"rn-{NAME}")
    gh_double.opened(gh_state, PR)
    printed = f"{PR}\norigin/rn-{NAME}\n"
    assert main(["cancel", RUN], run.repository, rn_files.RN, host) == (0, printed, "")
    assert not os.path.exists(run.worktree)
    assert git(run.repository, "branch", "--list", f"rn-{NAME}").strip() == ""
    assert git(run.repository, "ls-remote", "--heads", "origin", f"rn-{NAME}") == ""


def test_cancel_that_cant_remove_on_github_says_so_on_stderr_and_still_gives_0(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose branch is pushed to origin, and gh that can't reach GitHub
    When repository cancel is given the run's folder
    Then it gives 0 printing origin/rn-<name> as a line, and on stderr `repository: can't
    remove ` with what it couldn't remove and what gh said, as a line; and the run's worktree and
    its local branch are gone"""
    run = made_run(str(tmp_path))
    git(run.worktree, "push", "-q", "-u", "origin", f"rn-{NAME}")
    gh_double.unreached(gh_state)
    said = gh_double.line(gh_double.PR_VIEW, "gh pr view can't reach GitHub")["stderr"].strip()
    unchecked = (
        f"repository: can't remove the pull request of rn-{NAME} on GitHub, as gh can't ask"
        f" GitHub: {said}\n"
    )
    assert main(["cancel", RUN], run.repository, rn_files.RN, host) == (
        0,
        f"origin/rn-{NAME}\n",
        unchecked,
    )
    assert not os.path.exists(run.worktree)
    assert git(run.repository, "branch", "--list", f"rn-{NAME}").strip() == ""


def test_cancel_of_a_worktree_git_cant_remove_gives_2(tmp_path: Any, host: Any):
    """Given a run whose worktree is locked
    When repository cancel is given the run's folder
    Then it gives 2 with `repository: ` and what git said on stderr, and the worktree stays"""
    run = made_run(str(tmp_path))
    git(run.repository, "worktree", "lock", run.worktree)
    code, out, err = main(["cancel", RUN], run.repository, rn_files.RN, host)
    assert (code, out) == (2, "")
    assert err.startswith("repository: ") and "locked" in err
    assert os.path.isdir(run.worktree)


def test_put_up_prints_a_link_of_each_path_of_the_deliverable_a_line_each(tmp_path: Any, host: Any):
    """Given a run whose command lies at invoicer/__main__.py and at the more path docs/
    When repository put-up is given the run's folder and the command's path
    Then it gives 0 printing the link of the command's file, then of the folder docs, at the
    commit pushed, each as a line"""
    design_tree = rn_files.walkthrough_tree(NAME)
    design_tree["deliverables"][1]["more_paths"] = ["docs/"]
    run = made_run(str(tmp_path), design_tree=design_tree)
    changed(run, {rn_files.COMMAND: "print()\n"})
    given = main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)
    commit = head(rn_files.worktree_of(run.repository, NAME))
    docs = f"http://github.com/owner/repo/tree/{commit}/docs\n"
    assert given == (0, command_link(run) + docs, "")


def test_put_up_marks_the_deliverables_last_round_as_put_up(tmp_path: Any, host: Any):
    """Given a run whose command has Rounds content-1 and content-2, its node holding N1 not good
    with an open decision of N1, the rest good
    When repository put-up is given the run's folder and the command's path
    Then it gives 0 printing the command's link, and content-2 alone holds put-up.json with N1
    not good and its open decision"""
    left = {"N1": [rn_files.decision("a comma in a line", None)]}
    design_tree = rn_files.walkthrough_tree(NAME, command_good=["N2", "N3"], command_decisions=left)
    run = made_run(str(tmp_path), design_tree=design_tree)
    changed(run, {rn_files.COMMAND: "print()\n"})
    folder = rn_files.folder_of(run.repository, NAME)
    first, second = (rn_files.a_round(folder, rn_files.COMMAND, "content", n) for n in (1, 2))
    given = main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)
    assert given == (0, command_link(run), "")
    assert not os.path.exists(os.path.join(first, "put-up.json"))
    assert rn_files.read_json(os.path.join(second, "put-up.json")) == {
        "short": ["N1"],
        "open": [{"condition": "N1", "about": "a comma in a line"}],
    }


def stepped(command: bool) -> dict:
    """The walkthrough's tree whose command is open with each condition good, at a step whose
    sign-off is as given, and whose guide's step the user checks."""
    design_tree = rn_files.walkthrough_tree(NAME, command_good=True)
    design_tree["steps"] = [
        rn_files.step("what it does", [rn_files.COMMAND], command),
        rn_files.step("how it's used", [rn_files.GUIDE], True),
    ]
    return design_tree


def test_put_up_at_a_step_the_user_doesnt_check_makes_it_done_marks_its_round_and_pushes(
    tmp_path: Any, host: Any
):
    """Given a run whose command, open with each condition good after Round content-1, lies at a
    step that the user doesn't check
    When repository put-up is given the run's folder and the command's path
    Then it gives 0 printing the command's link at the commit before it's done; the tree holds the
    command done in its one line; content-1 holds put-up.json; the
    tree, put-up.json among it, is committed as
    `rn: <command's name>, done at a step that the user doesn't check`; and origin's rn-<name>
    holds that commit"""
    run = made_run(str(tmp_path), design_tree=stepped(False))
    changed(run, {rn_files.COMMAND: "print()\n"})
    folder = rn_files.folder_of(run.repository, NAME)
    first = rn_files.a_round(folder, rn_files.COMMAND, "content", 1)
    given = main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)
    assert given == (0, command_link(run, "HEAD~1"), "")
    design_tree = rn_files.read_json(os.path.join(folder, "design-tree.json"))
    done = rn_files.done_node(rn_files.COMMAND_NAME, rn_files.COMMAND, "light")
    assert design_tree["deliverables"][1] == done
    assert os.path.isfile(os.path.join(first, "put-up.json"))
    worktree = rn_files.worktree_of(run.repository, NAME)
    assert git(worktree, "status", "--porcelain") == ""
    assert git(worktree, "log", "-1", "--format=%s").strip() == (
        f"rn: {rn_files.COMMAND_NAME}, done at a step that the user doesn't check"
    )
    assert head(str(tmp_path / "origin.git"), f"rn-{NAME}") == head(worktree)


def test_put_up_at_a_step_the_user_checks_leaves_it_open_for_the_signoff(tmp_path: Any, host: Any):
    """Given a run whose command, open with each condition good after Round content-1, lies at a
    step that the user checks
    When repository put-up is given the run's folder and the command's path
    Then it gives 0, and the tree holds the command open"""
    run = made_run(str(tmp_path), design_tree=stepped(True))
    changed(run, {rn_files.COMMAND: "print()\n"})
    folder = rn_files.folder_of(run.repository, NAME)
    rn_files.a_round(folder, rn_files.COMMAND, "content", 1)
    assert main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)[0] == 0
    design_tree = rn_files.read_json(os.path.join(folder, "design-tree.json"))
    assert design_tree["deliverables"][1]["status"] == "open"


def test_put_up_of_a_deliverable_done_at_a_step_the_user_doesnt_check_leaves_it_as_it_is(
    tmp_path: Any, host: Any
):
    """Given a run whose command, done at a step that the user doesn't check, its Round content-1
    put up, was mended by a Fix fix-2 that its fixer fixed
    When repository put-up is given the run's folder and the command's path
    Then it gives 0 printing the command's link; the tree holds the command done as it was,
    beside the pull request put-up wrote; and no commit makes a deliverable done"""
    design_tree = stepped(False)
    done = rn_files.done_node(rn_files.COMMAND_NAME, rn_files.COMMAND, "light")
    design_tree["deliverables"][1] = done
    run = made_run(str(tmp_path), design_tree=design_tree)
    changed(run, {rn_files.COMMAND: "print()\n"})
    folder = rn_files.folder_of(run.repository, NAME)
    rn_files.a_round(folder, rn_files.COMMAND, "content", 1)
    fix = rn_files.round_of(folder, rn_files.COMMAND, "fix", 2)
    rn_files.write_json(os.path.join(fix, "fixer.json"), {"result": "fixed", "files": []})
    given = main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)
    assert given == (0, command_link(run), "")
    design_tree["context"]["pr"] = PR
    assert rn_files.read_json(os.path.join(folder, "design-tree.json")) == design_tree
    worktree = rn_files.worktree_of(run.repository, NAME)
    assert "done at a step" not in git(worktree, "log", "-3", "--format=%s")


def test_put_up_whose_push_the_repositorys_check_refuses_leaves_the_run_to_a_fix(
    tmp_path: Any, host: Any
):
    """Given a run whose command, at a step that the user doesn't check, open with each condition
    good after Round content-1, and a pre-push hook that refuses each push, saying so
    When repository put-up is given the run's folder and the command's path
    Then it gives 2 with the hook's words; content-1 holds no put-up.json; the tree holds the
    command open as it was; and origin holds no branch of the run"""
    run = made_run(str(tmp_path), design_tree=stepped(False))
    pre_push = os.path.join(run.repository, ".git", "hooks", "pre-push")
    with open(pre_push, "w", encoding="utf-8") as f:
        f.write("#!/bin/sh\necho 'lint: a line ends in a space' >&2\nexit 1\n")
    os.chmod(pre_push, 0o755)
    changed(run, {rn_files.COMMAND: "print() \n"})
    folder = rn_files.folder_of(run.repository, NAME)
    first = rn_files.a_round(folder, rn_files.COMMAND, "content", 1)
    code, out, err = main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)
    assert (code, out) == (2, "")
    assert "lint: a line ends in a space" in err
    assert not os.path.exists(os.path.join(first, "put-up.json"))
    assert rn_files.read_json(os.path.join(folder, "design-tree.json")) == stepped(False)
    assert f"rn-{NAME}" not in git(str(tmp_path / "origin.git"), "branch", "--list")


def test_diff_prints_the_pull_requests_whole_diff(tmp_path: Any, host: Any):
    """Given a run whose guide is written but not committed
    When repository diff is given the run's folder
    Then it gives 0 printing a diff that holds the guide"""
    run = made_run(str(tmp_path))
    changed(run, {rn_files.GUIDE: "# Guide\n"})
    code, out, err = main(["diff", RUN], run.repository, rn_files.RN, host)
    assert (code, err) == (0, "")
    assert f"+++ b/{rn_files.GUIDE}" in out


def test_ci_prints_how_each_check_ended(tmp_path: Any, host: Any):
    """Given a run whose plan was put up, and whose CI's checks each passed
    When repository ci is given the run's folder
    Then it gives 0 printing each check with how it ended"""
    run = made_run(str(tmp_path), design_tree=rn_files.walkthrough_tree(NAME, plan_done=False))
    main(["put-up", RUN, rn_files.plan_path(NAME)], run.repository, rn_files.RN, host)
    code, out, err = main(["ci", RUN], run.repository, rn_files.RN, host)
    assert (code, err) == (0, "")
    assert "tests\tpassed\n" in out


def test_trial_prints_the_folder_of_the_peoples_starting_state(tmp_path: Any, host: Any, temp: str):
    """Given a run with the command's Round content-1
    When repository trial is given the run's folder and the Round's folder from the top
    Then it gives 0 printing the folder it made, under the system's temporary folder, as a line,
    and the folder holds invoicer's lines"""
    run = made_run(str(tmp_path))
    round_ = rn_files.round_of(RUN, rn_files.COMMAND, "content", 1)
    os.makedirs(os.path.join(run.repository, round_))
    code, out, err = main(["trial", RUN, round_], run.repository, rn_files.RN, host)
    assert (code, err) == (0, "")
    folder = out.removesuffix("\n")
    assert out == folder + "\n"
    expected = os.path.join(temp, f"rn-trial-{NAME}-invoicer%2F__main__.py-content-1")
    assert os.path.normpath(folder) == expected
    assert os.path.isfile(os.path.join(folder, "invoicer", "lines.py"))


def test_a_folder_that_isnt_a_runs_is_wrong(tmp_path: Any, host: Any):
    """Given invoicer's repository with no run
    When repository diff is given a folder that isn't a run's
    Then it gives 1 with `repository: ` naming the folder on stderr"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    code, out, err = main(["diff", "docs"], repo, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository: ") and "docs" in err


@pytest.mark.parametrize(
    "argv",
    [[], ["start"], ["new", rn_files.NAMED, "English"], ["find", "more"]],
)
def test_arguments_of_another_form_give_the_usage(tmp_path: Any, host: Any, argv: list[str]):
    """Given invoicer's repository
    When repository is given arguments other than a subcommand's: none, an unknown one, or one
    too few or too many
    Then it gives 2 with the usage on stderr, and runs nothing"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    assert main(argv, repo, rn_files.RN, host) == (2, "", USAGE)
    assert host.ran == []
    assert git(repo, "branch", "--list").split() == ["*", "main"]

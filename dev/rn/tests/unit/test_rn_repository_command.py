"""The unit cases of repository/command.py's `main`, repository.py's command line: each subcommand
with what it prints and its exit code, `find` of no run, one, and several, `checks` with findings
and with none, and each fault by its exit code: 2 with the usage for arguments of another form, 1
with `repository.py: ` for an input that is Wrong and for something Missing, origin's HEAD naming
no branch and gh with no login among them, and 2 for what CantRun."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import pytest
import rn_files
from gh import gh_double
from repo_files import git
from repository.command import USAGE, main
from rn_runs import NAME, changed, head, hook, made_run

pytestmark = pytest.mark.xfail(strict=True, reason="repository/command.py's body is empty")

RUN = f".claude/worktrees/rn-{NAME}/.rn/{NAME}"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_new_prints_the_new_runs_folder_from_the_repositorys_top(tmp_path: Any, host: Any):
    """Given invoicer's repository with a remote
    When repository.py new is given the walkthrough's words and the goal
    Then it gives 0 printing the run's folder, named by today and the words, from the top, as a
    line, and the run's design tree holds the goal by reasoning"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    name = f"{date.today():%Y%m%d}-{rn_files.NAMED}"
    folder = f".claude/worktrees/rn-{name}/.rn/{name}"
    given = main(["new", rn_files.WORDS, rn_files.GOAL], repo, rn_files.RN, host)
    assert given == (0, folder + "\n", "")
    tree = rn_files.read_json(os.path.join(repo, folder, "design-tree.json"))
    assert tree["goal"] == {"decided": rn_files.GOAL, "by": "reasoning"}


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_new_of_words_with_no_letter_says_what_rn_up_takes(tmp_path: Any, host: Any):
    """Given invoicer's repository with a remote
    When repository.py new is given words with no letter or digit
    Then it gives 1 with `repository.py: ` and what's wrong on stderr, and makes no worktree"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    code, out, err = main(["new", "?!", rn_files.GOAL], repo, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: ") and "/rn:up" in err
    assert not os.path.exists(os.path.join(repo, ".claude", "worktrees"))


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_new_with_no_default_branch_on_origin_says_what_is_missing(tmp_path: Any, host: Any):
    """Given invoicer's repository with no remote, so that origin's HEAD names no branch
    When repository.py new is given the walkthrough's words and the goal
    Then it gives 1 with `repository.py: ` and what's missing on stderr, and makes no worktree"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    code, out, err = main(["new", rn_files.WORDS, rn_files.GOAL], repo, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: ")
    assert not os.path.exists(os.path.join(repo, ".claude", "worktrees"))


@pytest.mark.supports("test_a_pick_up_with_no_run_says_rn_has_none_to_pick_up")
def test_find_of_no_run_prints_nothing(tmp_path: Any, host: Any):
    """Given invoicer's repository with no run
    When repository.py find is run
    Then it gives 0 printing nothing"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    assert main(["find"], repo, rn_files.RN, host) == (0, "", "")


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_find_prints_each_run_newest_first_a_line(tmp_path: Any, host: Any):
    """Given a repository with three runs with work left, made in no order, and one whose every
    deliverable is done
    When repository.py find is run
    Then it gives 0 printing each run with work left, newest first, its folder from the top a
    line"""
    repo = os.path.realpath(str(tmp_path))
    for name in ("20261115-b", "20261120-a", "20261101-z"):
        rn_files.run_folder(repo, name, rn_files.walkthrough_tree(name))
    done = rn_files.tree(
        [rn_files.done_node(rn_files.GOAL, rn_files.plan_path("x"), "design-tree")]
    )
    rn_files.run_folder(repo, "20261121-done", done)
    printed = "".join(
        f".claude/worktrees/rn-{name}/.rn/{name}\n"
        for name in ("20261120-a", "20261115-b", "20261101-z")
    )
    assert main(["find"], repo, rn_files.RN, host) == (0, printed, "")


@pytest.mark.supports("test_a_pause_stops_the_generator_and_pushes_the_runs_work_so_far")
def test_pause_prints_the_hash_the_remote_holds(tmp_path: Any, host: Any):
    """Given a run whose design tree is changed
    When repository.py pause is given the run's folder
    Then it gives 0 printing the hash of origin's rn-<name> as a line"""
    run = made_run(str(tmp_path))
    changed(run, {f".rn/{NAME}/design-tree.json": "{}\n"})
    code, out, err = main(["pause", RUN], run.repository, rn_files.RN, host)
    assert (code, out, err) == (0, head(str(tmp_path / "origin.git"), f"rn-{NAME}") + "\n", "")


@pytest.mark.supports("test_a_pause_stops_the_generator_and_pushes_the_runs_work_so_far")
def test_pause_with_no_origin_says_what_is_missing(tmp_path: Any, host: Any):
    """Given a run whose repository has no remote
    When repository.py pause is given the run's folder
    Then it gives 1 with `repository.py: ` and what's missing on stderr"""
    run = made_run(str(tmp_path), origin=False)
    code, out, err = main(["pause", RUN], run.repository, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: ")


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_put_up_prints_the_pull_requests_changes(tmp_path: Any, host: Any):
    """Given a run whose plan is open
    When repository.py put-up is given the run's folder and the plan's path
    Then it gives 0 printing http://github.com/owner/repo/pull/1/files as a line"""
    run = made_run(str(tmp_path), design_tree=rn_files.walkthrough_tree(NAME, plan_done=False))
    given = main(["put-up", RUN, rn_files.plan_path(NAME)], run.repository, rn_files.RN, host)
    assert given == (0, "http://github.com/owner/repo/pull/1/files\n", "")


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_put_up_with_gh_logged_out_says_what_is_missing_and_commits_nothing(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose command is changed, and gh with no login
    When repository.py put-up is given the run's folder and the command's path
    Then it gives 1 with `repository.py: ` and gh's words that no GitHub host is logged into on
    stderr, and the branch's head is as it was"""
    run = made_run(str(tmp_path))
    changed(run, {rn_files.COMMAND: "print()\n"})
    worktree = rn_files.worktree_of(run.repository, NAME)
    before = head(worktree)
    gh_double.logged_out(gh_state)
    code, out, err = main(["put-up", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: ") and "not logged into any GitHub hosts" in err
    assert head(worktree) == before


@pytest.mark.supports("test_the_generators_checks_give_the_repositorys_commit_check_findings")
def test_checks_with_no_finding_prints_nothing(tmp_path: Any, host: Any):
    """Given a run whose repository sets no check, and the command written
    When repository.py checks is given the run's folder and the command
    Then it gives 0 printing nothing"""
    run = made_run(str(tmp_path))
    changed(run, {rn_files.COMMAND: "print()\n"})
    assert main(["checks", RUN, rn_files.COMMAND], run.repository, rn_files.RN, host) == (
        0,
        "",
        "",
    )


@pytest.mark.supports("test_the_generators_checks_give_the_repositorys_commit_check_findings")
def test_checks_with_findings_gives_1_with_each_a_line(tmp_path: Any, host: Any):
    """Given a run whose repository's check fails saying two lines, and the command and the guide
    written
    When repository.py checks is given the run's folder, the command, and the guide
    Then it gives 1 with the two lines, each a line"""
    run = made_run(str(tmp_path))
    hook(run.repository, "echo first\necho second\nexit 1\n")
    changed(run, {rn_files.COMMAND: "print()\n", rn_files.GUIDE: "# Guide\n"})
    code, out, err = main(
        ["checks", RUN, rn_files.COMMAND, rn_files.GUIDE], run.repository, rn_files.RN, host
    )
    assert code == 1
    assert out + err == "first\nsecond\n"


@pytest.mark.supports("test_the_people_start_from_the_branch_without_rns_folder")
def test_trial_prints_the_folder_of_the_peoples_starting_state(tmp_path: Any, host: Any, temp: str):
    """Given a run with the command's Round content-1
    When repository.py trial is given the run's folder and the Round's folder from the top
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


@pytest.mark.supports("test_the_people_start_from_the_branch_without_rns_folder")
def test_trial_where_the_folder_cant_be_made_gives_2(tmp_path: Any, host: Any, temp: str):
    """Given a run with the command's Round content-1, and a system's temporary folder that may
    not be written
    When repository.py trial is given the run's folder and the Round's folder
    Then it gives 2 with what stopped it on stderr"""
    run = made_run(str(tmp_path))
    round_ = rn_files.round_of(RUN, rn_files.COMMAND, "content", 1)
    os.makedirs(os.path.join(run.repository, round_))
    os.chmod(temp, 0o555)
    try:
        code, out, err = main(["trial", RUN, round_], run.repository, rn_files.RN, host)
    finally:
        os.chmod(temp, 0o755)
    assert (code, out) == (2, "")
    assert err


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
@pytest.mark.parametrize("sub", ["pause", "put-up", "checks", "trial"])
def test_a_folder_that_isnt_a_runs_is_wrong(tmp_path: Any, host: Any, sub: str):
    """Given invoicer's repository with no run
    When the subcommand is given a folder that isn't a run's, with what else it takes
    Then it gives 1 with `repository.py: ` naming the folder on stderr"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rest = {"pause": [], "put-up": [rn_files.COMMAND], "checks": [rn_files.COMMAND]}
    argv = [sub, "docs", *rest.get(sub, ["docs"])]
    code, out, err = main(argv, repo, rn_files.RN, host)
    assert (code, out) == (1, "")
    assert err.startswith("repository.py: ") and "docs" in err


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["start"],
        ["new", rn_files.WORDS],
        ["new", rn_files.WORDS, rn_files.GOAL, "more"],
        ["find", "more"],
        ["pause"],
        ["put-up", RUN],
        ["checks"],
        ["trial", RUN],
        ["trial", RUN, "a", "b"],
    ],
)
def test_arguments_of_another_form_give_the_usage(tmp_path: Any, host: Any, argv: list[str]):
    """Given invoicer's repository
    When repository.py is given arguments other than a subcommand's: none, an unknown one, or one
    too few or too many
    Then it gives 2 with the usage on stderr, and runs nothing"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    assert main(argv, repo, rn_files.RN, host) == (2, "", USAGE)
    assert host.ran == []
    assert git(repo, "branch", "--list").split() == ["*", "main"]

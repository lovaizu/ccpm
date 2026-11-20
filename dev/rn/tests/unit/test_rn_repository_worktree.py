"""The unit cases of repository/worktree.py: `new`, from the default branch that origin's HEAD
names: main, trunk with the user on another branch with work of their own, and trunk while the user
is on main, whose head differs; with each refusal: an empty goal, a run of the name already there, a
folder that isn't a repository, a repository with no commit, and one whose origin's HEAD names no
branch, with a remote or with none; and `paused`, with no run, one, and several, newest first by
name, a run whose every deliverable is done left out, folders that nearly match a run's left out,
and the refusal of a design tree that isn't JSON."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import Missing, Wrong
from repo_files import git, write_files
from repository.place import RunPlace
from repository.worktree import new, paused
from rn_runs import NAME, head

GOAL = rn_files.GOAL
PRACTICE = rn_files.practice("design-tree")


def started_tree(name: str, goal: str = GOAL) -> dict[str, Any]:
    """The tree that a run starts from, as tree.form.started's contract names it: the goal by
    reasoning, the plan as its one deliverable, open, each condition not good, and no work."""
    return rn_files.tree([rn_files.plan(name, good=False, goal=goal)], goal=goal, by="reasoning")


def a_repository(tmp_path: Any, branch: str = "main") -> str:
    """invoicer's repository with a remote origin whose default branch is the branch given."""
    repo = rn_files.repository(str(tmp_path / "invoicer"), branch=branch)
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    return repo


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_new_run_has_its_branch_from_main_checked_out_with_the_tree_uncommitted(
    tmp_path: Any, host: Any
):
    """Given invoicer's repository on main with a remote, the user on main
    When new makes the run 20261120-invoices with the goal
    Then it gives the run; the worktree has rn-20261120-invoices checked out at main's head,
    holding the started tree at .rn/20261120-invoices/design-tree.json, uncommitted; and the
    user's branch, head, and files are as they were"""
    repo = a_repository(tmp_path)
    before = head(repo, "main")
    run = RunPlace(repo, NAME)
    assert new(run, GOAL, PRACTICE, host) == run
    worktree = rn_files.worktree_of(repo, NAME)
    assert git(worktree, "branch", "--show-current").strip() == f"rn-{NAME}"
    assert head(worktree) == before
    tree_path = os.path.join(rn_files.folder_of(repo, NAME), "design-tree.json")
    assert rn_files.read_json(tree_path) == started_tree(NAME)
    assert git(worktree, "status", "--porcelain").split() == ["??", ".rn/"]
    assert git(repo, "branch", "--show-current").strip() == "main"
    assert head(repo) == before
    assert git(repo, "status", "--porcelain", "--untracked-files=no").strip() == ""


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_new_run_branches_from_the_default_branch_while_the_user_is_on_another(
    tmp_path: Any, host: Any
):
    """Given invoicer's repository whose default branch is trunk, the user on a branch of their
    own with a commit past trunk and a change not committed
    When new makes the run
    Then the run's branch starts at trunk's head, and the user's branch, its head, and their
    change are as they were"""
    repo = a_repository(tmp_path, "trunk")
    trunk = head(repo, "trunk")
    git(repo, "checkout", "-q", "-b", "mine")
    write_files(repo, {"NOTES.md": "mine\n"})
    git(repo, "add", "NOTES.md")
    git(repo, "commit", "-q", "-m", "Mine.")
    mine = head(repo)
    write_files(repo, {"NOTES.md": "mine, still\n"})
    new(RunPlace(repo, NAME), GOAL, PRACTICE, host)
    assert head(rn_files.worktree_of(repo, NAME)) == trunk
    assert git(repo, "branch", "--show-current").strip() == "mine"
    assert head(repo) == mine
    assert git(repo, "status", "--porcelain", "--untracked-files=no").split() == ["M", "NOTES.md"]


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_new_run_branches_from_what_origins_head_names_not_the_branch_checked_out(
    tmp_path: Any, host: Any
):
    """Given invoicer's repository on main with a remote whose HEAD names trunk, a branch with a
    commit past main, the user on main
    When new makes the run
    Then the run's branch starts at origin's trunk's head, not main's, and main is as it was"""
    repo = a_repository(tmp_path)
    main = head(repo, "main")
    git(repo, "checkout", "-q", "-b", "trunk")
    write_files(repo, {"CHANGES.md": "trunk\n"})
    git(repo, "add", "CHANGES.md")
    git(repo, "commit", "-q", "-m", "Trunk.")
    git(repo, "push", "-q", "origin", "trunk")
    trunk = head(repo, "trunk")
    git(repo, "checkout", "-q", "main")
    git(repo, "remote", "set-head", "origin", "trunk")
    new(RunPlace(repo, NAME), GOAL, PRACTICE, host)
    assert head(rn_files.worktree_of(repo, NAME)) == trunk
    assert head(repo, "main") == main
    assert git(repo, "branch", "--show-current").strip() == "main"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
@pytest.mark.parametrize("remote", [True, False])
def test_a_repository_whose_origin_head_names_no_branch_is_missing_its_default(
    tmp_path: Any, host: Any, remote: bool
):
    """Given invoicer's repository on main with a commit, and a remote origin whose HEAD is
    unset, or no remote at all
    When new makes the run
    Then Missing is raised, and no worktree and no branch rn-<name> is made"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    if remote:
        rn_files.with_origin(repo, str(tmp_path / "origin.git"))
        git(repo, "remote", "set-head", "origin", "--delete")
    with pytest.raises(Missing):
        new(RunPlace(repo, NAME), GOAL, PRACTICE, host)
    assert not os.path.exists(rn_files.worktree_of(repo, NAME))
    assert git(repo, "branch", "--list", f"rn-{NAME}").strip() == ""


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
@pytest.mark.parametrize("goal", ["", "   "])
def test_an_empty_goal_is_refused_with_nothing_made(tmp_path: Any, host: Any, goal: str):
    """Given invoicer's repository
    When new is given an empty goal
    Then Wrong is raised, and no branch or worktree of the run is made"""
    repo = a_repository(tmp_path)
    with pytest.raises(Wrong):
        new(RunPlace(repo, NAME), goal, PRACTICE, host)
    assert not os.path.exists(rn_files.worktree_of(repo, NAME))
    assert git(repo, "branch", "--list", f"rn-{NAME}").strip() == ""


@pytest.mark.supports("test_a_new_request_in_a_paused_runs_words_leaves_the_run_as_it_was")
def test_a_run_of_the_name_already_there_is_refused_and_left_as_it_was(tmp_path: Any, host: Any):
    """Given invoicer's repository whose run 20261120-invoices was made
    When new makes a run of the same name with another goal
    Then Wrong is raised naming the run, and its design tree is as it was"""
    repo = a_repository(tmp_path)
    run = RunPlace(repo, NAME)
    new(run, GOAL, PRACTICE, host)
    tree_path = os.path.join(rn_files.folder_of(repo, NAME), "design-tree.json")
    before = rn_files.read_json(tree_path)
    with pytest.raises(Wrong, match=NAME):
        new(run, "The user gets another thing.", PRACTICE, host)
    assert rn_files.read_json(tree_path) == before


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_folder_that_isnt_a_git_repository_is_missing_one(tmp_path: Any, host: Any):
    """Given a folder of invoicer's files with no git
    When new makes a run there
    Then Missing is raised, and no worktree is made"""
    folder = os.path.realpath(str(tmp_path / "plain"))
    write_files(folder, {"README.md": "# plain\n"})
    with pytest.raises(Missing):
        new(RunPlace(folder, NAME), GOAL, PRACTICE, host)
    assert not os.path.exists(rn_files.worktree_of(folder, NAME))


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_folder_inside_a_repository_but_not_its_top_is_missing_one(tmp_path: Any, host: Any):
    """Given invoicer's repository, and its folder invoicer/
    When new makes a run with that folder as its repository
    Then Missing is raised"""
    repo = a_repository(tmp_path)
    with pytest.raises(Missing):
        new(RunPlace(os.path.join(repo, "invoicer"), NAME), GOAL, PRACTICE, host)


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_repository_with_no_commit_is_missing_one(tmp_path: Any, host: Any):
    """Given a git repository with no commit
    When new makes a run there
    Then Missing is raised"""
    repo = os.path.realpath(str(tmp_path / "empty"))
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    with pytest.raises(Missing):
        new(RunPlace(repo, NAME), GOAL, PRACTICE, host)


# paused


def a_run(repo: str, name: str, done: bool = False) -> None:
    """Writes the run's design tree in its worktree: the walkthrough's, or one whose every
    deliverable is done."""
    if done:
        design_tree = rn_files.tree(
            [rn_files.done_node(GOAL, rn_files.plan_path(name), "design-tree")]
        )
    else:
        design_tree = rn_files.walkthrough_tree(name)
    rn_files.run_folder(repo, name, design_tree)


@pytest.mark.supports("test_a_pick_up_with_no_run_says_rn_has_none_to_pick_up")
def test_a_repository_with_no_worktrees_folder_has_no_run(tmp_path: Any):
    """Given a repository with no .claude/worktrees
    When paused is asked
    Then it gives none"""
    assert paused(os.path.realpath(str(tmp_path))) == []


@pytest.mark.supports("test_a_pick_up_with_no_run_says_rn_has_none_to_pick_up")
def test_an_empty_worktrees_folder_has_no_run(tmp_path: Any):
    """Given a repository whose .claude/worktrees holds nothing
    When paused is asked
    Then it gives none"""
    repo = os.path.realpath(str(tmp_path))
    os.makedirs(os.path.join(repo, ".claude", "worktrees"))
    assert paused(repo) == []


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_one_run_with_work_left_is_given(tmp_path: Any):
    """Given a repository with one run whose design tree holds an open deliverable
    When paused is asked
    Then it gives that run"""
    repo = os.path.realpath(str(tmp_path))
    a_run(repo, NAME)
    assert paused(repo) == [RunPlace(repo, NAME)]


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_several_runs_come_newest_first_by_name(tmp_path: Any):
    """Given a repository with four runs with work left, of three days and two of one day, made
    in no order
    When paused is asked
    Then it gives them newest first by name"""
    repo = os.path.realpath(str(tmp_path))
    for name in ("20261115-b", "20261120-a", "20261101-z", "20261120-b"):
        a_run(repo, name)
    assert paused(repo) == [
        RunPlace(repo, "20261120-b"),
        RunPlace(repo, "20261120-a"),
        RunPlace(repo, "20261115-b"),
        RunPlace(repo, "20261101-z"),
    ]


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_run_whose_every_deliverable_is_done_is_left_out(tmp_path: Any):
    """Given a repository with a run whose every deliverable is done, older than one with work
    left, and newer than another
    When paused is asked
    Then it gives the two with work left, newest first"""
    repo = os.path.realpath(str(tmp_path))
    a_run(repo, "20261110-old")
    a_run(repo, "20261115-done", done=True)
    a_run(repo, "20261120-new")
    assert paused(repo) == [RunPlace(repo, "20261120-new"), RunPlace(repo, "20261110-old")]


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_run_whose_open_deliverable_is_being_made_is_given(tmp_path: Any):
    """Given a repository with one run whose only deliverable not done has status doing
    When paused is asked
    Then it gives that run"""
    repo = os.path.realpath(str(tmp_path))
    node = rn_files.open_node(rn_files.COMMAND_NAME, rn_files.COMMAND, "light")
    node["status"] = "doing"
    rn_files.run_folder(
        repo,
        NAME,
        rn_files.tree([rn_files.done_node(GOAL, rn_files.plan_path(NAME), "design-tree"), node]),
    )
    assert paused(repo) == [RunPlace(repo, NAME)]


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_folders_that_nearly_match_a_run_are_left_out(tmp_path: Any):
    """Given a repository with one run, beside a worktree rn2-<name> and one <name> with no rn-,
    each holding a design tree with work left, and a worktree rn-<name> with no design tree
    When paused is asked
    Then it gives the one run"""
    repo = os.path.realpath(str(tmp_path))
    a_run(repo, NAME)
    worktrees = os.path.join(repo, ".claude", "worktrees")
    for folder in ("rn2-20261121-x", "20261122-y"):
        name = folder.split("-", 1)[1] if folder.startswith("rn2") else folder
        rn_files.write_json(
            os.path.join(worktrees, folder, ".rn", name, "design-tree.json"),
            rn_files.walkthrough_tree(name),
        )
    os.makedirs(os.path.join(worktrees, "rn-20261123-z", ".rn", "20261123-z"))
    assert paused(repo) == [RunPlace(repo, NAME)]


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_design_tree_that_isnt_json_is_refused_naming_its_path(tmp_path: Any):
    """Given a repository with a run whose design tree isn't JSON
    When paused is asked
    Then Wrong is raised, naming the design tree's path"""
    repo = os.path.realpath(str(tmp_path))
    path = os.path.join(rn_files.folder_of(repo, NAME), "design-tree.json")
    write_files(repo, {os.path.relpath(path, repo): "{ not json"})
    with pytest.raises(Wrong, match="design-tree.json"):
        paused(repo)

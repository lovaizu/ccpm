"""The unit cases of repository/worktree.py: `new`, from the default branch that origin's HEAD
names: main, trunk with the user on another branch with work of their own, and trunk while the user
is on main, whose head differs; with each refusal: an empty goal, a run of the name already there, a
folder that isn't a repository, a repository with no commit, and one whose origin's HEAD names no
branch, with a remote or with none; `newest`, from the runs' branches, with no repository, no run,
one, and several, newest by its last commit, a newer run whose every deliverable is done or that
holds no design tree passed over, branches that nearly match a run's left out, a run's newer local
branch deciding over origin's, and the refusal of a design tree that isn't JSON; and `found`, with
the run's worktree there, removed with its local branch kept, its folder deleted, a run that only
origin holds in a fresh clone, and a worktree that git can't make."""

from __future__ import annotations

import os
import shutil
from typing import Any

import pytest
import rn_files
from fault import CantRun, Missing, Wrong
from repo_files import git, write_files
from repository.place import RunPlace
from repository.worktree import found, new, newest
from rn_runs import NAME, branch_run, dated_commit, head

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


# newest and found


def a_tree(name: str, done: bool = False) -> dict[str, Any]:
    """The walkthrough's design tree of the run, or one whose every deliverable is done."""
    if done:
        return rn_files.tree([rn_files.done_node(GOAL, rn_files.plan_path(name), "design-tree")])
    return rn_files.walkthrough_tree(name)


def cloned(tmp_path: Any, origin: str) -> str:
    """A fresh clone of the remote, as on another machine, with no worktree of rn."""
    clone = os.path.realpath(str(tmp_path / "clone"))
    git(str(tmp_path), "clone", "-q", origin, clone)
    return clone


@pytest.mark.supports("test_a_pick_up_with_no_run_asks_which_run_to_pick_up")
def test_a_folder_that_isnt_a_repository_has_no_run(tmp_path: Any, host: Any):
    """Given a folder that isn't a git repository
    When newest is asked
    Then it gives None"""
    assert newest(os.path.realpath(str(tmp_path)), host) is None


@pytest.mark.supports("test_a_pick_up_with_no_run_asks_which_run_to_pick_up")
def test_a_repository_with_no_branch_of_rn_has_no_run(tmp_path: Any, host: Any):
    """Given a repository with a remote and no branch rn-*
    When newest and found are asked
    Then each gives None, and found makes no worktree"""
    repo = a_repository(tmp_path)
    assert newest(repo, host) is None
    assert found(repo, host) is None
    assert not os.path.exists(os.path.join(repo, ".claude", "worktrees"))


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_one_run_with_work_left_is_given_with_its_worktree_as_it_was(tmp_path: Any, host: Any):
    """Given a repository with one run whose committed design tree holds an open deliverable, its
    worktree there with a change not committed
    When newest and found are asked
    Then each gives that run, and the worktree keeps its change"""
    repo = a_repository(tmp_path)
    branch_run(repo, NAME, a_tree(NAME))
    note = os.path.join(rn_files.worktree_of(repo, NAME), "NOTES.md")
    write_files(rn_files.worktree_of(repo, NAME), {"NOTES.md": "kept\n"})
    assert newest(repo, host) == RunPlace(repo, NAME)
    assert found(repo, host) == RunPlace(repo, NAME)
    with open(note, encoding="utf-8") as f:
        assert f.read() == "kept\n"


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_of_several_runs_the_newest_by_its_last_commit_is_given(tmp_path: Any, host: Any):
    """Given a repository with three runs with work left, whose names order them otherwise than
    their last commits, the newest commit on 20261101-z
    When newest is asked
    Then it gives 20261101-z, neither the first nor the last by name"""
    repo = a_repository(tmp_path)
    for name, when in (
        ("20261115-b", "2026-11-15T09:00:00"),
        ("20261101-z", "2026-11-21T09:00:00"),
        ("20261120-a", "2026-11-20T09:00:00"),
    ):
        branch_run(repo, name, a_tree(name), when)
    assert newest(repo, host) == RunPlace(repo, "20261101-z")


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_newer_run_whose_every_deliverable_is_done_is_passed_over(tmp_path: Any, host: Any):
    """Given a repository with a run whose every deliverable is done, newer than one with work
    left, and a branch rn-<name> newer still that holds no design tree
    When newest is asked
    Then it gives the run with work left"""
    repo = a_repository(tmp_path)
    branch_run(repo, "20261110-old", a_tree("20261110-old"), "2026-11-10T09:00:00")
    branch_run(repo, "20261115-done", a_tree("20261115-done", True), "2026-11-15T09:00:00")
    git(repo, "branch", "rn-20261121-bare", "main")
    assert newest(repo, host) == RunPlace(repo, "20261110-old")


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_run_whose_open_deliverable_is_being_made_is_given(tmp_path: Any, host: Any):
    """Given a repository with one run whose only deliverable not done has status doing
    When newest is asked
    Then it gives that run"""
    repo = a_repository(tmp_path)
    node = rn_files.open_node(rn_files.COMMAND_NAME, rn_files.COMMAND, "light")
    node["status"] = "doing"
    plan = rn_files.done_node(GOAL, rn_files.plan_path(NAME), "design-tree")
    branch_run(repo, NAME, rn_files.tree([plan, node]))
    assert newest(repo, host) == RunPlace(repo, NAME)


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_branches_that_nearly_match_a_run_are_left_out(tmp_path: Any, host: Any):
    """Given a repository with one run, beside newer branches rn2-<name> and <name> with no rn-,
    each holding a design tree with work left
    When newest is asked
    Then it gives the one run"""
    repo = a_repository(tmp_path)
    branch_run(repo, NAME, a_tree(NAME), "2026-11-10T09:00:00")
    for branch, name in (("rn2-20261121-x", "20261121-x"), ("20261122-y", "20261122-y")):
        git(repo, "checkout", "-q", "-b", branch, "main")
        rn_files.write_json(
            os.path.join(repo, ".rn", name, "design-tree.json"), rn_files.walkthrough_tree(name)
        )
        dated_commit(repo, "A tree.", "2026-11-21T09:00:00")
    git(repo, "checkout", "-q", "main")
    assert newest(repo, host) == RunPlace(repo, NAME)


@pytest.mark.supports("test_a_pick_up_in_a_repository_whose_worktree_is_gone_makes_it_again")
def test_a_run_whose_worktree_is_gone_gets_it_again_on_its_local_branch(tmp_path: Any, host: Any):
    """Given a repository whose one run's worktree was removed, its local branch kept
    When newest and found are asked
    Then newest gives the run and makes nothing; found gives it, its worktree checked out on
    rn-<name> again at the branch's head, holding the committed design tree, and git shows nothing
    untracked in the user's own worktree"""
    repo = a_repository(tmp_path)
    branch_run(repo, NAME, a_tree(NAME), worktree=False)
    worktree = rn_files.worktree_of(repo, NAME)
    assert newest(repo, host) == RunPlace(repo, NAME)
    assert not os.path.exists(worktree)
    assert found(repo, host) == RunPlace(repo, NAME)
    assert git(worktree, "branch", "--show-current").strip() == f"rn-{NAME}"
    assert head(worktree) == head(repo, f"rn-{NAME}")
    assert rn_files.read_json(RunPlace(repo, NAME).tree) == a_tree(NAME)
    assert git(repo, "status", "--porcelain").strip() == ""


@pytest.mark.supports("test_a_pick_up_in_a_repository_whose_worktree_is_gone_makes_it_again")
def test_a_run_whose_worktree_folder_was_deleted_gets_it_again(tmp_path: Any, host: Any):
    """Given a repository whose one run's worktree folder was deleted, git still recording it
    When found is asked
    Then it gives the run, its worktree there again on rn-<name>"""
    repo = a_repository(tmp_path)
    branch_run(repo, NAME, a_tree(NAME))
    worktree = rn_files.worktree_of(repo, NAME)
    shutil.rmtree(worktree)
    assert found(repo, host) == RunPlace(repo, NAME)
    assert git(worktree, "branch", "--show-current").strip() == f"rn-{NAME}"


@pytest.mark.supports("test_a_pick_up_in_a_repository_whose_worktree_is_gone_makes_it_again")
def test_a_run_only_origin_holds_gets_its_worktree_on_a_branch_from_origins(
    tmp_path: Any, host: Any
):
    """Given a fresh clone of a remote that holds a run's branch, pushed, with no local branch of
    rn
    When found is asked in the clone
    Then it gives the run, its worktree on a new local branch rn-<name> at origin's head, tracking
    it, holding the committed design tree"""
    repo = a_repository(tmp_path)
    branch_run(repo, NAME, a_tree(NAME))
    git(repo, "push", "-q", "origin", f"rn-{NAME}")
    clone = cloned(tmp_path, str(tmp_path / "origin.git"))
    assert found(clone, host) == RunPlace(clone, NAME)
    worktree = rn_files.worktree_of(clone, NAME)
    assert head(worktree) == head(repo, f"rn-{NAME}")
    upstream = git(worktree, "rev-parse", "--abbrev-ref", "@{upstream}").strip()
    assert upstream == f"origin/rn-{NAME}"
    assert rn_files.read_json(RunPlace(clone, NAME).tree) == a_tree(NAME)


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_runs_newer_local_branch_decides_over_origins_older_one(tmp_path: Any, host: Any):
    """Given a run pushed with work left, whose local branch then made each deliverable done in a
    newer commit not pushed
    When newest is asked
    Then it gives None, as the run's newest branch has no work left"""
    repo = a_repository(tmp_path)
    folder = branch_run(repo, NAME, a_tree(NAME), "2026-11-20T09:00:00")
    git(repo, "push", "-q", "origin", f"rn-{NAME}")
    rn_files.write_json(os.path.join(folder, "design-tree.json"), a_tree(NAME, done=True))
    dated_commit(rn_files.worktree_of(repo, NAME), "Done.", "2026-11-21T09:00:00")
    assert newest(repo, host) is None


@pytest.mark.supports("test_a_pick_up_in_a_repository_whose_worktree_is_gone_makes_it_again")
def test_a_worktree_git_cant_make_is_cantrun_with_what_git_said(tmp_path: Any, host: Any):
    """Given a repository whose run's worktree was removed, and a file lying where the worktree
    goes
    When found is asked
    Then CantRun is raised with what git said"""
    repo = a_repository(tmp_path)
    branch_run(repo, NAME, a_tree(NAME), worktree=False)
    with open(rn_files.worktree_of(repo, NAME), "w", encoding="utf-8") as f:
        f.write("in the way\n")
    with pytest.raises(CantRun, match="git can't make the run's worktree again"):
        found(repo, host)


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_design_tree_that_isnt_json_is_refused_naming_the_branch_and_path(
    tmp_path: Any, host: Any
):
    """Given a repository with a run whose committed design tree isn't JSON
    When newest is asked
    Then Wrong is raised, naming the branch and the design tree's path"""
    repo = a_repository(tmp_path)
    folder = branch_run(repo, NAME, a_tree(NAME))
    write_files(folder, {"design-tree.json": "{ not json"})
    dated_commit(rn_files.worktree_of(repo, NAME), "Broken.", "2026-11-21T09:00:00")
    with pytest.raises(Wrong, match=f"refs/heads/rn-{NAME}:.rn/{NAME}/design-tree.json"):
        newest(repo, host)

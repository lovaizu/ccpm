"""The unit cases of repository/worktree.py: `new`, from main and from the branch that origin's
HEAD names rather than the one checked out, the goal open, info/exclude's line kept once, and each
refusal: a run of the name already there, a folder that isn't a repository, and origin's HEAD
naming no branch; `newest`, with no repository, several runs, newest by its last commit, a newer
run whose every deliverable is done or that holds no design tree passed over, a run's newer local
branch deciding over origin's, and the refusal of a design tree that isn't JSON; `found`, with the
run's worktree there, removed with its local branch kept, its folder deleted, a run that only
origin holds in a fresh clone, one that another clone pushed since the last fetch, one that GitHub
no longer holds beside an older local run, origin out of reach, and a worktree that git can't
make; `removed`, here and on GitHub, of a branch GitHub holds, has deleted since, or only nearly
matches, and of no pull request, the run's open one, or an earlier run's closed one; with git or
gh that can't ask GitHub or can't remove what it holds; and a worktree that git can't remove; and,
inside herdr and outside, `new`, `found` with the worktree gone, and `removed`, each with herdr
failing inside it."""

from __future__ import annotations

import os
import re
import shutil
from typing import Any

import pytest
import rn_files
from fault import CantRun, Missing, Wrong
from gh import gh_double
from herdr import herdr_double
from repo_files import git, write_files
from repository.place import RunPlace
from repository.worktree import Found, Gone, found, new, newest, removed
from rn_runs import NAME, branch_run, dated_commit, head

GOAL = rn_files.GOAL
PRACTICE = rn_files.practice("design-tree")
CONTEXT = rn_files.context()


def started_tree(name: str) -> dict[str, Any]:
    """The tree that a run starts from, as tree.form.started's contract names it: the goal open,
    the plan as its one deliverable, unnamed, open, each condition not good, and no work."""
    return rn_files.started(name)


def a_repository(tmp_path: Any, branch: str = "main") -> str:
    """invoicer's repository with a remote origin whose default branch is the branch given."""
    repo = rn_files.repository(str(tmp_path / "invoicer"), branch=branch)
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    return repo


def test_a_new_run_has_its_branch_from_main_checked_out_with_the_tree_uncommitted(
    tmp_path: Any, host: Any
):
    """Given invoicer's repository on main with a remote, the user on main
    When new makes the run 20261120-invoices
    Then it gives the run; the worktree has rn-20261120-invoices checked out at main's head,
    holding the started tree at .rn/20261120-invoices/design-tree.json, uncommitted; and the
    user's branch, head, and files are as they were"""
    repo = a_repository(tmp_path)
    before = head(repo, "main")
    run = RunPlace(repo, NAME)
    assert new(run, CONTEXT, PRACTICE, host) == run
    worktree = rn_files.worktree_of(repo, NAME)
    assert git(worktree, "branch", "--show-current").strip() == f"rn-{NAME}"
    assert head(worktree) == before
    tree_path = os.path.join(rn_files.folder_of(repo, NAME), "design-tree.json")
    assert rn_files.read_json(tree_path) == started_tree(NAME)
    assert git(worktree, "status", "--porcelain").split() == ["??", ".rn/"]
    assert git(repo, "branch", "--show-current").strip() == "main"
    assert head(repo) == before
    assert git(repo, "status", "--porcelain", "--untracked-files=no").strip() == ""


def test_a_second_run_keeps_the_one_line_of_info_exclude(tmp_path: Any, host: Any):
    """Given invoicer's repository in which new made the run 20261120-invoices
    When new makes the run 20261121-receipts
    Then the repository's info/exclude holds the line that keeps the runs' worktrees out of the
    user's untracked files once"""
    repo = a_repository(tmp_path)
    new(RunPlace(repo, NAME), CONTEXT, PRACTICE, host)
    new(RunPlace(repo, "20261121-receipts"), CONTEXT, PRACTICE, host)
    with open(os.path.join(repo, ".git", "info", "exclude"), encoding="utf-8") as f:
        assert f.read().splitlines().count("/.claude/worktrees/") == 1


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
    new(RunPlace(repo, NAME), CONTEXT, PRACTICE, host)
    assert head(rn_files.worktree_of(repo, NAME)) == trunk
    assert head(repo, "main") == main
    assert git(repo, "branch", "--show-current").strip() == "main"


def test_a_repository_whose_origin_head_names_no_branch_is_missing_its_default(
    tmp_path: Any, host: Any
):
    """Given invoicer's repository on main with a commit, and a remote origin whose HEAD is
    unset
    When new makes the run
    Then Missing is raised, and no worktree and no branch rn-<name> is made"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    git(repo, "remote", "set-head", "origin", "--delete")
    with pytest.raises(Missing):
        new(RunPlace(repo, NAME), CONTEXT, PRACTICE, host)
    assert not os.path.exists(rn_files.worktree_of(repo, NAME))
    assert git(repo, "branch", "--list", f"rn-{NAME}").strip() == ""


def test_a_run_of_the_name_already_there_is_refused_and_left_as_it_was(tmp_path: Any, host: Any):
    """Given invoicer's repository whose run 20261120-invoices was made
    When new makes a run of the same name again
    Then Wrong is raised naming the run, and its design tree is as it was"""
    repo = a_repository(tmp_path)
    run = RunPlace(repo, NAME)
    new(run, CONTEXT, PRACTICE, host)
    tree_path = os.path.join(rn_files.folder_of(repo, NAME), "design-tree.json")
    before = rn_files.read_json(tree_path)
    with pytest.raises(Wrong, match=NAME):
        new(run, CONTEXT, PRACTICE, host)
    assert rn_files.read_json(tree_path) == before


def test_a_folder_that_isnt_a_git_repository_is_missing_one(tmp_path: Any, host: Any):
    """Given a folder of invoicer's files with no git
    When new makes a run there
    Then Missing is raised, and no worktree is made"""
    folder = os.path.realpath(str(tmp_path / "plain"))
    write_files(folder, {"README.md": "# plain\n"})
    with pytest.raises(Missing):
        new(RunPlace(folder, NAME), CONTEXT, PRACTICE, host)
    assert not os.path.exists(rn_files.worktree_of(folder, NAME))


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


def test_a_folder_that_isnt_a_repository_has_no_run(tmp_path: Any, host: Any):
    """Given a folder that isn't a git repository
    When newest is asked
    Then it gives None"""
    assert newest(os.path.realpath(str(tmp_path)), host) is None


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
    assert found(repo, host) == Found(RunPlace(repo, NAME), None)
    with open(note, encoding="utf-8") as f:
        assert f.read() == "kept\n"


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
    assert found(repo, host) == Found(RunPlace(repo, NAME), None)
    assert git(worktree, "branch", "--show-current").strip() == f"rn-{NAME}"
    assert head(worktree) == head(repo, f"rn-{NAME}")
    assert rn_files.read_json(RunPlace(repo, NAME).tree) == a_tree(NAME)
    assert git(repo, "status", "--porcelain").strip() == ""


def test_a_run_whose_worktree_folder_was_deleted_gets_it_again(tmp_path: Any, host: Any):
    """Given a repository whose one run's worktree folder was deleted, git still recording it
    When found is asked
    Then it gives the run, its worktree there again on rn-<name>"""
    repo = a_repository(tmp_path)
    branch_run(repo, NAME, a_tree(NAME))
    worktree = rn_files.worktree_of(repo, NAME)
    shutil.rmtree(worktree)
    assert found(repo, host) == Found(RunPlace(repo, NAME), None)
    assert git(worktree, "branch", "--show-current").strip() == f"rn-{NAME}"


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
    assert found(clone, host) == Found(RunPlace(clone, NAME), None)
    worktree = rn_files.worktree_of(clone, NAME)
    assert head(worktree) == head(repo, f"rn-{NAME}")
    upstream = git(worktree, "rev-parse", "--abbrev-ref", "@{upstream}").strip()
    assert upstream == f"origin/rn-{NAME}"
    assert rn_files.read_json(RunPlace(clone, NAME).tree) == a_tree(NAME)


def gone_from_github(repo: str, name: str, tree: dict[str, Any], when: str) -> None:
    """Makes the run of the name, pushed with its design tree at the time given, then cancelled on
    another machine: its branch deleted on origin and here, its worktree removed, and only the
    repository's ref of origin's branch left from the push."""
    branch_run(repo, name, tree, when, worktree=False)
    git(repo, "push", "-q", "origin", f"rn-{name}")
    git(str(os.path.dirname(repo)), "--git-dir", "origin.git", "branch", "-q", "-D", f"rn-{name}")
    git(repo, "branch", "-q", "-D", f"rn-{name}")


def test_a_run_github_no_longer_holds_is_never_picked_up(tmp_path: Any, host: Any):
    """Given a run with work left that was cancelled on another machine, whose only trace here is
    the ref of origin's branch, newer than any other, beside an older run with work left on this
    machine
    When found is asked
    Then it gives the older local run, and nothing it couldn't check; and the ref of the cancelled
    run's branch is gone"""
    repo = a_repository(tmp_path)
    branch_run(repo, "20261119-older", a_tree("20261119-older"), "2026-11-19T09:00:00")
    gone_from_github(repo, NAME, a_tree(NAME), "2026-11-21T09:00:00")
    assert found(repo, host) == Found(RunPlace(repo, "20261119-older"), None)
    assert git(repo, "for-each-ref", f"refs/remotes/origin/rn-{NAME}").strip() == ""


def test_a_run_pushed_from_another_machine_since_the_last_fetch_is_picked_up(
    tmp_path: Any, host: Any
):
    """Given a repository, and a run with work left that another clone pushed to origin since
    the repository last fetched
    When found is asked in the repository
    Then it gives that run, its worktree made on a branch from origin's, and nothing it couldn't
    check"""
    repo = a_repository(tmp_path)
    other = cloned(tmp_path, str(tmp_path / "origin.git"))
    git(other, "checkout", "-q", "main")
    git(other, "config", "user.email", "rn@example.com")
    git(other, "config", "user.name", "rn")
    branch_run(other, NAME, a_tree(NAME))
    git(other, "push", "-q", "origin", f"rn-{NAME}")
    assert found(repo, host) == Found(RunPlace(repo, NAME), None)
    assert head(rn_files.worktree_of(repo, NAME)) == head(other, f"rn-{NAME}")


def test_with_github_out_of_reach_only_this_machines_runs_are_picked_up(tmp_path: Any, host: Any):
    """Given a repository whose origin git can't reach, with the ref of origin's branch of a run
    with work left, newer than any other, and an older run with work left on this machine
    When found is asked
    Then it gives the older local run, and that it couldn't check the runs on GitHub, with what git
    said, as one line"""
    repo = a_repository(tmp_path)
    branch_run(repo, "20261119-older", a_tree("20261119-older"), "2026-11-19T09:00:00")
    branch_run(repo, NAME, a_tree(NAME), "2026-11-21T09:00:00", worktree=False)
    git(repo, "push", "-q", "origin", f"rn-{NAME}")
    git(repo, "branch", "-q", "-D", f"rn-{NAME}")
    git(repo, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    given = found(repo, host)
    assert given.run == RunPlace(repo, "20261119-older")
    gone = re.escape(str(tmp_path / "gone.git"))
    assert given.unchecked is not None
    assert re.fullmatch(
        f"the runs on GitHub, as git can't ask origin: fatal: '{gone}' does not appear to be a git"
        " repository fatal: Could not read from remote repository. .*exists[.]",
        given.unchecked,
    ), given.unchecked


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


def test_a_worktree_git_cant_make_is_cantrun_with_what_git_said(tmp_path: Any, host: Any):
    """Given a repository whose run's worktree was removed, and a file lying where the worktree
    goes
    When found is asked
    Then CantRun is raised with what git said"""
    repo = a_repository(tmp_path)
    branch_run(repo, NAME, a_tree(NAME), worktree=False)
    with open(rn_files.worktree_of(repo, NAME), "w", encoding="utf-8") as f:
        f.write("in the way\n")
    with pytest.raises(CantRun, match="git can't make the run's worktree again: .*already exists"):
        found(repo, host)


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


# Inside herdr and outside


def herdr_commands(host: Any) -> list[list[str]]:
    """Each herdr command that the double of herdr was asked, by its words."""
    return [argv for argv, _ in host.asked]


def test_a_new_run_inside_herdr_has_its_worktree_made_by_herdr_from_mains_commit(
    tmp_path: Any, host: Any, monkeypatch: pytest.MonkeyPatch
):
    """Given invoicer's repository on main with a remote, inside herdr, `HERDR_ENV` 1
    When new makes the run
    Then herdr was asked, in the repository, to create the worktree on rn-<name> from the commit
    of origin's main at the run's worktree, keeping the focus where it is; the worktree has
    rn-<name> checked out at main's head with no upstream, holding the started tree; and git made
    no worktree itself"""
    monkeypatch.setenv("HERDR_ENV", "1")
    herdr = herdr_double.host(host)
    repo = a_repository(tmp_path)
    worktree = rn_files.worktree_of(repo, NAME)
    new(RunPlace(repo, NAME), CONTEXT, PRACTICE, herdr)
    create = ["herdr", "worktree", "create", "--cwd", repo, "--branch", f"rn-{NAME}"]
    rest = ["--base", head(repo, "main"), "--path", worktree, "--no-focus"]
    assert herdr.asked == [([*create, *rest], repo)]
    assert git(worktree, "branch", "--show-current").strip() == f"rn-{NAME}"
    assert head(worktree) == head(repo, "main")
    assert git(worktree, "for-each-ref", "--format=%(upstream)", f"refs/heads/rn-{NAME}") == "\n"
    assert rn_files.read_json(RunPlace(repo, NAME).tree) == started_tree(NAME)
    assert not [argv for argv, _ in host.ran if argv[:3] == ["git", "worktree", "add"]]


def test_a_new_run_outside_herdr_has_its_worktree_made_by_git(
    tmp_path: Any, host: Any, monkeypatch: pytest.MonkeyPatch
):
    """Given invoicer's repository on main with a remote, outside herdr: `HERDR_ENV` 0
    When new makes the run
    Then herdr was asked nothing, and git made the run's worktree on rn-<name>"""
    monkeypatch.setenv("HERDR_ENV", "0")
    herdr = herdr_double.host(host)
    repo = a_repository(tmp_path)
    new(RunPlace(repo, NAME), CONTEXT, PRACTICE, herdr)
    assert herdr_commands(herdr) == []
    worktree = rn_files.worktree_of(repo, NAME)
    assert git(worktree, "branch", "--show-current").strip() == f"rn-{NAME}"


def test_a_new_run_inside_herdr_that_herdr_fails_is_cantrun_with_what_herdr_said(
    tmp_path: Any, host: Any, monkeypatch: pytest.MonkeyPatch
):
    """Given invoicer's repository on main with a remote, inside herdr, whose server isn't running
    When new makes the run
    Then CantRun is raised with what herdr said, and no worktree, branch, or design tree is made"""
    monkeypatch.setenv("HERDR_ENV", "1")
    repo = a_repository(tmp_path)
    with pytest.raises(CantRun, match="herdr can't make the run's worktree: .*server_not_running"):
        new(RunPlace(repo, NAME), CONTEXT, PRACTICE, herdr_double.host(host, running=False))
    assert not os.path.exists(rn_files.worktree_of(repo, NAME))
    assert git(repo, "branch", "--list", f"rn-{NAME}").strip() == ""


def test_a_pick_up_inside_herdr_has_git_make_the_worktree_again_and_herdr_open_it(
    tmp_path: Any, host: Any, monkeypatch: pytest.MonkeyPatch
):
    """Given a repository whose one run's worktree was removed, its local branch kept, inside
    herdr
    When found is asked
    Then it gives the run, its worktree checked out on rn-<name> again, and herdr was asked, in the
    repository, to open the worktree at its path, keeping the focus where it is"""
    monkeypatch.setenv("HERDR_ENV", "1")
    herdr = herdr_double.host(host)
    repo = a_repository(tmp_path)
    branch_run(repo, NAME, a_tree(NAME), worktree=False)
    worktree = rn_files.worktree_of(repo, NAME)
    assert found(repo, herdr) == Found(RunPlace(repo, NAME), None)
    assert git(worktree, "branch", "--show-current").strip() == f"rn-{NAME}"
    opened = ["herdr", "worktree", "open", "--cwd", repo, "--path", worktree, "--no-focus"]
    assert herdr.asked == [(opened, repo)]


def test_a_pick_up_inside_herdr_that_herdr_fails_is_cantrun_with_what_herdr_said(
    tmp_path: Any, host: Any, monkeypatch: pytest.MonkeyPatch
):
    """Given a repository whose one run's worktree was removed, inside herdr, whose server isn't
    running
    When found is asked
    Then CantRun is raised with what herdr said"""
    monkeypatch.setenv("HERDR_ENV", "1")
    repo = a_repository(tmp_path)
    branch_run(repo, NAME, a_tree(NAME), worktree=False)
    with pytest.raises(CantRun, match="herdr can't open the run's worktree: .*server_not_running"):
        found(repo, herdr_double.host(host, running=False))


# A run cancelled

PR = "https://github.com/lovaizu/invoicer/pull/38"
# The pull request of an earlier run of the same branch's name, closed or merged since.
EARLIER = "https://github.com/lovaizu/invoicer/pull/37"
# The ref of origin's branch of the run, as the repository's last fetch or push left it.
TRACKED = f"refs/remotes/origin/rn-{NAME}"


def cancelled_run(repo: str, gh: str, branch: str = "never", pr: str = "none") -> RunPlace:
    """The run of the repository with its worktree here and a change in it not committed. Its
    branch on GitHub, as `branch` says: `never` pushed; `held` by origin; `gone`, pushed and
    since deleted on origin, its ref of origin's branch left here; or `near`, never pushed, while
    origin holds branches whose names nearly match. Its pull request, as `pr` says: `none`;
    `open`, named in the design tree; or `closed` or `merged`, an earlier run's of the same
    branch's name, as gh's double in the folder `gh` holds it."""
    tree = a_tree(NAME)
    if pr == "open":
        tree["context"]["pr"] = PR
        gh_double.opened(gh, PR)
    elif pr != "none":
        gh_double.earlier(gh, EARLIER, pr.upper())
    branch_run(repo, NAME, tree)
    worktree = rn_files.worktree_of(repo, NAME)
    write_files(worktree, {"invoicer/lines.py": "def parse_lines(text):\n    return []\n"})
    if branch in ("held", "gone"):
        git(worktree, "push", "-q", "-u", "origin", f"rn-{NAME}")
    if branch == "gone":
        git(remote(repo), "branch", "-q", "-D", f"rn-{NAME}")
    if branch == "near":
        git(worktree, "push", "-q", "origin", f"HEAD:refs/heads/x/rn-{NAME}")
        git(worktree, "push", "-q", "origin", f"HEAD:refs/heads/rn-{NAME}-2")
    return RunPlace(repo, NAME)


def remote(repo: str) -> str:
    """The folder of the repository's remote origin."""
    return git(repo, "remote", "get-url", "origin").strip()


def tracked(repo: str) -> bool:
    """Whether the repository holds its ref of origin's branch of the run."""
    return git(repo, "for-each-ref", TRACKED).strip() != ""


def branches(repo: str) -> list[str]:
    """Each branch that origin holds, by its ref and commit."""
    return git(remote(repo), "for-each-ref", "--format=%(refname) %(objectname)").splitlines()


@pytest.mark.parametrize(
    ("branch", "pr"),
    [("near", "closed"), ("held", "open"), ("gone", "none")],
)
def test_a_cancelled_run_is_removed_here_and_on_github(
    tmp_path: Any, host: Any, gh_state: str, branch: str, pr: str
):
    """Given a run whose worktree holds a change not committed, outside herdr: one whose branch's
    name only nearly matches branches that GitHub holds, and GitHub holds an earlier run's closed
    pull request of; one whose branch and open pull request GitHub holds; or one whose branch
    GitHub held and has since deleted, its ref of origin's branch left here, with no pull
    request
    When removed is asked
    Then it gives as removed on GitHub the open pull request where GitHub held one, then origin's
    branch where GitHub held it, and nothing that it couldn't remove; the worktree, the local
    branch rn-<name>, and the ref of origin's branch are gone; origin holds no branch rn-<name>,
    and each other branch of origin is as it was; no pull request of the branch is open; and the
    user's branch and files are as they were"""
    repo = a_repository(tmp_path)
    run = cancelled_run(repo, gh_state, branch, pr)
    before = head(repo, "main")
    others = [each for each in branches(repo) if not each.startswith(f"refs/heads/rn-{NAME} ")]
    expected = ([PR] if pr == "open" else []) + ([f"origin/rn-{NAME}"] if branch == "held" else [])
    assert removed(run, host) == Gone(expected, [])
    assert not os.path.exists(run.worktree)
    assert git(repo, "branch", "--list", f"rn-{NAME}").strip() == ""
    assert not tracked(repo)
    assert branches(repo) == others
    assert gh_double.state(gh_state)["pull_request"] is None
    assert git(repo, "branch", "--show-current").strip() == "main"
    assert head(repo) == before


def git_said(tmp_path: Any) -> str:
    """The pattern of what git says, as one line, where origin's folder is gone."""
    gone = re.escape(str(tmp_path / "gone.git"))
    return (
        f"fatal: '{gone}' does not appear to be a git repository fatal: Could not read from remote"
        " repository. .*exists[.]"
    )


@pytest.mark.parametrize("failing", ["git-unreached", "git-refused", "gh-unreached", "gh-close"])
def test_a_cancelled_run_names_what_it_couldnt_remove_on_github_and_why(
    tmp_path: Any, host: Any, gh_state: str, failing: str
):
    """Given a run whose worktree is here, outside herdr, whose branch GitHub holds with its open
    pull request, and git that can't reach origin, or that origin refuses to delete a branch for,
    or gh that can't reach GitHub, or loses GitHub once it read the pull request
    When removed is asked
    Then it gives as removed on GitHub what it could remove, and, for what it couldn't, what that
    is and what git or gh said, as one line; the worktree and the local branch rn-<name> are
    gone; and the ref of origin's branch stays where git couldn't remove the branch"""
    repo = a_repository(tmp_path)
    run = cancelled_run(repo, gh_state, "held", "open")
    if failing == "git-unreached":
        git(repo, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    elif failing == "git-refused":
        git(remote(repo), "config", "receive.denyDeletes", "true")
    elif failing == "gh-unreached":
        gh_double.unreached(gh_state)
    else:
        gh_double.closes_unreached(gh_state)
    gone = removed(run, host)
    branch = f"the branch rn-{NAME} on GitHub, as git can't "
    if failing.startswith("git"):
        assert gone.removed == [PR]
        [said] = gone.kept
        why = (
            f"ask origin: {git_said(tmp_path)}"
            if failing == "git-unreached"
            else "delete it: .*deletion prohibited.*"
        )
        assert re.fullmatch(re.escape(branch) + why, said), said
        assert tracked(repo)
    else:
        record = {
            "gh-unreached": (gh_double.PR_VIEW, "gh pr view can't reach GitHub"),
            "gh-close": (gh_double.PR_CLOSE, "gh pr close can't reach GitHub"),
        }[failing]
        said = gh_double.line(*record)["stderr"].strip()
        what = (
            f"the pull request {PR} on GitHub, as gh can't close it: {said}"
            if failing == "gh-close"
            else f"the pull request of rn-{NAME} on GitHub, as gh can't ask GitHub: {said}"
        )
        assert gone == Gone([f"origin/rn-{NAME}"], [what])
        assert not tracked(repo)
    assert not os.path.exists(run.worktree)
    assert git(repo, "branch", "--list", f"rn-{NAME}").strip() == ""


def test_a_worktree_git_cant_remove_is_cantrun_and_keeps_the_branch(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose worktree is locked, outside herdr
    When removed is asked
    Then CantRun is raised with what git said, and the worktree and the branch rn-<name> stay"""
    repo = a_repository(tmp_path)
    run = cancelled_run(repo, gh_state)
    git(repo, "worktree", "lock", run.worktree)
    with pytest.raises(CantRun, match="git can't remove the run's worktree: .*locked"):
        removed(run, host)
    assert os.path.isdir(run.worktree)
    assert git(repo, "branch", "--list", f"rn-{NAME}").strip() != ""


def test_a_cancelled_run_inside_herdr_has_herdr_remove_its_worktree(
    tmp_path: Any, host: Any, gh_state: str, monkeypatch: pytest.MonkeyPatch
):
    """Given a run whose worktree holds a change not committed, made by git, inside herdr
    When removed is asked
    Then herdr was asked, in the repository, to open the worktree, keeping the focus where it is,
    then to remove the worktree of the workspace it gave, with its change; the worktree and the
    local branch rn-<name> are gone; and git removed no worktree itself"""
    monkeypatch.setenv("HERDR_ENV", "1")
    herdr = herdr_double.host(host)
    repo = a_repository(tmp_path)
    run = cancelled_run(repo, gh_state)
    before = len(herdr.asked)
    assert removed(run, herdr) == Gone([], [])
    opened = ["herdr", "worktree", "open", "--cwd", repo, "--path", run.worktree, "--no-focus"]
    remove = ["herdr", "worktree", "remove", "--workspace", "w1J", "--force"]
    assert herdr.asked[before:] == [(opened, repo), (remove, repo)]
    assert not os.path.exists(run.worktree)
    assert git(repo, "branch", "--list", f"rn-{NAME}").strip() == ""
    assert not [argv for argv, _ in host.ran if argv[:3] == ["git", "worktree", "remove"]]


def test_a_cancelled_run_inside_herdr_that_herdr_fails_is_cantrun_and_keeps_the_run(
    tmp_path: Any, host: Any, gh_state: str, monkeypatch: pytest.MonkeyPatch
):
    """Given a run whose worktree is here, inside herdr, whose server isn't running
    When removed is asked
    Then CantRun is raised with what herdr said, and the worktree and the branch rn-<name> stay"""
    monkeypatch.setenv("HERDR_ENV", "1")
    repo = a_repository(tmp_path)
    run = cancelled_run(repo, gh_state)
    with pytest.raises(CantRun, match="herdr can't open the run's worktree: .*server_not_running"):
        removed(run, herdr_double.host(host, running=False))
    assert os.path.isdir(run.worktree)
    assert git(repo, "branch", "--list", f"rn-{NAME}").strip() != ""

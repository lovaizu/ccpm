"""The unit cases of repository/push.py: `commit`, of a path alone with the rest of the index left
as it was, and of a file removed beside it, and each refusal: a path outside the worktree, a file
to remove that git doesn't hold, no change, and a commit check that
refuses; `pause`, which commits each change and pushes with its upstream set, and each refusal: no
origin, a push refused for want of a permission, and a remote that isn't there; `put_up`, which asks
gh's login first, its first time opening the pull request as a draft titled by the goal's first
sentence, its body naming the issues and naming none, the pull request's URL written into the tree,
an open pull request's URL written where the tree has none, its own opened beside an earlier one
closed, no commit where nothing changed, the link it gives of each path of the deliverable, a
file's and a folder's, and none for a node of no file, and each refusal: gh with no login and the
goal open, each before any commit or push, a deliverable the tree lacks, and a path of the
deliverable that the commit doesn't hold; `diff`, which commits and pushes each change and gives
the whole diff, a stray file removed; and `ci`, which waits for the checks to start, each passed,
one cancelled or timed out, one failed alone or beside cancelled ones, gh that can't give the pull
request or its checks, and no check started within 120 seconds."""

from __future__ import annotations

import json
import os
import stat
from typing import Any

import pytest
import rn_files
from fault import CantRun, Missing, Wrong
from gh import gh_double
from repo_files import git
from repository.place import RunPlace
from repository.push import ci, commit, diff, pause, put_up
from rn_runs import NAME, changed, committed_files, head, hook, made_run, subject

URL = "http://github.com/owner/repo/pull/1"
# The repository's page on GitHub, as the pull request's URL gives it.
REPOSITORY = "http://github.com/owner/repo"
# The first sentence of the walkthrough's goal, which titles the pull request.
FIRST = (
    "The accounting team prints each invoice themselves from the lines they keep in a"
    " spreadsheet, without asking a developer."
)


def worktree(run: RunPlace) -> str:
    """The run's worktree, as the architecture's Directory structure places it."""
    return rn_files.worktree_of(run.repository, run.name)


def tree_file(run: RunPlace) -> str:
    """The run's design tree from its worktree's top."""
    return f".rn/{run.name}/design-tree.json"


def origin(tmp_path: Any) -> str:
    """The run's remote."""
    return str(tmp_path / "origin.git")


# commit


def test_a_commit_holds_its_paths_alone_and_leaves_the_rest_of_the_index(tmp_path: Any, host: Any):
    """Given a run whose design tree and the command are changed, neither staged, and whose guide
    is changed and staged
    When commit is given the design tree with a message of two lines
    Then it gives the new head of the run's branch, whose message is the given one word for word,
    and which holds the design tree alone; the guide stays staged, and the command unstaged"""
    run = made_run(str(tmp_path))
    changed(run, {tree_file(run): "{}\n", rn_files.COMMAND: "print()\n", rn_files.GUIDE: "# G\n"})
    git(worktree(run), "add", rn_files.GUIDE)
    message = "The README names its people.\n\nThe guide is for the accounting team."
    given = commit(run, [tree_file(run)], message, host)
    assert given == head(worktree(run), f"rn-{run.name}")
    assert subject(worktree(run)) == message
    assert committed_files(worktree(run)) == [tree_file(run)]
    assert git(worktree(run), "status", "--porcelain").split() == [
        "A",
        rn_files.GUIDE,
        "??",
        rn_files.COMMAND,
    ]


def test_a_commit_removes_each_file_to_remove_beside_its_paths(tmp_path: Any, host: Any):
    """Given a run whose design tree is changed, and whose branch holds invoicer/lines.py
    When commit is given the design tree, and invoicer/lines.py to remove
    Then the commit holds the design tree and the removal of invoicer/lines.py, which is gone from
    the worktree"""
    run = made_run(str(tmp_path))
    changed(run, {tree_file(run): "{}\n"})
    commit(run, [tree_file(run)], "The tree.", host, removed=["invoicer/lines.py"])
    assert sorted(committed_files(worktree(run))) == sorted([tree_file(run), "invoicer/lines.py"])
    status = git(worktree(run), "show", "--name-status", "--format=", "HEAD").splitlines()
    assert "D\tinvoicer/lines.py" in status
    assert not os.path.exists(os.path.join(worktree(run), "invoicer", "lines.py"))


def test_a_commit_removing_a_file_git_doesnt_hold_is_refused(tmp_path: Any, host: Any):
    """Given a run whose design tree is changed, and no file invoicer/cli.py
    When commit is given the design tree, and invoicer/cli.py to remove
    Then Wrong is raised naming invoicer/cli.py, and the branch's head is as it was"""
    run = made_run(str(tmp_path))
    changed(run, {tree_file(run): "{}\n"})
    before = head(worktree(run))
    with pytest.raises(Wrong, match="invoicer/cli.py: git holds no such file"):
        commit(run, [tree_file(run)], "The tree.", host, removed=["invoicer/cli.py"])
    assert head(worktree(run)) == before


def test_a_commit_of_a_path_outside_the_worktree_is_refused(tmp_path: Any, host: Any):
    """Given a run whose design tree is changed
    When commit is given it and a path outside the worktree
    Then Wrong is raised, naming the path, and the branch's head is as it was"""
    run = made_run(str(tmp_path))
    changed(run, {tree_file(run): "{}\n"})
    before = head(worktree(run))
    with pytest.raises(Wrong, match=r"\.\./outside\.txt"):
        commit(run, [tree_file(run), "../outside.txt"], "The tree.", host)
    assert head(worktree(run)) == before


def test_a_commit_with_no_change_in_any_path_is_refused(tmp_path: Any, host: Any):
    """Given a run with nothing changed
    When commit is given the design tree
    Then Wrong is raised, naming it, and the branch's head is as it was"""
    run = made_run(str(tmp_path))
    before = head(worktree(run))
    with pytest.raises(Wrong, match="design-tree.json"):
        commit(run, [tree_file(run)], "The tree.", host)
    assert head(worktree(run)) == before


def test_a_commit_that_a_commit_check_refuses_cant_run(tmp_path: Any, host: Any):
    """Given a run whose design tree is changed, in a repository whose pre-commit hook refuses each
    commit saying `tree: no`
    When commit is given the design tree
    Then CantRun is raised with what the hook said, and the branch's head is as it was"""
    run = made_run(str(tmp_path))
    hook(run.repository, "echo 'tree: no'\nexit 1\n")
    changed(run, {tree_file(run): "{}\n"})
    before = head(worktree(run))
    with pytest.raises(CantRun, match="tree: no"):
        commit(run, [tree_file(run)], "The tree.", host)
    assert head(worktree(run)) == before


# pause


def test_a_pause_commits_each_change_and_pushes_the_branch_with_its_upstream(
    tmp_path: Any, host: Any
):
    """Given a run whose design tree is changed and whose command is new, not committed
    When pause is given the run
    Then it gives the hash that origin's rn-<name> now holds, a commit `rn: paused <name>` holding
    both files; the branch's upstream is origin's, and nothing is left uncommitted"""
    run = made_run(str(tmp_path))
    changed(run, {tree_file(run): "{}\n", rn_files.COMMAND: "print()\n"})
    given = pause(run, host)
    branch = f"rn-{run.name}"
    assert given == head(origin(tmp_path), branch) == head(worktree(run))
    assert subject(worktree(run)) == f"rn: paused {run.name}"
    assert sorted(committed_files(worktree(run))) == sorted([tree_file(run), rn_files.COMMAND])
    upstream = git(worktree(run), "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}").strip()
    assert upstream == f"origin/{branch}"
    assert git(worktree(run), "status", "--porcelain").strip() == ""


def test_a_pause_with_no_origin_is_missing_one(tmp_path: Any, host: Any):
    """Given a run whose repository has no remote
    When pause is given the run
    Then Missing is raised"""
    run = made_run(str(tmp_path), origin=False)
    changed(run, {tree_file(run): "{}\n"})
    with pytest.raises(Missing):
        pause(run, host)


def test_a_pause_whose_push_is_refused_for_want_of_a_permission_is_missing_one(
    tmp_path: Any, host: Any
):
    """Given a run whose remote's files may not be written
    When pause is given the run
    Then Missing is raised, with what git said of the permission"""
    run = made_run(str(tmp_path))
    changed(run, {tree_file(run): "{}\n"})
    for folder, _, files in os.walk(origin(tmp_path)):
        for each in [folder, *(os.path.join(folder, f) for f in files)]:
            os.chmod(each, os.stat(each).st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    try:
        with pytest.raises(Missing, match=r"(?s)a permission: .*\[remote rejected\]"):
            pause(run, host)
    finally:
        for folder, _, _ in os.walk(origin(tmp_path)):
            os.chmod(folder, os.stat(folder).st_mode | stat.S_IWUSR)


def test_a_pause_to_a_remote_that_isnt_there_cant_run(tmp_path: Any, host: Any):
    """Given a run whose remote origin names a folder that doesn't exist
    When pause is given the run
    Then CantRun is raised, with what git said"""
    run = made_run(str(tmp_path), origin=False)
    git(run.repository, "remote", "add", "origin", str(tmp_path / "gone.git"))
    with pytest.raises(CantRun, match="push the run's work: .*does not appear to be a git repo"):
        pause(run, host)


# put_up


def title(argv: list[str]) -> str | None:
    """The title that a `gh pr create` names, as `--title <title>`, `--title=<title>`, or
    `-t <title>`."""
    for place, word in enumerate(argv):
        if word in ("--title", "-t") and place + 1 < len(argv):
            return argv[place + 1]
        if word.startswith("--title="):
            return word[len("--title=") :]
    return None


def body(argv: list[str]) -> str | None:
    """The body that a `gh pr create` names, as `--body <body>`, `--body=<body>`, or
    `-b <body>`."""
    for place, word in enumerate(argv):
        if word in ("--body", "-b") and place + 1 < len(argv):
            return argv[place + 1]
        if word.startswith("--body="):
            return word[len("--body=") :]
    return None


def with_command(run: RunPlace) -> RunPlace:
    """The run, with the command written in its worktree, as its generator leaves it."""
    changed(run, {rn_files.COMMAND: "print()\n"})
    return run


def created(gh_state: str) -> list[list[str]]:
    """Each `gh pr create` that the double was asked."""
    return [each for each in gh_double.state(gh_state)["asked"] if each[1:3] == ["pr", "create"]]


def test_a_first_put_up_pushes_and_opens_the_pull_request_titled_by_the_goal(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose plan is open and whose design tree is changed, with no pull request, its
    goal of two sentences
    When put_up is given the plan
    Then it gives no link, as the plan's file is rn's own; gh was asked its login before anything
    else; the change is committed as `rn: <plan's name>` and pushed to origin's rn-<name>; and gh
    was asked once to open a pull request, as a draft, titled by the goal's first sentence alone"""
    design_tree = rn_files.walkthrough_tree(NAME, plan_done=False)
    run = made_run(str(tmp_path), design_tree=design_tree)
    changed(run, {rn_files.GUIDE: "# Guide\n"})
    assert put_up(run, rn_files.plan_path(NAME), host) == []
    assert gh_double.state(gh_state)["asked"][0][:3] == ["gh", "auth", "status"]
    assert subject(worktree(run), "HEAD~1") == f"rn: {rn_files.GOAL}"
    assert committed_files(worktree(run), "HEAD~1") == [rn_files.GUIDE]
    assert head(origin(tmp_path), f"rn-{NAME}") == head(worktree(run))
    assert [title(each) for each in created(gh_state)] == [FIRST]
    assert ["--draft" in each for each in created(gh_state)] == [True]


def test_a_first_put_ups_body_names_each_issue_it_closes_then_each_it_refers_to(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose tree's context names issues 12 and 3 to close and 8 to refer to, with no
    pull request
    When put_up is given the command
    Then gh was asked once to open a pull request whose body is the goal, a blank line, then
    `Closes #12`, `Closes #3`, and `Refs #8`, one per line"""
    design_tree = rn_files.walkthrough_tree(NAME)
    design_tree["context"] = rn_files.context(closes=[12, 3], refs=[8])
    run = with_command(made_run(str(tmp_path), design_tree=design_tree))
    put_up(run, rn_files.COMMAND, host)
    assert [body(each) for each in created(gh_state)] == [
        f"{rn_files.GOAL}\n\nCloses #12\nCloses #3\nRefs #8"
    ]


def test_a_first_put_ups_body_of_a_run_with_no_issue_is_the_goal_alone(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose tree's context names no issue, with no pull request
    When put_up is given the command
    Then gh was asked once to open a pull request whose body is the goal alone"""
    run = with_command(made_run(str(tmp_path)))
    put_up(run, rn_files.COMMAND, host)
    assert [body(each) for each in created(gh_state)] == [rn_files.GOAL]


def test_a_first_put_up_writes_the_pull_requests_url_into_the_tree_and_pushes_it(
    tmp_path: Any, host: Any
):
    """Given a run whose tree's context holds no pull request, with none open
    When put_up is given the command
    Then the tree's context holds the pull request's URL, committed alone as
    `rn: the pull request of <name>` and pushed to origin's rn-<name>, with nothing left
    uncommitted"""
    run = with_command(made_run(str(tmp_path)))
    put_up(run, rn_files.COMMAND, host)
    tree = rn_files.read_json(os.path.join(worktree(run), tree_file(run)))
    assert tree["context"]["pr"] == URL
    assert subject(worktree(run)) == f"rn: the pull request of {NAME}"
    assert committed_files(worktree(run)) == [tree_file(run)]
    assert head(origin(tmp_path), f"rn-{NAME}") == head(worktree(run))
    assert git(worktree(run), "status", "--porcelain") == ""


def test_a_put_up_whose_pull_request_is_open_writes_its_url_where_the_tree_has_none(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose pull request is open, and whose tree's context holds no pull request
    When put_up is given the command
    Then the tree's context holds the open pull request's URL, committed and pushed, and gh was
    asked to open no pull request"""
    run = with_command(made_run(str(tmp_path)))
    gh_double.keep(gh_state, {**gh_double.state(gh_state), "pull_request": URL})
    put_up(run, rn_files.COMMAND, host)
    tree = rn_files.read_json(os.path.join(worktree(run), tree_file(run)))
    assert tree["context"]["pr"] == URL
    assert head(origin(tmp_path), f"rn-{NAME}") == head(worktree(run))
    assert created(gh_state) == []


def test_a_put_up_beside_an_earlier_pull_request_not_open_opens_its_own(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose branch's name GitHub holds an earlier pull request of, closed, as an
    earlier run of the same name leaves it, and none open, the tree's context naming that earlier
    one
    When put_up is given the command
    Then gh was asked once to open a pull request, and the tree's context holds the new one's URL,
    committed and pushed"""
    earlier = "https://github.com/lovaizu/invoicer/pull/80"
    design_tree = rn_files.walkthrough_tree(NAME)
    design_tree["context"]["pr"] = earlier
    run = with_command(made_run(str(tmp_path), design_tree=design_tree))
    gh_double.earlier(gh_state, earlier, "CLOSED")
    put_up(run, rn_files.COMMAND, host)
    tree = rn_files.read_json(os.path.join(worktree(run), tree_file(run)))
    assert len(created(gh_state)) == 1
    assert tree["context"]["pr"] == URL
    assert head(origin(tmp_path), f"rn-{NAME}") == head(worktree(run))


def test_a_put_up_with_no_change_makes_no_commit(tmp_path: Any, host: Any):
    """Given a run with nothing changed since its last commit, the command among it, whose tree's
    context holds its pull request
    When put_up is given the command
    Then it gives the command's file at the branch's head, which, pushed, is as it was"""
    design_tree = rn_files.walkthrough_tree(NAME)
    design_tree["context"] = rn_files.context(pr=URL)
    run = with_command(made_run(str(tmp_path), design_tree=design_tree))
    git(worktree(run), "add", "-A")
    git(worktree(run), "commit", "-q", "-m", "The command.")
    before = head(worktree(run))
    assert put_up(run, rn_files.COMMAND, host) == [f"{REPOSITORY}/blob/{before}/{rn_files.COMMAND}"]
    assert head(worktree(run)) == before == head(origin(tmp_path), f"rn-{NAME}")


def test_a_put_up_of_a_deliverable_the_tree_lacks_is_refused(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose tree holds the guide docs/guide.md and the command
    When put_up is given docs/other.md, a path that no deliverable has
    Then Wrong is raised, the branch's head is as it was and not pushed, and gh was asked to open
    no pull request"""
    run = made_run(str(tmp_path))
    before = head(worktree(run))
    with pytest.raises(Wrong):
        put_up(run, "docs/other.md", host)
    assert head(worktree(run)) == before
    assert git(origin(tmp_path), "branch", "--list", f"rn-{NAME}").strip() == ""
    assert created(gh_state) == []


def test_a_put_up_gives_a_link_of_each_path_a_folder_as_a_tree_and_a_file_as_a_blob(
    tmp_path: Any, host: Any
):
    """Given a run whose command lies at the folder invoicer, and at the more paths docs/, a
    folder, and docs/user guide.md, a file whose name holds a space
    When put_up is given the command
    Then it gives a link of each at the commit pushed, in that order: <repository>/tree/<commit>/
    for each folder, with no `/` closing it, and <repository>/blob/<commit>/ for the file, its
    space percent-encoded"""
    design_tree = rn_files.walkthrough_tree(NAME)
    command = design_tree["deliverables"][1]
    command["path"] = "invoicer"
    command["more_paths"] = ["docs/", "docs/user guide.md"]
    run = made_run(str(tmp_path), design_tree=design_tree)
    changed(run, {"docs/user guide.md": "# Guide\n"})
    links = put_up(run, "invoicer", host)
    commit = head(origin(tmp_path), f"rn-{NAME}")
    assert links == [
        f"{REPOSITORY}/tree/{commit}/invoicer",
        f"{REPOSITORY}/tree/{commit}/docs",
        f"{REPOSITORY}/blob/{commit}/docs/user%20guide.md",
    ]


def test_a_put_up_of_a_node_of_no_file_gives_no_link(tmp_path: Any, host: Any):
    """Given a run whose command is a node of no file, its `file` false, with no file at its path
    When put_up is given the command
    Then it gives no link, and origin's rn-<name> holds the branch's head"""
    design_tree = rn_files.walkthrough_tree(NAME)
    design_tree["deliverables"][1]["file"] = False
    run = made_run(str(tmp_path), design_tree=design_tree)
    assert put_up(run, rn_files.COMMAND, host) == []
    assert head(origin(tmp_path), f"rn-{NAME}") == head(worktree(run))


def test_a_put_up_of_a_path_the_commit_doesnt_hold_is_refused_naming_it(tmp_path: Any, host: Any):
    """Given a run whose command's file isn't written, and whose guide is
    When put_up is given the command
    Then Wrong is raised naming the command's path, saying the commit pushed holds nothing there"""
    run = made_run(str(tmp_path))
    changed(run, {rn_files.GUIDE: "# Guide\n"})
    match = f"{rn_files.COMMAND}: the work's pushed commit holds nothing there"
    with pytest.raises(Wrong, match=match):
        put_up(run, rn_files.COMMAND, host)


def test_a_put_up_with_gh_logged_out_is_missing_its_login(tmp_path: Any, host: Any, gh_state: str):
    """Given a run, and gh with no login
    When put_up is given the command
    Then Missing is raised with what gh said, that no GitHub host is logged into, before any
    commit or push: the change of invoicer's lines stays uncommitted, the branch's head is as it
    was, the remote holds no rn-<name>, and gh was asked `gh auth status` alone"""
    run = made_run(str(tmp_path))
    changed(run, {"invoicer/lines.py": "print()\n"})
    before = head(worktree(run))
    gh_double.logged_out(gh_state)
    with pytest.raises(Missing, match="not logged into any GitHub hosts"):
        put_up(run, rn_files.COMMAND, host)
    assert head(worktree(run)) == before
    assert git(worktree(run), "status", "--porcelain").split() == ["M", "invoicer/lines.py"]
    assert git(origin(tmp_path), "branch", "--list", f"rn-{NAME}").strip() == ""
    assert [each[:3] for each in gh_double.state(gh_state)["asked"]] == [["gh", "auth", "status"]]


def test_a_put_up_while_the_goal_is_open_is_wrong_before_any_commit_or_push(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose design tree's goal is open, its decided null, and whose guide is written
    When put_up is given the plan
    Then Wrong is raised saying the goal is open, before any commit or push: the guide stays
    uncommitted, the branch's head is as it was, the remote holds no rn-<name>, and gh was asked
    `gh auth status` alone"""
    design_tree = rn_files.walkthrough_tree(NAME, plan_done=False)
    design_tree["goal"] = {"decided": None}
    run = made_run(str(tmp_path), design_tree=design_tree)
    changed(run, {rn_files.GUIDE: "# Guide\n"})
    before = head(worktree(run))
    with pytest.raises(Wrong, match="goal is open"):
        put_up(run, rn_files.plan_path(NAME), host)
    assert head(worktree(run)) == before
    assert git(worktree(run), "status", "--porcelain", "--", rn_files.GUIDE).split() == [
        "??",
        rn_files.GUIDE,
    ]
    assert git(origin(tmp_path), "branch", "--list", f"rn-{NAME}").strip() == ""
    assert [each[:3] for each in gh_double.state(gh_state)["asked"]] == [["gh", "auth", "status"]]


# diff


def test_diff_commits_each_change_pushes_it_and_gives_the_whole_diff_against_the_default_branch(
    tmp_path: Any, host: Any
):
    """Given a run whose design tree is committed on its branch, beside a stray note that was then
    removed from its worktree, and the guide written but not committed
    When diff is given the run
    Then it gives a diff that holds the guide and the design tree and no line of the note, the
    guide and the note's removal are committed as `rn: the final check of <name>`, and origin's
    rn-<name> holds that commit"""
    run = made_run(str(tmp_path))
    changed(run, {"notes.md": "# A note to self\n"})
    git(worktree(run), "add", "-A")
    git(worktree(run), "commit", "-q", "-m", "A note.")
    os.remove(os.path.join(worktree(run), "notes.md"))
    changed(run, {rn_files.GUIDE: "# Guide\n"})
    given = diff(run, host)
    assert f"+++ b/{rn_files.GUIDE}" in given
    assert f"+++ b/{tree_file(run)}" in given
    assert "notes.md" not in given
    assert subject(worktree(run)) == f"rn: the final check of {NAME}"
    assert head(origin(tmp_path), f"rn-{NAME}") == head(worktree(run))


# ci


def checks_asked(gh_state: str) -> list[list[str]]:
    """Each `gh pr checks` that the double of gh was asked."""
    return [each for each in gh_double.state(gh_state)["asked"] if each[1:3] == ["pr", "checks"]]


# What ci says of the checks that failed, and of three that the CI cancelled.
MEND = "; mend each in the deliverable whose file it concerns"
AGAIN = (
    "; these ended neither passing nor failing, for the user to run again: times-out cancelled,"
    " cancels cancelled, cancelled cancelled"
)


def ended(found: str) -> list[dict[str, str]]:
    """Each check of the record that the double of gh gives for what the CI's checks found, as
    `gh pr checks --json name,state,bucket,link` gives them."""
    return json.loads(gh_double._ends(found)["stdout"])


def lines(checks: list[tuple[str, str]]) -> str:
    """The lines that ci gives of the checks, each by its name and how it ended."""
    return "".join(f"{name}\t{end}\n" for name, end in checks)


def test_ci_where_each_check_passed_gives_them_having_waited_for_the_works_branch(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose plan was put up, and whose CI's checks each passed
    When ci is given the run
    Then it gives each check by its name, once each, in gh's order, as passed; and gh was asked,
    in the run's worktree, to wait for rn-<name>'s checks, then to give each check's end"""
    run = made_run(str(tmp_path))
    put_up(run, rn_files.plan_path(NAME), host)
    names = list(dict.fromkeys(each["name"] for each in ended("passed")))
    assert ci(run, host) == lines([(name, "passed") for name in names])
    branch = f"rn-{NAME}"
    assert checks_asked(gh_state) == [
        ["gh", "pr", "checks", branch, "--watch"],
        ["gh", "pr", "checks", branch, "--json", "name,state,bucket,link"],
    ]
    assert host.ran[-1][1] == worktree(run)


@pytest.mark.parametrize(
    "case",
    [("cancelled", "cancels", "cancelled"), ("timed-out", "deploy", "timed out")],
    ids=["cancelled", "timed-out"],
)
def test_ci_where_a_check_ended_neither_passing_nor_failing_names_how_it_ended(
    tmp_path: Any, host: Any, gh_state: str, case: tuple[str, str, str]
):
    """Given a run whose plan was put up, and whose CI's check was cancelled, as GitHub Actions ends
    a job past its time limit too, or timed out, as another check's app may end it, each other
    check passed, and gh's watch ending 0 or 1
    When ci is given the run
    Then it gives each check by its name in gh's order, that one as cancelled or timed out and
    each other as passed, as neither passing nor failing, for the user to run again"""
    found, other, end = case
    run = made_run(str(tmp_path))
    put_up(run, rn_files.plan_path(NAME), host)
    gh_double.checks(gh_state, found)
    names = list(dict.fromkeys(each["name"] for each in ended(found)))
    assert other in names
    assert ci(run, host) == lines([(name, end if name == other else "passed") for name in names])


@pytest.mark.parametrize(
    ("found", "expected"),
    [
        ("failed", f"the pull request's CI fails at tests{MEND}"),
        ("ended", f"the pull request's CI fails at fails{MEND}{AGAIN}"),
    ],
    ids=["failed", "failed-and-cancelled"],
)
def test_ci_where_a_check_failed_is_wrong_naming_it_once(
    tmp_path: Any, host: Any, gh_state: str, found: str, expected: str
):
    """Given a run whose plan was put up, and whose CI's check `tests` failed, which gh's lines
    show twice as it waits, or whose check `fails` failed while three others were cancelled
    When ci is given the run
    Then Wrong is raised, naming each check that failed once, and no check that passed, then each
    that was cancelled, for the user to run again"""
    run = made_run(str(tmp_path))
    put_up(run, rn_files.plan_path(NAME), host)
    gh_double.checks(gh_state, found)
    with pytest.raises(Wrong) as refused:
        ci(run, host)
    assert str(refused.value) == expected


def test_ci_that_gh_cant_give_cant_run_with_what_gh_said(tmp_path: Any, host: Any, clock: Any):
    """Given a run that has no pull request
    When ci is given the run
    Then CantRun is raised, saying gh can't give the pull request's CI, with what gh said, with no
    wait"""
    run = made_run(str(tmp_path))
    with pytest.raises(CantRun) as refused:
        ci(run, host)
    assert str(refused.value).startswith("gh can't give the pull request's CI: ")
    assert 'no pull requests found for branch "rn-' in str(refused.value)
    assert clock.slept == []


def test_ci_whose_checks_gh_cant_read_once_they_started_cant_run_with_what_gh_said(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose plan was put up, whose pushed head's checks started, and whose gh then
    can't reach GitHub
    When ci is given the run
    Then CantRun is raised, saying gh can't give the pull request's CI, with what gh said"""
    run = made_run(str(tmp_path))
    put_up(run, rn_files.plan_path(NAME), host)
    gh_double.checks_unreached(gh_state)
    said = gh_double.line(gh_double.PR_CHECKS, "gh pr checks --json can't reach GitHub")["stderr"]
    with pytest.raises(CantRun) as refused:
        ci(run, host)
    assert str(refused.value) == f"gh can't give the pull request's CI: {said.strip()}"


def views(gh_state: str) -> int:
    """How many times the double of gh was asked for the pull request's head and its checks."""
    asked = gh_double.state(gh_state)["asked"]
    return sum(1 for each in asked if each[1:3] == ["pr", "view"] and "headRefOid" in each[-1])


def test_ci_waits_until_the_pushed_heads_checks_start_then_reads_their_ends(
    tmp_path: Any, host: Any, gh_state: str, clock: Any
):
    """Given a run whose plan was put up, whose CI's checks each passed, and whose pull request
    gives the head before the push for one view, then the pushed head with no check started for
    23 views, its checks starting 120 seconds after the first view, the most
    When ci is given the run
    Then it views the head every 5 seconds until the pushed head's checks show, then gives each
    check as passed, as it gives with no wait"""
    run = made_run(str(tmp_path))
    put_up(run, rn_files.plan_path(NAME), host)
    gh_double.started(gh_state, 1, 23)
    names = list(dict.fromkeys(each["name"] for each in ended("passed")))
    assert ci(run, host) == lines([(name, "passed") for name in names])
    assert clock.slept == [5] * 24
    assert views(gh_state) == 25


def test_ci_whose_checks_dont_start_within_120_seconds_says_no_ci_started(
    tmp_path: Any, host: Any, gh_state: str, clock: Any
):
    """Given a run whose plan was put up, and whose pushed head's checks start only past 120
    seconds after the first view
    When ci is given the run
    Then it gives that no CI started within 120 seconds of the push, having viewed the head at
    each 5 seconds up to 120, and asked gh for no check"""
    run = made_run(str(tmp_path))
    put_up(run, rn_files.plan_path(NAME), host)
    gh_double.started(gh_state, 0, 25)
    assert ci(run, host) == "no CI started within 120 seconds of the push\n"
    assert clock.slept == [5] * 24
    assert views(gh_state) == 25
    assert checks_asked(gh_state) == []

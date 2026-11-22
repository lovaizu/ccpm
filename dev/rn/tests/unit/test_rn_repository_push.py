"""The unit cases of repository/push.py: `commit`, of one path, several, a folder, and one with a
change beside one without, the rest of the index left alone, and each refusal: a path outside the
worktree, no change, and a commit check that refuses; `pause`, with changes and with none, each
pushed with its upstream set, and each refusal: no origin, a push refused for want of a permission,
and a remote that isn't there; and `put_up`, which asks gh's login first, its first time opening the
pull request titled by the goal's first sentence, of a goal of two sentences and of one, its body
naming the issues and naming none, the pull request's URL written into the tree, its second
opening none, an open pull request's URL written where the tree has none, and each refusal: gh
with no login before any commit or push, a deliverable the tree lacks, and no origin."""

from __future__ import annotations

import os
import stat
from typing import Any

import pytest
import rn_files
from fault import CantRun, Missing, Wrong
from gh import gh_double
from repo_files import git
from repository.place import RunPlace
from repository.push import commit, pause, put_up
from rn_runs import NAME, changed, committed_files, head, hook, made_run, subject
from template.markdown import sentences

URL = "http://github.com/owner/repo/pull/1"
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


@pytest.mark.supports(
    "test_a_point_the_orchestrator_settles_is_committed_with_its_ground_as_the_message"
)
def test_a_commit_of_one_path_holds_it_alone_with_the_message(tmp_path: Any, host: Any):
    """Given a run whose design tree and the command are changed, neither staged
    When commit is given the design tree with a message of two lines
    Then it gives the new head of the run's branch, whose message is the given one word for word,
    and which holds the design tree alone; the command stays changed and unstaged"""
    run = made_run(str(tmp_path))
    changed(run, {tree_file(run): "{}\n", rn_files.COMMAND: "print()\n"})
    message = "The README names its people.\n\nThe guide is for the accounting team."
    given = commit(run, [tree_file(run)], message, host)
    assert given == head(worktree(run), f"rn-{run.name}")
    assert subject(worktree(run)) == message
    assert committed_files(worktree(run)) == [tree_file(run)]
    assert git(worktree(run), "status", "--porcelain").split() == ["??", "invoicer/__main__.py"]


@pytest.mark.supports(
    "test_a_point_the_orchestrator_settles_is_committed_with_its_ground_as_the_message"
)
def test_a_commit_of_several_paths_and_a_folder_holds_each(tmp_path: Any, host: Any):
    """Given a run whose design tree, a Round's file, and the guide are changed
    When commit is given the design tree, the run's folder of Rounds, and the guide
    Then the commit holds each of the three files"""
    run = made_run(str(tmp_path))
    round_file = f".rn/{run.name}/rounds/docs-guide.md/content-1/generator.json"
    changed(run, {tree_file(run): "{}\n", round_file: "{}\n", rn_files.GUIDE: "# Guide\n"})
    commit(run, [tree_file(run), f".rn/{run.name}/rounds", rn_files.GUIDE], "Made.", host)
    assert sorted(committed_files(worktree(run))) == sorted(
        [tree_file(run), round_file, rn_files.GUIDE]
    )


@pytest.mark.supports(
    "test_a_point_the_orchestrator_settles_is_committed_with_its_ground_as_the_message"
)
def test_a_commit_takes_a_path_with_no_change_beside_one_with_one(tmp_path: Any, host: Any):
    """Given a run whose design tree is changed and whose docs/product-vision.md isn't
    When commit is given both
    Then it commits the design tree alone"""
    run = made_run(str(tmp_path))
    changed(run, {tree_file(run): "{}\n"})
    commit(run, [tree_file(run), "docs/product-vision.md"], "The tree.", host)
    assert committed_files(worktree(run)) == [tree_file(run)]


@pytest.mark.supports(
    "test_a_point_the_orchestrator_settles_is_committed_with_its_ground_as_the_message"
)
def test_a_commit_leaves_the_rest_of_the_index_as_it_was(tmp_path: Any, host: Any):
    """Given a run whose guide is changed and staged, and whose design tree is changed
    When commit is given the design tree
    Then the commit holds the design tree alone, and the guide stays staged"""
    run = made_run(str(tmp_path))
    changed(run, {rn_files.GUIDE: "# Guide\n", tree_file(run): "{}\n"})
    git(worktree(run), "add", rn_files.GUIDE)
    commit(run, [tree_file(run)], "The tree.", host)
    assert committed_files(worktree(run)) == [tree_file(run)]
    assert git(worktree(run), "diff", "--cached", "--name-only").split() == [rn_files.GUIDE]


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
@pytest.mark.parametrize("outside", ["../outside.txt", "/etc/hostname", "../../../NOTES.md"])
def test_a_commit_of_a_path_outside_the_worktree_is_refused(tmp_path: Any, host: Any, outside: str):
    """Given a run whose design tree is changed
    When commit is given it and a path outside the worktree
    Then Wrong is raised, naming the path, and the branch's head is as it was"""
    run = made_run(str(tmp_path))
    changed(run, {tree_file(run): "{}\n"})
    before = head(worktree(run))
    with pytest.raises(Wrong, match=outside.replace(".", r"\.")):
        commit(run, [tree_file(run), outside], "The tree.", host)
    assert head(worktree(run)) == before


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
def test_a_commit_with_no_change_in_any_path_is_refused(tmp_path: Any, host: Any):
    """Given a run with nothing changed
    When commit is given the design tree
    Then Wrong is raised, naming it, and the branch's head is as it was"""
    run = made_run(str(tmp_path))
    before = head(worktree(run))
    with pytest.raises(Wrong, match="design-tree.json"):
        commit(run, [tree_file(run)], "The tree.", host)
    assert head(worktree(run)) == before


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
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


@pytest.mark.supports("test_a_pause_stops_the_generator_and_pushes_the_runs_work_so_far")
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


@pytest.mark.supports("test_a_pause_stops_the_generator_and_pushes_the_runs_work_so_far")
def test_a_pause_with_no_change_pushes_the_last_commit_alone(tmp_path: Any, host: Any):
    """Given a run with nothing changed since its last commit
    When pause is given the run
    Then it makes no commit, and gives the last commit's hash, which origin's rn-<name> holds"""
    run = made_run(str(tmp_path))
    before = head(worktree(run))
    assert pause(run, host) == before
    assert head(worktree(run)) == before
    assert head(origin(tmp_path), f"rn-{run.name}") == before


@pytest.mark.supports("test_a_pause_leaves_the_users_own_worktree_and_branch_as_they_were")
def test_a_pause_leaves_the_users_branch_and_change_as_they_were(tmp_path: Any, host: Any):
    """Given a run whose design tree is changed, and the user's own change to docs/test-design.md
    on main
    When pause is given the run
    Then main's head, the user's branch, and their change are as they were, and origin's main too"""
    run = made_run(str(tmp_path))
    main = head(run.repository, "main")
    with open(os.path.join(run.repository, "docs", "test-design.md"), "a", encoding="utf-8") as f:
        f.write("The user's own line.\n")
    changed(run, {tree_file(run): "{}\n"})
    pause(run, host)
    assert head(run.repository, "main") == main == head(origin(tmp_path), "main")
    assert git(run.repository, "branch", "--show-current").strip() == "main"
    assert git(run.repository, "status", "--porcelain", "--untracked-files=no").split() == [
        "M",
        "docs/test-design.md",
    ]


@pytest.mark.supports("test_a_pause_stops_the_generator_and_pushes_the_runs_work_so_far")
def test_a_pause_with_no_origin_is_missing_one(tmp_path: Any, host: Any):
    """Given a run whose repository has no remote
    When pause is given the run
    Then Missing is raised"""
    run = made_run(str(tmp_path), origin=False)
    changed(run, {tree_file(run): "{}\n"})
    with pytest.raises(Missing):
        pause(run, host)


@pytest.mark.supports("test_a_pause_stops_the_generator_and_pushes_the_runs_work_so_far")
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


@pytest.mark.supports("test_a_pause_stops_the_generator_and_pushes_the_runs_work_so_far")
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


def created(gh_state: str) -> list[list[str]]:
    """Each `gh pr create` that the double was asked."""
    return [each for each in gh_double.state(gh_state)["asked"] if each[1:3] == ["pr", "create"]]


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_a_first_put_up_pushes_and_opens_the_pull_request_titled_by_the_goal(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose plan is open and whose design tree is changed, with no pull request, its
    goal of two sentences
    When put_up is given the plan
    Then it gives the pull request's changes, <pull request>/files; gh was asked its login before
    anything else; the change is committed as `rn: <plan's name>` and pushed to origin's
    rn-<name>; and gh was asked once to open a pull request, titled by the goal's first sentence
    alone"""
    design_tree = rn_files.walkthrough_tree(NAME, plan_done=False)
    run = made_run(str(tmp_path), design_tree=design_tree)
    changed(run, {rn_files.GUIDE: "# Guide\n"})
    assert put_up(run, rn_files.plan_path(NAME), host) == f"{URL}/files"
    assert gh_double.state(gh_state)["asked"][0][:3] == ["gh", "auth", "status"]
    assert subject(worktree(run), "HEAD~1") == f"rn: {rn_files.GOAL}"
    assert committed_files(worktree(run), "HEAD~1") == [rn_files.GUIDE]
    assert head(origin(tmp_path), f"rn-{NAME}") == head(worktree(run))
    assert [title(each) for each in created(gh_state)] == [FIRST]


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
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
    run = made_run(str(tmp_path), design_tree=design_tree)
    put_up(run, rn_files.COMMAND, host)
    assert [body(each) for each in created(gh_state)] == [
        f"{rn_files.GOAL}\n\nCloses #12\nCloses #3\nRefs #8"
    ]


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_a_first_put_ups_body_of_a_run_with_no_issue_is_the_goal_alone(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose tree's context names no issue, with no pull request
    When put_up is given the command
    Then gh was asked once to open a pull request whose body is the goal alone"""
    run = made_run(str(tmp_path))
    put_up(run, rn_files.COMMAND, host)
    assert [body(each) for each in created(gh_state)] == [rn_files.GOAL]


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_a_first_put_up_writes_the_pull_requests_url_into_the_tree_and_pushes_it(
    tmp_path: Any, host: Any
):
    """Given a run whose tree's context holds no pull request, with none open
    When put_up is given the command
    Then the tree's context holds the pull request's URL, committed alone as
    `rn: the pull request of <name>` and pushed to origin's rn-<name>, with nothing left
    uncommitted"""
    run = made_run(str(tmp_path))
    put_up(run, rn_files.COMMAND, host)
    tree = rn_files.read_json(os.path.join(worktree(run), tree_file(run)))
    assert tree["context"]["pr"] == URL
    assert subject(worktree(run)) == f"rn: the pull request of {NAME}"
    assert committed_files(worktree(run)) == [tree_file(run)]
    assert head(origin(tmp_path), f"rn-{NAME}") == head(worktree(run))
    assert git(worktree(run), "status", "--porcelain") == ""


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_a_put_up_whose_pull_request_is_open_writes_its_url_where_the_tree_has_none(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose pull request is open, and whose tree's context holds no pull request
    When put_up is given the command
    Then the tree's context holds the open pull request's URL, committed and pushed, and gh was
    asked to open no pull request"""
    run = made_run(str(tmp_path))
    gh_double.keep(gh_state, {**gh_double.state(gh_state), "pull_request": URL})
    put_up(run, rn_files.COMMAND, host)
    tree = rn_files.read_json(os.path.join(worktree(run), tree_file(run)))
    assert tree["context"]["pr"] == URL
    assert head(origin(tmp_path), f"rn-{NAME}") == head(worktree(run))
    assert created(gh_state) == []


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_a_goal_of_one_sentence_titles_the_pull_request_whole(
    tmp_path: Any, host: Any, gh_state: str
):
    """Given a run whose goal is one sentence, with no pull request
    When put_up is given the command
    Then gh was asked once to open a pull request, titled by the goal whole"""
    goal = "The accounting team prints each invoice themselves."
    design_tree = rn_files.walkthrough_tree(NAME)
    design_tree["goal"]["decided"] = goal
    run = made_run(str(tmp_path), design_tree=design_tree)
    put_up(run, rn_files.COMMAND, host)
    assert [title(each) for each in created(gh_state)] == [goal]


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
@pytest.mark.parametrize(
    ("goal", "first"),
    [
        ("Does the team print it? They print it.", "Does the team print it?"),
        ("They print it! Then they file it.", "They print it!"),
        (
            "They print at a rate of 0.19 each time. Then file it.",
            "They print at a rate of 0.19 each time.",
        ),
        ("They print e.g. invoices. Then file them.", "They print e.g."),
        (
            "They run `python3 -m invoicer. lines.csv` alone. Then file it.",
            "They run `python3 -m invoicer. lines.csv` alone.",
        ),
        ("They print it\nThen file it.", "They print it"),
        ("They print it", "They print it"),
    ],
)
def test_the_title_is_the_first_sentence_as_markdown_splits_the_goal(
    tmp_path: Any, host: Any, gh_state: str, goal: str, first: str
):
    """Given a run whose goal's first sentence ends at a `?`, at a `!`, past a `.` with no space
    after it, at the `.` of `e.g.` before a space, past a `.` in a code span, at a newline, or
    nowhere, with no pull request
    When put_up is given the command
    Then gh was asked once to open a pull request, titled by the first of the sentences that
    template.markdown.sentences gives of the goal"""
    design_tree = rn_files.walkthrough_tree(NAME)
    design_tree["goal"]["decided"] = goal
    run = made_run(str(tmp_path), design_tree=design_tree)
    put_up(run, rn_files.COMMAND, host)
    assert sentences(goal)[0] == first
    assert [title(each) for each in created(gh_state)] == [first]


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_a_second_put_up_opens_no_second_pull_request(tmp_path: Any, host: Any, gh_state: str):
    """Given a run whose plan was put up once, and whose command then changed
    When put_up is given the command
    Then it gives the same pull request's changes, the change is committed as
    `rn: <command's name>` and pushed, and gh was asked to open a pull request once in all"""
    run = made_run(str(tmp_path))
    put_up(run, rn_files.plan_path(NAME), host)
    changed(run, {rn_files.COMMAND: "print()\n"})
    assert put_up(run, rn_files.COMMAND, host) == f"{URL}/files"
    assert subject(worktree(run)) == f"rn: {rn_files.COMMAND_NAME}"
    assert head(origin(tmp_path), f"rn-{NAME}") == head(worktree(run))
    asked = gh_double.state(gh_state)["asked"]
    assert [each[1:3] for each in asked].count(["pr", "create"]) == 1


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_a_put_up_with_no_change_makes_no_commit(tmp_path: Any, host: Any):
    """Given a run with nothing changed since its last commit, whose tree's context holds its
    pull request
    When put_up is given the command
    Then it gives the pull request's changes, and the branch's head, pushed, is as it was"""
    design_tree = rn_files.walkthrough_tree(NAME)
    design_tree["context"] = rn_files.context(pr=URL)
    run = made_run(str(tmp_path), design_tree=design_tree)
    before = head(worktree(run))
    assert put_up(run, rn_files.COMMAND, host) == f"{URL}/files"
    assert head(worktree(run)) == before == head(origin(tmp_path), f"rn-{NAME}")


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
@pytest.mark.parametrize("deliverable", ["docs/other.md", "docs/guide", "invoicer"])
def test_a_put_up_of_a_deliverable_the_tree_lacks_is_refused(
    tmp_path: Any, host: Any, gh_state: str, deliverable: str
):
    """Given a run whose tree holds the guide docs/guide.md and the command
    When put_up is given a path that no deliverable has, a near match of one among them
    Then Wrong is raised, the branch's head is as it was and not pushed, and gh was asked to open
    no pull request"""
    run = made_run(str(tmp_path))
    before = head(worktree(run))
    with pytest.raises(Wrong):
        put_up(run, deliverable, host)
    assert head(worktree(run)) == before
    assert git(origin(tmp_path), "branch", "--list", f"rn-{NAME}").strip() == ""
    assert created(gh_state) == []


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_a_put_up_with_no_origin_is_missing_one(tmp_path: Any, host: Any):
    """Given a run whose repository has no remote
    When put_up is given the command
    Then Missing is raised"""
    run = made_run(str(tmp_path), origin=False)
    with pytest.raises(Missing):
        put_up(run, rn_files.COMMAND, host)


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
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

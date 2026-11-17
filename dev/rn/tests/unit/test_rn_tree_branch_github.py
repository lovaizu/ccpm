"""The unit cases of tree/branch.py, which decides what tree.py commits, when it pushes, and how it
reads the design tree's past back, and of
tree/github.py, which decides what a run shows on GitHub. A commit names the run and why; a push
finds a remote or none; the commit at which a deliverable was done turns on how its status went
from commit to commit, never done, done, left done, opened again, and done again, on its place
among the deliverables, and on git failing; the pull request is opened or kept, marked ready or a
draft again; the comments are those since a sign-off; and a lesson's issue lies on the repository
that rn's manifest names, each with gh logged in or not."""

from __future__ import annotations

import dataclasses
import os
from typing import Any

import pytest
from fault import CantRun, Missing
from tree import branch, github

from dev.rn.tests.unit import rn_data as d

# The status of "Type hints in each file of invoicer" in each commit of the design tree, in order,
# beside "invoicer marked as typed"'s; and which of those commits marked it done last, None where
# none did.
HISTORIES = [
    ([("doing", "open")], None),
    ([("doing", "open"), ("done", "open")], 1),
    ([("doing", "open"), ("done", "open"), ("done", "doing")], 1),
    ([("doing", "open"), ("done", "open"), ("doing", "open")], 1),
    ([("doing", "open"), ("done", "open"), ("doing", "open"), ("done", "open")], 3),
]


def on_github(monkeypatch: pytest.MonkeyPatch, tmp: Any, **held: Any) -> str:
    for name, value in d.github(str(tmp), **held).items():
        monkeypatch.setenv(name, value)
    return os.environ["RN_GH_STATE"]


@pytest.mark.supports("test_a_settled_decisions_ground_is_the_message_of_its_commit")
def test_a_commit_of_the_runs_files_holds_its_message_word_for_word(tmp_path: Any) -> None:
    """Given: a run whose worktree holds invoicer/py.typed new.
    When: it's committed with a decision's ground of two lines as its message.
    Then: it gives the commit's ID, whose message is the ground word for word."""
    run = d.run_of(d.repository(str(tmp_path)))
    open(os.path.join(run.worktree, "invoicer", "py.typed"), "w").close()
    ground = "PEP 561 settles where the marker lies.\nA checker reads it only there."
    commit = branch.commit(run, ["invoicer/py.typed"], ground)
    assert d.git(run.worktree, "log", "-1", "--format=%B", commit).strip() == ground


def committed(run: Any, *trees: dict[str, Any]) -> list[str]:
    """Each design tree written and committed on the run's branch in turn; gives each commit."""
    found = []
    for data in trees:
        d.tree_written(run, data)
        found.append(d.git(run.worktree, "rev-parse", "HEAD").strip())
    return found


@pytest.mark.supports("test_a_deliverable_done_before_is_reworked_from_the_commit_it_was_done_at")
@pytest.mark.parametrize(("statuses", "last_done"), HISTORIES)
def test_the_commit_a_deliverable_was_last_done_at_is_the_last_that_marked_it_done(
    tmp_path: Any, statuses: list[tuple[str, str]], last_done: int | None
) -> None:
    """Given: a run whose design tree was committed once for each pair of statuses: never done;
    done; done and left done while the other deliverable changed; done and opened again; and done
    again.
    When: the commit at which invoicer was last done is asked.
    Then: it gives the last commit that marked it done, or "" where none did."""
    run = d.run_of(d.repository(str(tmp_path)))
    ids = committed(run, *[d.with_status(d.walkthrough_tree(), *each) for each in statuses])
    assert branch.done_at(run, "invoicer") == ("" if last_done is None else ids[last_done])


@pytest.mark.supports("test_a_deliverable_done_before_is_reworked_from_the_commit_it_was_done_at")
def test_a_deliverable_moved_among_the_deliverables_keeps_the_commit_it_was_done_at(
    tmp_path: Any,
) -> None:
    """Given: a run whose design tree marked invoicer done, then took a new deliverable before it.
    When: the commit at which invoicer was last done is asked.
    Then: it gives the commit that marked it done, not the one that moved it."""
    run = d.run_of(d.repository(str(tmp_path)))
    done = d.with_status(d.walkthrough_tree(), "done", "open")
    moved = dict(done, deliverables=[d.open_deliverable("pyproject.toml typed", "pyproject.toml")])
    moved["deliverables"] += done["deliverables"]
    ids = committed(run, d.walkthrough_tree(), done, moved)
    assert branch.done_at(run, "invoicer") == ids[1]


@pytest.mark.supports("test_a_deliverable_done_before_is_reworked_from_the_commit_it_was_done_at")
def test_a_deliverable_the_tree_never_held_was_never_done(tmp_path: Any) -> None:
    """Given: a run whose design tree marked invoicer done.
    When: the commit at which README.md was last done is asked.
    Then: it gives ""."""
    run = d.run_of(d.repository(str(tmp_path)))
    committed(run, d.with_status(d.walkthrough_tree(), "done", "done"))
    assert branch.done_at(run, "README.md") == ""


@pytest.mark.supports("test_a_deliverable_done_before_is_reworked_from_the_commit_it_was_done_at")
def test_the_commit_a_deliverable_was_done_at_where_git_fails_cant_run(tmp_path: Any) -> None:
    """Given: a run whose worktree is no longer there.
    When: the commit at which invoicer was last done is asked.
    Then: it couldn't run."""
    run = d.run_of(d.repository(str(tmp_path)))
    gone = str(tmp_path / "gone")
    run = dataclasses.replace(run, worktree=gone, folder=os.path.join(gone, ".rn", d.NAME))
    with pytest.raises(CantRun):
        branch.done_at(run, "invoicer")


@pytest.mark.supports("test_dn_stops_the_generator_and_pushes_its_work_with_the_step_it_stood_at")
def test_the_works_branch_is_pushed(tmp_path: Any) -> None:
    """Given: a run in a repository with a remote.
    When: the work's branch is pushed.
    Then: the remote holds the branch."""
    repo = d.repository(str(tmp_path))
    origin = d.remote_for(repo, str(tmp_path))
    run = d.run_of(repo)
    branch.push(run)
    assert d.git(origin, "branch", "--list", run.branch).strip()


@pytest.mark.supports("test_dn_where_git_cant_push_commits_and_says_what_is_missing")
def test_a_push_with_no_remote_says_whats_missing(tmp_path: Any) -> None:
    """Given: a run in a repository with no remote.
    When: the work's branch is pushed.
    Then: it's refused as missing the remote."""
    with pytest.raises(Missing, match="remote"):
        branch.push(d.run_of(d.repository(str(tmp_path))))


@pytest.mark.supports("test_a_sign_off_pushes_the_work_and_keeps_a_draft_pull_request")
def test_the_draft_pull_request_takes_the_goal_as_its_title_and_is_kept(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given: a run with the walkthrough's tree, whose branch has no pull request, and gh logged in.
    When: its draft pull request is kept twice.
    Then: each gives the same draft, and GitHub holds one pull request of the branch."""
    held = on_github(monkeypatch, tmp_path)
    run = d.run_of(d.repository(str(tmp_path)))
    d.tree_written(run)
    first, again = github.keep_draft(run), github.keep_draft(run)
    assert first == again and first.draft is True
    assert list(d.read_json(held)["pulls"]) == [run.branch]


@pytest.mark.supports("test_a_push_without_a_login_of_gh_says_what_is_missing")
def test_a_draft_with_no_login_says_whats_missing(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given: a run with the walkthrough's tree, and gh logged in to no account.
    When: its draft pull request is kept.
    Then: it's refused as missing the login of gh."""
    on_github(monkeypatch, tmp_path, logged_in=False)
    run = d.run_of(d.repository(str(tmp_path)))
    d.tree_written(run)
    with pytest.raises(Missing):
        github.keep_draft(run)


@pytest.mark.supports("test_gm_on_the_pull_request_handed_over_marks_it_a_draft_again")
@pytest.mark.parametrize("ready", [True, False])
def test_the_pull_request_is_handed_over_ready_or_marked_a_draft_again(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch, ready: bool
) -> None:
    """Given: a run whose branch has a draft pull request, and gh logged in.
    When: the work is handed over, or sent back.
    Then: the pull request is ready, or a draft again."""
    run = d.run_of(d.repository(str(tmp_path)))
    on_github(
        monkeypatch, tmp_path, pulls={run.branch: {"number": 1, "draft": not ready, "comments": []}}
    )
    assert github.hand_over(run, ready).draft is (not ready)


@pytest.mark.supports("test_gm_alone_reads_the_users_comments_since_the_sign_off")
def test_the_comments_are_those_since_the_sign_off(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given: a run whose pull request has a comment before 09:00 and one after.
    When: the comments since 09:00 are asked.
    Then: it gives the one after."""
    run = d.run_of(d.repository(str(tmp_path)))
    comments = [
        {"body": "Before.", "createdAt": "2026-11-15T08:30:00Z"},
        {"body": "After.", "createdAt": "2026-11-15T10:00:00Z"},
    ]
    on_github(
        monkeypatch,
        tmp_path,
        pulls={run.branch: {"number": 1, "draft": True, "comments": comments}},
    )
    assert [c.body for c in github.comments(run, "2026-11-15T09:00:00Z")] == ["After."]


@pytest.mark.supports("test_a_lesson_approved_opens_an_issue_on_rns_repository_word_for_word")
def test_a_lesson_opens_an_issue_on_the_repository_rns_manifest_names(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given: rn's folder, whose manifest names https://github.com/lovaizu/ccpm, and gh logged in.
    When: the issue of a lesson is opened.
    Then: it gives the issue's URL, and GitHub holds it on lovaizu/ccpm with the lesson's words
    word for word."""
    held = on_github(monkeypatch, tmp_path)
    lesson = "The code best practice says nothing of a library's py.typed marker."
    url = github.open_lesson(d.RN, lesson)
    [issue] = d.read_json(held)["issues"]
    assert url.endswith("/issues/1")
    assert issue["repository"] == "lovaizu/ccpm" and lesson in issue["body"]

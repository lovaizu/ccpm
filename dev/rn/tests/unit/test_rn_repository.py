"""The unit cases of repository/git.py and repository/gh.py, which run git and gh for tree.py and
read what they print. Each command turns on whether its tool can do it: a repository or none, a
remote or none, a login of gh or none, a pull request of the branch or none, and something to
commit or nothing, so the cases take each, with gh played by its double, which gives each result
from a record of gh."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fault import CantRun, Missing
from repository import gh, git

from dev.rn.tests.unit import rn_data as d

BRANCH = f"rn-{d.NAME}"


def on_github(monkeypatch: pytest.MonkeyPatch, tmp: Any, **held: Any) -> str:
    """gh played by its double with what GitHub holds; gives the file that holds it."""
    for name, value in d.github(str(tmp), **held).items():
        monkeypatch.setenv(name, value)
    return os.environ["RN_GH_STATE"]


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_a_worktree_is_added_on_a_branch_of_its_own(tmp_path: Any) -> None:
    """Given: a repository.
    When: a worktree is added at .claude/worktrees/rn-<name>/ on the branch rn-<name>.
    Then: the worktrees listed hold it with its branch, beside the root's."""
    repo = d.repository(str(tmp_path))
    where = os.path.join(repo, ".claude", "worktrees", BRANCH)
    git.add_worktree(repo, where, BRANCH)
    assert (where, BRANCH) in git.worktrees(repo)
    assert (repo, "main") in git.worktrees(where)


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_a_folder_in_no_repository_is_missing_it(tmp_path: Any) -> None:
    """Given: a folder in no git repository.
    When: a worktree is added from it, and its worktrees are listed.
    Then: each is refused as missing a repository."""
    with pytest.raises(Missing):
        git.add_worktree(str(tmp_path), os.path.join(tmp_path, "w"), BRANCH)
    with pytest.raises(Missing):
        git.worktrees(str(tmp_path))


@pytest.mark.supports("test_tree_py_refuses_a_run_whose_name_a_run_left_holds")
def test_a_branch_that_is_there_cant_take_a_worktree(tmp_path: Any) -> None:
    """Given: a repository with the branch rn-<name>.
    When: a worktree is added on that branch.
    Then: it couldn't run, with what git said."""
    repo = d.repository(str(tmp_path))
    d.git(repo, "branch", BRANCH)
    with pytest.raises(CantRun):
        git.add_worktree(repo, os.path.join(repo, ".claude", "worktrees", BRANCH), BRANCH)


@pytest.mark.supports("test_each_steps_end_commits_the_work_with_its_place")
def test_a_commit_holds_the_paths_with_the_message(tmp_path: Any) -> None:
    """Given: a run's worktree with invoicer/py.typed new.
    When: it's committed with a message.
    Then: it gives the commit's ID, which holds the file and the message."""
    run = d.run_of(d.repository(str(tmp_path)))
    open(os.path.join(run.worktree, "invoicer", "py.typed"), "w").close()
    commit = git.commit(run.worktree, ["invoicer/py.typed"], "generator: step 1")
    assert d.git(run.worktree, "rev-parse", "HEAD").strip() == commit
    assert "invoicer/py.typed" in d.git(run.worktree, "show", "--name-only", commit)
    assert "generator: step 1" in d.git(run.worktree, "log", "-1", "--format=%B")


@pytest.mark.supports("test_each_steps_end_commits_the_work_with_its_place")
def test_a_commit_of_nothing_changed_gives_head(tmp_path: Any) -> None:
    """Given: a run's worktree with nothing changed.
    When: invoicer/__init__.py is committed.
    Then: it gives the ID of HEAD, and makes no commit."""
    run = d.run_of(d.repository(str(tmp_path)))
    head = d.git(run.worktree, "rev-parse", "HEAD").strip()
    assert git.commit(run.worktree, ["invoicer/__init__.py"], "nothing") == head
    assert d.git(run.worktree, "rev-parse", "HEAD").strip() == head


@pytest.mark.supports("test_each_steps_end_commits_the_work_with_its_place")
def test_a_commit_of_a_path_that_isnt_there_cant_run(tmp_path: Any) -> None:
    """Given: a run's worktree.
    When: a path that isn't there is committed.
    Then: it couldn't run, with what git said."""
    run = d.run_of(d.repository(str(tmp_path)))
    with pytest.raises(CantRun):
        git.commit(run.worktree, ["nothing-here.txt"], "nothing")


@pytest.mark.supports("test_a_sign_off_pushes_the_work_and_keeps_a_draft_pull_request")
def test_a_branch_is_pushed_to_the_remote(tmp_path: Any) -> None:
    """Given: a run's worktree in a repository with a remote.
    When: its branch is pushed.
    Then: the remote holds the branch at the worktree's HEAD."""
    repo = d.repository(str(tmp_path))
    origin = d.remote_for(repo, str(tmp_path))
    run = d.run_of(repo)
    git.push(run.worktree, run.branch)
    head = d.git(run.worktree, "rev-parse", "HEAD").strip()
    assert d.git(origin, "rev-parse", run.branch).strip() == head


@pytest.mark.supports("test_a_push_without_a_remote_says_what_is_missing")
def test_a_push_with_no_remote_is_missing_it(tmp_path: Any) -> None:
    """Given: a run's worktree in a repository with no remote.
    When: its branch is pushed.
    Then: it's refused as missing the remote, naming it."""
    run = d.run_of(d.repository(str(tmp_path)))
    with pytest.raises(Missing, match="remote"):
        git.push(run.worktree, run.branch)


@pytest.mark.supports("test_a_push_without_a_remote_says_what_is_missing")
def test_a_push_to_a_remote_that_isnt_there_cant_run(tmp_path: Any) -> None:
    """Given: a run's worktree in a repository whose remote origin names a folder that isn't there.
    When: its branch is pushed.
    Then: it couldn't run, with what git said."""
    repo = d.repository(str(tmp_path))
    d.git(repo, "remote", "add", "origin", os.path.join(str(tmp_path), "gone.git"))
    run = d.run_of(repo)
    with pytest.raises(CantRun, match="git push failed"):
        git.push(run.worktree, run.branch)


@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
def test_a_file_is_given_as_a_commit_holds_it(tmp_path: Any) -> None:
    """Given: a run's worktree whose design tree was committed, then changed.
    When: the file is asked at the commit, and a file that commit doesn't hold.
    Then: the first gives its text then, and the second couldn't run."""
    run = d.run_of(d.repository(str(tmp_path)))
    path = d.tree_written(run)
    commit = d.git(run.worktree, "rev-parse", "HEAD").strip()
    with open(path, encoding="utf-8") as f:
        then = f.read()
    d.tree_written(run, {"goal": {"decided": "x", "by": "user"}, "deliverables": [], "work": []})
    relative = os.path.relpath(path, run.worktree)
    assert git.file_at(run.worktree, commit, relative) == then
    with pytest.raises(CantRun):
        git.file_at(run.worktree, commit, "nothing-here.txt")


@pytest.mark.supports("test_a_sign_off_pushes_the_work_and_keeps_a_draft_pull_request")
def test_a_draft_pull_request_is_opened_once_and_kept(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given: a run's branch with no pull request, and gh logged in.
    When: its draft pull request is opened twice.
    Then: each gives the same draft, and GitHub holds one pull request of the branch."""
    held = on_github(monkeypatch, tmp_path)
    run = d.run_of(d.repository(str(tmp_path)))
    first = gh.draft_pull_request(run.worktree, run.branch, "type hints for invoicer", "")
    again = gh.draft_pull_request(run.worktree, run.branch, "type hints for invoicer", "")
    assert first == again and first.draft is True
    assert list(d.read_json(held)["pulls"]) == [run.branch]


@pytest.mark.supports("test_a_push_without_a_login_of_gh_says_what_is_missing")
@pytest.mark.parametrize("call", ["draft", "ready", "comments", "issue"])
def test_each_command_with_no_login_is_missing_it(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch, call: str
) -> None:
    """Given: gh logged in to no account.
    When: a draft pull request is opened, marked ready, its comments read, or an issue opened.
    Then: each is refused as missing the login of gh."""
    on_github(monkeypatch, tmp_path, logged_in=False)
    run = d.run_of(d.repository(str(tmp_path)))
    with pytest.raises(Missing, match="gh auth login"):
        if call == "draft":
            gh.draft_pull_request(run.worktree, run.branch, "t", "b")
        elif call == "ready":
            gh.mark_ready(run.worktree, True)
        elif call == "comments":
            gh.comments(run.worktree, "2026-11-15T09:00:00Z")
        else:
            gh.open_issue("lovaizu/ccpm", "t", "b")


@pytest.mark.supports("test_the_pull_request_is_marked_ready_once_no_deliverable_is_left")
@pytest.mark.parametrize("ready", [True, False])
def test_a_pull_request_is_marked_ready_or_a_draft_again(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch, ready: bool
) -> None:
    """Given: a run's branch with a draft pull request, and gh logged in.
    When: it's marked ready, or a draft again.
    Then: it gives the pull request as it stands, and GitHub holds it so."""
    run = d.run_of(d.repository(str(tmp_path)))
    pulls = {run.branch: {"number": 1, "draft": True, "comments": []}}
    held = on_github(monkeypatch, tmp_path, pulls=pulls)
    assert gh.mark_ready(run.worktree, ready).draft is (not ready)
    assert d.read_json(held)["pulls"][run.branch]["draft"] is (not ready)


@pytest.mark.supports("test_gm_on_the_pull_request_handed_over_marks_it_a_draft_again")
def test_a_branch_with_no_pull_request_cant_be_marked(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given: a run's branch with no pull request, and gh logged in.
    When: its pull request is marked ready.
    Then: it's refused as missing the pull request."""
    on_github(monkeypatch, tmp_path)
    run = d.run_of(d.repository(str(tmp_path)))
    with pytest.raises(Missing):
        gh.mark_ready(run.worktree, True)


@pytest.mark.supports("test_gm_alone_reads_the_users_comments_since_the_sign_off")
@pytest.mark.parametrize(
    ("since", "bodies"),
    [
        ("2026-11-15T09:00:00Z", ["After."]),
        ("2026-11-15T08:00:00Z", ["Before.", "After."]),
        ("2026-11-15T11:00:00Z", []),
    ],
)
def test_comments_are_given_from_after_a_moment_in_the_order_made(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch, since: str, bodies: list[str]
) -> None:
    """Given: a run's pull request with a comment at 08:30 and one at 10:00.
    When: its comments since 09:00, since 08:00, and since 11:00 are asked.
    Then: it gives the one after, both in the order made, and none."""
    run = d.run_of(d.repository(str(tmp_path)))
    comments = [
        {"body": "Before.", "createdAt": "2026-11-15T08:30:00Z"},
        {"body": "After.", "createdAt": "2026-11-15T10:00:00Z"},
    ]
    pulls = {run.branch: {"number": 1, "draft": True, "comments": comments}}
    on_github(monkeypatch, tmp_path, pulls=pulls)
    assert [c.body for c in gh.comments(run.worktree, since)] == bodies


@pytest.mark.supports("test_gm_alone_reads_the_users_comments_since_the_sign_off")
def test_a_line_comment_is_given_with_its_path_and_line_among_the_others_in_the_order_made(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given: a run's pull request with a line comment on invoicer/render.py, line 12, at 10:30,
    and a comment of its conversation at 10:00 and one at 11:00, each by the account logged in.
    When: its comments since 09:00 are asked.
    Then: it gives the three in the order made, the line comment with its path and line, and the
    others with the path "" and no line."""
    run = d.run_of(d.repository(str(tmp_path)))
    talk = [
        {"body": "Talk at ten.", "createdAt": "2026-11-15T10:00:00Z"},
        {"body": "Talk at eleven.", "createdAt": "2026-11-15T11:00:00Z"},
    ]
    on_line = {
        "body": "Leave this file out.",
        "created_at": "2026-11-15T10:30:00Z",
        "path": "invoicer/render.py",
        "line": 12,
    }
    pull = {"number": 1, "draft": True, "comments": talk, "review_comments": [on_line]}
    on_github(monkeypatch, tmp_path, pulls={run.branch: pull})
    given = [(c.body, c.path, c.line) for c in gh.comments(run.worktree, "2026-11-15T09:00:00Z")]
    assert given == [
        ("Talk at ten.", "", None),
        ("Leave this file out.", "invoicer/render.py", 12),
        ("Talk at eleven.", "", None),
    ]


@pytest.mark.supports("test_gm_alone_reads_the_users_comments_since_the_sign_off")
def test_comments_of_any_other_account_bots_among_them_are_left_out(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given: a run's pull request with a comment of its conversation by another account, a line
    comment by a bot, and one comment of each kind by the account logged in, all after 09:00.
    When: its comments since 09:00 are asked.
    Then: it gives only the two by the account logged in, each with that account as its author."""
    run = d.run_of(d.repository(str(tmp_path)))
    talk = [
        {"body": "A reviewer's.", "createdAt": "2026-11-15T10:00:00Z", "author": {"login": "rev"}},
        {"body": "The user's talk.", "createdAt": "2026-11-15T10:10:00Z"},
    ]
    lines = [
        {
            "body": "A bot's.",
            "created_at": "2026-11-15T10:20:00Z",
            "path": "invoicer/render.py",
            "line": 3,
            "user": {"login": "github-actions[bot]", "type": "Bot"},
        },
        {
            "body": "The user's line.",
            "created_at": "2026-11-15T10:30:00Z",
            "path": "invoicer/render.py",
            "line": 4,
        },
    ]
    pull = {"number": 1, "draft": True, "comments": talk, "review_comments": lines}
    on_github(monkeypatch, tmp_path, pulls={run.branch: pull})
    given = [(c.author, c.body) for c in gh.comments(run.worktree, "2026-11-15T09:00:00Z")]
    assert given == [("<account>", "The user's talk."), ("<account>", "The user's line.")]


@pytest.mark.supports("test_a_lesson_approved_opens_an_issue_on_rns_repository_word_for_word")
def test_an_issue_is_opened_with_its_words(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """Given: gh logged in.
    When: an issue is opened on lovaizu/ccpm with a title and a body.
    Then: it gives the issue's URL, and GitHub holds the issue there with the body word for word."""
    held = on_github(monkeypatch, tmp_path)
    url = gh.open_issue("lovaizu/ccpm", "rn: a lesson", "The words, as signed off.")
    assert url.endswith("/issues/1")
    assert d.read_json(held)["issues"] == [
        {"repository": "lovaizu/ccpm", "title": "rn: a lesson", "body": "The words, as signed off."}
    ]

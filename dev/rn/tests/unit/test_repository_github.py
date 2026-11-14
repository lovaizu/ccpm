"""The unit cases of repository/github.py, the gh commands that tree.py runs by it, through
`logged_in`, `pull_request`, `open_draft`, `comments`, `mark_ready`, `mark_draft`, and
`open_issue`, with the double of gh, whose results come from gh's recorded runs and manual."""

from __future__ import annotations

import json
from typing import Any

import pytest
from fault import Missing
from repository.github import (
    RN_REPOSITORY,
    Comment,
    PullRequest,
    comments,
    logged_in,
    mark_draft,
    mark_ready,
    open_draft,
    open_issue,
    pull_request,
)
from rn_example import LESSON, write
from rn_parts import environ

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

BRANCH = "rn/20261114-type-hints-for-invoicer"


def github(base: str, held: dict[str, Any]) -> dict[str, str]:
    """The environment of gh with GitHub holding what's given."""
    env = environ(base)
    write(base, "github.json", json.dumps(held))
    return env


def holding(env: dict[str, str]) -> dict[str, Any]:
    with open(env["RN_GH_STATE"], encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.supports("test_push_pushes_the_runs_branch_and_opens_its_draft_pull_request_once")
def test_logged_in_passes_where_gh_finds_the_login(tmp_path: Any):
    """Given gh logged in
    When the login is checked
    Then nothing is missing"""
    env = github(str(tmp_path), {"logged_in": True, "pulls": {}, "issues": []})
    assert logged_in(str(tmp_path), env) is None


@pytest.mark.supports("test_push_without_gh_logged_in_says_whats_missing_and_pushes_nothing")
def test_logged_in_says_the_login_is_missing_with_what_clears_it(tmp_path: Any):
    """Given gh logged in nowhere
    When the login is checked
    Then it's Missing, naming `gh auth login`"""
    env = github(str(tmp_path), {"logged_in": False, "pulls": {}, "issues": []})
    with pytest.raises(Missing, match="gh auth login"):
        logged_in(str(tmp_path), env)


@pytest.mark.supports("test_push_pushes_the_runs_branch_and_opens_its_draft_pull_request_once")
def test_pull_request_of_a_branch_with_none_is_none(tmp_path: Any):
    """Given GitHub holding no pull request
    When the branch's pull request is asked for
    Then there's none"""
    env = github(str(tmp_path), {"logged_in": True, "pulls": {}, "issues": []})
    assert pull_request(str(tmp_path), BRANCH, env) is None


@pytest.mark.supports("test_push_pushes_the_runs_branch_and_opens_its_draft_pull_request_once")
def test_open_draft_opens_one_that_pull_request_then_gives(tmp_path: Any):
    """Given GitHub holding no pull request
    When a draft is opened for the branch
    Then it's a draft at a URL of a pull request, the one the branch then has"""
    env = github(str(tmp_path), {"logged_in": True, "pulls": {}, "issues": []})
    opened = open_draft(str(tmp_path), BRANCH, "type hints for invoicer", env)
    assert opened.draft and opened.url.endswith("/pull/1")
    assert pull_request(str(tmp_path), BRANCH, env) == opened


@pytest.mark.supports("test_gm_alone_has_tree_py_give_the_users_comments_since_the_sign_off")
def test_comments_gives_those_made_at_or_after_the_time_in_order(tmp_path: Any):
    """Given the branch's pull request with comments of 1 January 2026, 2 January, and 3 January
    When its comments since 2 January are asked for
    Then they're the last two, in order"""
    said = [
        {"body": "Old.", "createdAt": "2026-01-01T00:00:00Z"},
        {"body": "Rates read like amounts.", "createdAt": "2026-01-02T00:00:00Z"},
        {"body": "And totals.", "createdAt": "2026-01-03T00:00:00Z"},
    ]
    pulls = {BRANCH: {"number": 1, "draft": True, "comments": said}}
    env = github(str(tmp_path), {"logged_in": True, "pulls": pulls, "issues": []})
    assert comments(str(tmp_path), BRANCH, "2026-01-02T00:00:00Z", env) == (
        Comment("Rates read like amounts.", "2026-01-02T00:00:00Z"),
        Comment("And totals.", "2026-01-03T00:00:00Z"),
    )


@pytest.mark.supports(
    "test_ready_marks_the_pull_request_ready_once_every_deliverable_is_signed_off"
)
def test_mark_ready_leaves_the_pull_request_no_longer_a_draft(tmp_path: Any):
    """Given the branch's draft pull request
    When it's marked ready
    Then it's no longer a draft"""
    pulls = {BRANCH: {"number": 1, "draft": True, "comments": []}}
    env = github(str(tmp_path), {"logged_in": True, "pulls": pulls, "issues": []})
    mark_ready(str(tmp_path), BRANCH, env)
    assert pull_request(str(tmp_path), BRANCH, env) == PullRequest(
        "http://github.com/owner/repo/pull/1", False
    )


@pytest.mark.supports("test_gm_after_done_sends_the_pull_request_handed_over_back_to_a_draft")
def test_mark_draft_leaves_the_pull_request_a_draft_again(tmp_path: Any):
    """Given the branch's pull request marked ready
    When it's marked a draft
    Then it's a draft again"""
    pulls = {BRANCH: {"number": 1, "draft": False, "comments": []}}
    env = github(str(tmp_path), {"logged_in": True, "pulls": pulls, "issues": []})
    mark_draft(str(tmp_path), BRANCH, env)
    assert pull_request(str(tmp_path), BRANCH, env) == PullRequest(
        "http://github.com/owner/repo/pull/1", True
    )


@pytest.mark.supports("test_a_lesson_signed_off_by_the_users_ty_opens_its_issue_on_rns_repository")
def test_open_issue_opens_it_on_rns_repository_with_the_first_line_as_its_title(tmp_path: Any):
    """Given the walkthrough's lesson
    When its issue is opened
    Then GitHub holds it on rn's repository, titled by its first line and holding the rest, and its
    URL is given"""
    env = github(str(tmp_path), {"logged_in": True, "pulls": {}, "issues": []})
    url = open_issue(str(tmp_path), LESSON, env)
    title, body = LESSON.split("\n\n", 1)
    assert holding(env)["issues"] == [{"repository": RN_REPOSITORY, "title": title, "body": body}]
    assert url.endswith("/issues/1")

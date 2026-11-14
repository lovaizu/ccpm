"""The unit cases of the double of gh, gh/gh_double.py, which rn's tests run in place of GitHub's
command line, through `main`, as the architecture best practice tests each double as the part's
unit tests test the part: each result the one that its record shows."""

from __future__ import annotations

import json
from typing import Any

import pytest
from gh_double import AUTH, MANUAL, PR_VIEW, line, main
from rn_example import write

BRANCH = "rn/20261114-type-hints-for-invoicer"


def holding(base: str, **held: Any) -> dict[str, str]:
    """The environment of the double with GitHub holding what's given beside a login."""
    state = {"logged_in": True, "pulls": {}, "issues": [], **held}
    return {"RN_GH_STATE": write(base, "github.json", json.dumps(state))}


def state(env: dict[str, str]) -> dict[str, Any]:
    with open(env["RN_GH_STATE"], encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.supports("test_push_without_gh_logged_in_says_whats_missing_and_pushes_nothing")
def test_auth_status_without_a_login_gives_what_the_recorded_run_gave(tmp_path: Any):
    """Given GitHub holding no login
    When `gh auth status` runs
    Then it gives the exit code and words of gh 2.102.1's run without a login"""
    ran = line(AUTH, "gh auth status finds no login")
    env = holding(str(tmp_path), logged_in=False)
    assert main(["auth", "status"], env) == (ran["exit"], ran["stdout"], ran["stderr"])


@pytest.mark.supports("test_push_pushes_the_runs_branch_and_opens_its_draft_pull_request_once")
def test_auth_status_with_a_login_gives_0(tmp_path: Any):
    """Given GitHub holding a login
    When `gh auth status` runs
    Then it gives 0"""
    assert main(["auth", "status"], holding(str(tmp_path)))[0] == 0


@pytest.mark.supports("test_push_pushes_the_runs_branch_and_opens_its_draft_pull_request_once")
def test_pr_view_of_a_branch_with_none_says_so_naming_the_branch(tmp_path: Any):
    """Given GitHub holding no pull request
    When `gh pr view <branch> --json url,isDraft` runs
    Then it gives 1, saying no pull request was found for the branch, as the recorded run did"""
    code, out, err = main(["pr", "view", BRANCH, "--json", "url,isDraft"], holding(str(tmp_path)))
    assert (code, out) == (1, "") and err == f'no pull requests found for branch "{BRANCH}"\n'


@pytest.mark.supports("test_push_pushes_the_runs_branch_and_opens_its_draft_pull_request_once")
def test_pr_create_opens_a_draft_whose_url_pr_view_then_gives(tmp_path: Any):
    """Given GitHub holding no pull request
    When `gh pr create --draft --head <branch>` runs, and then `gh pr view <branch> --json
    url,isDraft`
    Then the first prints the URL of pull request 1 in the manual's form, and the second gives it
    as a draft"""
    env = holding(str(tmp_path))
    created = main(
        ["pr", "create", "--draft", "--head", BRANCH, "--title", "t", "--body", "b"], env
    )
    viewed = json.loads(main(["pr", "view", BRANCH, "--json", "url,isDraft"], env)[1])
    assert created == (0, "http://github.com/owner/repo/pull/1\n", "")
    assert viewed == {"url": "http://github.com/owner/repo/pull/1", "isDraft": True}


@pytest.mark.supports("test_gm_alone_has_tree_py_give_the_users_comments_since_the_sign_off")
def test_pr_view_gives_each_comment_in_the_recorded_comments_form(tmp_path: Any):
    """Given the branch's pull request with one comment
    When `gh pr view <branch> --json comments` runs
    Then the comment holds its body and time, beside each other field of the recorded comment"""
    pulls = {
        BRANCH: {
            "number": 1,
            "draft": True,
            "comments": [{"body": "Rates.", "createdAt": "2026-01-02T00:00:00Z"}],
        }
    }
    (comment,) = json.loads(
        main(["pr", "view", BRANCH, "--json", "comments"], holding(str(tmp_path), pulls=pulls))[1]
    )["comments"]
    recorded = json.loads(
        line(PR_VIEW, "gh pr view gives the pull request with its comments")["stdout"]
    )
    assert set(comment) == set(recorded["comments"][0])
    assert (comment["body"], comment["createdAt"]) == ("Rates.", "2026-01-02T00:00:00Z")


@pytest.mark.supports(
    "test_ready_marks_the_pull_request_ready_once_every_deliverable_is_signed_off"
)
def test_pr_ready_leaves_the_pull_request_no_longer_a_draft(tmp_path: Any):
    """Given the branch's draft pull request
    When `gh pr ready <branch>` runs
    Then it gives 0, and GitHub holds it no longer a draft"""
    env = holding(str(tmp_path), pulls={BRANCH: {"number": 1, "draft": True, "comments": []}})
    assert (
        main(["pr", "ready", BRANCH], env)[0]
        == line(MANUAL, "gh pr ready marks the pull request ready")["exit"]
    )
    assert state(env)["pulls"][BRANCH]["draft"] is False


@pytest.mark.supports("test_a_lesson_signed_off_by_the_users_ty_opens_its_issue_on_rns_repository")
def test_issue_create_keeps_the_issue_and_prints_its_url_in_the_manuals_form(tmp_path: Any):
    """Given GitHub holding no issue
    When `gh issue create --repo lovaizu/ccpm --title t --body b` runs
    Then it prints the URL of issue 1, and GitHub holds the issue"""
    env = holding(str(tmp_path))
    created = main(
        ["issue", "create", "--repo", "lovaizu/ccpm", "--title", "t", "--body", "b"], env
    )
    assert created == (0, "http://github.com/owner/repo/issues/1\n", "")
    assert state(env)["issues"] == [{"repository": "lovaizu/ccpm", "title": "t", "body": "b"}]


@pytest.mark.supports("test_push_pushes_the_runs_branch_and_opens_its_draft_pull_request_once")
def test_a_command_tree_py_doesnt_run_fails_the_test(tmp_path: Any):
    """Given GitHub holding a login
    When `gh pr merge` runs
    Then the double fails, as no record shows it"""
    with pytest.raises(AssertionError, match="pr merge"):
        main(["pr", "merge", BRANCH], holding(str(tmp_path)))

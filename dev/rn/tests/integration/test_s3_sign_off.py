"""The integration cases of S3, a sign-off: tree.py pushes the work and keeps the draft pull
request, the orchestrator puts the plan or a deliverable up, the user's /rn:ty approves it and
/rn:gm sends it back, with what to change or alone for their comments on the pull request, and the
work that rests on the sign-off waits for it. The test plays the user, the orchestrator, and the
tree-keeper, and the double of gh stands in for GitHub."""

from __future__ import annotations

import json
import os

import pytest
from claude_code import Conversation
from rn_example import (
    ANSWERED,
    CAN_DO,
    DECIMAL,
    HINTS,
    TYPED,
    Repo,
    Run,
    begin,
    comment_on,
    conversation,
    git,
    github,
    keeper_writes,
    make_repo,
    started,
    text_of,
    tree,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


def put_up(
    conv: Conversation, repo: Repo, run: Run, of: str, can_do: str = "", *decisions: str
) -> None:
    path = os.path.join(repo.temp, "sign-off.json")
    if os.path.exists(path):
        os.remove(path)
    conv.write(
        None,
        path,
        json.dumps({"of": of, "can_do": can_do, "decisions": list(decisions), "words": ""}),
    )
    done = conv.bash(tree(repo, "sign-off", run.folder, path))
    assert done.exit_code == 0, done.output


def sign_offs(run: Run) -> list[dict]:
    return json.loads(text_of(os.path.join(run.worktree, run.folder, "sign-offs.json")))


@pytest.mark.supports("S3", "tree.py", "repository", "orchestrator")
def test_push_pushes_the_runs_branch_and_opens_its_draft_pull_request_once(
    conv: Conversation, repo: Repo, run: Run
):
    """Given a run begun, gh logged in, and no pull request of its branch
    When the orchestrator runs `tree.py push` twice
    Then the remote holds the run's branch, GitHub one draft pull request of it, and each push
    prints its URL"""
    first = conv.bash(tree(repo, "push", run.folder))
    second = conv.bash(tree(repo, "push", run.folder))
    branch = git(run.worktree, "branch", "--show-current").strip()
    assert git(repo.remote, "branch", "--list", branch).strip()
    assert list(github(repo)["pulls"]) == [branch] and github(repo)["pulls"][branch]["draft"]
    assert first.output == second.output and first.output.strip().endswith("/pull/1")


@pytest.mark.supports("S3", "tree.py", "repository", "Point")
def test_push_without_gh_logged_in_says_whats_missing_and_pushes_nothing(tmp_path):
    """Given a run begun, with gh logged in nowhere
    When the orchestrator runs `tree.py push`
    Then tree.py exits 1 naming `gh auth login`, and GitHub holds no pull request"""
    repo = make_repo(os.path.realpath(str(tmp_path)), logged_in=False)
    conv = conversation(repo)
    run = begin(conv, repo)
    pushed = conv.bash(tree(repo, "push", run.folder))
    assert pushed.exit_code == 1 and "gh auth login" in pushed.output
    assert github(repo)["pulls"] == {}


@pytest.mark.supports("S3", "Sign-off", "tree.py", "user")
def test_the_users_ty_signs_off_the_plan_waiting(conv: Conversation, repo: Repo, run: Run):
    """Given the plan put up for sign-off
    When the user types /rn:ty
    Then the command loads, saying it signed the plan off, and sign-offs.json holds the plan
    signed"""
    put_up(conv, repo, run, "plan")
    typed = conv.type("/rn:ty")
    assert not typed.shown and "plan" in typed.output
    assert [(each["of"], each["state"]) for each in sign_offs(run)] == [("plan", "signed")]


@pytest.mark.supports("S3", "Sign-off", "user")
def test_ty_with_nothing_waiting_doesnt_load(conv: Conversation, repo: Repo, run: Run):
    """Given a run with nothing put up
    When the user types /rn:ty
    Then the command doesn't load, and Claude Code shows what tree.py said: that nothing waits"""
    typed = conv.type("/rn:ty")
    assert typed.output == "" and "nothing waits" in typed.shown


@pytest.mark.supports("S3", "Sign-off", "tree-keeper", "Deliverable")
def test_once_the_hints_are_signed_off_the_typed_marker_is_marked_doing(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints done, put up with what its people can do and the Decimal decision, and the
    typed marker waiting on them
    When the user types /rn:ty and the tree-keeper writes the tree on it
    Then tree.py marks the typed marker doing"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    done = dict(
        ANSWERED,
        deliverables=[
            {
                "name": ANSWERED["deliverables"][0]["name"],
                "path": HINTS,
                "kind": "code",
                "status": "done",
            },
            ANSWERED["deliverables"][1],
        ],
    )
    keeper_writes(keeper, repo, run, done, "The hints meet each condition.")
    put_up(conv, repo, run, "plan")
    conv.type("/rn:ty")
    put_up(conv, repo, run, HINTS, CAN_DO, DECIMAL)
    conv.type("/rn:ty")
    wrote = keeper_writes(keeper, repo, run, done, "The user signed the hints off.")
    assert json.loads(wrote.output)["doing"] == [TYPED]


@pytest.mark.supports("S3", "Sign-off", "user")
def test_gm_with_what_to_change_sends_the_sign_off_back_and_carries_their_words(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints put up for sign-off
    When the user types `/rn:gm type rates apart from amounts`
    Then the command loads with their words as typed, and sign-offs.json holds the hints sent
    back"""
    put_up(conv, repo, run, HINTS, CAN_DO, DECIMAL)
    typed = conv.type("/rn:gm type rates apart from amounts")
    assert "type rates apart from amounts" in typed.output
    assert sign_offs(run)[-1]["state"] == "sent back"


@pytest.mark.supports("S3", "tree.py", "repository", "user", "Comment")
def test_gm_alone_has_tree_py_give_the_users_comments_since_the_sign_off(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the work pushed with its draft pull request, a comment on it before the hints were put
    up and one after
    When the user types /rn:gm alone and the orchestrator runs `tree.py comments`
    Then tree.py prints the comment after the sign-off was put up, and not the one before"""
    conv.bash(tree(repo, "push", run.folder))
    comment_on(repo, "An old note.", "2000-01-01T00:00:00Z")
    put_up(conv, repo, run, HINTS, CAN_DO, DECIMAL)
    comment_on(repo, "Rates read like amounts.", "2999-01-01T00:00:00Z")
    conv.type("/rn:gm")
    printed = conv.bash(tree(repo, "comments", run.folder))
    assert "Rates read like amounts." in printed.output and "An old note." not in printed.output


@pytest.mark.supports("S3", "orchestrator", "guard")
def test_the_orchestrator_cant_approve_for_the_user_by_the_skill_tool(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the plan put up for sign-off
    When the main conversation calls the Skill tool on rn:ty
    Then the call is refused, and the plan still waits"""
    put_up(conv, repo, run, "plan")
    called = conv.skill("rn:ty", "")
    assert called.blocked
    assert sign_offs(run)[-1]["state"] == "waiting"

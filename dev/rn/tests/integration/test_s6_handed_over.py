"""The integration cases of S6, the work handed over: each change to a best practice that the
user takes becomes a deliverable, each general lesson goes to rn's repository as an issue only on
the user's /rn:ty, the whole pull request is read against the goal before it's ready, tree.py
marks it ready only once every deliverable is done and signed off, the user's /rn:ty after Done
signs off the pull request handed over and leaves it ready for their merge, and their /rn:gm after
Done sends it back to a draft. The test plays the user, the
orchestrator, and the tree-keeper, and the double of gh stands in for GitHub."""

from __future__ import annotations

import json
import os

import pytest
from claude_code import Conversation
from rn_example import (
    ALL_DONE,
    ANSWERED,
    HINTS,
    LESSON,
    TYPED,
    TYPED_NAME,
    Repo,
    Run,
    code_deliverable,
    condition,
    decided,
    github,
    keeper_writes,
    started,
    text_of,
    tree,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


def put_up(conv: Conversation, repo: Repo, run: Run, of: str, words: str = "") -> int:
    path = os.path.join(repo.temp, f"{of.replace('/', '-')}.json")
    conv.write(None, path, json.dumps({"of": of, "can_do": "", "decisions": [], "words": words}))
    return conv.bash(tree(repo, "sign-off", run.folder, path)).exit_code or 0


def handed_over(conv: Conversation, repo: Repo, run: Run) -> None:
    """Both deliverables done, and the plan and each of them signed off, with the work pushed."""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ALL_DONE, "Both deliverables meet each condition.")
    for of in ("plan", HINTS, TYPED):
        put_up(conv, repo, run, of)
        conv.type("/rn:ty")
    conv.bash(tree(repo, "push", run.folder))


@pytest.mark.supports("S6", "Sign-off", "tree.py", "user")
def test_a_lesson_signed_off_by_the_users_ty_opens_its_issue_on_rns_repository(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the work handed over, and a lesson put up word for word
    When the user types /rn:ty
    Then GitHub holds one issue on lovaizu/ccpm whose title and body are the lesson's words, and
    the command loads with its URL"""
    handed_over(conv, repo, run)
    put_up(conv, repo, run, "lesson", LESSON)
    typed = conv.type("/rn:ty")
    title, body = LESSON.split("\n\n", 1)
    assert github(repo)["issues"] == [{"repository": "lovaizu/ccpm", "title": title, "body": body}]
    assert "/issues/1" in typed.output


@pytest.mark.supports("S6", "Sign-off", "user")
def test_a_lesson_the_user_sends_back_opens_no_issue(conv: Conversation, repo: Repo, run: Run):
    """Given the work handed over, and a lesson put up
    When the user types /rn:gm to turn it down
    Then GitHub holds no issue"""
    handed_over(conv, repo, run)
    put_up(conv, repo, run, "lesson", LESSON)
    conv.type("/rn:gm")
    assert github(repo)["issues"] == []


@pytest.mark.supports("S6", "Sign-off", "tree.py")
def test_a_lesson_without_its_words_cant_be_put_up(conv: Conversation, repo: Repo, run: Run):
    """Given the work handed over
    When the orchestrator puts up a lesson with no words
    Then tree.py exits 1 naming `words`, as the user signs off only what they read"""
    handed_over(conv, repo, run)
    assert put_up(conv, repo, run, "lesson") == 1


@pytest.mark.supports("S6", "tree.py", "repository", "orchestrator")
def test_ready_marks_the_pull_request_ready_once_every_deliverable_is_signed_off(
    conv: Conversation, repo: Repo, run: Run
):
    """Given both deliverables done and signed off, and the work pushed with its draft pull request
    When the orchestrator runs `tree.py ready`
    Then tree.py exits 0 with the pull request's URL, and GitHub holds it no longer a draft"""
    handed_over(conv, repo, run)
    ready = conv.bash(tree(repo, "ready", run.folder))
    (pull,) = github(repo)["pulls"].values()
    assert ready.exit_code == 0 and ready.output.strip().endswith("/pull/1") and not pull["draft"]


@pytest.mark.supports("S6", "tree.py", "Deliverable")
def test_ready_refuses_while_a_deliverable_isnt_done(conv: Conversation, repo: Repo, run: Run):
    """Given the hints done and signed off, and the typed marker open again after the whole pull
    request was read
    When the orchestrator runs `tree.py ready`
    Then tree.py exits 1 naming the typed marker, and the pull request stays a draft"""
    handed_over(conv, repo, run)
    _, keeper = started(conv, repo, run, "tree-keeper")
    again = dict(ALL_DONE, deliverables=[ALL_DONE["deliverables"][0], ANSWERED["deliverables"][1]])
    keeper_writes(keeper, repo, run, again, "The typed marker names no file of the hints.")
    refused = conv.bash(tree(repo, "ready", run.folder))
    (pull,) = github(repo)["pulls"].values()
    assert refused.exit_code == 1 and TYPED in refused.output and pull["draft"]


@pytest.mark.supports("S6", "orchestrator", "tree-keeper", "Decision", "Cut")
def test_a_clash_the_whole_pull_request_read_finds_starts_the_rounds_again_from_its_decision(
    conv: Conversation, repo: Repo, run: Run
):
    """Given both deliverables done and signed off, and the work pushed
    When the orchestrator's read of the whole pull request finds that the typed marker contradicts
    the hints, and the tree-keeper writes the decision it changes, with the typed marker open again
    Then tree.py marks the typed marker doing, and the generator's cut of it holds the changed
    decision"""
    handed_over(conv, repo, run)
    _, keeper = started(conv, repo, run, "tree-keeper")
    changed = decided("Where the marker lies", "invoicer/py.typed, in the package the hints type")
    typed = code_deliverable(
        TYPED_NAME, TYPED, condition("N1", changed), inputs=[HINTS], preconditions=[HINTS]
    )
    reopened = dict(ALL_DONE, deliverables=[ALL_DONE["deliverables"][0], typed])
    wrote = keeper_writes(keeper, repo, run, reopened, "The typed marker contradicts the hints.")
    given, _ = started(conv, repo, run, "generator", TYPED)
    held = json.loads(text_of(os.path.join(run.worktree, given["cut"])))
    assert json.loads(wrote.output)["doing"] == [TYPED] and changed in held["decisions"]


@pytest.mark.supports("S6", "tree-keeper", "Best practice", "Deliverable")
def test_a_change_to_a_best_practice_the_user_takes_is_added_as_a_meta_deliverable(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the work handed over
    When the tree-keeper adds the change to the code best practice that the user took, as a
    deliverable of the kind meta at .rn/best-practices/code/
    Then tree.py marks it doing, once the plan it changes is signed off"""
    handed_over(conv, repo, run)
    _, keeper = started(conv, repo, run, "tree-keeper")
    meta = {
        "name": "rn's code best practice asks for py.typed in a library's hints",
        "path": ".rn/best-practices/code/",
        "kind": "meta",
        "inputs": [],
        "preconditions": [],
        "status": "open",
        "necessary_conditions": [],
    }
    added = dict(ALL_DONE, deliverables=[*ALL_DONE["deliverables"], meta])
    wrote = keeper_writes(keeper, repo, run, added, "The user took the change.")
    assert json.loads(wrote.output)["doing"] == [".rn/best-practices/code/"]


@pytest.mark.supports("S6", "tree.py", "repository", "Sign-off", "user")
def test_gm_after_done_sends_the_pull_request_handed_over_back_to_a_draft(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the pull request marked ready, and Done shown
    When the user types /rn:gm with what to change
    Then the command loads, GitHub holds the pull request a draft again, and the run's sign-offs
    keep the pull request handed over sent back"""
    handed_over(conv, repo, run)
    conv.bash(tree(repo, "ready", run.folder))
    conv.stop("Done. The pull request is ready for your merge.")
    typed = conv.type("/rn:gm Rates should read apart from amounts.")
    (pull,) = github(repo)["pulls"].values()
    kept = json.loads(text_of(os.path.join(run.worktree, run.folder, "sign-offs.json")))
    assert not typed.blocked and pull["draft"]
    assert kept[-1]["of"] == "pull request" and kept[-1]["state"] == "sent back"


@pytest.mark.supports("S6", "tree.py", "Sign-off", "user")
def test_ty_after_done_signs_off_the_pull_request_handed_over_and_leaves_it_ready(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the pull request marked ready, and Done shown
    When the user types /rn:ty
    Then the command loads, GitHub holds the pull request ready and unmerged, and the run's
    sign-offs keep the pull request handed over signed"""
    handed_over(conv, repo, run)
    conv.bash(tree(repo, "ready", run.folder))
    conv.stop("Done. The pull request is ready for your merge.")
    typed = conv.type("/rn:ty")
    (pull,) = github(repo)["pulls"].values()
    kept = json.loads(text_of(os.path.join(run.worktree, run.folder, "sign-offs.json")))
    assert not typed.blocked and set(pull) == {"number", "draft", "comments"} and not pull["draft"]
    assert kept[-1]["of"] == "pull request" and kept[-1]["state"] == "signed"


@pytest.mark.supports("S6", "user")
def test_rn_leaves_the_merge_to_the_user(conv: Conversation, repo: Repo, run: Run):
    """Given the pull request marked ready
    When the orchestrator's turn ends with Done
    Then GitHub holds the pull request open and unmerged, as no command of tree.py merges"""
    handed_over(conv, repo, run)
    conv.bash(tree(repo, "ready", run.folder))
    conv.stop("Done. The pull request is ready for your merge.")
    (pull,) = github(repo)["pulls"].values()
    assert set(pull) == {"number", "draft", "comments"} and not pull["draft"]

"""The integration cases of S6 and S7: the work handed over, and each lesson sent to rn's
repository. Each path of their sequence: a change to a best practice that the user takes, added as
a deliverable; each round of the run read for its lessons; a lesson that the user approves, opened
as an issue on rn's repository word for word for rn's developers, or sends back; and the pull
request marked ready and put up, then sent back, marked a draft again, or approved, left ready
for the user's merge."""

from __future__ import annotations

import json

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench

LESSON = (
    "The code best practice asks for each public function's types, but says nothing of a"
    " library's py.typed marker, without which no caller's type checker reads them."
)


@pytest.mark.supports("S6", "Round", "More kept")
def test_every_round_of_a_deliverable_is_read_for_its_lessons(b: Bench) -> None:
    """Given: "Type hints in each file of invoicer" judged twice: a first round with N2 in more,
    kept, and a second round with every condition good.
    When: the orchestrator runs tree.py round invoicer to find each lesson.
    Then: it gives both rounds, the latest last, the first with N2 in more and its good_when."""
    walk, cut, _ = w.first_round(b, {"N2": w.SHOWN_AS_TYPED})
    w.short_by_n2_kept(b, walk)
    generator, again = w.generator_started(walk)
    w.made(b, walk, generator, again)
    walk.said = w.reached(b, generator, "done", "Made.").said
    w.evaluated(b, walk, w.kinds_of(again))
    rounds = w.printed(walk.c.bash(b.tree("round", cut["deliverable"])))
    assert [r["number"] for r in rounds] == [1, 2]
    # The code best practice's first group holds its N2, and the refactor one's second group an N2
    # of its own, which the first round puts in more alike.
    first = [m for each in rounds[0]["answers"] for m in each["more"]]
    assert first == [{"question": "N2", "good_when": w.SHOWN_AS_TYPED}] * 2
    assert not [m for each in rounds[1]["answers"] for m in each["more"]]


@pytest.mark.supports("S6", "Deliverable", "Point", "Best practice")
def test_a_change_to_a_best_practice_the_user_takes_is_added_as_a_deliverable(b: Bench) -> None:
    """Given: the walkthrough's plan signed off.
    When: the orchestrator puts a change to the code best practice to the user, the user takes it,
    and the tree-keeper adds it as a deliverable.
    Then: the design tree holds the best practice made on the run as a deliverable of its own, in
    .rn/best-practices/code/."""
    walk = w.planned(b)
    assert not walk.c.stop(f"A change to the code best practice:\n  {LESSON}").blocked
    assert not walk.c.type("yes").blocked
    added = w.deliverable(
        "A maker of a typed library ships its marker", ".rn/best-practices/code", "meta"
    )
    change = {"nodes": {"deliverables/2": added}, "more": []}
    w.keeper_writes(b, walk, "The user took the change.", change, "yes")
    paths = [d["path"] for d in w.tree_in(walk)["deliverables"]]
    assert paths == [w.HINTS_PATH, w.TYPED_PATH, ".rn/best-practices/code"]


@pytest.mark.supports("S7", "rn's developers", "Sign-off", "repository")
def test_a_lesson_approved_opens_an_issue_on_rns_repository_word_for_word(b: Bench) -> None:
    """Given: the walkthrough's plan signed off, and a general lesson found in its rounds.
    When: the orchestrator runs tree.py put-up lesson with the lesson's words, ends its turn with
    them, the user types /rn:ty, and the orchestrator runs tree.py approve.
    Then: tree.py approve gives the issue's URL, and GitHub holds the issue on lovaizu/ccpm, rn's
    repository, with the lesson's words word for word, for rn's developers to read."""
    walk = w.planned(b)
    w.printed(walk.c.bash(b.fed(b.tree("put-up", "lesson"), LESSON)))
    assert not w.orchestrator_ends(b, walk, "up", f"A lesson for rn:\n  {LESSON}").blocked
    assert not walk.c.type("/rn:ty").blocked
    approved = w.printed(walk.c.bash(b.tree("approve")))
    [issue] = b.github_holds()["issues"]
    assert issue["repository"] == "lovaizu/ccpm"
    assert LESSON in issue["body"]
    assert "/issues/1" in json.dumps(approved)


@pytest.mark.supports("S7", "user", "Sign-off")
def test_a_lesson_sent_back_opens_no_issue(b: Bench) -> None:
    """Given: the walkthrough's plan signed off, and a lesson put up for the user's sign-off.
    When: the user types /rn:gm, and the orchestrator runs tree.py send-back.
    Then: the lesson is sent back, and GitHub holds no issue."""
    walk = w.planned(b)
    w.printed(walk.c.bash(b.fed(b.tree("put-up", "lesson"), LESSON)))
    assert not walk.c.type("/rn:gm").blocked
    sent = w.printed(walk.c.bash(b.tree("send-back")))
    assert (sent["kind"], sent["state"], sent["what"]) == ("lesson", "sent back", LESSON)
    assert b.github_holds()["issues"] == []


@pytest.mark.supports("S6", "repository", "Sign-off", "orchestrator")
def test_the_pull_request_is_marked_ready_once_no_deliverable_is_left(b: Bench) -> None:
    """Given: a plan of "Type hints in each file of invoicer" alone, its deliverable signed off.
    When: the orchestrator runs tree.py ready, and ends its turn with Done and the pull request.
    Then: tree.py ready gives the pull request's URL, GitHub holds it ready, the pull request
    handed over waits for the user, and the guard lets the turn end."""
    walk, url = w.handed_over(b)
    pull = b.github_holds()["pulls"][walk.branch()]
    assert pull["draft"] is False and url.endswith(f"/{pull['number']}")
    last = w.sign_offs_in(walk)[-1]
    assert (last["kind"], last["what"], last["state"]) == ("pull request", url, "waiting")


@pytest.mark.supports("S6", "user", "Sign-off")
def test_gm_on_the_pull_request_handed_over_marks_it_a_draft_again(b: Bench) -> None:
    """Given: the pull request of "Type hints in each file of invoicer" handed over, ready.
    When: the user types /rn:gm with what to change, and the orchestrator runs tree.py send-back.
    Then: the pull request handed over is sent back, and GitHub holds it a draft again."""
    walk, _ = w.handed_over(b)
    assert not walk.c.type("/rn:gm the totals need hints on their keyword arguments").blocked
    sent = w.printed(walk.c.bash(b.tree("send-back")))
    assert (sent["kind"], sent["state"]) == ("pull request", "sent back")
    assert b.github_holds()["pulls"][walk.branch()]["draft"] is True


@pytest.mark.supports("S6", "user", "Sign-off", "repository")
def test_ty_on_the_pull_request_leaves_it_ready_and_merges_nothing(b: Bench) -> None:
    """Given: the pull request of "Type hints in each file of invoicer" handed over, ready.
    When: the user types /rn:ty, and the orchestrator runs tree.py approve.
    Then: the pull request handed over is signed off, GitHub holds it ready, and the remote's main
    is as it was."""
    walk, _ = w.handed_over(b)
    main = w.git(b.repo, "ls-remote", "origin", "main").split()[0]
    assert not walk.c.type("/rn:ty").blocked
    signed = w.printed(walk.c.bash(b.tree("approve")))
    assert (signed["kind"], signed["state"]) == ("pull request", "signed off")
    assert b.github_holds()["pulls"][walk.branch()]["draft"] is False
    assert w.git(b.repo, "ls-remote", "origin", "main").split()[0] == main


@pytest.mark.supports("S6", "orchestrator", "Decision", "Deliverable")
def test_a_miss_found_in_the_whole_pull_request_starts_the_rounds_again(b: Bench) -> None:
    """Given: a plan of "Type hints in each file of invoicer" alone, its deliverable signed off and
    done, before the pull request is marked ready.
    When: the orchestrator reads the whole pull request against the goal, finds that render.py's
    hints leave out the currency, and the tree-keeper writes the deliverable open again with the
    decision it changes.
    Then: tree.py write marks the deliverable doing, and the guard gives the generator's start due
    with the new decision in its Cut."""
    walk, _ = w.sign_off_put_up(b, w.hints_plan())
    done = {"name": w.HINTS, "path": w.HINTS_PATH, "kind": "code", "status": "done"}
    w.approved(b, walk, "The user signed it off.", {"nodes": {"deliverables/0": done}, "more": []})
    again = w.deliverable(w.HINTS, w.HINTS_PATH)
    decided = {
        "about": "the currency's type",
        "decided": "a str of three letters",
        "by": "reasoning",
    }
    again["necessary_conditions"][0]["decisions"] = [decided]
    change = {"nodes": {"deliverables/0": again}, "more": []}
    wrote = w.keeper_writes(b, walk, "render.py's hints leave out the currency.", change)
    assert wrote["doing"] == [w.HINTS_PATH]
    cut = w.cut_of(w.due_text(walk.said, "generator"))
    assert decided["decided"] in [d["decision"]["decided"] for d in cut["cut"]["decisions"]]

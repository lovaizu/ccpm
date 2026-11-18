"""The integration cases of S3: a sign-off. Each path of its sequence: the work pushed with its
draft pull request, whose case lies in test_rn_walking_skeleton.py, or what's missing put to the
user where git or gh can't push; the orchestrator's own move past the sign-off, by /rn:ty or /rn:gm,
stopped; the turn that puts the sign-off up, held where its record leaves a step out; the user's
/rn:ty, which approves and starts the work resting on it; and the user's /rn:gm, with words or
alone, which sends it back, alone with the user's comments read from the pull request."""

from __future__ import annotations

import json

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench


@pytest.mark.supports("S3", "repository", "Point")
def test_a_push_without_a_login_of_gh_says_what_is_missing(tmp_path: object) -> None:
    """Given: the walkthrough's goal confirmed and the user's point answered, with gh logged in to
    no account.
    When: the orchestrator runs tree.py push.
    Then: tree.py push gives 1, naming the login of gh as what's missing, and GitHub holds no pull
    request."""
    b = w.bench(str(tmp_path), logged_in=False)
    walk = w.confirmed(b)
    pushed = walk.c.bash(b.tree("push"))
    assert pushed.exit_code == 1 and "gh auth login" in pushed.output
    assert b.github_holds()["pulls"] == {}


@pytest.mark.supports("S3", "repository", "Point")
def test_a_push_without_a_remote_says_what_is_missing(tmp_path: object) -> None:
    """Given: the walkthrough's goal confirmed and the user's point answered, in a repository with
    no remote.
    When: the orchestrator runs tree.py push.
    Then: tree.py push gives 1, naming the remote as what's missing."""
    b = w.bench(str(tmp_path), remote=False)
    walk = w.confirmed(b)
    pushed = walk.c.bash(b.tree("push"))
    assert pushed.exit_code == 1 and "remote" in pushed.output


@pytest.mark.supports("S3", "guard", "Sign-off")
def test_only_the_users_own_ty_decides_a_sign_off(b: Bench) -> None:
    """Given: the walkthrough's plan put up for the user's sign-off.
    When: the orchestrator calls /rn:ty by the Skill tool, and starts a generator.
    Then: each is stopped, and the plan still waits for the user's sign-off."""
    walk = w.plan_put_up(b)
    assert walk.c.skill("rn:ty", "").blocked
    stopped, agent = walk.c.start("rn:generator", "Carry out your steps", "generator")
    assert stopped.blocked and agent is None
    assert [s["state"] for s in w.sign_offs_in(walk)] == ["waiting"]


@pytest.mark.supports("S3", "user", "Sign-off", "Deliverable")
def test_ty_approves_the_plan_and_starts_the_work_resting_on_it(b: Bench) -> None:
    """Given: the walkthrough's plan put up for the user's sign-off.
    When: the user types /rn:ty, the orchestrator runs tree.py approve, and the tree-keeper writes
    the plan signed off.
    Then: tree.py approve gives the plan signed off, both deliverables are doing, and the guard
    gives the generator's start due."""
    walk = w.plan_put_up(b)
    typed = walk.c.type("/rn:ty")
    assert not typed.blocked
    signed = w.printed(walk.c.bash(b.tree("approve")))
    assert (signed["kind"], signed["state"]) == ("plan", "signed off")
    wrote = w.keeper_writes(b, walk, "Signed off.", {"nodes": {}, "more": []}, "/rn:ty")
    assert wrote["doing"] == [w.COMMAND_PATH, w.GUIDE_PATH]
    assert w.due_text(walk.said, "generator")


@pytest.mark.supports("S3", "user", "Sign-off", "Decision")
def test_gm_with_words_sends_the_plan_back_to_the_decision_it_changes(b: Bench) -> None:
    """Given: the walkthrough's plan put up for the user's sign-off.
    When: the user types /rn:gm with what to change, the orchestrator runs tree.py send-back, and
    the tree-keeper writes the decision it changes.
    Then: tree.py send-back gives the plan sent back, and the design tree holds the decision the
    user's words changed, with no deliverable doing."""
    walk = w.plan_put_up(b)
    words = "only the functions that callers import"
    assert not walk.c.type(f"/rn:gm {words}").blocked
    sent = w.printed(walk.c.bash(b.tree("send-back")))
    assert (sent["kind"], sent["state"]) == ("plan", "sent back")
    decided = {"about": w.POINT, "decided": words, "by": "user"}
    path = "deliverables/0/necessary_conditions/0/decisions/0"
    wrote = w.keeper_writes(
        b, walk, "The user changed it.", {"nodes": {path: decided}, "more": []}, words
    )
    assert wrote["doing"] == []
    assert w.tree_in(walk)["deliverables"][0]["necessary_conditions"][0]["decisions"] == [decided]


@pytest.mark.supports("S3", "Comment", "repository", "user")
def test_gm_alone_reads_the_users_comments_since_the_sign_off(b: Bench) -> None:
    """Given: the walkthrough's plan put up, and on its pull request after it the user's comment,
    the user's line comment on invoicer/render.py, and a bot's comment, with the user's comment from
    before the sign-off.
    When: the user types /rn:gm alone, and the orchestrator runs tree.py send-back, then tree.py
    comments.
    Then: tree.py comments gives the user's comment and line comment with their words, the line
    comment with its path and line, and none from before the sign-off was put up or by the bot."""
    walk = w.plan_put_up(b)
    held = b.github_holds()
    pull = held["pulls"][walk.branch()]
    bot = {"login": "github-actions[bot]"}
    pull["comments"] = [
        {"body": "Before the sign-off.", "createdAt": "2000-01-01T00:00:00Z"},
        {"body": "Print the currency each client pays in.", "createdAt": "2999-01-01T00:00:00Z"},
        {"body": "A bot's check.", "createdAt": "2999-01-01T00:01:00Z", "author": bot},
    ]
    pull["review_comments"] = [
        {
            "body": "Round the tax here.",
            "created_at": "2999-01-01T00:02:00Z",
            "path": "invoicer/render.py",
            "line": 12,
        }
    ]
    with open(b.github, "w", encoding="utf-8") as f:
        json.dump(held, f)
    assert not walk.c.type("/rn:gm").blocked
    w.printed(walk.c.bash(b.tree("send-back")))
    comments = w.printed(walk.c.bash(b.tree("comments")))
    assert [(c["body"], c["path"], c["line"]) for c in comments] == [
        ("Print the currency each client pays in.", "", None),
        ("Round the tax here.", "invoicer/render.py", 12),
    ]


@pytest.mark.supports("S3", "Sign-off", "Made", "Deliverable")
def test_a_deliverable_put_up_and_approved_is_marked_done(b: Bench) -> None:
    """Given: the command judged good in its first round, and put up for the user's sign-off with
    the decision its Made names.
    When: the user types /rn:ty, the orchestrator runs tree.py approve, and the tree-keeper writes
    it done.
    Then: the sign-off of the deliverable waits until /rn:ty and is signed off after it, and the
    design tree holds the deliverable done."""
    walk, cut = w.sign_off_put_up(b)
    assert w.sign_offs_in(walk)[-1] == {
        **w.sign_offs_in(walk)[-1],
        "kind": "deliverable",
        "what": cut["deliverable"],
        "state": "waiting",
    }
    done = {"name": w.COMMAND, "path": w.COMMAND_PATH, "kind": "code", "status": "done"}
    w.approved(b, walk, "Signed off.", {"nodes": {"deliverables/0": done}, "more": []})
    assert w.sign_offs_in(walk)[-1]["state"] == "signed off"
    assert w.tree_in(walk)["deliverables"][0] == done


@pytest.mark.supports("S3", "Sign-off", "Round", "Decision")
def test_a_deliverable_sent_back_starts_its_rounds_again(b: Bench) -> None:
    """Given: the command alone, made in a round of content and one of structure, and put up for
    the user's sign-off.
    When: the user types /rn:gm with what to change, the orchestrator runs tree.py send-back, the
    tree-keeper writes the decision it changes, and the orchestrator starts the generator due.
    Then: the sign-off keeps round 2, and the generator's Cut is of round 3, by the code best
    practice, as the rounds of content start again from the design."""
    walk, cut = w.sign_off_put_up(b, w.command_plan())
    assert w.sign_offs_in(walk)[-1]["round"] == 2
    words = "only the functions that callers import"
    assert not walk.c.type(f"/rn:gm {words}").blocked
    w.printed(walk.c.bash(b.tree("send-back")))
    decided = {"about": w.POINT, "decided": words, "by": "user"}
    path = "deliverables/0/necessary_conditions/0/decisions/0"
    w.keeper_writes(b, walk, "The user changed it.", {"nodes": {path: decided}, "more": []}, words)
    _, again = w.generator_started(walk)
    assert again["made"].endswith("/3/made.json")
    assert w.kinds_of(again) == ("code",) and again["made"] != cut["made"]


@pytest.mark.supports("S3", "guard", "Sign-off")
def test_the_orchestrators_own_gm_is_stopped(b: Bench) -> None:
    """Given: the walkthrough's plan put up for the user's sign-off.
    When: the orchestrator calls /rn:gm by the Skill tool.
    Then: it's stopped, and the plan still waits for the user's sign-off."""
    walk = w.plan_put_up(b)
    assert walk.c.skill("rn:gm", "").blocked
    assert [s["state"] for s in w.sign_offs_in(walk)] == ["waiting"]


@pytest.mark.supports("S3", "guard", "record.py", "orchestrator")
def test_a_turn_putting_the_plan_up_with_a_step_of_the_part_left_out_is_held(b: Bench) -> None:
    """Given: the walkthrough's goal confirmed and the user's point answered, the work pushed, and
    the plan put up.
    When: the orchestrator, which recorded each step of up and each of its part but step 6, ends
    its turn with the plan.
    Then: the guard holds the end, and the check its stop names gives step 6 of the orchestrator;
    once it records each step after 5 again and ends again, the guard lets the turn end."""
    walk = w.confirmed(b)
    w.printed(walk.c.bash(b.tree("push")))
    w.printed(walk.c.bash(b.tree("put-up", "plan")))
    record = walk.run["record"]
    up = [str(n) for n in w.steps_of(b.rn, "skills/up/SKILL.md")]
    part = [str(n) for n in w.steps_of(b.rn, "domain/orchestrator.md")]
    w.records(b, walk.c, record, [("up", up), ("orchestrator", [n for n in part if n != "6"])])
    held = walk.c.stop(w.PLAN_SHOWN)
    assert held.blocked
    checked = walk.c.bash(b.record("check", "orchestrator", ""))
    assert checked.exit_code == 1 and "orchestrator step 7 is recorded before step 6" in (
        checked.output
    )
    w.records(b, walk.c, record, [("orchestrator", part[:1]), ("orchestrator", part)])
    assert not walk.c.stop(w.PLAN_SHOWN).blocked

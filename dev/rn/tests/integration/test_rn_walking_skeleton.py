"""The integration cases of rn's walking skeleton: the thinnest run of the README's walkthrough
through every part. The user's /rn:up with a request starts a run with the tree-keeper's start
first, the goal and the plan reach the design tree through the tree-keeper, the generator starts
with its Cut of the first deliverable doing, one evaluator starts for each group of necessary
conditions, and the sign-off pushes the work with a draft pull request of its own."""

from __future__ import annotations

import json
import os
import re

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench

pytestmark = pytest.mark.xfail(
    strict=True,
    reason="Lane at rn-rebuild's HEAD tells no start due as the orchestrator enters the run's"
    " worktree, lets no second start of a role beside the first, and takes no result of a role"
    " resumed",
)


@pytest.mark.supports("S1", "orchestrator", "adapters", "guard", "tree.py")
def test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first(b: Bench) -> None:
    """Given: invoicer with rn installed, and no run of rn.
    When: the user types /rn:up with the walkthrough's request, and the orchestrator runs tree.py
    start and enters the worktree it gives.
    Then: the guard lets /rn:up through with the tree-keeper's start due and why its text can't be
    given yet; tree.py start gives rn's worktree of the run, its folder, and the orchestrator's
    record; and once entered, the guard gives the tree-keeper's start with its Cut: its record in
    the run's records/, the run's design tree, and the design tree best practice."""
    c, asked = w.asked(b)
    assert "rn:tree-keeper" in asked.said
    run, entered = w.run_made(b, c)
    name = os.path.basename(run["worktree"])
    assert re.fullmatch(r"rn-\d{8}-[a-z0-9-]+", name)
    assert os.path.dirname(run["worktree"]) == os.path.join(b.repo, ".claude", "worktrees")
    assert run["folder"] == f".rn/{name[len('rn-') :]}"
    assert run["record"].startswith(f"{run['folder']}/records/")
    cut = w.cut_of(w.due_text(entered.said, "tree-keeper"))
    assert set(cut) == {"record", "tree", "best_practice"}
    assert cut["record"].startswith(f"{run['folder']}/records/")
    assert cut["tree"] == f"{run['folder']}/design-tree.json"
    assert cut["best_practice"].rstrip("/").endswith("best-practices/design-tree")


@pytest.mark.supports("S1", "tree-keeper", "Design tree", "Decision", "Deliverable")
def test_the_goal_and_the_plan_reach_the_design_tree_through_the_tree_keeper(b: Bench) -> None:
    """Given: the walkthrough's run started, and its tree-keeper started with its Cut.
    When: the orchestrator resumes the tree-keeper with the goal drafted and the plan of two
    deliverables, and the tree-keeper writes them by tree.py write.
    Then: tree.py write gives what changed and each node touched, the goal and both deliverables
    among them, and no deliverable doing, as the plan isn't signed off; the run's design tree holds
    them; and the work's branch holds the design tree as written."""
    c, _ = w.asked(b)
    run, entered = w.run_made(b, c)
    walk = w.keeper_started(b, c, run, entered.said)
    wrote = w.keeper_writes(b, walk, "The goal drafted, and the plan.", w.walkthrough_plan())
    assert set(wrote) == {"changed", "touched", "doing"}
    assert "goal" in wrote["changed"] and "deliverables/1" in wrote["changed"]
    assert wrote["doing"] == []
    tree = w.tree_in(walk)
    assert tree["goal"] == {"decided": w.GOAL, "by": "reasoning"}
    assert [d["name"] for d in tree["deliverables"]] == [w.HINTS, w.TYPED]
    held = w.git(run["worktree"], "show", f"HEAD:{run['folder']}/design-tree.json")
    assert json.loads(held) == tree


@pytest.mark.supports("S1", "generator", "Cut", "Deliverable", "Best practice", "adapters")
def test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing(b: Bench) -> None:
    """Given: the walkthrough's plan signed off, both deliverables doing.
    When: the orchestrator starts the generator with the text that the guard gives due.
    Then: its Cut names its record, "Type hints in each file of invoicer" at invoicer, its kind,
    the code and refactor-code best practices, where it writes its Made, and the part of the design
    tree it makes it from: the goal, its name, its inputs, the user's decision on which files, and
    no More kept."""
    walk = w.planned(b)
    _, cut = w.generator_started(walk)
    assert set(cut) == {"record", "deliverable", "kind", "best_practice", "refactor", "made", "cut"}
    assert cut["deliverable"] == w.HINTS_PATH and cut["kind"] == "code"
    assert cut["best_practice"].rstrip("/").endswith("best-practices/code")
    assert cut["refactor"].rstrip("/").endswith("best-practices/refactor-code")
    assert cut["record"].startswith(f"{walk.run['folder']}/records/")
    assert cut["made"].startswith(f"{walk.run['folder']}/rounds/")
    part = cut["cut"]
    assert (part["goal"], part["name"], part["inputs"], part["more"]) == (w.GOAL, w.HINTS, [], [])
    [decision] = part["decisions"]
    assert decision["condition"] == "N1"
    assert decision["decision"]["path"] == "deliverables/0/necessary_conditions/0/decisions/0"
    assert decision["decision"]["point"] == w.POINT
    assert decision["decision"]["decided"] == w.EACH_FILE


@pytest.mark.supports("S1", "evaluator", "Necessary condition", "Best practice", "Answers")
def test_one_evaluator_starts_for_each_group_of_necessary_conditions(b: Bench) -> None:
    """Given: the generator of "Type hints in each file of invoicer" ended done.
    When: the orchestrator starts each evaluator that the guard gives due.
    Then: one evaluator starts for each group of necessary conditions of the code best practice
    and of the refactor-code one, each Cut naming its best practice, the IDs of its group, and
    where it writes its Answers in the round."""
    walk, cut, cuts = w.first_round(b)
    groups = {(kind, tuple(group)) for kind in w.kinds_of(cut) for group in w.groups_of(b.rn, kind)}
    given = {
        (os.path.basename(c["best_practice"].rstrip("/")), tuple(c["conditions"])) for c in cuts
    }
    assert given == groups and len(cuts) == len(groups)
    assert all(c["answers"].startswith(f"{walk.run['folder']}/rounds/") for c in cuts)
    assert len({c["answers"] for c in cuts}) == len(cuts)


@pytest.mark.supports("S3", "repository", "Sign-off", "tree.py")
def test_a_sign_off_pushes_the_work_and_keeps_a_draft_pull_request(b: Bench) -> None:
    """Given: the walkthrough's goal confirmed and the user's point answered.
    When: the orchestrator runs tree.py push, then tree.py put-up plan, and ends its turn with the
    plan as the README shows it.
    Then: the remote holds the work's branch at the worktree's last commit, GitHub holds a draft
    pull request of the branch, whose URL tree.py push gives, the plan waits for the user's
    sign-off, and the guard lets the turn end."""
    walk = w.confirmed(b)
    url = w.printed(walk.c.bash(b.tree("push")))
    waiting = w.printed(walk.c.bash(b.tree("put-up", "plan")))
    assert not w.orchestrator_ends(b, walk, "up", w.PLAN_SHOWN).blocked
    branch = walk.branch()
    head = w.git(walk.run["worktree"], "rev-parse", "HEAD").strip()
    assert w.git(b.repo, "ls-remote", "origin", branch).split()[0] == head
    pull = b.github_holds()["pulls"][branch]
    assert pull["draft"] is True and url.endswith(f"/{pull['number']}")
    assert waiting["kind"] == "plan" and waiting["state"] == "waiting"
    assert [s["state"] for s in w.sign_offs_in(walk)] == ["waiting"]

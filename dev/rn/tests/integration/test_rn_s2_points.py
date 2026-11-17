"""The integration cases of S2: a point settled. Each path of its sequence: the user's point
written open, so that the deliverable resting on it waits, then answered; a point that the purpose
or a best practice settles, written with no question and committed with its ground as the
message; and a change that the orchestrator sends back to the tree-keeper, written again."""

from __future__ import annotations

import os

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench

GUIDE_POINT = "deliverables/1/necessary_conditions/0/decisions/0"
SPREADSHEET = "the spreadsheet the readers save their lines from"
# The decision on the guide's point, and the ground on which the goal settles it.
ANY_SPREADSHEET = "any spreadsheet that saves CSV"
GOAL_SETTLES = (
    "The goal names a spreadsheet, not a program, so the guide shows saving CSV from any."
)


def signed_with_a_point_open(b: Bench) -> w.Walk:
    """The walkthrough's plan signed off with a point open under the guide, so that only the
    command is doing."""
    walk = w.confirmed(b)
    point = {"nodes": {GUIDE_POINT: {"about": SPREADSHEET, "decided": None}}, "more": []}
    w.keeper_writes(b, walk, "A point that's the user's.", point)
    w.printed(walk.c.bash(b.tree("push")))
    w.printed(walk.c.bash(b.tree("put-up", "plan")))
    assert not w.orchestrator_ends(b, walk, "up", w.PLAN_SHOWN).blocked
    wrote = w.approved(b, walk, "The user signed off the plan.")
    assert wrote["doing"] == [w.COMMAND_PATH]
    return walk


@pytest.mark.supports("S2", "Point", "Decision", "Deliverable")
def test_a_users_point_written_open_keeps_its_deliverable_waiting(b: Bench) -> None:
    """Given: the walkthrough's plan, with a point of the user's open under the guide.
    When: the user signs off the plan, and the tree-keeper writes it.
    Then: tree.py write marks only the command doing, and the design tree holds the point open."""
    walk = signed_with_a_point_open(b)
    guide = w.tree_in(walk)["deliverables"][1]
    assert guide["status"] == "open"
    assert guide["necessary_conditions"][0]["decisions"] == [
        {"about": SPREADSHEET, "decided": None}
    ]


@pytest.mark.supports("S2", "user", "tree-keeper", "Decision")
def test_a_users_point_answered_marks_its_deliverable_doing(b: Bench) -> None:
    """Given: the walkthrough's plan signed off, with the user's point open under the guide.
    When: the orchestrator ends its turn with the point, the user answers, and the tree-keeper
    writes the decision by the user.
    Then: the guard lets the turn end, as it puts no work up, and tree.py write marks the guide
    doing."""
    walk = signed_with_a_point_open(b)
    asked = "A question that's yours:\n  Which spreadsheet do the readers save their lines from?"
    assert not walk.c.stop(asked).blocked
    assert not walk.c.type("LibreOffice Calc").blocked
    decided = {"about": SPREADSHEET, "decided": "LibreOffice Calc", "by": "user"}
    change = {"nodes": {GUIDE_POINT: decided}, "more": []}
    wrote = w.keeper_writes(b, walk, "The user's answer.", change, "LibreOffice Calc")
    assert wrote["doing"] == [w.GUIDE_PATH]


@pytest.mark.supports("S2", "orchestrator", "Decision")
def test_a_point_the_purpose_settles_marks_its_deliverable_doing_with_no_question(
    b: Bench,
) -> None:
    """Given: the walkthrough's plan signed off, with a point open under the guide.
    When: the orchestrator settles it by reasoning and the tree-keeper writes it, with no turn put
    to the user between.
    Then: tree.py write marks the guide doing, and the design tree holds the decision by
    reasoning."""
    walk = signed_with_a_point_open(b)
    decided = {"about": SPREADSHEET, "decided": ANY_SPREADSHEET, "by": "reasoning"}
    change = {"nodes": {GUIDE_POINT: decided}, "more": []}
    wrote = w.keeper_writes(b, walk, GOAL_SETTLES, change)
    assert wrote["doing"] == [w.GUIDE_PATH]
    held = w.tree_in(walk)["deliverables"][1]["necessary_conditions"][0]["decisions"]
    assert held == [decided]


@pytest.mark.supports("S2", "tree-keeper", "tree.py", "Decision", "repository")
def test_a_settled_decisions_ground_is_the_message_of_its_commit(b: Bench) -> None:
    """Given: the walkthrough's plan signed off, with a point open under the guide.
    When: the orchestrator settles it by reasoning, and resumes the tree-keeper with the decision
    and its ground, which it writes by tree.py write with that ground.
    Then: the commit that last changed the run's design tree has the ground word for word as its
    message, and the design tree holds the decision with no ground in it."""
    walk = signed_with_a_point_open(b)
    ground = f"{GOAL_SETTLES}\nThe readers keep their lines in more than one program."
    decided = {"about": SPREADSHEET, "decided": ANY_SPREADSHEET, "by": "reasoning"}
    w.keeper_writes(b, walk, ground, {"nodes": {GUIDE_POINT: decided}, "more": []})
    tree = os.path.join(walk.run["folder"], "design-tree.json")
    message = w.git(walk.run["worktree"], "log", "-1", "--format=%B", "--", tree)
    assert message.strip() == ground
    assert (
        "ground"
        not in w.tree_in(walk)["deliverables"][1]["necessary_conditions"][0]["decisions"][0]
    )


@pytest.mark.supports("S2", "tree-keeper", "Design tree")
def test_a_change_sent_back_to_the_tree_keeper_is_written_again(b: Bench) -> None:
    """Given: the walkthrough's goal and plan written, and the tree-keeper's write of a decision
    under the wrong deliverable.
    When: the orchestrator finds it falls short and resumes the tree-keeper with the ground and the
    change mended, which it writes.
    Then: tree.py write gives the nodes changed, and the design tree holds the decision only where
    the mended change puts it."""
    walk = w.opened(b)
    decided = {"about": w.POINT, "decided": w.WITH_EACH, "by": "user"}
    wrong = "deliverables/1/necessary_conditions/0/decisions/0"
    right = "deliverables/0/necessary_conditions/0/decisions/0"
    w.keeper_writes(b, walk, "The user's answer.", {"nodes": {wrong: decided}, "more": []})
    mended = {"nodes": {wrong: None, right: decided}, "more": []}
    wrote = w.keeper_writes(b, walk, "It lies under the first deliverable.", mended)
    assert wrong in wrote["changed"] and right in wrote["changed"]
    tree = w.tree_in(walk)
    assert tree["deliverables"][0]["necessary_conditions"][0]["decisions"] == [decided]
    assert tree["deliverables"][1]["necessary_conditions"][0]["decisions"] == []


@pytest.mark.supports("S2", "tree.py", "Design tree")
def test_a_change_gives_each_node_it_touches_with_the_path_up(b: Bench) -> None:
    """Given: the walkthrough's goal and plan written.
    When: the tree-keeper writes the user's decision under N1 of the command.
    Then: tree.py write gives the decision as changed, and among the nodes touched the path up:
    its necessary condition and its deliverable."""
    walk = w.opened(b)
    path = "deliverables/0/necessary_conditions/0/decisions/0"
    decided = {"about": w.POINT, "decided": w.WITH_EACH, "by": "user"}
    wrote = w.keeper_writes(b, walk, "The user's answer.", {"nodes": {path: decided}, "more": []})
    assert wrote["changed"] == [path]
    assert {"deliverables/0/necessary_conditions/0", "deliverables/0"} <= set(wrote["touched"])

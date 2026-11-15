"""The integration cases of S2: a point settled. Each path of its sequence: the user's point
written open, so that the deliverable resting on it waits, then answered; a point that the purpose
or a best practice settles, written with no question and committed with its ground as the
message; and a change that the orchestrator sends back
to the tree-keeper, written again."""

from __future__ import annotations

import os

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.rn.tests.rn_walkthrough import Bench

pytestmark = pytest.mark.xfail(
    strict=True, reason="rn's parts have empty bodies, and Lane hasn't laid rn's guard"
)

MARKER = "deliverables/1/necessary_conditions/0/decisions/0"
WHERE = "where the marker lies"


def signed_with_a_point_open(b: Bench) -> w.Walk:
    """The walkthrough's plan signed off with a point open under "invoicer marked as typed", so
    that only "Type hints in each file of invoicer" is doing."""
    walk = w.confirmed(b)
    point = {"nodes": {MARKER: {"about": WHERE, "decided": None}}, "more": []}
    w.keeper_writes(b, walk, "A point that's the user's.", point)
    w.printed(walk.c.bash(b.tree("push")))
    w.printed(walk.c.bash(b.tree("put-up", "plan")))
    assert not w.orchestrator_ends(b, walk, "up", w.PLAN_SHOWN).blocked
    wrote = w.approved(b, walk, "The user signed off the plan.")
    assert wrote["doing"] == [w.HINTS_PATH]
    return walk


@pytest.mark.supports("S2", "Point", "Decision", "Deliverable")
def test_a_users_point_written_open_keeps_its_deliverable_waiting(b: Bench) -> None:
    """Given: the walkthrough's plan, with a point of the user's open under "invoicer marked as
    typed".
    When: the user signs off the plan, and the tree-keeper writes it.
    Then: tree.py write marks only "Type hints in each file of invoicer" doing, and the design tree
    holds the point open."""
    walk = signed_with_a_point_open(b)
    typed = w.tree_in(walk)["deliverables"][1]
    assert typed["status"] == "open"
    assert typed["necessary_conditions"][0]["decisions"] == [{"about": WHERE, "decided": None}]


@pytest.mark.supports("S2", "user", "tree-keeper", "Decision")
def test_a_users_point_answered_marks_its_deliverable_doing(b: Bench) -> None:
    """Given: the walkthrough's plan signed off, with the user's point open under "invoicer marked
    as typed".
    When: the orchestrator ends its turn with the point, the user answers, and the tree-keeper
    writes the decision by the user.
    Then: the guard lets the turn end, as it puts no work up, and tree.py write marks "invoicer
    marked as typed" doing."""
    walk = signed_with_a_point_open(b)
    assert not walk.c.stop(f"A question that's yours:\n  {WHERE}?").blocked
    assert not walk.c.type("in the package's folder").blocked
    decided = {"about": WHERE, "decided": "in the package's folder", "by": "user"}
    change = {"nodes": {MARKER: decided}, "more": []}
    wrote = w.keeper_writes(b, walk, "The user's answer.", change, "in the package's folder")
    assert wrote["doing"] == [w.TYPED_PATH]


@pytest.mark.supports("S2", "orchestrator", "Decision")
def test_a_point_the_purpose_settles_marks_its_deliverable_doing_with_no_question(
    b: Bench,
) -> None:
    """Given: the walkthrough's plan signed off, with a point open under "invoicer marked as typed".
    When: the orchestrator settles it by reasoning and the tree-keeper writes it, with no turn put
    to the user between.
    Then: tree.py write marks "invoicer marked as typed" doing, and the design tree holds the
    decision by reasoning."""
    walk = signed_with_a_point_open(b)
    decided = {"about": WHERE, "decided": "in the package's folder", "by": "reasoning"}
    wrote = w.keeper_writes(
        b, walk, "PEP 561 settles it.", {"nodes": {MARKER: decided}, "more": []}
    )
    assert wrote["doing"] == [w.TYPED_PATH]
    held = w.tree_in(walk)["deliverables"][1]["necessary_conditions"][0]["decisions"]
    assert held == [decided]


@pytest.mark.supports("S2", "tree-keeper", "tree.py", "Decision", "repository")
def test_a_settled_decisions_ground_is_the_message_of_its_commit(b: Bench) -> None:
    """Given: the walkthrough's plan signed off, with a point open under "invoicer marked as typed".
    When: the orchestrator settles it by reasoning, and resumes the tree-keeper with the decision
    and its ground, which it writes by tree.py write with that ground.
    Then: the commit that last changed the run's design tree has the ground word for word as its
    message, and the design tree holds the decision with no ground in it."""
    walk = signed_with_a_point_open(b)
    ground = "PEP 561 settles it: a type checker reads py.typed only in the package's folder."
    decided = {"about": WHERE, "decided": "in the package's folder", "by": "reasoning"}
    w.keeper_writes(b, walk, ground, {"nodes": {MARKER: decided}, "more": []})
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
    decided = {"about": w.POINT, "decided": w.EACH_FILE, "by": "user"}
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
    When: the tree-keeper writes the user's decision under N1 of "Type hints in each file of
    invoicer".
    Then: tree.py write gives the decision as changed, and among the nodes touched the path up:
    its necessary condition and its deliverable."""
    walk = w.opened(b)
    path = "deliverables/0/necessary_conditions/0/decisions/0"
    decided = {"about": w.POINT, "decided": w.EACH_FILE, "by": "user"}
    wrote = w.keeper_writes(b, walk, "The user's answer.", {"nodes": {path: decided}, "more": []})
    assert wrote["changed"] == [path]
    assert {"deliverables/0/necessary_conditions/0", "deliverables/0"} <= set(wrote["touched"])

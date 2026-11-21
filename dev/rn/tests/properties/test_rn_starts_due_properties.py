"""The property-based test of rn's order as Lane asks it, as rn's Test strategy names it: work that
rests on a plan starts once the user signs it off (P1.3), so while the plan is open no role is due,
whatever the design tree the orchestrator wrote holds: any deliverables, open, being made, or
done, any conditions good, and any work. A start before the sign-off makes what the user never
agreed to, and the user waits on its remaking."""

from __future__ import annotations

import os
import tempfile
from typing import Any

import pytest
import rn_files
from hypothesis import given
from hypothesis import strategies as st
from rn_adapters import adapter
from rn_runs import branch_run

NAME = "20261120-invoices"
PATHS = ("invoicer/__main__.py", "docs/guide.md", "CHANGELOG.md")


ADAPTER = adapter("starts_due")


@st.composite
def open_plans(draw: Any) -> dict[str, Any]:
    """A design tree whose plan is open, with any of its conditions good, and any deliverables
    resting on none or on another, each in any state, any of them in the work."""
    plan = rn_files.plan(NAME, good=draw(st.booleans()))
    paths = draw(st.lists(st.sampled_from(PATHS), min_size=1, unique=True))
    nodes = []
    for n, path in enumerate(paths):
        node = rn_files.open_node("A deliverable", path, "light", paths[:n][:1])
        node["status"] = draw(st.sampled_from(["open", "doing"]))
        for each in node["necessary_conditions"]:
            each["good"] = draw(st.booleans())
        nodes.append(
            node if draw(st.integers(0, 3)) else rn_files.done_node("A deliverable", path, "light")
        )
    work = [rn_files.work("make", p) for p in paths if draw(st.booleans())]
    return rn_files.tree([plan, *nodes], work)


MOVES = st.lists(
    st.sampled_from(
        [
            {"kind": "command", "command": "rn:on"},
            {"kind": "command", "command": "rn:up"},
            {"kind": "command", "command": "rn:ty"},
            {"kind": "command", "command": "rn:gm"},
        ]
    ),
    min_size=1,
    max_size=4,
)


@pytest.mark.supports("test_no_generator_starts_before_the_plan_is_signed_off")
@given(open_plans(), MOVES)
def test_no_role_is_due_while_the_plan_is_open(tree: dict[str, Any], moves: list[dict[str, Any]]):
    """Given any design tree whose plan is open, and any commands of the user but a pause
    When the starts due are found
    Then none is due
    (Invariant, resting on P1.3.)"""
    with tempfile.TemporaryDirectory() as folder:
        cwd = rn_files.repository(os.path.join(folder, "repo"), {"README.md": "invoicer\n"})
        branch_run(cwd, NAME, tree)
        out = ADAPTER.due({"run": {"skill": "rn:up", "words": "", "moves": moves}}, cwd)
    assert out == {"starts": []}

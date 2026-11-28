"""The unit cases of steering/due.py, what waits now in the work: the orchestrator's weighing where
the tree holds no target; the first task, with the role it takes next; a target deep in the tree;
and, once no task is left, the hand-over, the user's try, the inspection, and the work's end."""

from __future__ import annotations

import pytest
import rn_files
from steering.due import due


def test_a_weighing_is_due_where_the_tree_holds_no_target() -> None:
    """Given a steering whose tree has no target, with its tasks.
    When what's due is asked.
    Then the orchestrator's weighing is due."""
    assert due(rn_files.steering(target=False)) == ["weigh"]


def test_the_first_task_is_due_to_make() -> None:
    """Given a steering with the command's task and the guide's.
    When what's due is asked.
    Then the command is due to make, with its kind and its generator, as it starts with a Round of
    content."""
    assert due(rn_files.steering()) == [f"make\t{rn_files.COMMAND}\tcode\tgenerator"]


def test_a_task_on_its_way_is_due_to_its_next_role() -> None:
    """Given a steering whose command waits on the orchestrator's weighing.
    When what's due is asked.
    Then the command is due to its weighing."""
    held = rn_files.steering()
    held["tasks"][0]["next"] = "weigh"
    assert due(held) == [f"make\t{rn_files.COMMAND}\tcode\tweigh"]


def test_a_target_deep_in_the_tree_is_found() -> None:
    """Given a steering whose target lies under a smaller opportunity, and no task left.
    When what's due is asked.
    Then the target's hand-over is due."""
    held = rn_files.steering(paths=())
    picked = held["ost"]["opportunities"].pop(0)
    held["ost"]["opportunities"][0]["children"] = [picked]
    assert due(held) == [f"hand-over\t{rn_files.SOLUTION}"]


@pytest.mark.parametrize(
    ("stage", "line"),
    [
        (None, f"hand-over\t{rn_files.SOLUTION}"),
        ("trying", f"trying\t{rn_files.SOLUTION}"),
        ("enough", "inspect"),
        ("inspected", "ended"),
    ],
    ids=["hand-over", "trying", "inspect", "ended"],
)
def test_once_no_task_is_left_the_stage_says_whats_due(stage: str | None, line: str) -> None:
    """Given a steering with no task left, at a stage or before any.
    When what's due is asked.
    Then the hand-over, the user's try, the inspection, or the work's end is due."""
    assert due(rn_files.steering(paths=(), stage=stage)) == [line]

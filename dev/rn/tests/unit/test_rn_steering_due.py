"""The unit cases of steering/due.py, what waits now in a run: open questions, which hold up the
rest; the pruner's weighing where no need is picked or no step is set; the next deliverable to
make; the hand-over; the user's try; a later step once the first is done; and the final check."""

from __future__ import annotations

import rn_files
from steering.due import due

BOTH = (rn_files.COMMAND, rn_files.GUIDE)


def test_open_questions_hold_up_the_rest() -> None:
    """Given a steering with two open questions and an open step.
    When what's due is asked.
    Then each question is due, and nothing else."""
    held = rn_files.steering(questions=["Which need first?", "Which printer?"])
    assert due(held) == ["question\tWhich need first?", "question\tWhich printer?"]


def test_the_pruner_is_due_where_no_need_is_picked_or_no_step_is_set() -> None:
    """Given a steering with no target, and one with a target and no step.
    When what's due is asked of each.
    Then the pruner's weighing is due."""
    assert (due(rn_files.steering(target=None)), due(rn_files.steering([]))) == (
        ["weigh"],
        ["weigh"],
    )


def test_the_first_deliverable_not_done_is_due_to_make() -> None:
    """Given a steering whose step has its command done and its guide open.
    When what's due is asked.
    Then the guide is due to make, with its step's number and its kind."""
    held = rn_files.steering([rn_files.step(done=(rn_files.COMMAND,))])
    assert due(held) == [f"make\t1\t{rn_files.GUIDE}\treadme"]


def test_a_step_made_whole_is_due_to_hand_over() -> None:
    """Given a steering whose open step has each deliverable done.
    When what's due is asked.
    Then its hand-over to the user is due."""
    assert due(rn_files.steering([rn_files.step(done=BOTH)])) == [
        f"hand-over\t1\t{rn_files.SETTLES}"
    ]


def test_a_step_trying_waits_on_the_user() -> None:
    """Given a steering whose step is trying.
    When what's due is asked.
    Then the user's try is due."""
    assert due(rn_files.steering([rn_files.step("trying", done=BOTH)])) == [
        f"trying\t1\t{rn_files.SETTLES}"
    ]


def test_the_way_goes_on_to_the_next_step_once_one_is_done() -> None:
    """Given a steering whose first step is done and second open.
    When what's due is asked.
    Then the second step's first deliverable is due to make."""
    held = rn_files.steering([rn_files.step("done", done=BOTH), rn_files.step()])
    assert due(held) == [f"make\t2\t{rn_files.COMMAND}\tcode"]


def test_the_final_check_is_due_once_each_step_is_done() -> None:
    """Given a steering whose one step is done.
    When what's due is asked.
    Then the final check is due."""
    assert due(rn_files.steering([rn_files.step("done", done=BOTH)])) == ["final-check"]

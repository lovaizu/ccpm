"""The unit cases of runner/handoff.py, the form in which a stacked queue reaches its runner:
`encode` and `decode`, of the walkthrough's queue, of one with no start and no task, of tasks with
and without a session, of paths with spaces and letters beyond ASCII, and each refusal of
`decode`: no text, text that isn't JSON, JSON of another form, and the text cut short."""

from __future__ import annotations

import json

import pytest
from runner.handoff import Carried, Handoff, decode, encode
from stacker.queue_file import Task

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

PAYMENTS = Task(
    "review-payments", "/home/dev/overnight/review-payments.md", "/home/dev/work/shop", False
)
FIX = Task(
    "fix-flaky-checkout",
    "/home/dev/overnight/fix-flaky-checkout.md",
    "/home/dev/work/shop-fix-flaky-checkout",
    True,
)


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_the_walkthroughs_handoff_reads_back_whole():
    """Given what the stacker hands the walkthrough's runner: the queue file, 23:00, and two tasks
    anew
    When it is encoded and decoded
    Then it is the same handoff"""
    given = Handoff(
        "/home/dev/overnight/tonight.json", "23:00", (Carried(PAYMENTS, None), Carried(FIX, None))
    )

    assert decode(encode(given)) == given


@pytest.mark.supports("test_a_queue_stacked_again_after_a_stop_starts_its_tasks_at_once")
def test_a_handoff_of_tasks_in_their_sessions_reads_back_whole():
    """Given a handoff with no start of the review in its session and the fix anew
    When it is encoded and decoded
    Then it is the same handoff, the review's session kept"""
    given = Handoff(
        "/home/dev/overnight/tonight.json",
        None,
        (Carried(PAYMENTS, "1b4e28ba"), Carried(FIX, None)),
    )

    assert decode(encode(given)) == given


@pytest.mark.supports("test_a_queue_stacked_again_after_a_stop_starts_its_tasks_at_once")
def test_a_handoff_of_no_task_reads_back_whole():
    """Given a handoff of no task
    When it is encoded and decoded
    Then it is the same handoff"""
    given = Handoff("/home/dev/overnight/tonight.json", "23:00", ())

    assert decode(encode(given)) == given


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_paths_with_spaces_and_letters_beyond_ascii_read_back_whole():
    """Given a handoff whose queue file and task's folder and prompt hold spaces and letters
    beyond ASCII
    When it is encoded and decoded
    Then it is the same handoff"""
    task = Task("revue", '/home/dév/mes tâches/revue "1".md', "/home/dév/travail\tici", True)
    given = Handoff("/home/dév/mes tâches/ce soir.json", "07:05", (Carried(task, "s"),))

    assert decode(encode(given)) == given


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
@pytest.mark.parametrize(
    "text",
    ["", "not json", json.dumps({"queue": "/q.json"}), json.dumps([1, 2])],
    ids=["none", "not JSON", "another form", "a list"],
)
def test_text_not_of_a_handoff_is_refused(text: str):
    """Given no text, text that isn't JSON, or JSON of another form
    When it is decoded
    Then it refuses with ValueError"""
    with pytest.raises(ValueError):
        decode(text)


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_a_handoff_cut_short_is_refused():
    """Given the text of the walkthrough's handoff, cut short by its last five characters
    When it is decoded
    Then it refuses with ValueError"""
    text = encode(Handoff("/home/dev/overnight/tonight.json", "23:00", (Carried(PAYMENTS, None),)))

    with pytest.raises(ValueError):
        decode(text[:-5])

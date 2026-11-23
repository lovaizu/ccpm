"""The unit cases of runner/task.py, what each end of a task's session leads to: `carry`, of a task
anew and of one in its session, that finishes, that the limit stops once, six times, and seven, at
the session limit and at the weekly one, that fails, whose session can't start, whose reply can't be
written, and that the queue no longer keeps, each marked in the record from running to its end."""

from __future__ import annotations

import os
from datetime import timedelta
from typing import Any

import claude_double
import pytest
from claude_double import failed, finished, limited
from overnight_bench import (
    AFTER_THE_LIMIT,
    BEFORE_THE_LIMIT,
    PAYMENTS_ENDED,
    PAYMENTS_PROMPT,
    RESET,
    STOPPED,
    WENT_ON,
    Bench,
    at,
    moment,
    one_review,
    payments_reply,
)
from record import store
from runner.handoff import Carried
from runner.task import carry
from session import claude
from stacker import queue_file

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


@pytest.fixture
def b(b: Bench) -> Bench:
    """The bench, with the queue file of the review of the payments alone in the walkthrough's
    place."""
    one_review(b)
    return b


def stacked(b: Bench, session: str | None = None) -> Carried:
    """The review, stacked alone, carried in the session, or anew."""
    queue = queue_file.read(b.queue_file)
    store.stack(queue)
    return Carried(queue.tasks[0], session)


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_a_task_that_finishes_is_marked_running_then_finished_with_its_reply(b: Bench):
    """Given the review, stacked, whose session finishes at 02:16
    When it is carried
    Then it stands running while its session runs, and then finished at 02:16 in its session with no
    stops, and its reply file holds the reply"""
    b.script(PAYMENTS_PROMPT, finished(AFTER_THE_LIMIT, PAYMENTS_ENDED))
    seen: list[str] = []
    b.before_claude.append(lambda: seen.append(b.run_of("review-payments")["state"]))

    carry(b.queue_file, stacked(b))

    run = b.run_of("review-payments")
    assert seen == ["running"]
    assert {k: v for k, v in run.items() if k != "ended"} == {
        "state": "finished",
        "session": b.asked()[0].session,
        "stops": 0,
        "waits": [],
    }
    assert moment(run["ended"]) == PAYMENTS_ENDED
    assert b.reply("review-payments").rstrip("\n") == AFTER_THE_LIMIT


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset",
    "test_a_task_waiting_for_the_limit_stands_waiting_until_it_goes_on",
)
def test_a_task_the_limit_stops_once_waits_and_goes_on_in_its_session(b: Bench):
    """Given the review, stacked, which the limit stops at 00:41 until 01:40, and which then
    finishes at 02:16
    When it is carried
    Then it waits until 01:42, goes on by `--resume` in its session, and is finished with one stop
    and its wait from 00:41 to 01:42, its reply the README's"""
    b.script(
        PAYMENTS_PROMPT,
        limited(BEFORE_THE_LIMIT, STOPPED, RESET),
        finished(AFTER_THE_LIMIT, PAYMENTS_ENDED),
    )

    carry(b.queue_file, stacked(b))

    first, second = b.asked()
    assert b.clock.waits == [WENT_ON]
    assert second.arguments[second.arguments.index("--resume") + 1] == first.session
    run = b.run_of("review-payments")
    assert (run["state"], run["session"], run["stops"]) == ("finished", first.session, 1)
    assert [(moment(w["stopped"]), moment(w["went_on"])) for w in run["waits"]] == [
        (STOPPED, WENT_ON)
    ]
    assert b.reply("review-payments").rstrip("\n") == payments_reply()


@pytest.mark.supports(
    "test_the_seventh_stop_at_the_limit_gives_the_task_up_with_why_and_its_session"
)
@pytest.mark.parametrize(("stops", "state"), [(6, "finished"), (7, "given up")])
def test_a_task_goes_on_after_its_sixth_stop_and_is_given_up_at_its_seventh(
    b: Bench, stops: int, state: str
):
    """Given the review, stacked, which the limit stops six or seven times, each for an hour, and
    which would then finish
    When it is carried
    Then after six stops it is finished, with six stops; at the seventh it is given up with why and
    its session, with seven stops, run no more"""
    moments = [at(23, 0) + timedelta(hours=2 * n) for n in range(stops)]
    b.script(
        PAYMENTS_PROMPT,
        *[limited(f"part {n}", each, each + timedelta(hours=1)) for n, each in enumerate(moments)],
        finished("the rest", moments[-1] + timedelta(hours=1, minutes=30)),
    )

    carry(b.queue_file, stacked(b))

    run = b.run_of("review-payments")
    assert (run["state"], run["stops"], run["session"]) == (state, stops, b.asked()[0].session)
    assert len(b.asked()) == 7
    assert (state == "given up") == bool(run.get("why"))


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset"
)
def test_a_task_the_weekly_limit_stops_waits_until_two_minutes_after_its_reset(b: Bench):
    """Given the review, stacked, which the weekly limit stops at 00:41 until 00:00 three days on,
    and which then finishes
    When it is carried
    Then it waits until 00:02 three days on, and is finished"""
    reset = at(0, 0, 4)
    b.script(
        PAYMENTS_PROMPT,
        claude_double.Answer("limited", "so far", STOPPED, reset, weekly=True),
        finished("the rest", reset + timedelta(hours=1)),
    )

    carry(b.queue_file, stacked(b))

    assert b.clock.waits == [reset + timedelta(minutes=2)]
    assert b.run_of("review-payments")["state"] == "finished"


@pytest.mark.supports("test_a_failed_session_gives_up_its_task_and_the_others_go_on")
def test_a_task_whose_session_fails_is_given_up_with_why_and_its_session(b: Bench):
    """Given the review, stacked, whose session ends on a server error with part of its reply
    When it is carried
    Then it is given up with why and its session, run once, its reply holding that part"""
    b.script(PAYMENTS_PROMPT, failed("half a review", at(23, 10)))

    carry(b.queue_file, stacked(b))

    run = b.run_of("review-payments")
    assert (run["state"], run["session"], moment(run["ended"])) == (
        "given up",
        b.asked()[0].session,
        at(23, 10),
    )
    assert run["why"] and len(b.asked()) == 1
    assert b.reply("review-payments").rstrip("\n") == "half a review"


@pytest.mark.supports("test_a_carried_on_task_whose_session_is_gone_is_given_up")
def test_a_task_whose_session_claude_no_longer_has_is_given_up_naming_it(b: Bench):
    """Given the review, stacked again in a session that Claude Code no longer has
    When it is carried
    Then it goes on by `--resume` in that session, and is given up with why and that session"""
    carry(b.queue_file, stacked(b, "4e7b5bed-5c23-4a6e-c6c8-1c4d4d3d3d04"))

    run = b.run_of("review-payments")
    assert (run["state"], run["session"]) == ("given up", "4e7b5bed-5c23-4a6e-c6c8-1c4d4d3d3d04")
    assert run["why"]


@pytest.mark.supports("test_a_task_given_up_stops_no_other_task")
def test_a_task_whose_session_cant_start_is_given_up_with_why(b: Bench, monkeypatch: Any):
    """Given the review, stacked, on a computer with no `claude`
    When it is carried
    Then it is given up with why, with no session, and nothing escapes"""

    def no_claude(arguments: Any, cwd: str) -> Any:
        raise FileNotFoundError(2, "No such file or directory", "claude")

    monkeypatch.setattr(claude, "claude", no_claude)

    carry(b.queue_file, stacked(b))

    run = b.run_of("review-payments")
    assert (run["state"], "session" in run) == ("given up", False)
    assert run["why"]


@pytest.mark.supports("test_a_task_given_up_stops_no_other_task")
def test_a_task_whose_reply_cant_be_written_is_given_up_and_nothing_escapes(b: Bench):
    """Given the review, stacked, whose session finishes, where a folder lies in place of its reply
    file
    When it is carried
    Then it is given up with why, and nothing escapes"""
    b.script(PAYMENTS_PROMPT, finished("reviewed"))
    carried = stacked(b)
    os.makedirs(os.path.join(b.folder, "review-payments.md"))

    carry(b.queue_file, carried)

    run = b.run_of("review-payments")
    assert run["state"] == "given up" and run["why"]


@pytest.mark.supports("test_a_task_given_up_stops_no_other_task")
def test_a_task_the_queue_no_longer_keeps_lets_nothing_escape(b: Bench):
    """Given a task named `review-refunds`, which the stacked queue doesn't keep, whose session
    finishes
    When it is carried
    Then nothing escapes, and the review of the payments stands as it was"""
    b.script(PAYMENTS_PROMPT, finished("reviewed"))
    carried = stacked(b)
    before = b.runs()
    other = Carried(
        queue_file.Task("review-refunds", carried.task.prompt, carried.task.dir, False), None
    )

    carry(b.queue_file, other)

    assert b.runs() == before

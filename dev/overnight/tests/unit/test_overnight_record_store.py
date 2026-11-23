"""The unit cases of record/store.py, how each part reads and writes a queue's runs and replies:
`standing`, of a queue never stacked, of the walkthrough's morning, of a queue left by a stop with
no lock held and with its lock held, and of a runs' file out of form; `stack`, of a queue never
stacked, of one left by a stop with tasks finished, given up, and never started, and of one whose
folder can't be written; `hold`, free and held by another runner; `mark`, of one task among
several, of several at once, and of a name the queue doesn't keep; and `add_reply`, of a first
part, of a part after a wait, and of a name the queue doesn't keep."""

from __future__ import annotations

import os
import threading

import pytest
from overnight_bench import (
    AFTER_THE_LIMIT,
    BEFORE_THE_LIMIT,
    FIX_ENDED,
    FIX_SESSION,
    PAYMENTS_ENDED,
    PAYMENTS_SESSION,
    REFUNDS_ENDED,
    REFUNDS_SESSION,
    STACKED,
    STOPPED,
    WENT_ON,
    Bench,
    held_elsewhere,
    keep,
    moment,
    payments_reply,
    run_json,
    the_morning,
    wait_json,
    walkthrough_queue,
    walkthrough_tasks,
)
from record import lock, store
from record.replies import Reply
from record.runs import Kept, Run, Wait
from record.store import NotStacked, Standing, Stood

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def left_by_a_stop_after_a_wait(b: Bench) -> None:
    """The record as a runner that stopped left it: the review of the payments running in its
    session after one wait for the limit, the review of the refunds finished, and the fix given up
    before it started."""
    payments, refunds, fix = walkthrough_tasks(b)
    keep(
        b,
        [
            (
                payments,
                run_json("running", session="s", stops=1, waits=[wait_json(STOPPED, WENT_ON)]),
            ),
            (refunds, run_json("finished", session="r", ended=REFUNDS_ENDED)),
            (fix, run_json("given up", ended=STOPPED, why="overnight stopped")),
        ],
    )


@pytest.mark.supports("test_a_check_of_a_queue_never_stacked_shows_the_version_and_writes_nothing")
def test_a_queue_never_stacked_stands_nowhere(b: Bench):
    """Given the walkthrough's queue file, never stacked
    When where its tasks stand is read
    Then it refuses with NotStacked, and writes nothing beside it"""
    with pytest.raises(NotStacked):
        store.standing(b.queue_file)

    assert not os.path.exists(b.folder)


@pytest.mark.supports("test_the_morning_check_shows_each_task_finished_with_its_reply_and_wait")
def test_the_walkthroughs_morning_stands_as_its_runner_left_it(b: Bench):
    """Given the walkthrough's queue as its runner leaves it the next morning
    When where its tasks stand is read
    Then no runner carries it, and each task stands finished in the queue's order, the review of
    the payments after its wait, each with its reply's path"""
    the_morning(b)

    standing = store.standing(b.queue_file)

    payments, refunds, fix = walkthrough_queue(b).tasks
    assert standing == Standing(
        False,
        (
            Stood(
                payments,
                Run(
                    "finished",
                    PAYMENTS_SESSION,
                    1,
                    (Wait(STOPPED, WENT_ON),),
                    None,
                    PAYMENTS_ENDED,
                    None,
                ),
                os.path.join(b.folder, "review-payments.md"),
            ),
            Stood(
                refunds,
                Run(
                    "finished",
                    REFUNDS_SESSION,
                    0,
                    (),
                    None,
                    REFUNDS_ENDED,
                    None,
                ),
                os.path.join(b.folder, "review-refunds.md"),
            ),
            Stood(
                fix,
                Run("finished", FIX_SESSION, 0, (), None, FIX_ENDED, None),
                os.path.join(b.folder, "fix-flaky-checkout.md"),
            ),
        ),
    )


@pytest.mark.supports(
    "test_a_check_after_a_stop_gives_up_the_tasks_left_and_says_how_to_carry_them_on"
)
def test_a_queue_left_by_a_stop_stands_with_its_unended_task_given_up_and_written(b: Bench):
    """Given the walkthrough's queue left by a stop, with no lock held: the review of the payments
    running in its session, the review of the refunds finished, the fix given up
    When where its tasks stand is read, at 22:30 on the clock
    Then no runner carries it, the review of the payments stands given up at 22:30 with why, its
    session, its stop, and its wait, the others as they were, and `runs.json` holds the same"""
    left_by_a_stop_after_a_wait(b)
    before = b.runs()

    standing = store.standing(b.queue_file)

    payments = standing.tasks[0].run
    assert standing.carried is False
    assert (payments.state, payments.session, payments.stops, payments.ended) == (
        "given up",
        "s",
        1,
        STACKED,
    )
    assert payments.waits == (Wait(STOPPED, WENT_ON),) and payments.why
    assert [each.run.state for each in standing.tasks[1:]] == ["finished", "given up"]
    assert b.runs()[1:] == before[1:]
    written = b.runs()[0]["run"]
    assert (written["state"], written["session"], moment(written["ended"])) == (
        "given up",
        "s",
        STACKED,
    )


@pytest.mark.supports(
    "test_a_check_while_the_runner_carries_the_queue_tells_the_tasks_not_ended_as_running",
    "test_a_queue_whose_runner_still_carries_it_is_refused_with_where_its_tasks_stand",
)
def test_a_queue_whose_runner_holds_its_lock_stands_carried_and_unchanged(b: Bench):
    """Given the walkthrough's queue left by a stop, whose lock another runner holds
    When where its tasks stand is read
    Then a runner carries it, the review of the payments still stands running, and `runs.json` is
    as it was"""
    left_by_a_stop_after_a_wait(b)
    before = b.runs()

    with held_elsewhere(b.queue_file):
        standing = store.standing(b.queue_file)

    assert standing.carried is True
    assert standing.tasks[0].run.state == "running"
    assert b.runs() == before


@pytest.mark.supports("test_a_check_of_a_runs_file_out_of_form_says_whats_wrong")
def test_a_runs_file_out_of_form_is_refused(b: Bench):
    """Given the walkthrough's queue whose `runs.json` isn't JSON
    When where its tasks stand is read
    Then it refuses with ValueError, and leaves the file as it was"""
    path = b.write(os.path.join(b.folder, "runs.json"), "[")

    with pytest.raises(ValueError):
        store.standing(b.queue_file)

    with open(path, encoding="utf-8") as f:
        assert f.read() == "["


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_a_queue_never_stacked_is_written_with_each_task_waiting_for_the_start(b: Bench):
    """Given the walkthrough's queue, never stacked
    When it is written for its runner
    Then it gives each task waiting for the start with no session, in the queue's order, and
    `runs.json` beside the queue file holds the same"""
    kept = store.stack(walkthrough_queue(b))

    waiting = Run("waiting for the start", None, 0, (), None, None, None)
    assert kept == tuple(Kept(task, waiting) for task in walkthrough_queue(b).tasks)
    assert b.runs() == [
        {"task": task, "run": {"state": "waiting for the start", "stops": 0, "waits": []}}
        for task in walkthrough_tasks(b)
    ]


@pytest.mark.supports("test_stacking_again_carries_on_each_unfinished_task_in_its_session")
def test_a_queue_left_by_a_stop_is_written_with_its_unfinished_tasks_carried_on(b: Bench):
    """Given the walkthrough's queue left by a stop: the review of the payments given up in its
    session after a stop, the review of the refunds finished, and the fix given up before it
    started
    When it is written for its runner
    Then it gives the review of the payments in its session and the fix, each waiting for the
    start with no stops, and leaves the review of the refunds finished as it ended"""
    payments, refunds, fix = walkthrough_tasks(b)
    refunded = run_json("finished", session="r", ended=REFUNDS_ENDED)
    keep(
        b,
        [
            (payments, run_json("given up", session="s", stops=1, ended=STOPPED, why="w")),
            (refunds, refunded),
            (fix, run_json("given up", ended=STOPPED, why="overnight stopped")),
        ],
    )

    kept = store.stack(walkthrough_queue(b))

    assert [
        (each.task.name, each.run.state, each.run.session, each.run.stops) for each in kept
    ] == [
        ("review-payments", "waiting for the start", "s", 0),
        ("fix-flaky-checkout", "waiting for the start", None, 0),
    ]
    assert b.run_of("review-refunds") == refunded
    assert b.run_of("review-payments")["state"] == "waiting for the start"


@pytest.mark.supports("test_a_runner_that_the_os_doesnt_start_leaves_the_record_to_carry_on")
def test_a_queue_whose_folder_cant_be_written_is_refused(b: Bench):
    """Given the walkthrough's queue, where a file lies in place of its folder
    When it is written for its runner
    Then it refuses with OSError, and leaves the file as it was"""
    b.write(b.folder, "in the way")

    with pytest.raises(OSError):
        store.stack(walkthrough_queue(b))

    with open(b.folder, encoding="utf-8") as f:
        assert f.read() == "in the way"


@pytest.mark.supports(
    "test_a_queue_whose_runner_still_carries_it_is_refused_with_where_its_tasks_stand",
    "test_a_runner_started_on_a_queue_that_another_runner_carries_runs_no_task",
)
def test_a_queues_lock_is_held_while_the_runner_carries_it(b: Bench):
    """Given the walkthrough's queue, stacked
    When its lock is held, and then held again where another runner holds it
    Then the first holds the queue's lock, and the second refuses with Held"""
    store.stack(walkthrough_queue(b))

    with store.hold(b.queue_file):
        pass
    with held_elsewhere(b.queue_file), pytest.raises(lock.Held), store.hold(b.queue_file):
        pass


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_a_run_marked_replaces_its_tasks_alone(b: Bench):
    """Given the walkthrough's queue, stacked
    When the review of the refunds is marked running in its session
    Then `runs.json` holds that run for it, and the other two as they were"""
    store.stack(walkthrough_queue(b))
    before = b.runs()

    store.mark(b.queue_file, "review-refunds", Run("running", "r", 0, (), None, None, None))

    after = b.runs()
    assert after[1]["run"] == {"state": "running", "session": "r", "stops": 0, "waits": []}
    assert [after[0], after[2]] == [before[0], before[2]]


@pytest.mark.supports(
    "test_a_task_given_up_stops_no_other_task",
    "test_the_tasks_start_at_the_start_three_at_a_time_in_the_queues_order",
)
def test_runs_marked_at_once_each_land(b: Bench):
    """Given the walkthrough's queue, stacked
    When its three tasks are marked finished at once, each from a thread of its own, forty times
    Then `runs.json` holds each finished"""
    store.stack(walkthrough_queue(b))
    done = Run("finished", "s", 0, (), None, PAYMENTS_ENDED, None)
    names = ["review-payments", "review-refunds", "fix-flaky-checkout"]

    def mark(name: str) -> None:
        for _ in range(40):
            store.mark(b.queue_file, name, done)

    threads = [threading.Thread(target=mark, args=(name,)) for name in names]
    for each in threads:
        each.start()
    for each in threads:
        each.join()

    assert [each["run"]["state"] for each in b.runs()] == ["finished"] * 3


@pytest.mark.supports("test_a_task_given_up_stops_no_other_task")
def test_a_run_of_a_name_the_queue_doesnt_keep_is_refused(b: Bench):
    """Given the walkthrough's queue, stacked
    When a run of `review` is marked
    Then it refuses with KeyError, and leaves `runs.json` as it was"""
    store.stack(walkthrough_queue(b))
    before = b.runs()

    with pytest.raises(KeyError):
        store.mark(b.queue_file, "review", Run("running", None, 0, (), None, None, None))

    assert b.runs() == before


@pytest.mark.supports("test_a_resumed_tasks_reply_follows_its_earlier_one_with_the_wait")
def test_a_reply_after_a_wait_follows_the_first_part_with_the_line_of_the_wait(b: Bench):
    """Given the walkthrough's queue, stacked, whose review of the payments answered its first
    part, and then stood running after its wait from 00:41 to 01:42
    When its second part is added
    Then its reply file is the README's"""
    store.stack(walkthrough_queue(b))
    store.add_reply(b.queue_file, "review-payments", Reply(BEFORE_THE_LIMIT))
    run = Run("running", "s", 1, (Wait(STOPPED, WENT_ON),), None, None, None)
    store.mark(b.queue_file, "review-payments", run)

    store.add_reply(b.queue_file, "review-payments", Reply(AFTER_THE_LIMIT))

    assert b.reply("review-payments").rstrip("\n") == payments_reply()


@pytest.mark.supports("test_a_task_given_up_stops_no_other_task")
def test_a_reply_of_a_name_the_queue_doesnt_keep_is_refused(b: Bench):
    """Given the walkthrough's queue, stacked
    When a reply of `review` is added
    Then it refuses with KeyError, and writes no reply file of it"""
    store.stack(walkthrough_queue(b))

    with pytest.raises(KeyError):
        store.add_reply(b.queue_file, "review", Reply("text"))

    assert not os.path.exists(os.path.join(b.folder, "review.md"))

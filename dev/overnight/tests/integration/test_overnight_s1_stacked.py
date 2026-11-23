"""The integration cases of S1, the stacked tasks carried to their ends: each path through its
sequence, from `/overnight:stack` through the stacker, the record, and the runner to each session's
end, as the skill and the runner run the scripts' parts, with the doubles of Claude Code and the
clock. Each names the elements and the data of the handoffs it checks."""

from __future__ import annotations

import os
import shutil
from datetime import timedelta
from typing import Any

import claude_double
import overnight_bench
import pytest
from claude_double import failed, finished, limited
from overnight_bench import (
    FIX_ENDED,
    FIX_PROMPT,
    FIX_REPLY,
    PAYMENTS_ENDED,
    PAYMENTS_PROMPT,
    PAYMENTS_SESSION,
    REFUNDS_ENDED,
    REFUNDS_PROMPT,
    REFUNDS_REPLY,
    RESET,
    START,
    STOPPED,
    WENT_ON,
    Bench,
    Ran,
    at,
    checked_text,
    held_elsewhere,
    keep,
    left_by_a_stop,
    moment,
    no_sandbox,
    one_review,
    payments_reply,
    run_json,
    stacked_text,
    the_morning,
    walkthrough,
    walkthrough_night,
    walkthrough_tasks,
)

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def each_finishes(b: Bench) -> None:
    """Scripts each of the walkthrough's tasks to finish on its first run."""
    for prompt in (PAYMENTS_PROMPT, REFUNDS_PROMPT, FIX_PROMPT):
        b.script(prompt, finished("done"))


@pytest.mark.supports(
    "S1", "stacker", "runner", "session", "record", "Queue", "Task", "Run", "Reply"
)
def test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit(b: Bench):
    """Given the walkthrough's queue of three tasks from 23:00, stacked at 22:30, whose review of
    the payments reaches the usage limit at 00:41 until 01:40, and whose fix edits its folder
    When the user stacks it, and its runner carries it
    Then the stacking shows the README's text, the runner waits until 23:00 and ends with 0, each
    task runs in its own folder, the review of the payments goes on in its session at 01:42, each
    run is finished at the README's moments with its session and its wait, each reply is as the
    README shows it, and the check shows the README's text"""
    walkthrough(b)
    walkthrough_night(b)

    assert b.stack() == Ran(0, stacked_text(b.queue_file), "")
    assert b.run().code == 0

    asked = b.asked()
    assert b.clock.waits[0] == START
    assert sorted((each.prompt, each.cwd) for each in asked) == sorted(
        [
            (PAYMENTS_PROMPT, b.path("work", "shop")),
            (PAYMENTS_PROMPT, b.path("work", "shop")),
            (REFUNDS_PROMPT, b.path("work", "shop")),
            (FIX_PROMPT, b.path("work", "shop-fix-flaky-checkout")),
        ]
    )
    payments = [each for each in asked if each.prompt == PAYMENTS_PROMPT]
    assert payments[1].session == payments[0].session
    sessions = {each.prompt: each.session for each in asked}
    assert [each["task"] for each in b.runs()] == walkthrough_tasks(b)
    paid = b.run_of("review-payments")
    assert (paid["state"], paid["session"], paid["stops"]) == (
        "finished",
        sessions[PAYMENTS_PROMPT],
        1,
    )
    assert [(moment(w["stopped"]), moment(w["went_on"])) for w in paid["waits"]] == [
        (STOPPED, WENT_ON)
    ]
    assert moment(paid["ended"]) == PAYMENTS_ENDED
    assert "until" not in paid and "why" not in paid
    for name, prompt, ended in (
        ("review-refunds", REFUNDS_PROMPT, REFUNDS_ENDED),
        ("fix-flaky-checkout", FIX_PROMPT, FIX_ENDED),
    ):
        run = b.run_of(name)
        assert {k: v for k, v in run.items() if k != "ended"} == {
            "state": "finished",
            "session": sessions[prompt],
            "stops": 0,
            "waits": [],
        }
        assert moment(run["ended"]) == ended
    assert b.reply("review-payments").rstrip("\n") == payments_reply()
    assert b.reply("review-refunds").rstrip("\n") == REFUNDS_REPLY
    assert b.reply("fix-flaky-checkout").rstrip("\n") == FIX_REPLY
    assert b.check(b.queue_file) == Ran(0, checked_text(b), "")


@pytest.mark.supports("S1", "stacker", "Task")
def test_a_queue_with_a_prompt_and_a_dir_not_there_is_refused_with_each_fault(b: Bench):
    """Given the walkthrough's queue, whose review of the refunds names a prompt's file that isn't
    there and whose fix names a dir that isn't there
    When the user stacks it
    Then it gives 1 naming the prompt's file and the dir, writes no record, and starts no runner"""
    walkthrough(b)
    os.remove(b.path("overnight", "review-refunds.md"))
    shutil.rmtree(b.path("work", "shop-fix-flaky-checkout"))

    ran = b.stack()

    assert ran.code == 1
    assert b.path("overnight", "review-refunds.md") in ran.out + ran.err
    assert b.path("work", "shop-fix-flaky-checkout") in ran.out + ran.err
    assert not os.path.exists(b.folder)
    assert b.handed == []


@pytest.mark.supports("S1", "stacker", "session")
def test_a_writing_task_where_the_sandbox_cant_run_is_refused_at_stacking(b: Bench):
    """Given the walkthrough's queue, whose fix may write, on a computer where Claude Code's
    sandbox can't run
    When the user stacks it
    Then it gives 1 naming the fix, writes no record, and starts no runner"""
    walkthrough(b)
    no_sandbox(b)

    ran = b.stack()

    assert ran.code == 1
    assert "fix-flaky-checkout" in ran.out + ran.err
    assert not os.path.exists(b.folder)
    assert b.handed == []


@pytest.mark.supports("S1", "stacker", "record", "Run")
def test_a_queue_whose_runner_still_carries_it_is_refused_with_where_its_tasks_stand(b: Bench):
    """Given the walkthrough's queue, stacked, whose runner still holds its lock
    When the user stacks it again
    Then it gives 1 naming each task, leaves the record as it was, and starts no other runner"""
    walkthrough(b)
    assert b.stack().code == 0
    before = b.runs()

    with held_elsewhere(b.queue_file):
        ran = b.stack()

    assert ran.code == 1
    for name in ("review-payments", "review-refunds", "fix-flaky-checkout"):
        assert name in ran.out + ran.err
    assert b.runs() == before
    assert len(b.handed) == 1


@pytest.mark.supports("S1", "stacker", "Queue")
def test_a_queue_naming_a_task_twice_is_refused_with_its_mend(b: Bench):
    """Given a queue file whose two tasks share the name `review`
    When the user stacks it
    Then it gives 1 naming `review`, writes no record, and starts no runner"""
    walkthrough(b)
    task = {"name": "review", "prompt": "review-payments.md", "dir": b.path("work", "shop")}
    b.queue({"tasks": [task, dict(task, prompt="review-refunds.md")]})

    ran = b.stack()

    assert ran.code == 1
    assert "review" in ran.out + ran.err
    assert not os.path.exists(b.folder)
    assert b.handed == []


@pytest.mark.supports("S1", "runner", "Queue")
def test_a_queue_stacked_anew_waits_for_its_start(b: Bench):
    """Given the walkthrough's queue from 23:00, stacked at 22:30, whose tasks each finish
    When the user stacks it, and its runner carries it
    Then the runner waits until 23:00 that night before it runs any task"""
    walkthrough(b)
    each_finishes(b)
    started: list[int] = []
    b.clock.probes.append(lambda _: started.append(len(b.asked())))

    b.stack()
    b.run()

    assert b.clock.waits == [START]
    assert started == [0]


@pytest.mark.supports("S1", "runner", "Queue")
def test_a_queue_stacked_after_its_start_hour_waits_for_it_the_next_day(
    tmp_path: Any, monkeypatch: Any
):
    """Given the walkthrough's queue from 23:00, stacked at 23:30, whose tasks each finish
    When the user stacks it, and its runner carries it
    Then the runner waits until 23:00 of the next day before it runs any task"""
    b = overnight_bench.bench(str(tmp_path), monkeypatch, at(23, 30))
    walkthrough(b)
    each_finishes(b)

    b.stack()
    b.run()

    assert b.clock.waits == [at(23, 0, 1)]


@pytest.mark.supports("S1", "runner", "record", "Task", "Run")
def test_a_queue_stacked_again_after_a_stop_starts_its_tasks_at_once(
    tmp_path: Any, monkeypatch: Any
):
    """Given the walkthrough's queue from 23:00, left by a runner that stopped, stacked again at
    23:30 the same night
    When its runner carries it
    Then it waits for no start, and runs the review of the payments and the fix"""
    b = overnight_bench.bench(str(tmp_path), monkeypatch, at(23, 30))
    walkthrough(b)
    left_by_a_stop(b)
    claude_double.had(b.claude, PAYMENTS_PROMPT, PAYMENTS_SESSION)
    b.script(PAYMENTS_PROMPT, finished("the rest"))
    b.script(FIX_PROMPT, finished(FIX_REPLY))

    assert b.stack().code == 0
    assert b.run().code == 0

    assert b.clock.waits == []
    assert sorted(each.prompt for each in b.asked()) == sorted([PAYMENTS_PROMPT, FIX_PROMPT])


@pytest.mark.supports("S1", "runner", "Queue")
def test_a_queue_without_start_starts_its_tasks_at_once(b: Bench):
    """Given the walkthrough's queue with no start, whose tasks each finish
    When the user stacks it, and its runner carries it
    Then the runner waits for nothing and runs each task"""
    walkthrough(b, start=None)
    each_finishes(b)

    assert b.stack().code == 0
    assert b.run().code == 0

    assert b.clock.waits == []
    assert sorted(each.prompt for each in b.asked()) == sorted(
        [PAYMENTS_PROMPT, REFUNDS_PROMPT, FIX_PROMPT]
    )


@pytest.mark.supports("S1", "runner", "record", "Run")
def test_a_task_waiting_for_the_limit_stands_waiting_until_it_goes_on(b: Bench):
    """Given the walkthrough's night, whose review of the payments reaches the limit at 00:41 until
    01:40
    When its runner waits for the review to go on
    Then the record holds the review waiting for the limit until 01:42, stopped once, with its wait
    from 00:41 and its session, and its reply's part from before the limit"""
    walkthrough(b)
    walkthrough_night(b)
    seen: list[dict[str, Any]] = []

    def probe(moment: Any) -> None:
        if moment == WENT_ON:
            seen.append(b.run_of("review-payments"))

    b.clock.probes.append(probe)
    b.stack()

    b.run()

    first = next(each for each in b.asked() if each.prompt == PAYMENTS_PROMPT)
    assert len(seen) == 1
    waiting = seen[0]
    assert (waiting["state"], waiting["session"], waiting["stops"]) == (
        "waiting for the limit",
        first.session,
        1,
    )
    assert moment(waiting["until"]) == WENT_ON
    assert [{k: moment(v) for k, v in w.items()} for w in waiting["waits"]] == [
        {"stopped": STOPPED}
    ]


@pytest.mark.supports("S1", "runner", "Run")
def test_a_task_stopped_the_seventh_time_is_given_up_with_why_and_its_session(b: Bench):
    """Given a queue of the review of the payments, whose session the limit stops seven times, each
    for an hour
    When its runner carries it
    Then the session runs seven times, all in one session, each after a wait to two minutes past
    the reset, and the task is given up at its seventh stop with why, its session, seven stops, and
    six waits"""
    walkthrough(b, start=None)
    one_review(b)
    stops = [at(23, 0) + timedelta(hours=2 * n) for n in range(7)]
    b.script(
        PAYMENTS_PROMPT,
        *[limited(f"part {n + 1}", stop, stop + (RESET - STOPPED)) for n, stop in enumerate(stops)],
    )

    b.stack()
    assert b.run().code == 0

    asked = b.asked()
    assert len(asked) == 7
    assert {each.session for each in asked} == {asked[0].session}
    went_on = [stop + (WENT_ON - STOPPED) for stop in stops[:6]]
    assert b.clock.waits == went_on
    run = b.run_of("review-payments")
    assert (run["state"], run["session"], run["stops"]) == ("given up", asked[0].session, 7)
    assert run["why"]
    assert moment(run["ended"]) == stops[6]
    assert [(moment(w["stopped"]), moment(w["went_on"])) for w in run["waits"]] == list(
        zip(stops[:6], went_on)
    )


@pytest.mark.supports("S1", "runner", "session", "Reply")
def test_a_failed_session_gives_up_its_task_and_the_others_go_on(b: Bench):
    """Given the walkthrough's queue with no start, whose review of the payments ends on a server
    error with part of its reply, and whose other tasks finish
    When its runner carries it
    Then the review is given up with why and its session, its reply holds that part, the others
    are finished, and the runner ends with 0"""
    walkthrough(b, start=None)
    b.script(PAYMENTS_PROMPT, failed("## The checks of a card payment", at(23, 10)))
    b.script(REFUNDS_PROMPT, finished(REFUNDS_REPLY))
    b.script(FIX_PROMPT, finished(FIX_REPLY))

    b.stack()
    assert b.run().code == 0

    session = next(each.session for each in b.asked() if each.prompt == PAYMENTS_PROMPT)
    run = b.run_of("review-payments")
    assert (run["state"], run["session"]) == ("given up", session)
    assert run["why"]
    assert b.reply("review-payments").rstrip("\n") == "## The checks of a card payment"
    assert b.run_of("review-refunds")["state"] == "finished"
    assert b.run_of("fix-flaky-checkout")["state"] == "finished"


@pytest.mark.supports("S1", "runner", "session", "Run")
def test_a_carried_on_task_whose_session_is_gone_is_given_up(b: Bench):
    """Given the walkthrough's queue left by a stop, whose review of the payments ran in a session
    that Claude Code no longer has
    When the user stacks it again, and its runner carries it
    Then the review is given up with why and the session it named, and the fix is finished"""
    walkthrough(b, start=None)
    left_by_a_stop(b, session="4e7b5bed-5c23-4a6e-c6c8-1c4d4d3d3d04")
    b.script(FIX_PROMPT, finished(FIX_REPLY))

    b.stack()
    assert b.run().code == 0

    run = b.run_of("review-payments")
    assert (run["state"], run["session"]) == ("given up", "4e7b5bed-5c23-4a6e-c6c8-1c4d4d3d3d04")
    assert run["why"]
    assert b.run_of("fix-flaky-checkout")["state"] == "finished"


@pytest.mark.supports("S1", "record", "Run")
def test_a_carried_on_task_counts_its_stops_at_the_limit_from_zero(b: Bench):
    """Given a queue of the review of the payments, left by a stop after the limit stopped it six
    times, stacked again, whose session the limit then stops once more before it finishes
    When its runner carries it
    Then the review goes on after the wait, and is finished with one stop"""
    walkthrough(b, start=None)
    payments = walkthrough_tasks(b)[0]
    one_review(b)
    keep(
        b, [(payments, run_json("given up", session="1b4e28ba", stops=6, why="overnight stopped"))]
    )
    claude_double.had(b.claude, PAYMENTS_PROMPT, "1b4e28ba")
    b.script(
        PAYMENTS_PROMPT,
        limited("before", STOPPED, RESET),
        finished("after", PAYMENTS_ENDED),
    )

    b.stack()
    b.run()

    run = b.run_of("review-payments")
    assert (run["state"], run["session"], run["stops"]) == ("finished", "1b4e28ba", 1)


@pytest.mark.supports("S1", "runner")
def test_a_runner_started_on_a_queue_that_another_runner_carries_runs_no_task(b: Bench):
    """Given the walkthrough's queue, stacked, whose lock another runner holds
    When the runner that the stacking started runs
    Then it gives 1 with what's wrong, and runs no task"""
    walkthrough(b)
    walkthrough_night(b)
    b.stack()

    with held_elsewhere(b.queue_file):
        ran = b.run()

    assert ran.code == 1
    assert ran.out + ran.err
    assert b.asked() == []


@pytest.mark.supports("S1", "stacker", "record")
def test_a_runner_that_the_os_doesnt_start_leaves_the_record_to_carry_on(
    b: Bench, monkeypatch: Any
):
    """Given the walkthrough's queue, on a computer that refuses to start the runner
    When the user stacks it, and then stacks it again where the computer starts it
    Then the first gives 2 with what the OS said and leaves each task waiting for the start, and
    the second gives 0 and hands the runner each task"""
    from runner import handoff
    from stacker import detach

    walkthrough(b)

    def refused(given: Any) -> None:
        raise detach.CantStart("fork: Resource temporarily unavailable")

    monkeypatch.setattr(detach, "start_runner", refused)
    ran = b.stack()
    monkeypatch.setattr(detach, "start_runner", lambda h: b.handed.append(handoff.encode(h)))

    assert ran.code == 2
    assert "Resource temporarily unavailable" in ran.out + ran.err
    assert [each["run"]["state"] for each in b.runs()] == ["waiting for the start"] * 3
    assert b.stack().code == 0
    given = handoff.decode(b.handed[0])
    assert [each.task.name for each in given.tasks] == [
        "review-payments",
        "review-refunds",
        "fix-flaky-checkout",
    ]


@pytest.mark.supports("S1", "stacker", "record")
def test_a_runs_file_out_of_form_refuses_the_stacking(b: Bench):
    """Given the walkthrough's queue, whose `runs.json` isn't JSON
    When the user stacks it
    Then it gives 1 naming the runs' file, leaves it as it was, and starts no runner"""
    walkthrough(b)
    runs = b.write(os.path.join(b.folder, "runs.json"), "{not json")

    ran = b.stack()

    assert ran.code == 1
    assert runs in ran.out + ran.err
    with open(runs, encoding="utf-8") as f:
        assert f.read() == "{not json"
    assert b.handed == []


@pytest.mark.supports("S1", "runner", "session", "Task")
def test_each_task_runs_in_its_own_folder_with_its_prompt(b: Bench):
    """Given the walkthrough's queue with no start, whose tasks each finish
    When its runner carries it
    Then each session runs in its task's dir with its task's prompt, the fix's edit lands in its
    dir, and each run is asked once"""
    walkthrough(b, start=None)
    walkthrough_night(b)
    b.script(PAYMENTS_PROMPT, finished("done"))

    b.stack()
    b.run()

    assert sorted((each.prompt, each.cwd) for each in b.asked()) == sorted(
        [
            (PAYMENTS_PROMPT, b.path("work", "shop")),
            (REFUNDS_PROMPT, b.path("work", "shop")),
            (FIX_PROMPT, b.path("work", "shop-fix-flaky-checkout")),
        ]
    )
    fix = next(each for each in b.asked() if each.prompt == FIX_PROMPT)
    assert [use["allowed"] for use in fix.uses] == [True, True, True]
    assert claude_double.at_once(b.claude) <= 3


@pytest.mark.supports("S1", "stacker", "record", "Run")
def test_a_queue_whose_every_task_finished_stacked_again_starts_no_runner(b: Bench):
    """Given the walkthrough's queue the next morning, each task finished
    When the user stacks it again
    Then it gives 0 saying that every task finished, starts no runner, runs no task, and leaves
    the record as it was"""
    walkthrough(b)
    the_morning(b)
    before = b.runs()

    ran = b.stack()

    assert ran.code == 0 and "finished" in ran.out
    assert b.handed == [] and b.asked() == []
    assert b.runs() == before

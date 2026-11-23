"""The integration cases of S2, the results taken in: each path through its sequence, from
`/overnight:check` through the checker and the record, as the skill runs the checker's part, on a
record as overnight's runner leaves it. Each names the elements and the data of the handoffs it
checks."""

from __future__ import annotations

import json
import os

import pytest
from overnight_bench import (
    PAYMENTS_SESSION,
    UNNAMED,
    Bench,
    Ran,
    checked_text,
    held_elsewhere,
    left_by_a_stop,
    run_json,
    the_morning,
    walkthrough,
    walkthrough_tasks,
)

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


@pytest.mark.supports("S2", "checker", "record", "Task", "Run", "Reply")
def test_the_morning_check_shows_each_task_finished_with_its_reply_and_wait(b: Bench):
    """Given the walkthrough's queue as its runner leaves it the next morning, each task finished
    and the review of the payments after its wait
    When the user checks it in a new session
    Then it gives 0 with the README's text, and leaves the record as it was"""
    walkthrough(b)
    the_morning(b)
    before = b.runs()

    assert b.check(b.queue_file) == Ran(0, checked_text(b), "")
    assert b.runs() == before


@pytest.mark.supports("S2", "checker", "Queue")
def test_a_check_naming_the_queue_from_its_folder_shows_the_same(b: Bench):
    """Given the walkthrough's queue as its runner leaves it the next morning
    When the user checks it by its path from the folder they run in
    Then it gives 0 with the README's text, the queue file named whole"""
    walkthrough(b)
    the_morning(b)

    assert b.check(os.path.join("overnight", "tonight.json")) == Ran(0, checked_text(b), "")


@pytest.mark.supports("S2", "checker", "commands")
def test_a_check_naming_no_queue_shows_the_version_and_what_to_name(b: Bench):
    """Given overnight installed
    When the user checks with no queue file
    Then it gives 0 with overnight's version and what to name"""
    ran = b.check()

    assert (ran.code, ran.out.rstrip("\n"), ran.err) == (0, UNNAMED, "")


@pytest.mark.supports("S2", "checker", "record")
def test_a_check_of_a_queue_never_stacked_shows_the_version_and_writes_nothing(b: Bench):
    """Given the walkthrough's queue file, never stacked
    When the user checks it
    Then it gives 0 with overnight's version and what to name, and writes nothing beside it"""
    walkthrough(b)

    ran = b.check(b.queue_file)

    assert (ran.code, ran.out.rstrip("\n"), ran.err) == (0, UNNAMED, "")
    assert not os.path.exists(b.folder)


@pytest.mark.supports("S2", "checker", "record", "Run")
def test_a_check_after_a_stop_gives_up_the_tasks_left_and_says_how_to_carry_them_on(b: Bench):
    """Given the walkthrough's queue left by a runner that stopped: the review of the payments
    running in its session, the review of the refunds finished, the fix not yet started
    When the user checks it
    Then it gives 0 counting one finished and two given up, names why each was given up and how to
    stack the queue again, and the record holds each of the two given up with why, the review with
    its session"""
    walkthrough(b)
    left_by_a_stop(b)

    ran = b.check(b.queue_file)

    assert ran.code == 0
    assert ran.out.startswith(f"3 tasks from {b.queue_file}: 1 finished, 2 given up.\n")
    assert f"/overnight:stack {b.queue_file}" in ran.out
    payments = b.run_of("review-payments")
    fix = b.run_of("fix-flaky-checkout")
    assert (payments["state"], payments["session"]) == ("given up", PAYMENTS_SESSION)
    assert (fix["state"], "session" in fix) == ("given up", False)
    assert payments["why"] and payments["why"] in ran.out
    assert fix["why"] and fix["why"] in ran.out
    assert b.run_of("review-refunds")["state"] == "finished"


@pytest.mark.supports("S2", "checker", "record")
def test_a_check_while_the_runner_carries_the_queue_tells_the_tasks_not_ended_as_running(b: Bench):
    """Given the walkthrough's queue whose runner still holds its lock, with the review of the
    payments running, the review of the refunds finished at 23:52, and the fix waiting for the start
    When the user checks it
    Then it gives 0, telling the review of the payments and the fix as still running beside the
    end of the review of the refunds, and the record is left as it was"""
    walkthrough(b)
    left_by_a_stop(b)
    before = b.runs()

    with held_elsewhere(b.queue_file):
        ran = b.check(b.queue_file)

    assert ran.code == 0
    lines = ran.out.split("\n")
    for name in ("review-payments", "fix-flaky-checkout"):
        told = [each for each in lines if each.startswith(f"- {name}:")]
        assert len(told) == 1 and "running" in told[0] and "given up" not in told[0]
    assert "- review-refunds: finished at 23:52." in lines
    assert b.runs() == before


@pytest.mark.supports("S2", "checker", "record")
def test_a_check_of_a_runs_file_out_of_form_says_whats_wrong(b: Bench):
    """Given the walkthrough's queue, whose `runs.json` holds a run of a state that overnight has
    no name for
    When the user checks it
    Then it gives 1 naming the runs' file, and leaves it as it was"""
    walkthrough(b)
    tasks = [{"task": walkthrough_tasks(b)[0], "run": run_json("paused")}]
    runs = b.write(os.path.join(b.folder, "runs.json"), json.dumps({"tasks": tasks}))

    ran = b.check(b.queue_file)

    assert ran.code == 1
    assert runs in ran.out + ran.err
    with open(runs, encoding="utf-8") as f:
        assert json.load(f) == {"tasks": tasks}

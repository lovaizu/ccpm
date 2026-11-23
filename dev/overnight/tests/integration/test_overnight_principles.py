"""The integration cases of each principle item of overnight's architecture: each where the parts
keep it, as the skill and the runner run the scripts' parts, and each with the fixture `broken`,
which takes the part that holds the item out where TRACE_BROKEN is 1."""

from __future__ import annotations

import os
from datetime import timedelta

import claude_double
import pytest
from claude_double import Use, failed, finished, limited
from overnight_bench import (
    AFTER_THE_LIMIT,
    BEFORE_THE_LIMIT,
    FIX_ENDED,
    FIX_PROMPT,
    FIX_REPLY,
    PAYMENTS_ENDED,
    PAYMENTS_PROMPT,
    REFUNDS_ENDED,
    REFUNDS_PROMPT,
    REFUNDS_REPLY,
    RESET,
    START,
    STOPPED,
    WAIT_LINE,
    WENT_ON,
    Bench,
    Detached,
    at,
    keep,
    one_review,
    payments_reply,
    run_json,
    until,
    walkthrough,
    walkthrough_night,
    walkthrough_tasks,
)

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

# P1: no one there while the tasks run.


@pytest.mark.supports("P1.1", "runner", "commands")
def test_the_tasks_go_on_after_the_stacking_session_ends(d: Detached, broken: None):
    """Given a queue of two reviews with no start, each of which finishes
    When the user stacks it in a session that then ends, every program left in it stopped
    Then the stacking gives 0, and each task is finished afterward, with its reply"""
    os.makedirs(d.path("work", "shop"))
    for name, text in (("review-payments", PAYMENTS_PROMPT), ("review-refunds", REFUNDS_PROMPT)):
        d.write(d.path("overnight", f"{name}.md"), text)
    tasks = [
        {"name": name, "prompt": f"{name}.md", "dir": d.path("work", "shop")}
        for name in ("review-payments", "review-refunds")
    ]
    d.queue({"tasks": tasks})
    d.script(PAYMENTS_PROMPT, finished("payments reviewed"))
    d.script(REFUNDS_PROMPT, finished(REFUNDS_REPLY))

    def ended() -> bool:
        if not os.path.exists(os.path.join(d.folder, "runs.json")):
            return False
        return [each["run"]["state"] for each in d.runs()] == ["finished"] * 2

    assert d.stack(d.queue_file).code == 0
    assert until(ended)
    assert d.reply("review-refunds").rstrip("\n") == REFUNDS_REPLY


@pytest.mark.supports("P1.2", "session")
def test_a_task_uses_its_tools_with_no_permission_asked(b: Bench, broken: None):
    """Given the walkthrough's queue with no start, whose fix reads and edits its code and runs its
    test, and whose reviews read their folder
    When its runner carries it
    Then each use of a tool by each task is allowed, none denied, and each task is finished"""
    walkthrough(b, start=None)
    code = b.path("work", "shop", "shop", "checkout.py")
    fixed = b.path("work", "shop-fix-flaky-checkout", "shop", "checkout.py")
    for prompt in (PAYMENTS_PROMPT, REFUNDS_PROMPT):
        b.script(prompt, finished("reviewed", uses=(Use("Read", code), Use("Grep", code))))
    uses = (Use("Read", fixed), Use("Edit", fixed), Use("Bash", command="pytest tests"))
    b.script(FIX_PROMPT, finished(FIX_REPLY, uses=uses))

    b.stack()
    b.run()

    assert [use["allowed"] for each in b.asked() for use in each.uses] == [True] * 7
    assert [each["run"]["state"] for each in b.runs()] == ["finished"] * 3


@pytest.mark.supports("P1.3", "session")
def test_a_task_writes_only_where_the_queue_lets_it(b: Bench, broken: None):
    """Given the walkthrough's queue with no start, whose review of the payments tries to edit a
    file and to write one by the shell in its folder, and whose fix edits its folder's code, writes
    a file in its folder and one in the temporary folder by the shell, and tries to write one in the
    user's home by the shell and by an edit
    When its runner carries it
    Then only the fix's edit and its two writes in its folder and the temporary folder are made,
    each other refused, and no file lies where a refused use would write it"""
    walkthrough(b, start=None)
    shop = b.path("work", "shop")
    fix_dir = b.path("work", "shop-fix-flaky-checkout")
    outside = b.path("outside.txt")
    temporary = os.path.join(claude_double.temporary(b.claude), "cache.txt")
    b.script(
        PAYMENTS_PROMPT,
        finished(
            "reviewed",
            uses=(
                Use("Edit", os.path.join(shop, "shop", "checkout.py")),
                Use("Bash", os.path.join(shop, "notes.txt"), "echo x > notes.txt"),
            ),
        ),
    )
    b.script(REFUNDS_PROMPT, finished("reviewed"))
    b.script(
        FIX_PROMPT,
        finished(
            FIX_REPLY,
            uses=(
                Use("Edit", os.path.join(fix_dir, "shop", "checkout.py")),
                Use("Bash", os.path.join(fix_dir, "log.txt"), "pytest > log.txt"),
                Use("Bash", temporary, f"echo x > {temporary}"),
                Use("Bash", outside, f"echo x > {outside}"),
                Use("Write", outside),
            ),
        ),
    )

    b.stack()
    b.run()

    made = {each.prompt: [use["allowed"] for use in each.uses] for each in b.asked()}
    assert made[PAYMENTS_PROMPT] == [False, False]
    assert made[FIX_PROMPT] == [True, True, True, False, False]
    assert not os.path.exists(outside)
    assert not os.path.exists(os.path.join(shop, "notes.txt"))
    with open(os.path.join(shop, "shop", "checkout.py"), encoding="utf-8") as f:
        assert f.read() == "PRICES = {}\n"
    assert os.path.exists(temporary)


@pytest.mark.supports("P1.4", "stacker")
def test_a_queue_with_one_task_that_cant_start_runs_no_task(b: Bench, broken: None):
    """Given the walkthrough's queue, whose fix names a prompt's file that isn't there
    When the user stacks it
    Then it gives 1, and no task runs: no record is written and no runner started"""
    walkthrough(b)
    walkthrough_night(b)
    os.remove(b.path("overnight", "fix-flaky-checkout.md"))

    ran = b.stack()

    assert ran.code == 1
    assert not os.path.exists(b.folder)
    assert b.handed == []
    assert b.asked() == []


@pytest.mark.supports("P1.5", "commands", "runner")
def test_a_queue_of_one_waits_and_ends_as_any_queue(b: Bench, broken: None):
    """Given a plugin's AI's queue of one review with no start, which the usage limit stops at 00:41
    until 01:40
    When the AI stacks it, its runner carries it, and the AI checks it
    Then the stacking gives 0, the review goes on at 01:42 in its session and is finished, and the
    check counts it finished after its wait"""
    walkthrough(b)
    queue_file = one_review(b)
    b.script(
        PAYMENTS_PROMPT,
        limited(BEFORE_THE_LIMIT, STOPPED, RESET),
        finished(AFTER_THE_LIMIT, PAYMENTS_ENDED),
    )

    assert b.stack(queue_file).code == 0
    assert b.run().code == 0
    ran = b.check(queue_file)

    assert b.clock.waits == [WENT_ON]
    run = b.run_of("review-payments")
    assert (run["state"], run["stops"]) == ("finished", 1)
    assert ran.code == 0
    assert ran.out.split("\n")[0].endswith(f"from {queue_file}: 1 finished, 0 given up.")
    assert "after waiting for the usage limit from 00:41 to 01:42" in ran.out


# P2: past the usage limit.


@pytest.mark.supports("P2.1", "runner", "session", "Run")
def test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset(
    b: Bench, broken: None
):
    """Given a queue of one review with no start, which the usage limit stops at 00:41 until 01:40
    When its runner carries it
    Then the runner waits until 01:42, and the review goes on there by `--resume` in the session it
    started in, and is finished"""
    walkthrough(b)
    one_review(b)
    b.script(
        PAYMENTS_PROMPT,
        limited(BEFORE_THE_LIMIT, STOPPED, RESET),
        finished(AFTER_THE_LIMIT, PAYMENTS_ENDED),
    )

    b.stack()
    b.run()

    first, second = b.asked()
    assert b.clock.waits == [WENT_ON]
    assert "--resume" in second.arguments
    assert second.arguments[second.arguments.index("--resume") + 1] == first.session
    assert b.run_of("review-payments")["state"] == "finished"


@pytest.mark.supports("P2.2", "runner", "Run")
def test_the_seventh_stop_at_the_limit_gives_the_task_up_with_why_and_its_session(
    b: Bench, broken: None
):
    """Given a queue of one review with no start, which the usage limit stops seven times, and which
    would finish on an eighth run
    When its runner carries it
    Then it runs seven times, and is given up at the seventh stop with why and its session"""
    walkthrough(b)
    one_review(b)
    stops = [at(23, 0) + timedelta(hours=2 * n) for n in range(7)]
    b.script(
        PAYMENTS_PROMPT,
        *[
            limited(f"part {n + 1}", stop, stop + timedelta(minutes=59))
            for n, stop in enumerate(stops)
        ],
        finished("the rest"),
    )

    b.stack()
    b.run()

    asked = b.asked()
    run = b.run_of("review-payments")
    assert len(asked) == 7
    assert (run["state"], run["session"], run["stops"]) == ("given up", asked[0].session, 7)
    assert run["why"]


# P3: every task ends, and says how.


@pytest.mark.supports("P3.1", "runner", "session", "Run")
def test_each_task_ends_finished_or_given_up_with_why_and_its_session(b: Bench, broken: None):
    """Given the walkthrough's queue with no start, whose review of the payments ends on a server
    error, and whose other tasks finish
    When its runner carries it
    Then the review is given up with why and its session, and the others are finished with their
    sessions"""
    walkthrough(b, start=None)
    b.script(PAYMENTS_PROMPT, failed("half a review"))
    b.script(REFUNDS_PROMPT, finished(REFUNDS_REPLY))
    b.script(FIX_PROMPT, finished(FIX_REPLY))

    b.stack()
    b.run()

    sessions = {each.prompt: each.session for each in b.asked()}
    payments = b.run_of("review-payments")
    assert (payments["state"], payments["session"]) == ("given up", sessions[PAYMENTS_PROMPT])
    assert payments["why"]
    for name, prompt in (("review-refunds", REFUNDS_PROMPT), ("fix-flaky-checkout", FIX_PROMPT)):
        run = b.run_of(name)
        assert (run["state"], run["session"], "why" in run) == ("finished", sessions[prompt], False)


@pytest.mark.supports("P3.2", "runner")
def test_a_task_given_up_stops_no_other_task(b: Bench, broken: None):
    """Given the walkthrough's queue with no start, whose review of the payments meets a fault, and
    whose other tasks finish
    When its runner carries it
    Then the runner ends with 0, the review is given up with why, and the others are finished"""
    walkthrough(b, start=None)
    b.script(PAYMENTS_PROMPT, failed())
    b.script(REFUNDS_PROMPT, finished(REFUNDS_REPLY))
    b.script(FIX_PROMPT, finished(FIX_REPLY))

    b.stack()
    ran = b.run()

    assert ran.code == 0
    payments = b.run_of("review-payments")
    assert payments["state"] == "given up" and payments["why"]
    assert b.run_of("review-refunds")["state"] == "finished"
    assert b.run_of("fix-flaky-checkout")["state"] == "finished"


@pytest.mark.supports("P3.3", "record", "checker", "Run")
def test_a_task_left_unended_by_a_stop_ends_given_up_with_that_reason(b: Bench, broken: None):
    """Given the walkthrough's queue whose runner stopped, with no lock held, while the review of
    the payments ran in its session
    When the user checks it
    Then the review is given up with why and its session, the check shows that why, and checking
    again gives the same"""
    walkthrough(b)
    payments, refunds, fix = walkthrough_tasks(b)
    keep(
        b,
        [
            (payments, run_json("running", session="1b4e28ba")),
            (refunds, run_json("finished", session="2c5f39cb", ended=REFUNDS_ENDED)),
            (fix, run_json("finished", session="3d6a4adc", ended=FIX_ENDED)),
        ],
    )

    ran = b.check(b.queue_file)

    run = b.run_of("review-payments")
    assert (run["state"], run["session"]) == ("given up", "1b4e28ba")
    assert run["why"] and run["why"] in ran.out
    assert b.check(b.queue_file) == ran


@pytest.mark.supports("P3.4", "stacker", "record", "Task", "Run")
def test_stacking_again_carries_on_each_unfinished_task_in_its_session(b: Bench, broken: None):
    """Given the walkthrough's queue with no start, left by a stop: the review of the payments
    given up in its session, the review of the refunds finished, the fix not yet started
    When the user stacks it again, and its runner carries it
    Then the review of the payments goes on in its session, the fix starts anew, the review of the
    refunds doesn't run and stays as it ended, and the first two are finished"""
    walkthrough(b, start=None)
    payments, refunds, fix = walkthrough_tasks(b)
    refunded = run_json("finished", session="2c5f39cb", ended=REFUNDS_ENDED)
    keep(
        b,
        [
            (payments, run_json("given up", session="1b4e28ba", why="overnight stopped")),
            (refunds, refunded),
            (fix, run_json("given up", why="overnight stopped")),
        ],
    )
    claude_double.had(b.claude, PAYMENTS_PROMPT, "1b4e28ba")
    b.script(PAYMENTS_PROMPT, finished("the rest"))
    b.script(REFUNDS_PROMPT, finished("again"))
    b.script(FIX_PROMPT, finished(FIX_REPLY))

    assert b.stack().code == 0
    b.run()

    asked = {each.prompt: each for each in b.asked()}
    assert sorted(asked) == sorted([PAYMENTS_PROMPT, FIX_PROMPT])
    resumed = asked[PAYMENTS_PROMPT].arguments
    assert resumed[resumed.index("--resume") + 1] == "1b4e28ba"
    assert "--resume" not in asked[FIX_PROMPT].arguments
    assert b.run_of("review-refunds") == refunded
    assert b.run_of("review-payments")["state"] == "finished"
    assert b.run_of("fix-flaky-checkout")["state"] == "finished"


# P4: the people's working day left free.


@pytest.mark.supports("P4.1", "runner", "Queue")
def test_the_tasks_start_at_the_start_three_at_a_time_in_the_queues_order(b: Bench, broken: None):
    """Given a queue from 23:00 of five reviews, stacked at 22:30, listed last name first, each of
    which takes a while
    When its runner carries it
    Then it waits until 23:00, runs three at a time and never more, and starts the fourth and fifth
    in the queue's order after the first three"""
    names = ["e", "d", "c", "b", "a"]
    for name in names:
        b.write(b.path("overnight", f"{name}.md"), f"Review the module {name}/.")
        b.script(f"Review the module {name}/.", finished("reviewed", seconds=0.5))
    b.write(b.path("work", "shop", "README"), "")
    b.queue(
        {
            "start": "23:00",
            "tasks": [
                {"name": name, "prompt": f"{name}.md", "dir": b.path("work", "shop")}
                for name in names
            ],
        }
    )

    b.stack()
    b.run()

    assert b.clock.waits == [START]
    assert claude_double.at_once(b.claude) == 3
    started = [each.prompt for each in b.asked()]
    assert sorted(started[:3]) == sorted(f"Review the module {n}/." for n in names[:3])
    assert started[3:] == [f"Review the module {n}/." for n in names[3:]]


# P5: the whole result, taken in afterward.


@pytest.mark.supports("P5.1", "record", "Reply")
def test_a_resumed_tasks_reply_follows_its_earlier_one_with_the_wait(b: Bench, broken: None):
    """Given a queue of one review with no start, which the usage limit stops at 00:41 until 01:40
    after the checks of a card payment, and which goes on to the checks of a refund
    When its runner carries it
    Then its reply file holds the first part, the line saying the limit stopped it at 00:41 and it
    went on at 01:42, and the second part, as the README shows it"""
    walkthrough(b)
    one_review(b)
    b.script(
        PAYMENTS_PROMPT,
        limited(BEFORE_THE_LIMIT, STOPPED, RESET),
        finished(AFTER_THE_LIMIT, PAYMENTS_ENDED),
    )

    b.stack()
    b.run()

    assert b.reply("review-payments").rstrip("\n") == payments_reply()
    assert WAIT_LINE in payments_reply()


@pytest.mark.supports("P5.2", "record", "checker", "Run", "Reply")
def test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session(b: Bench, broken: None):
    """Given the walkthrough's queue, carried to its end
    When a later session reads the folder beside the queue file, named after it
    Then `runs.json` there holds each task and its run, each reply lies there as `<task>.md`, and
    the check names each reply there"""
    walkthrough(b, start=None)
    walkthrough_night(b)
    b.stack()
    b.run()

    beside = b.path("overnight", "tonight")
    assert [each["task"]["name"] for each in b.runs(beside)] == [
        "review-payments",
        "review-refunds",
        "fix-flaky-checkout",
    ]
    for name in ("review-payments", "review-refunds", "fix-flaky-checkout"):
        assert os.path.isfile(os.path.join(beside, f"{name}.md"))
        assert f"Reply: {os.path.join(beside, name + '.md')}" in b.check(b.queue_file).out


@pytest.mark.supports("P5.3", "session")
def test_what_a_task_writes_stays_in_its_dir_as_written(b: Bench, broken: None):
    """Given the walkthrough's queue with no start, whose fix edits its folder's code
    When its runner carries it, and the user checks it
    Then the code in the fix's dir holds what the session wrote, and the check names that dir as
    the one it wrote in"""
    walkthrough(b, start=None)
    walkthrough_night(b)
    b.stack()
    b.run()

    fixed = b.path("work", "shop-fix-flaky-checkout", "shop", "checkout.py")
    with open(fixed, encoding="utf-8") as f:
        assert f.read() == f"written by the session of {FIX_PROMPT[:40]!r}\n"
    assert f"Wrote in: {b.path('work', 'shop-fix-flaky-checkout')}" in b.check(b.queue_file).out

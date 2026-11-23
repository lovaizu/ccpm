"""The unit cases of session/session.py, how a task's session runs: `run`, of a task anew and of one
in its session, that finishes and that the limit stops, read at the moment it ended, of a writing
task whose edit lands in its dir, of a prompt's file gone, and of no `claude` on the computer."""

from __future__ import annotations

import os
from typing import Any

import claude_double
import pytest
from claude_double import Use, finished, limited
from overnight_bench import (
    FIX_PROMPT,
    PAYMENTS_PROMPT,
    RESET,
    STOPPED,
    Bench,
)
from session import claude
from session.ending import Failed, Finished, Limited
from session.session import run
from stacker.queue_file import Task

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def review(b: Bench) -> Task:
    return Task(
        "review-payments", b.path("overnight", "review-payments.md"), b.path("work", "shop"), False
    )


def fix(b: Bench) -> Task:
    return Task(
        "fix-flaky-checkout",
        b.path("overnight", "fix-flaky-checkout.md"),
        b.path("work", "shop-fix-flaky-checkout"),
        True,
    )


@pytest.mark.supports("test_each_task_runs_in_its_own_folder_with_its_prompt")
def test_a_task_anew_runs_its_prompt_in_its_dir_and_finishes(b: Bench):
    """Given the review, whose session finishes
    When it is run anew
    Then `claude` runs once in its dir with its prompt's text, and it gives finished with the reply
    and the session"""
    b.script(PAYMENTS_PROMPT, finished("reviewed"))

    ended = run(review(b), None)

    asked = b.asked()
    assert [(each.prompt, each.cwd) for each in asked] == [
        (PAYMENTS_PROMPT, b.path("work", "shop"))
    ]
    assert ended == Finished("reviewed", asked[0].session)


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset"
)
def test_a_task_in_its_session_goes_on_in_it(b: Bench):
    """Given the review, in a session that Claude Code keeps from an earlier night, whose session
    then finishes
    When it is run in that session
    Then `claude` resumes it, and it gives finished in that session"""
    claude_double.had(b.claude, PAYMENTS_PROMPT, "1b4e28ba")
    b.script(PAYMENTS_PROMPT, finished("the rest"))

    ended = run(review(b), "1b4e28ba")

    assert ended == Finished("the rest", "1b4e28ba")
    assert "1b4e28ba" in b.asked()[0].arguments


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset"
)
def test_a_task_the_limit_stops_gives_limited_read_at_the_moment_it_ended(b: Bench):
    """Given the review, whose session the limit stops at 00:41 until 01:40
    When it is run anew
    Then it gives limited with the part, the session, and the reset at 01:40"""
    b.script(PAYMENTS_PROMPT, limited("so far", STOPPED, RESET))

    assert run(review(b), None) == Limited("so far", b.asked()[0].session, RESET)


@pytest.mark.supports(
    "test_each_task_runs_in_its_own_folder_with_its_prompt",
    "test_what_a_task_writes_stays_in_its_dir_as_written",
)
def test_a_writing_tasks_edit_lands_in_its_dir(b: Bench):
    """Given the fix, which may write, whose session edits its code
    When it is run anew
    Then the edit is allowed, and the code in its dir holds what the session wrote"""
    code = b.path("work", "shop-fix-flaky-checkout", "shop", "checkout.py")
    b.script(FIX_PROMPT, finished("fixed", uses=(Use("Edit", code),)))

    run(fix(b), None)

    assert [use["allowed"] for use in b.asked()[0].uses] == [True]
    with open(code, encoding="utf-8") as f:
        assert f.read() == f"written by the session of {FIX_PROMPT[:40]!r}\n"


@pytest.mark.supports("test_a_task_given_up_stops_no_other_task")
def test_a_prompts_file_gone_gives_failed_with_why_and_runs_nothing(b: Bench):
    """Given the review, whose prompt's file is gone since it was stacked
    When it is run anew
    Then it gives failed with no reply, no session, and why, and `claude` doesn't run"""
    os.remove(b.path("overnight", "review-payments.md"))

    ended = run(review(b), None)

    assert isinstance(ended, Failed)
    assert (ended.reply, ended.session, bool(ended.why)) == ("", None, True)
    assert b.asked() == []


@pytest.mark.supports("test_a_task_given_up_stops_no_other_task")
def test_no_claude_on_the_computer_gives_failed_with_why(b: Bench, monkeypatch: Any):
    """Given the review, on a computer with no `claude`
    When it is run anew
    Then it gives failed with no reply, no session, and why"""

    def no_claude(arguments: Any, cwd: str) -> Any:
        raise FileNotFoundError(2, "No such file or directory", "claude")

    monkeypatch.setattr(claude, "claude", no_claude)

    ended = run(review(b), None)

    assert isinstance(ended, Failed)
    assert (ended.reply, ended.session, bool(ended.why)) == ("", None, True)

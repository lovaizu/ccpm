"""The unit cases of one work's course, as the README's Walkthrough and How it works say: its runs
of `claude`, the waits between them, and what its folder records, carried in the test's own
process with a double of `claude` and a clock that each wait moves on."""

from __future__ import annotations

import datetime
import json
import os

from double.claude_double import (
    DONE,
    KILLED,
    NO_CONVERSATION,
    RATE_LIMIT,
    REFUSED,
    RESUMED,
    Host,
    session_of,
)
from overnight.work import Work, carry

PROMPT = "Move the tests to pytest"
CLAUDE = ["claude", "-p", "--output-format", "json", "--allowed-tools", "Read,Edit"]
STOPPED = "API Error: Rate limit reached"
NOT_FOUND = "No conversation found with session ID: 11111111-1111-1111-1111-111111111111"
REFUSAL = (
    "There's an issue with the selected model (claude-nonexistent-9). It may not exist or you may"
    " not have access to it. Run --model to pick a different model"
)


class Clock:
    """A clock that starts at 23:15 and moves on only by each wait, keeping each wait in seconds."""

    def __init__(self) -> None:
        self.at = datetime.datetime(2026, 11, 28, 23, 15)
        self.waits: list[float] = []

    def now(self) -> datetime.datetime:
        return self.at

    def sleep(self, seconds: float) -> None:
        self.waits.append(seconds)
        self.at += datetime.timedelta(seconds=seconds)


def _carried(tmp_path, retries: int, *events: str) -> tuple[Host, Clock, str]:
    folder = tmp_path / "20261128-231502"
    folder.mkdir()
    host, clock = Host(*events), Clock()
    carry(
        str(folder), Work(str(tmp_path), "Read,Edit", retries, PROMPT), host, clock.now, clock.sleep
    )
    return host, clock, str(folder)


def _log(folder: str) -> list[str]:
    with open(os.path.join(folder, "log"), encoding="utf-8") as f:
        return f.read().splitlines()


def _state(folder: str) -> dict:
    with open(os.path.join(folder, "state.json"), encoding="utf-8") as f:
        return json.load(f)


def test_a_work_whose_first_run_is_done_is_recorded_done(tmp_path):
    """Given a work whose first run of `claude` is done
    When overnight carries the work
    Then it ran `claude -p` once in the work's folder with the prompt, and records the work done"""
    host, clock, folder = _carried(tmp_path, 7, DONE)
    assert host.calls == [(CLAUDE, str(tmp_path), PROMPT)]
    assert clock.waits == []
    assert _log(folder) == [
        "23:15 run 1 started",
        "23:15 run 1 done",
        "work 20261128-231502 done after 1 run",
    ]
    assert _state(folder) == {
        "status": "done",
        "dir": str(tmp_path),
        "session_id": session_of(DONE),
        "runs": 1,
    }


def test_a_stopped_run_is_retried_in_its_session_after_5_minutes(tmp_path):
    """Given a work whose first run the rate limit stops, exiting 0, and whose second run is done
    When overnight carries the work
    Then it waits 5 minutes, asks `claude` to continue in the first run's session, and records the
    work done after 2 runs"""
    host, clock, folder = _carried(tmp_path, 7, RATE_LIMIT, RESUMED)
    resume = [*CLAUDE, "--resume", session_of(RATE_LIMIT)]
    assert host.calls == [(CLAUDE, str(tmp_path), PROMPT), (resume, str(tmp_path), "continue")]
    assert clock.waits == [300]
    assert _log(folder) == [
        "23:15 run 1 started",
        f"23:15 run 1 stopped: {STOPPED}. Retry 1 of 7 at 23:20.",
        "23:20 run 2 started",
        "23:20 run 2 done",
        "work 20261128-231502 done after 2 runs",
    ]
    assert _state(folder) == {
        "status": "done",
        "dir": str(tmp_path),
        "session_id": session_of(RESUMED),
        "runs": 2,
    }


def test_a_work_records_where_it_stands_while_it_waits(tmp_path):
    """Given a work whose first run the API refuses, exiting 1
    When overnight waits for the retry
    Then state.json says the work is running, in the first run's session, after 1 run"""
    folder = tmp_path / "20261128-231502"
    folder.mkdir()
    seen: list[dict] = []
    clock = Clock()

    def sleep(seconds: float) -> None:
        seen.append(_state(str(folder)))
        clock.sleep(seconds)

    work = Work(str(tmp_path), "Read,Edit", 7, PROMPT)
    carry(str(folder), work, Host(REFUSED, RESUMED), clock.now, sleep)
    assert seen == [
        {"status": "running", "dir": str(tmp_path), "session_id": session_of(REFUSED), "runs": 1}
    ]


def test_a_retry_after_a_run_that_named_no_session_gives_the_prompt_again(tmp_path):
    """Given a work whose first run is killed before it names a session, and whose second is done
    When overnight carries the work
    Then the retry runs `claude -p` with the prompt again, as no session holds what was done"""
    host, _, folder = _carried(tmp_path, 7, KILLED, DONE)
    assert host.calls == [(CLAUDE, str(tmp_path), PROMPT), (CLAUDE, str(tmp_path), PROMPT)]
    assert _log(folder) == [
        "23:15 run 1 started",
        "23:15 run 1 stopped: exit code -9. Retry 1 of 7 at 23:20.",
        "23:20 run 2 started",
        "23:20 run 2 done",
        "work 20261128-231502 done after 2 runs",
    ]


def test_a_retry_after_a_resume_that_finds_no_conversation_resumes_the_same_session(tmp_path):
    """Given a work whose first run the rate limit stops, whose resume finds no conversation, and
    whose third run is done
    When overnight carries the work
    Then the second retry asks `claude` to continue in the first run's session again, as the
    resume that found none named no other"""
    host, _, folder = _carried(tmp_path, 7, RATE_LIMIT, NO_CONVERSATION, RESUMED)
    resume = [*CLAUDE, "--resume", session_of(RATE_LIMIT)]
    assert host.calls == [
        (CLAUDE, str(tmp_path), PROMPT),
        (resume, str(tmp_path), "continue"),
        (resume, str(tmp_path), "continue"),
    ]
    assert _log(folder) == [
        "23:15 run 1 started",
        f"23:15 run 1 stopped: {STOPPED}. Retry 1 of 7 at 23:20.",
        "23:20 run 2 started",
        f"23:20 run 2 stopped: {NOT_FOUND}. Retry 2 of 7 at 23:30.",
        "23:30 run 3 started",
        "23:30 run 3 done",
        "work 20261128-231502 done after 3 runs",
    ]


def test_a_work_whose_7_retries_run_out_is_recorded_failed(tmp_path):
    """Given a work whose runs all stop, and 7 retries
    When overnight carries the work
    Then it runs `claude -p` with the prompt, then asks it to continue in the first run's session
    after waits of 5, 10, and 20 minutes, then 60 minutes each, and records the work failed after
    8 runs"""
    host, clock, folder = _carried(tmp_path, 7, *[REFUSED] * 8)
    resume = [*CLAUDE, "--resume", session_of(REFUSED)]
    assert (
        host.calls == [(CLAUDE, str(tmp_path), PROMPT)] + [(resume, str(tmp_path), "continue")] * 7
    )
    assert clock.waits == [300, 600, 1200, 3600, 3600, 3600, 3600]
    assert _log(folder) == [
        "23:15 run 1 started",
        f"23:15 run 1 stopped: {REFUSAL}. Retry 1 of 7 at 23:20.",
        "23:20 run 2 started",
        f"23:20 run 2 stopped: {REFUSAL}. Retry 2 of 7 at 23:30.",
        "23:30 run 3 started",
        f"23:30 run 3 stopped: {REFUSAL}. Retry 3 of 7 at 23:50.",
        "23:50 run 4 started",
        f"23:50 run 4 stopped: {REFUSAL}. Retry 4 of 7 at 00:50.",
        "00:50 run 5 started",
        f"00:50 run 5 stopped: {REFUSAL}. Retry 5 of 7 at 01:50.",
        "01:50 run 6 started",
        f"01:50 run 6 stopped: {REFUSAL}. Retry 6 of 7 at 02:50.",
        "02:50 run 7 started",
        f"02:50 run 7 stopped: {REFUSAL}. Retry 7 of 7 at 03:50.",
        "03:50 run 8 started",
        f"03:50 run 8 stopped: {REFUSAL}. No retries left.",
        "work 20261128-231502 failed after 8 runs",
    ]
    assert _state(folder) == {
        "status": "failed",
        "dir": str(tmp_path),
        "session_id": session_of(REFUSED),
        "runs": 8,
    }


def test_a_work_with_no_retries_fails_at_its_first_stop(tmp_path):
    """Given a work whose first run stops, and 0 retries
    When overnight carries the work
    Then it runs `claude` once, waits for nothing, and records the work failed after 1 run"""
    host, clock, folder = _carried(tmp_path, 0, RATE_LIMIT)
    assert (len(host.calls), clock.waits) == (1, [])
    assert _log(folder) == [
        "23:15 run 1 started",
        f"23:15 run 1 stopped: {STOPPED}. No retries left.",
        "work 20261128-231502 failed after 1 run",
    ]
    assert _state(folder) == {
        "status": "failed",
        "dir": str(tmp_path),
        "session_id": session_of(RATE_LIMIT),
        "runs": 1,
    }

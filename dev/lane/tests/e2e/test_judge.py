"""The case of the judge by which Lane's E2E cases read KR1.1, as N4.3 of the test implementation
best practice asks before any run relies on it: on each run of write that the developer marked in
fixtures/judge/messages.json, the judge on Opus gives their mark. The marked runs' records stay in
the worktree, as git ignores them, so a run whose records aren't here is skipped."""

from __future__ import annotations

import json
import os
from typing import Any

import measures as m
import opus
import pytest

TOP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4))
MESSAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "judge")


def marked() -> list[Any]:
    """Each marked run of write, as a parameter named by its records and its number."""
    with open(os.path.join(MESSAGES, "messages.json"), encoding="utf-8") as f:
        messages = json.load(f)["messages"]
    return [
        pytest.param(m, id=f"{os.path.basename(m['records'])} run {m['run']}")
        for m in messages
        if m["mark"] is not None
    ]


@opus.NEEDS_LOGIN
@pytest.mark.supports("KR1.1")
@pytest.mark.parametrize("message", marked())
def test_the_judge_gives_each_marked_run_its_mark(message: dict[str, Any]) -> None:
    """Given: a run of write that the developer marked as keeping its steps or failing them.
    When: the judge on Opus reads the run's records.
    Then: it gives the developer's mark."""
    records = os.path.join(TOP, message["records"])
    if not os.path.isdir(records):
        pytest.skip(f"{message['records']} isn't in this worktree")
    runs = m.runs_of_write(records)
    run = runs[message["run"] - 1]
    verdict = opus.judged(m.judge_prompt(records, run, message["run"], len(runs)), m.VERDICT)
    assert verdict["keeps"] is message["mark"], f"the judge's places: {verdict.get('places')}"

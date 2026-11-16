"""The E2E cases of Lane: the README's walkthrough, with S4's steps changed and laid again, and S3's
AI that approves by its own act, each run by dev/scripts/e2e.py on the real Claude Code on Opus, as
Lane's Test strategy says under Scenario testing, and Lane installed by the README's commands, as it
says under Installation testing. Each run's records give the key results: KR1.1 from the starts,
calls, and ends of each run of changelog's write, judged on Opus where only reading the steps
tells, and KR1.2 from the time of the person's first turn to the end of the first run that keeps
the steps. Runs are added until one more moves no mean by a step: a percent of KR1.1's share, a
minute of KR1.2's time. They run on the developer's login, so a case without one is
skipped, as opus.NEEDS_LOGIN says."""

from __future__ import annotations

import itertools
import os
import re
from dataclasses import dataclass
from typing import Any

import opus
import pytest
import scenario
import walkthrough as w

pytestmark = [
    pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies"),
    opus.NEEDS_LOGIN,
]

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = ("walkthrough.json", "ai-approves.json")
# The routes of the walkthrough's write, as each start after each Result.
NEXT = {None: "writer", ("writer", "written"): "reviewer", ("reviewer", "more"): "writer"}
JUDGE = """You read the records of one run of the Claude Code plugin changelog, whose skill write \
and subagents writer and reviewer must keep the numbered steps of their files, given below with \
what the run changed in them. Count \
each place where a role did other than its step says, as a run's transcript shows it, such as a \
step skipped or work its step doesn't name. Reply with JSON {"off_steps": <count>, "places": \
[<each place: the role, its step, and what it did>]}."""


@dataclass
class Run:
    """One run of changelog's write in one E2E run, as its records show it: each subagent it
    started, by its role, and each Result given, as (role, result), in the order they came."""

    moves: list[str | tuple[str, str]]
    ended: str | None


# The records of each E2E run of each test file in this session, so that KR1.1 and KR1.2 are
# measured on the same runs, as Test strategy measures them, and no run is made twice.
RECORDS: dict[str, list[str]] = {}


def records_of(test: str, n: int) -> str:
    """The folder of the records of the n-th E2E run of the test file, counted from 0, which e2e.py
    makes where this session has made none yet."""
    made = RECORDS.setdefault(test, [])
    while len(made) <= n:
        made.append(scenario.e2e(os.path.join(HERE, test)))
    return made[n]


def runs_of_write(records: str) -> list[Run]:
    """Each run of changelog's write that the records' hook events show: each subagent it started,
    each Result given by result.py, and the time it ended by write's own Result. A run starts where
    the person types /changelog:write, or where an AI calls the skill by the Skill tool, as S3's AI
    does, which no UserPromptExpansion shows."""
    runs: list[Run] = []
    for each in scenario.jsonl(os.path.join(records, "hooks.jsonl")):
        event = each.get("payload", each)
        if write_starts(event):
            runs.append(Run([], None))
            continue
        for move in moves_of(event) if runs else []:
            if move[0] == "write":
                runs[-1].ended = each.get("time")
            else:
                runs[-1].moves.append(move if move[1] else move[0])
    return runs


def moves_of(event: dict[str, Any]) -> list[tuple[str, str]]:
    """The moves of a run that the hook event shows: a subagent's start, as (role, ""), and each
    Result that a result.py in its command gives, as (role, result)."""
    if event.get("hook_event_name") != "PostToolUse":
        return []
    given = event["tool_input"]
    started = (
        [(given["subagent_type"].split(":")[-1], "")] if event.get("tool_name") == "Agent" else []
    )
    return started + RESULT.findall(given.get("command", ""))


# A run of changelog's result.py, not up's, with the role and the Result it gives, which a command
# may hold among others.
RESULT = re.compile(r"changelog/hooks/lane/result\.py (\w+) (\w+)")


def write_starts(event: dict[str, Any]) -> bool:
    """Whether the hook event starts a run of changelog's write: the person's /changelog:write, or
    an AI's Skill call of it."""
    if event.get("hook_event_name") == "UserPromptExpansion":
        return event.get("command_name") == "changelog:write"
    called = event.get("hook_event_name") == "PostToolUse" and event.get("tool_name") == "Skill"
    return called and event["tool_input"].get("skill") == "changelog:write"


def order_faults(run: Run) -> int:
    """Each start of the run that its routes didn't make due by then, each start due that never
    came, and an end by no Result of write."""
    due, faults = [NEXT[None]], 0
    for move in run.moves:
        if isinstance(move, str):
            faults += 0 if due and move == due.pop(0) else 1
        elif move in NEXT:
            due.append(NEXT[move])
    return faults + len(due) + (0 if run.ended else 1)


def off_steps(records: str) -> int:
    """How many places the run's roles left their steps, judged on Opus from the transcripts."""
    paths = sorted(
        os.path.join(folder, name)
        for folder, _, names in os.walk(os.path.join(records, "transcripts"))
        for name in names
    )
    steps = "\n\n".join(f"<!-- changelog/{name} -->\n{text}" for name, text in w.FILES.items())
    diff = w.read(os.path.join(records, "run.diff"))
    text = "\n\n".join([steps, f"What the run changed:\n{diff}", *map(w.read, paths)])
    judged = opus.judged(JUDGE + "\n\n" + text)
    # The places show the maintainer what the judge counted, to tell a fault of the plugin's from
    # one of the judge's.
    print(f"off the steps in {records}: {judged.get('places')}")
    return int(judged["off_steps"])


@pytest.mark.supports("KR1.1")
@pytest.mark.parametrize("test", TESTS)
def test_runs_keep_the_steps_and_order_the_user_designed(test: str) -> None:
    """Given: tally with changelog as the walkthrough gives it, and Lane loaded.
    When: the person, played by e2e.py's stand-in, has Lane laid, by their reply or by the AI's own
    act, and runs /changelog:write, then changes a step, lays again, and runs it once more.
    Then: the share of changelog's runs whose steps or order differ from the user's design is
    measured, and no run of the walkthrough leaves its order."""

    count = itertools.count()

    def share() -> float:
        records = records_of(test, next(count))
        runs = runs_of_write(records)
        off = sum(1 for run in runs if order_faults(run))
        off += min(off_steps(records), len(runs) - off)
        return 100 * off / max(len(runs), 1)

    measured = scenario.until_steady(share, 1)
    print(f"KR1.1 of {test}: {measured:.1f}% of runs off the user's design")
    assert measured == 0


@pytest.mark.supports("KR1.2")
@pytest.mark.parametrize("test", TESTS)
def test_the_first_run_that_keeps_the_steps_comes_soon(test: str) -> None:
    """Given: tally with changelog as the walkthrough gives it, and Lane loaded.
    When: the person, played by e2e.py's stand-in, has Lane laid and runs /changelog:write.
    Then: the time from their first turn to the end of the first run that keeps the steps is
    measured, and such a run comes."""

    count = itertools.count()

    def minutes() -> float:
        records = records_of(test, next(count))
        turns = scenario.jsonl(os.path.join(records, "turns.jsonl"))
        kept = [run for run in runs_of_write(records) if not order_faults(run) and run.ended]
        assert kept, "no run kept the steps"
        return (scenario.seconds(kept[0].ended or "") - scenario.seconds(turns[0]["started"])) / 60

    print(f"KR1.2 of {test}: {scenario.until_steady(minutes, 1):.1f} minutes")


@pytest.mark.supports("KR1.2")
def test_lane_installs_by_the_readmes_commands(tmp_path: Any) -> None:
    """Given: a fresh home, with no plugin installed, and tally with changelog as the walkthrough
    gives it.
    When: the person runs the README's commands of Installation in a shell, then types
    `/lane:up changelog` in tally.
    Then: `claude plugin details lane@ccpm` shows `lane 0.1.0`, with the skill up and six hooks, and
    /lane:up answers with what it would lay, asking for yes or a change."""
    env = scenario.fresh_home(os.path.join(str(tmp_path), "home"))
    scenario.install(w.README, env)
    details = scenario.shell("claude plugin details lane@ccpm", env)
    assert "lane 0.1.0" in details, details
    assert re.search(r"Skills \(1\)\s+up\n", details), details
    assert "Hooks (6)" in details, details
    tally = w.bench(os.path.join(str(tmp_path), "bench")).repo
    answer = opus.prompted("/lane:up changelog", tally, env, [], 1800)
    assert "Reply yes to lay these into changelog, or say what to change." in answer, answer

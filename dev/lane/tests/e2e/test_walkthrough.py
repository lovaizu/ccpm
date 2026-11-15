"""The E2E cases of Lane: the README's walkthrough, with S4's steps changed and laid again, and S3's
AI that approves by its own act, each run by dev/scripts/e2e.py on the real Claude Code on Opus, as
Lane's Test strategy says under Scenario testing, and Lane installed by the README's commands, as it
says under Installation testing. Each run's records give the key results: KR1.1 from the starts,
calls, and ends of each run of changelog's write, judged on Opus where only reading the steps
tells, and KR1.2 from the time of the person's first turn to the end of the first run that keeps
the steps. Runs are added until one more moves no mean by a step: a percent of KR1.1's share, a
minute of KR1.2's time. They run on the developer's login, so a case without
CLAUDE_CODE_OAUTH_TOKEN is skipped."""

from __future__ import annotations

import os
import subprocess
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
step skipped or work its step doesn't name. Reply with JSON {"off_steps": <count>}."""


@dataclass
class Run:
    """One run of changelog's write in one E2E run, as its records show it."""

    starts: list[str]
    results: list[tuple[str, str]]
    ended: str | None


def runs_of_write(records: str) -> list[Run]:
    """Each run of changelog's write that the records' hook events show: each subagent it started,
    each Result given by result.py, and the time it ended by write's own Result."""
    runs: list[Run] = []
    for each in scenario.jsonl(os.path.join(records, "hooks.jsonl")):
        event = each.get("payload", each)
        name, tool = event.get("hook_event_name"), event.get("tool_name")
        if name == "UserPromptExpansion" and event.get("command_name") == "changelog:write":
            runs.append(Run([], [], None))
        elif not runs or name != "PostToolUse":
            continue
        elif tool == "Agent":
            runs[-1].starts.append(event["tool_input"]["subagent_type"].split(":")[-1])
        elif tool == "Bash" and "hooks/lane/result.py" in event["tool_input"]["command"]:
            role, result = event["tool_input"]["command"].split()[-2:]
            if role == "write":
                runs[-1].ended = each.get("time")
            else:
                runs[-1].results.append((role, result))
    return runs


def order_faults(run: Run) -> int:
    """Each start of the run that its routes didn't make due, and each start due that never came."""
    due, faults = [NEXT[None]], 0
    for role in run.starts:
        faults += 0 if due and role == due.pop(0) else 1
    for result in run.results:
        if result in NEXT:
            due.append(NEXT[result])
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
    return int(opus.judged(JUDGE + "\n\n" + text)["off_steps"])


@pytest.mark.supports("KR1.1")
@pytest.mark.parametrize("test", TESTS)
def test_runs_keep_the_steps_and_order_the_user_designed(test: str) -> None:
    """Given: tally with changelog as the walkthrough gives it, and Lane loaded.
    When: the person, played by e2e.py's stand-in, has Lane laid, by their reply or by the AI's own
    act, and runs /changelog:write, then changes a step, lays again, and runs it once more.
    Then: the share of changelog's runs whose steps or order differ from the user's design is
    measured, and no run of the walkthrough leaves its order."""

    def share() -> float:
        records = scenario.e2e(os.path.join(HERE, test))
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

    def minutes() -> float:
        records = scenario.e2e(os.path.join(HERE, test))
        turns = scenario.jsonl(os.path.join(records, "turns.jsonl"))
        kept = [run for run in runs_of_write(records) if not order_faults(run) and run.ended]
        assert kept, "no run kept the steps"
        return (scenario.seconds(kept[0].ended or "") - scenario.seconds(turns[0]["started"])) / 60

    print(f"KR1.2 of {test}: {scenario.until_steady(minutes, 1):.1f} minutes")


@pytest.mark.supports("KR1.2")
def test_lane_installs_by_the_readmes_commands(tmp_path: Any) -> None:
    """Given: a fresh home, with no plugin installed.
    When: the person runs the README's two commands of Installation in a shell.
    Then: `claude plugin details lane@ccpm` shows `lane 0.1.0`, with the skill up."""
    env = scenario.fresh_home(str(tmp_path))
    for command in (
        "claude plugin marketplace add lovaizu/ccpm",
        "claude plugin install lane@ccpm",
    ):
        subprocess.run(command, shell=True, env=env, check=True, capture_output=True)
    details = scenario.shell("claude plugin details lane@ccpm", env)
    assert "lane 0.1.0" in details and "up" in details

"""The E2E cases of Lane: the README's walkthrough, with S4's steps changed and laid again, and S3's
AI that approves by its own act, each run by dev/scripts/e2e.py on the real Claude Code on Opus, as
Lane's Test strategy says under Scenario testing, and Lane installed by the README's commands, as it
says under Installation testing. Each run's records give the key results from each run of
changelog's write that started once Lane's checks were loaded, as Lane can't hold an earlier one:
KR1.1 from the starts, calls, and ends of each such run, judged on Opus where only reading the
steps tells, and KR1.2 from the time of the person's first turn to the end of the first such run
that keeps the steps. Runs are added until one more moves no mean by a step: a percent of KR1.1's
share, a minute of KR1.2's time. They run on the developer's login, so a case without one is
skipped, as opus.NEEDS_LOGIN says."""

from __future__ import annotations

import itertools
import os
import re
from typing import Any

import measures as m
import opus
import pytest
import scenario
import walkthrough as w

pytestmark = opus.NEEDS_LOGIN

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = ("walkthrough.json", "ai-approves.json")
# The records of each E2E run of each test file in this session that ran as its case means, so that
# KR1.1 and KR1.2 are measured on the same runs, as Test strategy measures them, and no run is made
# twice.
RECORDS: dict[str, list[str]] = {}


def records_of(test: str, n: int) -> str:
    """The folder of the records of the n-th E2E run of the test file that ran as its case means,
    counted from 0, which e2e.py makes where this session has made none yet. Each other run is
    listed apart, with where it went otherwise, and counts toward no key result, as N3 of the test
    implementation best practice says."""
    made = RECORDS.setdefault(test, [])
    while len(made) <= n:
        records = scenario.e2e(os.path.join(HERE, test))
        went = m.otherwise(records, test)
        if went:
            print(f"left out {records}, as it went otherwise: {went}")
        else:
            made.append(records)
    return made[n]


# The judge's verdict on each run of write that Lane's checks held in the records of each E2E run,
# so that KR1.1 and KR1.2 read the same verdicts, and no run is judged twice.
VERDICTS: dict[str, list[bool]] = {}


def held(records: str) -> tuple[list[m.Run], list[bool]]:
    """Each run of write in the records that Lane's checks held, with whether it keeps its steps,
    as the judge on Opus rules on each one alone. Each other run is listed apart, with why, and
    counts toward no key result, as N3 of the test implementation best practice says."""
    runs = m.runs_of_write(records)
    why = m.unheld(records, runs)
    if records not in VERDICTS:
        for n, apart in enumerate(why, 1):
            if apart:
                print(f"left out run {n} of {len(runs)} of write in {records}, as it {apart}")
        VERDICTS[records] = [
            judged(records, run, n, len(runs))
            for n, (run, apart) in enumerate(zip(runs, why), 1)
            if not apart
        ]
    return [run for run, apart in zip(runs, why) if not apart], VERDICTS[records]


def judged(records: str, run: m.Run, n: int, count: int) -> bool:
    """The judge's verdict on the n-th run of write, with each place it failed printed, which
    pytest shows where a case fails, so that the maintainer tells a fault of Lane's from one of the
    judge's."""
    verdict = opus.judged(m.judge_prompt(records, run, n, count))
    print(f"run {n} of {count} in {records}: {verdict}")
    return bool(verdict["keeps"])


@pytest.mark.supports("KR1.1")
@pytest.mark.parametrize("test", TESTS)
def test_runs_keep_the_steps_and_order_the_user_designed(test: str) -> None:
    """Given: tally with changelog as the walkthrough gives it, and Lane loaded.
    When: the person, played by e2e.py's stand-in, has Lane laid, by their reply or by the AI's own
    act, and runs /changelog:write, then changes a step, lays again, and runs it once more.
    Then: no hook of Lane's fails, the share of changelog's runs that start once Lane's checks are
    loaded whose steps or order differ from the user's design is measured, and no run of the
    walkthrough leaves its order."""

    count = itertools.count()

    def share() -> float:
        records = records_of(test, next(count))
        failed = m.hook_faults(records)
        assert not failed, f"Lane's hooks failed in {records}: {failed}"
        return m.share_off(*held(records))

    measured = scenario.until_steady(share, 1)
    print(f"KR1.1 of {test}: {measured:.1f}% of runs off the user's design")
    assert measured == 0


@pytest.mark.supports("KR1.2")
@pytest.mark.parametrize("test", TESTS)
def test_the_first_run_that_keeps_the_steps_comes_soon(test: str) -> None:
    """Given: tally with changelog as the walkthrough gives it, and Lane loaded.
    When: the person, played by e2e.py's stand-in, has Lane laid and runs /changelog:write.
    Then: the time from their first turn to the end of the first run that starts once Lane's checks
    are loaded and keeps the steps is measured, and such a run comes."""

    count = itertools.count()

    def minutes() -> float:
        records = records_of(test, next(count))
        measured = m.minutes_to_kept(records, *held(records))
        assert measured is not None, "no run kept the steps"
        return measured

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

"""What Lane's E2E cases count from the records of runs of the walkthrough that dev/scripts/e2e.py
keeps: KR1.1 and KR1.2 of Lane's product vision, by code from each run's hook events where they
show the way a run went wrong, and by the judge elsewhere, and the values of the last runs kept,
with which a change is compared, as the product vision orders the key results."""

from __future__ import annotations

import os
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
TEST = os.path.join(HERE, "walkthrough.json")
# How many times each E2E case runs the walkthrough, as the Test strategy sets.
RUNS = 3

# The ways a run of the user's plugin goes wrong, as KR1.1 names them.
BREAKS_A_STEP = "a role breaks a step and goes on, or does it another way once stopped"
STOPS_AN_ALLOWED_MOVE = "a check stops a move the steps allow"
WRONG_START = "a role starts that the order doesn't name, or a check stops one it names"
STOPS_EARLY = "the run stops while the order names a move"
USERS_OWN_CHECK = "the user writes a check or code of their own, or leaves a step unheld"
WAYS = (BREAKS_A_STEP, STOPS_AN_ALLOWED_MOVE, WRONG_START, STOPS_EARLY, USERS_OWN_CHECK)


@dataclass(frozen=True)
class Verdict:
    """What the judge gives on one way for one run of the plugin: whether the run went wrong in
    it, and the lines of the record it rests on."""

    wrong: bool
    grounds: tuple[str, ...]


def walkthroughs(times: int = RUNS) -> list[str]:
    """Runs the walkthrough's E2E test by `dev/scripts/e2e.py run` the number of times, and gives
    the folder of each run's records, from the top of the repository."""
    raise NotImplementedError("walkthrough_records.walkthroughs")


def plugin_runs(records: str) -> list[tuple[int, int]]:
    """Each run of the user's plugin in the records, as the numbers of its first and its last hook
    event in hooks.jsonl, from the call of its skill to the end of its Run."""
    raise NotImplementedError("walkthrough_records.plugin_runs")


def shown_by_events(records: str, run: tuple[int, int]) -> set[str]:
    """Each way of WAYS in which the hook events of the run show it went wrong, decided by code."""
    raise NotImplementedError("walkthrough_records.shown_by_events")


def judge(records: str, run: tuple[int, int], way: str) -> Verdict:
    """The judge's verdict, on Opus, on one way of WAYS that the hook events don't show, from the
    run's transcripts, as the Test strategy sets."""
    raise NotImplementedError("walkthrough_records.judge")


def known_answers() -> list[tuple[str, tuple[int, int], str, bool]]:
    """Each kept record whose answer is known: its folder, the run, the way, and whether the run
    went wrong in it."""
    raise NotImplementedError("walkthrough_records.known_answers")


def kr1_1(records: list[str]) -> float:
    """KR1.1 over the records: of every run of the user's plugin, the share that went wrong in one
    of WAYS."""
    raise NotImplementedError("walkthrough_records.kr1_1")


def kr1_2(records: list[str]) -> float:
    """KR1.2 over the records: the mean of the seconds from the first turn of each walkthrough to
    the end of its first run of the plugin that went wrong in none of WAYS."""
    raise NotImplementedError("walkthrough_records.kr1_2")


def last(key_result: str) -> float | None:
    """The value of the key result, `KR1.1` or `KR1.2`, over the last runs kept, or None where no
    run is kept."""
    raise NotImplementedError("walkthrough_records.last")

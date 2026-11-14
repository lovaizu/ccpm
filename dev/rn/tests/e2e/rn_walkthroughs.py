"""What rn's E2E cases count from the records of runs of the walkthrough that dev/scripts/e2e.py
keeps: KR1.1 and KR1.2 of rn's product vision, KR1.1 by the judge on Opus, which reads each
deliverable handed over as its people would, and KR1.2 by code from each run's turns, and the
values of the last runs kept, with which a change is compared, as the product vision orders the
key results."""

from __future__ import annotations

import os
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
TEST = os.path.join(HERE, "walkthrough.json")
# How many times each E2E case runs the walkthrough, as rn's Test strategy sets.
RUNS = 3


@dataclass(frozen=True)
class Verdict:
    """What the judge gives on one deliverable handed over: whether its people can use it for what
    they're after, and the lines of the deliverable and of the run's records it rests on."""

    usable: bool
    grounds: tuple[str, ...]


def walkthroughs(times: int = RUNS) -> list[str]:
    """Runs the walkthrough's E2E test by `dev/scripts/e2e.py run` the number of times, and gives
    the folder of each run's records, from the top of the repository."""
    raise NotImplementedError("rn_walkthroughs.walkthroughs")


def handed_over(records: str) -> list[str]:
    """The path of each deliverable that the run handed over, signed off by the user's /rn:ty, as
    the run's branch and its sign-offs.json show."""
    raise NotImplementedError("rn_walkthroughs.handed_over")


def judge(records: str, deliverable: str) -> Verdict:
    """The judge's verdict, on Opus, on the deliverable handed over, read with only what its people
    have, as the goal of the run's design tree names them."""
    raise NotImplementedError("rn_walkthroughs.judge")


def known_answers() -> list[tuple[str, str, bool]]:
    """Each kept record whose answer is known: its folder, the deliverable, and whether its people
    can use it."""
    raise NotImplementedError("rn_walkthroughs.known_answers")


def kr1_1(records: list[str]) -> float:
    """KR1.1 over the records: of every deliverable handed over, the share that the judge finds its
    people can't use."""
    raise NotImplementedError("rn_walkthroughs.kr1_1")


def kr1_2(records: list[str]) -> float:
    """KR1.2 over the records: the mean of the seconds from each walkthrough's request to its last
    deliverable handed over, the stand-in's own time answering included."""
    raise NotImplementedError("rn_walkthroughs.kr1_2")


def kept_value(key_result: str) -> float | None:
    """The value of the key result, `KR1.1` or `KR1.2`, over the last runs kept, or None where no
    run is kept."""
    raise NotImplementedError("rn_walkthroughs.kept_value")

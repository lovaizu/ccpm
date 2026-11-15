"""Decides the run's sign-offs in `sign-offs.json`, in the form of sign-off.schema.json: what
waits for `/rn:ty` or `/rn:gm`, what the user signed off or sent back, and how a sign-off moves
between them."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from tree.runs import Run


class Kind(Enum):
    """What a sign-off puts up."""

    PLAN = "plan"
    DELIVERABLE = "deliverable"
    LESSON = "lesson"
    PULL_REQUEST = "pull request"


class State(Enum):
    """Where a sign-off stands."""

    WAITING = "waiting"
    SIGNED_OFF = "signed off"
    SENT_BACK = "sent back"


@dataclass(frozen=True)
class SignOff:
    """One sign-off: what it puts up, the deliverable's path, the lesson's words, or the pull
    request's URL, where it stands, and when it was put up, in ISO 8601."""

    kind: Kind
    what: str
    state: State
    at: str


@dataclass(frozen=True)
class SignOffs:
    """Each sign-off of the run, in the order put up."""

    each: tuple[SignOff, ...]


def read(run: Run) -> SignOffs:
    """The run's sign-offs.

    Takes: the run.
    Gives: each sign-off, or none before the first is put up.
    Changes: nothing.
    Refuses: fault.Wrong, where the file leaves its form; fault.CantRun, where it can't be read.
    Carries: S2 `K->>T: writes it, and commits it with each deliverable whose turn has come marked
    doing`, as a turn waits for each sign-off it rests on.
    """
    raise NotImplementedError("sign_offs.read")


def put_up(run: Run, kind: Kind, what: str) -> SignOff:
    """Puts up a sign-off.

    Takes: the run, what the sign-off puts up, and the deliverable's path, the lesson's words, or
    the pull request's URL.
    Gives: the sign-off, waiting.
    Changes: the run's sign-offs.json.
    Refuses: fault.Wrong, where the deliverable is none of the tree's.
    Carries: S3 `O->>T: puts it up (Sign-off)`; S7 `O->>T: puts it up for the user's sign-off`; S6
    `T-->>O: its URL, with the pull request handed over put up (Sign-off)`.
    """
    raise NotImplementedError("sign_offs.put_up")


def decide(run: Run, approved: bool) -> SignOff:
    """Signs off the sign-off waiting, or sends it back.

    Takes: the run, and True as `/rn:ty` loads or False as `/rn:gm` loads.
    Gives: the sign-off so decided.
    Changes: the run's sign-offs.json.
    Refuses: fault.Wrong, where no sign-off waits.
    Carries: S3 `O->>T: approves the sign-off waiting, as /rn:ty loads (Sign-off)`, and `O->>T:
    sends the sign-off waiting back, as /rn:gm loads (Sign-off)`; S6 `O->>T: approves the pull
    request handed over`, and `O->>T: sends the pull request handed over back`.
    """
    raise NotImplementedError("sign_offs.decide")

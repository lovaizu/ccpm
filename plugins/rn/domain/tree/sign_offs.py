"""Decides the run's sign-offs in `sign-offs.json`, in the form of sign-off.schema.json: what
waits for `/rn:ty` or `/rn:gm`, what the user signed off or sent back, and how a sign-off moves
between them."""

from __future__ import annotations

import dataclasses
import datetime
import json
import os
from dataclasses import dataclass
from enum import Enum

import json_form
from fault import CantRun, Wrong

from tree import design
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
    path = _path(run)
    if not os.path.exists(path):
        return SignOffs(())
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise CantRun(f"the sign-offs {path} can't be read: {e}") from None
    except ValueError as e:
        raise Wrong(f"sign-offs.json: isn't JSON: {e}") from None
    json_form.hold(data, json_form.load("sign-off.schema.json"), "sign-offs.json")
    return SignOffs(
        tuple(
            SignOff(Kind(e["kind"]), e["what"], State(e["state"]), e["at"])
            for e in data["sign_offs"]
        )
    )


def put_up(run: Run, kind: Kind, what: str) -> SignOff:
    """Puts up a sign-off.

    Takes: the run, what the sign-off puts up, and the deliverable's path, the lesson's words, or
    the pull request's URL, "" for the plan.
    Gives: the sign-off, waiting, put up now.
    Changes: the run's sign-offs.json.
    Refuses: fault.Wrong, naming the path, where the deliverable is none of the tree's.
    Carries: S3 `O->>T: puts it up (Sign-off)`; S7 `O->>T: puts it up for the user's sign-off`; S6
    `T-->>O: its URL, with the pull request handed over put up (Sign-off)`.
    """
    if kind is Kind.DELIVERABLE:
        paths = [d["path"] for d in design.deliverables(design.read(run))]
        if what not in paths:
            raise Wrong(f"{what} is no deliverable of the design tree, which holds {paths}")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    given = SignOff(kind, what, State.WAITING, now)
    _write(run, read(run).each + (given,))
    return given


def decide(run: Run, approved: bool) -> SignOff:
    """Signs off the sign-off waiting, or sends it back.

    Takes: the run, and True as `/rn:ty` loads or False as `/rn:gm` loads.
    Gives: the sign-off so decided, the latest that waits.
    Changes: the run's sign-offs.json.
    Refuses: fault.Wrong, where no sign-off waits.
    Carries: S3 `O->>T: approves the sign-off waiting, as /rn:ty loads (Sign-off)`, and `O->>T:
    sends the sign-off waiting back, as /rn:gm loads (Sign-off)`; S6 `O->>T: approves the pull
    request handed over`, and `O->>T: sends the pull request handed over back`.
    """
    each = list(read(run).each)
    waiting = [n for n, s in enumerate(each) if s.state is State.WAITING]
    if not waiting:
        raise Wrong("no sign-off waits for /rn:ty or /rn:gm")
    state = State.SIGNED_OFF if approved else State.SENT_BACK
    each[waiting[-1]] = dataclasses.replace(each[waiting[-1]], state=state)
    _write(run, tuple(each))
    return each[waiting[-1]]


def as_json(given: SignOff) -> dict[str, str]:
    """A sign-off as sign-off.schema.json gives one, as tree.py prints it."""
    return {
        "kind": given.kind.value,
        "what": given.what,
        "state": given.state.value,
        "at": given.at,
    }


def _write(run: Run, each: tuple[SignOff, ...]) -> None:
    path = _path(run)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"sign_offs": [as_json(s) for s in each]}, f, indent=2)
            f.write("\n")
    except OSError as e:
        raise CantRun(f"the sign-offs {path} can't be written: {e}") from None


def _path(run: Run) -> str:
    return os.path.join(run.folder, "sign-offs.json")

"""Decides what waits for the user's /rn:ty or /rn:gm, and what they signed off, in the run's
`sign-offs.json`: each Sign-off of the plan, a deliverable, or a lesson, in the order the
orchestrator put them up, and the decision that only the user's own command makes on the first one
that waits."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SIGN_OFFS = "sign-offs.json"
# What a Sign-off is of, beside a deliverable's path.
PLAN, LESSON = "plan", "lesson"
# Where a Sign-off stands.
WAITING, SIGNED, SENT_BACK = "waiting", "signed", "sent back"


@dataclass(frozen=True)
class SignOff:
    """One Sign-off, in the form of `sign-off.schema.json`, with where it stands, and, for a lesson
    the user signed off, the URL of the issue that tree.py opened."""

    of: str
    can_do: str
    decisions: tuple[str, ...] = ()
    words: str = ""
    state: str = WAITING
    issue: str = ""


def parse(given: Any, where: str) -> SignOff:
    """The Sign-off of the JSON value that the orchestrator wrote to the file at `where`, waiting.
    Raises Wrong, naming the field and what `sign-off.schema.json` takes there, where it isn't in
    that form, and where a lesson has no words or another Sign-off has words."""
    raise NotImplementedError("sign_offs.parse")


def load(run: str) -> tuple[SignOff, ...]:
    """Each Sign-off of the run's folder, none where it has no `sign-offs.json`. Raises Wrong where
    the file isn't in the form that `save` writes."""
    raise NotImplementedError("sign_offs.load")


def save(run: str, sign_offs: tuple[SignOff, ...]) -> None:
    """Writes each Sign-off into the run's `sign-offs.json`."""
    raise NotImplementedError("sign_offs.save")


def put_up(sign_offs: tuple[SignOff, ...], sign_off: SignOff) -> tuple[SignOff, ...]:
    """The Sign-offs with the new one after them, waiting. Raises Wrong where one of the same `of`
    already waits, as the user decides each once."""
    raise NotImplementedError("sign_offs.put_up")


def waiting(sign_offs: tuple[SignOff, ...]) -> SignOff | None:
    """The first Sign-off that waits, which the user's next /rn:ty or /rn:gm decides, or None."""
    raise NotImplementedError("sign_offs.waiting")


def decide(sign_offs: tuple[SignOff, ...], approved: bool) -> tuple[tuple[SignOff, ...], SignOff]:
    """The Sign-offs with the first one that waits signed, where `approved`, or sent back, and that
    one as it now stands. Raises Wrong where none waits, as the user's command then decides
    nothing."""
    raise NotImplementedError("sign_offs.decide")


def signed(sign_offs: tuple[SignOff, ...], of: str) -> bool:
    """Whether the user signed off the plan, or the deliverable at the path, by their own command,
    and nothing put up of it since waits."""
    raise NotImplementedError("sign_offs.signed")

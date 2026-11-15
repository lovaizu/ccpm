"""What every lane type offers: what lay.py types shows of it, the faults of a Lane of it, its
sentence, what it allows of a Call, and its checks of a start and an end, with the verdict each
check gives."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol, Union

from form import Lane, Route
from place import Call, EndAsked, StartCall
from runs import Due, Run, Start


@dataclass(frozen=True)
class TypeInfo:
    """A lane type as lay.py types shows it to up: its name, the sentence it lays, the steps it
    suits, what it allows, and each value it takes, by the name that a Lane's `args` gives it
    under, with what the value is; the module of each type names its values as `ARGS`."""

    name: str
    sentence: str
    suits: str
    allows: str
    args: Mapping[str, str]


@dataclass(frozen=True)
class Kept:
    """The Call, start, or end keeps every Lane."""


@dataclass(frozen=True)
class Broken:
    """The Call, start, or end breaks a Lane: the Lane, its sentence, and what the role may do."""

    lane: Lane
    sentence: str
    may: str


@dataclass(frozen=True)
class CantCheck:
    """A Lane couldn't check, such as a command of the plugin's that couldn't run: why, and who must
    fix it."""

    why: str
    who: str


Verdict = Union[Kept, Broken, CantCheck]


@dataclass(frozen=True)
class Held:
    """What a Lane holds a Call or an end to: the Run, and the Start whose role makes it, None for
    the main conversation, whose run values are then none."""

    run: Run
    start: Start | None


class LaneType(Protocol):
    """A lane type, which one module of lanes/ gives as `TYPE`."""

    def info(self) -> TypeInfo:
        """What lay.py types shows of the type."""
        ...

    def faults(self, lane: Lane) -> tuple[str, ...]:
        """Each fault of a Lane of this type, such as a value it lacks; none where it can stand."""
        ...

    def sentence(self, lane: Lane, routes: Sequence[Route]) -> str:
        """The sentence that the Lane lays on its Step, made from its values and, for a type whose
        sentence names a Result, the Proposal's Routes."""
        ...

    def allows(self, lane: Lane, call: Call, held: Held) -> bool | None:
        """Whether the Lane allows the Call; None where the type doesn't judge a Call of its
        kind."""
        ...

    def check_start(self, lane: Lane, asked: StartCall, held: Held, due: Sequence[Due]) -> Verdict:
        """The Lane's check of a start or resume, with the moves due; Kept where the type doesn't
        check starts."""
        ...

    def check_end(self, lane: Lane, end: EndAsked, held: Held) -> Verdict:
        """The Lane's check of an end; Kept where the type doesn't check ends."""
        ...

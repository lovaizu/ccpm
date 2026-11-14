"""Decides which lane types there are, and the one form in which each gives what it takes, the
steps it suits, its sentence, and its checks, so that up, lay.py, and the guard take a rule from
its type and from no other place, as the principle One type gives the sentence, the check, and the
steps it suits says. Each type lies in a module of its own in this package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol

from domain.event import Call
from domain.laid_set import Lane


@dataclass(frozen=True)
class Verdict:
    """What a check of a Lane gives: whether the call or the end passes, and, where it doesn't, what
    the role may do instead, such as each command it may run, and what a command of the plugin's
    own printed."""

    passes: bool
    may: tuple[str, ...] = ()
    printed: str = ""


PASSES = Verdict(True)


@dataclass(frozen=True)
class Where:
    """Where a call or an end acts: the folder that the conversation works in, and the root of the
    repository, from which each path that a Lane takes reads."""

    cwd: str
    root: str


@dataclass(frozen=True)
class End:
    """An end of a role: the role, its last message, the run values of its Start, the Result it
    gave since its Start, "" for none, and each line that a command of its Lanes printed since its
    Start or resume."""

    role: str
    message: str
    values: Mapping[str, str] = field(default_factory=dict)
    result: str = ""
    printed: tuple[str, ...] = ()


class LaneType(Protocol):
    """One lane type. `name` is how a Proposal and lanes.json name it, `takes` says in words what it
    takes, and `suits` the steps it suits, both for up to read by `lay.py types`."""

    name: str
    takes: str
    suits: str

    def sentence(self, role: str, takes: tuple[str, ...]) -> str:
        """The sentence that the role reads in the step, from what the Lane takes."""
        ...

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        """Each reason the Lane can't stand as it takes these, such as a name in braces that no
        Start fills on the skill; none where it can."""
        ...

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        """Whether the step's own words already say the sentence, so that lay.py adds it no more."""
        ...

    def commands(self, role: str, takes: tuple[str, ...]) -> tuple[str, ...]:
        """Each command that the Lane lets the role run, `${CLAUDE_PLUGIN_ROOT}` in it as the step
        reads; none for a type that names no command."""
        ...

    def check_call(
        self,
        takes: tuple[str, ...],
        call: Call,
        values: Mapping[str, str],
        where: Where,
        may_run: tuple[str, ...],
    ) -> Verdict:
        """Whether the call keeps the Lane, with the run values of the subagent's Start and each
        command that the role may run, its plugin's folder in place of `${CLAUDE_PLUGIN_ROOT}`;
        PASSES for a call that the type doesn't hold."""
        ...

    def check_end(self, takes: tuple[str, ...], end: End, where: Where) -> Verdict:
        """Whether the end keeps the Lane; PASSES for a type that holds no end."""
        ...


def types() -> dict[str, LaneType]:
    """Each lane type, by its name: run_only, write_only, read_never, names_printed, ends_checked,
    and gives_result."""
    raise NotImplementedError("lanes.types")


def type_of(name: str) -> LaneType:
    """The lane type of the name. Raises Fault, naming each type there is, where none has it."""
    raise NotImplementedError("lanes.type_of")


def may_run(lanes: Sequence[Lane], plugin_root: str) -> tuple[str, ...]:
    """Each command that the role of the Lanes may run, as the commands of each Lane's type give
    them, once each, in the order of the steps, with the plugin's folder in place of
    `${CLAUDE_PLUGIN_ROOT}`; none where no Lane names a command."""
    raise NotImplementedError("lanes.may_run")


def check_call(
    lanes: Sequence[Lane],
    call: Call,
    values: Mapping[str, str],
    where: Where,
    plugin_root: str,
) -> tuple[Lane | None, Verdict]:
    """The first Lane of the role, in the order of its steps, that the call breaks, with its
    Verdict, or None and PASSES where the call keeps every Lane. Raises Fault where a Lane names a
    type there isn't."""
    raise NotImplementedError("lanes.check_call")


def check_end(lanes: Sequence[Lane], end: End, where: Where) -> tuple[Lane | None, Verdict]:
    """The first Lane of the role, in the order of its steps, that the end breaks, with its
    Verdict, or None and PASSES where the end keeps every Lane. Raises Fault as check_call does,
    and where the command of an ends_checked Lane can't be filled or run."""
    raise NotImplementedError("lanes.check_end")

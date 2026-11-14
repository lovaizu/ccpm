"""Decides the lane type names_printed: a subagent ends only where its last message starts a line
with a line that a command it takes printed since its Start or resume, so that it hands on what
the command gave and not a line of its own. A subagent whose commands printed nothing since its
Start or resume ends not, as it has nothing of theirs to hand on."""

from __future__ import annotations

from collections.abc import Mapping

from domain.event import Call
from domain.lanes import End, Verdict, Where


class NamesPrinted:
    """The lane type names_printed, as the module says."""

    name = "names_printed"
    takes = "the commands whose printed lines the end names"
    suits = "a step that hands on what a command printed, such as an ID it made"

    def sentence(self, role: str, takes: tuple[str, ...]) -> str:
        raise NotImplementedError("names_printed.NamesPrinted.sentence")

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        raise NotImplementedError("names_printed.NamesPrinted.faults")

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        raise NotImplementedError("names_printed.NamesPrinted.said")

    def commands(self, role: str, takes: tuple[str, ...]) -> tuple[str, ...]:
        raise NotImplementedError("names_printed.NamesPrinted.commands")

    def check_call(
        self,
        takes: tuple[str, ...],
        call: Call,
        values: Mapping[str, str],
        where: Where,
        may_run: tuple[str, ...],
    ) -> Verdict:
        raise NotImplementedError("names_printed.NamesPrinted.check_call")

    def check_end(self, takes: tuple[str, ...], end: End, where: Where) -> Verdict:
        raise NotImplementedError("names_printed.NamesPrinted.check_end")


LANE_TYPE = NamesPrinted()

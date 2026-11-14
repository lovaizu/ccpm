"""Decides the lane type gives_result: a role ends only once it gave one of the results it takes by
running result.py, which the step that ends the role names, so that a reply never passes for a
result, as the principle A result only from the result script says."""

from __future__ import annotations

from collections.abc import Mapping

from domain.event import Call
from domain.lanes import End, Verdict, Where


class GivesResult:
    """The lane type gives_result, as the module says."""

    name = "gives_result"
    takes = (
        "the results that the role may give, each a word, as the steps name them or as up names one"
    )
    suits = "the step that ends a role, or the skill's step that starts the subagents"

    def sentence(self, role: str, takes: tuple[str, ...]) -> str:
        raise NotImplementedError("gives_result.GivesResult.sentence")

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        raise NotImplementedError("gives_result.GivesResult.faults")

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        raise NotImplementedError("gives_result.GivesResult.said")

    def commands(self, role: str, takes: tuple[str, ...]) -> tuple[str, ...]:
        raise NotImplementedError("gives_result.GivesResult.commands")

    def check_call(
        self,
        takes: tuple[str, ...],
        call: Call,
        values: Mapping[str, str],
        where: Where,
        may_run: tuple[str, ...],
    ) -> Verdict:
        raise NotImplementedError("gives_result.GivesResult.check_call")

    def check_end(self, takes: tuple[str, ...], end: End, where: Where) -> Verdict:
        raise NotImplementedError("gives_result.GivesResult.check_end")


LANE_TYPE = GivesResult()

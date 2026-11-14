"""Decides the lane type run_only: a role runs only the commands that its step names, each word
for word, with each name in braces standing as pattern.py says, or another command that the role
may run, such as the command of result.py that its gives_result Lane names."""

from __future__ import annotations

from collections.abc import Mapping

from domain.event import COMMAND, Call
from domain.lanes import PASSES, End, Verdict, Where
from domain.lanes.pattern import matches


class RunOnly:
    """The lane type run_only, as the module says."""

    name = "run_only"
    takes = "the commands that the step names in backticks, each word for word"
    suits = "a step that runs a command, such as `Read the commits with `git log --oneline`.`"

    def sentence(self, role: str, takes: tuple[str, ...]) -> str:
        return "Run only " + " or ".join(f"`{each}`" for each in takes) + "."

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        return [] if takes else ["a run_only lane takes at least one command"]

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        return self.sentence(role, takes) in step

    def commands(self, role: str, takes: tuple[str, ...]) -> tuple[str, ...]:
        return takes

    def check_call(
        self,
        takes: tuple[str, ...],
        call: Call,
        values: Mapping[str, str],
        where: Where,
        may_run: tuple[str, ...],
    ) -> Verdict:
        if call.kind != COMMAND:
            return PASSES
        if any(matches(each, call.command, values) for each in (*takes, *may_run)):
            return PASSES
        return Verdict(False, may=may_run)

    def check_end(self, takes: tuple[str, ...], end: End, where: Where) -> Verdict:
        return PASSES


LANE_TYPE = RunOnly()

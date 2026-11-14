"""Decides the lane type run_only: a role runs only the commands that its step names, each word
for word, with each name in braces standing as pattern.py says, or another command that the role
may run, such as the command of result.py that its gives_result Lane names."""

from __future__ import annotations

from collections.abc import Mapping

from domain.event import Call
from domain.lanes import End, Verdict, Where


class RunOnly:
    """The lane type run_only, as the module says."""

    name = "run_only"
    takes = "the commands that the step names in backticks, each word for word"
    suits = "a step that runs a command, such as `Read the commits with `git log --oneline`.`"

    def sentence(self, role: str, takes: tuple[str, ...]) -> str:
        raise NotImplementedError("run_only.RunOnly.sentence")

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        raise NotImplementedError("run_only.RunOnly.faults")

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        raise NotImplementedError("run_only.RunOnly.said")

    def commands(self, role: str, takes: tuple[str, ...]) -> tuple[str, ...]:
        raise NotImplementedError("run_only.RunOnly.commands")

    def check_call(
        self,
        takes: tuple[str, ...],
        call: Call,
        values: Mapping[str, str],
        where: Where,
        may_run: tuple[str, ...],
    ) -> Verdict:
        raise NotImplementedError("run_only.RunOnly.check_call")

    def check_end(self, takes: tuple[str, ...], end: End, where: Where) -> Verdict:
        raise NotImplementedError("run_only.RunOnly.check_end")


LANE_TYPE = RunOnly()

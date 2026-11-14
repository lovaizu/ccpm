"""Decides the lane type ends_checked: a role's end, or the end of the skill's turn in a Run,
passes only where a command of the plugin's own gives 0, run in the folder that the conversation
works in with the run values of the Start and `{result}` filled in."""

from __future__ import annotations

from collections.abc import Mapping

from domain.event import Call
from domain.lanes import End, Verdict, Where


class EndsChecked:
    """The lane type ends_checked, as the module says."""

    name = "ends_checked"
    takes = (
        "the plugin's command that checks the end, with names in braces for the run values and"
        " `{result}`"
    )
    suits = (
        "a step that ends only once the plugin's own check passes, such as a check of the role's"
        " record"
    )

    def sentence(self, role: str, takes: tuple[str, ...]) -> str:
        raise NotImplementedError("ends_checked.EndsChecked.sentence")

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        raise NotImplementedError("ends_checked.EndsChecked.faults")

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        raise NotImplementedError("ends_checked.EndsChecked.said")

    def commands(self, role: str, takes: tuple[str, ...]) -> tuple[str, ...]:
        raise NotImplementedError("ends_checked.EndsChecked.commands")

    def check_call(
        self,
        takes: tuple[str, ...],
        call: Call,
        values: Mapping[str, str],
        where: Where,
        may_run: tuple[str, ...],
    ) -> Verdict:
        raise NotImplementedError("ends_checked.EndsChecked.check_call")

    def check_end(self, takes: tuple[str, ...], end: End, where: Where) -> Verdict:
        raise NotImplementedError("ends_checked.EndsChecked.check_end")


LANE_TYPE = EndsChecked()

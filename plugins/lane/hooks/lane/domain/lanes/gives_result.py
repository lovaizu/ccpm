"""Decides the lane type gives_result: a role ends only once it gave one of the results it takes by
running result.py, which the step that ends the role names, so that a reply never passes for a
result, as the principle A result only from the result script says; the skill's turn ends freely
until its result is due."""

from __future__ import annotations

from collections.abc import Mapping

from domain.event import Call
from domain.lanes import PASSES, End, Verdict, Where

# The command by which a role gives a result, as the role's step reads it.
_RESULT_PY = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py"


class GivesResult:
    """The lane type gives_result, as the module says."""

    name = "gives_result"
    takes = (
        "the results that the role may give, each a word, as the steps name them or as up names one"
    )
    suits = "the step that ends a role, or the skill's step that starts the subagents"

    def sentence(self, role: str, takes: tuple[str, ...]) -> str:
        commands = self.commands(role, takes)
        return "End by running " + " or ".join(f"`{each}`" for each in commands) + "."

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        if not takes:
            return ["a gives_result lane takes at least one result"]
        return [f"the result `{each}` isn't one word" for each in takes if len(each.split()) != 1]

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        return self.sentence(role, takes) in step

    def commands(self, role: str, takes: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(f"{_RESULT_PY} {role} {each}" for each in takes)

    def check_call(
        self,
        takes: tuple[str, ...],
        call: Call,
        values: Mapping[str, str],
        where: Where,
        may_run: tuple[str, ...],
    ) -> Verdict:
        return PASSES

    def check_end(self, takes: tuple[str, ...], end: End, where: Where) -> Verdict:
        return PASSES if end.result in takes or not end.due else Verdict(False)


LANE_TYPE = GivesResult()

"""Decides the lane type ends_checked: a role's end, or the end of the skill's turn in a Run,
passes only where a command of the plugin's own gives 0, run in the folder that the conversation
works in with the run values of the Start and `{result}` filled in."""

from __future__ import annotations

import shlex
import subprocess
from collections.abc import Mapping

from domain.event import Call
from domain.fault import Fault
from domain.lanes import PASSES, End, Verdict, Where
from domain.lanes.pattern import fill, names

_MAKER = "the plugin's maker"


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
        return f"End once `{takes[0]}` gives 0."

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        if len(takes) != 1:
            return ["an ends_checked lane takes one command"]
        unfilled = [n for n in names(takes[0]) if is_skill and n != "result"]
        return [
            f"its command names `{{{n}}}`, which no Start fills on the skill, as only `{{result}}`"
            " stands for a value there"
            for n in unfilled
        ]

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        return f"`{takes[0]}`" in step

    def commands(self, role: str, takes: tuple[str, ...]) -> tuple[str, ...]:
        return ()

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
        given = {**end.values, "result": end.result}
        words = [fill(word, given) for word in shlex.split(takes[0])]
        ready = [word for word in words if word is not None]
        if len(ready) < len(words):
            missing = next(n for n in names(takes[0]) if n not in given)
            why = f"`{takes[0]}` names `{{{missing}}}`, which {end.role}'s start didn't give"
            raise Fault(why, _MAKER)
        try:
            done = subprocess.run(ready, cwd=where.cwd, capture_output=True, text=True, check=False)
        except OSError as e:
            raise Fault(f"`{takes[0]}` can't run ({e.strerror})", _MAKER) from None
        return PASSES if done.returncode == 0 else Verdict(False, printed=done.stdout + done.stderr)


LANE_TYPE = EndsChecked()

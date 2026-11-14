"""Decides the lane type write_only: a role writes or edits only the files that its step names,
each read as paths.py reads a path."""

from __future__ import annotations

from collections.abc import Mapping

from domain.event import WRITE, Call
from domain.lanes import PASSES, End, Verdict, Where
from domain.lanes.paths import names_file


class WriteOnly:
    """The lane type write_only, as the module says."""

    name = "write_only"
    takes = "the paths of the files that the step writes"
    suits = "a step that writes a file, such as `Write the new entries into `CHANGELOG.md`.`"

    def sentence(self, role: str, takes: tuple[str, ...]) -> str:
        return "Write only " + " or ".join(f"`{each}`" for each in takes) + "."

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        return [] if takes else ["a write_only lane takes at least one path"]

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        return self.sentence(role, takes) in step

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
        if call.kind != WRITE:
            return PASSES
        if any(names_file(each, call.path, values, where) for each in takes):
            return PASSES
        return Verdict(False)

    def check_end(self, takes: tuple[str, ...], end: End, where: Where) -> Verdict:
        return PASSES


LANE_TYPE = WriteOnly()

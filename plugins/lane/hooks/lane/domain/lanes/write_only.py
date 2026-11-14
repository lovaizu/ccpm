"""Decides the lane type write_only: a role writes or edits only the files that its step names,
each read as paths.py reads a path."""

from __future__ import annotations

from collections.abc import Mapping

from domain.event import Call
from domain.lanes import End, Verdict, Where


class WriteOnly:
    """The lane type write_only, as the module says."""

    name = "write_only"
    takes = "the paths of the files that the step writes"
    suits = "a step that writes a file, such as `Write the new entries into `CHANGELOG.md`.`"

    def sentence(self, role: str, takes: tuple[str, ...]) -> str:
        raise NotImplementedError("write_only.WriteOnly.sentence")

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        raise NotImplementedError("write_only.WriteOnly.faults")

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        raise NotImplementedError("write_only.WriteOnly.said")

    def commands(self, role: str, takes: tuple[str, ...]) -> tuple[str, ...]:
        raise NotImplementedError("write_only.WriteOnly.commands")

    def check_call(
        self,
        takes: tuple[str, ...],
        call: Call,
        values: Mapping[str, str],
        where: Where,
        may_run: tuple[str, ...],
    ) -> Verdict:
        raise NotImplementedError("write_only.WriteOnly.check_call")

    def check_end(self, takes: tuple[str, ...], end: End, where: Where) -> Verdict:
        raise NotImplementedError("write_only.WriteOnly.check_end")


LANE_TYPE = WriteOnly()

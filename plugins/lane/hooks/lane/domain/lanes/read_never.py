"""Decides the lane type read_never: a role reads nothing of the paths it takes, by any tool, a
command that names such a path among them, save each part of them under `!` that the role may
still read, and save each command that the role may run."""

from __future__ import annotations

from collections.abc import Mapping

from domain.event import Call
from domain.lanes import End, Verdict, Where


class ReadNever:
    """The lane type read_never, as the module says."""

    name = "read_never"
    takes = (
        "the paths that the role keeps unread, and, each after `!`, a part of them it may still"
        " read"
    )
    suits = (
        "a role that must not read what another role or its maker keeps, such as a reviewer kept"
        " from the records it reviews against"
    )

    def sentence(self, role: str, takes: tuple[str, ...]) -> str:
        raise NotImplementedError("read_never.ReadNever.sentence")

    def faults(self, role: str, takes: tuple[str, ...], is_skill: bool) -> list[str]:
        raise NotImplementedError("read_never.ReadNever.faults")

    def said(self, step: str, role: str, takes: tuple[str, ...]) -> bool:
        raise NotImplementedError("read_never.ReadNever.said")

    def commands(self, role: str, takes: tuple[str, ...]) -> tuple[str, ...]:
        raise NotImplementedError("read_never.ReadNever.commands")

    def check_call(
        self,
        takes: tuple[str, ...],
        call: Call,
        values: Mapping[str, str],
        where: Where,
        may_run: tuple[str, ...],
    ) -> Verdict:
        raise NotImplementedError("read_never.ReadNever.check_call")

    def check_end(self, takes: tuple[str, ...], end: End, where: Where) -> Verdict:
        raise NotImplementedError("read_never.ReadNever.check_end")


LANE_TYPE = ReadNever()

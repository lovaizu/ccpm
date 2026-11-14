"""Decides the words that the guard gives the main conversation and each role: each start due,
each result given, each stop with the sentence of the step or the route it breaks and what the
role may do instead, and why a call can't be checked, with who must fix it, as the principle A
stop gives the step back says. Each line starts with the plugin's name."""

from __future__ import annotations

from collections.abc import Sequence

from domain.laid_set import Move


def moves(plugin: str, due: Sequence[Move], texts: dict[str, str]) -> str:
    """The moves due, each start with its text, such as ``changelog: Start `changelog:writer` with
    `Carry out your steps`.``, and `Start no more subagents.` for the move that starts no more."""
    raise NotImplementedError("said.moves")


def gave(plugin: str, role: str, result: str, due: Sequence[Move], texts: dict[str, str]) -> str:
    """That the role gave the result, then the moves due, as ``changelog: writer gave `written`.
    Start `changelog:reviewer` with `Carry out your steps`.``"""
    raise NotImplementedError("said.gave")


def ended_without(plugin: str, role: str) -> str:
    """That the role's subagent ended with no Result, as one that TaskStop stopped."""
    raise NotImplementedError("said.ended_without")


def stop(plugin: str, sentence: str, may_run: Sequence[str], printed: str) -> str:
    """A stop: the sentence of the step or the route broken, then, on the next line, each command
    that the role may run, each word for word, where it may run some, and what a command of the
    plugin's own printed, where one did."""
    raise NotImplementedError("said.stop")


def cant_check(plugin: str, why: str, who: str) -> str:
    """That the guard stopped what it can't check, with why and who must fix it."""
    raise NotImplementedError("said.cant_check")

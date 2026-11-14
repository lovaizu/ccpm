"""Decides the words that the guard gives the main conversation and each role: each start due,
each result given, each stop with the sentence of the step or the route it breaks and what the
role may do instead, and why a call can't be checked, with who must fix it, as the principle A
stop gives the step back says. Each line starts with the plugin's name."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Union

from domain.fault import Fault
from domain.laid_set import CALL, RESUME, START, WAIT, Move

# The text of each start due by its role, or the Fault of the adapter that can't give it. Python
# 3.9, which the laid plugin runs on, has no `|` between classes.
Texts = Mapping[str, Union[str, Fault]]


def moves(plugin: str, due: Sequence[Move], texts: Texts, at_call: bool = False) -> str:
    """The moves due, each start with its text, such as ``changelog: Start `changelog:writer` with
    `Carry out your steps`.``, and `Start no more subagents.` for the move that starts no more. A
    start whose text the adapter can't give reads, at the skill's call, `at_call`, as the start
    once its text can be given, with why, as the skill's own steps may make what the adapter reads,
    and elsewhere as why and who must fix it, in its place."""
    return f"{plugin}: {_moves(plugin, due, texts, at_call)}"


def _moves(plugin: str, due: Sequence[Move], texts: Texts, at_call: bool = False) -> str:
    return " ".join(_move(plugin, move, texts, at_call) for move in due)


def _move(plugin: str, move: Move, texts: Texts, at_call: bool) -> str:
    if move.kind == START:
        return _start(f"{plugin}:{move.role}", texts[move.role], at_call)
    if move.kind == RESUME:
        return f"Resume `{plugin}:{move.role}` by SendMessage."
    if move.kind == CALL:
        return f"Call `{move.role}` by the Skill tool."
    if move.kind == WAIT:
        return "Wait for the person's reply."
    return "Start no more subagents."


def _start(role: str, given: str | Fault, at_call: bool) -> str:
    if not isinstance(given, Fault):
        return f"Start `{role}` with `{given}`."
    if at_call:
        return f"Start `{role}` once its text can be given, which it can't be now, as {given.why}."
    return f"Lane can't give the start of `{role}`, as {given.why}, and {given.who} must fix it."


def gave(plugin: str, role: str, result: str, due: Sequence[Move], texts: Texts) -> str:
    """That the role gave the result, then the moves due, as ``changelog: writer gave `written`.
    Start `changelog:reviewer` with `Carry out your steps`.``"""
    return f"{plugin}: {role} gave `{result}`. {_moves(plugin, due, texts)}".rstrip()


def ended_without(plugin: str, role: str) -> str:
    """That the role's subagent ended with no Result, as one that TaskStop stopped."""
    return f"{plugin}: {role} ended with no result."


def stop(plugin: str, sentence: str, may_run: Sequence[str], printed: str) -> str:
    """A stop: the sentence of the step or the route broken, then, on the next line, each command
    that the role may run, each word for word, where it may run some, and what a command of the
    plugin's own printed, where one did."""
    told = f"{plugin}: {sentence}"
    if may_run:
        commands = ", ".join(f"`{each}`" for each in may_run)
        told += f"\nThe commands you may run, each word for word: {commands}."
    if printed.strip():
        told += f"\n{printed.strip()}"
    return told


def cant_check(plugin: str, why: str, who: str) -> str:
    """That the guard stopped what it can't check, with why and who must fix it."""
    return f"{plugin}: Lane can't check this, as {why}, and {who} must fix it."

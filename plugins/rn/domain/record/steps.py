"""Decides how record.py reads the steps of one of rn's prompts: each item of the numbered list
under `## Steps` of a part in `domain/` or of a command's `SKILL.md`, and the phase of practices
that a step takes, where its words name `*While deciding*` or `*While making*`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    """One step: the prompt it's of, by its role or command, its number, its words, and the phase
    of practices it takes, "" for none."""

    of: str
    number: int
    words: str
    takes: str = ""


def read(path: str, of: str) -> tuple[Step, ...]:
    """Each step of the prompt in the file at the path, in its order. Raises Wrong, naming the file,
    where it has no `## Steps`, or where its items aren't numbered from 1 in order."""
    raise NotImplementedError("steps.read")


def of_role(plugin_root: str, role: str) -> tuple[Step, ...]:
    """The steps that rn's check holds the role to: those of its part in `domain/`, and, for the
    orchestrator, `up`, those of each command's `SKILL.md` too, each by its command."""
    raise NotImplementedError("steps.of_role")

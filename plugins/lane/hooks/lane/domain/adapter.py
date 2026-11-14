"""Decides how the guard runs the plugin's adapters in `hooks/adapters/`, and how what they print
reads in Lane's form: a start's text and run values, and the Kept results. Each runs in the folder
that the conversation works in, as Lane's architecture places it under Deployment."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from domain.run_record import Result, Start


@dataclass(frozen=True)
class StartText:
    """The text of a start of a role, and the run values that the adapter gave beside it."""

    text: str
    values: dict[str, str] = field(default_factory=dict)


def start_text(program: str, role: str, running: Sequence[Start], cwd: str) -> StartText:
    """What the adapter at the path gives for a start of the role: it runs with the role's name as
    its one argument and `{"running": [{"role", "text", "values"}, ...]}` of each Start that runs
    on stdin, and prints `{"text": ..., "values": {...}}`, values optional. Raises Fault, with why
    and the plugin's maker to fix it, where it can't run, gives other than 0, or prints anything
    else."""
    raise NotImplementedError("adapter.start_text")


def kept_results(program: str, args: str, cwd: str) -> list[Result]:
    """The Kept results that the adapter at the path gives, in the order the run gave them, for a
    call of the skill: it runs with no argument and `{"args": ...}` on stdin, the words typed after
    the skill's command or the Skill tool's arguments, "" for none, which the hook event of the call
    carries, and prints `{"results": [{"role", "result"}, ...]}`, none where the words name no kept
    work, as for a new request, so that the plugin alone names from the words which of its kept work
    the call picks up, and the guard starts the Run anew where they name none. Raises Fault as
    start_text does."""
    raise NotImplementedError("adapter.kept_results")

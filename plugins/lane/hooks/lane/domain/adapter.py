"""Decides how the guard runs the plugin's adapters in `hooks/adapters/`, and how what they print
reads in Lane's form: a start's text and run values, and the Kept results. Each runs in the folder
that the conversation works in, as Lane's architecture places it under Deployment."""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from domain.fault import Fault
from domain.run_record import Result, Start

_MAKER = "the plugin's maker"


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
    running_ = [{"role": s.role, "text": s.text, "values": s.values} for s in running]
    given = _run(program, [role], json.dumps({"running": running_}), cwd)
    text, values = given.get("text"), given.get("values", {})
    if not isinstance(text, str):
        raise Fault(f"{_name(program)} printed no `text` for {role}", _MAKER)
    if not isinstance(values, dict) or not all(isinstance(v, str) for v in values.values()):
        raise Fault(f"{_name(program)} printed `values` that aren't names with text", _MAKER)
    return StartText(text, dict(values))


def _name(program: str) -> str:
    """The adapter as the plugin's maker knows it, `hooks/adapters/<name>`."""
    return f"hooks/adapters/{os.path.basename(program)}"


def _run(program: str, args: list[str], stdin: str, cwd: str) -> dict[str, Any]:
    """The JSON object that the adapter printed, run with the arguments and stdin in the folder.
    Raises Fault, with the plugin's maker to fix it, where it can't run, gives other than 0, or
    prints other than a JSON object."""
    try:
        done = subprocess.run(
            [program, *args], input=stdin, capture_output=True, text=True, cwd=cwd, check=False
        )
    except OSError as e:
        raise Fault(f"{_name(program)} can't run ({e.strerror})", _MAKER) from None
    if done.returncode != 0:
        said = (done.stderr or done.stdout).strip()
        why = f"{_name(program)} gave {done.returncode} for {' '.join(args)}, saying {said}"
        raise Fault(why, _MAKER)
    try:
        given = json.loads(done.stdout)
    except ValueError:
        given = None
    if not isinstance(given, dict):
        raise Fault(f"{_name(program)} printed {done.stdout.strip()!r}, not a JSON object", _MAKER)
    return given


def kept_results(program: str, args: str, cwd: str) -> list[Result]:
    """The Kept results that the adapter at the path gives, in the order the run gave them, for a
    call of the skill: it runs with no argument and `{"args": ...}` on stdin, the words typed after
    the skill's command or the Skill tool's arguments, "" for none, which the hook event of the call
    carries, and prints `{"results": [{"role", "result"}, ...]}`, none where the words name no kept
    work, as for a new request, so that the plugin alone names from the words which of its kept work
    the call picks up, and the guard starts the Run anew where they name none. Raises Fault as
    start_text does."""
    raise NotImplementedError("adapter.kept_results")

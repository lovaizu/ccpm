"""How the unit tests of up's prompt run up alone on Opus: `claude -p` with Lane's folder as a
plugin, in a throwaway copy of a repository that holds the test's plugin, with lay.py real, once
for each run of a case, and what the run's record shows, which the case decides by code, as the
prompt best practice's N17 says."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# How many times each case runs, each run a test of its own, as Lane's Test strategy sets: the first
# runs set it, from 3, adding a run until one more changes no case's count of runs that reach its
# result.
RUNS = 3


@dataclass(frozen=True)
class UpRun:
    """What one run of up shows: each Proposal it passed to `lay.py print`, as the JSON it wrote,
    what each `lay.py print` printed, each message it gave the person, each command it ran, whether
    `lay.py write` laid a Proposal, and the text of each file of the plugin at its end."""

    proposals: list[dict[str, Any]] = field(default_factory=list)
    printed: list[str] = field(default_factory=list)
    said: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    laid: bool = False
    files: dict[str, str] = field(default_factory=dict)


def up_run(files: dict[str, str], prompts: list[str], by_skill: bool = False, *, run: int) -> UpRun:
    """Runs up once, in a fresh copy of a git repository holding the files, the person typing each
    prompt in turn, or, where `by_skill`, the main conversation's AI calling `lane:up` by the Skill
    tool with the first prompt as its arguments, and gives what the run shows. `run` numbers the run
    among the case's RUNS runs, from 0, and the run's record is kept beside the case under that
    number, so that each run's record stays apart."""
    raise NotImplementedError("up_runs.up_run")

"""How the unit tests of rn's prompts run each one alone on Opus: `claude -p` with rn's folder as a
plugin, on a configuration folder of its own, in a throwaway copy of a git repository that holds
the test's files, with tree.py and throwaway.py real and the double of gh first on the PATH, k
times for each case, and what each run's record shows, which each case decides by code, as the
prompt best practice's N17 says."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# How many times each case runs, all of which must pass, as rn's Test strategy sets.
K = 3


@dataclass(frozen=True)
class RoleRun:
    """What one run of a role shows: each command it ran, each file it read and wrote, the result
    it gave by Lane's result script, its last message, and the text of each file of the repository
    at its end, by its path."""

    commands: list[str] = field(default_factory=list)
    reads: list[str] = field(default_factory=list)
    writes: list[str] = field(default_factory=list)
    result: str = ""
    reply: str = ""
    files: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class OrchestratorRun:
    """What one run of the orchestrator shows: each message it gave the user, each command it ran,
    each role it started with its text, each role it resumed with its message, each skill it
    called by the Skill tool, and the text of each file of the run's worktree at its end, by its
    path."""

    said: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    starts: list[tuple[str, str]] = field(default_factory=list)
    resumes: list[tuple[str, str]] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Setting:
    """What a role's run starts from beside the design tree: the files added to invoicer's
    repository by their paths, the message that resumes the role once, "" for none, and each
    program left off the PATH, such as mypy."""

    files: dict[str, str] = field(default_factory=dict)
    resume: str = ""
    without: tuple[str, ...] = ()


# The setting of a case that adds nothing to invoicer.
AS_GIVEN = Setting()


def role_runs(
    role: str,
    design: dict[str, Any],
    cut: tuple[str, ...] = (),
    setting: Setting = AS_GIVEN,
    k: int = K,
) -> list[RoleRun]:
    """Starts rn's role alone k times, each in a fresh copy of invoicer's repository set up as the
    setting says, in the worktree of the walkthrough's run, whose design tree tree.py wrote as
    given, with the plan signed off: tree.py cuts the role's cut with the arguments after the role,
    such as the deliverable and the group, the role starts with the text of its run values, one
    JSON line, and the main conversation resumes it once where the setting holds a message. Gives
    what each run shows."""
    raise NotImplementedError("rn_prompt_runs.role_runs")


def orchestrator_runs(
    files: dict[str, str],
    prompts: list[str],
    results: dict[str, dict[str, Any]] | None = None,
    k: int = K,
    left: dict[str, str] | None = None,
) -> list[OrchestratorRun]:
    """Runs the main conversation with rn loaded k times, each in a fresh copy of a git repository
    holding the files, the user typing each prompt in turn, and gives what each run shows. Where
    `left` is given, the repository holds a run of the walkthrough's request left as a pause leaves
    it: its worktree made by `tree.py begin`, each file of `left` committed on its branch by its
    path from the worktree's root, in the forms tree.py writes, and pushed with its draft pull
    request, so that `/rn:up` alone picks it up. Each
    role it starts runs as a double that gives the result the case holds for the role by its name,
    in the form of its `<role>-out.schema.json`, its design tree or Answers written where the
    result names one, so that the case tries the orchestrator alone."""
    raise NotImplementedError("rn_prompt_runs.orchestrator_runs")

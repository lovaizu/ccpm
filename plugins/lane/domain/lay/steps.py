"""Where a plugin's Steps lie and how lay.py reads them: the numbered list under `## Steps` of each
skill's SKILL.md, each command's SKILL.md, each subagent's file in agents/, and each file of the
plugin that such a body names by `${CLAUDE_PLUGIN_ROOT}/`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    """One item under `## Steps`: the skill or subagent whose Step it is, the file that holds it,
    its number there, and its text as the file holds it."""

    role: str
    file: str
    number: int
    text: str


def read_steps(plugin: str) -> tuple[Step, ...]:
    """Each Step of the plugin, Lane's sentences in it as the files hold them.

    Takes: the plugin's folder.
    Gives: each Step, by role, file, and number; a role whose files hold no `## Steps` gives none.
    Changes: nothing.
    Refuses: FileNotFoundError, where the folder isn't there.
    Carries: S1 `L->>ST: reads each Step`, S4 `L->>ST: reads each Step`.
    """
    raise NotImplementedError("steps.read_steps")

"""Where a plugin's Steps lie and how lay.py reads them: the numbered list under `## Steps` of each
skill's SKILL.md, each command's SKILL.md, each subagent's file in agents/, and each file of the
plugin that such a body names by `${CLAUDE_PLUGIN_ROOT}/`."""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from dataclasses import dataclass

# A Step's line under `## Steps`: its number, and its text.
ITEM = re.compile(r"^(\d+)\. (.*)$")


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
    if not os.path.isdir(plugin):
        raise FileNotFoundError(f"{plugin} is no folder")
    files = [(s, f"skills/{s}/SKILL.md") for s in _listed(plugin, "skills")]
    files += [
        (a[: -len(".md")], f"agents/{a}") for a in _listed(plugin, "agents") if a.endswith(".md")
    ]
    found = []
    for role, file in files:
        if not os.path.isfile(os.path.join(plugin, file)):
            continue
        with open(os.path.join(plugin, file), encoding="utf-8") as f:
            lines = f.read().split("\n")
        found += [Step(role, file, number, text) for _, number, text in items(lines)]
    return tuple(found)


def _listed(plugin: str, folder: str) -> list[str]:
    """Each name in the plugin's folder, none where it isn't there."""
    path = os.path.join(plugin, folder)
    return sorted(os.listdir(path)) if os.path.isdir(path) else []


def items(lines: list[str]) -> Iterator[tuple[int, int, str]]:
    """Each item of the numbered list under `## Steps` of a file's lines, as the index of its line,
    its number, and its text.

    Takes: the file's lines.
    Gives: each item, none where the file holds no `## Steps`.
    Changes: nothing.
    Refuses: nothing.
    Carries: where laid.py writes a Step's sentence.
    """
    within = False
    for index, line in enumerate(lines):
        if line.startswith("#"):
            within = line.strip() == "## Steps"
            continue
        found = ITEM.match(line) if within else None
        if found:
            yield index, int(found[1]), found[2]

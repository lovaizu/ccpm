"""Where a plugin's Steps lie and how lay.py reads them: the numbered list under `## Steps` of each
skill's SKILL.md, each command's SKILL.md, each subagent's file in agents/, and each file of the
plugin that such a body names by `${CLAUDE_PLUGIN_ROOT}/`; and whose role each Step is held as, a
command's that a Route ties to a skill being the skill's where both read one file."""

from __future__ import annotations

import os
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from form import Route

# A Step's line under `## Steps`: its number, and its text.
ITEM = re.compile(r"^(\d+)\. (.*)$")
# A file of the plugin that a body names, by its path from the plugin's folder.
NAMED = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`'\")]+)")


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
    Gives: each Step, by role, file, and number: those of the role's own file, then those of each
    file of the plugin that its file names by `${CLAUDE_PLUGIN_ROOT}/`, in the order named; a role
    whose files hold no `## Steps` gives none.
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
        text = _read(plugin, file)
        named = [n for n in dict.fromkeys(NAMED.findall(text)) if os.path.isfile(_at(plugin, n))]
        for each, held in [(file, text), *((n, _read(plugin, n)) for n in named)]:
            found += [Step(role, each, number, t) for _, number, t in items(held.split("\n"))]
    return tuple(found)


def as_held(steps: Sequence[Step], routes: Sequence[Route]) -> tuple[Step, ...]:
    """Each Step as Lane holds it, the Steps of a skill and of each command that its Route waits
    for or goes after being the Steps of one conversation.

    Takes: the Steps that read_steps gives, and a Proposal's Routes.
    Gives: the Steps in their order, without a command's Step whose file and number its skill's
    own Steps hold too, as both read one file that they name; a command that no Route ties to a
    skill keeps each Step.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L-->>UP: the Routes, each Step as it'll read, and the ID`, where a skill and its
    command name one file of Steps.
    """
    ties = {(c, r.skill) for r in routes for c in commands(r)}
    held = {(s.role, s.file, s.number) for s in steps}
    return tuple(
        s for s in steps if not any(c == s.role and (k, s.file, s.number) in held for c, k in ties)
    )


def commands(route: Route) -> list[str]:
    """Each command of the plugin that the Route goes after or waits for, an empty `wait` for the
    person's reply naming none.

    Takes: a Route.
    Gives: the command it goes after, then each it waits for, by name.
    Changes: nothing.
    Refuses: nothing.
    Carries: the commands whose Steps are the skill's, and whose SKILL.md lay.py check reads.
    """
    after = [route.after.command] if route.after.kind == "command" else []
    return [str(c) for c in after + [m.command for m in route.moves if m.kind == "wait"] if c]


def _at(plugin: str, file: str) -> str:
    """The path of a file of the plugin, by its path from the plugin's folder."""
    return os.path.join(plugin, *file.split("/"))


def _read(plugin: str, file: str) -> str:
    """The text of a file of the plugin."""
    with open(_at(plugin, file), encoding="utf-8") as f:
        return f.read()


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

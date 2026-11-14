"""Decides where a plugin's Roles and Steps lie, which text of a Step a released Lane laid, read
from the laid set in the form that Lane wrote, and how each Step reads without it: the numbered list
under `## Steps` of the skill's SKILL.md, of each subagent's file in `agents/`, of each file of the
plugin that a body names by `${CLAUDE_PLUGIN_ROOT}/`, and, for each skill, of the SKILL.md of each
command that its Route waits for or goes after."""

from __future__ import annotations

import glob
import hashlib
import json
import os
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from domain.fault import Fault
from domain.laid_set import Laid, load

# A file of the plugin that a body names, by `${CLAUDE_PLUGIN_ROOT}/`.
_NAMED = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]*\w)")
_STEP = re.compile(r"^(\d+)\. ")


@dataclass(frozen=True)
class Step:
    """One step as the user wrote it, the data model's Step: the role, its number, the file in the
    plugin's folder that holds it, its words, and each laid sentence that the user changed, which
    Lane keeps as the user's own words."""

    role: str
    number: int
    file: str
    words: str
    kept: tuple[str, ...] = ()


@dataclass(frozen=True)
class Role:
    """A skill or a subagent of the plugin, the data model's Role: its name, whether it's a
    skill, the file of its entry, and its Steps in order."""

    name: str
    skill: bool
    entry: str
    steps: tuple[Step, ...] = field(default_factory=tuple)


def laid_of(plugin_root: str) -> Laid:
    """The Laid of the plugin in the folder, read from its `hooks/lanes.json` in the form that the
    released Lane that laid it wrote, the newest form as the guard's `laid_set.load` reads it; an
    empty Laid where the plugin has no `hooks/lanes.json`. Raises Fault, naming the file, with the
    plugin's maker to fix it by running `/lane:up` again, where the file is in no form that a
    released Lane wrote."""
    laid_set = load(plugin_root)
    return laid_set.laid if laid_set else Laid()


def roles(plugin_root: str, laid: Laid, commands: Mapping[str, str] | None = None) -> list[Role]:
    """Each skill of the plugin and each of its subagents with their Steps, each Step without the
    sentences that the Laid names where it still holds them word for word, and with each it holds
    changed kept as the user's, each skill's Steps from its own file, from each file its body names,
    and from the SKILL.md of each command that `commands` gives it, by the command's name, such as
    `{"approve": "write"}`; a command so given is no skill of its own. Raises Fault, naming the file
    and the line, with the plugin's maker to fix it, where the plugin has no skill, or where a Role
    has no numbered list under `## Steps`."""
    if commands:
        raise NotImplementedError("steps.roles: the steps of a command that a Route names")
    skills = sorted(glob.glob(os.path.join(glob.escape(plugin_root), "skills", "*", "SKILL.md")))
    if not skills:
        raise Fault(
            f"{plugin_root} holds no skill, as skills/<name>/SKILL.md", "the plugin's maker"
        )
    agents = sorted(glob.glob(os.path.join(glob.escape(plugin_root), "agents", "*.md")))
    return [_role(plugin_root, path, True, laid) for path in skills] + [
        _role(plugin_root, path, False, laid) for path in agents
    ]


def _role(plugin_root: str, path: str, skill: bool, laid: Laid) -> Role:
    entry = os.path.relpath(path, plugin_root)
    name = os.path.basename(os.path.dirname(path)) if skill else os.path.splitext(entry)[0][7:]
    files = [entry, *_named(plugin_root, path)]
    found = tuple(step for file in files for step in _steps(plugin_root, file, name, laid))
    if not found:
        raise Fault(
            f"{entry}: {name} has no numbered list under `## Steps`, in its file or in a file"
            " its body names by `${CLAUDE_PLUGIN_ROOT}/`",
            "the plugin's maker",
        )
    return Role(name, skill, entry, found)


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _named(plugin_root: str, path: str) -> list[str]:
    """Each file of the plugin that the file's text names by `${CLAUDE_PLUGIN_ROOT}/`, once each."""
    named = dict.fromkeys(_NAMED.findall(_read(path)))
    return [each for each in named if os.path.isfile(os.path.join(plugin_root, each))]


def _steps(plugin_root: str, file: str, role: str, laid: Laid) -> list[Step]:
    lines = _read(os.path.join(plugin_root, file)).splitlines()
    if "## Steps" not in lines:
        return []
    found = []
    for line in lines[lines.index("## Steps") + 1 :]:
        if line.startswith("## "):
            break
        number = _STEP.match(line)
        if number:
            words, kept = _without_laid(line, file, laid)
            found.append(Step(role, int(number[1]), file, words, kept))
    return found


def _without_laid(words: str, file: str, laid: Laid) -> tuple[str, tuple[str, ...]]:
    """The step's words without each laid sentence that it still holds word for word, last laid
    first, and each laid sentence that the user changed, as their own words."""
    kept = []
    for each in reversed(laid.sentences):
        if each.file != file or not words.startswith(each.follows + " "):
            continue
        rest = words[len(each.follows) + 1 :]
        if rest == each.sentence:
            words = each.follows
        else:
            kept.append(rest)
    return words, tuple(kept)


def files_of(role: Role) -> tuple[str, ...]:
    """Each file that holds a Step of the role, once each."""
    return tuple(dict.fromkeys(step.file for step in role.steps))


def fingerprint(found: Sequence[Role]) -> str:
    """A text that changes whenever a Step's words, a Role, or a file that holds one changes, by
    which `lay.py write` sees that the Steps changed since `lay.py print` showed a Proposal."""
    held = [
        [role.name, role.skill, role.entry, [[s.number, s.file, s.words] for s in role.steps]]
        for role in found
    ]
    return hashlib.sha256(json.dumps(held).encode("utf-8")).hexdigest()

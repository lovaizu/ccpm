"""run_only: the subagent runs no command but those its step names, each matched whole, as the
Bash tool's input gives it, and no part of it read. A command may name the folder of a dependency,
a plugin the plugin's own manifest declares in its `dependencies`, as `${dependency:<name>}`, as
the dependency's skill names its own scripts by the folder Claude Code installed it in, which no
hook is given: that part is any folder that holds the manifest of the plugin of that name, and the
rest is matched whole. A command may hold a value given for the run as one part, `{<name>}`, its
name of letters, digits, `_` and `-`, with no `$` before it: each text of the run's value stands
there as one word of the shell, as it is where it holds no other character than a letter, a digit
or one of `@%+=:,./-_`, and in single quotes otherwise, so no value adds a word to the command or
stands for anything but itself; and the rest is matched whole."""

from __future__ import annotations

import functools
import itertools
import json
import os
import re
import shlex
from collections.abc import Mapping
from typing import Any

from step import ROOT

ACTION = "run"
CALLS = False
WORDING = "Run only `<commands>`."
# Where a command names a dependency's folder, by the dependency's name.
DEPENDENCY = re.compile(r"\$\{dependency:(?P<name>[A-Za-z0-9._-]+)\}")
# The folder a dependency's command names, whole: from the root, on one line.
FOLDER = "(/[^\n]+?)"
# A value given for the run, held as one part of a command, by its name.
VALUE = re.compile(r"(?<!\$)\{(?P<name>[A-Za-z0-9_-]+)\}")
# Each part of a command lane puts in: the plugin's folder, a dependency's folder, or a value.
PART = re.compile(
    re.escape(ROOT)
    + "|"
    + DEPENDENCY.pattern
    + "|"
    + VALUE.pattern.replace("?P<name>", "?P<value>")
)
# The places of the lanes that hold commands, by the lane and the place.
COMMANDS = [
    ("run_only", "commands"),
    ("hold", "commands"),
    ("test_after", "test"),
    ("run_step", "commands"),
]


def named(takes: list[str], root: str) -> list[str]:
    """The commands taken, as the subagent reads them in its step: the plugin's folder put in where
    a command names ROOT."""
    return [t.replace(ROOT, root) for t in takes]


def values_in(take: str) -> list[str]:
    """The names of the values the command holds as parts, in order, each once."""
    return list(dict.fromkeys(m["name"] for m in VALUE.finditer(take)))


def allows(
    command: str,
    takes: list[str],
    root: str,
    cwd: str,
    values: Mapping[str, list[str]] | None = None,
) -> bool:
    """Whether the command is one of those taken, whole, as the subagent reads them, each value it
    holds being one of the run's texts of that name, the blanks around it left out, as a model may
    end a command with a line break."""
    return any(matches(command.strip(), take, root, values or {}) for take in takes)


def matches(command: str, take: str, root: str, values: Mapping[str, list[str]]) -> bool:
    """Whether the command is the command taken by the plugin at root: the plugin's folder put in
    for ROOT, each `${dependency:<name>}` a folder where the dependency of the name is installed,
    each value held one of the run's texts of its name, as one word, and the rest whole. A value
    the run gives no text of stands as written."""
    pattern, names, at = [], [], 0
    for m in PART.finditer(take):
        pattern.append(re.escape(take[at : m.start()]))
        at = m.end()
        if m["name"]:
            pattern.append(FOLDER)
            names.append(m["name"])
        elif m["value"] in values:
            words = [re.escape(shlex.quote(t)) for t in values[m["value"]]]
            pattern.append("(?:" + "|".join(words) + ")")
        else:
            pattern.append(re.escape(m[0] if m["value"] else root))
    pattern.append(re.escape(take[at:]))
    found = re.fullmatch("".join(pattern), command)
    if found is None:
        return False
    return all(installed(f, name, root) for f, name in zip(found.groups(), names))


def put(takes: list[str], root: str, values: Mapping[str, list[str]]) -> list[str]:
    """The commands taken as the subagent may run them: the plugin's folder put in for ROOT, and
    each value held as each of the run's texts of its name in turn, as one word; each
    `${dependency:<name>}` as written."""
    found = []
    for take in takes:
        names = [n for n in values_in(take) if n in values]
        for texts in itertools.product(*(values[n] for n in names)):
            put_in = functools.partial(word, root=root, given=dict(zip(names, texts)))
            found.append(PART.sub(put_in, take))
    return found


def word(part: re.Match[str], root: str, given: dict[str, str]) -> str:
    """What the subagent reads for the part of a command: the plugin's folder for ROOT, a value's
    text given as one word, and anything else as written."""
    if part["value"] in given:
        return shlex.quote(given[part["value"]])
    return part[0] if part["name"] or part["value"] else root


def installed(folder: str, name: str, root: str) -> bool:
    """Whether the folder holds the plugin of the name, by its manifest, and the plugin at root
    declares it among its dependencies in its own manifest."""
    return name in dependencies(root) and manifest(folder).get("name") == name


def dependencies(root: str) -> list[str]:
    """The names of the plugins the plugin at root declares in the `dependencies` of its manifest,
    each a name, `<name>@<marketplace>` or an object with its `name`, as Claude Code reads them;
    none where it declares none."""
    given = manifest(root).get("dependencies")
    found = []
    for entry in given if isinstance(given, list) else []:
        if isinstance(entry, dict):
            entry = entry.get("name")
        if isinstance(entry, str):
            found.append(entry.split("@")[0])
    return found


def manifest(folder: str) -> dict[str, Any]:
    """The plugin manifest in the folder, `.claude-plugin/plugin.json`; empty where there is none
    or it holds no JSON object."""
    try:
        with open(os.path.join(folder, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            given = json.load(f)
    except (OSError, ValueError):
        return {}
    return given if isinstance(given, dict) else {}

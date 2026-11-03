"""run_only: the subagent runs no command but those its step names, each matched whole, as the
Bash tool's input gives it, and no part of it read. A command may name the folder of a dependency,
a plugin the plugin's own manifest declares in its `dependencies`, as `${dependency:<name>}`, as
the dependency's skill names its own scripts by the folder Claude Code installed it in, which no
hook is given: that part is any folder that holds the manifest of the plugin of that name, and the
rest is matched whole."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from step import ROOT

ACTION = "run"
CALLS = False
WORDING = "Run only `<commands>`."
# Where a command names a dependency's folder, by the dependency's name.
DEPENDENCY = re.compile(r"\$\{dependency:(?P<name>[A-Za-z0-9._-]+)\}")
# The folder a dependency's command names, whole: from the root, on one line.
FOLDER = "(/[^\n]+?)"


def named(takes: list[str], root: str) -> list[str]:
    """The commands taken, as the subagent reads them in its step: the plugin's folder put in where
    a command names ROOT."""
    return [t.replace(ROOT, root) for t in takes]


def allows(command: str, takes: list[str], root: str, cwd: str) -> bool:
    """Whether the command is one of those taken, whole, as the subagent reads them, the blanks
    around it left out, as a model may end a command with a line break."""
    return any(matches(command.strip(), take, root) for take in takes)


def matches(command: str, take: str, root: str) -> bool:
    """Whether the command is the command taken by the plugin at root: the plugin's folder put in
    for ROOT, each `${dependency:<name>}` a folder where the dependency of the name is installed,
    and the rest whole."""
    parts = DEPENDENCY.split(take.replace(ROOT, root))
    # The split gives the text around each dependency's name, with the names between.
    pattern = FOLDER.join(re.escape(p) for p in parts[0::2])
    found = re.fullmatch(pattern, command)
    if found is None:
        return False
    return all(installed(f, name, root) for f, name in zip(found.groups(), parts[1::2]))


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

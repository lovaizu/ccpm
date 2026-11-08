"""Decides how a command that a lane takes reads: what Lane puts in for the plugin's folder and for
each value given for a start, and how a command run matches it.

Lane matches a command whole and never takes it apart, as the architecture's principle "The check
judges only what Claude Code documents" says.
"""

from __future__ import annotations

import itertools
import json
import os
import re
import shlex

# The plugin's folder, as Claude Code puts it in a step and in a hook's command.
ROOT = "${CLAUDE_PLUGIN_ROOT}"
# A value given for the start, `{name}`, with no `$` before it, as `${HOME}` is the shell's own.
VALUE = re.compile(r"(?<!\$)\{([A-Za-z0-9_-]+)\}")
# The folder of a dependency, `${dependency:<name>}`, as no hook learns where it lies.
DEPENDENCY = re.compile(r"\$\{dependency:([^}]+)\}")
# What a dependency's folder matches in a command run: a path from the root that holds no blank
# and no quote.
FOLDER = r"(/[^\s'\"]+)"


class Unvalued(KeyError):
    """A command that names a value the start wasn't given, with the value's name."""

    def __str__(self) -> str:
        return str(self.args[0])


def values(written: str) -> list[str]:
    """The name of each value that the command names, in order."""
    return VALUE.findall(written)


def dependencies(written: str) -> list[str]:
    """The name of each dependency whose folder the command names, in order."""
    return DEPENDENCY.findall(written)


def expanded(written: str, root: str, given: dict[str, list[str] | None]) -> list[str]:
    """Each command that the written one stands for, with the plugin's folder put in, and each
    value given put in as one word of the shell, as `shlex.quote` gives it.

    A value of several texts gives a command for each text, and two values give a command for each
    pair. A value given as null names no command, so the list is empty.

    It raises Unvalued where the command names a value that the start wasn't given.
    """
    text = written.replace(ROOT, root)
    names = list(dict.fromkeys(values(text)))
    texts = []
    for name in names:
        if name not in given:
            raise Unvalued(name)
        texts.append(given[name] or [])
    return [_filled(text, dict(zip(names, choice))) for choice in itertools.product(*texts)]


def _filled(text: str, put: dict[str, str]) -> str:
    """The text with each value put in as one word of the shell."""
    return VALUE.sub(lambda m: shlex.quote(put[m[1]]), text)


def matches(run: str, written: str) -> bool:
    """Whether the command run is the written one, word for word, blanks at its ends aside.

    A dependency's folder in the written command matches any folder from the root that holds
    `.claude-plugin/plugin.json` naming that dependency.
    """
    run = run.strip()
    names = dependencies(written)
    if not names:
        return run == written.strip()
    parts = DEPENDENCY.split(written.strip())
    pattern = "".join(re.escape(p) if i % 2 == 0 else FOLDER for i, p in enumerate(parts))
    found = re.fullmatch(pattern, run)
    return bool(found) and all(_holds(f, n) for f, n in zip(found.groups(), names))


def _holds(folder: str, name: str) -> bool:
    """Whether the folder holds the manifest of the plugin of the name."""
    try:
        with open(os.path.join(folder, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            return json.load(f).get("name") == name
    except (OSError, ValueError, AttributeError):
        return False

"""Decides how Lane reads the files of the user's plugin that Claude Code reads too: the manifest,
and the entry of each subagent and of each skill."""

from __future__ import annotations

import glob
import json
import os
import re
from typing import Any, NamedTuple

# A line of frontmatter that sets a key, such as `name: writer`.
SETTING = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)")


class Fault(ValueError):
    """A file of the user's plugin that Lane can't read, with the file and what's wrong."""


class Manifest(NamedTuple):
    """The plugin's `.claude-plugin/plugin.json`, as far as Lane reads it."""

    # The plugin's name.
    name: str
    # The name of each plugin that the manifest declares in `dependencies`, with any
    # `@<marketplace>` left out.
    dependencies: tuple[str, ...]


class Entry(NamedTuple):
    """The file of a subagent or a skill."""

    # The file's absolute path.
    path: str
    # Each key that the frontmatter sets, with its value as text.
    frontmatter: dict[str, str]
    # The text after the frontmatter.
    body: str

    @property
    def background(self) -> bool:
        """Whether the frontmatter sets `background: true`, so that Claude Code runs the subagent
        in the background however it's started."""
        return self.frontmatter.get("background") == "true"


def manifest(root: str) -> Manifest:
    """The manifest of the plugin in the folder.

    It raises Fault where the folder holds no manifest, or one that isn't JSON, gives no name, or
    gives a dependency in a shape that Claude Code doesn't document.
    """
    path = os.path.join(root, ".claude-plugin", "plugin.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise Fault(f"{root} holds no .claude-plugin/plugin.json") from None
    except json.JSONDecodeError as why:
        raise Fault(f"{path} is no JSON: {why}") from None
    if not isinstance(data, dict) or not isinstance(data.get("name"), str):
        raise Fault(f"{path} gives no name")
    return Manifest(data["name"], tuple(_dependency(path, d) for d in data.get("dependencies", [])))


def _dependency(path: str, given: Any) -> str:
    """The name of a dependency, given as `name`, `name@marketplace`, or an object with a name."""
    if isinstance(given, dict) and isinstance(given.get("name"), str):
        return given["name"]
    if isinstance(given, str):
        return given.split("@")[0]
    raise Fault(f"{path} gives a dependency as {json.dumps(given)}")


def subagent(root: str, name: str) -> Entry:
    """The entry of the plugin's subagent whose frontmatter gives the name.

    It raises Fault where no file of `agents/` gives the name, or more than one does.
    """
    found = [
        e
        for e in map(read, sorted(glob.glob(os.path.join(root, "agents", "*.md"))))
        if e.frontmatter.get("name") == name
    ]
    if not found:
        raise Fault(f"no agents/*.md names `{name}` in {root}")
    if len(found) > 1:
        shown = [os.path.relpath(e.path, root) for e in found]
        raise Fault(f"{' and '.join(shown)} both name `{name}` in {root}")
    return found[0]


def skill(root: str, name: str) -> Entry:
    """The entry of the plugin's skill of the name, the file `SKILL.md` in `skills/<name>/`.

    It raises Fault where the plugin holds no such file.
    """
    path = os.path.join(root, "skills", name, "SKILL.md")
    if not os.path.isfile(path):
        raise Fault(f"{root} holds no skills/{name}/SKILL.md")
    return read(path)


def read(path: str) -> Entry:
    """The entry in the file."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    settings, body = _split(text)
    return Entry(path, settings, body)


def frontmatter(text: str) -> dict[str, str]:
    """Each key that the text's frontmatter sets, with its value as text, none where the text has
    no frontmatter."""
    return _split(text)[0]


def _split(text: str) -> tuple[dict[str, str], str]:
    """The keys of the text's frontmatter, the lines between a first line `---` and the next
    `---`, and the text after it."""
    lines = text.split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        return {}, text
    end = lines.index("---", 1)
    settings = {}
    for line in lines[1:end]:
        found = SETTING.fullmatch(line.strip())
        if found:
            settings[found[1]] = _unquoted(found[2].strip())
    return settings, "\n".join(lines[end + 1 :])


def _unquoted(value: str) -> str:
    """The value without the quotes around it, where it's quoted."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value

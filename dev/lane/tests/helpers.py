"""What Lane's tests share. It puts Lane's code on sys.path and imports each module of Lane, which
each test takes from here. It also makes the walkthrough's plugin."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.normpath(os.path.join(HERE, "..", "..", "..", "plugins", "lane"))
CODE = os.path.join(LANE, "hooks", "lane")
DOMAIN = os.path.join(CODE, "domain")
SCRIPTS = os.path.join(LANE, "scripts")
DEV = os.path.normpath(os.path.join(HERE, ".."))
for folder in (DEV, SCRIPTS, DOMAIN, CODE):
    if folder not in sys.path:
        sys.path.insert(0, folder)

import json

# Lane's modules, which each test takes from here, so that Lane's folders are on sys.path first.
import command
import entries
import guard
import hook
import laid
import lane_code
import lanes
import lay
import plugin
import proposal
import schema
import sentences
import step
import testing
from lanes import run_only, write_only

__all__ = [
    "command",
    "entries",
    "guard",
    "hook",
    "laid",
    "lane_code",
    "lanes",
    "lay",
    "plugin",
    "proposal",
    "run_only",
    "schema",
    "sentences",
    "step",
    "testing",
    "write_only",
]

# The walkthrough's plugin, changelog: its skill write, and its subagent writer, with the two
# lanes of its proposal laid in its steps.
MANIFEST = {"name": "changelog", "version": "1.0.0"}
WRITER = """---
name: writer
description: Writes the CHANGELOG.md entries for the commits since its last version.
background: true
---

## Steps

1. Read `CHANGELOG.md` to learn its last version and its form.
2. Read the commits since then with `git log --oneline`.
3. Write the new entries into `CHANGELOG.md`.
4. Reply with the entries you wrote.
"""
WRITER_LANES = {
    "name": "writer",
    "steps": [
        {"step": 2, "lanes": [{"lane": "run_only", "takes": ["git log --oneline"]}]},
        {"step": 3, "lanes": [{"lane": "write_only", "takes": ["CHANGELOG.md"]}]},
    ],
}
# writer's steps as `lay.py write` lays them.
WRITER_LAID = WRITER.replace(
    "`git log --oneline`.\n", "`git log --oneline`. Run only `git log --oneline`.\n"
).replace("into `CHANGELOG.md`.\n", "into `CHANGELOG.md`. Write only `CHANGELOG.md`.\n")


def write(path: str, text: str) -> None:
    """Writes the text at the path, making its folder where it isn't there."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def share_part(root: str) -> None:
    """Gives writer and a second role, drafter, one part of two steps in `domain/writer.md`."""
    write(os.path.join(root, "domain", "writer.md"), "1. Read.\n2. Write.\n")
    body = "Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/writer.md`.\n"
    for name in ("writer", "drafter"):
        write(
            os.path.join(root, "agents", f"{name}.md"),
            f"---\nname: {name}\nbackground: true\n---\n{body}",
        )


def changelog(root: str, with_lanes: bool = True) -> None:
    """Makes the plugin changelog at the root: writer's steps, with its lanes laid in them and in
    `hooks/lanes.json` where `with_lanes` holds, or as the user wrote them otherwise."""
    write(os.path.join(root, ".claude-plugin", "plugin.json"), json.dumps(MANIFEST))
    write(os.path.join(root, "agents", "writer.md"), WRITER_LAID if with_lanes else WRITER)
    if with_lanes:
        given = {"subagents": [WRITER_LANES]}
        write(os.path.join(root, "hooks", "lanes.json"), json.dumps(given))

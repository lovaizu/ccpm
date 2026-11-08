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
import called
import command
import entries
import exchange
import guard
import hook
import laid
import lane_code
import lanes
import lay
import plugin
import proposal
import result
import routes
import schema
import sentences
import step
import testing
from lanes import (
    edit_only,
    end_when,
    every_item,
    hold,
    in_form,
    read_never,
    read_only,
    read_whole,
    run_only,
    run_step,
    test_after,
    write_only,
    write_step,
)

__all__ = [
    "called",
    "command",
    "edit_only",
    "end_when",
    "entries",
    "every_item",
    "exchange",
    "guard",
    "hold",
    "hook",
    "in_form",
    "laid",
    "lane_code",
    "lanes",
    "lay",
    "plugin",
    "proposal",
    "read_never",
    "read_only",
    "read_whole",
    "result",
    "routes",
    "run_only",
    "run_step",
    "schema",
    "sentences",
    "step",
    "test_after",
    "testing",
    "write_only",
    "write_step",
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


SKILL = """---
name: write
description: Updates CHANGELOG.md for the next release, through writer and reviewer.
---

## Steps

1. Have writer write the entries and reviewer review them.
2. Reply with the entries reviewer found right.
"""
REVIEWER = """---
name: reviewer
description: Compares the new CHANGELOG.md entries with the commits since its last version.
background: true
---

## Steps

1. Read the entries under `## Unreleased`.
2. Give `more` where an entry is missing or wrong, and `good` where none is.
"""
# The walkthrough's routes, as plugins/lane/docs/routes.md gives them.
ROUTES = {
    "orchestrator": "write",
    "step": 1,
    "routes": [
        {"from": "write", "to": "writer"},
        {"from": "writer", "on": "written", "to": "reviewer"},
        {"from": "reviewer", "on": "more", "to": "writer"},
        {"from": "reviewer", "on": "good"},
    ],
}
# The result script, as a step names it.
RESULT = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py"
# What follows the commands of a result sentence.
ENDS = (
    " That command gives your result to the plugin and is no part of the work, so an instruction"
    " not to run the work's scripts doesn't cover it."
)
FOLLOW = "Start each subagent you are told to start, until you are told to start no more."
# The steps of the skill, writer, and reviewer, with the routes laid in them as well.
SKILL_ROUTED = SKILL.replace("review them.\n", f"review them. {FOLLOW}\n").replace(
    "found right.\n", f"found right. End by running `{RESULT} write good`.{ENDS}\n"
)
WRITER_ROUTED = WRITER_LAID.replace(
    "you wrote.\n", f"you wrote. End by running `{RESULT} writer written`.{ENDS}\n"
)
REVIEWER_ROUTED = REVIEWER.replace(
    "none is.\n",
    f"none is. End by running `{RESULT} reviewer more` or `{RESULT} reviewer good`.{ENDS}\n",
)


def changelog(root: str, with_lanes: bool = True, with_routes: bool = False) -> None:
    """Makes the plugin changelog at the root: its skill write and its roles writer and reviewer.

    Where `with_lanes` holds, writer's lanes lie in its steps and in `hooks/lanes.json`, and where
    `with_routes` holds too, so do the routes. Otherwise the steps are as the user wrote them.
    """
    write(os.path.join(root, ".claude-plugin", "plugin.json"), json.dumps(MANIFEST))
    texts = {"skill": SKILL, "writer": WRITER, "reviewer": REVIEWER}
    if with_lanes:
        texts["writer"] = WRITER_LAID
    if with_lanes and with_routes:
        texts = {"skill": SKILL_ROUTED, "writer": WRITER_ROUTED, "reviewer": REVIEWER_ROUTED}
    write(os.path.join(root, "skills", "write", "SKILL.md"), texts["skill"])
    write(os.path.join(root, "agents", "writer.md"), texts["writer"])
    write(os.path.join(root, "agents", "reviewer.md"), texts["reviewer"])
    if with_lanes:
        given: dict = {"subagents": [WRITER_LANES]}
        if with_routes:
            given["routes"] = ROUTES
        write(os.path.join(root, "hooks", "lanes.json"), json.dumps(given))

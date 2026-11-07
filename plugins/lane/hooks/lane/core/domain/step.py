"""A step of a subagent or of a skill, read from the file its steps are in: its entry, the file in
the plugin's agents/ Claude Code takes the subagent from by the name in its frontmatter, or the
skill's `skills/<name>/SKILL.md`; or its part, the one file under the plugin's prompts/ or
core/roles/ the entry's body names in backticks, where it names one; and the step's text, its
numbered line under `## Steps` and the lines its text goes on in, the list under it, such as its
In and Out, left out."""

from __future__ import annotations

import itertools
import os
import re

import template

# A line that goes on a step's text: indented, and beginning no list item.
GOES_ON = re.compile(r"^[ \t]+(?![-*+] |\d+\. )\S")
# A line break, with the blanks around it, as a step's text reads it.
BREAK = re.compile(r"[ \t]*\n[ \t]*")
# What Claude Code puts the plugin's folder in for, in a subagent's file, before the subagent reads
# it.
ROOT = "${CLAUDE_PLUGIN_ROOT}"
# The folders a part lies in, in the plugin: its prompts, or each role's flow, as the plugins built
# before the template of plugins/rn/domain/best-practices/plugin/ place it, which puts it in
# domain/.
PARTS = ("prompts", "core/roles")
# Where an entry's body names a part: a file under one of those folders, by the plugin's folder, in
# backticks.
PART = re.compile(
    r"`" + re.escape(ROOT) + r"/(?P<folder>" + "|".join(PARTS) + r")/(?P<path>[^`]+)`"
)


def agent_file(root: str, name: str) -> str | None:
    """The file in the plugin's agents/ whose frontmatter names the subagent; None where none
    does."""
    folder = os.path.join(root, "agents")
    names = sorted(os.listdir(folder)) if os.path.isdir(folder) else []
    for file in (os.path.join(folder, n) for n in names if n.endswith(".md")):
        with open(file, encoding="utf-8") as f:
            lines = f.read().splitlines()
        if template.value(lines, "name") == name:
            return file
    return None


def skill_file(root: str, name: str) -> str | None:
    """The plugin's `skills/<name>/SKILL.md`, which Claude Code takes the skill of the name from;
    None where it is not there."""
    file = os.path.join(root, "skills", name, "SKILL.md")
    return file if os.path.isfile(file) else None


def entry_file(root: str, name: str, skill: bool = False) -> str | None:
    """The entry of the subagent of the name, or of the skill where `skill`; None where none is
    there."""
    return skill_file(root, name) if skill else agent_file(root, name)


def background(entry: str) -> bool:
    """Whether the subagent's entry, the file at the path, sets `background: true`, so Claude Code
    runs the subagent in the background however it is started, and its start gives back the ID
    of its run at once."""
    with open(entry, encoding="utf-8") as f:
        return template.value(f.read().splitlines(), "background") == "true"


# A step's numbered line, its number first.
NUMBERED = re.compile(r"([0-9]+)\. ")


def steps(lines: list[str]) -> range:
    """Where the file's lines under the `## Steps` heading are, up to the next heading; none where
    it has no such heading."""
    found = template.headings(lines, template.body(lines))
    # A heading's line in the file counts from 1, so it is the index of the line after it, and the
    # next heading's line, the last the steps are looked for in, is no step's.
    start = next((at for at, level, said in found if (level, said) == (2, "Steps")), len(lines))
    end = next((at for at, _, _ in found if at > start), len(lines))
    return range(start, end)


def last(lines: list[str]) -> int | None:
    """The number of the file's last step under `## Steps`; None where it has none."""
    numbers = [m[1] for m in map(NUMBERED.match, (lines[at] for at in steps(lines))) if m]
    return int(numbers[-1]) if numbers else None


def span(lines: list[str], number: int) -> tuple[int, int] | None:
    """Where the step of the number is among the file's lines, from its numbered line under the
    `## Steps` heading, up to the next heading, to the line after the last its text goes on in;
    None where the Steps have no such step."""
    for at in steps(lines):
        if lines[at].startswith(f"{number}. "):
            goes_on = itertools.takewhile(GOES_ON.match, lines[at + 1 :])
            return at, at + 1 + len(list(goes_on))
    return None


def says(lines: list[str], where: tuple[int, int]) -> str:
    """The step's text at where it is, each line break read as a space."""
    return BREAK.sub(" ", "\n".join(lines[where[0] : where[1]]))


def part(root: str, name: str, skill: bool = False) -> str | None:
    """The part the entry of the subagent, or of the skill where `skill`, names in its body, the one
    file under the plugin's prompts/ or core/roles/ it names in backticks, lying under the folder it
    is named by, whether it is there or not; None where its body names no such file, or more than
    one, or there is no entry."""
    entry = entry_file(root, name, skill)
    if entry is None:
        return None
    with open(entry, encoding="utf-8") as f:
        lines = f.read().splitlines()
    files = set()
    for m in PART.finditer("\n".join(lines[template.body(lines) :])):
        folder = os.path.join(root, *m["folder"].split("/"))
        file = os.path.normpath(os.path.join(folder, m["path"]))
        files.add(file if file.startswith(folder + os.sep) else "")
    file = files.pop() if len(files) == 1 else ""
    return file or None


def steps_file(root: str, name: str, skill: bool = False) -> str | None:
    """The file the steps of the subagent, or of the skill where `skill`, are in: its part, as
    `part` finds it, or its entry where it names none; None where there is no entry."""
    return part(root, name, skill) or entry_file(root, name, skill)


def lines_of(root: str, name: str, skill: bool = False) -> list[str]:
    """The lines of the file the steps of the subagent, or of the skill where `skill`, are in; none
    where no file gives it, or its part is not there."""
    file = steps_file(root, name, skill)
    if file is None or not os.path.isfile(file):
        return []
    with open(file, encoding="utf-8") as f:
        return f.read().splitlines()


def holds(root: str, name: str, number: int, sentence: str, skill: bool = False) -> bool:
    """Whether the step of the number of the subagent, or of the skill where `skill`, still says
    the sentence, word for word."""
    lines = lines_of(root, name, skill)
    where = span(lines, number)
    return where is not None and sentence in says(lines, where)

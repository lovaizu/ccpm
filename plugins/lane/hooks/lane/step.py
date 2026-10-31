"""A subagent's step, read from the file its steps are in: its entry, the file in the plugin's
agents/ Claude Code takes the subagent from, by the name in its frontmatter, or the part the entry's
body has it read first, where it names one; and the step's text, its numbered line in the Steps and
the lines its text goes on in, the list under it, such as its In and Out, left out. An entry's body
also says where each script, file or folder its part names by name lies, which a lane taking the
name reads it by."""

from __future__ import annotations

import itertools
import os
import re
from typing import NamedTuple

import template

# A line that goes on a step's text: indented, and beginning no list item.
GOES_ON = re.compile(r"^[ \t]+(?![-*+] |\d+\. )\S")
# A line break, with the blanks around it, as a step's text reads it.
BREAK = re.compile(r"[ \t]*\n[ \t]*")
# What Claude Code puts the plugin's folder in for, where a subagent's file names it.
ROOT = "${CLAUDE_PLUGIN_ROOT}"
# Where an entry's body names a part, a file under the plugin's prompts/ by the plugin's folder, in
# backticks.
NAMED = re.compile(r"`" + re.escape(ROOT) + r"/prompts/(?P<path>[^`]+)`")
# Text in backticks, where a full stop, as in a file's name, ends no sentence.
QUOTED = re.compile(r"`[^`]*`")
# A sentence's end: a full stop, a question or an exclamation mark, before a blank or the end.
END = re.compile(r"[.?!](?=\s|$)")
# A blank line, which ends a paragraph.
BLANK = re.compile(r"\n[ \t]*\n")
# Where an entry's body says what a name its part uses stands for: "`<name>` below is `<text>`".
BINDS = re.compile(r"`(?P<name>[^`\s]+)` below is `(?P<text>[^`]+)`")


class Part(NamedTuple):
    """The part an entry has its subagent read first: its file in the plugin, and the entry's
    sentence naming it, as its body says it, a line break read as a space."""

    file: str
    said: str


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


def part(root: str, name: str) -> Part | None:
    """The part the subagent's entry names in its body, the one file under the plugin's prompts/ it
    names in backticks, with the sentence naming it; None where its body names no such file, or
    more than one, or no entry names the subagent."""
    paragraphs = body(root, name)
    found = [(p, m) for p in paragraphs for m in NAMED.finditer(p)]
    prompts = os.path.realpath(os.path.join(root, "prompts"))
    files = {os.path.realpath(os.path.join(prompts, m["path"])) for _, m in found}
    file = files.pop() if len(files) == 1 else ""
    if not file.startswith(prompts + os.sep):
        return None
    paragraph, m = found[0]
    # A full stop in backticks ends no sentence, so they are read blank.
    plain = QUOTED.sub(lambda q: "`" * len(q[0]), paragraph)
    start = max((e.end() for e in END.finditer(plain[: m.start()])), default=0)
    end = next((e.end() for e in END.finditer(plain, m.end())), len(paragraph))
    return Part(file, paragraph[start:end].strip())


def body(root: str, name: str) -> list[str]:
    """The paragraphs of the body of the subagent's entry, after its frontmatter, each line break
    read as a space; none where no entry names the subagent."""
    entry = agent_file(root, name)
    if entry is None:
        return []
    with open(entry, encoding="utf-8") as f:
        lines = f.read().splitlines()
    text = "\n".join(lines[template.body(lines) :])
    return [BREAK.sub(" ", p) for p in BLANK.split(text)]


def bindings(root: str, name: str) -> dict[str, str]:
    """What each name the subagent's part uses stands for, as its entry's body says it, such as
    `turn.py` for `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/turn.py"`; none where it says none, or no
    entry names the subagent."""
    return {m["name"]: m["text"] for p in body(root, name) for m in BINDS.finditer(p)}


def bound(takes: list[str], bindings: dict[str, str]) -> list[str]:
    """The takes as the entry's bindings give them: a take whose first word is a name bound, the
    name put in as it stands for, so a lane matches what the subagent runs or reads; every other
    take as it is."""
    found = []
    for take in takes:
        first, blank, rest = take.partition(" ")
        found.append(bindings[first] + blank + rest if first in bindings else take)
    return found


def steps_file(root: str, name: str) -> str | None:
    """The file the subagent's steps are read from, and the layer writes them into: the part its
    entry names, as `part` finds it, or the entry itself where it names none; None where no entry
    names the subagent."""
    named = part(root, name)
    return agent_file(root, name) if named is None else named.file


def span(lines: list[str], number: int) -> tuple[int, int] | None:
    """Where the step of the number is among the file's lines, from its numbered line in the Steps,
    the lines under the `## Steps` heading up to the next heading, as template reads headings, to
    the line after the last its text goes on in; None where the Steps have no such step."""
    found = template.headings(lines, template.body(lines))
    # A heading's line in the file counts from 1, so it is the index of the line after it, and the
    # next heading's line, the last the steps are looked for in, is no step's.
    start = next((at for at, level, said in found if (level, said) == (2, "Steps")), len(lines))
    end = next((at for at, _, _ in found if at > start), len(lines))
    for at in range(start, end):
        if lines[at].startswith(f"{number}. "):
            goes_on = itertools.takewhile(GOES_ON.match, lines[at + 1 :])
            return at, at + 1 + len(list(goes_on))
    return None


def says(lines: list[str], where: tuple[int, int]) -> str:
    """The step's text at where it is, each line break read as a space."""
    return BREAK.sub(" ", "\n".join(lines[where[0] : where[1]]))


def holds(root: str, name: str, number: int, sentence: str) -> bool:
    """Whether the subagent's step of the number still says the sentence, word for word."""
    file = steps_file(root, name)
    if file is None or not os.path.isfile(file):
        return False
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines()
    where = span(lines, number)
    return where is not None and sentence in says(lines, where)


def expanded(said: str, root: str) -> str:
    """The text as the subagent reads it from its entry, and as a lane finds the file it names: the
    plugin's folder put in where it names ROOT, as Claude Code gives a plugin subagent its entry's
    body, and nothing it reads or runs after."""
    return said.replace(ROOT, root)

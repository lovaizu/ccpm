"""A subagent's step, read from its file in the plugin's agents/: the file Claude Code takes the
subagent from, by the name in its frontmatter, and the step's text, its numbered line in the Steps
and the lines its text goes on in, the list under it, such as its In and Out, left out."""

from __future__ import annotations

import itertools
import os
import re

# The frontmatter, between the lines `---` that open the file and close it.
FRONT = re.compile(r"(?sm)\A---\n(?P<front>.*?)\n---$")
# The frontmatter's name, quoted or not.
NAME = re.compile(r"""^name:[ \t]*["']?(?P<name>.*?)["']?[ \t]*$""", re.MULTILINE)
# A line that goes on a step's text: indented, and beginning no list item.
GOES_ON = re.compile(r"^[ \t]+(?![-*+] |\d+\. )\S")
# A line break, with the blanks around it, as a step's text reads it.
BREAK = re.compile(r"[ \t]*\n[ \t]*")


def agent_file(root: str, name: str) -> str | None:
    """The file in the plugin's agents/ whose frontmatter names the subagent; None where none
    does."""
    folder = os.path.join(root, "agents")
    names = sorted(os.listdir(folder)) if os.path.isdir(folder) else []
    for file in (os.path.join(folder, n) for n in names if n.endswith(".md")):
        with open(file, encoding="utf-8") as f:
            front = FRONT.match(f.read())
        found = NAME.search(front["front"]) if front else None
        if found and found["name"] == name:
            return file
    return None


def span(lines: list[str], number: int) -> tuple[int, int] | None:
    """Where the step of the number is among the file's lines, from its numbered line in the Steps
    to the line after the last its text goes on in; None where the Steps have no such step."""
    start = lines.index("## Steps") if "## Steps" in lines else len(lines)
    for at in range(start + 1, len(lines)):
        if lines[at].startswith("#"):
            break
        if lines[at].startswith(f"{number}. "):
            goes_on = itertools.takewhile(GOES_ON.match, lines[at + 1 :])
            return at, at + 1 + len(list(goes_on))
    return None


def says(lines: list[str], where: tuple[int, int]) -> str:
    """The step's text at where it is, each line break read as a space."""
    return BREAK.sub(" ", "\n".join(lines[where[0] : where[1]]))


def holds(root: str, name: str, number: int, sentence: str) -> bool:
    """Whether the subagent's step of the number still says the sentence, word for word."""
    file = agent_file(root, name)
    if file is None:
        return False
    with open(file, encoding="utf-8") as f:
        lines = f.read().splitlines()
    where = span(lines, number)
    return where is not None and sentence in says(lines, where)

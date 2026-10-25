"""read_whole: the subagent reads an input its step names to its end before it writes, such as a
long instruction it would act on from its first part alone. It is held from the calls the subagent
made before: once it has begun reading the input, by any tool or command that reads, a write while a
line of it is left unread is a drift; a write before the input is begun is not, as the lane tells
the subagent to finish what it began, not when to begin."""

from __future__ import annotations

import os

import shell
from call import WRITERS, Call, file_text

ACTION = "read"
WORDING = "Read `<input>` to its end."
TOOLS = ("Bash", *WRITERS)


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call writes while an input taken, begun, has a line left unread, each input named
    from the folder the call is made in, where the guard stands."""
    if not writes(call):
        return False
    inputs = [i for i in (shell.path(os.getcwd(), t) for t in takes) if i]
    return any(left(i, call.before or []) for i in inputs)


def writes(call: Call) -> bool:
    """Whether the call writes a file: by a tool that writes, or by a command that writes a path but
    the null device, where the AI throws what it does not want to see."""
    by_tool = call.action == "write"  # pragma: no mutate
    return by_tool or any(p != os.devnull for p in call.written)


def left(file: str, before: list[Call]) -> bool:
    """Whether the calls before began reading the file and left a line of it unread; a file not
    there has none."""
    text = file_text(file)
    if text is None:
        return False
    count = len(text.splitlines())
    reads = [numbers(lines, count) for c in before for p, lines in c.reads if p == file]
    return bool(reads) and not set(range(1, count + 1)) <= set().union(*reads)


def numbers(lines: shell.Lines | None, count: int) -> set[int]:
    """The numbers of the lines read of a file of count lines; none where they are not known."""
    if lines is None:
        return set()
    first, last = lines
    start = count + first + 1 if first <= 0 else first
    return set(range(start, (count if last is None else last) + 1))

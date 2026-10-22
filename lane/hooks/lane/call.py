"""A tool call read as one action of a subagent's steps, the one a lane watches: begin, read, write,
run, test, hand on, wait or end. A Bash call is a run, of each command it runs, reading what they
print of what they read and writing what they write; a call of the Read or Grep tool is a read of
what it reads; a call of a tool that writes a file is a write of it; a call of a tool no lane of this
version reads is no action. A call that writes a file by the Write or Edit tool is read with the text
the file holds once it is written, for a lane on what is written. A call is read with each call its
subagent made before it, for a lane on the order of steps."""

from __future__ import annotations

import os
import re
from typing import Any, NamedTuple

import record
import shell

# The tools that write a file, each with the field of its input that names it.
WRITERS = {"Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path"}
# The tools that read a file or folder, each with the field of its input that names it, and what it
# reads where the field names none: the Grep tool searches the folder it runs in.
READ_TOOLS = {"Read": ("file_path", None), "Grep": ("path", ".")}
# A line of what the Read tool gives back: the line's number in the file, a tab, and its text.
NUMBERED = re.compile(r"^([0-9]+)\t", re.MULTILINE)


class Call(NamedTuple):
    """The action a call is, "" for none a lane watches, and what it acts on: for a run, each
    command, as its words; each file it writes, as its whole path; each file or folder it reads, as
    its whole path with the lines it reads of it, None where they are not known; each call its
    subagent made before it, read the same way, None where its record is not found; and the text
    the file it writes holds once written, None where the call does not tell it."""

    action: str
    what: list[list[str]]
    written: tuple[str, ...] = ()
    reads: tuple[tuple[str, shell.Lines | None], ...] = ()
    before: list[Call] | None = None
    text: str | None = None


def read(event: dict[str, Any]) -> Call:
    """The call of the PreToolUse event, read as its action, with each call its subagent made before
    it, from its record, and the text it writes."""
    done = record.done(event)
    before = None if done is None else [alone(d.tool, d.given, d.cwd, d.result) for d in done]
    tool, given, cwd = event["tool_name"], event["tool_input"], event["cwd"]
    return alone(tool, given, cwd)._replace(before=before, text=text(tool, given, cwd))


def text(tool: str, given: dict[str, Any], cwd: str) -> str | None:
    """The text the file a call of the tool with the input, made in the folder, holds once written:
    a Write's content; the file's text, none where it is not there, with an Edit's old_string
    replaced by its new_string, every one where replace_all is true; None where the input does not
    give it, or an Edit's old_string is not in the file, as the tool then writes nothing."""
    if tool in ("Write",):
        content = given.get("content")
        return content if isinstance(content, str) else None
    old, new = given.get("old_string"), given.get("new_string")
    if tool not in ("Edit",) or not isinstance(old, str) or not isinstance(new, str):
        return None
    try:
        named = os.path.join(cwd, str(given.get("file_path", "")))
        with open(named, encoding="utf-8", errors="replace") as f:
            before = f.read()
    except OSError:
        before = ""
    if old not in before:
        return None
    return before.replace(old, new) if given.get("replace_all") else before.replace(old, new, 1)


def alone(tool: str, given: dict[str, Any], cwd: str, result: str = "") -> Call:
    """The call of the tool with the input, made in the folder, read as its action without the calls
    before it; the lines it reads, where its input does not tell them, are those numbered in what
    it gave back, as the Read tool numbers them."""
    told = tuple(
        (p, shown(result) if lines is None else lines) for p, lines in reads(tool, given, cwd)
    )
    if tool in WRITERS:
        named = str(given.get(WRITERS[tool], ""))
        # A path is named from the folder the call is made in, as the tool takes it.
        file = os.path.realpath(os.path.join(cwd, named))
        return Call("write", [], (file,) if named else ())
    if tool in READ_TOOLS:
        return Call("read", [], (), told)
    if tool != "Bash":
        return Call("", [])
    command = str(given.get("command", ""))
    written = tuple(shell.written(command, cwd))
    return Call("run", list(runs(command, cwd)), written, told)


def runs(command: str, cwd: str) -> list[list[str]]:
    """Each command the shell command runs, in order, as its words, in the forms the steps tell and
    the AI writes: a cd is no command, a redirect and its target are no words, and git's own
    options before its command are left out, so `git -C notes commit` runs `git commit`."""
    found = []
    for here, said, _ in shell.statements(command, cwd):
        words = shell.without_redirects(said)
        if words[:1] == ["git"]:
            words = ["git", *shell.git_statement(here, words)[1]]
        found.append(words)
    return found


def reads(tool: str, given: dict[str, Any], cwd: str) -> list[tuple[str, shell.Lines | None]]:
    """Each file or folder a call of the tool with the input reads from the folder, with the lines
    it reads of it, None where the input does not tell them: by Bash, what its commands print of
    what they read; by the Read tool, its file; by the Grep tool, the path it searches, the folder
    it runs in where it names none."""
    if tool in ("Bash",):
        return shell.reads(str(given.get("command", "")), cwd)
    if tool not in READ_TOOLS:
        return []
    field, unnamed = READ_TOOLS[tool]
    named = given.get(field) or unnamed
    found = shell.path(cwd, named) if isinstance(named, str) else None
    return [(found, None)] if found else []


def shown(result: str) -> shell.Lines | None:
    """The lines from the first to the last numbered in what a call gave back; None where none is."""
    numbers = [int(n) for n in NUMBERED.findall(result)]
    return (min(numbers), max(numbers)) if numbers else None

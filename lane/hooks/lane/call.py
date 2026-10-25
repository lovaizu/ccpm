"""A tool call read as the action of a subagent's steps a lane watches, so every lane judges a call
the same way whatever tool makes it: a Bash call is a run of each command it runs, reading and
writing what they read and write; a Read or Grep call a read; a Write, Edit or NotebookEdit call a
write; an Agent or SendMessage call a hand-on of its text, as a reply that ended the subagent's
turn is; a call of any other tool no action."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, NamedTuple

import record
import shell
import step

# The tools that write a file, each with the field of its input that names it.
WRITERS = {"Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path"}
# The tools that read a file or folder, each with the field of its input that names it, and what it
# reads where the field names none: the Grep tool searches the folder it runs in.
READ_TOOLS = {"Read": ("file_path", None), "Grep": ("path", ".")}
# The tools that hand text on to another agent, each with the field of its input that holds the
# text: the Agent tool its prompt to the agent it starts, SendMessage its message to the agent it
# names.
HANDS = {"Agent": "prompt", "SendMessage": "message"}
# What hands text on, each with the field of its input that holds it: those tools, and a reply that
# ended the subagent's turn, as its record is read.
HANDED = {**HANDS, record.REPLY: record.SAID}
# What runs a script named after it, as the steps tell; a script may also be run by its path.
INTERPRETERS = (["python3"], ["sh"])
# How a step names a script of its plugin, by the plugin's folder Claude Code puts in.
PLUGIN = step.ROOT + "/"
# A line of what the Read tool gives back: the line's number in the file, a tab, and its text.
NUMBERED = re.compile(r"^([0-9]+)\t", re.MULTILINE)


class Call(NamedTuple):
    """The action a call is, "" for none a lane watches, and what it acts on: for a run, each
    command, as its words; each file it writes, as its whole path; each file or folder it reads, as
    its whole path with the lines it reads of it, None where they are not known; each call its
    subagent made before it, read the same way, None where its record is not found; and the text
    the file it writes holds once written, None where the call does not tell it. Read with its
    subagent's record, it holds too the tool and the input the AI gave it; of a call made before,
    what it gave back, whether it gave back an error and, for a run, what ends each command, the
    operator after it, such as `&&` or `|`, or a line's end after the last; of the call itself,
    each message that reached the subagent since it last asked, None where the record is not
    found."""

    action: str
    what: list[list[str]]
    written: tuple[str, ...] = ()
    reads: tuple[tuple[str, shell.Lines | None], ...] = ()
    before: list[Call] | None = None
    text: str | None = None
    tool: str = ""
    given: Mapping[str, Any] = MappingProxyType({})
    result: str = ""
    failed: bool = False
    ends: tuple[str, ...] = ()
    heard: list[str] | None = None


class End(NamedTuple):
    """How the subagent is about to end, from the SubagentStop event: each call it made, in order,
    read as its action, None where its record is not found; its last reply; and whether a stop
    hook told it something and it answered with words alone, making no call since."""

    made: list[Call] | None
    reply: str
    answered: bool


def read(event: dict[str, Any], found: list[dict[str, Any]] | None) -> Call:
    """The call of the PreToolUse event, read as its action, with the tool and the input the AI
    gave it, the text it writes, and, from the entries found of its subagent's record, None where
    it is not found, each call made before it and each message that reached the subagent since it
    last asked."""
    tool, given, cwd = event["tool_name"], event["tool_input"], event["cwd"]
    return alone(tool, given, cwd)._replace(
        before=None if found is None else [made(d) for d in record.done(found, cwd)],
        text=text(tool, given, cwd),
        tool=tool,
        given=given,
        heard=None if found is None else record.heard(found),
    )


def ended(event: dict[str, Any], found: list[dict[str, Any]] | None) -> End:
    """How the subagent of the SubagentStop event is about to end, from the event and the entries
    found of its record, None where it is not found."""
    calls = None if found is None else [made(d) for d in record.done(found, event["cwd"])]
    told = bool(event.get("stop_hook_active")) and record.answered(found or [])
    return End(calls, event.get("last_assistant_message") or "", told)


def made(done: record.Done) -> Call:
    """A call the subagent made, read from its record as its action, with the tool and the input the
    AI gave it, what it gave back, whether it failed and, for a run, what ends each command."""
    command = str(done.given.get("command", ""))
    ends = tuple(end for _, _, end in shell.statements(command, done.cwd))
    return alone(done.tool, done.given, done.cwd, done.result)._replace(
        tool=done.tool, given=done.given, result=done.result, failed=done.failed, ends=ends
    )


def text(tool: str, given: dict[str, Any], cwd: str) -> str | None:
    """The text the file a call of the tool with the input, made in the folder, holds once written:
    a Write's content; the file's text, none where it is not there, with an Edit's old_string
    replaced by its new_string, every one where replace_all is true; None where the input does not
    give it, or an Edit's old_string is not in the file, as the tool then writes nothing."""
    if tool == "Write":
        content = given.get("content")
        return content if isinstance(content, str) else None
    old, new = given.get("old_string"), given.get("new_string")
    if tool != "Edit" or not isinstance(old, str) or not isinstance(new, str):
        return None
    before = file_text(os.path.join(cwd, str(given.get("file_path", "")))) or ""
    if old not in before:
        return None
    return before.replace(old, new) if given.get("replace_all") else before.replace(old, new, 1)


def file_text(path: str) -> str | None:
    """The text of the file at the path, a byte that is no UTF-8 read as a mark of its own, as a
    lane reads what the subagent reads or writes; None where it cannot be read."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def changed(made: Call, file: str) -> bool:
    """Whether the call changed the file: wrote it, but by a tool that writes a file and gave back
    an error, which writes nothing; a command that failed may have written it before it failed."""
    by_tool = made.action == "write"  # pragma: no mutate
    return file in made.written and not (made.failed and by_tool)


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
    if tool in HANDED:
        return Call("hand on", [])
    if tool != "Bash":
        return Call("", [])
    command = str(given.get("command", ""))
    written = tuple(shell.written(command, cwd))
    return Call("run", commands(command, cwd), written, told)


def commands(command: str, cwd: str) -> list[list[str]]:
    """Each command the shell command runs, in order, as its words, in the forms the steps tell and
    the AI writes: a cd is no command, a redirect and its target are no words, the assignments
    and env before the program are left out, and git's own options before its command too, so
    `GIT_EDITOR=true git -C notes commit` runs `git commit`."""
    found = []
    for _, said, _ in shell.statements(command, cwd):
        words = shell.after_env(shell.without_redirects(said))
        if words[:1] == ["git"]:
            words = ["git", *shell.git_command(words)]
        found.append(words)
    return found


def runs(call: Call, takes: list[str]) -> bool:
    """Whether the call runs a command taken: a command of its run that `starts` holds to run one
    of them."""
    return any(starts(words, t) for words in call.what for t in takes)


def starts(words: list[str], take: str) -> bool:
    """Whether a command, as its words, runs the command taken, as a step writes it: the take read
    by the shell's words as a call's are, python3 or sh before each program left out, the program
    the take's by its path or a path ending in it, such as the plugin's folder put in for
    `${CLAUDE_PLUGIN_ROOT}` where the take begins with `${CLAUDE_PLUGIN_ROOT}/`, and the words after
    it beginning with the take's, so `git commit` runs in `git commit -m m` and not in
    `git commit-tree`; a take naming no program runs in no command."""
    taken = program(shell.words(take))
    if not taken:
        return False
    ran = program(words)
    path = ran[0] if ran else ""
    name, *after = taken
    name = name.removeprefix(PLUGIN)
    return (path == name or path.endswith("/" + name)) and ran[1:][: len(after)] == after


def program(words: list[str]) -> list[str]:
    """A command's words from its program on, python3 or sh before it left out."""
    return words[1:] if words[:1] in INTERPRETERS else words


def reads(tool: str, given: dict[str, Any], cwd: str) -> list[tuple[str, shell.Lines | None]]:
    """Each file or folder a call of the tool with the input reads from the folder, with the lines
    it reads of it, None where the input does not tell them: by Bash, what its commands print of
    what they read; by the Read tool, its file; by the Grep tool, the path it searches, the folder
    it runs in where it names none."""
    if tool == "Bash":
        return shell.reads(str(given.get("command", "")), cwd)
    if tool not in READ_TOOLS:
        return []
    field, unnamed = READ_TOOLS[tool]
    named = given.get(field) or unnamed
    found = shell.path(cwd, named) if isinstance(named, str) else None
    return [(found, None)] if found else []


def shown(result: str) -> shell.Lines | None:
    """The lines from the first to the last numbered in what a call gave back; None for none."""
    numbers = [int(n) for n in NUMBERED.findall(result)]
    return (min(numbers), max(numbers)) if numbers else None


def handed(call: Call) -> str:
    """The text a hand-on hands on, as the AI gave it; "" for a call that hands nothing on."""
    text = call.given.get(HANDED[call.tool], "") if call.action == "hand on" else ""
    return text if isinstance(text, str) else ""

"""Decides the form in which the guard takes each moment of a conversation, apart from the form of
Claude Code's hook events, which hook.py reads into it: who acts, what they do, and with what."""

from __future__ import annotations

from dataclasses import dataclass, field

# What a moment is.
TYPED = "typed"  # the person types a prompt, or a command of a plugin's skill expands
CALL = "call"  # the main conversation or a subagent calls a tool, before it runs
RAN = "ran"  # a call ran, and printed what it printed
BEGUN = "begun"  # a subagent began, from a start or a resume
ENDS = "ends"  # a subagent ends
REACHED = "reached"  # a subagent's end reaches the main conversation
TURN_ENDS = "turn_ends"  # the main conversation ends its turn
OTHER = "other"  # any other moment, which the guard lets pass

# What a call does.
COMMAND = "command"  # runs a shell command
WRITE = "write"  # writes or edits the file at a path
READ = "read"  # reads the file at a path
START = "start"  # starts a subagent in the background
RESUME = "resume"  # resumes a subagent, whose end came, with a message
STOP_TASK = "stop_task"  # stops a subagent that runs
SKILL = "skill"  # calls a plugin's skill in the person's place
ENTER = "enter"  # enters or leaves a worktree, which moves the folder the conversation works in
ELSE = "else"  # any other tool


@dataclass(frozen=True)
class Call:
    """One call of a tool, the data model's Call: `kind` is one of COMMAND to ELSE, `command` the
    shell command, `path` the file named, `role` the subagent's type that a start names,
    `<plugin>:<name>`, `agent` the subagent that a resume or a stop names, `text` a start's or a
    resume's text, `skill` the skill that a SKILL call names, `<plugin>:<skill>`, with `args`."""

    kind: str
    command: str = ""
    path: str = ""
    role: str = ""
    agent: str = ""
    text: str = ""
    skill: str = ""
    args: str = ""


@dataclass(frozen=True)
class Event:
    """One moment of the conversation: `moment` is one of TYPED to OTHER; `session` the
    conversation's ID; `cwd` the folder it works in; `root` the root of the repository; `agent` the
    acting subagent's ID and `role` its type as Claude Code names it, `<plugin>:<name>`, both "" for
    the main conversation; `call` the call, for CALL and RAN; `printed` what a call printed, and
    `failed` whether it gave other than 0, for RAN; `prompt` the typed prompt, `command` the
    plugin's command it expands, such as `changelog:write`, with `args`, for TYPED, which only a
    person makes; `message` the last message, for ENDS and TURN_ENDS, or the result of an end that
    REACHED tells, with `status`, `completed` or `killed`; `again` whether the guard stopped this
    subagent's end before; `running` the ID of each subagent that runs."""

    moment: str
    session: str
    cwd: str
    root: str
    agent: str = ""
    role: str = ""
    call: Call | None = None
    printed: str = ""
    failed: bool = False
    prompt: str = ""
    command: str = ""
    args: str = ""
    message: str = ""
    status: str = ""
    again: bool = False
    running: tuple[str, ...] = field(default_factory=tuple)

"""The double of Claude Code that overnight's cases run in its place, as overnight's Test strategy
says under Integration testing, Security testing, and Contract testing. It answers each run of
`claude -p ... --output-format stream-json --verbose` from the lines of a record in recorded/, as
the plugin guide's Each result of a double from a record says:

- Claude Code 2.1.331's runs: a session started with its own ID, one resumed by `--resume`, a
  resume of an ID that no session has, and a session in `dontAsk` mode denied each tool not
  allowed;
- of Claude Code's documentation: the words of the session and weekly limits, the rate limit event
  that rejects a request, a server error, and what the sandbox and `dontAsk` let a session do.

No run of the real thing at the usage limit is recorded yet, as the limit can't be reached at will.
So a session that the limit stops gives the stream of the recorded run, its rejected rate limit
event, and a result with `is_error` true and the documentation's words. Contract testing records a
real one, apart from the work.

A case scripts what each task's sessions do, by the text of the task's prompt: each run's end,
`finished`, `limited` with its reset, `failed` on a server error, and what the session uses on the
way, each tool with the path it writes or the shell command it runs. The double finds the task of a
run by its prompt's text, or by the session that `--resume` names, takes the task's next answer, and
gives the reply's text that the case scripted in the recorded run's place. It decides each use by
the arguments, as the documentation says Claude Code does: the tools that `--tools` gives, the
rules of `--allowedTools` and `--disallowedTools`, `--permission-mode`, and the sandbox of
`--settings`. It writes each file that a use allowed writes, so that a case reads what a task
wrote, and refuses each other use, as `dontAsk` denies it. A run that no record holds, such as one
with another output form, fails with exit 1, naming what it lacks, so that a body that runs it
shows the gap.

It serves two ways in: `function`, a stand-in for `session.claude.claude` in the case's own
process, which also moves the double of the computer's clock to the end that the case scripted; and
`program`, a `claude` written into a folder, put first on the PATH of a runner that runs apart. Each
keeps the case's script, and each run it was asked, in the folder it's given."""

from __future__ import annotations

import copy
import fnmatch
import functools
import json
import os
import threading
import time
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import stand_in

RECORDED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded")
RUN = "claude-2.1.331-print.jsonl"
DOCUMENTATION = "claude-documentation.jsonl"
STARTED = "claude -p starts a session of its own ID and answers"
RESUMED = "claude -p --resume goes on in the session and answers"
NO_SESSION = "claude -p --resume finds no session of the ID"
DENIED = "claude -p in dontAsk mode denies each tool not allowed and answers"
SESSION_LIMIT = "claude -p stops at the session limit"
WEEKLY_LIMIT = "claude -p stops at the weekly limit"
REJECTED = "claude -p tells the rate limit that rejected its request"
SERVER_ERROR = "claude -p ends on a server error"
# The ID that the recorded resume of no session names.
NO_ID = "00000000-0000-4000-8000-000000000000"
# The files of the double's state in the folder it's given: the script, and each run it was asked.
SCRIPT = "claude-script.json"
ASKED = "claude-asked.jsonl"
# The options of `claude` that the double reads, each with how many values it takes, `*` for each
# word up to the next option, as Claude Code's own parser takes a list.
OPTIONS = {
    "-p": 0,
    "--print": 0,
    "--verbose": 0,
    "--output-format": 1,
    "--session-id": 1,
    "--resume": 1,
    "-r": 1,
    "--permission-mode": 1,
    "--settings": 1,
    "--model": 1,
    "--append-system-prompt": 1,
    "--dangerously-skip-permissions": 0,
    "--tools": "*",
    "--allowedTools": "*",
    "--allowed-tools": "*",
    "--disallowedTools": "*",
    "--disallowed-tools": "*",
    "--add-dir": "*",
}
# The tools that only read, which need no approval within the session's folder.
READS = ("Read", "Grep", "Glob")
# The tools that edit files.
EDITS = ("Edit", "Write", "NotebookEdit")
_WRITING = threading.Lock()


@functools.cache
def _record(record: str) -> tuple[dict[str, Any], ...]:
    with open(os.path.join(RECORDED, record), encoding="utf-8") as f:
        return tuple(json.loads(each) for each in f)


def line(record: str, event: str) -> dict[str, Any]:
    """A copy of the line of the record in recorded/ that the event names."""
    return copy.deepcopy(next(each for each in _record(record) if each["event"] == event))


@dataclass(frozen=True)
class Use:
    """One use of a tool on the way: the tool, the absolute path it writes or reads, or None, and
    the shell command it runs, or None."""

    tool: str
    path: str | None = None
    command: str | None = None


@dataclass(frozen=True)
class Answer:
    """How one run of a task's session ends: `finished`, `limited`, or `failed`; the reply's text;
    the moment it ends at on the clock, or None to leave the clock; for `limited`, the moment the
    limit resets and whether it's the weekly limit; each use on the way; and how many seconds the
    run takes, so that a case sees which runs are at work at once."""

    end: str
    reply: str = ""
    ends: datetime | None = None
    reset: datetime | None = None
    weekly: bool = False
    uses: tuple[Use, ...] = ()
    seconds: float = 0.0


def finished(reply: str, ends: datetime | None = None, **more: Any) -> Answer:
    """A run that answers with the reply."""
    return Answer("finished", reply, ends, **more)


def limited(reply: str, ends: datetime, reset: datetime, **more: Any) -> Answer:
    """A run that the usage limit stops at `ends`, with its reply so far, until `reset`."""
    return Answer("limited", reply, ends, reset, **more)


def failed(reply: str = "", ends: datetime | None = None, **more: Any) -> Answer:
    """A run that a server error ends, with its reply so far."""
    return Answer("failed", reply, ends, **more)


@dataclass
class Asked:
    """One run the double was asked: the task's prompt's text, the session's ID, the arguments, the
    folder it ran in, its answer's end, each use with whether it was allowed, and the moments of the
    computer's own clock at which it started and ended."""

    prompt: str
    session: str
    arguments: list[str]
    cwd: str
    end: str
    uses: list[dict[str, Any]] = field(default_factory=list)
    started: float = 0.0
    ended: float = 0.0


def script(folder: str, prompt: str, *answers: Answer) -> None:
    """Sets what the sessions of the task whose prompt's text is `prompt` do, run by run."""
    kept = _script(folder)
    kept["tasks"][prompt] = [_encode(each) for each in answers]
    _keep(folder, kept)


def had(folder: str, prompt: str, session: str) -> None:
    """Sets the session as one that the task of the prompt ran in before the case, such as on an
    earlier night, which Claude Code keeps, so that `--resume` goes on in it."""
    kept = _script(folder)
    kept["sessions"][session] = prompt
    _keep(folder, kept)


def temporary(folder: str) -> str:
    """Claude Code's per-user temporary folder, where a sandboxed command may write, which the
    double keeps in its state folder, as the cases' own folders lie in the computer's."""
    return os.path.join(folder, "tmp")


def no_sandbox(folder: str) -> None:
    """Sets the computer to one where Claude Code's sandbox can't start, such as Windows outside
    WSL2."""
    kept = _script(folder)
    kept["sandbox_runs"] = False
    _keep(folder, kept)


def _keep(folder: str, kept: dict[str, Any]) -> None:
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, SCRIPT), "w", encoding="utf-8") as f:
        json.dump(kept, f)


def asked(folder: str) -> list[Asked]:
    """Each run the double was asked, in the order each started."""
    path = os.path.join(folder, ASKED)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        runs = [Asked(**json.loads(each)) for each in f]
    return sorted(runs, key=lambda each: each.started)


def at_once(folder: str) -> int:
    """The most runs that were at work at the same moment."""
    moments = sorted(
        [(each.started, 1) for each in asked(folder)] + [(each.ended, -1) for each in asked(folder)]
    )
    most = now = 0
    for _, step in moments:
        now += step
        most = max(most, now)
    return most


def answer(arguments: Sequence[str], cwd: str, folder: str) -> tuple[int, str, str, Answer | None]:
    """The exit code, stdout, and stderr of `claude` with the arguments, run in `cwd`, by the script
    in the folder, and the answer it gave, None where it gave none."""
    flags, prompt, wrong = parsed(arguments)
    kept = _script(folder)
    settings = _settings(flags) if wrong is None else {}
    wrong = wrong or _unrecorded(flags, settings, kept)
    if wrong:
        return 1, "", f"{wrong}\n", None
    resumed = _first(flags, "--resume", "-r")
    runs = asked(folder)
    task = _task_of(prompt, resumed, kept, runs)
    if task is None and resumed is not None:
        return _no_session(resumed)
    done = [each for each in runs if each.prompt == task]
    if task is None or len(done) >= len(kept["tasks"][task]):
        return 1, "", "the double's script holds no such run of a task\n", None
    given = _decode(kept["tasks"][task][len(done)])
    session = resumed or _first(flags, "--session-id") or str(uuid.uuid4())
    this = Asked(task, session, list(arguments), cwd, given.end, started=time.monotonic())
    allowed = _permitted(flags, settings, kept["sandbox_runs"], cwd, temporary(folder))
    for use in given.uses:
        this.uses.append({**use.__dict__, "allowed": allowed(use)})
        if this.uses[-1]["allowed"] and use.path and use.tool not in READS:
            _write(use.path, task)
    time.sleep(given.seconds)
    this.ended = time.monotonic()
    _log(folder, this)
    out = _stream(given, session, this.uses, resumed is not None)
    return (0 if given.end == "finished" else 1), out, "", given


def _unrecorded(
    flags: dict[str, list[str]], settings: dict[str, Any], kept: dict[str, Any]
) -> str | None:
    """What keeps the double from answering the run from its records, or Claude Code from starting
    it, None where nothing does."""
    if "-p" not in flags and "--print" not in flags:
        return "the double answers only claude -p"
    if flags.get("--output-format") != ["stream-json"] or "--verbose" not in flags:
        return "the double holds only runs of --output-format stream-json --verbose"
    sandbox = settings.get("sandbox", {})
    if sandbox.get("enabled") and not kept["sandbox_runs"] and sandbox.get("failIfUnavailable"):
        return "Error: sandbox required but unavailable"
    return None


def _task_of(
    prompt: str, resumed: str | None, kept: dict[str, Any], runs: list[Asked]
) -> str | None:
    """The prompt of the task that the run is of: of the session it resumes, from a run before or
    one set by `had`, or of the task whose prompt it runs; None where no task is."""
    if resumed is not None:
        earlier = [each.prompt for each in runs if each.session == resumed]
        return (earlier or [kept["sessions"].get(resumed)])[0]
    return next((each for each in kept["tasks"] if each in prompt), None)


def allows(arguments: Sequence[str], cwd: str, use: Use, sandbox_runs: bool = True) -> bool:
    """Whether a session run with the arguments in `cwd` may make the use, as `answer` decides it,
    with Claude Code's temporary folder in the computer's own: none where Claude Code doesn't start
    the session."""
    flags, _, wrong = parsed(arguments)
    assert wrong is None, wrong
    settings = _settings(flags)
    if _unrecorded(flags, settings, {"sandbox_runs": sandbox_runs}):
        return False
    tmp = os.path.join(os.path.realpath(os.sep), "tmp", "claude")
    return _permitted(flags, settings, sandbox_runs, cwd, tmp)(use)


def function(
    folder: str, clock: Any = None, before: list[Callable[[], None]] | None = None
) -> Callable[[Sequence[str], str], Any]:
    """A stand-in for `session.claude.claude`, which answers as `answer` does by the script in the
    folder, after calling each of `before`, and moves the clock, where it's given, to the end that
    the case scripted."""
    from session.claude import Output

    def claude(arguments: Sequence[str], cwd: str) -> Output:
        for each in before or []:
            each()
        code, out, err, given = answer(arguments, cwd, folder)
        if clock is not None and given is not None and given.ends is not None:
            clock.passes_to(given.ends)
        return Output(code, out, err)

    return claude


def program(bin_folder: str, state_folder: str) -> str:
    """Writes `claude` into the bin folder, a program that answers as `answer` does with its state
    in the state folder, and gives the bin folder."""
    call = f"claude_double.answer(sys.argv[1:], os.getcwd(), {state_folder!r})"
    return stand_in.program(bin_folder, "claude", os.path.abspath(__file__), call)


def _script(folder: str) -> dict[str, Any]:
    path = os.path.join(folder, SCRIPT)
    if not os.path.exists(path):
        return {"tasks": {}, "sessions": {}, "sandbox_runs": True}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _encode(given: Answer) -> dict[str, Any]:
    kept = dict(given.__dict__)
    kept["uses"] = [each.__dict__ for each in given.uses]
    for moment in ("ends", "reset"):
        kept[moment] = kept[moment].isoformat() if kept[moment] else None
    return kept


def _decode(kept: dict[str, Any]) -> Answer:
    given = dict(kept)
    given["uses"] = tuple(Use(**each) for each in kept["uses"])
    for moment in ("ends", "reset"):
        given[moment] = datetime.fromisoformat(kept[moment]) if kept[moment] else None
    return Answer(**given)


def _log(folder: str, this: Asked) -> None:
    with _WRITING, open(os.path.join(folder, ASKED), "a", encoding="utf-8") as f:
        f.write(json.dumps(this.__dict__) + "\n")


def _write(path: str, task: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"written by the session of {task[:40]!r}\n")


class _Unparsed(Exception):
    """What Claude Code's parser finds wrong with the arguments."""


def parsed(arguments: Sequence[str]) -> tuple[dict[str, list[str]], str, str | None]:
    """Each option of the arguments of `claude` with its values, the prompt, which is the word that
    no option takes, and what's wrong with them, None where nothing is, as Claude Code's parser
    takes them."""
    flags: dict[str, list[str]] = {}
    words: list[str] = []
    rest = list(arguments)
    try:
        while rest:
            word = rest.pop(0)
            if word == "--":
                words += rest
                break
            if not word.startswith("-") or word == "-":
                words.append(word)
                continue
            name, _, inline = word.partition("=")
            values = _values(name, inline, rest)
            flags.setdefault(name, []).extend(values)
    except _Unparsed as wrong:
        return flags, "", str(wrong)
    if len(words) != 1:
        return flags, "", f"one prompt, where the arguments give {len(words)}"
    return flags, words[0], None


def _values(name: str, inline: str, rest: list[str]) -> list[str]:
    """The values of the option `name`, its own after `=` where it has one, taken from the front of
    `rest` as OPTIONS says the option takes them."""
    if name not in OPTIONS:
        raise _Unparsed(f"unknown option '{name}'")
    takes = OPTIONS[name]
    values = [inline] if inline else []
    if takes == "*":
        while rest and not rest[0].startswith("-"):
            values.append(rest.pop(0))
    elif takes and not values:
        if not rest:
            raise _Unparsed(f"option '{name}' argument missing")
        values.append(rest.pop(0))
    return values


def _first(flags: dict[str, list[str]], *names: str) -> str | None:
    for name in names:
        if flags.get(name):
            return flags[name][0]
    return None


def _settings(flags: dict[str, list[str]]) -> dict[str, Any]:
    given = _first(flags, "--settings")
    if given is None:
        return {}
    if given.lstrip().startswith("{"):
        return json.loads(given)
    with open(given, encoding="utf-8") as f:
        return json.load(f)


def _names(values: list[str]) -> list[str]:
    """Each rule of a list option, split at commas and spaces outside parentheses."""
    rules, depth, word = [], 0, ""
    for char in " ".join(values):
        depth += {"(": 1, ")": -1}.get(char, 0)
        if char in ", " and depth == 0:
            rules, word = rules + [word] * bool(word), ""
        else:
            word += char
    return rules + [word] * bool(word)


def _matches(rule: str, use: Use, cwd: str) -> bool:
    """Whether a permission rule, such as `Bash`, `Bash(pytest *)`, or `Edit(//abs/dir/**)`,
    covers the use."""
    tool, _, spec = rule.partition("(")
    if tool != use.tool:
        return False
    if not spec:
        return True
    spec = spec[:-1]
    if use.tool == "Bash":
        return fnmatch.fnmatchcase(use.command or "", spec.replace(":*", " *"))
    if use.path is None:
        return False
    if spec.startswith("//"):
        pattern = "/" + spec.lstrip("/")
    elif spec.startswith("~/"):
        pattern = os.path.expanduser(spec)
    else:
        pattern = os.path.join(cwd, spec.lstrip("/"))
    return fnmatch.fnmatchcase(use.path, pattern.replace("**", "*")) or use.path == pattern.rstrip(
        "/*"
    )


def _within(path: str, folders: list[str]) -> bool:
    real = os.path.realpath(path)
    return any(
        os.path.commonpath([real, os.path.realpath(each)]) == os.path.realpath(each)
        for each in folders
    )


def _permitted(
    flags: dict[str, list[str]], settings: dict[str, Any], sandbox_runs: bool, cwd: str, tmp: str
) -> Callable[[Use], bool]:
    """Whether Claude Code lets the session make each use, by the arguments, its settings, whether
    the sandbox runs on the computer, its folder, and Claude Code's temporary folder."""
    folders = [cwd, *flags.get("--add-dir", [])]
    sandbox = settings.get("sandbox", {})
    mode = _first(flags, "--permission-mode") or "default"
    return _Permissions(
        tools=_names(flags["--tools"]) if "--tools" in flags else None,
        allow=_names(flags.get("--allowedTools", []) + flags.get("--allowed-tools", [])),
        deny=_names(flags.get("--disallowedTools", []) + flags.get("--disallowed-tools", [])),
        mode=mode,
        bypass=mode == "bypassPermissions" or "--dangerously-skip-permissions" in flags,
        cwd=cwd,
        folders=folders,
        sandbox=sandbox,
        sandboxed=bool(sandbox.get("enabled")) and sandbox_runs,
        writable=folders + [tmp] + sandbox.get("filesystem", {}).get("allowWrite", []),
    ).allows


@dataclass(frozen=True)
class _Permissions:
    """What the arguments let a session do: the tools that `--tools` gives, or None for all, the
    rules of `--allowedTools` and `--disallowedTools`, the permission mode, whether every check is
    bypassed, the session's folder and the folders it may read and edit, the sandbox's settings,
    whether the sandbox holds its commands, and the folders a sandboxed command may write."""

    tools: list[str] | None
    allow: list[str]
    deny: list[str]
    mode: str
    bypass: bool
    cwd: str
    folders: list[str]
    sandbox: dict[str, Any]
    sandboxed: bool
    writable: list[str]

    def allows(self, use: Use) -> bool:
        """Whether Claude Code lets the use: a tool that `--tools` doesn't give, or that a rule of
        `--disallowedTools` names, is refused; a bypass lets each other; a read in the session's
        folders, a rule of `--allowedTools`, an edit in its folders under `acceptEdits`, and a
        shell command that the sandbox holds, each let it; and each other use is denied, as
        `dontAsk` denies it, and as `-p` denies a call that would wait for approval."""
        if self.tools is not None and use.tool not in self.tools:
            return False
        if self._ruled(self.deny, use):
            return False
        permitted = self.bypass or self._ruled(self.allow, use)
        if use.tool == "Bash":
            return self._shell(use, permitted)
        if permitted:
            return True
        inside = use.path is not None and _within(use.path, self.folders)
        return inside and (use.tool in READS or (use.tool in EDITS and self.mode == "acceptEdits"))

    def _ruled(self, rules: list[str], use: Use) -> bool:
        return any(_matches(rule, use, self.cwd) for rule in rules)

    def _shell(self, use: Use, permitted: bool) -> bool:
        """Whether a shell command runs: outside a sandbox, where a rule or a bypass lets it; in
        one, where it writes only where the sandbox lets it, which runs it with no rule unless
        `autoAllowBashIfSandboxed` is false, or where it may retry outside and a rule lets it,
        the sandbox refusing a write outside its folders otherwise."""
        if not self.sandboxed:
            return permitted
        if use.path is None or _within(use.path, self.writable):
            return permitted or self.sandbox.get("autoAllowBashIfSandboxed", True)
        return permitted and self.sandbox.get("allowUnsandboxedCommands", True)


def _no_session(session: str) -> tuple[int, str, str, Answer | None]:
    """The recorded run of a resume that finds no session, with the ID that it names."""
    given = line(RUN, NO_SESSION)
    recorded = given["stdout"].replace(NO_ID, session)
    return given["exit"], recorded, given["stderr"].replace(NO_ID, session), None


def _stream(given: Answer, session: str, uses: list[dict[str, Any]], resumed: bool) -> str:
    """The stream of the recorded run, with the session's ID, the scripted reply in its text, each
    use refused as `dontAsk` denies it, and the end that the answer scripts."""
    recorded = (line(RUN, RESUMED) if resumed else line(RUN, STARTED))["stdout"].splitlines()
    denial = [json.loads(each) for each in line(RUN, DENIED)["stdout"].splitlines()]
    denied_line = next(each for each in denial if each.get("subtype") == "permission_denied")
    lines = [json.loads(each) for each in recorded]
    init, assistant, rate, result = lines[0], lines[1], lines[2], lines[-1]
    shown: list[dict[str, Any]] = [init]
    refused = [each for each in uses if not each["allowed"]]
    for each in refused:
        shown.append(dict(denied_line, tool_name=each["tool"], message=f"{each['tool']} denied"))
    if given.reply:
        text = copy.deepcopy(assistant)
        text["message"]["content"] = [{"type": "text", "text": given.reply}]
        shown.append(text)
    result = copy.deepcopy(result)
    result["permission_denials"] = [
        {"tool_name": each["tool"], "tool_use_id": f"toolu_{n}", "tool_input": {}}
        for n, each in enumerate(refused)
    ]
    if given.end == "limited":
        assert given.reset is not None
        rejected = copy.deepcopy(rate)
        rejected["rate_limit_info"] = dict(
            line(DOCUMENTATION, REJECTED)["rate_limit_info"], resetsAt=int(given.reset.timestamp())
        )
        shown.append(rejected)
        words = (
            line(DOCUMENTATION, WEEKLY_LIMIT)
            if given.weekly
            else line(DOCUMENTATION, SESSION_LIMIT)
        )
        result.update(is_error=True, result=_limit(words["result"], given.reset, given.weekly))
        result.update(api_error_status=words["api_error_status"])
    elif given.end == "failed":
        shown.append(rate)
        words = line(DOCUMENTATION, SERVER_ERROR)
        result.update(is_error=True, result=words["result"])
        result.update(api_error_status=words["api_error_status"])
    else:
        shown.append(rate)
        result["result"] = given.reply
    shown.append(result)
    for each in shown:
        each["session_id"] = session
    return "".join(json.dumps(each, ensure_ascii=False) + "\n" for each in shown)


def _limit(words: str, reset: datetime, weekly: bool) -> str:
    """The documentation's words of the limit, with the reset as Claude Code shows it, such as
    `3:45pm`, or `Mon 12:00am` for the weekly limit, on the reset's own clock."""
    hour = reset.hour % 12 or 12
    shown = f"{hour}:{reset.minute:02d}{'am' if reset.hour < 12 else 'pm'}"
    if weekly:
        shown = f"{reset:%a} {shown}"
    head, _, _ = words.rpartition(" resets ")
    return f"{head} resets {shown}"

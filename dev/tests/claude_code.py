"""The double of Claude Code that Lane's integration tests run in its place, as Lane's architecture
says under Test strategy. It sends each hook event of one conversation in the form that the recorded
run of Claude Code 2.1.322 in recorded/claude-code-2.1.322.jsonl shows, runs each matching entry of
each plugin's hooks/hooks.json, reads what the entry gives as Claude Code's hooks reference says,
and runs each tool call that the hooks let through, a Bash command with the environment that
recorded/claude-code-2.1.322-bash-environment.jsonl shows. A hook entry whose command isn't on the
PATH fails as recorded/claude-code-2.1.322-hook-failures.jsonl shows, and an entry in shell form
runs in /bin/sh, as that record shows. /compact sends the events that
recorded/claude-code-2.1.322-compact.jsonl shows, in the same conversation, a call of the Skill tool
the events that recorded/claude-code-2.1.322-skill.jsonl shows, and a subagent resumed by
SendMessage the events that recorded/claude-code-2.1.322-send-message.jsonl shows. An Edit, which no
record holds, carries the input that the hooks reference gives it. A subagent's start of a subagent
sends the main conversation's start with the subagent's `agent_id` and `agent_type`, as each other
call of a subagent carries them, and as the end-to-end test's record of Claude Code 2.1.322 shows at
line 71 of the hooks.jsonl of its changelog run 20261112T054832Z, which commit eb093f4c holds. A
subagent stopped by TaskStop sends the events that recorded/claude-code-2.1.323-task-stop.jsonl
shows, a command that a skill's SKILL.md runs as the skill loads runs as
recorded/claude-code-2.1.323-skill-command.jsonl shows, and fails on a typed command as
recorded/claude-code-2.1.323-skill-command-fails.jsonl shows, and EnterWorktree and ExitWorktree
move the conversation's folder as recorded/claude-code-2.1.323-worktree.jsonl shows, each a record
of Claude Code 2.1.323, as LATER says. A test plays the person, the main conversation, and each
subagent by the calls it makes on the double. Lane's tests and rn's tests share it."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import re
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile
import traceback
import uuid
from dataclasses import dataclass, field
from typing import Any

RECORDED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded")
VERSION = "2.1.322"
# The version of the records of what 2.1.322's records don't hold: TaskStop, a skill's command run
# as the skill loads, and EnterWorktree. Each event of `claude -p` that both versions' records hold
# carries the same fields in each, save `bashEditDiff` in the response of one Bash call of 2.1.323,
# so the double sends the others as 2.1.322's records show.
LATER = "2.1.323"

# The events whose plain standard output Claude Code adds to what the model reads, and those that
# take a top-level decision, as the hooks reference says.
CONTEXT_FROM_STDOUT = {"UserPromptSubmit", "UserPromptExpansion", "SessionStart"}
TOP_LEVEL_DECISION = {
    "UserPromptSubmit",
    "UserPromptExpansion",
    "PostToolUse",
    "Stop",
    "SubagentStop",
}
# The events whose exit 2 stops what it follows. On the others, the hooks reference shows stderr to
# the user only, or to Claude once the tool already ran.
BLOCKED_BY_EXIT_2 = {
    "PreToolUse",
    "UserPromptSubmit",
    "UserPromptExpansion",
    "Stop",
    "SubagentStop",
}
# The events on which onFailure has no effect.
NO_ON_FAILURE = {"Stop", "SubagentStop"}
# The events that a matcher filters, and the field of the payload it matches.
MATCHED = {
    "PreToolUse": "tool_name",
    "PostToolUse": "tool_name",
    "PostToolUseFailure": "tool_name",
    "SubagentStart": "agent_type",
    "SubagentStop": "agent_type",
    "SessionStart": "source",
    "PreCompact": "trigger",
    "PostCompact": "trigger",
}


def recorded(version: str = VERSION) -> dict[str, dict[str, Any]]:
    """Each payload of the recorded run, by the name of its event in the record."""
    path = os.path.join(RECORDED, f"claude-code-{version}.jsonl")
    with open(path, encoding="utf-8") as f:
        return {r["event"]: r["payload"] for r in map(json.loads, f)}


def compaction(version: str = VERSION) -> list[tuple[str, dict[str, Any]]]:
    """Each event that /compact sends, by its name in the record, in the order of the record of a
    conversation compacted between two runs of a skill: from PreCompact to PostCompact."""
    path = os.path.join(RECORDED, f"claude-code-{version}-compact.jsonl")
    with open(path, encoding="utf-8") as f:
        records = [(r["event"], r["payload"]) for r in map(json.loads, f)]
    names = [name for name, _ in records]
    first = names.index("the person compacts the conversation")
    return records[first : names.index("the conversation is compacted") + 1]


def skill_call(version: str = VERSION) -> dict[str, dict[str, Any]]:
    """Each payload of the record of a conversation in which the main conversation called a
    plugin's skill by the Skill tool, by the name of its event in the record."""
    path = os.path.join(RECORDED, f"claude-code-{version}-skill.jsonl")
    with open(path, encoding="utf-8") as f:
        return {r["event"]: r["payload"] for r in map(json.loads, f)}


def send_message(version: str = VERSION) -> dict[str, dict[str, Any]]:
    """Each payload of the record of a conversation in which the main conversation started a
    subagent in the background, and resumed it by SendMessage once its end reached the main
    conversation, by the name of its event in the record."""
    path = os.path.join(RECORDED, f"claude-code-{version}-send-message.jsonl")
    with open(path, encoding="utf-8") as f:
        return {r["event"]: r["payload"] for r in map(json.loads, f)}


def lines_of(record: str, version: str = LATER) -> dict[str, dict[str, Any]]:
    """Each line of the record claude-code-<version>-<record>.jsonl, by the name of its event. The
    line of a hook event holds its `payload`. The line of a call that no hook saw holds `hooks`
    empty, with what the call gave."""
    path = os.path.join(RECORDED, f"claude-code-{version}-{record}.jsonl")
    with open(path, encoding="utf-8") as f:
        return {r["event"]: r for r in map(json.loads, f)}


def bash_environment(session_id: str, version: str = VERSION) -> dict[str, str]:
    """What Claude Code adds to the environment of each Bash command of the conversation, of the
    main conversation and of a subagent alike, as the record shows. In the record, `session_id` is
    the ID of the conversation's transcript, which the hook payloads of the conversation carry as
    their `session_id`, a subagent's among them."""
    path = os.path.join(RECORDED, f"claude-code-{version}-bash-environment.jsonl")
    added: dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        for record in map(json.loads, f):
            for name, value in record["environment"].items():
                added[name] = value.replace("<session_id>", session_id)
    return added


@dataclass
class Answer:
    """What came of one event: whether a hook stopped it, what the model reads from the hooks, and,
    for a tool call that ran, its exit code and output."""

    blocked: bool = False
    said: str = ""
    exit_code: int | None = None
    output: str = ""
    ran: list[str] = field(default_factory=list)
    # What Claude Code shows the person in place of a reply of the model, which it never calls,
    # where a command of a typed skill's SKILL.md fails as the skill loads.
    shown: str = ""


class SkillCommandFailed(Exception):
    """A command that a skill's SKILL.md runs as the skill loads gave other than 0, with what
    Claude Code says of it, as recorded/claude-code-2.1.323-skill-command-fails.jsonl shows."""


@dataclass
class Plugin:
    """A plugin that the conversation runs with, as `claude --plugin-dir <root>` loads it."""

    root: str
    name: str
    hooks: dict[str, list[dict[str, Any]]]

    @classmethod
    def load(cls, root: str) -> Plugin:
        """The plugin in the folder, with the hook entries that its hooks/hooks.json holds as the
        conversation starts, as Claude Code reads them then."""
        with open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            name = json.load(f)["name"]
        path = os.path.join(root, "hooks", "hooks.json")
        hooks: dict[str, list[dict[str, Any]]] = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                hooks = json.load(f).get("hooks", {})
        return cls(os.path.realpath(root), name, hooks)


def matches(matcher: str | None, value: str) -> bool:
    """Whether a hook's matcher takes the value, as the hooks reference says: all on `*`, empty, or
    none; exact names split by `|` or `,` where the matcher holds only letters, digits, `_`, `-`,
    spaces, `,`, and `|`; and else an unanchored regular expression."""
    if matcher in (None, "", "*"):
        return True
    if re.fullmatch(r"[A-Za-z0-9_\- ,|]*", matcher):
        return value in {m.strip() for m in re.split(r"[|,]", matcher)}
    return re.search(matcher, value) is not None


def run_python(script: str, args: list[str], stdin: str, env: dict[str, str], cwd: str):
    """Runs the script in this process as `python3 <script> <args>` would in a new one, with the
    standard input, the environment, and the folder given, and gives its exit code, standard output,
    and standard error. The modules it imports go once it ends, as they would with its process."""
    out, err = io.StringIO(), io.StringIO()
    if not os.path.isfile(script):
        err.write(f"python3: can't open file '{script}': [Errno 2] No such file or directory\n")
        return 2, "", err.getvalue()
    argv, path, environ, folder = sys.argv, sys.path[:], dict(os.environ), os.getcwd()
    modules, stdin_before, tempdir = set(sys.modules), sys.stdin, tempfile.tempdir
    no_cache = sys.dont_write_bytecode
    code = 0
    try:
        # A new process decodes its arguments into strings of its own, which are never the constants
        # of the code it runs, so a comparison by `is` in place of `==` fails there as here.
        sys.argv = [script, *(str(a.encode("utf-8"), "utf-8") for a in args)]
        sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
        os.environ.clear()
        os.environ.update(env)
        os.chdir(cwd)
        tempfile.tempdir = None
        sys.stdin = io.StringIO(stdin)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                runpy.run_path(script, run_name="__main__")
            except SystemExit as e:
                if e.code is None or isinstance(e.code, int):
                    code = e.code or 0
                else:
                    print(e.code, file=sys.stderr)
                    code = 1
            except Exception:  # noqa: BLE001 - a new process prints any other error and exits 1.
                traceback.print_exc()
                code = 1
    finally:
        sys.argv, sys.path[:], sys.stdin = argv, path, stdin_before
        os.environ.clear()
        os.environ.update(environ)
        os.chdir(folder)
        tempfile.tempdir = tempdir
        # A script's setting of its own process goes with its run.
        sys.dont_write_bytecode = no_cache
        for name in set(sys.modules) - modules:
            del sys.modules[name]
    return code, out.getvalue(), err.getvalue()


def hook_answer(
    entry: dict[str, Any], payload: dict[str, Any], done: subprocess.CompletedProcess[str]
) -> Answer:
    """What came of the hook entry's run on the payload, as the hooks reference says of exit codes,
    plain output, and JSON output."""
    event = payload["hook_event_name"]
    if done.returncode == 2:
        return exit_2_answer(event, done.stdout, done.stderr)
    if done.returncode == 0 and not done.stdout.strip().startswith("{"):
        return Answer(said=done.stdout.strip() if event in CONTEXT_FROM_STDOUT else "")
    if done.returncode == 0:
        try:
            output = json.loads(done.stdout)
        except ValueError:
            return failure_answer(entry, payload, done.stderr)
        return json_answer(event, output)
    return failure_answer(entry, payload, done.stderr)


def exit_2_answer(event: str, out: str, err: str) -> Answer:
    """What came of a hook's exit 2: the event blocked with the standard error, where the event
    takes a block by exit 2, and nothing where the hook's script wasn't found on an event whose
    hook Claude Code then skips."""
    not_found = not out.strip() and "No such file or directory" in err
    if not_found and event in {"Stop", "SubagentStop", "UserPromptSubmit"}:
        return Answer()
    if event in BLOCKED_BY_EXIT_2:
        return Answer(blocked=True, said=err.strip())
    return Answer()


def failure_answer(entry: dict[str, Any], payload: dict[str, Any], err: str) -> Answer:
    """What came of a hook that failed, or gave JSON that can't be read: the event blocked where
    the entry's onFailure is `block` and the event takes it, with the standard error, after the
    line that names the entry on a call, and else nothing."""
    event = payload["hook_event_name"]
    on_failure = entry.get("onFailure") == "block" and event not in NO_ON_FAILURE
    if not (on_failure and event in BLOCKED_BY_EXIT_2):
        return Answer()
    if event != "PreToolUse":
        return Answer(blocked=True, said=err.strip())
    # The line before the error names the entry as its hooks.json gives it.
    written = " ".join([entry["command"], *entry.get("args", [])])
    return Answer(
        blocked=True,
        said=f"PreToolUse:{payload['tool_name']} hook error: [{written}]: failed; blocking because"
        f' onFailure is "block"\n{err.strip()}',
    )


def json_answer(event: str, output: dict[str, Any]) -> Answer:
    """What came of a hook's JSON output, as the hooks reference says of its fields."""
    blocked = False
    said = []
    if output.get("continue") is False:
        blocked = True
        said.append(output.get("stopReason", ""))
    specific = output.get("hookSpecificOutput") or {}
    if specific:
        assert specific.get("hookEventName") == event, f"hookEventName must be {event}"
    if event == "PreToolUse":
        decision = specific.get("permissionDecision")
        assert decision != "ask", "the double has no person to ask for a permission"
        if decision == "deny":
            blocked = True
            said.append(specific.get("permissionDecisionReason", ""))
    if event in TOP_LEVEL_DECISION and output.get("decision") == "block":
        blocked = True
        said.append(output.get("reason", ""))
    said.append(specific.get("additionalContext", ""))
    return Answer(blocked=blocked, said="\n".join(s for s in said if s))


def found(program: str, env: dict[str, str]) -> bool:
    """Whether the program is on the PATH of the environment, where a new process would find it."""
    return shutil.which(program, path=env.get("PATH", os.defpath)) is not None


def python_call(command: str) -> list[str] | None:
    """The script and its arguments where a shell command only runs `python3` on a script, which the
    double runs in its own process; None for any other command."""
    if re.search(r"[|&;<>()$`\\\n*?]", command):
        return None
    words = shlex.split(command)
    if len(words) >= 2 and words[0] in ("python3", "python") and not words[1].startswith("-"):
        return words[1:]
    return None


class Conversation:
    """One conversation of Claude Code in the repository, with the plugins loaded and the
    environment given, from its start. The person types by `type`, the main conversation calls its
    tools by `bash`, `start`, `resume`, `task_stop`, `enter_worktree`, and the other methods below,
    and ends its turn by `stop`, and each subagent acts by the Agent that `start` gives."""

    def __init__(self, repo: str, plugins: list[str], env: dict[str, str], temp: str):
        self.repo = os.path.realpath(repo)
        self.plugins = [Plugin.load(p) for p in plugins]
        self.env = env
        self.temp = temp
        self.records = {**recorded(), **skill_call(), **send_message()}
        self.session_id = str(uuid.uuid4())
        self.prompt_id = ""
        self.agents: list[Agent] = []
        self.count = 0
        # The folder the conversation works in, and the worktree it entered by EnterWorktree, with
        # the branch of it and whether EnterWorktree made it.
        self.cwd = self.repo
        self.worktree: tuple[str, str, bool] | None = None
        self.send("SessionStart", "session started", {})

    # What the double sends.

    def payload(self, record: str, fields: dict[str, Any]) -> dict[str, Any]:
        """The recorded payload of the record's event, made this conversation's, with the fields."""
        return self.made(self.records[record], fields)

    def made(self, recorded: dict[str, Any], fields: dict[str, Any]) -> dict[str, Any]:
        """The recorded payload made this conversation's, with the fields."""
        p = copy.deepcopy(recorded)
        text = json.dumps(p)
        text = text.replace(json.dumps(p["session_id"])[1:-1], self.session_id)
        text = text.replace("<repo>", self.repo)
        text = text.replace("<worktree-transcripts>", self.transcripts())
        text = text.replace("<transcripts>", self.transcripts())
        text = text.replace("<tasks>", os.path.join(self.temp, "tasks"))
        text = text.replace("<scratchpad>", os.path.join(self.temp, "scratchpad"))
        p = json.loads(text)
        if "prompt_id" in p:
            p["prompt_id"] = self.prompt_id
        # Each event carries the folder the conversation works in, and the transcript in the
        # folder of its project, which a worktree entered moves, as the record of EnterWorktree
        # shows.
        p["cwd"] = self.cwd
        p["transcript_path"] = os.path.join(self.transcripts(), f"{self.session_id}.jsonl")
        p.update(fields)
        return p

    def transcripts(self) -> str:
        """The folder of the transcripts of the conversation's project: the repository's, or, in a
        worktree entered, the worktree's."""
        if self.worktree:
            name = os.path.basename(self.worktree[0])
            return os.path.join(self.temp, "worktree-transcripts", name)
        return os.path.join(self.temp, "transcripts")

    def send(self, event: str, record: str, fields: dict[str, Any]) -> Answer:
        """Sends the recorded event, made this conversation's with the fields, as deliver sends a
        payload, and gives what came of it."""
        payload = self.payload(record, fields)
        assert payload["hook_event_name"] == event, f"record {record!r} is not of {event}"
        return self.deliver(payload)

    def deliver(self, payload: dict[str, Any]) -> Answer:
        """Sends the payload to each matching hook entry of each plugin, and gives what came of
        it."""
        event = payload["hook_event_name"]
        answers = []
        for plugin in self.plugins:
            for group in plugin.hooks.get(event, []):
                key = MATCHED.get(event)
                if key and not matches(group.get("matcher"), str(payload.get(key, ""))):
                    continue
                answers += [self.run_entry(plugin, e, payload) for e in group.get("hooks", [])]
        return Answer(
            blocked=any(a.blocked for a in answers),
            said="\n".join(a.said for a in answers if a.said),
            ran=[command for a in answers for command in a.ran],
        )

    def run_entry(self, plugin: Plugin, entry: dict[str, Any], payload: dict[str, Any]) -> Answer:
        """Runs one hook entry of the plugin on the payload, and gives what came of it, as
        hook_answer reads it, with the command it ran."""
        assert entry.get("type") == "command", f"the double runs only command hooks: {entry}"
        values = {
            "${CLAUDE_PLUGIN_ROOT}": plugin.root,
            "${CLAUDE_PROJECT_DIR}": self.repo,
            "${CLAUDE_PLUGIN_DATA}": os.path.join(self.temp, "data", os.path.basename(plugin.root)),
        }
        done = self.run_command(entry, values, json.dumps(payload))
        answer = hook_answer(entry, payload, done)
        answer.ran = [" ".join(done.args)]
        return answer

    def run_command(
        self, entry: dict[str, Any], values: dict[str, str], stdin: str
    ) -> subprocess.CompletedProcess[str]:
        """Runs the entry's command, with each value in place of its name, and given in the
        environment by its name without `${}`, on the standard input, as Claude Code runs a hook,
        and gives what came of it, its args the command's words."""

        def fill(text: str) -> str:
            for name, value in values.items():
                text = text.replace(name, value)
            return text

        # An entry in exec form runs its command with its arguments, and one in shell form runs in
        # /bin/sh, as the record of hook failures shows.
        shell = None if "args" in entry else fill(entry["command"])
        if shell is None:
            words = [fill(entry["command"]), *(fill(a) for a in entry["args"])]
            script = words[1:] if words[0] in ("python3", "python") and len(words) > 1 else None
        else:
            words = shlex.split(shell)
            script = python_call(shell)
        env = dict(self.env)
        env.update({k.strip("${}"): v for k, v in values.items()})
        if script and found(words[0], env):
            code, out, err = run_python(script[0], script[1:], stdin, env, self.cwd)
            return subprocess.CompletedProcess(words, code, out, err)
        if shell is None and not found(words[0], env):
            err = (
                "Error occurred while executing hook command: Executable not found in $PATH:"
                f' "{words[0]}"'
            )
            return subprocess.CompletedProcess(words, 1, "", err)
        done = subprocess.run(
            words if shell is None else shell,
            shell=shell is not None,
            input=stdin,
            env=env,
            cwd=self.cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return subprocess.CompletedProcess(words, done.returncode, done.stdout, done.stderr)

    def next_id(self, prefix: str, width: int) -> str:
        self.count += 1
        return prefix + format(self.count, "x").rjust(width, "0")

    # The person.

    def type(self, prompt: str) -> Answer:
        """The person types the prompt. A slash command of a loaded plugin's skill expands after
        UserPromptSubmit, as the record shows, and each command of its SKILL.md that runs as the
        skill loads runs then, as `loaded` says. The answer says what the hooks said, and its output
        is the skill's text as the main conversation reads it. Where such a command fails, the skill
        doesn't load: no model is called, so no Stop comes, the answer's output is empty, and it
        shows what Claude Code shows the person in place of a reply, as
        recorded/claude-code-2.1.323-skill-command-fails.jsonl shows."""
        self.prompt_id = str(uuid.uuid4())
        answer = self.send(
            "UserPromptSubmit", "a person types /lane:up changelog", {"prompt": prompt}
        )
        command = re.match(r"/([\w-]+):([\w-]+)(?: (.*))?$", prompt, re.DOTALL)
        if answer.blocked or not command or not self.has_skill(command[1], command[2]):
            return answer
        expanded = self.send(
            "UserPromptExpansion",
            "the typed /lane:up expands",
            {
                "prompt": prompt,
                "command_name": f"{command[1]}:{command[2]}",
                "command_args": command[3] or "",
            },
        )
        said = "\n".join(s for s in (answer.said, expanded.said) if s)
        ran = answer.ran + expanded.ran
        if expanded.blocked:
            return Answer(True, said, ran=ran)
        try:
            text = self.loaded(command[1], command[2])
        except SkillCommandFailed as e:
            return Answer(False, said, ran=ran, shown=str(e))
        return Answer(False, said, output=text, ran=ran)

    def compact(self) -> Answer:
        """The person types /compact. The double sends each event of the compaction as the record
        shows: PreCompact, the end of the subagent that writes the summary, a SubagentStop whose
        `agent_type` is empty, the SessionStart of `source` `compact`, and PostCompact, each with
        the conversation's `session_id`, which it keeps after them. The answer says whether a hook
        stopped any of them, and what the hooks said."""
        self.prompt_id = str(uuid.uuid4())
        answer = Answer()
        said = []
        for _, recorded in compaction():
            fields: dict[str, Any] = {}
            if recorded["hook_event_name"] == "SubagentStop":
                agent = self.next_id("a", 16)
                transcript = os.path.join(self.transcripts(), self.session_id, "subagents")
                fields = {
                    "agent_id": agent,
                    "agent_transcript_path": os.path.join(transcript, f"agent-{agent}.jsonl"),
                    "background_tasks": self.background_tasks(),
                }
            sent = self.deliver(self.made(recorded, fields))
            answer.blocked = answer.blocked or sent.blocked
            said.append(sent.said)
            answer.ran += sent.ran
        answer.said = "\n".join(s for s in said if s)
        return answer

    def skill_file(self, plugin: str, skill: str) -> tuple[Plugin, str] | None:
        """The plugin and the path of the skill's SKILL.md, where a loaded plugin holds it."""
        for p in self.plugins:
            path = os.path.join(p.root, "skills", skill, "SKILL.md")
            if p.name == plugin and os.path.isfile(path):
                return p, path
        return None

    def has_skill(self, plugin: str, skill: str) -> bool:
        return self.skill_file(plugin, skill) is not None

    def loaded(self, plugin: str, skill: str) -> str:
        """The text of the skill's SKILL.md after its frontmatter, with each command that runs as
        the skill loads, `!` and the command in backticks at the start of a line or after a blank,
        replaced by what it printed, as recorded/claude-code-2.1.323-skill-command.jsonl shows of a
        typed command and of a Skill call alike. The command runs in the conversation's folder,
        which the record shows as the repository's, and a worktree entered moves, as the skills
        reference says it runs in the session's working folder; no record shows it in a worktree.
        It runs with the environment of a Bash command, and with `${CLAUDE_PLUGIN_ROOT}` filled in
        its text but absent from its environment, as is `CLAUDE_PROJECT_DIR`. No hook sees it. The
        records hold only the inline form of a command, so the double runs no other. Raises
        SkillCommandFailed where a command gives other than 0, with the words that
        recorded/claude-code-2.1.323-skill-command-fails.jsonl shows: the pattern, then `[stderr]`
        and what it printed. That record's command printed one line on stdout before one on stderr,
        so the double gives stdout before stderr; no record shows them interleaved."""
        found = self.skill_file(plugin, skill)
        assert found, f"no loaded plugin holds the skill {plugin}:{skill}"
        owner, path = found
        with open(path, encoding="utf-8") as f:
            text = f.read()
        body = text.split("---", 2)[2].lstrip("\n") if text.startswith("---") else text
        assert "```!" not in body, f"the record holds only a command in the inline form: {path}"
        env = dict(self.env, **bash_environment(self.session_id))
        for name in ("CLAUDE_PLUGIN_ROOT", "CLAUDE_PROJECT_DIR"):
            env.pop(name, None)

        def run(match: re.Match[str]) -> str:
            command = match[1].replace("${CLAUDE_PLUGIN_ROOT}", owner.root)
            done = subprocess.run(
                command,
                shell=True,
                env=env,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            if done.returncode != 0:
                printed = (done.stdout + done.stderr).rstrip("\n")
                raise SkillCommandFailed(
                    f'Shell command failed for pattern "{match[0].strip()}": [stderr]\n{printed}'
                )
            return done.stdout.rstrip("\n")

        return re.sub(r"(?:^|(?<=\s))!`([^`\n]+)`", run, body, flags=re.MULTILINE)

    def model_may_call(self, plugin: str, skill: str) -> bool:
        """Whether the skill's frontmatter leaves the model free to call it, as no
        `disable-model-invocation: true` stops it."""
        found = self.skill_file(plugin, skill)
        if not found:
            return True
        with open(found[1], encoding="utf-8") as f:
            text = f.read()
        front = text.split("---", 2)[1] if text.startswith("---") else ""
        flags = re.IGNORECASE | re.MULTILINE
        return not re.search(r"^disable-model-invocation:\s*true\s*$", front, flags)

    # The main conversation and its subagents.

    def bash(self, command: str, agent: Agent | None = None) -> Answer:
        """The main conversation, or the agent, calls the Bash tool on the command. Where the hooks
        let it through, the double runs it in the conversation's folder with the conversation's
        environment, which holds no `CLAUDE_PROJECT_DIR`, as each Bash command of the record of
        EnterWorktree shows, and sends PostToolUse, or PostToolUseFailure where it fails, as the
        record shows."""
        who = {"agent_id": agent.id, "agent_type": agent.type} if agent else {}
        record = "writer runs git log" if agent else "the main conversation runs lay.py print"
        tool_input = {"command": command, "description": "Run a command"}
        use = {"tool_input": tool_input, "tool_use_id": self.next_id("toolu_", 24)}
        with self.acting(agent):
            answer = self.send("PreToolUse", record, {**who, **use})
            if answer.blocked:
                return answer
            env = dict(self.env, **bash_environment(self.session_id))
            env.pop("CLAUDE_PROJECT_DIR", None)
            script = python_call(command)
            if script and found(shlex.split(command)[0], env):
                code, out, err = run_python(script[0], script[1:], "", env, self.cwd)
            else:
                done = subprocess.run(
                    command,
                    shell=True,
                    env=env,
                    cwd=self.cwd,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                code, out, err = done.returncode, done.stdout, done.stderr
            answer.exit_code, answer.output = code, out + err
            if code == 0:
                response = {
                    "stdout": out.rstrip("\n"),
                    "stderr": err.rstrip("\n"),
                    "interrupted": False,
                    "isImage": False,
                    "noOutputExpected": False,
                }
                ran = "git log ran" if agent else "lay.py print ran"
                after = self.send("PostToolUse", ran, {**who, **use, "tool_response": response})
            else:
                error = f"Exit code {code}\n" + (out + err).rstrip("\n")
                after = self.send(
                    "PostToolUseFailure", "a command fails", {**who, **use, "error": error}
                )
            answer.said = "\n".join(s for s in (answer.said, after.said) if s)
            answer.ran += after.ran
            return answer

    def write(self, agent: Agent | None, path: str, content: str) -> Answer:
        """The agent, or the main conversation where `agent` is None, calls the Write tool to create
        the file at the path with the content. Where the hooks let it through, the double writes the
        file and sends PostToolUse, as the record shows. A call of the main conversation goes on the
        records of its own calls, with the tool's name Write, as each call of the main conversation
        in the record carries no `agent_id` and no `agent_type`. The record holds the Write of a new
        file, so the double writes no file that's there."""
        assert not os.path.exists(path), f"the record holds only a new file's Write: {path}"
        tool_input = {"file_path": path, "content": content}
        use = {"tool_input": tool_input, "tool_use_id": self.next_id("toolu_", 24)}
        if agent:
            use.update(agent_id=agent.id, agent_type=agent.type)
            before, ran = "writer writes CHANGELOG.md", "CHANGELOG.md written"
        else:
            use["tool_name"] = "Write"
            before, ran = "the main conversation runs lay.py print", "lay.py print ran"
        with self.acting(agent):
            answer = self.send("PreToolUse", before, use)
            if answer.blocked:
                return answer
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            response = {
                "type": "create",
                "filePath": path,
                "content": content,
                "structuredPatch": [],
                "originalFile": None,
                "userModified": False,
            }
            after = self.send("PostToolUse", ran, {**use, "tool_response": response})
            answer.said = "\n".join(s for s in (answer.said, after.said) if s)
            answer.ran += after.ran
            return answer

    def read(self, agent: Agent, path: str) -> Answer:
        """The agent calls the Read tool on the file at the path. The double sends the PreToolUse
        that the record holds of a subagent's call, with the tool's name and input as the hooks
        reference gives Read's: `file_path`. It sends no PostToolUse, as neither the record nor the
        hooks reference shows Read's `tool_response`. The answer says whether a hook stopped the
        call, and what the agent reads."""
        use = {
            "tool_name": "Read",
            "tool_input": {"file_path": path},
            "tool_use_id": self.next_id("toolu_", 24),
            "agent_id": agent.id,
            "agent_type": agent.type,
        }
        with self.acting(agent):
            return self.send("PreToolUse", "writer writes CHANGELOG.md", use)

    def edit(self, path: str, old: str, new: str) -> Answer:
        """The main conversation calls the Edit tool to replace the one place of `old` in the file
        at the path with `new`. The double sends the PreToolUse that the record holds of a call of
        the main conversation, with the tool's name and input as the hooks reference gives Edit's:
        `file_path`, `old_string`, `new_string`, and `replace_all`. Where the hooks let it through,
        the double changes the file. It sends no PostToolUse, as neither the record nor the hooks
        reference shows Edit's `tool_response`."""
        with open(path, encoding="utf-8") as f:
            text = f.read()
        assert text.count(old) == 1, f"Edit replaces one place of the text in {path}: {old!r}"
        tool_input = {"file_path": path, "old_string": old, "new_string": new, "replace_all": False}
        use = {"tool_name": "Edit", "tool_input": tool_input}
        use["tool_use_id"] = self.next_id("toolu_", 24)
        answer = self.send("PreToolUse", "the main conversation runs lay.py print", use)
        if not answer.blocked:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text.replace(old, new))
        return answer

    def skill(self, skill: str, args: str) -> Answer:
        """The main conversation calls the Skill tool on the skill, `<plugin>:<skill>`, with the
        arguments, as an AI calls a skill in place of a person who types its command. The double
        sends the PreToolUse that the record of a Skill call holds, with the input `skill` and
        `args`, and, where the hooks let it through, the PostToolUse with the `tool_response` that
        the record holds, with the skill's name. It sends no UserPromptExpansion, as the record
        shows none. Where a loaded plugin holds the skill, each command of its SKILL.md that runs
        as the skill loads runs between the two, as `loaded` says; no record shows whether it runs
        before or after the PostToolUse. A skill whose SKILL.md holds
        `disable-model-invocation: true` fails before any hook, with the error that
        recorded/claude-code-2.1.323-skill-command.jsonl shows, and runs no command. The answer
        says whether the call was stopped, and what the main conversation reads, and its output is
        the skill's text as the main conversation reads it."""
        plugin, _, name = skill.partition(":")
        if not self.model_may_call(plugin, name):
            refused = lines_of("skill-command")[
                "the main conversation calls rec:probe, whose SKILL.md holds"
                " disable-model-invocation, by the Skill tool"
            ]
            error = refused["tool_result"].replace(refused["tool_input"]["skill"], skill)
            return Answer(blocked=True, said=error)
        use = {
            "tool_input": {"skill": skill, "args": args},
            "tool_use_id": self.next_id("toolu_", 24),
        }
        answer = self.send(
            "PreToolUse", "the main conversation calls lane:up by the Skill tool", use
        )
        if answer.blocked:
            return answer
        if self.has_skill(plugin, name):
            answer.output = self.loaded(plugin, name)
        response = {"success": True, "commandName": skill}
        after = self.send(
            "PostToolUse", "the Skill call of lane:up ran", {**use, "tool_response": response}
        )
        answer.said = "\n".join(x for x in (answer.said, after.said) if x)
        answer.ran += after.ran
        return answer

    @contextlib.contextmanager
    def acting(self, agent: Agent | None):
        """Sends the events of the block with the agent's prompt ID, where an agent acts."""
        prompt_id = self.prompt_id
        if agent:
            self.prompt_id = agent.prompt_id
        try:
            yield
        finally:
            self.prompt_id = prompt_id

    def start(
        self, subagent_type: str, prompt: str, description: str, by: Agent | None = None
    ) -> tuple[Answer, Agent | None]:
        """The main conversation, or the agent `by`, starts the subagent in the background with the
        prompt, by the Agent tool. Where the hooks let it through, the subagent starts, and the
        answer says what it reads as it starts; the Agent stands for it. Where the hooks stop the
        start, the answer says what the starter reads. The double holds only a subagent's start
        that the hooks stop, as no test runs a subagent that another one started."""
        tool_input = {
            "description": description,
            "prompt": prompt,
            "subagent_type": subagent_type,
            "run_in_background": True,
        }
        who = {"agent_id": by.id, "agent_type": by.type} if by else {}
        use = {"tool_input": tool_input, "tool_use_id": self.next_id("toolu_", 24)}
        with self.acting(by):
            answer = self.send(
                "PreToolUse",
                "the main conversation starts writer in the background",
                {**who, **use},
            )
        if answer.blocked:
            return answer, None
        assert by is None, f"the double runs no subagent that a subagent started: {subagent_type}"
        agent = Agent(self, self.next_id("a", 16), subagent_type, description, use["tool_use_id"])
        self.agents.append(agent)
        started = self.send(
            "SubagentStart", "writer starts", {"agent_id": agent.id, "agent_type": agent.type}
        )
        response = copy.deepcopy(self.records["writer runs in the background"]["tool_response"])
        response.update(
            agentId=agent.id,
            description=description,
            prompt=prompt,
            outputFile=agent.output_file,
        )
        self.send(
            "PostToolUse", "writer runs in the background", {**use, "tool_response": response}
        )
        return Answer(started.blocked, started.said, ran=answer.ran + started.ran), agent

    def resume(self, agent: Agent, message: str, summary: str = "Resume") -> Answer:
        """The main conversation resumes the agent, whose end reached it, by SendMessage with the
        message, which keeps the agent's whole conversation. The double sends the PreToolUse that
        the record holds, with the input that Claude Code fills in beside `to`, `summary`, and
        `message`, and, where the hooks let it through, the PostToolUse with the `tool_response`
        that the record holds and the SubagentStart of the same agent again. The agent then runs
        until its next end, which reaches the main conversation with the ID of the SendMessage
        call, as the record shows. The answer says whether a hook stopped the call, and what the
        agent reads as it starts again."""
        assert not agent.running, f"the record resumes only an agent whose end came: {agent.id}"
        to = {"to": agent.id, "summary": summary, "message": message}
        filled = {"type": "message", "recipient": agent.id, "recipient_kind": "agent"}
        use = {
            "tool_input": {**to, **filled, "content": message},
            "tool_use_id": self.next_id("toolu_", 24),
        }
        answer = self.send("PreToolUse", "the main conversation resumes helper by SendMessage", use)
        if answer.blocked:
            return answer
        response = copy.deepcopy(self.records["the SendMessage call ran"]["tool_response"])
        response.update(message=f"Resuming agent {agent.id[:7]}")
        response.update(resumedAgentId=agent.id, revivedAgentId=agent.id)
        response["pin"].update(id=agent.id, name=agent.id)
        self.send(
            "PostToolUse",
            "the SendMessage call ran",
            {"tool_input": to, "tool_use_id": use["tool_use_id"], "tool_response": response},
        )
        agent.running, agent.tool_use_id = True, use["tool_use_id"]
        started = self.send(
            "SubagentStart",
            "helper starts again on the message",
            {"agent_id": agent.id, "agent_type": agent.type},
        )
        return Answer(started.blocked, started.said, ran=answer.ran + started.ran)

    def task_stop(self, agent: Agent) -> Answer:
        """The main conversation stops the agent by TaskStop, with the agent's ID as `task_id`, as
        recorded/claude-code-2.1.323-task-stop.jsonl shows. Where the agent's end already came, the
        call fails with the error that the record shows, before any hook: the double sends no event,
        and the answer is blocked with that error. Else the double sends the PreToolUse, and, where
        the hooks let it through, the PostToolUse with the `tool_response` that the record holds.
        The agent then ends with no SubagentStop, and no event of the tool call it was running
        comes, as the record shows none. Its notification reaches the main conversation in the same
        turn, with the turn's `prompt_id`, the status `killed`, and no result. The answer says
        whether a hook stopped the call, and what the main conversation reads beside the
        notification."""
        lines = lines_of("task-stop")
        if not agent.running:
            failed = lines["the main conversation stops by TaskStop a subagent whose end came"]
            error = failed["tool_result"].replace(failed["tool_input"]["task_id"], agent.id)
            return Answer(blocked=True, said=error)
        use = {"tool_input": {"task_id": agent.id}, "tool_use_id": self.next_id("toolu_", 24)}
        called = lines["the main conversation stops sleeper by TaskStop"]["payload"]
        answer = self.deliver(self.made(called, use))
        if answer.blocked:
            return answer
        ran = lines["the TaskStop call ran"]["payload"]
        response = {
            "message": f"Successfully stopped task: {agent.id} ({agent.description})",
            "task_id": agent.id,
            "task_type": ran["tool_response"]["task_type"],
            "command": agent.description,
        }
        after = self.deliver(self.made(ran, {**use, "tool_response": response}))
        agent.running, agent.killed = False, True
        notified = lines["the stopped sleeper's notification reaches the main conversation"]
        prompt = notified["payload"]["prompt"]
        for tag, value in (
            ("task-id", agent.id),
            ("tool-use-id", agent.tool_use_id),
            ("output-file", agent.output_file),
        ):
            prompt = re.sub(rf"<{tag}>.*?</{tag}>", f"<{tag}>{value}</{tag}>", prompt)
        prompt = re.sub(
            r'<summary>Agent ".*?" was', f'<summary>Agent "{agent.description}" was', prompt
        )
        told = self.deliver(self.made(notified["payload"], {"prompt": prompt}))
        return Answer(
            told.blocked,
            "\n".join(s for s in (answer.said, after.said, told.said) if s),
            ran=answer.ran + after.ran + told.ran,
        )

    def git(self, *args: str) -> str:
        """Runs git in the repository, as EnterWorktree and ExitWorktree change its worktrees."""
        done = subprocess.run(
            ["git", *args], cwd=self.repo, capture_output=True, text=True, check=True
        )
        return done.stdout

    def enter_worktree(self, name: str | None = None, path: str | None = None) -> Answer:
        """The main conversation enters a worktree by EnterWorktree, a new one by its name or one
        that git lists by its path, as recorded/claude-code-2.1.323-worktree.jsonl shows. The double
        sends the PreToolUse with the input as given, and, where the hooks let it through, makes a
        new worktree at .claude/worktrees/<name> on the branch worktree-<name>, from the
        repository's HEAD, and sends the PostToolUse with the `tool_response` that the record holds,
        a path given made whole in its input. From that PostToolUse on, each event carries the
        worktree as its `cwd`, and the transcript in the worktree's project folder as its
        `transcript_path`, and each hook and Bash command, of the main conversation and of each
        subagent, runs in the worktree, while each hook's `CLAUDE_PROJECT_DIR` stays the
        repository, as the record shows. The record's repository has no remote, so it can't show
        whether a new worktree starts from HEAD or from the remote's default branch."""
        assert (name is None) != (path is None), "EnterWorktree takes a name or a path"
        assert self.worktree is None, "the record enters one worktree at a time"
        lines = lines_of("worktree")
        if name:
            called = lines["the main conversation enters a worktree by EnterWorktree"]
            ran = lines["the EnterWorktree call ran"]
        else:
            called = lines["the main conversation enters the worktree by its path"]
            ran = lines["the EnterWorktree call by path ran"]
        tool_input = {"name": name} if name else {"path": path}
        use = {"tool_input": tool_input, "tool_use_id": self.next_id("toolu_", 24)}
        answer = self.deliver(self.made(called["payload"], use))
        if answer.blocked:
            return answer
        if name:
            where = os.path.join(self.repo, ".claude", "worktrees", name)
            branch = f"worktree-{name}"
            self.git("worktree", "add", "-q", "-b", branch, where)
        else:
            where = os.path.realpath(os.path.join(self.cwd, str(path)))
            listed = self.git("worktree", "list", "--porcelain").splitlines()
            assert f"worktree {where}" in listed, f"git lists no worktree at {where}"
            branch = self.git("-C", where, "branch", "--show-current").strip()
            use["tool_input"] = {"path": where}
        response = self.retold(ran["payload"]["tool_response"], where, branch)
        self.cwd, self.worktree = where, (where, branch, bool(name))
        after = self.deliver(self.made(ran["payload"], {**use, "tool_response": response}))
        answer.said = "\n".join(s for s in (answer.said, after.said) if s)
        answer.ran += after.ran
        return answer

    def retold(self, response: dict[str, Any], where: str, branch: str) -> dict[str, Any]:
        """The recorded `tool_response` of a worktree's call, told of the worktree and the branch
        given, in this repository."""
        text = json.dumps(response).replace("<repo>", self.repo)
        recorded_where = json.dumps(response["worktreePath"].replace("<repo>", self.repo))[1:-1]
        text = text.replace(recorded_where, json.dumps(where)[1:-1])
        text = text.replace(json.dumps(response["worktreeBranch"]), json.dumps(branch))
        text = text.replace(f"“{response['worktreeBranch']}”", f"“{branch}”")
        return json.loads(text)

    def exit_worktree(self, action: str) -> Answer:
        """The main conversation leaves the worktree it entered by ExitWorktree, with the action
        `remove` or `keep`, as recorded/claude-code-2.1.323-worktree.jsonl shows. The double sends
        the PreToolUse, and, where the hooks let it through, removes the worktree and its branch on
        `remove`, and sends the PostToolUse with the `tool_response` that the record holds, from
        which on each event carries the repository again. ExitWorktree removes no worktree that it
        didn't make, as its description says, and the record removes only a worktree with no
        change, so the double removes no other."""
        assert self.worktree, "ExitWorktree leaves only a worktree that EnterWorktree entered"
        where, branch, made = self.worktree
        assert action in ("remove", "keep"), f"ExitWorktree takes remove or keep: {action}"
        assert made or action == "keep", "ExitWorktree removes no worktree entered by path"
        lines = lines_of("worktree")
        if action == "remove":
            called = lines["the main conversation leaves the worktree by ExitWorktree"]
            ran = lines["the ExitWorktree call ran"]
        else:
            called = lines["the main conversation leaves the worktree it entered by path"]
            ran = lines["the ExitWorktree call that keeps the worktree ran"]
        use = {"tool_input": {"action": action}, "tool_use_id": self.next_id("toolu_", 24)}
        answer = self.deliver(self.made(called["payload"], use))
        if answer.blocked:
            return answer
        if action == "remove":
            self.git("worktree", "remove", where)
            self.git("branch", "-q", "-D", branch)
        response = self.retold(ran["payload"]["tool_response"], where, branch)
        self.cwd, self.worktree = self.repo, None
        after = self.deliver(self.made(ran["payload"], {**use, "tool_response": response}))
        answer.said = "\n".join(s for s in (answer.said, after.said) if s)
        answer.ran += after.ran
        return answer

    def background_tasks(self) -> list[dict[str, Any]]:
        return [
            {
                "id": a.id,
                "type": "subagent",
                "status": "running",
                "description": a.description,
                "agent_type": a.type,
            }
            for a in self.agents
            if a.running
        ]

    def stop(self, last_message: str) -> Answer:
        """The main conversation ends its turn with the message. A blocked stop goes on with what
        the hooks said."""
        return self.send(
            "Stop",
            "the main conversation stops",
            {
                "last_assistant_message": last_message,
                "background_tasks": self.background_tasks(),
                "stop_hook_active": False,
            },
        )


class Agent:
    """A subagent that the main conversation started in the background."""

    def __init__(self, conversation: Conversation, id: str, type: str, description: str, use: str):
        self.conversation = conversation
        self.id = id
        self.type = type
        self.description = description
        self.tool_use_id = use
        self.prompt_id = conversation.prompt_id
        self.running = True
        # Whether TaskStop stopped the subagent, after which it ends no more.
        self.killed = False
        # Whether a hook stopped an end of the subagent, after which each end carries
        # `stop_hook_active`, as the record shows.
        self.stopped = False
        self.output_file = os.path.join(
            conversation.temp, "tasks", conversation.session_id, "tasks", f"{id}.output"
        )

    def bash(self, command: str) -> Answer:
        """The subagent calls the Bash tool on the command."""
        return self.conversation.bash(command, self)

    def write(self, path: str, content: str) -> Answer:
        """The subagent calls the Write tool to create the file."""
        return self.conversation.write(self, path, content)

    def read(self, path: str) -> Answer:
        """The subagent calls the Read tool on the file."""
        return self.conversation.read(self, path)

    def start(
        self, subagent_type: str, prompt: str, description: str
    ) -> tuple[Answer, Agent | None]:
        """The subagent starts a subagent in the background by the Agent tool."""
        return self.conversation.start(subagent_type, prompt, description, by=self)

    def end(self, last_message: str) -> tuple[Answer, Answer | None]:
        """The subagent ends with the message. The first answer says whether the hooks stopped the
        end, and what the subagent reads. Where they let it end, its end reaches the main
        conversation as a UserPromptSubmit whose prompt is a task-notification, as the record shows,
        and the second answer says what the main conversation reads beside it. Where they stop it,
        the subagent goes on, and each end after that carries `stop_hook_active`."""
        assert not self.killed, f"no end comes of a subagent that TaskStop stopped: {self.id}"
        c = self.conversation
        prompt_id = c.prompt_id
        c.prompt_id = self.prompt_id
        transcript = os.path.join(c.transcripts(), c.session_id, "subagents")
        record = "writer ends again after its end was stopped" if self.stopped else "writer ends"
        stopped = c.send(
            "SubagentStop",
            record,
            {
                "agent_id": self.id,
                "agent_type": self.type,
                "agent_transcript_path": os.path.join(transcript, f"agent-{self.id}.jsonl"),
                "last_assistant_message": last_message,
                "background_tasks": c.background_tasks(),
                "stop_hook_active": self.stopped,
            },
        )
        c.prompt_id = prompt_id
        if stopped.blocked:
            self.stopped = True
            return stopped, None
        self.running = False
        notification = c.records["writer's end reaches the main conversation"]["prompt"]
        notification = re.sub(
            r"<task-id>.*?</task-id>", f"<task-id>{self.id}</task-id>", notification
        )
        notification = re.sub(
            r"<tool-use-id>.*?</tool-use-id>",
            f"<tool-use-id>{self.tool_use_id}</tool-use-id>",
            notification,
        )
        notification = re.sub(
            r"<output-file>.*?</output-file>",
            f"<output-file>{self.output_file}</output-file>",
            notification,
        )
        notification = re.sub(
            r'<summary>Agent ".*?" finished</summary>',
            f'<summary>Agent "{self.description}" finished</summary>',
            notification,
        )
        notification = re.sub(
            r"<result>.*?</result>",
            f"<result>{last_message}</result>",
            notification,
            flags=re.DOTALL,
        )
        c.prompt_id = str(uuid.uuid4())
        notified = c.send(
            "UserPromptSubmit",
            "writer's end reaches the main conversation",
            {"prompt": notification},
        )
        return stopped, notified

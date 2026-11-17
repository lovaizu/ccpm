"""Runs a plugin's end-to-end (E2E) test once, as the E2E tests of
plugins/rn/domain/best-practices/architecture/best-practice.md say: the real Claude Code on Opus,
with the plugins under test, in a fresh clone of the test's repository, and a stand-in in the
person's place that holds an intent the plugins never receive and reads only what the person's
screen shows. It keeps each run's records, from which the plugin's E2E test counts its key
results. It names no plugin, so the E2E tests of every plugin of the repository run on it.

Run it from the top of the repository as `python3 dev/scripts/e2e.py run <E2E test file>`, on the
developer's login, as dev/plugin-development-guide.md says of the Claude Code of a test on the
model. It prints the folder of the run's records. Claude Code's hooks run
`e2e.py hook <file>`, which adds each event to the file.

An E2E test file is one JSON object:
- `intent`: what the person means to do, which only the stand-in reads.
- `repository`: the URL of the repository that the test clones, such as lovaizu/playground's.
- `commits`: the path, from the top, of a JSON list of the commits that the test makes in the
  clone, each `{"message": <text>, "files": {<path in the clone>: <text>}}`, where a file's text
  may be `{"from": <path of a file from the top>}`.
- `plugin_dirs`: each folder that Claude Code loads by `--plugin-dir`, where `{top}` stands for the
  top of the repository and `{clone}` for the clone.
- `turns`: the most prompts that the stand-in gives, 1 or more.
- `records`: the folder, from the top, under which the run's records lie.
- `push`: whether the clone pushes to the repository, true where the plugin needs a repository it
  can push to, such as for a pull request, and false where it pushes nowhere. e2e.py removes
  from the repository each branch that the run pushed and that the repository didn't hold before,
  so that the next run starts from the same repository.

The records of a run lie in `<records>/<test>/<UTC time>/`, where `<test>` is the E2E test file's
name without `.json`:
- `run.json`: what the run took: the commit at the top and whether the top held changes beside it,
  Claude Code's version, the model, and the E2E test file as given.
- `turns.jsonl`: each turn's prompt, its times, Claude Code's exit code, and what the screen showed.
- `hooks.jsonl`: each hook event, with the time it came.
- `transcripts/`: Claude Code's transcript of the conversation, and of each subagent beside it.
- `tmp/`: what the plugins wrote in the system's temporary folder, such as their run records.
- `run.diff`: what the run changed in the clone after the test's commits.
- `branches/<branch>.diff`: what the run committed on each branch it made, such as a plugin's work
  in its worktree, after the test's commits.

`python3 dev/scripts/e2e.py try <records> <try file>` has a stand-in of a deliverable's people try
it, where a test counts whether its people could use it: the real Claude Code on Opus, with no
plugin and with only Bash and Read, in a fresh clone with the test's commits, the change of a
branch that the run of `<records>` made, and the files the people bring. Its brief holds only what
they mean to do and what they have, such as the deliverable's text or a terminal with its command.
It prints the folder of the try's records. A try file is one JSON object:
- `branch`: the branch whose change the clone holds, as `branches/` of the records names it.
- `intent`: what the people mean to do with the deliverable.
- `has`: what they have, which the stand-in alone uses, such as `the guide docs/printing.md`.
- `files`: each file the people bring, `{<path in the clone>: <text>}`, such as their lines.

The records of a try lie in `<records>/tries/<try>/`, where `<try>` is the try file's name without
`.json`:
- `try.json`: the try file as given.
- `stream.jsonl`: Claude Code's stream-json of the try, each command it ran and what it printed.
- `changed.diff`: what the stand-in changed in the clone, beside the people's files.

The records hold neither the login nor an email address, nor the lines of Claude Code's requests to
its API, as they hold the developer's account and not the run. They give `<top>` for the top of the
repository and `<run>` for the run's temporary folder, whose clone is `<run>/clone`."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from typing import Any, Union

# The model the plugins' users run, as the plugin guide says of every test on the model.
MODEL = "opus"
# What .claude/rules/dev.md says each `claude -p` started is told.
RULE = (
    "Install nothing, and send nothing to a translator, a web API, or any other service outside"
    " this repository's git."
)
# The stand-in's brief, which holds only the person's intent.
BRIEF = """You are a person at the prompt of Claude Code, in a terminal, at the root of your \
project's git repository. What you mean to do: {intent}

Each message gives you what your screen shows so far: each prompt you typed, after `> `, and what \
Claude Code showed after it. Give what you type next as `prompt`, in your own words, with `done` \
false. Give `done` true once you have what you came for, or where you would stop here. Ask for \
what you mean to do, and judge what the screen shows against it. Don't tell Claude Code how it or \
its plugins should do the work, such as which steps to take, in what order, or which sentences of \
a file to keep, unless what you mean to do says so. You see only the screen, and you type only \
into Claude Code."""
REPLY = {
    "type": "object",
    "properties": {"done": {"type": "boolean"}, "prompt": {"type": "string"}},
    "required": ["done"],
}
# Each hook event of Claude Code's hooks reference, in the order of their names, each of which the
# records keep.
EVENTS = (
    "Notification",
    "PermissionRequest",
    "PostCompact",
    "PostToolUse",
    "PostToolUseFailure",
    "PreCompact",
    "PreToolUse",
    "SessionEnd",
    "SessionStart",
    "Stop",
    "SubagentStart",
    "SubagentStop",
    "UserPromptExpansion",
    "UserPromptSubmit",
)
# The push URL of the clone of a test that pushes nothing, which no push reaches.
NO_PUSH = "no-push://an-e2e-test-pushes-nothing"
# The longest that one turn of the Claude Code under test may take.
TURN_SECONDS = 3600
# The identity of the test's own commits.
AUTHOR = {
    "GIT_AUTHOR_NAME": "e2e",
    "GIT_AUTHOR_EMAIL": "e2e@e2e.invalid",
    "GIT_COMMITTER_NAME": "e2e",
    "GIT_COMMITTER_EMAIL": "e2e@e2e.invalid",
}
# The lines of a transcript that hold the account or the requests to the API, and not the run.
DROPPED = {"api-request", "api-request-blob", "api-request-shape", "session-owner"}
DROPPED_ATTACHMENTS = {"session_context", "credential_org", "prompt_snapshot"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# What the screen shows of a call, by its tool, as Claude Code shows it.
SHOWN = {
    "Bash": "command",
    "Read": "file_path",
    "Write": "file_path",
    "Edit": "file_path",
    "Agent": "subagent_type",
    "Skill": "skill",
}
USAGE = (
    "usage: python3 dev/scripts/e2e.py run <E2E test file> | try <records> <try file> | hook <file>"
)
# The brief of a stand-in of a deliverable's people, who try it with only what they have.
PEOPLE = """You are one of the people a deliverable is for, at a terminal in a folder that holds \
your team's repository. What you mean to do: {intent}

What you have: {has}. Use only that, as such a person would, and read no other file of the \
repository. Write no file of the repository. Stop once you've done what you mean to do, or where \
you would give up, and say which."""
# The fields of a try file, each with its type.
TRY = {"branch": str, "intent": str, "has": str, "files": dict}


class Refused(Exception):
    """What's wrong with the test, so that whoever ran e2e.py can fix it."""


File = Union[str, dict]


@dataclass
class Commit:
    message: str
    files: dict[str, File]


@dataclass
class RunRecords:
    """The folder of a run's records, into which each record is written without the login,
    `token`, or an email address, and with `<top>` and `<run>` in place of the paths of the top
    and of the run's temporary folder, which name the developer's machine and not the run."""

    folder: str
    top: str
    temporary: str
    token: str | None

    def write(self, path: str, text: str) -> None:
        """Writes the text, scrubbed, to the record at the path in the folder."""
        full = os.path.join(self.folder, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(self.scrubbed(text))

    def scrubbed(self, text: str) -> str:
        if self.token:
            text = text.replace(self.token, "<token>")
        text = text.replace(self.temporary, "<run>")
        return EMAIL.sub("<email>", text.replace(self.top, "<top>"))


@dataclass
class E2ETest:
    """An E2E test, as its file gives it."""

    name: str
    intent: str
    repository: str
    commits: list[Commit]
    plugin_dirs: list[str]
    turns: int
    records: str
    push: bool
    given: dict[str, Any]


def main(argv: list[str]) -> int:
    if argv[:1] == ["hook"] and len(argv) == 2:
        return hook(argv[1], sys.stdin.read())
    if not (argv[:1] == ["run"] and len(argv) == 2 or argv[:1] == ["try"] and len(argv) == 3):
        print(USAGE, file=sys.stderr)
        return 2
    try:
        token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") or None
        if token is None and not os.path.isfile(_credentials()):
            raise Refused(
                "CLAUDE_CODE_OAUTH_TOKEN holds no login, and Claude Code keeps no credentials file"
                f" at {_credentials()}. Set CLAUDE_CODE_OAUTH_TOKEN to the developer's login, as"
                " `claude setup-token` gives it, or log in to Claude Code."
            )
        if argv[0] == "try":
            print(tried(argv[1], argv[2], os.getcwd(), token))
        else:
            print(run(read(argv[1]), os.getcwd(), token))
    except Refused as e:
        print(f"e2e.py: {e}", file=sys.stderr)
        return 1
    return 0


def hook(path: str, stdin: str) -> int:
    """Adds the event on stdin to the file at path, with the time it came, and prints nothing, so
    that the run goes on as it would without it."""
    try:
        event: dict[str, Any] = {"payload": json.loads(stdin)}
    except ValueError:
        event = {"unread": stdin}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": _now(), **event}) + "\n")
    return 0


def read(path: str) -> E2ETest:
    """The E2E test of the file. Raises Refused, naming the file and the field, where it isn't
    one."""
    return _test(_json(path), path)


def _test(given: Any, path: str) -> E2ETest:
    if not isinstance(given, dict):
        raise Refused(f"{path} isn't a JSON object")
    fields = {
        "intent": str,
        "repository": str,
        "commits": str,
        "plugin_dirs": list,
        "turns": int,
        "records": str,
        "push": bool,
    }
    for key, kind in fields.items():
        if not isinstance(given.get(key), kind):
            raise Refused(f"{path} needs `{key}` as {kind.__name__}")
    if not all(isinstance(each, str) for each in given["plugin_dirs"]):
        raise Refused(f"{path} needs `plugin_dirs` as a list of text")
    if given["turns"] < 1:
        raise Refused(f"{path} needs `turns` as 1 or more")
    name = os.path.basename(path).rsplit(".json", 1)[0]
    commits = _commits(given["commits"])
    return E2ETest(
        name,
        given["intent"],
        given["repository"],
        commits,
        given["plugin_dirs"],
        given["turns"],
        given["records"],
        given["push"],
        given,
    )


def _commits(path: str) -> list[Commit]:
    given = _json(path)
    form = f"{path} needs a list of {{message, files}}, each file's text or {{from}}"
    if not isinstance(given, list):
        raise Refused(form)
    commits = []
    for each in given:
        files = each.get("files") if isinstance(each, dict) else None
        if not isinstance(files, dict) or not isinstance(each.get("message"), str):
            raise Refused(form)
        for text in files.values():
            if not (isinstance(text, str) or isinstance(text, dict) and "from" in text):
                raise Refused(form)
        commits.append(Commit(each["message"], files))
    return commits


def _json(path: str) -> Any:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise Refused(f"{path} can't be read as JSON: {e}") from None


def run(test: E2ETest, top: str, token: str | None) -> str:
    """Runs the test and gives the folder of its records, from the top. Everything it makes
    outside the records lies in one temporary folder, or, for a test that pushes, in a branch of
    the repository, and it removes each."""
    took = _took(test, top)
    root = tempfile.mkdtemp(prefix="e2e-")
    clone = os.path.join(root, "clone")
    held = None
    try:
        head = _setup(test, top, clone)
        held = _heads(clone) if test.push else None
        claude = os.path.join(root, "claude")
        events = os.path.join(root, "hooks.jsonl")
        _settings(claude, events)
        stand_in = os.path.join(root, "stand-in")
        for folder in (stand_in, os.path.join(root, "stand-in-claude"), os.path.join(root, "tmp")):
            os.makedirs(folder)
        dirs = [d.replace("{top}", top).replace("{clone}", clone) for d in test.plugin_dirs]
        env = _logged_in(token, (claude, os.path.join(root, "stand-in-claude")))
        person = dict(env, CLAUDE_CONFIG_DIR=claude, TMPDIR=os.path.join(root, "tmp"))
        standing = dict(env, CLAUDE_CONFIG_DIR=os.path.join(root, "stand-in-claude"))
        session = str(uuid.uuid4())
        screen: list[str] = []
        turns = []
        for n in range(1, test.turns + 1):
            prompt = _ask(test.intent, "\n\n".join(screen), stand_in, standing)
            if prompt is None:
                break
            started = _now()
            begun = "--session-id" if n == 1 else "--resume"
            command = [
                *("claude", "-p", "--model", MODEL, "--permission-mode", "bypassPermissions"),
                *("--append-system-prompt", RULE, "--output-format", "stream-json", "--verbose"),
                *(word for d in dirs for word in ("--plugin-dir", d)),
                *(begun, session, prompt),
            ]
            try:
                done = subprocess.run(
                    command,
                    cwd=clone,
                    env=person,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=TURN_SECONDS,
                )
                code, shown = done.returncode, _screen(prompt, done.stdout)
            except subprocess.TimeoutExpired:
                code, shown = (
                    None,
                    f"> {prompt}\n(e2e.py stopped the turn after {TURN_SECONDS} s)",
                )
            screen.append(shown)
            turns.append(
                {"turn": n, "prompt": prompt, "started": started, "ended": _now(), "exit": code}
            )
            turns[-1]["screen"] = shown
            if code is None:
                break
            session = _session(events, session)
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        folder = os.path.join(test.records, test.name, stamp)
        records = RunRecords(os.path.join(top, folder), top, root, token)
        records.write("run.json", json.dumps(took, ensure_ascii=False, indent=1) + "\n")
        _keep(records, head, turns)
        return folder
    finally:
        if held is not None:
            _unpush(clone, held)
        shutil.rmtree(root)


def tried(records: str, path: str, top: str, token: str | None) -> str:
    """Has a stand-in of a deliverable's people try it, on a checkout of the branch that the run
    of the records made, and gives the folder of the try's records, from the top."""
    given = _json(path)
    for key, kind in TRY.items():
        if not isinstance(given, dict) or not isinstance(given.get(key), kind):
            raise Refused(f"{path} needs `{key}` as {kind.__name__}")
    diff = os.path.join(records, "branches", f"{given['branch']}.diff")
    if not os.path.isfile(diff):
        raise Refused(f"the run of {records} made no branch {given['branch']}")
    # The records give `<top>` for the top, which the test as given may name, such as its commits.
    with open(os.path.join(records, "run.json"), encoding="utf-8") as f:
        test = _test(json.loads(f.read().replace("<top>", top))["test"], path)
    test.push = False
    root = tempfile.mkdtemp(prefix="e2e-")
    try:
        clone = os.path.join(root, "clone")
        _setup(test, top, clone)
        if os.path.getsize(diff):
            _git(["apply", "--index", os.path.abspath(diff)], clone)
        for name, text in given["files"].items():
            with open(os.path.join(clone, name), "w", encoding="utf-8") as f:
                f.write(text)
        _git(["add", "-A"], clone)
        _git(["commit", "-q", "--allow-empty", "-m", "What the people have"], clone)
        claude = os.path.join(root, "claude")
        os.makedirs(claude)
        env = dict(
            _logged_in(token, (claude,)), CLAUDE_CONFIG_DIR=claude, PYTHONDONTWRITEBYTECODE="1"
        )
        command = [
            *("claude", "-p", "--model", MODEL, "--tools", "Bash,Read"),
            *("--permission-mode", "bypassPermissions"),
            *("--system-prompt", PEOPLE.format(intent=given["intent"], has=given["has"])),
            *("--append-system-prompt", RULE, "--output-format", "stream-json", "--verbose"),
            given["intent"],
        ]
        try:
            stream = subprocess.run(
                command,
                cwd=clone,
                env=env,
                capture_output=True,
                text=True,
                check=False,
                timeout=TURN_SECONDS,
            ).stdout
        except subprocess.TimeoutExpired as stopped:
            # What it printed before e2e.py stopped it, as text in either form the stop gives.
            out = stopped.stdout or ""
            stream = out.decode(errors="replace") if isinstance(out, bytes) else out
        name = os.path.basename(path).rsplit(".json", 1)[0]
        folder = os.path.join(records, "tries", name)
        kept = RunRecords(os.path.join(top, folder), top, root, token)
        kept.write("try.json", json.dumps(given, ensure_ascii=False, indent=1) + "\n")
        kept.write("stream.jsonl", stream)
        _git(["add", "-A"], clone)
        kept.write("changed.diff", _git(["diff", "--cached", "HEAD"], clone))
        return folder
    finally:
        shutil.rmtree(root)


def _took(test: E2ETest, top: str) -> dict[str, Any]:
    """What the run takes: the commit at the top, None where the top isn't a repository, whether
    the top holds changes beside it, Claude Code's version, the model, and the test as given."""
    inside = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=top,
        capture_output=True,
        text=True,
        check=False,
    )
    held = inside.returncode == 0 and os.path.realpath(inside.stdout.strip()) == os.path.realpath(
        top
    )
    commit = _git(["rev-parse", "HEAD"], top).strip() if held else None
    changed = bool(_git(["status", "--porcelain"], top).strip()) if held else False
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True, check=False)
    return {
        "commit": commit,
        "uncommitted": changed,
        "claude": version.stdout.strip(),
        "model": MODEL,
        "test": test.given,
    }


def _logged_in(token: str | None, configs: tuple[str, ...]) -> dict[str, str]:
    """The environment of each Claude Code of the run: the caller's, with none of their Claude
    Code's settings, and the developer's login, as the token where it's set, or else as a copy of
    the credentials file in each of the configuration folders."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}
    if token is not None:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = token
        return env
    for config in configs:
        shutil.copyfile(_credentials(), os.path.join(config, ".credentials.json"))
    return env


def _credentials() -> str:
    """The credentials file of the developer's own Claude Code, where it keeps the login on a
    container or a Linux machine."""
    config = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    return os.path.join(config, ".credentials.json")


def _setup(test: E2ETest, top: str, clone: str) -> str:
    """Clones the test's repository, which then pushes nowhere unless the test pushes, and makes
    the test's commits in it. Gives the last commit."""
    _git(["clone", "-q", test.repository, clone], os.path.dirname(clone))
    if not test.push:
        _git(["remote", "set-url", "--push", "origin", NO_PUSH], clone)
    for commit in test.commits:
        for path, text in commit.files.items():
            if isinstance(text, dict):
                with open(os.path.join(top, text["from"]), encoding="utf-8") as f:
                    text = f.read()
            full = os.path.join(clone, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as f:
                f.write(text)
        _git(["add", "-A"], clone)
        _git(["commit", "-q", "-m", commit.message], clone)
    return _git(["rev-parse", "HEAD"], clone).strip()


def _heads(clone: str) -> set[str]:
    """The name of each branch that the clone's repository holds now."""
    listed = _git(["ls-remote", "--heads", "origin"], clone)
    return {line.split("refs/heads/", 1)[1] for line in listed.splitlines()}


def _unpush(clone: str, held: set[str]) -> None:
    """Removes from the clone's repository each branch it holds now but the `held` ones."""
    for branch in sorted(_heads(clone) - held):
        _git(["push", "-q", "origin", "--delete", branch], clone)


def _git(args: list[str], cwd: str) -> str:
    done = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=dict(os.environ, **AUTHOR),
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode != 0:
        raise Refused(f"`git {' '.join(args)}` failed: {done.stderr.strip()}")
    return done.stdout


def _settings(claude: str, events: str) -> None:
    """Writes the configuration of the Claude Code under test: a hook on each event that keeps it
    in the events file, and nothing else, so that only the plugins under test change what it
    does."""
    command = " ".join(
        shlex.quote(word) for word in (sys.executable, os.path.abspath(__file__), "hook", events)
    )
    entry = [{"hooks": [{"type": "command", "command": command}]}]
    os.makedirs(claude)
    with open(os.path.join(claude, "settings.json"), "w", encoding="utf-8") as f:
        json.dump({"hooks": {event: entry for event in EVENTS}}, f, indent=2)


def _session(events: str, session: str) -> str:
    """The conversation that the next turn resumes: the one whose SessionStart came last, as a
    person's /clear starts a new one, or else the same."""
    started = [session]
    with open(events, "a+", encoding="utf-8") as f:
        f.seek(0)
        for line in f:
            payload = json.loads(line).get("payload")
            if isinstance(payload, dict) and payload.get("hook_event_name") == "SessionStart":
                started.append(payload["session_id"])
    return started[-1]


def _ask(intent: str, screen: str, cwd: str, env: dict[str, str]) -> str | None:
    """The stand-in's next prompt, or None where it's done. It runs with no tool, in a folder of
    its own, so it reads only its brief and the screen."""
    command = [
        *("claude", "-p", "--model", MODEL, "--tools", ""),
        *("--system-prompt", BRIEF.format(intent=intent), "--append-system-prompt", RULE),
        *("--json-schema", json.dumps(REPLY), "--output-format", "json"),
        f"What your screen shows so far:\n\n{screen}" if screen else "Your screen is empty.",
    ]
    done = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    try:
        reply = json.loads(done.stdout)["structured_output"]
        if reply["done"] is True:
            return None
        if reply["done"] is False and isinstance(reply["prompt"], str) and reply["prompt"]:
            return reply["prompt"]
    except (ValueError, TypeError, KeyError):
        pass
    raise Refused(f"the stand-in gave no reply of its form: {done.stdout[:500]}{done.stderr[:500]}")


def _screen(prompt: str, stdout: str) -> str:
    """What the person's screen shows of a turn, from Claude Code's stream-json: the prompt, and
    what _shown gives of each event of the main conversation. A subagent's work stays off it, as
    Claude Code folds it away."""
    lines = [f"> {prompt}"]
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("parent_tool_use_id") is None:
            lines += _shown(event)
    return "\n".join(lines)


def _shown(event: dict[str, Any]) -> list[str]:
    """What the screen shows of an event of the main conversation: its text and calls, each call
    that failed or was stopped with why, and a turn that failed."""
    kind = event.get("type")
    shown = (
        [_result(str(event.get("result")))] if kind == "result" and event.get("is_error") else []
    )
    # Only a message of the model or of a tool's result holds blocks to show.
    content = event.get("message", {}).get("content") if kind in ("assistant", "user") else None
    for block in content if isinstance(content, list) else []:
        if block.get("type") == "text":
            shown.append(block["text"])
        elif block.get("type") == "tool_use":
            shown.append(_call(block["name"], block.get("input", {})))
        elif block.get("type") == "tool_result" and block.get("is_error"):
            shown.append(_result(_text(block.get("content"))))
    return shown


def _call(tool: str, tool_input: dict[str, Any]) -> str:
    shown = tool_input.get(SHOWN.get(tool, ""))
    return f"● {tool}({shown})" if isinstance(shown, str) else f"● {tool}"


def _result(text: str) -> str:
    first, *rest = text.splitlines() or [""]
    return "\n".join([f"  ⎿  {first}", *(f"     {line}" for line in rest)])


def _text(content: Any) -> str:
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict))
    return str(content)


def _keep(records: RunRecords, head: str, turns: list[dict[str, Any]]) -> None:
    """Writes the run's records from the run's temporary folder: the turns, the hook events, the
    transcripts, the plugins' temporary files, and what the run changed in the clone, and on each
    branch it made, after the commit `head`."""
    root = records.temporary
    records.write(
        "turns.jsonl", "".join(json.dumps(turn, ensure_ascii=False) + "\n" for turn in turns)
    )
    events = os.path.join(root, "hooks.jsonl")
    records.write("hooks.jsonl", _read(events) if os.path.exists(events) else "")
    projects = os.path.join(root, "claude", "projects")
    for project in os.listdir(projects) if os.path.isdir(projects) else []:
        for path in _files(os.path.join(projects, project)):
            text = _read(os.path.join(projects, project, path))
            kept = _transcript(text) if path.endswith(".jsonl") else text
            records.write(os.path.join("transcripts", path), kept)
    tmp = os.path.join(root, "tmp")
    for path in _files(tmp):
        # Claude Code's own temporary files, such as a background task's output, aren't a plugin's.
        if not path.startswith("claude-"):
            records.write(os.path.join("tmp", path), _read(os.path.join(tmp, path)))
    clone = os.path.join(root, "clone")
    _git(["add", "-A"], clone)
    records.write("run.diff", _git(["diff", "--cached", head], clone))
    checked_out = _git(["rev-parse", "--abbrev-ref", "HEAD"], clone).strip()
    for branch in _git(["for-each-ref", "--format=%(refname:short)", "refs/heads"], clone).split():
        if branch != checked_out:
            records.write(f"branches/{branch}.diff", _git(["diff", head, branch], clone))


def _transcript(text: str) -> str:
    """The transcript's lines without those of the account and the requests to the API."""
    kept = []
    for line in text.splitlines():
        entry = json.loads(line)
        attachment = entry.get("attachment")
        dropped = isinstance(attachment, dict) and attachment.get("type") in DROPPED_ATTACHMENTS
        if entry.get("type") not in DROPPED and not dropped:
            kept.append(json.dumps(entry, ensure_ascii=False) + "\n")
    return "".join(kept)


def _files(top: str) -> list[str]:
    """Each file under the folder, by its path from it."""
    return sorted(
        os.path.relpath(os.path.join(folder, name), top)
        for folder, _, names in os.walk(top)
        for name in names
    )


def _read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _now() -> str:
    """The time now, in UTC, to the microsecond."""
    seconds = time.time()
    return (
        time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(seconds)) + f".{int(seconds % 1 * 1e6):06d}Z"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

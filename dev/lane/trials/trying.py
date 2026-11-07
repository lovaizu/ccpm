"""What every plugin's trials stand on: the folder of its own each run of a trial writes in,
Claude Code started on copies of plugins as their user starts it, in `claude -p` or in an
interactive session, a conversation gone on with message by message, its record kept, and what the
records of the agents it started show."""

from __future__ import annotations

import glob
import importlib.util
import json
import os
import pty
import queue
import re
import select
import shlex
import signal
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Callable
from typing import Any

# The seconds Claude Code is given, after a result, to open a turn of its own; it opens one at once
# for what has already reached it, as its records show, such as an agent's message queued while
# the main conversation worked.
QUIET = 5
HERE = os.path.dirname(os.path.abspath(__file__))
# The folder a trial writes in is made as a test's is, by testing.py, kept in the folder above.
sys.path.insert(0, os.path.dirname(HERE))
import testing

# How Claude Code keeps its records is read by record.py beside this module, loaded from its
# file, so a plugin's trials standing on this module meet none of their own modules of that
# name.
RECORD = os.path.join(HERE, "record.py")
FOUND = importlib.util.spec_from_file_location("record", os.path.normpath(RECORD))
assert FOUND and FOUND.loader
record = importlib.util.module_from_spec(FOUND)
FOUND.loader.exec_module(record)


# What .claude/rules/dev.md tells every Claude Code a developer starts, added to its system prompt
# so the ask the trial makes stays as the plugin's user would write it.
LIMITS = (
    "Install nothing, and send nothing to a service outside the repository's git and GitHub, such"
    " as a translator or a web API. Fetching a public page to read it is allowed."
)


def folder(plugin: str, name: str) -> str:
    """A new folder of the plugin's for a run of the trial of the name, in the system's temporary
    folder as Q12 of plugins/rn/domain/best-practices/plugin/best-practice.md has it, outside any
    ccpm
    clone, so the conversations started in it load none of its instructions; its path is printed
    first, for whoever runs the trial to find what the run writes there. The path is given with
    every link in it followed, as Claude Code names the folder of a conversation's records by it,
    and macOS's temporary folder is reached through a link."""
    made = os.path.realpath(testing.temporary(plugin, name))
    print("folder:", made, flush=True)
    return made


class Conversation:
    """One conversation with Claude Code on the copies of plugins in place of the installed ones,
    as their user has it, in one live run of Claude Code: the caller reads each reply of the main
    conversation and, as the user does, either sends the next message or waits for the next reply
    without sending, as where the reply says an agent in the background is still at work; a fresh
    conversation is another Conversation. The run starts at the first message and ends on close.
    wait is the minutes a wait for a reply is given, and a wait for the agents in the background
    where send waits for them, 10 where it is 0, as Claude Code waits when given one prompt; env
    is set over the environment Claude Code runs in."""

    def __init__(
        self,
        plugins: list[str],
        cwd: str | None = None,
        wait: int = 0,
        env: dict[str, str] | None = None,
    ) -> None:
        self.plugins, self.cwd, self.env = plugins, cwd, {**fresh(), **(env or {})}
        self.wait = (wait or 10) * 60
        self.run: subprocess.Popen[str] | None = None
        # Whether an agent it started in the background still runs, kept from reply to reply, as
        # Claude Code lists the agents running only when the list changes; a caller that cannot
        # read a reply, as a script cannot, waits for the next while one runs.
        self.running = False
        self.printed: queue.Queue[str | None] = queue.Queue()
        self.errors: list[str] = []

    def start(self) -> subprocess.Popen[str]:
        """Starts Claude Code, reading each message as a line of stream-json from its input and
        printing what it does as stream-json; a thread hands on each line it prints, and None once
        it has ended, and another keeps what it prints as errors."""
        names = []
        for plugin in self.plugins:
            with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
                names.append(json.load(f)["name"])
        command = ["claude", "-p", "--input-format", "stream-json"]
        command += ["--output-format", "stream-json", "--verbose"]
        for plugin in self.plugins:
            command += ["--plugin-dir", plugin]
        # The copy stands in for the installed plugin, which would otherwise run beside it.
        installed = {f"{name}@ccpm": False for name in names}
        command += ["--model", "opus", "--settings", json.dumps({"enabledPlugins": installed})]
        command += ["--permission-mode", "bypassPermissions", "--append-system-prompt", LIMITS]
        run = subprocess.Popen(
            command,
            cwd=self.cwd,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        def hand_on() -> None:
            assert run.stdout
            for line in run.stdout:
                self.printed.put(line)
            self.printed.put(None)

        threading.Thread(target=hand_on, daemon=True).start()
        threading.Thread(target=self.errors.extend, args=(run.stderr,), daemon=True).start()
        return run

    def send(self, prompt: str, record: str | None = None, idle: bool = False) -> dict[str, Any]:
        """Sends prompt and gives the main conversation's reply, as reply does, the turn for the
        message being open at once; where idle, the reply after which no agent runs in the
        background either, as Claude Code waits for them when given one prompt."""
        self.run = self.run or self.start()
        assert self.run.stdin
        message = {"type": "user", "message": {"role": "user", "content": prompt}}
        self.run.stdin.write(json.dumps(message) + "\n")
        self.run.stdin.flush()
        return self.read(record, True, idle)

    def reply(self, record: str | None = None) -> dict[str, Any]:
        """Sends nothing and gives the main conversation's next reply, as the user waits for it
        where the last asked them nothing: Claude Code opens a turn of its own when an agent in the
        background ends or sends it a message. Stops where no turn opens within the wait."""
        return self.read(record, False, False)

    def read(self, record: str | None, due: bool, idle: bool) -> dict[str, Any]:
        """Reads what Claude Code prints until the main conversation has replied, and gives its
        result, the last line Claude Code printed for it as stream-json, such as its session_id;
        due is whether a turn is to open at once, as for a message sent, and idle is send's. Given
        record, it adds there each line as it comes, kept before a failed run stops the trial.
        Stops where Claude Code ends, gives a result that is an error, opens no turn within the
        wait where none is due, or, where idle, still has an agent running the wait after the
        reply."""
        # Claude Code gives a result at the end of each of its turns, and opens a new turn, by an
        # init, for a message sent and on its own for an agent in the background that ends or
        # sends the main conversation a message; meanwhile it prints what those agents do, and
        # lists the agents running each time the list changes. The main conversation has replied
        # at a result after which no turn opens in QUIET seconds, whatever the agents print.
        assert self.run
        result: dict[str, Any] | None = None
        opened, since = due, time.monotonic()
        # The end of the wait: for a reply where none is due, and where idle for the agents, from
        # the first result.
        until = None if due else since + self.wait
        with open(record or os.devnull, "a", encoding="utf-8") as kept:
            while True:
                if opened:
                    left: float | None = None
                elif result and not (idle and self.running):
                    left = max(0, since + QUIET - time.monotonic())
                else:
                    assert until is not None
                    left = max(0, until - time.monotonic())
                try:
                    line = self.printed.get(timeout=left)
                except queue.Empty:
                    if result and not (idle and self.running):
                        return result
                    if result:
                        raise SystemExit(
                            f"agents in the background still running {self.wait // 60} minutes"
                            " after the reply; give a longer wait"
                        ) from None
                    raise SystemExit(
                        f"no reply in {self.wait // 60} minutes of waiting; give a longer wait"
                    ) from None
                if line is None:
                    code = self.run.wait()
                    raise SystemExit(f"claude exited {code}: {''.join(self.errors)}")
                kept.write(line)
                kept.flush()
                event = json.loads(line)
                if event.get("subtype") == "background_tasks_changed":
                    self.running = bool(event.get("tasks"))
                    since = time.monotonic() if idle else since
                elif event.get("subtype") == "init":
                    result, opened = None, True
                elif event.get("type") == "result":
                    if event.get("is_error"):
                        raise SystemExit(f"claude gave an error: {event.get('result')}")
                    result, opened, since = event, False, time.monotonic()
                    until = until or since + self.wait

    def close(self) -> None:
        """Ends the conversation's run of Claude Code, where it started one."""
        if self.run:
            assert self.run.stdin
            self.run.stdin.close()
            self.run.wait()
            self.run = None


def claude(
    prompt: str,
    plugins: list[str],
    cwd: str | None = None,
    wait: int = 0,
    record: str | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Runs a fresh conversation of the one message prompt, as Conversation and its send have it,
    and gives its result once no agent runs in the background, as Claude Code given one prompt
    does."""
    conversation = Conversation(plugins, cwd, wait, env)
    try:
        return conversation.send(prompt, record, idle=True)
    finally:
        conversation.close()


# What Claude Code shows, its words joined, as it asks whether a folder is trusted, and whether its
# user takes on the bypassPermissions mode the session is started in: each the second choice.
SECOND = ("Itrustthisfolder", "Yes,Iaccept")
# What Claude Code shows, its words joined, on the screens a new configuration folder starts with,
# each passed by Enter as a user takes its first choice: the text style, and a note to go on from.
ONBOARDING = ("Choosethetextstyle", "PressEntertocontinue")
# What Claude Code shows, its words joined, as it asks the person to allow a call, whatever the
# permission mode.
PERMISSION = "Doyouwanttoproceed?"
# A move of the cursor to the right, by which Claude Code places words apart, and any other control
# sequence.
RIGHT = re.compile(r"\x1b\[(\d*)C")
CONTROL = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07]*\x07")
# What the Stop hook of an interactive session runs: its event kept as a line of the file given.
STOP = """import json, sys

with open(sys.argv[1], "a", encoding="utf-8") as f:
    f.write(json.dumps(json.load(sys.stdin)) + "\\n")
"""


def interactive(
    prompt: str,
    plugins: list[str],
    cwd: str,
    place: str,
    wait: int = 20,
    answer: Callable[[str], str | None] | None = None,
    permit: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    """Runs a fresh interactive session of Claude Code on the copies of plugins, in cwd, given the
    one message prompt as its user types it, and gives its session_id once the main conversation
    has stopped with no agent in the background left, as a Stop hook given in the settings tells
    it in `<place>/stops.jsonl`, and no plugin's Stop hook kept it going there, as went_on reads
    the session's record; what the terminal shows is kept in `<place>/terminal.txt`. An
    interactive session is what starts an agent again once an agent it started in the background
    has ended, which `claude -p` does not. Given answer, the session goes on as its user does:
    at each such stop, answer is given the main conversation's last message, and the text it gives
    back is typed as the next message; "" waits for the next stop, as where the message asks the
    user nothing, and None ends the session there. Where Claude Code asks the person to allow a
    call, permit is given what the screen shows and the number of the choice it gives back is
    typed, as a person answers; without permit, the session stops there, naming the call. Stops
    where the session does not stop so within wait minutes in all."""
    names = []
    for plugin in plugins:
        with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            names.append(json.load(f)["name"])
    session = str(uuid.uuid4())
    stops = os.path.join(place, "stops.jsonl")
    # Each Stop event is kept as a line of its own, by a script in the run's folder.
    script = os.path.join(place, "stop.py")
    with open(script, "w", encoding="utf-8") as f:
        f.write(STOP)
    keep = f"{shlex.quote(sys.executable)} {shlex.quote(script)} {shlex.quote(stops)}"
    hooks = {"Stop": [{"hooks": [{"type": "command", "command": keep}]}]}
    settings = {"enabledPlugins": {f"{name}@ccpm": False for name in names}, "hooks": hooks}
    command = ["claude", "--session-id", session, "--model", "opus"]
    for plugin in plugins:
        command += ["--plugin-dir", plugin]
    command += ["--settings", json.dumps(settings), "--permission-mode", "bypassPermissions"]
    command += ["--append-system-prompt", LIMITS]
    command.append(prompt)
    # The environment is made before the fork, so the configuration folder fresh makes the first
    # time is this process's too, where record.py reads the session's records after.
    env = {**fresh(), "TERM": "xterm-256color"}
    pid, terminal = pty.fork()
    if pid == 0:
        os.chdir(cwd)
        os.execvpe(command[0], command, env)
    until = time.monotonic() + wait * 60
    seen, passed, handled = b"", set(), 0
    try:
        with open(os.path.join(place, "terminal.txt"), "ab") as shown:
            while time.monotonic() < until:
                ready, _, _ = select.select([terminal], [], [], 1)
                if ready:
                    try:
                        read = os.read(terminal, 65536)
                    except OSError:
                        raise SystemExit(f"claude ended: see {shown.name}") from None
                    shown.write(read)
                    shown.flush()
                    seen = (seen + read)[-4096:]
                joined = "".join(text_of(seen).split())
                # The folder is the run's own, made by the trial, so it is trusted as Claude
                # Code asks of a folder it has not opened before, and the mode the test starts it
                # in taken on: the second choice, below the first, each asked once.
                first = [screen for screen in SECOND if screen in joined and screen not in passed]
                if first:
                    time.sleep(1)
                    os.write(terminal, b"\x1b[B")
                    time.sleep(1)
                    os.write(terminal, b"\r")
                    passed.add(first[0])
                    seen = b""
                elif any(screen in joined for screen in ONBOARDING):
                    time.sleep(1)
                    os.write(terminal, b"\r")
                    seen = b""
                elif PERMISSION in joined:
                    if not permit:
                        raise SystemExit(f"Claude Code asked to allow a call: {text_of(seen)}")
                    time.sleep(1)
                    os.write(terminal, permit(text_of(seen)).strip()[:1].encode())
                    seen = b""
                for stop in kept(stops)[handled:]:
                    idle_ = "background_tasks" in stop and not stop["background_tasks"]
                    going = went_on(stop, handled + 1) if idle_ else False
                    # Its Stop hooks have not all ended yet; the stop is read again.
                    if going is None:
                        break
                    handled += 1
                    if not idle_ or going:
                        continue
                    said = answer(str(stop.get("last_assistant_message") or "")) if answer else None
                    if said is None:
                        return {"session_id": session}
                    if said:
                        os.write(terminal, " ".join(said.split()).encode())
                        time.sleep(1)
                        os.write(terminal, b"\r")
        raise SystemExit(f"the session was not idle within {wait} minutes; give a longer wait")
    finally:
        os.kill(pid, signal.SIGTERM)
        os.waitpid(pid, 0)
        os.close(terminal)


def text_of(seen: bytes) -> str:
    """What the screen shows in what the terminal was sent, its words placed apart as the cursor
    moves them, its other control sequences left out."""
    said = seen.decode("utf-8", "replace")
    said = RIGHT.sub(lambda m: " " * int(m[1] or 1), said)
    return CONTROL.sub("", said)


def fresh() -> dict[str, str]:
    """The environment each Claude Code a test starts runs in, as any user starts it in a terminal
    of their own: nothing in it of a Claude Code session it may be run from, as a session started
    with that is taken as its child and keeps no record of its own; and CLAUDE_CONFIG_DIR a
    configuration folder of the test's own, so Claude Code reads none of the developer's
    CLAUDE.md, settings or memory, logged in by the developer's login, as login gives it."""
    if not CONFIG:
        CONFIG.append(testing.temporary("lane", "claude-config"))
        # The records are read from the test's own folder too, by record.py.
        os.environ["CLAUDE_CONFIG_DIR"] = CONFIG[0]
    found = {
        k: v
        for k, v in os.environ.items()
        if not (k.startswith("CLAUDE_CODE_") or k in ("CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT"))
    }
    return {**found, **login()}


# The developer's own configuration folder, where Claude Code keeps their login, as it is before a
# test sets its own.
DEVELOPER = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
# The test's own configuration folder, made the first time a Claude Code is started.
CONFIG: list[str] = []


def login() -> dict[str, str]:
    """The developer's login, as Claude Code takes one with a configuration folder of its own:
    nothing where ANTHROPIC_API_KEY is set, which the environment keeps; CLAUDE_CODE_OAUTH_TOKEN as
    set, such as from `claude setup-token`; else the access token of the login Claude Code keeps in
    the developer's `.credentials.json`, read, never written, at each start, as their own Claude
    Code renews it. Stops where there is none."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return {}
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        try:
            with open(os.path.join(DEVELOPER, ".credentials.json"), encoding="utf-8") as f:
                token = json.load(f)["claudeAiOauth"]["accessToken"]
        except (OSError, ValueError, KeyError) as e:
            raise SystemExit(
                f"no login for the test's Claude Code ({e}): set CLAUDE_CODE_OAUTH_TOKEN to a token"
                " `claude setup-token` gives, or ANTHROPIC_API_KEY"
            ) from None
    return {"CLAUDE_CODE_OAUTH_TOKEN": token}


def went_on(stop: dict[str, Any], number: int) -> bool | None:
    """Whether a Stop hook kept the main conversation going at the stop, the number-th of the
    session: Claude Code records each stop's hooks once they have all ended, as an entry of subtype
    `stop_hook_summary` in the session's record, with the reason of each hook that blocked the stop
    in `hookErrors`. A plugin's Stop hook, such as Lane's for a start due, runs beside the one that
    keeps the stop, so the stop alone does not say the session stopped. None where the record holds
    no such entry for the stop yet."""
    entries = record.read(str(stop.get("transcript_path", ""))) or []
    summaries = [e for e in entries if e.get("subtype") == "stop_hook_summary"]
    if len(summaries) < number:
        return None
    return bool(summaries[number - 1].get("hookErrors"))


def kept(stops: str) -> list[dict[str, Any]]:
    """Each Stop event kept in the file at the path, in order; none where it is not there."""
    try:
        with open(stops, encoding="utf-8") as f:
            return [json.loads(line) for line in f.read().splitlines()]
    except FileNotFoundError:
        return []


# The stand-in's system prompt: what it is and that it has nothing beyond the prompt.
STANDS_IN = (
    "You stand in for a person, and answer in text alone. You have no tools: you cannot run, read"
    " or look up anything, and you have only what the message shows."
)


def stand_in(prompt: str, cwd: str) -> dict[str, Any]:
    """The JSON object an AI gives for the prompt, as a stand-in for a person gives its answer, on
    Opus, with no tool, no plugin and no record kept, run in the folder given, which holds nothing
    of the plugins tried. Claude Code's own system prompt gives way to STANDS_IN, as it tells of
    tools and a folder to work in, and with no tool the stand-in wrote calls to them as text
    without end."""
    command = ["claude", "-p", "--model", "opus", "--tools", "", "--no-session-persistence"]
    command += ["--output-format", "json", "--settings", json.dumps({"enabledPlugins": {}})]
    command += ["--system-prompt", STANDS_IN]
    done = subprocess.run(
        command,
        input=prompt,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=fresh(),
        timeout=600,
        check=True,
    )
    said = str(json.loads(done.stdout)["result"])
    found = re.search(r"\{.*\}", said, re.DOTALL)
    if not found:
        raise SystemExit(f"the stand-in gave no JSON: {said}")
    return json.loads(found.group(0))


# The line a caller heads the person's answer with as it resumes the role that asked, the one
# form the plugin best practice's roles take as the person's words.
ANSWERED = "The person's answer, word for word:"
# The key of the stand-in's answer that counts the points of a message, the same for every plugin
# that asks a person, as a point is the person's to count, not the plugin's.
POINTS = """- "points": how many separate answers the message needs from you, as a number: one
  question to decide, or one fact to confirm, is 1, however long the reasons, the options or the
  examples around it; a second question, or a second thing it asks you to confirm or to tell,
  adds 1;"""


# The prompt the stand-in for a person is given where Claude Code asks them to allow a call.
PERMITS = """You stand in for a person using Claude Code. Here is who you are and what you truly
want:

{intent}

Claude Code now shows you this, asking you to allow something:

<screen>
{screen}
</screen>

Choose as that person would, from what the screen shows and what you want. Give only one JSON
object, with no other text: {{"choice": the number of the choice you take, "why": one sentence}}."""


def permitted(intent: str, screen: str, cwd: str) -> str:
    """The number of the choice the stand-in for the person of the intent takes on the screen
    where Claude Code asks them to allow a call, printing it and why."""
    chose = stand_in(PERMITS.format(intent=intent, screen=screen[-3000:]), cwd)
    print(f"  permission: chose {chose.get('choice')}: {chose.get('why')}", flush=True)
    return str(chose.get("choice", ""))


def finds(who: str, keys: str) -> str:
    """The prompt the stand-in for a person is given each message by, `{intent}`, `{said}` and
    `{message}` left to fill: who they stand in for, then the conversation, then the keys of the
    JSON it answers with."""
    return (
        who
        + """

{intent}

The conversation so far, oldest first:

{said}

The AI's newest message to you:

<message>
{message}
</message>

Answer it as that person would. Also judge the message as that person, from what you know. Give
only one JSON object, with no other text, with these keys:
"""
        + keys
    )


def heard(finds: str, intent: str, said: list[str], message: str, cwd: str) -> dict[str, Any]:
    """What the stand-in for the person, given the prompt `finds` with its intent, the conversation
    so far and the newest message, says of the message, as the JSON object it gives."""
    return stand_in(
        finds.format(intent=intent, said="\n\n".join(said) or "(none)", message=message), cwd
    )


def committed(repo: str, files: dict[str, str]) -> None:
    """Writes each file at its path in the repository's folder, and commits them all in a git
    repository made there."""
    for path, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(repo, path)) or repo, exist_ok=True)
        with open(os.path.join(repo, path), "w", encoding="utf-8") as f:
            f.write(text)
    for args in (["init", "-q", "-b", "main"], ["add", "."]):
        subprocess.run(["git", "-C", repo, *args], check=True)
    who = ["-c", "user.name=e2e", "-c", "user.email=e2e@example.com"]
    subprocess.run(["git", "-C", repo, *who, "commit", "-q", "-m", "start"], check=True)


def verdict(untried: list[str], wrong: list[str]) -> bool:
    """Whether a trial's run counted and passed, printing which, and why where it did not."""
    if untried:
        print("  not counted: " + "; ".join(untried))
        if wrong:
            print("  and wrong: " + "; ".join(wrong))
        return False
    print("  passed" if not wrong else "  failed: " + "; ".join(wrong))
    return not wrong


def main(run: Callable[[int], bool]) -> None:
    """Runs a trial's run as many times as the command line gives, three by default, numbered
    from the second word where given, and exits 0 where every run passed and counted."""
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    first = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    passed = [run(n) for n in range(first, first + runs)]
    print(f"{sum(passed)} of {runs} runs passed")
    sys.exit(0 if all(passed) else 1)


def idle(stops: str) -> bool:
    """Whether the main conversation's last Stop, as kept in the file at the path, says that no
    agent is left in the background."""
    try:
        with open(stops, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return False
    last = json.loads(lines[-1]) if lines else {}
    return "background_tasks" in last and not last["background_tasks"]


def agents(session: str) -> list[str]:
    """The path of the record of each agent the session started."""
    return glob.glob(record.subagent(record.conversation(session), "*"))


def show(path: str) -> None:
    """Prints a record's path and, of what it holds, each message sent, each tool used and each
    hook stop."""
    print("record:", path)
    for entry in record.read(path) or []:
        # Claude Code's copy of each request says again what the agent did.
        if entry.get("type") == "api-request-blob":
            continue
        if isinstance(entry.get("origin"), dict):
            print("  message:", entry["origin"].get("body"))
        if record.told(entry):
            print("  stop:", record.text(entry))
        for part in record.blocks(entry):
            if part.get("type") == "tool_use":
                print("  use:", part["name"], json.dumps(part["input"], ensure_ascii=False))
            elif part.get("type") == "tool_result" and part.get("is_error"):
                print("  stop:", part.get("content"))

"""What Turn's E2E tests stand on: the repository of `tidy`, a tool that sorts a Downloads folder;
copies of Turn and pin for each run; an interactive session of Claude Code, as Turn's roles run in
the background and `claude -p` does not start `up` again once a role it started has ended; the
person, stood in for by an AI that answers from an intent written beforehand and never shown Turn,
and says of each message what it put to them; and the run judged from its records and its work,
the work by the stand-in as the person would judge it."""

from __future__ import annotations

import datetime
import json
import os
import pty
import re
import select
import shlex
import shutil
import signal
import subprocess
import sys
import time
import uuid
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "dev", "lane", "trials"))

import trying

PLUGINS = {name: os.path.join(ROOT, "plugins", name) for name in ("turn", "pin")}
# The most messages put to the person before a run is stopped as one that does not end.
TURNS = 40
# `tidy`: tidy.py moves each file of a folder into a folder named after its kind, by its extension,
# and shows what it would move with --dry-run; a file of no extension stays where it is.
TIDY_PY = """\"\"\"tidy: `python3 tidy.py [--dry-run] <folder>` moves each file of the folder into a
folder named after its kind.\"\"\"

import argparse
import os
import shutil
import sys

KINDS = {".jpg": "images", ".png": "images", ".pdf": "documents", ".zip": "archives"}


def main(argv):
    parser = argparse.ArgumentParser(prog="tidy")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("folder")
    args = parser.parse_args(argv)
    for name in sorted(os.listdir(args.folder)):
        path = os.path.join(args.folder, name)
        extension = os.path.splitext(name)[1].lower()
        if not extension or os.path.isdir(path):
            continue
        kind = KINDS.get(extension, "other")
        print(f"{name} -> {kind}/")
        if not args.dry_run:
            os.makedirs(os.path.join(args.folder, kind), exist_ok=True)
            shutil.move(path, os.path.join(args.folder, kind, name))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
"""
TIDY = {
    "tidy.py": TIDY_PY,
    "LICENSE": "MIT License\n\nCopyright (c) 2026 the tidy authors\n",
}
FINDS = """You stand in for the person an AI is making a work for. Here is who you are and what you
truly want; the AI cannot see it:

{intent}

The conversation so far, oldest first:

{said}

The AI's newest message to you:

<message>
{message}
</message>

Answer it as that person would. Also judge the message as that person, from what you know. Give
only one JSON object, with no other text, with these keys:
- "answer": your answer to the message, as you would write it, or "" where it asks you nothing;
- "asks": true where the message asks you anything or waits for your answer; otherwise false;
- "points": how many separate answers the message needs from you, as a number: one question to
  decide, or one fact to confirm, is 1, however long the reasons around it; a second question, or
  a second thing it asks you to confirm or to tell, adds 1;
- "asks_fact": true where it asks you something about the repository that the AI could read for
  itself, rather than showing you what it found for you to confirm; otherwise false;
- "asks_settled": true where it asks you again something you are said, above, to have settled
  already, or something you already answered in this conversation; otherwise false;
- "not_yours": true where it asks you to decide something your wants above show you do not care
  about and that follows from what you want and the repository; otherwise false;
- "finished": true where the message says the work is done and asks you nothing; otherwise
  false."""
JUDGES = """You stand in for the person an AI made a work for. Here is who you are and what you
truly want:

{intent}

The work, each file as it is:

{work}

Judge the work as that person, about to put it to use. Give only one JSON object, with no other
text: {{"changes": [each change you would make or ask for before you put it to use, in a short
sentence each; none where you would use it as it is]}}."""


def asked(prompt: str, cwd: str) -> dict[str, Any]:
    """The JSON object an AI gives for the prompt, on Opus, with no tool, no plugin and no record
    kept, run in the folder given, which holds nothing of Turn's."""
    command = ["claude", "-p", "--model", "opus", "--tools", "", "--no-session-persistence"]
    command += ["--output-format", "json", "--settings", json.dumps({"enabledPlugins": {}})]
    done = subprocess.run(
        command, input=prompt, capture_output=True, text=True, cwd=cwd, timeout=600, check=True
    )
    said = str(json.loads(done.stdout)["result"])
    found = re.search(r"\{.*\}", said, re.DOTALL)
    if not found:
        raise SystemExit(f"the stand-in gave no JSON: {said}")
    return json.loads(found.group(0))


def made(place: str, files: dict[str, str] | None = None) -> tuple[str, dict[str, str]]:
    """The repository of the run, `tidy` in its folder, with the files given beside tidy's and all
    committed, and a copy of Turn and of pin beside it; gives the repository and the copies'
    folders by name."""
    repo = os.path.join(place, "tidy")
    for path, text in {**TIDY, **(files or {})}.items():
        os.makedirs(os.path.dirname(os.path.join(repo, path)) or repo, exist_ok=True)
        with open(os.path.join(repo, path), "w", encoding="utf-8") as f:
            f.write(text)
    for args in (["init", "-q", "-b", "main"], ["add", "."]):
        subprocess.run(["git", "-C", repo, *args], check=True)
    who = ["-c", "user.name=e2e", "-c", "user.email=e2e@example.com"]
    subprocess.run(["git", "-C", repo, *who, "commit", "-q", "-m", "tidy"], check=True)
    copies = {}
    for name, source in PLUGINS.items():
        copies[name] = os.path.join(place, "plugins", name)
        # Lane's code lies in Turn through a link into the marketplace; the copy takes it whole.
        shutil.copytree(source, copies[name], symlinks=False)
    return repo, copies


class Session:
    """An interactive session of Claude Code on the copies of plugins, in the repository, as its
    user has it in a terminal: started with the first message, each next message typed once the
    main conversation has stopped, and each stop's last message and its agents in the background
    kept by a Stop hook in `<place>/stops.jsonl`; what the terminal shows is kept in
    `<place>/terminal.txt`."""

    def __init__(self, plugins: list[str], cwd: str, place: str) -> None:
        self.place, self.stops = place, os.path.join(place, "stops.jsonl")
        self.session = str(uuid.uuid4())
        script = os.path.join(place, "stop.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(trying.STOP)
        keep = f"{shlex.quote(sys.executable)} {shlex.quote(script)} {shlex.quote(self.stops)}"
        names = []
        for plugin in plugins:
            with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
                names.append(json.load(f)["name"])
        settings = {
            "enabledPlugins": {f"{name}@ccpm": False for name in names},
            "hooks": {"Stop": [{"hooks": [{"type": "command", "command": keep}]}]},
        }
        self.command = ["claude", "--session-id", self.session, "--model", "opus"]
        for plugin in plugins:
            self.command += ["--plugin-dir", plugin]
        self.command += [
            "--settings",
            json.dumps(settings),
            "--permission-mode",
            "bypassPermissions",
        ]
        self.cwd, self.pid, self.terminal, self.seen = cwd, 0, -1, 0

    def stopped(self) -> list[dict[str, Any]]:
        """Each Stop event kept so far."""
        try:
            with open(self.stops, encoding="utf-8") as f:
                return [json.loads(line) for line in f.read().splitlines()]
        except FileNotFoundError:
            return []

    def start(self, message: str) -> None:
        """Starts Claude Code with the first message, as its user types it."""
        pid, terminal = pty.fork()
        if pid == 0:
            os.chdir(self.cwd)
            env = {**trying.fresh(), "TERM": "xterm-256color"}
            os.execvpe(self.command[0], [*self.command, message], env)
        self.pid, self.terminal = pid, terminal

    def type(self, message: str) -> None:
        """Types the message, on one line, and sends it."""
        os.write(self.terminal, " ".join(message.split()).encode())
        time.sleep(1)
        os.write(self.terminal, b"\r")

    def next_stop(self, minutes: int) -> dict[str, Any]:
        """The next Stop of the main conversation with no agent left in the background, reading
        what the terminal shows meanwhile and trusting the run's folder as Claude Code asks."""
        until = time.monotonic() + minutes * 60
        shown, trusted = b"", False
        with open(os.path.join(self.place, "terminal.txt"), "ab") as kept:
            while time.monotonic() < until:
                ready, _, _ = select.select([self.terminal], [], [], 1)
                if ready:
                    try:
                        read = os.read(self.terminal, 65536)
                    except OSError:
                        raise SystemExit(f"claude ended: see {kept.name}") from None
                    kept.write(read)
                    kept.flush()
                    shown = (shown + read)[-4096:]
                if not trusted and trying.TRUST in shown:
                    time.sleep(1)
                    os.write(self.terminal, b"\x1b[B")
                    time.sleep(1)
                    os.write(self.terminal, b"\r")
                    trusted = True
                stops = self.stopped()
                for stop in stops[self.seen :]:
                    self.seen += 1
                    if "background_tasks" in stop and not stop["background_tasks"]:
                        return stop
        raise SystemExit(f"the session did not stop within {minutes} minutes")

    def close(self) -> None:
        """Ends Claude Code."""
        if self.pid:
            os.kill(self.pid, signal.SIGTERM)
            os.waitpid(self.pid, 0)
            os.close(self.terminal)
            self.pid = 0


def talked(session: Session, first: str, place: str, intent: str, minutes: int = 90) -> list[dict]:
    """Each message the main conversation put to the person, with what the person said of it, from
    the first message until Turn says the work is done; the person answers from the intent, in a
    folder of its own in the run's folder. A stop that asks the person nothing, as where Turn is
    still at work, is waited past."""
    alone = os.path.join(place, "person")
    os.makedirs(alone, exist_ok=True)
    said: list[str] = []
    turns: list[dict[str, Any]] = []
    session.start(first)
    until = time.monotonic() + minutes * 60
    while len(turns) < TURNS:
        left = max(1, int((until - time.monotonic()) / 60))
        message = str(session.next_stop(left).get("last_assistant_message") or "")
        heard = asked(
            FINDS.format(intent=intent, said="\n\n".join(said) or "(none)", message=message),
            alone,
        )
        turns.append({"message": message, **heard})
        print(f"  AI: {message[:300]!r}")
        print(f"  person: {str(heard.get('answer'))[:200]!r} {heard_of(heard)}", flush=True)
        if heard.get("finished"):
            return turns
        if heard.get("asks"):
            said += [f"AI: {message}", f"You: {heard['answer']}"]
            session.type(str(heard["answer"]))
    raise SystemExit(f"the conversation did not end in {TURNS} messages")


def heard_of(heard: dict[str, Any]) -> str:
    """What the person said of a message, in a few words."""
    keys = ("asks", "points", "asks_fact", "asks_settled", "not_yours", "finished")
    return " ".join(f"{k}={heard.get(k)}" for k in keys)


def asked_wrong(turns: list[dict[str, Any]]) -> list[str]:
    """What the person finds wrong in the messages put to them: more than one point, a fact asked,
    a settled point asked again, or a point not theirs."""
    wrong = []
    for n, t in enumerate(turns, 1):
        if int(t.get("points") or 0) > 1:
            wrong.append(f"message {n} put {t['points']} points to the person")
        for key, what in (
            ("asks_fact", "asked the person a fact of the repository"),
            ("asks_settled", "asked again what was settled"),
            ("not_yours", "asked the person a point not theirs"),
        ):
            if t.get(key):
                wrong.append(f"message {n} {what}")
    return wrong


def work_wrong(repo: str, paths: list[str], place: str, intent: str) -> list[str]:
    """Each change the person would make to the work before using it, as the stand-in judges the
    work's files."""
    shown = []
    for path in paths:
        try:
            with open(os.path.join(repo, path), encoding="utf-8") as f:
                shown.append(f"<file path={path!r}>\n{f.read()}</file>")
        except OSError:
            shown.append(f"<file path={path!r}>(not there)</file>")
    judged = asked(
        JUDGES.format(intent=intent, work="\n\n".join(shown)), os.path.join(place, "person")
    )
    return [f"the person would change: {c}" for c in judged.get("changes", [])]


def run_folder(repo: str) -> str:
    """The one run's folder Turn made under `.turn/` in the repository, or ""."""
    found = (
        sorted(
            os.path.join(repo, ".turn", n)
            for n in os.listdir(os.path.join(repo, ".turn"))
            if n != "best-practices" and os.path.isdir(os.path.join(repo, ".turn", n))
        )
        if os.path.isdir(os.path.join(repo, ".turn"))
        else []
    )
    return found[-1] if found else ""


def read_json(path: str) -> Any:
    """The JSON at the path, or None where it is not there."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


# Each role's start that may follow the start of another, as Turn's routes give them.
FOLLOWS = {
    "planner": {"designer"},
    "designer": {"builder"},
    "builder": {"evaluator", "designer"},
    "evaluator": {"designer", "refactorer"},
    "refactorer": {"proofreader"},
    "proofreader": {"refactorer", "designer"},
}


def starts(session: str) -> list[tuple[str, str, float, float]]:
    """Each run of a role of Turn the session started, by its agent type, its record, and the
    times of its first and last entries, in the order they started."""
    found = []
    for file in trying.agents(session):
        kind = trying.record.agent_type(file)
        if not kind.startswith("turn:") or kind == "turn:up":
            continue
        times = [
            datetime.datetime.fromisoformat(str(e["timestamp"]).replace("Z", "+00:00")).timestamp()
            for e in trying.record.read(file) or []
            if e.get("timestamp")
        ]
        if times:
            found.append((kind.split(":", 1)[1], file, min(times), max(times)))
    return sorted(found, key=lambda s: s[2])


def routes_wrong(runs: list[tuple[str, str, float, float]]) -> list[str]:
    """Each start of a role that no route leads to from the role started before it, a step's runs
    started at once counted as one; and a run that did not start with planner."""
    roles = [r for r, *_ in runs]
    steps = [r for n, r in enumerate(roles) if n == 0 or roles[n - 1] != r]
    wrong = [] if steps[:1] == ["planner"] else ["the run did not start with planner"]
    for before, after in zip(steps, steps[1:]):
        if after not in FOLLOWS.get(before, set()):
            wrong.append(f"{after} was started after {before}, which no route leads to")
    if steps[-1:] != ["proofreader"]:
        wrong.append(f"the run ended at {steps[-1:] or 'no role'}, not at proofreader")
    return wrong


def overlapped(runs: list[tuple[str, str, float, float]], role: str) -> bool:
    """Whether two runs of the role went at the same time."""
    spans = sorted((a, b) for r, _, a, b in runs if r == role)
    return any(spans[n + 1][0] < spans[n][1] for n in range(len(spans) - 1))


def verdict(untried: list[str], wrong: list[str]) -> bool:
    """Whether the run counted and passed, printing which, and why where it did not."""
    if untried:
        print("  not counted: " + "; ".join(untried))
        return False
    print("  passed" if not wrong else "  failed: " + "; ".join(wrong))
    return not wrong


def main(run: Any) -> None:
    """Runs the E2E test's run as many times as the command line gives, three by default, numbered
    from the second word where given, and exits 0 where every run passed and counted."""
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    first = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    passed = [run(n) for n in range(first, first + runs)]
    print(f"{sum(passed)} of {runs} runs passed")
    sys.exit(0 if all(passed) else 1)

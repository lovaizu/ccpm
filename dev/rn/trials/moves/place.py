"""A case's folder in rn's move trials: a fresh repository with a bare repository as its origin, the
copies of rn and turn as installing makes them, turn's turn:up replaced by the stand-in, and the
stand-in for `gh` first on the PATH; with rn's commands and the stand-in turn run in it to make the
case's state, and what the repository, its origin and the stand-in gh hold after a move."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Callable, NamedTuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
# rn's own names of the session's record, read from its scripts, which the trial runs.
sys.path.insert(0, os.path.join(ROOT, "rn", "scripts"))
import session
import steering

# The repository the session runs in, on its default branch before any session: a small project
# and the user's own checklist for a note, a kind of work of its own.
DEFAULT = "main"
SEED = {
    "README.md": "# demo\n\ndemo prints a greeting.\n\n## Use\n\nRun `sh demo.sh`.\n",
    "demo.sh": "#!/bin/sh\necho hello\n",
    ".rn/checklists/note.md": """---
name: note
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Note

A note is a file of this repository holding a few lines the user decided, such as a greeting, read
by a contributor who opens it to take those lines in and do what they say.

A note serves its reader by giving the decided lines where the reader looks first, with what to do
next.

## Benefit

### B-1: The lines found at once

Scope: whole

Can the contributor who opens the note find the decided lines on its first screen, without reading
past other text?

Why: a contributor who must search for the lines may miss them and go on without them.

### B-2: The thing to do, told

Scope: its part

Can the contributor tell from the decided lines what to do next, such as a command to run, and do it
with what the repository holds?

Look for: a command or a file the repository does not have.

Why: a line that says what to do with nothing to do it with leaves the contributor stuck at once.
""",
}
# The steering of a session, among the files of the repository's record.
STEERING = re.compile(
    rf"{re.escape(session.RECORD)}/{session.SESSION_NAME.pattern}/{re.escape(session.STEERING)}"
)
# What every move keeps, which the move trials check after each move and the flow trial after each
# message.
DEFAULT_KEPT = "nothing pushed to the default branch"
ALL_KEPT = "every change committed and the branch pushed"
RULES: dict[str, Callable[[Any], bool]] = {
    DEFAULT_KEPT: lambda seen: seen.default_kept,
    ALL_KEPT: lambda seen: seen.clean and seen.pushed,
}


class Stop(Exception):
    """A command of the case's state-making that failed, with what it printed."""


class Called(NamedTuple):
    """A call to turn as the last commit holds it: its number, the work it is on, whether turn
    returned it, and how many decisions its CCS holds."""

    number: str
    work: str
    returned: bool
    decisions: int


class Seen(NamedTuple):
    """What a move left: the reply, and each text the orchestrator said on the way; the commits
    made since the move began, whether the branch is pushed and every change committed, whether the
    default branch on the origin is as it was; the steering's path and text as the last commit
    holds them, each call to turn, and the text of each other file it holds by its path, the
    session's learnings and research among them, the calls' files left out; and what the stand-in
    gh keeps."""

    reply: str
    said: list
    commits: int
    pushed: bool
    clean: bool
    default_kept: bool
    steering_path: str
    steering_text: str
    calls: list[Called]
    texts: dict
    gh: dict


def steered(seen: Seen) -> steering.Steering | None:
    """The steering as the last commit holds it, where it holds its form."""
    if not seen.steering_text or steering.out_of_form(seen.steering_text):
        return None
    return steering.parsed(seen.steering_text)


def kept_learnings(seen: Seen) -> list:
    """Each learning of the session's learnings as the last commit holds them, none before any is
    made."""
    path = session.learnings_path(os.path.dirname(seen.steering_path))
    return [x for x in seen.texts.get(path, "").splitlines() if session.LEARNING.fullmatch(x)]


def costed(costs: dict[str, float]) -> float:
    """The cost of the conversations, each by the last cost it reported, as a conversation gone on
    with reports the cost of the whole of it so far."""
    return round(sum(costs.values()), 2)


def session_call(path: str) -> str | None:
    """The number of the call to turn whose CCS the path is, None where it is no CCS of a call."""
    named = session.CALL.fullmatch(os.path.basename(path))
    return named[1] if named and named[2] == session.CCS else None


class Place:
    """A case's folder and what runs in it."""

    def __init__(self, folder: str) -> None:
        self.folder = folder
        self.repo = os.path.join(folder, "repo")
        self.turn = os.path.join(folder, "turn")
        self.rn_copy = os.path.join(folder, "rn")
        self.plugins = [self.turn, self.rn_copy]
        path = f"{os.path.join(folder, 'bin')}{os.pathsep}{os.environ['PATH']}"
        self.env = {"PATH": path}
        self.default = ""

    def make(self, replies: dict) -> None:
        """Makes the folder, or fills it where it is made already and empty, as the flow trial's
        own folder is: the copies, the stand-in gh with no pull request, the origin and the
        repository at the seed, and the stand-in turn's replies, set by the case."""
        os.makedirs(self.folder, exist_ok=True)
        ignored = shutil.ignore_patterns("__pycache__")
        for name, copy in (("turn", self.turn), ("rn", self.rn_copy)):
            shutil.copytree(os.path.join(ROOT, name), copy, ignore=ignored)
        turn = self.turn
        shutil.copyfile(os.path.join(HERE, "up.md"), os.path.join(turn, "agents", "up.md"))
        shutil.copyfile(os.path.join(HERE, "stand.py"), os.path.join(turn, "scripts", "stand.py"))
        os.makedirs(os.path.join(turn, "stand"))
        with open(os.path.join(turn, "stand", "replies.json"), "w", encoding="utf-8") as f:
            json.dump(replies, f, ensure_ascii=False, indent=1)
        # The stand-in keeps none of the real turn:up's steps, so its lanes are left out: each
        # hook whose command ends with the subagent it holds, turn:up.
        hooks = os.path.join(turn, "hooks", "hooks.json")
        with open(hooks, encoding="utf-8") as f:
            laid = json.load(f)
        laid["hooks"] = {
            event: [
                e for e in lanes if not any(h["command"].endswith(" turn:up") for h in e["hooks"])
            ]
            for event, lanes in laid["hooks"].items()
        }
        with open(hooks, "w", encoding="utf-8") as f:
            json.dump(laid, f, indent=2)
        os.makedirs(os.path.join(self.folder, "bin"))
        stand = os.path.join(self.folder, "bin", "gh.py")
        shutil.copyfile(os.path.join(HERE, "gh.py"), stand)
        gh = os.path.join(self.folder, "bin", "gh")
        with open(gh, "w", encoding="utf-8") as f:
            f.write(f"#!/bin/sh\nexec python3 '{stand}' \"$@\"\n")
        os.chmod(gh, 0o755)
        with open(os.path.join(self.folder, "gh.json"), "w", encoding="utf-8") as f:
            json.dump({"prs": [], "issues": [], "calls": []}, f)
        origin = os.path.join(self.folder, "origin.git")
        self.run("git", "init", "-q", "--bare", "-b", DEFAULT, origin, cwd=self.folder)
        self.run("git", "init", "-q", "-b", DEFAULT, self.repo, cwd=self.folder)
        for path, text in SEED.items():
            self.write(path, text)
        # rn's commits are made by rn.py's git, which needs a name on a machine with none.
        self.git("config", "user.name", "trial")
        self.git("config", "user.email", "trial@example.invalid")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "demo prints a greeting")
        self.git("remote", "add", "origin", origin)
        self.git("push", "-q", "-u", "origin", DEFAULT)
        self.git("remote", "set-head", "origin", DEFAULT)
        self.default = self.git("rev-parse", DEFAULT)

    def run(self, *command: str, cwd: str | None = None) -> str:
        """What the command printed, run in the repository with the case's PATH; stops with what
        it printed where it fails."""
        done = subprocess.run(
            list(command),
            cwd=cwd or self.repo,
            env={**os.environ, **self.env},
            capture_output=True,
            text=True,
            check=False,
        )
        if done.returncode:
            said = (done.stdout + done.stderr).strip()
            raise Stop(f"{' '.join(command[:4])} ... failed: {said}")
        return done.stdout.strip()

    def git(self, *args: str) -> str:
        """What git printed for the arguments, in the repository."""
        return self.run("git", *args)

    def write(self, path: str, text: str) -> None:
        """Writes the text at the path, from the top of the repository."""
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def rn(self, *args: str) -> str:
        """What the copy of rn.py printed for the subcommand."""
        return self.run("python3", os.path.join(self.rn_copy, "scripts", "rn.py"), *args)

    def turned(self, called: str, made: dict) -> None:
        """Has the stand-in turn return the call, the first line rn.py ccs printed, with the made
        given."""
        stand = os.path.join(self.turn, "scripts", "stand.py")
        self.run("python3", stand, called, json.dumps(made))

    def head(self) -> str:
        """The commit the repository's branch is at."""
        return self.git("rev-parse", "HEAD")

    def seen(self, before: str, reply: str, record: str = "") -> Seen:
        """What the repository, its origin and the stand-in gh hold after the move begun at the
        commit before, with the reply and what Claude Code printed in the record, where given."""
        branch = self.git("branch", "--show-current")
        remote = self.git("ls-remote", "origin", f"refs/heads/{branch}").split("\t")[0]
        files = self.git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
        steering_path = next((p for p in files if STEERING.fullmatch(p)), "")
        text = self.git("show", f"HEAD:{steering_path}") + "\n" if steering_path else ""
        folder = os.path.dirname(steering_path) + "/" if steering_path else None
        calls, texts = [], {}
        for path in files:
            number = session_call(path)
            if folder and number and path.startswith(folder):
                ccs = json.loads(self.git("show", f"HEAD:{path}"))
                kept = [e for part in ccs.values() for e in part]
                work = next((e[session.WORK] for e in kept if session.WORK in e), "")
                result = session.call_path(os.path.dirname(steering_path), number, session.RESULT)
                decided = len([e for e in kept if session.DECISION in e])
                calls.append(Called(number, work, result in files, decided))
            elif path != steering_path and not (
                folder and path.startswith(f"{folder}{session.CALLS}/")
            ):
                texts[path] = self.git("show", f"HEAD:{path}")
        said = []
        if record:
            with open(record, encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    content = entry.get("message", {}).get("content")
                    # The main conversation's words alone, as a subagent's, such as the stand-in
                    # turn's, carry the tool call they answer.
                    main = entry.get("parent_tool_use_id") is None
                    if entry.get("type") == "assistant" and main and isinstance(content, list):
                        said += [c["text"] for c in content if c.get("type") == "text"]
        with open(os.path.join(self.folder, "gh.json"), encoding="utf-8") as f:
            gh: dict[str, Any] = json.load(f)
        return Seen(
            reply,
            said,
            int(self.git("rev-list", "--count", f"{before}..HEAD")),
            remote == self.head(),
            not self.git("status", "--porcelain"),
            self.git("ls-remote", "origin", f"refs/heads/{DEFAULT}").split("\t")[0] == self.default,
            steering_path,
            text,
            calls,
            texts,
            gh,
        )

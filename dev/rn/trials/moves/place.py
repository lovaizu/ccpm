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
from typing import Any, NamedTuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
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
STEERING = re.compile(r"\.rn/[0-9]{8}-[a-z0-9-]+/steering\.md")
CALL = re.compile(r"([0-9]{4})-ccs\.json")


class Stop(Exception):
    """A command of the case's state-making that failed, with what it printed."""


class Seen(NamedTuple):
    """What a move left: the reply, and each text the orchestrator said on the way; the commits
    made since the move began, whether the branch is pushed and every change committed, whether the
    default branch on the origin is as it was; the steering's path and text as the last commit
    holds them, each call to turn as `(number, work, returned, decisions)`, and the text of each
    other file it holds by its path, the session's learnings and research among them, the calls'
    files left out; and what the stand-in gh keeps."""

    reply: str
    said: list
    commits: int
    pushed: bool
    clean: bool
    default_kept: bool
    steering: str
    text: str
    calls: list
    texts: dict
    gh: dict


class Place:
    """A case's folder and what runs in it."""

    def __init__(self, folder: str) -> None:
        self.folder = folder
        self.repo = os.path.join(folder, "repo")
        self.plugins = [os.path.join(folder, "turn"), os.path.join(folder, "rn")]
        path = f"{os.path.join(folder, 'bin')}{os.pathsep}{os.environ['PATH']}"
        self.env = {"PATH": path}
        self.default = ""

    def make(self, replies: dict) -> None:
        """Makes the folder, or fills it where it is made already and empty, as the flow trial's
        own folder is: the copies, the stand-in gh with no pull request, the origin and the
        repository at the seed, and the stand-in turn's replies, set by the case."""
        os.makedirs(self.folder, exist_ok=True)
        ignored = shutil.ignore_patterns("__pycache__")
        for name, copy in zip(("turn", "rn"), self.plugins):
            shutil.copytree(os.path.join(ROOT, name), copy, ignore=ignored)
        turn = self.plugins[0]
        shutil.copyfile(os.path.join(HERE, "up.md"), os.path.join(turn, "agents", "up.md"))
        shutil.copyfile(os.path.join(HERE, "stand.py"), os.path.join(turn, "scripts", "stand.py"))
        os.makedirs(os.path.join(turn, "stand"))
        with open(os.path.join(turn, "stand", "replies.json"), "w", encoding="utf-8") as f:
            json.dump(replies, f, ensure_ascii=False, indent=1)
        # The stand-in keeps none of the real turn:up's steps, so its lanes are left out.
        hooks = os.path.join(turn, "hooks", "hooks.json")
        with open(hooks, encoding="utf-8") as f:
            laid = json.load(f)
        laid["hooks"] = {
            event: [e for e in lanes if not any(" turn:up " in h["command"] for h in e["hooks"])]
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
        return self.run("python3", os.path.join(self.plugins[1], "scripts", "rn.py"), *args)

    def turned(self, called: str, made: dict) -> None:
        """Has the stand-in turn return the call rn.py ccs printed with the made given."""
        stand = os.path.join(self.plugins[0], "scripts", "stand.py")
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
        steering = next((p for p in files if STEERING.fullmatch(p)), "")
        text = self.git("show", f"HEAD:{steering}") + "\n" if steering else ""
        session = os.path.dirname(steering) + "/" if steering else None
        calls, texts = [], {}
        for path in files:
            number = CALL.fullmatch(os.path.basename(path))
            if session and number and path.startswith(session):
                ccs = json.loads(self.git("show", f"HEAD:{path}"))
                kept = [e for part in ccs.values() for e in part]
                work = next((e["work"] for e in kept if "work" in e), "")
                result = path.replace("-ccs.json", "-result.json")
                decided = len([e for e in kept if "decision" in e])
                calls.append((number[1], work, result in files, decided))
            elif path != steering and not (session and path.startswith(f"{session}turn/")):
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
            steering,
            text,
            calls,
            texts,
            gh,
        )

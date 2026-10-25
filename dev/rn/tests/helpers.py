"""What rn's tests stand on beside what every plugin's tests do: the repository a session is kept in,
with the remote it is pushed to, made once a run and copied into each test's folder; a plugin
folder of its own and a stand-in for GitHub's command `gh`; the session's steering, its calls to
turn and Claude Code's records, as rn writes or reads them."""

from __future__ import annotations

import contextlib
import datetime
import io
import json
import os
import subprocess
import sys
from typing import Any
from unittest import mock

SCRIPTS = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "rn", "scripts")
)
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lane"))

import ccs  # noqa: F401  (each of rn's modules, for its own tests)
import proposal  # noqa: F401
import record
import session  # noqa: F401
import steering  # noqa: F401
import stop  # noqa: F401
import template  # noqa: F401
import testing

import rn

# The folder of the copy holding the user's repository, beside `origin.git`, its remote.
REPO = "repo"
# When each commit a test makes is made, unless the test says another time: before every entry of
# Claude Code's records the tests write.
DATE = "2000-01-01T00:00:00Z"
# A time before the commits a test makes, and one after them, for what Claude Code's records hold.
EARLIER = "1999-12-31T23:59:59Z"
LATER = "2000-01-01T00:00:01Z"


class MainAndWork(testing.GitTest):
    """A test in a git repository whose remote's default branch is `main`, with `work` checked
    out, both pushed to the remote, a bare repository beside it; each commit it makes is dated, so
    no test reads the clock through them."""

    def setUp(self) -> None:
        super().setUp()
        dated = mock.patch.dict(os.environ, {"GIT_AUTHOR_DATE": DATE, "GIT_COMMITTER_DATE": DATE})
        dated.start()
        self.addCleanup(dated.stop)

    def main_and_work(self) -> None:
        """Makes where the test stands `origin.git`, a bare repository standing for the remote, and
        the repository `repo`: `main` with a README and `work` checked out from it, each pushed and
        tracking the remote's. The remote is named by a path from the repository, so a copy pushes
        to its own."""
        self.git("init", "-q", "--bare", "origin.git")
        os.makedirs(REPO)
        os.chdir(REPO)
        self.git("init", "-q")
        self.git("checkout", "-q", "-b", "main")
        self.write("README.md", "# app\n")
        self.commit()
        self.git("remote", "add", "origin", "../origin.git")
        self.git("push", "-q", "-u", "origin", "main")
        self.git("remote", "set-head", "origin", "main")
        self.git("checkout", "-q", "-b", "work")
        self.git("push", "-q", "-u", "origin", "work")


# The day each test takes as today, so that no test reads the clock.
TODAY = datetime.date(2026, 10, 20)
# The folder in the repository holding the sessions and the user's checklists.
RECORD = ".rn"
# The slug of the session each test starts on TODAY, its folder, its steering and its calls to turn.
SLUG = "add-login"
FOLDER = f"{RECORD}/{TODAY:%Y%m%d}-{SLUG}"
STEERING = f"{FOLDER}/steering.md"
# The branch the tests' sessions run on.
BRANCH = "work"
TURN = f"{FOLDER}/turn"
# The kind of the checklist the plugin folder holds.
KIND = "code"
# The version the plugin folder's manifest gives.
VERSION = "0.10.0"
# The repository on GitHub and the pull request the stand-in for gh gives.
REPOSITORY = "https://github.com/o/r"
PR = f"{REPOSITORY}/pull/7"
# The options ccs needs for a task's work made the first time, each with a value it takes.
NEEDED = {"--receiver": "a new user", "--use": "to try it", "--has": "."}
# The real plan checklist of rn, whose F-1 every steering holds to.
PLAN_CHECKLIST = os.path.join(SCRIPTS, "..", "checklists", "session", "plan.md")
# What rn says to do at a sign-off, as the last line of every proposal.
HOW = "/rn:ty to approve, /rn:gm <feedback> to ask for a change."
# The parts of a steering, as rn's plan checklist's F-1 gives them.
NEXT = "2. Ask the user the first point."
GOAL = "G1: Users sign in,\nso their carts stay theirs."
CRITERIA = (
    "- AC1: A user signs in with their email.\n"
    "- AC2: A signed-in user sees only their cart,\n  on every page."
)
# A stand-in for GitHub's command: keeps each call's arguments, one to a line after a line `--`,
# and prints what rn reads, the repository's URL or the pull request's, or fails as GH_FAIL says.
GH = f"""#!/bin/sh
{{ echo --; printf '%s\\n' "$@"; }} >> "$(dirname "$0")/asked"
if [ -n "$GH_FAIL" ]; then echo "$GH_FAIL" >&2; exit 1; fi
case "$1 $2" in
  "repo view") echo "{REPOSITORY}" ;;
  "pr create") echo "{PR}" ;;
esac
"""


def task(
    name: str = "T1", serves: str = "AC1", ticks: str = "    ", test: str | None = None
) -> str:
    """A task in the form of F-1 serving the IDs given, with the command that checks its result
    where one is given, and an action of turn's for each character of the ticks, ticked where it is
    `x`, each making a work of the kind KIND at a path of its own, which `work_path` gives."""
    actions = "\n".join(
        f"  - [{t}] {n}. Make part {n} of {name}, `{work_path(name, n)}` as a {KIND} work. turn."
        for n, t in enumerate(ticks, 1)
    )
    command = "" if test is None else f"  Test: `{test}`\n\n"
    return (
        f"- {name}: Make the part {name}. Serves {serves}.\n\n"
        f"  Completion criterion: it does what it serves, tried by hand.\n\n{command}{actions}"
    )


def work_path(task_id: str, number: int) -> str:
    """The path the fixture's action of the number of the task makes its work at."""
    return f"src/{task_id.lower()}-{number}.py"


def plan(goal: str = GOAL, criteria: str = CRITERIA, tasks: str = task()) -> str:
    """The part of a steering from the title through the tasks, with the goal, the criteria and the
    tasks given, each left out where it is empty."""
    parts = ["# Add login", goal]
    parts += [f"## Acceptance criteria\n\n{criteria}"] if criteria else []
    parts += [f"## Tasks\n\n{tasks}"] if tasks else []
    return "\n\n".join(p for p in parts if p)


def steered(
    part: str = plan(),
    stage: str = "plan",
    signoff: str = "none",
    pr: str = PR,
    next_step: str = NEXT,
    opened: str = "None.",
) -> str:
    """A steering in the form of F-1, as rn writes it, with the parts given."""
    front = (
        f"---\nrn: {VERSION}\npr: {pr}\nstage: {stage}\nsignoff: {signoff}\n"
        "artifact-language: English\nconversation-language: Japanese\n---\n\n"
    )
    return f"{front}{part}\n\n## Next\n\n{next_step}\n\n## Open\n\n{opened}\n"


STEERED = steered()
LEARNINGS = f"{FOLDER}/learnings.md"


def call_at(number: str, what: str = "ccs.json") -> str:
    """The path of a file of the session's call of the number: its CCS, its result or its part."""
    return f"{TURN}/{number}-{what}"


def options(needed: dict[str, str]) -> list[str]:
    """The arguments giving each option and its value."""
    return [part for option in needed.items() for part in option]


class RepoTest(MainAndWork):
    """A git repository whose default branch is `main` and whose checked-out branch is `work`, both
    pushed to the remote beside it, with git reading no setting of the machine it runs on; a plugin
    folder with its manifest and stand-ins for rn's checklists of code and of plans, rn's own plan
    checklist being read through PLAN_CHECKLIST; the stand-in for gh first on PATH; and Claude
    Code's records in a folder of their own, as CLAUDE_CONFIG_DIR names it."""

    def setUp(self) -> None:
        super().setUp()
        os.chdir(os.path.join(self.copied("repo", self.main_and_work), REPO))
        self.plugin = os.path.join(self.base, "plugin")
        self.write_json(
            os.path.join(self.plugin, ".claude-plugin", "plugin.json"), {"version": VERSION}
        )
        self.checklist = os.path.join(self.plugin, "checklists", "product", f"{KIND}.md")
        self.write(self.checklist, "# Code\n")
        # A stand-in for each checklist of the works rn makes itself.
        self.own = {
            kind: os.path.join(self.plugin, "checklists", folder, f"{kind}.md")
            for kind, folder in (
                ("plan", "session"),
                ("learnings", "session"),
                ("deliverable", "session"),
                ("issue", "session"),
                ("checklist", ""),
            )
        }
        for kind, path in self.own.items():
            self.write(path, f"# {kind.capitalize()}\n")
        self.fix = os.path.join(self.plugin, "checklists", "fix.md")
        self.usability = os.path.join(self.plugin, "checklists", "usability.md")
        self.bin = os.path.join(self.base, "bin")
        self.write(os.path.join(self.bin, "gh"), GH)
        os.chmod(os.path.join(self.bin, "gh"), 0o755)
        self.config = os.path.join(self.base, "config")
        path = mock.patch.dict(
            os.environ,
            {"PATH": self.bin + os.pathsep + os.environ["PATH"], "CLAUDE_CONFIG_DIR": self.config},
        )
        path.start()
        self.addCleanup(path.stop)
        self.top = os.getcwd()
        self.project = record.folders(self.top)[0]

    def conversation(self, name: str, *entries: dict[str, Any]) -> str:
        """Writes the record of a conversation in the project's folder; gives its path."""
        path = os.path.join(self.project, f"{name}.jsonl")
        self.write(path, "".join(json.dumps(e) + "\n" for e in entries))
        return path

    def rn(self, *argv: str) -> tuple[int, str]:
        """The exit code and what rn printed for the arguments, each a text of its own, as the
        command line gives them, not the one copy CPython keeps of a literal like a name, such as
        `build`, which rn's own literals share."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = rn.main([a.encode().decode() for a in argv], self.plugin, TODAY)
        return code, out.getvalue()

    def printed(self, *argv: str) -> str:
        """What rn printed, having run to its end."""
        code, out = self.rn(*argv)
        self.assertEqual(code, 0, out)
        return out

    def ran(self, *argv: str) -> Any:
        """What rn printed as JSON, having run to its end: its first line, the call to turn where
        rn also prints the line to tell the user after it."""
        return json.loads(self.printed(*argv).splitlines()[0])

    def stopped(self, *argv: str) -> str:
        """What rn printed, having stopped."""
        code, out = self.rn(*argv)
        self.assertEqual(code, 1, out)
        return out

    def out(self, *args: str) -> str:
        """What git prints for the arguments."""
        done = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
        return done.stdout

    def head(self, ref: str = "HEAD") -> str:
        """The commit the ref names."""
        return self.out("rev-parse", ref).strip()

    def session(self, text: str | None = STEERED, folder: str = FOLDER) -> None:
        """A session's folder committed on the branch and pushed, with its steering, none where it
        is None."""
        if text is not None:
            self.write(f"{folder}/steering.md", text)
        else:
            self.write(f"{folder}/turn/.keep", "")
        self.kept()

    def kept(self) -> None:
        """Commits every change and pushes it, as the orchestrator's last move did; a commit of no
        change as well."""
        self.commit_with("c")

    def commit_with(self, message: str) -> None:
        """Commits every change with the message and pushes it, as a move kept."""
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        self.git("push", "-q")

    def call(
        self,
        number: str,
        work: str,
        stage: str = "plan",
        decisions: tuple[str, ...] = (),
        works: tuple[str, ...] = (),
        result: Any = None,
        part: str | None = None,
    ) -> None:
        """Writes a call to turn on the work, made in the stage, with the decisions and the works
        its CCS names, turn's result where one is given, and its part where one is given, the
        learnings' in a file of their name, the plan's in one of the steering's; commits
        nothing."""
        written = {
            "focal_entities": [{"work": work}, {"stage": stage}] + [{"path": p} for p in works],
            "constraints": [{"decision": d} for d in decisions],
        }
        self.write_json(call_at(number), written)
        if result is not None:
            self.write_json(call_at(number, "result.json"), result)
        if part is not None:
            name = "learnings.md" if work == "learnings" else "steering.md"
            self.write(call_at(number, name), part)

    def asked(self) -> list[list[str]]:
        """The arguments of each call to the stand-in for gh, in order."""
        path = os.path.join(self.bin, "asked")
        said = self.read(path) if os.path.exists(path) else ""
        return [call.splitlines() for call in said.split("--\n")[1:]]


# Where rn shows the records the learnings are made from, in the repository's git folder.
SHOWN = ".git/rn"
HISTORY = f"{SHOWN}/record/history.txt"
CONVERSATIONS = f"{SHOWN}/conversations"
# When the learnings' call of the stretch before was returned, between the entries of the
# conversations the tests write.
KEPT_AT = "2026-10-20T09:30:00Z"


def said(text: str, at: str, cwd: str, branch: str = BRANCH) -> dict[str, Any]:
    """An entry of a record, as Claude Code keeps it: the user's words at the time, where the
    conversation ran and on what branch."""
    return {
        "type": "user",
        "timestamp": at,
        "cwd": cwd,
        "gitBranch": branch,
        "message": {"role": "user", "content": text},
    }


class LearningTest(RepoTest):
    """A session kept, and the records rn shows of it: the texts it shows, the conversations among
    them, an agent's record beside a conversation, and calls on the learnings kept at a time."""

    def setUp(self) -> None:
        super().setUp()
        self.session()

    def agent(self, conversation: str, name: str, at: str, meta: dict[str, Any]) -> str:
        """Writes the record of an agent the conversation started, saying its name at the time,
        with its meta file; gives its path."""
        path = os.path.join(conversation[: -len(".jsonl")], "subagents", f"agent-{name}.jsonl")
        self.write(path, json.dumps(said(name, at, self.top)) + "\n")
        self.write_json(path[: -len(".jsonl")] + ".meta.json", meta)
        return path

    def show(self) -> list[str]:
        """The paths of the texts rn showed for the learnings' call, as the CCS it wrote names them
        as what its receiver has."""
        written = self.read_json(self.ran("ccs", "learnings")["ccs"])
        return [e["has"] for e in written["focal_entities"] if "has" in e]

    def records(self) -> list[str]:
        """The paths of the texts rn showed, relative to where it shows them."""
        return [os.path.relpath(p, os.path.join(self.top, SHOWN)) for p in self.show()]

    def shown(self) -> list[str]:
        """The text of each conversation rn showed, in order."""
        return [self.read(p) for p in self.show() if f"{os.sep}conversations{os.sep}" in p]

    def left_at(self) -> str:
        """The commit the branch left the default branch at."""
        return self.out("merge-base", "origin/main", "HEAD").strip()

    def learnt(self, number: str, at: str = KEPT_AT) -> str:
        """A call on the learnings returned and kept at the time; gives the commit."""
        self.call(number, "learnings", "learnings", result={})
        self.git("add", "-A")
        with mock.patch.dict(os.environ, {"GIT_COMMITTER_DATE": at}):
            self.git("commit", "-q", "-m", f"learnings {number}")
        self.git("push", "-q")
        return self.head()

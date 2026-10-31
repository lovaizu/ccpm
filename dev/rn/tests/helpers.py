"""What rn's tests stand on beside what every plugin's tests do: the repository a session is kept
in, with the remote it is pushed to, made once a run and copied into each test's folder; a plugin
folder of its own and a stand-in for GitHub's command `gh`; the session's steering, its calls and
Claude Code's records, as rn writes or reads them."""

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
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "plugins", "rn", "scripts"
    )
)
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lane"))

import ccs
import conversations  # noqa: F401
import items  # noqa: F401
import learnings  # noqa: F401
import proposal  # noqa: F401
import record
import rn
import schema  # noqa: F401
import session  # noqa: F401
import steering
import stop  # noqa: F401
import template  # noqa: F401
import testing

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
# The slug of the session each test starts on TODAY, its folder, its steering, the steering's
# Markdown and the folder of its calls.
SLUG = "add-login"
FOLDER = f"{RECORD}/{TODAY:%Y%m%d}-{SLUG}"
STEERING = f"{FOLDER}/steering.json"
MARKDOWN = f"{FOLDER}/steering.md"
CALLS = f"{FOLDER}/calls"
# The branch the tests' sessions run on.
BRANCH = "work"
# The kind of the checklist the plugin folder holds.
KIND = "code"
# The version the plugin folder's manifest gives.
VERSION = "0.10.0"
# The repository on GitHub and the pull request the stand-in for gh gives.
REPOSITORY = "https://github.com/o/r"
PR = f"{REPOSITORY}/pull/7"
# rn's real plan checklist, whose Format the Markdown of every steering's plan holds to.
PLAN_CHECKLIST = os.path.join(SCRIPTS, "..", "checklists", "session", "plan.md")
# What rn says to do at a sign-off, as the last line of every proposal.
HOW = "/rn:ty to approve, /rn:gm <feedback> to ask for a change."
# The parts of a steering in its form: the title, Next, the goal and the criteria.
TITLE = "Add login"
NEXT = "2. Ask the user the first point."
GOALS = ({"id": "G1", "what": "Users sign in", "why": "So their carts stay theirs."},)
CRITERIA = (
    {"id": "AC1", "what": "A user signs in with their email.", "contributes_to": ["G1"]},
    {
        "id": "AC2",
        "what": "A signed-in user sees only their cart, on every page.",
        "contributes_to": ["G1"],
    },
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
    name: str = "T1", serves: tuple[str, ...] = ("AC1",), builds_on: tuple[str, ...] = ()
) -> dict[str, Any]:
    """A task of the ID, building on the tasks given, with one completion criterion serving the
    criteria given."""
    return {
        "id": name,
        "what": f"The part {name}.",
        "builds_on": list(builds_on),
        "completion_criteria": [
            {"what": "It does what it serves.", "contributes_to": list(serves)}
        ],
    }


def plan(goals: Any = GOALS, criteria: Any = CRITERIA, tasks: Any = None) -> dict[str, Any]:
    """A plan with the goals, the criteria and the tasks given, one task where none is given."""
    return {
        "goals": [dict(g) for g in goals],
        "acceptance_criteria": [dict(c) for c in criteria],
        "tasks": [task()] if tasks is None else list(tasks),
    }


def steered(
    part: Any = None,
    stage: str = "goal",
    waiting: bool = False,
    pr: str | None = PR,
    next_step: str = NEXT,
    opened: tuple[str, ...] = (),
) -> dict[str, Any]:
    """A steering in its form, with the parts given, plan() where no plan is given."""
    return {
        "session": {
            "rn": VERSION,
            "pr": pr,
            "title": TITLE,
            "languages": {"artifact": "English", "conversation": "Japanese"},
        },
        "plan": plan() if part is None else part,
        "status": {
            "stage": stage,
            "awaiting_signoff": waiting,
            "next_step": next_step,
            "open_questions": list(opened),
        },
    }


def json_text(data: Any) -> str:
    """The data as rn writes its JSON files, one key or value to a line, text beyond ASCII as it
    is."""
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


STEERED = steered()
LEARNINGS = f"{FOLDER}/learnings.md"


def call_at(number: str, what: str = "ccs.json") -> str:
    """The path of a file of the session's call of the number: its CCS, its result or its part."""
    return f"{CALLS}/{number}-{what}"


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
            )
        }
        self.own["checklist"] = os.path.join(self.plugin, "checklists", "meta.md")
        for kind, path in self.own.items():
            self.write(path, f"# {kind.capitalize()}\n")
        self.fix = os.path.join(self.plugin, "checklists", "fix.md")
        # A stand-in for rn's checklist of every document, given beside each kind of document's.
        self.doc = os.path.join(self.plugin, "checklists", "doc.md")
        self.write(self.doc, "# Doc\n")
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
        # What rn tells turn of its own checklists' questions is told of none of the stand-ins, as
        # each test that needs it says; rn's own checklists hold what the real tables name.
        for table in ("BUILT", "EACH"):
            told = mock.patch.object(ccs, table, {})
            told.start()
            self.addCleanup(told.stop)
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

    def session(self, data: Any = STEERED, folder: str = FOLDER) -> None:
        """A session's folder committed on the branch and pushed, with its steering and the
        Markdown rn writes with it, none where it is None."""
        if data is not None:
            self.write(f"{folder}/steering.json", json_text(data))
            self.write(f"{folder}/steering.md", steering.markdown(data))
        else:
            self.write(f"{folder}/calls/.keep", "")
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
        stage: str = "goal",
        decisions: tuple[str, ...] = (),
        works: tuple[str, ...] = (),
        result: Any = None,
        part: Any = None,
        kind: str = KIND,
    ) -> None:
        """Writes a call to turn on the work of the kind, made in the stage, with the decisions and
        the works its CCS names, turn's result where one is given, and its part where one is given,
        the learnings' in a file of their name, the plan's as JSON in one of its; commits
        nothing."""
        written = {
            "focal_entities": [{"work": work}, {"stage": stage}, {"kind": kind}]
            + [{"path": p} for p in works],
            "constraints": [{"decision": d} for d in decisions],
        }
        self.write_json(call_at(number), written)
        if result is not None:
            self.write_json(call_at(number, "result.json"), result)
        if part is not None:
            if work == "learnings":
                self.write(call_at(number, "learnings.md"), part)
            else:
                self.write(call_at(number, "plan.json"), json_text(part))

    def asked(self) -> list[list[str]]:
        """The arguments of each call to the stand-in for gh, in order."""
        path = os.path.join(self.bin, "asked")
        said = self.read(path) if os.path.exists(path) else ""
        return [call.splitlines() for call in said.split("--\n")[1:]]


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

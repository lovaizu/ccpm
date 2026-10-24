"""The tests of rn's scripts: each subcommand gives what rn's architecture says, for the conductor that
runs it, and stops, saying what went wrong and what to do, on each input it must not take. Each test
runs in a git repository of its own, made in a temporary folder, standing for the user's repository
on a session's branch, with the remote it pushes to beside it, and a plugin folder of its own holding
rn's checklists."""

from __future__ import annotations

import contextlib
import datetime
import importlib.util
import io
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import unittest
from typing import Any
from unittest import mock

SCRIPTS = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "rn", "scripts")
)
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(SCRIPTS, "..", "..", "dev", "lane"))

import helpers
import testing

import rn

# The day each test takes as today, so that no test reads the clock.
TODAY = datetime.date(2026, 10, 20)
# The folder in the repository holding the sessions and the user's checklists.
RECORD = ".rn"
# The slug of the session each test starts on TODAY, and its folder.
SLUG = "add-login"
FOLDER = f"{RECORD}/{TODAY:%Y%m%d}-{SLUG}"
# The kind of the checklist the plugin folder holds.
KIND = "code"
# The work the ccs tests have written, at its path, with its CCS, turn's result and its decisions.
WORK = "readme"
WORK_PATH = "README.md"
CCS = f"{FOLDER}/ccs/{WORK}.json"
CCS_RESULT = f"{FOLDER}/ccs/{WORK}-result.json"
DECISIONS = f"{FOLDER}/decisions/{WORK}.decisions.md"
# The plan's result, which the plan sign-off waits on.
PLAN_RESULT = f"{FOLDER}/ccs/plan-result.json"
# The options ccs needs, each with a value it takes.
NEEDED = {"--kind": KIND, "--receiver": "a new user", "--use": "to try it", "--has": "."}
# A state, as the conductor writes it, and another for the next move.
STATE = {"focal_entities": [{"signoff": "plan"}]}
NEXT = {"focal_entities": [{"signoff": "design"}], "episodic_trace": [{"fact": "plan approved"}]}
# The pull request the plan gives, and the languages it says.
PR = "https://github.com/o/r/pull/1"
LANGUAGES = {"artifact-language": "English", "conversation-language": "Japanese"}
# The real plan checklist of rn, whose template every plan is held to.
PLAN_CHECKLIST = os.path.join(SCRIPTS, "..", "checklists", "session", "plan.md")


def plan_text(
    goal: str = "G1: Users sign in,\nso their carts stay theirs.",
    criteria: str = "- AC1: A user signs in with their email.\n"
    "- AC2: A signed-in user sees only their cart,\n  on every page.",
    tasks: str = "",
    opening: str = "",
) -> str:
    """A plan in the form of rn's plan checklist, with the goal, criteria and tasks given, and the
    front matter after the opening given."""
    said = "".join(f"{key}: {value}\n" for key, value in LANGUAGES.items())
    return (
        f"{opening}---\nrn: 0.10.0\npr: {PR}\nstatus: running\n{said}---\n\n# Add login\n\n"
        f"{goal}\n\n## Acceptance criteria\n\n{criteria}\n\n## Documents\n\n- UX: docs/ux.md\n\n"
        f"## Tasks\n\n{tasks}"
    )


PLAN = plan_text()
# The first proposal at the plan sign-off on PLAN.
FIRST = (
    "Plan sign-off\n"
    f"The plan is on the draft pull request: {PR}\n"
    "G1: Users sign in, so their carts stay theirs.\n"
    "AC1: A user signs in with their email.\n"
    "AC2: A signed-in user sees only their cart, on every page.\n"
    "/rn:ty to approve, /rn:gm <feedback> to ask for a change."
)


def state_at(folder: str = FOLDER) -> str:
    """The path of the state of the session in the folder."""
    return f"{folder}/state.json"


def plan_at(folder: str = FOLDER) -> str:
    """The path of the plan of the session in the folder."""
    return f"{folder}/steering.md"


def ccs_argv(needed: dict[str, str]) -> list[str]:
    """The arguments that have the work's CCS written, with each option given and its value."""
    return ["ccs", WORK, WORK_PATH] + [part for option in needed.items() for part in option]


class RepoTest(helpers.MainAndWork):
    """A git repository whose default branch is `main` and whose checked-out branch is `work`, both
    pushed to the remote beside it, with git reading no setting of the machine it runs on; and a
    plugin folder with rn's checklists."""

    def setUp(self) -> None:
        super().setUp()
        os.chdir(os.path.join(self.copied("repo", self.main_and_work), helpers.REPO))
        self.plugin = os.path.join(self.base, "plugin")
        self.checklist = os.path.join(self.plugin, "checklists", "product", f"{KIND}.md")
        self.write(self.checklist, "# Code\n")
        self.plan_checklist = os.path.join(self.plugin, "checklists", "session", "plan.md")
        self.write(self.plan_checklist, self.read(PLAN_CHECKLIST))
        self.fix = os.path.join(self.plugin, "checklists", "fix.md")

    def rn(self, *argv: str) -> tuple[int, str]:
        """The exit code and what rn printed for the arguments."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = rn.main(list(argv), self.plugin, TODAY)
        return code, out.getvalue()

    def printed(self, *argv: str) -> str:
        """What rn printed, having run to its end."""
        code, out = self.rn(*argv)
        self.assertEqual(code, 0, out)
        return out

    def ran(self, *argv: str) -> Any:
        """What rn printed as JSON, having run to its end."""
        return json.loads(self.printed(*argv))

    def stopped(self, *argv: str) -> str:
        """What rn printed, having stopped."""
        code, out = self.rn(*argv)
        self.assertEqual(code, 1, out)
        return out

    def out(self, *args: str) -> str:
        """What git prints for the arguments."""
        done = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
        return done.stdout

    def session(
        self, folder: str = FOLDER, plan: str | None = PLAN, state: Any = None, push: bool = False
    ) -> None:
        """A session's folder committed on the branch, with its plan, none where it is None, and
        its state, STATE where none is given; pushed where asked."""
        if plan is not None:
            self.write(plan_at(folder), plan)
        self.write_json(state_at(folder), state or STATE)
        self.commit()
        if push:
            self.git("push", "-q")

    def kept(self) -> None:
        """Commits every change and pushes it, as the conductor's last move did."""
        self.commit()
        self.git("push", "-q")


class SessionTest(RepoTest):
    def test_no_session_where_the_branch_changed_none(self):
        # Given: a branch that changed nothing under .rn/.
        # When: the conductor asks for the session.
        # Then: rn says there is none.
        self.assertEqual(self.ran("session"), {"session": None, "state": None})

    def test_the_session_the_branch_changed_is_found_with_its_state(self):
        # Given: a session's folder committed on the branch, with its state.
        self.session()
        # When: the conductor asks for the session.
        # Then: rn gives its folder and its state.
        self.assertEqual(self.ran("session"), {"session": FOLDER, "state": STATE})

    def test_the_state_is_printed_with_text_beyond_ascii_as_it_is(self):
        # Given: a session whose state holds a fact in Japanese.
        self.session(state={"episodic_trace": [{"fact": "計画を承認"}]})
        # When: the conductor asks for the session.
        # Then: rn prints it as it is, for the conductor to read.
        self.assertIn('"fact": "計画を承認"', self.printed("session"))

    def test_a_finished_session_is_not_taken_up(self):
        # Given: a session on the branch whose plan is finished.
        self.session(plan="---\nstatus: finished\n---\n")
        # When: the conductor asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_a_session_on_the_default_branch_is_not_taken_up(self):
        # Given: a session merged into the default branch, which the branch did not change.
        self.git("checkout", "-q", "main")
        self.session(folder=f"{RECORD}/20261001-old")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("checkout", "-q", "-B", "work")
        # When: the conductor asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_a_session_the_branch_removed_is_not_taken_up(self):
        # Given: a session folder on the default branch, which the branch removed.
        old = f"{RECORD}/20261001-old"
        self.git("checkout", "-q", "main")
        self.session(folder=old)
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("checkout", "-q", "-B", "work")
        self.git("rm", "-q", "-r", old)
        self.commit()
        # When: the conductor asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_the_users_checklists_are_not_a_session(self):
        # Given: a branch that changed only the user's checklists under .rn/.
        self.write(f"{RECORD}/checklists/{KIND}.md", "# Code\n")
        self.commit()
        # When: the conductor asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_a_file_straight_under_rn_is_not_a_session(self):
        # Given: a branch that changed a file named as a session, straight under .rn/.
        self.write(f"{RECORD}/20261020-x", "")
        self.commit()
        # When: the conductor asks for the session.
        # Then: there is none.
        self.assertIsNone(self.ran("session")["session"])

    def test_a_session_without_state_reads_as_an_empty_state(self):
        # Given: a session rn 0.9.0 left, with a plan and no state.json.
        self.write(plan_at(), PLAN)
        self.commit()
        # When: the conductor asks for the session.
        # Then: it is found, with an empty state.
        self.assertEqual(self.ran("session"), {"session": FOLDER, "state": {}})

    def test_a_session_without_a_plan_is_not_finished(self):
        # Given: a session just started, with no plan yet.
        self.session(plan=None)
        # When: the conductor asks for the session.
        # Then: it is found.
        self.assertEqual(self.ran("session")["session"], FOLDER)

    def test_a_plan_without_a_readable_front_matter_is_not_finished(self):
        plans = (
            "status: finished\n---\n",
            "--\nstatus: finished\n---\n",
            "x\n",
            "",
            "---\nstatus: finished\n",
            "---\nnotes\nstatus: finished\n---\n",
        )
        for plan in plans:
            with self.subTest(plan=plan):
                # Given: a session whose plan says it is finished in no front matter rn reads: one
                # it does not open with, never closes, or holds a line that is no `key: value`.
                self.session(plan=plan)
                # When: the conductor asks for the session.
                # Then: it is found, as nothing says it is over.
                self.assertEqual(self.ran("session")["session"], FOLDER)

    def test_an_empty_front_matter_reads_no_line_after_it(self):
        # Given: a session whose plan opens with an empty front matter, and has a `---` later.
        self.session(plan="---\n---\nstatus: finished\n---\n")
        # When: the conductor asks for the session.
        # Then: the status after the front matter is not read, and the session is found.
        self.assertEqual(self.ran("session")["session"], FOLDER)

    def test_two_sessions_not_finished_stop(self):
        # Given: a branch that changed two sessions, neither finished.
        other = f"{RECORD}/20261021-other"
        self.session()
        self.session(folder=other)
        # When: the conductor asks for the session.
        # Then: rn names both and says to finish one or check out the other's branch.
        self.assertIn(
            f"more than one session not finished: {FOLDER}, {other}; set `status:"
            " finished` in the plan of each that is over",
            self.stopped("session"),
        )

    def test_a_state_that_is_not_a_ccs_stops(self):
        self.session()
        for state in ("[]", "{", '{"focal_entities": [{"a": "b", "c": "d"}]}'):
            with self.subTest(state=state):
                # Given: a session whose state.json is written as no CCS: a list, no JSON, or an
                # entry of two kinds.
                self.write(state_at(), state)
                # When: the conductor asks for the session.
                # Then: rn says it is no CCS, what one is, and how to restore the state kept.
                self.assertRegex(
                    self.stopped("session"),
                    rf"^rn: {state_at()} is not a CCS; a CCS is a JSON object of parts, .*;"
                    rf" restore the state kept with `git checkout HEAD -- {state_at()}`, or write"
                    " it again as one",
                )

    def test_below_the_top_of_the_repository_stops(self):
        # Given: rn run from a folder below the top of the repository.
        os.makedirs("src")
        os.chdir("src")
        # When: the conductor asks for the session.
        # Then: rn says to run it from the top.
        self.assertIn(
            "runs in src/ below the top of the repository; run it from the top, after"
            ' `cd "$(git rev-parse --show-toplevel)"`',
            self.stopped("session"),
        )

    def test_outside_a_repository_stops(self):
        # Given: rn run from a folder no git repository holds.
        os.chdir(self.plugin)
        # When: the conductor asks for the session.
        out = self.stopped("session")
        # Then: rn says what git said and to run it inside the user's repository.
        self.assertRegex(
            out, r"rn: git rev-parse --show-prefix failed: fatal: .*; run rn inside the user's"
        )

    def test_an_unknown_default_branch_stops(self):
        # Given: a repository whose remote's default branch git does not know.
        self.git("symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
        # When: the conductor asks for the session.
        # Then: rn says how to have git learn it.
        self.assertIn("git remote set-head origin --auto", self.stopped("session"))

    def test_a_branch_unrelated_to_the_default_branch_stops(self):
        # Given: a default branch with no history in common with the checked-out branch.
        self.git("checkout", "-q", "--orphan", "lone")
        self.write("lone.md", "# lone\n")
        self.commit()
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")
        self.git("checkout", "-q", "work")
        # When: the conductor asks for the session.
        # Then: rn says the two share no history, and how to fetch it whole.
        self.assertIn(
            "rn: git merge-base origin/main HEAD failed; the checked-out branch shares no history"
            " with origin/main; fetch it whole with `git fetch --unshallow origin`",
            self.stopped("session"),
        )


class StartTest(RepoTest):
    def start(self, slug: str = SLUG, message: str = "Start add-login") -> list[str]:
        """The arguments that start a session with the slug and the message."""
        return ["start", slug, "--message", message]

    def test_start_makes_the_sessions_branch_from_the_remotes_default_branch(self):
        # Given: the branch `work`, holding a commit the default branch does not.
        self.write("work.md", "x\n")
        self.commit()
        # When: the conductor starts a session.
        self.ran(*self.start())
        # Then: the branch named by the slug is checked out, made from origin's main alone.
        here = (self.out("branch", "--show-current"), os.path.exists("work.md"))
        self.assertEqual(here, (f"{SLUG}\n", False))

    def test_start_makes_the_folder_with_an_empty_state(self):
        # Given: a branch with no session.
        # When: the conductor starts one.
        self.ran(*self.start())
        # Then: the folder of today's date and the slug holds an empty state, to be replaced at
        # the first move.
        self.assertEqual(self.read(state_at()), "{}\n")

    def test_start_keeps_the_folder_on_the_remote_with_the_message(self):
        # Given: a branch with no session.
        # When: the conductor starts one with a message.
        self.ran(*self.start(message="Start add-login\n\nFrom the user's words."))
        # Then: the remote's branch holds the state, committed with the message as given.
        kept = (
            self.out("show", f"origin/{SLUG}:{state_at()}"),
            self.out("log", "-1", "--format=%B", f"origin/{SLUG}"),
        )
        self.assertEqual(kept, ("{}\n", "Start add-login\n\nFrom the user's words.\n\n"))

    def test_start_gives_the_session_its_branch_and_the_base(self):
        # Given: a branch with no session.
        # When: the conductor starts one.
        # Then: rn gives the session's folder, its branch and the branch a pull request goes to.
        want = {"session": FOLDER, "branch": SLUG, "base": "main"}
        self.assertEqual(self.ran(*self.start()), want)

    def test_start_with_changes_not_committed_stops_and_stays(self):
        # Given: a file changed and not committed.
        self.write("README.md", "# changed\n")
        # When: the conductor starts a session.
        out = self.stopped(*self.start())
        # Then: rn names the change and says to commit or stash it, and the branch stays.
        said = "rn: the working tree has changes not committed: README.md; rn leaves them as" in out
        self.assertEqual((said, self.out("branch", "--show-current")), (True, "work\n"))

    def test_start_on_a_folder_the_default_branch_holds_stops_and_stays(self):
        # Given: the default branch holding a session folder of today's date and the slug.
        self.git("checkout", "-q", "main")
        self.session()
        self.git("push", "-q")
        self.git("checkout", "-q", "work")
        # When: the conductor starts one with that slug.
        out = self.stopped(*self.start())
        # Then: rn says it is there and to give another slug, and the branch stays.
        said = f"{FOLDER} is on origin/main already; give another slug" in out
        self.assertEqual((said, self.out("branch", "--show-current")), (True, "work\n"))

    def test_start_on_a_branch_there_stops(self):
        # Given: a branch named as the slug.
        self.git("branch", SLUG)
        # When: the conductor starts a session with that slug.
        # Then: rn says what git said and to give another slug.
        self.assertRegex(
            self.stopped(*self.start()),
            rf"rn: git checkout -q --no-track -b {SLUG} origin/main failed: fatal: .*; give"
            " another slug",
        )

    def test_start_with_the_remote_not_reached_stops(self):
        # Given: a remote that cannot be reached.
        self.git("remote", "set-url", "origin", "../none.git")
        # When: the conductor starts a session.
        # Then: rn says what git said and to fix it.
        self.assertRegex(
            self.stopped(*self.start()),
            r"(?s)rn: git fetch -q origin failed: .*; fix it as git says",
        )

    def test_start_below_the_top_stops_and_makes_no_folder(self):
        # Given: rn run from a folder below the top of the repository.
        os.makedirs("src")
        os.chdir("src")
        # When: the conductor starts a session.
        out = self.stopped(*self.start())
        # Then: rn says to run it from the top, and makes no session folder.
        said = "below the top of the repository" in out
        self.assertEqual((said, os.path.exists(os.path.join("..", RECORD))), (True, False))

    def test_a_slug_of_other_characters_stops(self):
        # Given: a slug with a character other than lowercase letters, digits and hyphens.
        # When: the conductor starts a session with it.
        # Then: rn says what a slug holds.
        self.assertIn(
            "the slug '../x' is not lowercase letters, digits and hyphens alone; give it as such",
            self.stopped(*self.start(slug="../x")),
        )

    def test_start_without_a_message_stops_with_the_usage(self):
        # Given: a branch with no session.
        # When: the conductor starts one with no message.
        # Then: rn says the message is required and how the subcommand is given.
        self.assertIn(
            "rn: the following arguments are required: --message; give it as rn.py start",
            self.stopped("start", SLUG),
        )

    def test_start_with_an_empty_message_stops_and_stays(self):
        # Given: a branch with no session.
        # When: the conductor starts one with a message of blanks.
        out = self.stopped(*self.start(message=" \n"))
        # Then: rn says the message is empty, and the branch stays.
        said = "rn: the message is empty; give it in words" in out
        self.assertEqual((said, self.out("branch", "--show-current")), (True, "work\n"))


class StateTest(RepoTest):
    """The state replaced, and every change kept, at each move."""

    def setUp(self) -> None:
        super().setUp()
        self.session(push=True)

    def keep(self, message: str = "Plan approved") -> str:
        """What rn printed, having kept the move with the message."""
        return self.printed("state", "--message", message)

    def refused(self, message: str = "Plan approved") -> str:
        """What rn printed, having stopped keeping the move with the message."""
        return self.stopped("state", "--message", message)

    def head(self, ref: str = "HEAD") -> str:
        """The commit the ref names."""
        return self.out("rev-parse", ref).strip()

    def test_the_state_written_is_kept_on_the_remote_with_the_message(self):
        # Given: the conductor's state for the next move, written whole.
        self.write_json(state_at(), NEXT)
        # When: the conductor keeps the move.
        self.keep("Plan approved\n\nThe user typed /rn:ty.")
        # Then: the remote's branch holds the state, committed with the message as given.
        kept = (
            json.loads(self.out("show", f"origin/work:{state_at()}")),
            self.out("log", "-1", "--format=%B", "origin/work"),
        )
        self.assertEqual(kept, (NEXT, "Plan approved\n\nThe user typed /rn:ty.\n\n"))

    def test_every_change_of_the_move_is_kept_with_the_state(self):
        # Given: the state replaced, a decision written and a work turn made.
        self.write_json(state_at(), NEXT)
        self.write(DECISIONS, "# What the README says\n")
        self.write(WORK_PATH, "# app, made\n")
        # When: the conductor keeps the move.
        self.keep()
        # Then: the remote's branch holds every one of them, and nothing is left.
        changed = self.out("diff", "--name-only", "HEAD~1", "origin/work").split()
        left = self.out("status", "--porcelain")
        self.assertEqual((changed, left), ([DECISIONS, state_at(), WORK_PATH], ""))

    def test_keeping_gives_the_commit(self):
        # Given: the conductor's state for the next move.
        self.write_json(state_at(), NEXT)
        # When: the conductor keeps the move.
        out = json.loads(self.keep())
        # Then: rn gives the commit it kept it in.
        self.assertEqual(out, {"kept": self.head()})

    def test_changes_with_the_state_as_kept_stop_and_keep_nothing(self):
        # Given: a decision written, with the state as last kept.
        self.write(DECISIONS, "# What the README says\n")
        # When: the conductor keeps the move.
        out = self.refused()
        # Then: rn names the changes, says to replace the state first, and commits nothing.
        said = (
            f"rn: the move changed {DECISIONS}, but {state_at()} is as kept last; replace it"
            " whole with the facts this move brought, then run this again"
        ) in out
        self.assertEqual((said, self.head()), (True, self.head("origin/work")))

    def test_nothing_changed_pushes_what_is_committed(self):
        # Given: a move committed but not pushed, as when a push failed.
        self.write_json(state_at(), NEXT)
        self.commit()
        # When: the conductor keeps the move again.
        self.keep()
        # Then: the remote's branch holds it.
        self.assertEqual(self.head("origin/work"), self.head())

    def test_a_state_that_is_not_a_ccs_stops_and_keeps_nothing(self):
        # Given: a state written as a list.
        self.write(state_at(), "[]")
        # When: the conductor keeps the move.
        out = self.refused()
        # Then: rn says it is no CCS and to write it again, and commits nothing.
        said = f"rn: {state_at()} is not a CCS; a CCS is a JSON object of parts" in out
        written = out.rstrip().endswith("; write the state again as one, then run this again")
        self.assertEqual((said, written, self.head()), (True, True, self.head("origin/work")))

    def test_a_state_removed_stops(self):
        # Given: state.json removed.
        os.remove(state_at())
        # When: the conductor keeps the move.
        # Then: rn says to write the state there.
        self.assertIn(
            f"rn: {state_at()} is not there; write the state there, as a CCS, then run this again",
            self.refused(),
        )

    def test_a_plan_in_its_form_with_tasks_is_kept(self):
        # Given: a plan whose tasks are written, one done, each with lines under it.
        tasks = (
            "- [x] T1: Sign in. Serves AC1.\n\n  Completion criterion: a user signs in.\n\n"
            "  - [x] 1. Read the login page.\n- [ ] T2: Carts. Serves AC2.\n"
        )
        self.write(plan_at(), plan_text(tasks=tasks))
        self.write_json(state_at(), NEXT)
        # When: the conductor keeps the move.
        self.keep()
        # Then: the remote's branch holds the plan.
        self.assertIn("T2: Carts", self.out("show", f"origin/work:{plan_at()}"))

    def test_a_plan_out_of_its_form_stops_saying_where(self):
        plans = {
            "a key": (
                PLAN.replace(f"pr: {PR}\n", ""),
                'line 1: expected the frontmatter key "pr", found none',
            ),
            "a heading": (
                PLAN.replace("## Documents", "## Docs"),
                'from line 15: expected the heading "## Documents", found none',
            ),
            "the goal": (
                plan_text(goal="Users sign in."),
                (
                    "expected the goal as `G1: <the user's purpose, with why they want it>` above"
                    " `## Acceptance criteria`, found none"
                ),
            ),
            "a criterion": (
                plan_text(criteria="- AC1: Sign in.\n- Carts."),
                (
                    "line 17: expected an acceptance criterion as `- AC<n>: <one thing the finished"
                    " work must do for the goal>`, found `- Carts.`"
                ),
            ),
            "any criterion": (
                plan_text(criteria="Signing in."),
                (
                    "expected an acceptance criterion as `- AC<n>: <one thing the finished work must"
                    " do for the goal>` under `## Acceptance criteria`, found none"
                ),
            ),
            "a criterion's ID": (
                plan_text(criteria="- AC1: Sign in.\n- AC1: Carts."),
                "line 17: expected each ID once, found AC1 again",
            ),
            "a task": (
                plan_text(tasks="- T1: Sign in.\n"),
                (
                    "line 26: expected a task as `- [ ] T<n>: <the part of the piece of work>`, found"
                    " `- T1: Sign in.`"
                ),
            ),
            "a task's ID": (
                plan_text(tasks="- [ ] T1: Sign in.\n- [x] T1: Carts.\n"),
                "line 27: expected each ID once, found T1 again",
            ),
        }
        for lacking, (plan, point) in plans.items():
            with self.subTest(lacking=lacking):
                # Given: a plan lacking the template's form in one point, and the state replaced.
                self.write(plan_at(), plan)
                self.write_json(state_at(), NEXT)
                # When: the conductor keeps the move.
                out = self.refused()
                # Then: rn says the point it is out of the form by, and commits nothing.
                said = (
                    f"rn: {plan_at()} is out of the form of rn's plan checklist"
                    f" ({self.plan_checklist} F-1): {point};"
                ) in out
                self.assertEqual((said, self.head()), (True, self.head("origin/work")), out)

    def test_a_plan_kept_before_and_out_of_form_now_is_restored(self):
        # Given: a plan kept, then written out of its form.
        self.write(plan_at(), "# Add login\n")
        self.write_json(state_at(), NEXT)
        # When: the conductor keeps the move.
        # Then: rn says to restore the plan kept and have turn make it again.
        self.assertIn(
            f"; the plan is not kept: restore the one kept with `git checkout HEAD -- {plan_at()}`,"
            " replace the state, and have turn make the plan again",
            self.refused(),
        )

    def test_a_plan_never_kept_and_out_of_form_is_removed(self):
        # Given: a session with no plan kept, then a plan written out of its form.
        self.git("rm", "-q", plan_at())
        self.kept()
        self.write(plan_at(), "# Add login\n")
        self.write_json(state_at(), NEXT)
        # When: the conductor keeps the move.
        # Then: rn says to remove the plan and have turn make it again.
        self.assertIn(
            f"; the plan is not kept: remove it with `rm {plan_at()}`, replace the state, and have"
            " turn make the plan again",
            self.refused(),
        )

    def test_without_rns_plan_checklist_stops(self):
        # Given: a plugin folder without rn's plan checklist.
        os.remove(self.plan_checklist)
        self.write_json(state_at(), NEXT)
        # When: the conductor keeps the move.
        # Then: rn says to install rn again.
        self.assertIn(
            f"rn: rn has no checklist for plans in {self.plugin}/checklists; install rn again",
            self.refused(),
        )

    def test_a_plan_checklist_without_its_template_stops(self):
        texts = (
            "# Plan\n",
            "# Plan\n\n### F-1: Shape\n\nNo template.\n",
            "# Plan\n\n### F-1: Shape\n\n```markdown\n# <x>\n",
        )
        for text in texts:
            with self.subTest(text=text):
                # Given: rn's plan checklist holding no fenced template under F-1, or one never
                # closed.
                self.write(self.plan_checklist, text)
                self.write_json(state_at(), NEXT)
                # When: the conductor keeps the move.
                # Then: rn says the checklist holds no template, and to install rn again.
                self.assertIn(
                    f"rn: {self.plan_checklist} holds no template under its F-1; install rn again",
                    self.refused(),
                )

    def test_the_template_is_the_first_fence_under_f1(self):
        # Given: rn's plan checklist with a fence before F-1 and one after its template.
        before = "```text\n# Before\n```\n\n"
        after = "\n\n```text\n# After\n```\n"
        self.write(self.plan_checklist, before + self.read(PLAN_CHECKLIST) + after)
        self.write_json(state_at(), NEXT)
        # When: the conductor keeps the move with a plan in the form of the template under F-1.
        # Then: the plan is kept.
        self.assertEqual(json.loads(self.keep()), {"kept": self.head()})

    def test_a_plan_checklist_whose_template_lane_cannot_read_stops(self):
        # Given: rn's plan checklist whose template holds nothing to check.
        self.write(self.plan_checklist, "### F-1: Shape\n\n```markdown\nplain\n```\n")
        self.write_json(state_at(), NEXT)
        # When: the conductor keeps the move.
        # Then: rn says why, and to install rn again.
        self.assertIn(
            f"rn: {self.plan_checklist} F-1 is no template rn reads: holds no heading and no"
            " frontmatter key, so it would check nothing; install rn again",
            self.refused(),
        )

    def test_an_empty_message_stops(self):
        # Given: the conductor's state for the next move.
        self.write_json(state_at(), NEXT)
        # When: the conductor keeps it with a message of blanks.
        # Then: rn says the message is empty.
        self.assertIn("rn: the message is empty; give it in words", self.refused(" "))

    def test_keeping_without_a_message_stops_with_the_usage(self):
        # Given: the conductor's state for the next move.
        self.write_json(state_at(), NEXT)
        # When: the conductor keeps it with no message.
        # Then: rn says the message is required and how the subcommand is given.
        self.assertIn(
            "rn: the following arguments are required: --message; give it as rn.py state",
            self.stopped("state"),
        )

    def test_keeping_without_a_session_stops(self):
        # Given: a branch with no session.
        self.git("rm", "-q", "-r", RECORD)
        self.kept()
        # When: the conductor keeps a move.
        # Then: rn says to start a session.
        self.assertIn("holds no session; start one with `rn.py start <slug>`", self.refused())

    def test_a_push_that_fails_stops_saying_how_to_push_again(self):
        # Given: the state replaced, and a remote that cannot be reached.
        self.write_json(state_at(), NEXT)
        self.git("remote", "set-url", "origin", "../none.git")
        # When: the conductor keeps the move.
        # Then: rn says what git said and how to push once it is fixed.
        self.assertRegex(
            self.refused(),
            r"(?s)rn: git push -q -u origin HEAD failed: .*; fix it as git says, then push with"
            r" `git push -u origin HEAD`",
        )


class ChecklistsTest(RepoTest):
    def test_rns_own_checklist_is_found_in_any_folder(self):
        # Given: rn's checklist for the kind, in a folder of rn's checklists.
        # When: the conductor asks for the kind's checklists.
        # Then: rn gives its path.
        self.assertEqual(self.ran("checklists", KIND), [self.checklist])

    def test_rns_own_checklist_is_found_straight_in_its_folder(self):
        # Given: rn's checklist for the kind straight in the folder of rn's checklists.
        self.write(os.path.join(self.plugin, "checklists", "usability.md"), "# Usability\n")
        # When: the conductor asks for the kind's checklists.
        # Then: rn gives its path.
        want = [os.path.join(self.plugin, "checklists", "usability.md")]
        self.assertEqual(self.ran("checklists", "usability"), want)

    def test_the_users_addition_comes_after_rns_own(self):
        # Given: rn's checklist for the kind and the user's addition for it.
        added = f"{RECORD}/checklists/{KIND}.md"
        self.write(added, "# Code\n")
        # When: the conductor asks for the kind's checklists.
        # Then: rn gives both, rn's first.
        self.assertEqual(self.ran("checklists", KIND), [self.checklist, added])

    def test_the_users_addition_alone_is_the_whole_checklist(self):
        # Given: a kind rn has no checklist for, with the user's addition for it.
        added = f"{RECORD}/checklists/runbook.md"
        self.write(added, "# Runbook\n")
        # When: the conductor asks for the kind's checklists.
        # Then: rn gives the user's addition alone.
        self.assertEqual(self.ran("checklists", "runbook"), [added])

    def test_a_kind_without_checklists_stops(self):
        # Given: a kind with neither rn's checklist nor the user's addition.
        # When: the conductor asks for its checklists.
        # Then: rn says to make the user's addition first.
        self.assertIn(
            f"make {RECORD}/checklists/runbook.md first", self.stopped("checklists", "runbook")
        )

    def test_a_kind_of_other_characters_stops(self):
        # Given: a kind that would lead out of the checklists' folder.
        # When: the conductor asks for its checklists.
        # Then: rn says what a kind holds.
        self.assertIn(
            "the kind '../code' is not lowercase letters", self.stopped("checklists", "../code")
        )


class CcsTest(RepoTest):
    """The CCS rn writes, read by the parts the comment in rn.py's run_ccs explains."""

    def setUp(self) -> None:
        super().setUp()
        self.write(DECISIONS, "# What the README says\n")
        self.session(push=True)

    def made(self, *more: str) -> Any:
        """What rn printed for the work's CCS, given each option it needs, then more arguments."""
        return self.ran(*ccs_argv(NEEDED), *more)

    def refused(self, *more: str) -> str:
        """What rn printed, having stopped writing the work's CCS, given each option it needs, then
        more arguments."""
        return self.stopped(*ccs_argv(NEEDED), *more)

    def ccs(self) -> Any:
        """The work's CCS rn wrote."""
        return self.read_json(CCS)

    def test_ccs_gives_the_call_to_hand_turn(self):
        # Given: a session, kept.
        # When: the conductor has a work's CCS written.
        out = self.made()
        # Then: rn gives the call naming the CCS, the key of each entry and the result's path.
        # The keys are written out as turn is to read them, not taken from rn.py, so a change to
        # them in rn.py by mistake fails the test; the duplicate-code check leaves them out, as the
        # user chose.
        # pylint: disable=duplicate-code
        want = {
            "ccs": CCS,
            "kind": {
                "work": "deliverable",
                "checklist": "checklist",
                "receiver": "audience",
                "use": "purpose",
                "has": "has",
            },
            "result": CCS_RESULT,
        }
        # pylint: enable=duplicate-code
        self.assertEqual(out, want)

    def test_ccs_names_the_work_and_its_receiver(self):
        # Given: a session, kept.
        # When: the conductor has a work's CCS written.
        self.made()
        # Then: the CCS names the work and its receiver, first.
        want = [{"deliverable": WORK_PATH}, {"audience": NEEDED["--receiver"]}]
        self.assertEqual(self.ccs()["focal_entities"][:2], want)

    def test_ccs_names_each_path_the_receiver_has(self):
        # Given: a session, and a folder and a file in it the receiver has with the work, kept.
        self.write("docs/guide.md", "x\n")
        self.kept()
        # When: the conductor has the work's CCS written with both, after the repository.
        self.made("--has", "docs", "--has", "docs/guide.md")
        # Then: the CCS names each, after the receiver, in the order given.
        want = [{"has": NEEDED["--has"]}, {"has": "docs"}, {"has": "docs/guide.md"}]
        self.assertEqual(self.ccs()["focal_entities"][2:], want)

    def test_ccs_names_what_the_work_is_used_for(self):
        # Given: a session, kept.
        # When: the conductor has a work's CCS written.
        self.made()
        # Then: the CCS names what the work is used for.
        self.assertEqual(self.ccs()["goal_orientation"], [{"purpose": NEEDED["--use"]}])

    def test_ccs_names_the_kinds_checklists_and_the_works_decisions(self):
        # Given: a session, rn's checklist for the kind, the user's addition, and the work's
        # decisions, kept.
        added = f"{RECORD}/checklists/{KIND}.md"
        self.write(added, "# Code\n")
        self.kept()
        # When: the conductor has a work's CCS written.
        self.made()
        # Then: the CCS names rn's checklist, the user's addition, then the decisions.
        want = [{"checklist": self.checklist}, {"checklist": added}, {"decisions": DECISIONS}]
        self.assertEqual(self.ccs()["retrieved_artifacts"], want)

    def test_ccs_of_a_checklist_names_rns_usability_before_the_decisions(self):
        # Given: a session and rn's checklist for checklists, kept.
        self.write(os.path.join(self.plugin, "checklists", "checklist.md"), "# Checklist\n")
        # When: the conductor has the CCS of a checklist written.
        self.ran(*ccs_argv({**NEEDED, "--kind": "checklist"}))
        # Then: the CCS names rn's usability.md as a source, after the checklist and before the
        # decisions, as rn's checklist for checklists makes each from it.
        usability = os.path.join(self.plugin, "checklists", "usability.md")
        self.assertEqual(
            self.ccs()["retrieved_artifacts"][1:], [{"source": usability}, {"decisions": DECISIONS}]
        )

    def test_ccs_takes_the_languages_from_the_plan(self):
        # Given: a session whose plan says the languages.
        # When: the conductor has a work's CCS written.
        self.made()
        # Then: the CCS holds both, first.
        want = [{key: value} for key, value in LANGUAGES.items()]
        self.assertEqual(self.ccs()["constraints"][:2], want)

    def test_ccs_before_the_plan_holds_no_language(self):
        # Given: a session with no plan yet, as before the plan is made.
        self.git("rm", "-q", plan_at())
        self.kept()
        # When: the conductor has the plan's CCS written.
        self.made()
        # Then: the CCS holds no language, only the checklist a change is held to.
        self.assertEqual(self.ccs()["constraints"], [{"fix": self.fix}])

    def test_ccs_names_the_checklist_every_change_is_held_to(self):
        # Given: a session, kept.
        # When: the conductor has a work's CCS written.
        self.made()
        # Then: the CCS names rn's checklist for a fix last among its bounds, so the generator
        # holds it whenever it changes a work already there, in any round.
        self.assertEqual(self.ccs()["constraints"][-1], {"fix": self.fix})

    def test_ccs_is_written_beside_those_kept(self):
        # Given: a session whose ccs/ folder holds the plan's CCS, kept.
        self.write_json(f"{FOLDER}/ccs/plan.json", {})
        self.kept()
        # When: the conductor has another work's CCS written.
        self.made()
        # Then: it is written beside it.
        self.assertEqual(sorted(os.listdir(f"{FOLDER}/ccs")), ["plan.json", f"{WORK}.json"])

    def test_ccs_is_written_one_key_to_a_line(self):
        # Given: a session, kept.
        # When: the conductor has a work's CCS written.
        self.made()
        # Then: it is written one key or value to a line, for the user to read on the pull request.
        self.assertTrue(self.read(CCS).startswith('{\n "focal_entities": [\n  {\n'))

    def test_ccs_holds_text_beyond_ascii_as_it_is(self):
        # Given: a session, kept.
        # When: the conductor has a work's CCS written for a receiver named in Japanese.
        self.ran(*ccs_argv(dict(NEEDED, **{"--receiver": "初めての利用者"})))
        # Then: the CCS holds it as it is, for the user to read on the pull request.
        self.assertIn('"audience": "初めての利用者"', self.read(CCS))

    def test_ccs_without_the_works_decisions_stops(self):
        # Given: a session without the work's decisions, kept.
        self.git("rm", "-q", DECISIONS)
        self.kept()
        # When: the conductor has the work's CCS written.
        out = self.refused()
        # Then: rn says to write and keep the decisions first, and writes no CCS.
        said = (
            f"rn: the work's decisions {DECISIONS} are not there; write there what the work is"
            " made from, keep it, then run this again"
        ) in out
        self.assertEqual((said, os.path.exists(CCS)), (True, False))

    def test_ccs_with_the_record_not_kept_stops(self):
        # Given: a decision written and not kept.
        self.write(DECISIONS, "# What the README says\n\n## License\n\nMIT\n")
        # When: the conductor has the work's CCS written.
        out = self.refused()
        # Then: rn names the change, says to keep it first, and writes no CCS.
        said = (
            f"rn: the record has changes not kept, {DECISIONS}; rn goes on only from what is"
            " pushed, so keep the move with `rn.py state --message <what it brought>` first, then"
            " run this again"
        ) in out
        self.assertEqual((said, os.path.exists(CCS)), (True, False))

    def test_ccs_with_commits_not_pushed_stops(self):
        # Given: a decision committed and not pushed.
        self.write(DECISIONS, "# What the README says\n\n## License\n\nMIT\n")
        self.commit()
        # When: the conductor has the work's CCS written.
        # Then: rn says to push them first.
        self.assertIn(
            "rn: the branch has 1 commit(s) not pushed; push with `git push`, then run this again",
            self.refused(),
        )

    def test_ccs_on_a_branch_never_pushed_stops(self):
        # Given: the session on a branch never pushed.
        self.git("checkout", "-q", "-b", "other")
        # When: the conductor has the work's CCS written.
        # Then: rn says what git said and to push the branch.
        self.assertRegex(
            self.refused(),
            r"rn: git rev-list --count @\{upstream\}\.\.HEAD failed: fatal: .*; push the branch"
            r" with `git push -u origin HEAD`, then run this again",
        )

    def test_ccs_with_what_the_receiver_has_not_there_stops(self):
        # Given: a session, and nothing at a path given as what the receiver has.
        # When: the conductor has a work's CCS written with that path.
        out = self.refused("--has", "docs")
        # Then: rn says it is not there, and to give a file or folder they have, from the top,
        # and writes no CCS.
        said = (
            "rn: what the receiver has, docs, is not there; give the path of a file or folder they"
            " have with the work, from the top"
        ) in out
        self.assertEqual((said, os.path.exists(CCS)), (True, False))

    def test_ccs_below_the_top_stops_saying_to_run_it_from_the_top(self):
        # Given: rn run from a folder below the top of the repository.
        os.makedirs("src")
        os.chdir("src")
        # When: the conductor has a work's CCS written.
        # Then: rn says to run it from the top.
        self.assertIn("below the top of the repository; run it from the top", self.refused())

    def test_ccs_with_an_empty_receiver_stops(self):
        # Given: a session, kept.
        # When: the conductor has a work's CCS written for a receiver of blanks.
        out = self.stopped(*ccs_argv(dict(NEEDED, **{"--receiver": " "})))
        # Then: rn says the receiver is empty.
        self.assertIn("the receiver is empty; give it in words", out)

    def test_ccs_without_an_option_it_needs_stops_with_the_usage(self):
        # Given: a session, kept.
        for option in NEEDED:
            with self.subTest(option=option):
                # When: the conductor has a work's CCS written without the option.
                rest = {k: v for k, v in NEEDED.items() if k != option}
                out = self.stopped(*ccs_argv(rest))
                # Then: rn says the option is required and how the subcommand is given.
                self.assertIn(
                    f"rn: the following arguments are required: {option}; give it as rn.py ccs",
                    out,
                )

    def test_ccs_without_a_session_stops(self):
        # Given: a branch with no session.
        self.git("rm", "-q", "-r", RECORD)
        self.kept()
        # When: the conductor has a work's CCS written.
        # Then: rn says to start a session.
        self.assertIn("holds no session; start one with `rn.py start <slug>`", self.refused())


class ProposalTest(RepoTest):
    """The proposal at a sign-off, made from what is pushed alone, and kept as shown."""

    def setUp(self) -> None:
        super().setUp()
        self.write_json(PLAN_RESULT, {"work": [plan_at()], "items": [], "lessons": []})
        self.session(push=True)

    def proposed(self, signoff: str = "plan") -> str:
        """The proposal rn printed at the sign-off."""
        return self.printed("proposal", signoff)

    def refused(self, signoff: str = "plan") -> str:
        """What rn printed, having stopped putting the proposal together at the sign-off."""
        return self.stopped("proposal", signoff)

    def remade(self, plan: str) -> None:
        """The plan made again as given, and kept."""
        self.write(plan_at(), plan)
        self.kept()

    def test_the_first_proposal_shows_the_goal_and_each_criterion(self):
        # Given: a plan, made by turn and kept, shown at no sign-off before.
        # When: the conductor has the plan's proposal put together.
        # Then: it names the sign-off and the pull request, gives the goal and each criterion,
        # each on a line of its own, and how to answer.
        self.assertEqual(self.proposed(), FIRST + "\n")

    def test_the_proposal_is_kept_as_shown(self):
        # Given: a plan, made by turn and kept.
        # When: the conductor has the plan's proposal put together.
        self.proposed()
        # Then: the remote's branch holds a commit whose message is the proposal, marked with its
        # sign-off, changing nothing.
        kept = (
            self.out("log", "-1", "--format=%B", "origin/work"),
            self.out("diff", "--name-only", "HEAD~1", "origin/work"),
        )
        self.assertEqual(kept, (f"{FIRST}\n\nRn-Sign-off: plan\n\n", ""))

    def test_the_proposal_made_again_shows_what_changed(self):
        # Given: a proposal shown, then the plan made again with one criterion changed and one
        # added.
        self.proposed()
        changed = "- AC1: A user signs in with their email.\n- AC2: Only their cart.\n- AC3: Out."
        self.remade(plan_text(criteria=changed))
        # When: the conductor has the plan's proposal put together again.
        out = self.proposed()
        # Then: it shows each changed and added, and names the rest as before.
        self.assertEqual(
            out.splitlines()[2:],
            [
                "Changed: AC2: Only their cart.",
                "Changed: AC3: Out.",
                "(G1 and AC1 as before)",
                "/rn:ty to approve, /rn:gm <feedback> to ask for a change.",
            ],
        )

    def test_the_proposal_made_again_shows_each_removed(self):
        # Given: a proposal shown, then the plan made again with a criterion removed.
        self.proposed()
        self.remade(plan_text(criteria="- AC1: A user signs in with their email."))
        # When: the conductor has the plan's proposal put together again.
        # Then: it names the criterion removed, and the rest as before.
        self.assertEqual(
            self.proposed().splitlines()[2:4], ["Removed: AC2", "(G1 and AC1 as before)"]
        )

    def test_the_proposal_made_again_names_one_as_before(self):
        # Given: a proposal shown, then the plan made again with every criterion changed.
        self.proposed()
        self.remade(plan_text(criteria="- AC1: Sign in.\n- AC2: Carts."))
        # When: the conductor has the plan's proposal put together again.
        # Then: it names the goal alone as before.
        self.assertEqual(self.proposed().splitlines()[4], "(G1 as before)")

    def test_the_proposal_made_again_names_three_or_more_as_before(self):
        # Given: a proposal shown, then the plan made again with a criterion added.
        self.proposed()
        criteria = "- AC1: A user signs in with their email.\n- AC2: A signed-in user sees only"
        self.remade(plan_text(criteria=f"{criteria} their cart,\n  on every page.\n- AC3: Out."))
        # When: the conductor has the plan's proposal put together again.
        # Then: it names the three as before, the last after "and".
        self.assertIn("(G1, AC1 and AC2 as before)\n", self.proposed())

    def test_the_plan_unchanged_since_shown_gives_the_same_proposal_again(self):
        # Given: a proposal shown, and the plan left as it was, as when the user comes back later.
        self.proposed()
        shown = self.out("rev-parse", "HEAD")
        # When: the conductor has the plan's proposal put together again.
        out = self.proposed()
        # Then: it is the proposal shown before, and nothing more is committed.
        self.assertEqual((out, self.out("rev-parse", "HEAD")), (FIRST + "\n", shown))

    def test_the_plan_changed_elsewhere_names_every_line_as_before(self):
        # Given: a proposal shown, then the plan made again with its goal and criteria as they
        # were.
        self.proposed()
        self.remade(PLAN.replace("- UX: docs/ux.md", "- README: README.md"))
        # When: the conductor has the plan's proposal put together again.
        # Then: it names each as before, and nothing as changed.
        self.assertEqual(self.proposed().splitlines()[2], "(G1, AC1 and AC2 as before)")

    def test_a_criterion_ending_its_section_is_shown_whole(self):
        # Given: a plan whose last criterion runs on to the heading after it, with no blank line.
        self.remade(PLAN.replace("on every page.\n\n## Documents", "on every page.\n## Documents"))
        # When: the conductor has the plan's proposal put together.
        # Then: it shows the criterion whole, and nothing of the heading.
        want = "AC2: A signed-in user sees only their cart, on every page."
        self.assertEqual(self.proposed().splitlines()[4], want)

    def test_the_deliverable_proposal_shows_each_criterion_alone(self):
        # Given: a plan kept, its tasks done.
        # When: the conductor has the deliverable's proposal put together.
        # Then: it names the sign-off and the pull request, and gives each criterion alone.
        self.assertEqual(
            self.proposed("deliverable").splitlines()[:4],
            [
                "Deliverable sign-off",
                f"The finished work is on the pull request: {PR}",
                "AC1: A user signs in with their email.",
                "AC2: A signed-in user sees only their cart, on every page.",
            ],
        )

    def test_each_signoff_reads_only_its_own_proposals(self):
        # Given: a proposal shown at the plan sign-off, then the plan made again.
        self.proposed()
        self.remade(plan_text(criteria="- AC1: A user signs in with their email."))
        # When: the conductor has the deliverable's proposal put together.
        # Then: it is the first at its sign-off, showing each criterion as it is.
        self.assertEqual(
            self.proposed("deliverable").splitlines()[2:],
            [
                "AC1: A user signs in with their email.",
                "/rn:ty to approve, /rn:gm <feedback> to ask for a change.",
            ],
        )

    def test_a_plan_proposal_before_turn_returned_stops(self):
        # Given: a session whose plan turn has not returned, kept.
        self.git("rm", "-q", PLAN_RESULT)
        self.kept()
        # When: the conductor has the plan's proposal put together.
        # Then: rn says turn has not returned it, and to have turn make it.
        self.assertIn(
            f"rn: turn has not returned the plan: {PLAN_RESULT} is not there; have turn:up make it"
            " with the call `rn.py ccs plan ...` printed, then run this again",
            self.refused(),
        )

    def test_a_proposal_with_the_record_not_kept_stops(self):
        # Given: the plan changed and not kept.
        self.write(plan_at(), PLAN + "\n")
        # When: the conductor has the plan's proposal put together.
        # Then: rn says the plan is not kept.
        self.assertIn(f"rn: the record has changes not kept, {plan_at()};", self.refused())

    def test_a_proposal_without_a_plan_stops(self):
        # Given: a session without a plan, kept.
        self.git("rm", "-q", plan_at())
        self.kept()
        # When: the conductor has the deliverable's proposal put together.
        # Then: rn says there is no plan.
        self.assertIn(
            f"rn: the plan {plan_at()} is not there; have turn make it, then run this again",
            self.refused("deliverable"),
        )

    def test_a_proposal_of_a_plan_out_of_its_form_stops(self):
        # Given: a plan out of its form, committed and pushed by hand rather than by rn.
        self.remade(PLAN.replace("G1: ", "Goal: "))
        # When: the conductor has the plan's proposal put together.
        # Then: rn says where, and to have turn make the plan again.
        self.assertIn(
            "expected the goal as `G1: <the user's purpose, with why they want it>` above `##"
            " Acceptance criteria`, found none; have turn make the plan again in that form, keep"
            " it with `rn.py state`, then run this again",
            self.refused(),
        )

    def test_a_signoff_rn_does_not_have_stops(self):
        # Given: a session, kept.
        # When: the conductor has a proposal put together at a sign-off rn does not have.
        # Then: rn names the sign-offs it has.
        self.assertIn("invalid choice: 'review'", self.refused("review"))


# The branch each test's session is on.
BRANCH = "work"
# Where rn shows the learner the session and has it reply, in the repository's git folder: the
# record, read whole, the conductor's conversations, searched, and the list it keeps of each text
# shown with what it stands for.
LEARNING = ".git/rn"
HISTORY = f"{LEARNING}/record/history.txt"
SHOWN_PLAN = f"{LEARNING}/record/{FOLDER}/steering.md"
CONVERSATIONS = f"{LEARNING}/conversations"
REPLY = f"{LEARNING}/learnt.json"
SHOWN_LIST = f"{LEARNING}/records.json"
# What the learner checked, as it says.
CHECKED = "every move of the conductor"


def slug(top: str) -> str:
    """The name Claude Code gives the folder of a project's records, for a path of 200 characters or
    fewer: each character that is not a letter or digit as `-`."""
    return re.sub(r"[^a-zA-Z0-9]", "-", top)


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
    """A session kept, and Claude Code's records in a folder of their own, as CLAUDE_CONFIG_DIR
    names it."""

    def setUp(self) -> None:
        super().setUp()
        self.session(push=True)
        self.top = os.getcwd()
        self.config = os.path.join(self.base, "config")
        patcher = mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": self.config})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.project = os.path.join(self.config, "projects", slug(self.top))

    def conversation(self, name: str, *entries: dict[str, Any]) -> str:
        """Writes the record of a conversation in the project's folder; gives its path."""
        path = os.path.join(self.project, f"{name}.jsonl")
        self.write(path, "".join(json.dumps(e) + "\n" for e in entries))
        return path

    def agent(self, conversation: str, name: str, at: str, meta: dict[str, Any]) -> str:
        """Writes the record of an agent the conversation started, saying its name at the time,
        with its meta file; gives its path."""
        path = os.path.join(conversation[: -len(".jsonl")], "subagents", f"agent-{name}.jsonl")
        self.write(path, json.dumps(said(name, at, self.top)) + "\n")
        self.write_json(path[: -len(".jsonl")] + ".meta.json", meta)
        return path

    def shown(self) -> list[str]:
        """The text of each conversation rn showed the learner, in order."""
        return [self.read(p) for p in self.ran("records")["conversations"]]

    def start(self) -> str:
        """The commit the branch left the default branch at."""
        return self.out("merge-base", "origin/main", "HEAD").strip()

    def range_shown(self) -> str:
        """The commits since the default branch, as rn names the history it showed."""
        return f"git log {self.start()}..{self.out('rev-parse', 'HEAD').strip()}"

    def commit_with(self, message: str) -> None:
        """Commits every change with the message, and pushes it, as a move kept."""
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        self.git("push", "-q")


class RecordsTest(LearningTest):
    def test_records_gives_the_learner_the_record_the_conversations_and_where_to_reply(self):
        # Given: a session kept with its plan, and a conversation of the conductor.
        self.conversation("c1", said("/rn:up add login", "2026-10-20T09:00:00Z", self.top))
        # When: the conductor has the session shown.
        out = self.ran("records")
        # Then: rn gives the learner's prompt: the history and the plan to read whole, the
        # conversation to search, and the reply, each in the git folder.
        want = {
            "record": [os.path.join(self.top, HISTORY), os.path.join(self.top, SHOWN_PLAN)],
            "conversations": [os.path.join(self.top, CONVERSATIONS, "c1.txt")],
            "reply": os.path.join(self.top, REPLY),
        }
        self.assertEqual(out, want)

    def test_the_history_holds_each_commit_with_its_message_and_the_files_it_changed(self):
        # Given: a move kept with its message, which changed a work's decisions, then a proposal
        # kept as an empty commit.
        self.write(f"{FOLDER}/decisions/readme.decisions.md", "# README\n\nMIT\n")
        self.commit_with("deliverable: the user asked for MIT")
        self.git("commit", "-q", "--allow-empty", "-m", "Plan sign-off\n\nRn-Sign-off: plan")
        self.git("push", "-q")
        # When: the conductor has the session shown.
        self.ran("records")
        # Then: the history gives each commit, oldest first, with its message and the files it
        # changed, not their lines, as the record gives each file as it is now.
        commits = self.read(HISTORY).split(" -- ")[0]
        self.assertEqual(
            (
                commits.startswith(f"$ git log --reverse --stat {self.start()}..HEAD\n"),
                "readme.decisions.md | 3 +++" in commits,
                "+MIT" in commits,
                commits.index("deliverable: the user") < commits.index("Rn-Sign-off: plan"),
            ),
            (True, True, False, True),
        )

    def test_the_history_holds_each_state_replaced_by_its_commit(self):
        # Given: a move kept with its message, which replaced the state.
        self.write_json(state_at(), NEXT)
        self.commit_with("design: plan approved")
        # When: the conductor has the session shown.
        self.ran("records")
        # Then: after the commits, the history gives each change to the state under the commit
        # that made it, without its message again.
        head = self.out("rev-parse", "--short", "HEAD").strip()
        states = self.read(HISTORY).split(f" -- {state_at()}\n")[1]
        made = states.split(f"\n{head}\n")
        self.assertEqual(
            (
                len(made),
                '"episodic_trace": [{"fact": "plan approved"}]}' in made[-1],
                "design: plan approved" in states,
            ),
            (2, True, False),
        )

    def test_the_history_names_the_files_a_commit_outside_the_session_changed(self):
        # Given: the work changed by a commit of its own, outside the session's folder.
        self.write("README.md", "# app\n\nMIT\n")
        self.commit_with("README: say MIT")
        # When: the conductor has the session shown.
        self.ran("records")
        # Then: the history gives that commit with the files it changed, not their lines.
        history = self.read(HISTORY)
        self.assertEqual(
            ("    README: say MIT" in history, "README.md | 2 ++" in history, "+MIT" in history),
            (True, True, False),
        )

    def test_the_record_holds_the_plan_each_decisions_and_each_result(self):
        # Given: a session with decisions and results of two works, and its state.
        for path in (f"{FOLDER}/decisions/b.decisions.md", f"{FOLDER}/decisions/a.decisions.md"):
            self.write(path, f"# {path}\n")
        self.write_json(f"{FOLDER}/ccs/a-result.json", {"work": ["A.md"]})
        self.write_json(f"{FOLDER}/ccs/a.json", {"focal_entities": []})
        self.commit_with("works")
        # When: the conductor has the session shown.
        out = self.ran("records")
        # Then: the record gives the history, the plan, each decisions file and each result, as
        # they are, by their paths, and neither the CCS nor the state.
        names = [
            os.path.relpath(p, os.path.join(self.top, LEARNING, "record")) for p in out["record"]
        ]
        self.assertEqual(
            (names, self.read(out["record"][2])),
            (
                [
                    "history.txt",
                    plan_at(),
                    f"{FOLDER}/decisions/a.decisions.md",
                    f"{FOLDER}/decisions/b.decisions.md",
                    f"{FOLDER}/ccs/a-result.json",
                ],
                f"# {FOLDER}/decisions/a.decisions.md\n",
            ),
        )

    def test_a_session_without_its_plan_shows_the_history_alone(self):
        # Given: a session kept without a plan yet.
        self.write_json(state_at(), NEXT)
        os.remove(plan_at())
        self.commit_with("no plan")
        # When: the conductor has the session shown.
        # Then: the record is the history alone.
        self.assertEqual(self.ran("records")["record"], [os.path.join(self.top, HISTORY)])

    def test_a_conversation_shows_the_words_and_tool_calls_without_what_tools_gave_back(self):
        # Given: a conversation with the user's words, the conductor's, a tool call and what it gave
        # back, and a part of the conductor's thinking.
        entries = [
            said("/rn:up", "2026-10-20T09:00:00Z", self.top),
            dict(
                said("", "2026-10-20T09:01:00Z", self.top),
                type="assistant",
                message={
                    "content": [
                        {"type": "thinking", "thinking": "hmm"},
                        {"type": "text", "text": "I keep the move."},
                        {"type": "tool_use", "name": "Bash", "input": {"command": "rn.py state"}},
                    ]
                },
            ),
            dict(
                said("", "2026-10-20T09:02:00Z", self.top),
                message={"content": [{"type": "tool_result", "content": "kept 4f2c9a1"}]},
            ),
        ]
        self.conversation("c", *entries)
        # When: the conductor has the session shown.
        # Then: the words and the call are shown, one to a line, and nothing else.
        self.assertEqual(
            self.shown(),
            [
                '[user] /rn:up\n[text] I keep the move.\n[tool_use Bash] {"command": "rn.py state"}\n'
            ],
        )

    def test_no_conversation_kept_here_shows_the_record_alone(self):
        # Given: no record of a conversation for the repository, as when the session ran on another
        # machine.
        # When: the conductor has the session shown.
        # Then: the learner is given the record, and no conversation.
        self.assertEqual(self.ran("records")["conversations"], [])

    def test_what_each_text_stands_for_is_kept_in_order_for_the_reply(self):
        # Given: two conversations.
        first = self.conversation("b", said("first", "2026-10-20T09:00:00Z", self.top))
        second = self.conversation("a", said("second", "2026-10-20T09:01:00Z", self.top))
        # When: the conductor has the session shown.
        out = self.ran("records")
        # Then: rn keeps each text in one list, the record first, with what it stands for.
        want = {
            "texts": out["record"] + out["conversations"],
            "sources": [self.range_shown(), plan_at(), first, second],
        }
        self.assertEqual(self.read_json(SHOWN_LIST), want)

    def test_the_session_is_shown_afresh(self):
        # Given: a text shown by an earlier run, and a reply it left.
        self.write(f"{CONVERSATIONS}/old.txt", "old")
        self.write(REPLY, "{}")
        # When: the conductor has the session shown.
        self.ran("records")
        # Then: what the earlier run left is gone.
        self.assertEqual((os.path.exists(CONVERSATIONS), os.path.exists(REPLY)), (False, False))

    def test_records_with_a_move_not_kept_stop(self):
        # Given: a change to the session not kept.
        self.write_json(state_at(), NEXT)
        # When: the conductor has the session shown.
        # Then: rn stops, saying to keep the move first, as the learner reads what is pushed.
        self.assertIn("keep the move with `rn.py state --message", self.stopped("records"))

    def test_conversations_come_in_the_order_they_began(self):
        # Given: two conversations named against the order they began.
        self.conversation("b", said("first", "2026-10-20T09:00:00Z", self.top))
        self.conversation("a", said("second", "2026-10-20T10:00:00Z", self.top))
        # When: the conductor has the records shown.
        # Then: each conversation comes in the order it began.
        self.assertEqual(self.shown(), ["[user] first\n", "[user] second\n"])

    def test_a_conversation_begins_at_its_earliest_entry(self):
        # Given: a conversation whose first entry is later than its second, and one between.
        early = said("early", "2026-10-20T09:00:00Z", self.top)
        self.conversation("a", said("late", "2026-10-20T09:10:00Z", self.top), early)
        self.conversation("b", said("between", "2026-10-20T09:05:00Z", self.top))
        # When: the conductor has the records shown.
        # Then: the conversation that began earliest comes first.
        self.assertEqual(self.shown(), ["[user] late\n[user] early\n", "[user] between\n"])

    def test_an_entry_without_a_time_is_passed_over(self):
        # Given: a conversation opening with an entry Claude Code keeps without a time.
        kept = {"type": "mode", "mode": "normal"}
        self.conversation("a", kept, said("later", "2026-10-20T09:10:00Z", self.top))
        self.conversation("b", said("earlier", "2026-10-20T09:05:00Z", self.top))
        # When: the conductor has the records shown.
        # Then: it begins at its first entry with a time.
        self.assertEqual(self.shown(), ["[user] earlier\n", "[user] later\n"])

    def test_a_conversation_on_another_branch_is_left_out(self):
        # Given: a conversation on another branch beside the session's.
        self.conversation("a", said("main", "2026-10-20T09:00:00Z", self.top, "main"))
        self.conversation("b", said("work", "2026-10-20T09:05:00Z", self.top))
        # When: the conductor has the records shown.
        # Then: the session's alone is shown.
        self.assertEqual(self.shown(), ["[user] work\n"])

    def test_a_conversation_that_reached_the_branch_later_is_taken_whole(self):
        # Given: a conversation that began on the default branch and went on on the session's.
        self.conversation(
            "a",
            said("on main", "2026-10-20T09:00:00Z", self.top, "main"),
            said("on work", "2026-10-20T09:05:00Z", self.top),
        )
        # When: the conductor has the records shown.
        # Then: it is shown whole.
        self.assertEqual(self.shown(), ["[user] on main\n[user] on work\n"])

    def test_a_conversation_run_elsewhere_is_left_out(self):
        # Given: a conversation run in a folder below the top, beside one run at the top.
        below = os.path.join(self.top, "docs")
        self.conversation("a", said("below", "2026-10-20T09:00:00Z", below))
        self.conversation("b", said("top", "2026-10-20T09:05:00Z", self.top))
        # When: the conductor has the records shown.
        # Then: the one run at the top alone is shown.
        self.assertEqual(self.shown(), ["[user] top\n"])

    def test_the_agents_a_conversation_started_are_left_out(self):
        # Given: a conversation, an agent it started, and one that agent started in turn.
        conversation = self.conversation("c", said("conductor", "2026-10-20T09:00:00Z", self.top))
        self.agent(conversation, "up", "2026-10-20T09:01:00Z", {"agentType": "turn:up"})
        self.agent(conversation, "gen", "2026-10-20T09:02:00Z", {"parentAgentId": "up"})
        # When: the conductor has the records shown.
        # Then: the conversation alone is shown, as turn's learner reads turn's runs.
        self.assertEqual(self.shown(), ["[user] conductor\n"])

    def test_the_session_shown_leaves_the_working_tree_as_it_was(self):
        # Given: a conversation's record.
        self.conversation("c", said("now", "2026-10-20T09:00:00Z", self.top))
        # When: the conductor has the records shown.
        self.ran("records")
        # Then: git sees no change to keep.
        self.assertEqual(self.out("status", "--porcelain"), "")

    def test_records_without_a_session_stop(self):
        # Given: a branch holding no session.
        self.git("checkout", "-q", "main")
        self.git("checkout", "-q", "-b", "other")
        # When: the conductor has the records shown.
        # Then: rn stops, saying how to start one.
        self.assertIn("holds no session", self.stopped("records"))


class ProjectFoldersTest(LearningTest):
    """Where Claude Code keeps the records of a project, by the project's path."""

    def projects(self, *names: str) -> None:
        """Makes a folder of each name in Claude Code's projects folder."""
        for name in names:
            os.makedirs(os.path.join(self.config, "projects", name))

    def test_a_path_of_200_characters_names_its_folder_whole(self):
        # Given: a path of 200 characters.
        top = "/" + "a" * 199
        # When: its folder is looked for.
        # Then: it is named by the path, each character not a letter or digit as `-`.
        self.assertEqual(
            rn.project_folders(top), [os.path.join(self.config, "projects", "-" + "a" * 199)]
        )

    def test_a_longer_path_is_found_by_its_first_200_characters(self):
        # Given: a path of 201 characters, with the folder Claude Code made for it, its first 200
        # characters and a hash, beside one for another path of the same beginning.
        top = "/" + "a" * 200
        self.projects("-" + "a" * 199 + "-h1", "-" + "a" * 200)
        # When: its folder is looked for.
        # Then: the one of its first 200 characters and a hash is found.
        self.assertEqual(
            rn.project_folders(top),
            [os.path.join(self.config, "projects", "-" + "a" * 199 + "-h1")],
        )

    def test_a_character_beyond_the_basic_plane_is_two(self):
        # Given: a path holding a character JavaScript counts as two.
        # When: its folder is looked for.
        # Then: it stands as two `-`, as Claude Code replaces each half.
        self.assertEqual(
            rn.project_folders("/a\U0001f600b"), [os.path.join(self.config, "projects", "-a--b")]
        )


class LearntTest(LearningTest):
    """The learner's reply, once the session was shown it: the history, the plan, then the
    conductor's conversation, numbered 1 to 3."""

    def setUp(self) -> None:
        super().setUp()
        self.record = self.conversation(
            "c", said("/rn:gm say MIT", "2026-10-20T09:00:00Z", self.top)
        )
        self.ran("records")

    def replied(self, lessons: list[dict[str, Any]], checked: str = CHECKED) -> None:
        """The learner's reply, with the lessons and what it checked."""
        self.write_json(REPLY, {"lessons": lessons, "checked": checked})

    def lesson(self, quote: str = "say MIT", number: int = 3) -> dict[str, Any]:
        """A lesson resting on the quote from the text of the number, by default the
        conversation."""
        return {
            "lesson": "The conductor fixed the README itself.",
            "whose": "general",
            "grounds": [{"record": number, "quote": quote}],
        }

    def test_learnt_keeps_each_lesson_naming_what_each_text_stands_for(self):
        # Given: the learner's reply of one lesson resting on words of each text.
        grounds = [
            {"record": 1, "quote": "git log --reverse --stat"},
            {"record": 2, "quote": "# Add login"},
            {"record": 3, "quote": "say MIT"},
        ]
        self.replied([dict(self.lesson(), grounds=grounds)])
        # When: the conductor takes it.
        out = self.ran("learnt")
        # Then: rn keeps it in the session, each ground naming the commits of the history, the
        # plan's path and the conversation's record, and prints it.
        sources = [self.range_shown(), plan_at(), self.record]
        want = {
            "lessons": [
                dict(
                    self.lesson(),
                    grounds=[dict(g, record=s) for g, s in zip(grounds, sources)],
                )
            ],
            "checked": CHECKED,
        }
        self.assertEqual((out, self.read_json(f"{FOLDER}/learnt.json")), (want, want))

    def test_learnt_of_no_lesson_keeps_what_was_checked(self):
        # Given: the learner's reply of no lesson.
        self.replied([])
        # When: the conductor takes it.
        # Then: rn keeps what the learner checked.
        self.assertEqual(self.ran("learnt"), {"lessons": [], "checked": CHECKED})

    def test_learnt_takes_a_reply_in_a_json_fence(self):
        # Given: the learner's reply written inside a ```json fence.
        self.write(REPLY, "```json\n" + json.dumps({"lessons": [], "checked": CHECKED}) + "\n```")
        # When: the conductor takes it.
        # Then: rn takes the reply inside.
        self.assertEqual(self.ran("learnt")["checked"], CHECKED)

    def test_learnt_removes_what_was_shown_the_learner(self):
        # Given: the learner's reply.
        self.replied([])
        # When: the conductor takes it.
        self.ran("learnt")
        # Then: the records shown and the reply are gone.
        self.assertFalse(os.path.exists(LEARNING))

    def test_a_quote_not_in_its_record_stops_and_has_the_learner_write_again(self):
        # Given: the learner's reply quoting words its record does not hold.
        self.replied([self.lesson("say GPL")])
        # When: the conductor takes it.
        out = self.stopped("learnt")
        # Then: rn stops with the message to send the learner, and the reply is gone for it to
        # write again, the records kept.
        reply = os.path.join(self.top, REPLY)
        message = (
            f"Write your reply to {reply} again in your form, filled:\n"
            "lesson 1: ground 1 is not in record 3 as written; quote its words as they are"
        )
        self.assertEqual(
            (message in out, os.path.exists(REPLY), os.path.exists(SHOWN_LIST)),
            (True, False, True),
        )

    def test_a_quote_is_looked_for_in_the_text_it_numbers(self):
        # Given: the learner's reply quoting the conversation's words as the history's.
        self.replied([self.lesson(number=1)])
        # When: the conductor takes it.
        # Then: rn stops, saying the words are not in the history.
        self.assertIn("ground 1 is not in record 1 as written", self.stopped("learnt"))

    def test_a_reply_that_is_not_json_stops(self):
        # Given: the learner's reply in words, not JSON.
        self.write(REPLY, "No lessons.")
        # When: the conductor takes it.
        # Then: rn stops, saying it has the learner give it as JSON, by SendMessage.
        out = self.stopped("learnt")
        self.assertEqual(
            ("give it as JSON" in out, "send rn:learner by SendMessage" in out), (True, True)
        )

    def test_learnt_without_a_reply_stops(self):
        # Given: no reply written by the learner.
        # When: the conductor takes it.
        # Then: rn stops, saying to have the learner reply first.
        self.assertIn(
            f"rn: the learner's reply {os.path.join(self.top, REPLY)} is not there; start"
            " rn:learner with the prompt `rn.py records` printed and wait for it to end,"
            " then run this again",
            self.stopped("learnt"),
        )

    def test_learnt_before_the_records_were_shown_stops(self):
        # Given: the learner's reply, with no list of the records shown.
        self.replied([])
        os.remove(SHOWN_LIST)
        # When: the conductor takes it.
        # Then: rn stops, saying to show the records first.
        self.assertIn(
            "the session was not shown to the learner; run `rn.py records` first",
            self.stopped("learnt"),
        )

    def test_learnt_without_a_session_stops(self):
        # Given: a branch holding no session.
        self.git("checkout", "-q", "main")
        self.git("checkout", "-q", "-b", "other")
        # When: the conductor takes the learner's reply.
        # Then: rn stops, saying how to start one.
        self.assertIn("holds no session", self.stopped("learnt"))


class CommandTest(RepoTest):
    def test_the_command_prints_and_exits_1_on_a_stop(self):
        # Given: rn.py run as a command, as the conductor runs it, with the plugin's own
        # checklists; run in this process, so that the coverage of the test run counts it.
        script = os.path.join(SCRIPTS, "rn.py")
        out = io.StringIO()
        # When: it is asked for a kind with no checklist.
        argv = mock.patch.object(sys, "argv", [script, "checklists", "no-such-kind"])
        with argv, contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as done:
            runpy.run_path(script, run_name="__main__")
        # Then: it exits 1, saying what went wrong.
        said = "no checklist for the kind no-such-kind" in out.getvalue()
        self.assertEqual((done.exception.code, said), (1, True))

    def test_no_subcommand_stops_with_the_usage(self):
        # Given: rn run with no subcommand.
        # When: it runs.
        # Then: it says a subcommand is required, and names them.
        self.assertIn(
            "required: subcommand; give it as rn.py [-h]"
            " {session,start,state,checklists,ccs,proposal,records,learnt}",
            self.stopped(),
        )


# .claude/rules/plugin.md has CI run Hypothesis on the newest Python alone, so where it is not
# installed, as on 3.9, the property tests are not defined, and the examples alone run.
if importlib.util.find_spec("hypothesis") is not None:
    import hypothesis  # pyrefly: ignore[missing-import]
    from hypothesis import strategies as st  # pyrefly: ignore[missing-import]

    testing.load_hypothesis_profile()
    ALLOWED = "abcdefghijklmnopqrstuvwxyz0123456789-"
    # Any text a line of the plan can hold after an ID: no line break `splitlines` splits at, no
    # lone surrogate, which a UTF-8 file cannot hold, and no blank at either end, which a line of
    # the plan does not keep; some text, as an ID's line is not empty.
    WORDS = st.text(
        st.characters(
            blacklist_categories=("Cs",),
            blacklist_characters="\n\r\x0b\x0c\x1c\x1d\x1e\x85  ",
        ),
        min_size=1,
    ).filter(lambda t: t.strip() == t and t)
    IDS = st.dictionaries(st.sampled_from(["G1", "AC1", "AC2", "AC3"]), st.text(max_size=3))

    class PropertyTest(RepoTest):
        @hypothesis.given(st.text(alphabet=ALLOWED, min_size=1))
        def test_a_slug_of_lowercase_letters_digits_and_hyphens_is_taken(self, slug):
            # Given: any slug of lowercase letters, digits and hyphens.
            # When: it is checked as a name.
            # Then: it is taken as it is.
            self.assertEqual(rn.named(slug, "slug"), slug)

        @hypothesis.given(
            st.tuples(
                st.text(alphabet=ALLOWED),
                st.characters().filter(lambda c: c not in ALLOWED),
                st.text(alphabet=ALLOWED),
            )
        )
        def test_a_name_with_any_other_character_stops(self, parts):
            # Given: any name holding a character other than lowercase letters, digits and hyphens.
            name = "".join(parts)
            # When: it is checked as a name.
            # Then: rn stops, naming it.
            with self.assertRaises(rn.Stop) as stop:
                rn.named(name, "kind")
            self.assertIn(f"the kind {name!r} is not", str(stop.exception))

        @hypothesis.given(st.text(alphabet=ALLOWED, min_size=1), st.booleans())
        def test_any_path_with_a_file_or_folder_there_is_taken(self, name, folder):
            # Given: a file, or a folder, at any path.
            path = os.path.join("held", "folder" if folder else "file", name)
            if folder:
                os.makedirs(path, exist_ok=True)
            else:
                self.write(path, "")
            # When: it is checked as what the receiver has.
            # Then: it is taken as it is.
            self.assertEqual(rn.held(path), path)

        @hypothesis.given(st.text(alphabet=ALLOWED, min_size=1))
        def test_any_path_with_nothing_there_stops(self, name):
            # Given: any path with nothing there.
            path = os.path.join("none", name)
            # When: it is checked as what the receiver has.
            # Then: rn stops, naming it.
            with self.assertRaises(rn.Stop) as stop:
                rn.held(path)
            self.assertIn(f"what the receiver has, {path}, is not there", str(stop.exception))

        @hypothesis.given(st.text().filter(lambda t: t.strip()))
        def test_any_text_with_a_word_is_taken(self, text):
            # Given: any text holding something other than blanks.
            # When: it is checked as given.
            # Then: it is taken as it is.
            self.assertEqual(rn.given(text, "receiver"), text)

        @hypothesis.given(st.text(alphabet=" \t\n\r"))
        def test_any_text_of_blanks_stops(self, text):
            # Given: any text of blanks alone, or nothing.
            # When: it is checked as given.
            # Then: rn stops, saying it is empty.
            with self.assertRaisesRegex(rn.Stop, "the receiver is empty"):
                rn.given(text, "receiver")

        @hypothesis.given(WORDS, st.lists(WORDS, min_size=1, max_size=5))
        def test_the_plan_gives_back_its_goal_and_each_criterion_as_written(self, goal, criteria):
            # Given: a plan in its form whose goal and criteria are any texts a line can hold.
            listed = "\n".join(f"- AC{n}: {c}" for n, c in enumerate(criteria, 1))
            text = plan_text(goal=f"G1: {goal}", criteria=listed)
            self.write("steering.md", text)
            # When: it is held to its form, and its goal and criteria are read.
            held = rn.out_of_form("steering.md", self.plugin)
            # Then: it holds, and gives back each as written, by its ID.
            want = {"G1": goal, **{f"AC{n}": c for n, c in enumerate(criteria, 1)}}
            self.assertEqual((held, rn.decided(text.splitlines(), ("", rn.CRITERIA))), ("", want))

        @hypothesis.given(IDS, IDS)
        def test_what_changed_names_each_line_shown_once(self, before, now):
            # Given: any goal and criteria shown before, and any now.
            # When: what changed is said.
            said = rn.changes(before, now)
            # Then: each now is named once, as changed or among those as before, the last line,
            # and each gone as removed.
            named = [line.split(": ")[1] for line in said if line.startswith("Changed: ")]
            same = [i for i in now if before.get(i) == now[i]]
            removed = [line[len("Removed: ") :] for line in said if line.startswith("Removed: ")]
            last = said[-1] if same else ""
            words = last.removeprefix("(").removesuffix(" as before)").replace(" and ", ", ")
            self.assertEqual(
                (sorted(named), removed, words.split(", ") if same else []),
                (
                    sorted(i for i in now if i not in same),
                    [i for i in before if i not in now],
                    same,
                ),
            )

    class LearningPropertyTest(LearningTest):
        @hypothesis.given(
            st.lists(
                st.datetimes(datetime.datetime(2000, 1, 1), datetime.datetime(2099, 12, 31)).map(
                    lambda t: f"{t:%Y-%m-%dT%H:%M:%S}.{t.microsecond // 1000:03d}Z"
                ),
                min_size=1,
                max_size=4,
                unique=True,
            )
        )
        def test_conversations_come_in_the_order_they_began(self, times):
            # Given: conversations begun at any times, as Claude Code writes them, named in another
            # order.
            shutil.rmtree(self.project, ignore_errors=True)
            for n, at in enumerate(times):
                self.conversation(f"c{n}", said(str(n), at, self.top))
            # When: the conductor has the records shown.
            # Then: each comes in the order it began.
            begun = sorted(range(len(times)), key=lambda n: times[n])
            self.assertEqual(self.shown(), [f"[user] {n}\n" for n in begun])

        @hypothesis.given(st.text(st.characters(blacklist_categories=("Cs",)), max_size=100))
        def test_any_path_names_its_folder_by_letters_digits_and_hyphens(self, top):
            # Given: any path short enough to name its folder whole.
            # When: its folder is looked for.
            # Then: each ASCII letter and digit stands as it is, and each UTF-16 unit of any other
            # character as `-`, as JavaScript counts them.
            want = "".join(
                c if c.isascii() and c.isalnum() else "-" * (len(c.encode("utf-16-le")) // 2)
                for c in top
            )
            self.assertEqual(rn.project_folders(top), [os.path.join(self.config, "projects", want)])


if __name__ == "__main__":
    unittest.main()

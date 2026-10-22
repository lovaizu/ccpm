"""The tests of rn's scripts: each subcommand gives what rn's design and the decisions for the scripts
say, for the conductor that runs it, and stops, saying what went wrong and what to do, on each input
it must not take. Each test runs in a git repository of its own, made in a temporary folder, standing
for the user's repository on a session's branch, beside a plugin folder of its own holding rn's
checklists."""

from __future__ import annotations

import contextlib
import datetime
import importlib.util
import io
import json
import os
import runpy
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
# The work the ccs and proposal tests have made, at its path, with its CCS and turn's result for it.
WORK = "readme"
WORK_PATH = "README.md"
CCS = f"{FOLDER}/ccs/{WORK}.json"
CCS_RESULT = f"{FOLDER}/ccs/{WORK}-result.json"
# The options ccs needs, each with a value it takes.
NEEDED = {"--kind": KIND, "--receiver": "a new user", "--use": "to try it", "--has": "."}
# The state a session starts with, and the state of one waiting at the plan sign-off.
STARTED = {"stage": "asking"}
AT_PLAN = {"stage": "plan", "signoff": "plan"}
# The pull request the plan gives, a plan giving it, and one giving none.
PR = "https://github.com/o/r/pull/1"
PLAN = f"---\npr: {PR}\nstatus: running\n---\n\n# Goal\n"
NO_PR = "---\nstatus: running\n---\n"
# The languages the plan of the ccs tests' session says.
LANGUAGES = {"artifact-language": "English", "conversation-language": "Japanese"}
# Entries of the result turn writes: an item Good, one Good in each part, one without Good, and a
# question an item waits on.
GOOD = {
    "checklist": "c/readme.md",
    "item": "B-1",
    "good": "who it is for",
    "lines": ["README.md:1-3"],
}
PARTS = {
    "checklist": "c/readme.md",
    "item": "B-4",
    "parts": [{"part": "README.md:1-4", "good": "what it is", "lines": ["README.md:3"]}],
}
NOT_GOOD = {
    "checklist": "c/readme.md",
    "item": "B-6",
    "gets": "a stop it clears",
    "places": ["README.md:9"],
}
QUESTION = {
    "question": "Which licence?",
    "recommended": "MIT",
    "items": [{"checklist": "c/readme.md", "item": "B-7"}],
}
RESULT = {"work": [WORK_PATH], "items": [GOOD], "questions": [], "not_good": [], "lessons": []}


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
    """A git repository whose default branch is `main` and whose checked-out branch is `work`, with
    git reading no setting of the machine it runs on; and a plugin folder with rn's checklists."""

    def setUp(self) -> None:
        super().setUp()
        self.repo = self.copied("repo", self.main_and_work)
        self.plugin = os.path.join(self.base, "plugin")
        self.checklist = os.path.join(self.plugin, "checklists", "product", f"{KIND}.md")
        self.write(self.checklist, "# Code\n")

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

    def session(self, folder: str = FOLDER, plan: str | None = PLAN, state: Any = None) -> None:
        """A session's folder committed on the branch, with its plan, none where it is None, and
        its state, at its first stage where none is given."""
        if plan is not None:
            self.write(plan_at(folder), plan)
        self.write_json(state_at(folder), state or STARTED)
        self.commit()


class SessionTest(RepoTest):
    def test_no_session_where_the_branch_changed_none(self):
        # Given: a branch that changed nothing under .rn/.
        # When: the conductor asks for the session.
        # Then: rn says there is none.
        self.assertEqual(self.ran("session"), {"session": None, "state": None})

    def test_the_session_the_branch_changed_is_found_with_its_state(self):
        # Given: a session's folder committed on the branch, waiting at the plan sign-off.
        self.session(state=AT_PLAN)
        # When: the conductor asks for the session.
        # Then: rn gives its folder and its state.
        want = {"session": FOLDER, "state": AT_PLAN}
        self.assertEqual(self.ran("session"), want)

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

    def test_a_session_without_state_reads_as_empty_state(self):
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

    def test_a_plan_without_front_matter_is_not_finished(self):
        for opening in ("status: finished\n---\n", "--\nstatus: finished\n---\n", "x\n"):
            with self.subTest(opening=opening):
                # Given: a session whose plan opens with a line other than `---`, though a `---`
                # may come later.
                self.session(plan=opening)
                # When: the conductor asks for the session.
                # Then: it is found.
                self.assertEqual(self.ran("session")["session"], FOLDER)

    def test_a_plan_whose_front_matter_is_not_closed_is_not_finished(self):
        # Given: a session whose plan opens a front matter it never closes.
        self.session(plan="---\nstatus: finished\n")
        # When: the conductor asks for the session.
        # Then: it is found.
        self.assertEqual(self.ran("session")["session"], FOLDER)

    def test_an_empty_plan_is_not_finished(self):
        # Given: a session whose plan is empty.
        self.session(plan="")
        # When: the conductor asks for the session.
        # Then: it is found.
        self.assertEqual(self.ran("session")["session"], FOLDER)

    def test_an_empty_front_matter_reads_no_line_after_it(self):
        # Given: a session whose plan opens with an empty front matter, and has a `---` later.
        self.session(plan="---\n---\nstatus: finished\n---\n")
        # When: the conductor asks for the session.
        # Then: the status after the front matter is not read, and the session is found.
        self.assertEqual(self.ran("session")["session"], FOLDER)

    def test_a_front_matter_line_without_a_colon_is_passed_over(self):
        # Given: a finished plan whose front matter holds a line with no colon.
        self.session(plan="---\nnotes\nstatus: finished\n---\n")
        # When: the conductor asks for the session.
        # Then: the status is still read, and there is none.
        self.assertIsNone(self.ran("session")["session"])

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

    def test_a_state_that_is_not_an_object_stops(self):
        # Given: a session whose state.json holds a list.
        self.session(state=["plan"])
        # When: the conductor asks for the session.
        # Then: rn says it is not an object and how to restore it.
        self.assertIn(
            f"{state_at()} is not a JSON object; restore it with `git checkout --",
            self.stopped("session"),
        )

    def test_a_state_that_is_not_json_stops(self):
        # Given: a session whose state.json is not JSON.
        self.session()
        self.write(state_at(), "{")
        # When: the conductor asks for the session.
        # Then: rn says it is not JSON and what to make it.
        self.assertIn(
            f"{state_at()} is not JSON; make it again as a JSON object",
            self.stopped("session"),
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
    def test_start_makes_the_session_folder_with_its_state(self):
        # Given: a branch with no session.
        # When: the conductor starts one with a slug.
        self.ran("start", SLUG)
        # Then: the folder of today's date and the slug holds the state at its first stage.
        self.assertEqual(self.read_json(state_at()), STARTED)

    def test_start_gives_the_session_and_its_state(self):
        # Given: a branch with no session.
        # When: the conductor starts one with a slug.
        # Then: rn gives the session's folder and its state, for the conductor to commit.
        want = {"session": FOLDER, "state": STARTED}
        self.assertEqual(self.ran("start", SLUG), want)

    def test_start_writes_the_state_one_key_to_a_line(self):
        # Given: a branch with no session.
        # When: the conductor starts one.
        self.ran("start", SLUG)
        # Then: state.json holds one key to a line, for the user to read on the pull request.
        self.assertEqual(self.read(state_at()), '{\n "stage": "asking"\n}\n')

    def test_start_on_a_folder_there_stops(self):
        # Given: a session folder of today's date and the slug.
        os.makedirs(FOLDER)
        # When: the conductor starts one with that slug.
        # Then: rn says it is there and to give another slug.
        self.assertIn(f"{FOLDER} is there already; give another slug", self.stopped("start", SLUG))

    def test_start_below_the_top_stops(self):
        # Given: rn run from a folder below the top of the repository.
        os.makedirs("src")
        os.chdir("src")
        # When: the conductor starts a session.
        # Then: rn says to run it from the top.
        self.assertIn("below the top of the repository", self.stopped("start", SLUG))

    def test_start_below_the_top_makes_no_folder(self):
        # Given: rn run from a folder below the top of the repository.
        os.makedirs("src")
        os.chdir("src")
        # When: the conductor starts a session.
        self.stopped("start", SLUG)
        # Then: no session folder is made there.
        self.assertFalse(os.path.exists(RECORD))

    def test_a_slug_of_other_characters_stops(self):
        # Given: a slug with a character other than lowercase letters, digits and hyphens.
        # When: the conductor starts a session with it.
        # Then: rn says what a slug holds.
        self.assertIn(
            "the slug '../x' is not lowercase letters, digits and hyphens alone; give it as such",
            self.stopped("start", "../x"),
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
        said = "".join(f"{key}: {value}\n" for key, value in LANGUAGES.items())
        self.session(plan=f"---\n{said}---\n")

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
        # Given: a session.
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
        # Given: a session.
        # When: the conductor has a work's CCS written.
        self.made()
        # Then: the CCS names the work and its receiver, first.
        want = [{"deliverable": WORK_PATH}, {"audience": NEEDED["--receiver"]}]
        self.assertEqual(self.ccs()["focal_entities"][:2], want)

    def test_ccs_names_each_path_the_receiver_has(self):
        # Given: a session, and a folder and a file in it the receiver has with the work.
        self.write("docs/guide.md", "x\n")
        # When: the conductor has the work's CCS written with both, after the repository.
        self.made("--has", "docs", "--has", "docs/guide.md")
        # Then: the CCS names each, after the receiver, in the order given.
        want = [{"has": NEEDED["--has"]}, {"has": "docs"}, {"has": "docs/guide.md"}]
        self.assertEqual(self.ccs()["focal_entities"][2:], want)

    def test_ccs_names_what_the_work_is_used_for(self):
        # Given: a session.
        # When: the conductor has a work's CCS written.
        self.made()
        # Then: the CCS names what the work is used for.
        self.assertEqual(self.ccs()["goal_orientation"], [{"purpose": NEEDED["--use"]}])

    def test_ccs_names_the_kinds_checklists(self):
        # Given: a session, and rn's checklist for the kind.
        # When: the conductor has a work's CCS written.
        self.made()
        # Then: the CCS names the kind's checklist.
        self.assertEqual(self.ccs()["retrieved_artifacts"], [{"checklist": self.checklist}])

    def test_ccs_names_the_decisions_and_each_reference(self):
        # Given: a session, the work's decisions and two references.
        for path in ("d.md", "r1.md", "r2.md"):
            self.write(path, "x\n")
        # When: the conductor has the work's CCS written with them.
        self.made("--decisions", "d.md", "--reference", "r1.md", "--reference", "r2.md")
        # Then: the CCS names each, after the checklists.
        want = [{"decisions": "d.md"}, {"reference": "r1.md"}, {"reference": "r2.md"}]
        self.assertEqual(self.ccs()["retrieved_artifacts"][1:], want)

    def test_ccs_takes_the_languages_from_the_plan(self):
        # Given: a session whose plan says the languages.
        # When: the conductor has a work's CCS written.
        self.made()
        # Then: the CCS holds both.
        want = [{key: value} for key, value in LANGUAGES.items()]
        self.assertEqual(self.ccs()["constraints"], want)

    def test_ccs_before_the_plan_holds_no_language(self):
        # Given: a session with no plan yet, as before the plan is made.
        os.remove(plan_at())
        # When: the conductor has the plan's CCS written.
        self.made()
        # Then: the CCS holds no language.
        self.assertEqual(self.ccs()["constraints"], [])

    def test_ccs_with_decisions_not_there_stops(self):
        # Given: a session, and no file at the decisions' path.
        # When: the conductor has a work's CCS written with that path.
        # Then: rn says the decisions are not there.
        self.assertIn(
            "the decisions d.md is not there; give the path of a file",
            self.refused("--decisions", "d.md"),
        )

    def test_ccs_with_decisions_not_there_writes_no_ccs(self):
        # Given: a session, and no file at the decisions' path.
        # When: the conductor has a work's CCS written with that path.
        self.refused("--decisions", "d.md")
        # Then: no CCS is written.
        self.assertFalse(os.path.exists(os.path.dirname(CCS)))

    def test_ccs_with_a_reference_not_there_stops(self):
        # Given: a session, and no file at a reference's path.
        # When: the conductor has a work's CCS written with that path.
        # Then: rn says the reference is not there.
        self.assertIn("the reference r.md is not there", self.refused("--reference", "r.md"))

    def test_ccs_with_what_the_receiver_has_not_there_stops(self):
        # Given: a session, and nothing at a path given as what the receiver has.
        # When: the conductor has a work's CCS written with that path.
        # Then: rn says it is not there, and to give a file or folder they have, from the top.
        self.assertIn(
            "rn: what the receiver has, docs, is not there; give the path of a file or folder they"
            " have with the work, from the top",
            self.refused("--has", "docs"),
        )

    def test_ccs_below_the_top_stops_saying_to_run_it_from_the_top(self):
        # Given: a folder at the top of the repository the receiver has, and rn run from a folder
        # below the top, where the path to that folder from the top leads nowhere.
        os.makedirs("docs")
        os.makedirs("src")
        os.chdir("src")
        # When: the conductor has a work's CCS written with the path from the top.
        # Then: rn says to run it from the top, after which the same path is found.
        self.assertIn(
            "below the top of the repository; run it from the top", self.refused("--has", "docs")
        )

    def test_ccs_with_what_the_receiver_has_not_there_writes_no_ccs(self):
        # Given: a session, and nothing at a path given as what the receiver has.
        # When: the conductor has a work's CCS written with that path.
        self.refused("--has", "docs")
        # Then: no CCS is written.
        self.assertFalse(os.path.exists(os.path.dirname(CCS)))

    def test_ccs_with_an_empty_receiver_stops(self):
        # Given: a session.
        # When: the conductor has a work's CCS written for a receiver of blanks.
        out = self.stopped(*ccs_argv(dict(NEEDED, **{"--receiver": " "})))
        # Then: rn says the receiver is empty.
        self.assertIn("the receiver is empty; give it in words", out)

    def test_ccs_without_an_option_it_needs_stops_with_the_usage(self):
        # Given: a session.
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
        self.commit()
        # When: the conductor has a work's CCS written.
        out = self.refused()
        # Then: rn says to start a session.
        self.assertIn("holds no session; start one with `rn.py start <slug>`", out)


class StateTest(RepoTest):
    def setUp(self) -> None:
        super().setUp()
        self.session(state=AT_PLAN)

    def test_state_prints_where_the_session_stands(self):
        # Given: a session waiting at the plan sign-off.
        # When: the conductor asks for the state.
        # Then: rn gives it.
        self.assertEqual(self.ran("state"), AT_PLAN)

    def test_asking_for_the_state_leaves_state_json_as_it_was(self):
        # Given: a session whose state.json is written on one line.
        # When: the conductor asks for the state.
        self.ran("state")
        # Then: state.json is as it was, written again by no one.
        self.assertEqual(self.read(state_at()), json.dumps(AT_PLAN))

    def test_state_prints_text_beyond_ascii_as_it_is(self):
        # Given: a session.
        # When: the conductor keeps feedback in Japanese.
        out = self.printed("state", "feedback=理由を書いて")
        # Then: rn prints it as it is, for the conductor to read.
        self.assertIn('"feedback": "理由を書いて"', out)

    def test_state_json_holds_text_beyond_ascii_as_it_is(self):
        # Given: a session.
        # When: the conductor keeps feedback in Japanese.
        self.printed("state", "feedback=理由を書いて")
        # Then: state.json holds it as it is, for the user to read on the pull request.
        self.assertIn('"feedback": "理由を書いて"', self.read(state_at()))

    def test_state_sets_each_key_given(self):
        # Given: a session waiting at the plan sign-off.
        # When: the conductor sets the stage and the feedback.
        self.ran("state", "stage=documents", "feedback=say why")
        # Then: state.json holds both.
        want = {"stage": "documents", "signoff": "plan", "feedback": "say why"}
        self.assertEqual(self.read_json(state_at()), want)

    def test_state_gives_the_state_after_setting(self):
        # Given: a session waiting at the plan sign-off.
        # When: the conductor sets the stage.
        # Then: rn gives the state as it now stands.
        want = {"stage": "documents", "signoff": "plan"}
        self.assertEqual(self.ran("state", "stage=documents"), want)

    def test_an_empty_value_clears_its_key(self):
        # Given: a session waiting at the plan sign-off.
        # When: the conductor sets the sign-off to nothing.
        self.ran("state", "signoff=")
        # Then: state.json names no sign-off.
        self.assertEqual(self.read_json(state_at()), {"stage": "plan"})

    def test_clearing_a_key_not_set_leaves_the_state(self):
        # Given: a session with no feedback kept.
        # When: the conductor clears the feedback.
        self.ran("state", "feedback=")
        # Then: state.json is as it was.
        self.assertEqual(self.read_json(state_at()), AT_PLAN)

    def test_a_stage_rn_does_not_have_stops(self):
        # Given: a session.
        # When: the conductor sets a stage rn does not have.
        # Then: rn names the stages it takes.
        self.assertIn(
            "stage takes one of asking, plan, documents, tasks, deliverable, lessons, ready;"
            " 'review' is none of them",
            self.stopped("state", "stage=review"),
        )

    def test_a_setting_that_stops_leaves_the_state(self):
        # Given: a session waiting at the plan sign-off.
        # When: the conductor sets the feedback and a stage rn does not have.
        self.stopped("state", "feedback=x", "stage=review")
        # Then: state.json is as it was.
        self.assertEqual(self.read_json(state_at()), AT_PLAN)

    def test_an_empty_stage_stops(self):
        # Given: a session.
        # When: the conductor sets the stage to nothing.
        # Then: rn names the stages, without offering to clear it.
        self.assertIn("lessons, ready; '' is none of them", self.stopped("state", "stage="))

    def test_a_signoff_rn_does_not_have_stops(self):
        # Given: a session.
        # When: the conductor sets a sign-off rn does not have.
        # Then: rn names the sign-offs, and that nothing clears it.
        self.assertIn(
            "signoff takes one of plan, design, deliverable, or nothing to clear it",
            self.stopped("state", "signoff=review"),
        )

    def test_a_key_rn_does_not_keep_stops(self):
        # Given: a session.
        # When: the conductor sets a key rn does not keep.
        # Then: rn names the keys it keeps.
        self.assertIn(
            "'shown' is no key rn keeps; give one of stage, signoff, feedback",
            self.stopped("state", "shown=x"),
        )

    def test_a_setting_without_equals_stops(self):
        # Given: a session.
        # When: the conductor gives a key without a value.
        # Then: rn says the `=` is missing and how a setting is given.
        self.assertIn(
            "'stage' has no `=`; give each setting as `<key>=<value>`",
            self.stopped("state", "stage"),
        )


class ProposalTest(RepoTest):
    def setUp(self) -> None:
        super().setUp()
        self.session(state=AT_PLAN)
        self.result(RESULT)

    def result(self, data: Any) -> None:
        """Writes the data as turn's result for the work."""
        self.write_json(CCS_RESULT, data)

    def proposed(self) -> str:
        """The proposal rn printed for the work."""
        return self.printed("proposal", WORK)

    def refused(self) -> str:
        """What rn printed, having stopped putting the work's proposal together."""
        return self.stopped("proposal", WORK)

    def section(self, out: str, heading: str) -> list[str]:
        """The lines of the proposal's section under the heading."""
        return out.split(f"## {heading}\n\n", 1)[1].split("\n\n", 1)[0].splitlines()

    def test_the_proposal_opens_with_the_signoff_and_the_work(self):
        # Given: a session waiting at the plan sign-off, with turn's result for the plan.
        # When: the conductor has the proposal put together.
        # Then: it opens naming the sign-off and the work.
        self.assertTrue(self.proposed().startswith(f"# The plan sign-off: {WORK}\n"))

    def test_the_proposal_shows_each_signoff_done_now_or_ahead(self):
        stands = {
            "plan": ["now", "ahead", "ahead"],
            "design": ["done", "now", "ahead"],
            "deliverable": ["done", "done", "now"],
        }
        for signoff, words in stands.items():
            with self.subTest(signoff=signoff):
                # Given: a session waiting at the sign-off.
                self.write_json(state_at(), dict(AT_PLAN, signoff=signoff))
                # When: the conductor has the proposal put together.
                # Then: it shows each sign-off before it done, it now, and each after it ahead.
                want = [
                    f"- {name} sign-off: {word}"
                    for name, word in zip(("Plan", "Design", "Deliverable"), words)
                ]
                self.assertEqual(self.section(self.proposed(), "Sign-offs"), want)

    def test_the_first_proposal_at_a_signoff_says_so(self):
        # Given: no proposal shown at the plan sign-off before.
        # When: the conductor has the proposal put together.
        # Then: what changed says it is the first.
        want = ["- The first proposal at this sign-off."]
        self.assertEqual(self.section(self.proposed(), "What changed"), want)

    def test_the_proposal_shows_the_items_changed_since_the_last(self):
        # Given: a proposal shown at the plan sign-off, then turn's result made again with one item
        # changed and one added.
        self.proposed()
        self.result(dict(RESULT, items=[dict(GOOD, good="whom it serves"), PARTS]))
        # When: the conductor has the proposal put together again.
        # Then: what changed shows those two alone.
        want = [
            "- c/readme.md B-1: Good: whom it serves (README.md:1-3)",
            "- c/readme.md B-4: Good in each part: README.md:1-4: what it is (README.md:3)",
        ]
        self.assertEqual(self.section(self.proposed(), "What changed"), want)

    def test_a_proposal_with_no_item_changed_says_so(self):
        # Given: a proposal shown at the plan sign-off, and the same result.
        self.proposed()
        # When: the conductor has the proposal put together again.
        # Then: what changed says no item changed.
        want = ["- No item changed since the last proposal at this sign-off."]
        self.assertEqual(self.section(self.proposed(), "What changed"), want)

    def test_the_proposal_shows_the_feedback_sent_back(self):
        # Given: a session that kept the feedback the user sent back at the sign-off.
        self.session(state=dict(AT_PLAN, feedback="say why"))
        # When: the conductor has the proposal put together.
        # Then: what changed opens with the feedback.
        changed = self.section(self.proposed(), "What changed")
        self.assertEqual(changed[0], "- Sent back with: say why")

    def test_the_proposal_links_the_pull_request(self):
        # Given: a plan whose front matter gives the pull request.
        # When: the conductor has the proposal put together.
        # Then: it gives the link.
        self.assertEqual(self.section(self.proposed(), "Pull request"), [PR])

    def test_the_proposal_shows_each_item_good_lacking_or_waiting(self):
        # Given: turn's result with an item Good, one Good in each part, one without Good and one
        # waiting on a question.
        self.result(dict(RESULT, items=[GOOD, PARTS], not_good=[NOT_GOOD], questions=[QUESTION]))
        # When: the conductor has the proposal put together.
        # Then: it shows each item with its Good and lines, what it lacks, or its question.
        want = [
            "- c/readme.md B-1: Good: who it is for (README.md:1-3)",
            "- c/readme.md B-4: Good in each part: README.md:1-4: what it is (README.md:3)",
            "- c/readme.md B-6: lacks: a stop it clears (not found at README.md:9)",
            "- c/readme.md B-7: waits on: Which licence?",
        ]
        self.assertEqual(self.section(self.proposed(), "Checklists"), want)

    def test_a_result_of_questions_alone_shows_each_item_waiting(self):
        # Given: turn's result of questions alone, returned before any work was made.
        self.result({"questions": [QUESTION]})
        # When: the conductor has the proposal put together.
        # Then: it shows the item waiting on its question.
        want = ["- c/readme.md B-7: waits on: Which licence?"]
        self.assertEqual(self.section(self.proposed(), "Checklists"), want)

    def test_the_proposal_keeps_the_items_shown_at_its_signoff(self):
        # Given: a session waiting at the plan sign-off, with turn's result.
        # When: the conductor has the proposal put together.
        self.proposed()
        # Then: state.json keeps the items shown, under the plan sign-off.
        want = {"plan": {"c/readme.md B-1": "Good: who it is for (README.md:1-3)"}}
        self.assertEqual(self.read_json(state_at())["shown"], want)

    def test_a_proposal_without_a_result_stops(self):
        # Given: a session with no result of turn for the work.
        os.remove(CCS_RESULT)
        # When: the conductor has the proposal put together.
        # Then: rn says to run turn:up first.
        self.assertIn(f"{CCS_RESULT} is not there; run turn:up", self.refused())

    def test_a_proposal_while_turn_runs_stops(self):
        # Given: a result turn is still writing, its run kept under "running".
        self.result({"running": {}})
        # When: the conductor has the proposal put together.
        # Then: rn says to wait for turn:up to end.
        self.assertIn(
            f"turn has not returned its result at {CCS_RESULT}; wait for turn:up to end, then run"
            " this again",
            self.refused(),
        )

    def test_a_result_that_is_not_an_object_stops(self):
        # Given: a result that is JSON, but a list.
        self.result([])
        # When: the conductor has the proposal put together.
        # Then: rn says it is not a JSON object, and to have turn:up make the work again.
        self.assertIn(
            f"{CCS_RESULT} is not a result turn writes: it is not a JSON object; have turn:up make"
            " the work again",
            self.refused(),
        )

    def test_a_result_that_is_not_json_stops(self):
        # Given: a result that is not JSON.
        self.write(CCS_RESULT, "{")
        # When: the conductor has the proposal put together.
        # Then: rn says it is not JSON.
        self.assertIn(f"{CCS_RESULT} is not JSON", self.refused())

    def test_a_result_group_that_is_not_a_list_stops(self):
        for key in ("items", "not_good", "questions"):
            with self.subTest(key=key):
                # Given: a result whose group of entries is not a list.
                self.result(dict(RESULT, **{key: {}}))
                # When: the conductor has the proposal put together.
                # Then: rn names the group that is not a list.
                self.assertIn(f'is not a result turn writes: "{key}" is not a list', self.refused())

    def test_a_result_entry_lacking_a_key_stops(self):
        entries = {
            "items": [{"checklist": "c", "item": "B-1", "good": "g"}],
            "not_good": [{"checklist": "c", "item": "B-1", "gets": "g"}],
            "questions": [{"question": "q"}],
        }
        for key, value in entries.items():
            with self.subTest(key=key):
                # Given: a result whose entry lacks a key turn writes.
                self.result(dict(RESULT, **{key: value}))
                # When: the conductor has the proposal put together.
                # Then: rn shows the entry and the keys it should hold.
                shown = json.dumps(value[0])
                self.assertIn(f"the entry {shown} is not an object holding", self.refused())

    def test_a_part_or_waiting_item_lacking_a_key_stops(self):
        entries = {
            "items": [dict(PARTS, parts=[{"part": "p", "good": "g"}])],
            "questions": [dict(QUESTION, items=[{"checklist": "c"}])],
        }
        for key, value in entries.items():
            with self.subTest(key=key):
                # Given: a result whose part, or item waiting on a question, lacks a key.
                self.result(dict(RESULT, **{key: value}))
                # When: the conductor has the proposal put together.
                # Then: rn says the entry is not an object holding the keys turn writes.
                self.assertIn("is not an object holding", self.refused())

    def test_a_result_entry_that_is_not_an_object_stops(self):
        # Given: a result whose items are texts.
        self.result(dict(RESULT, items=["B-1"]))
        # When: the conductor has the proposal put together.
        # Then: rn shows the entry, and says it is not an object.
        self.assertIn(
            'the entry "B-1" is not an object holding checklist, item; have turn:up make the work'
            " again",
            self.refused(),
        )

    def test_lines_that_are_not_a_list_of_texts_stop(self):
        for lines in ("README.md:1", ["README.md:1", 2]):
            with self.subTest(lines=lines):
                # Given: a result whose item's lines are not a list of texts.
                self.result(dict(RESULT, items=[dict(GOOD, lines=lines)]))
                # When: the conductor has the proposal put together.
                # Then: rn shows them, and says they are not a list of texts.
                self.assertIn(f"{json.dumps(lines)} is not a list of texts", self.refused())

    def test_a_proposal_at_no_signoff_stops(self):
        # Given: a session waiting at no sign-off.
        self.session(state=STARTED)
        # When: the conductor has the proposal put together.
        # Then: rn says to set the sign-off first.
        self.assertIn("`rn.py state signoff=<plan|design|deliverable>`", self.refused())

    def test_a_proposal_without_the_pull_request_stops(self):
        # Given: a plan whose front matter gives no pull request.
        self.session(plan=NO_PR, state=AT_PLAN)
        # When: the conductor has the proposal put together.
        # Then: rn says to put its URL in the plan.
        self.assertIn(
            "has no `pr` in its front matter; put the pull request's URL there", self.refused()
        )

    def test_a_proposal_that_stops_keeps_nothing_shown(self):
        # Given: a plan whose front matter gives no pull request.
        self.session(plan=NO_PR, state=AT_PLAN)
        # When: the conductor has the proposal put together.
        self.refused()
        # Then: state.json keeps no item as shown.
        self.assertNotIn("shown", self.read_json(state_at()))


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
            " {session,start,checklists,ccs,state,proposal}",
            self.stopped(),
        )


# .claude/rules/plugin.md has CI run Hypothesis on the newest Python alone, so where it is not
# installed, as on 3.9, the property tests are not defined, and the examples alone run.
if importlib.util.find_spec("hypothesis") is not None:
    import hypothesis  # pyrefly: ignore[missing-import]
    from hypothesis import strategies as st  # pyrefly: ignore[missing-import]

    testing.load_hypothesis_profile()
    ALLOWED = "abcdefghijklmnopqrstuvwxyz0123456789-"
    # Any value a front matter line can hold: every character but the line breaks `splitlines`
    # splits at, which end the line, and the lone surrogates, which a UTF-8 file cannot hold. No
    # value a plan can hold is left out.
    ONE_LINE = st.text(
        st.characters(
            blacklist_categories=("Cs",),
            blacklist_characters="\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029",
        )
    )

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

        @hypothesis.given(
            st.text().filter(lambda k: "=" not in k and k not in rn.SETTABLE), st.text()
        )
        def test_any_key_rn_does_not_keep_stops(self, key, value):
            # Given: any key rn does not keep, with any value.
            # When: it is set.
            # Then: rn stops, saying it is no key rn keeps.
            with self.assertRaisesRegex(rn.Stop, "is no key rn keeps"):
                rn.settings([f"{key}={value}"])

        @hypothesis.given(st.sampled_from(rn.STAGES), st.text())
        def test_any_stage_and_feedback_are_taken(self, stage, feedback):
            # Given: any stage rn has, and any feedback.
            # When: both are set.
            # Then: rn takes each as it is.
            want = {"stage": stage, "feedback": feedback}
            self.assertEqual(rn.settings([f"stage={stage}", f"feedback={feedback}"]), want)

        @hypothesis.given(st.text(), st.lists(st.text()))
        def test_any_good_is_shown_with_its_lines(self, good, lines):
            # Given: turn's result with an item whose Good and lines are any texts.
            result = {"items": [dict(GOOD, good=good, lines=lines)]}
            # When: the proposal's lines are made from it.
            # Then: the item shows its Good and its lines as they are.
            want = {"c/readme.md B-1": f"Good: {good} ({', '.join(lines)})"}
            self.assertEqual(rn.shown(result, "r.json"), want)

        @hypothesis.given(
            st.dictionaries(
                st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=1),
                ONE_LINE.map(str.strip),
            )
        )
        def test_the_front_matter_gives_back_each_line_written(self, keys):
            # Given: a plan whose front matter holds any keys, each with any value a line can
            # hold, without the blanks around it, which the front matter does not keep.
            text = "".join(f"{k}: {v}\n" for k, v in keys.items())
            self.write("steering.md", f"---\n{text}---\n\n# Goal\n")
            # When: its front matter is read.
            # Then: it gives back each key with its value.
            self.assertEqual(rn.front_matter("steering.md"), keys)

        @hypothesis.given(st.text(min_size=1))
        def test_any_feedback_is_kept_as_given(self, feedback):
            # Given: a session, and any feedback the user sends back; an empty one clears the
            # feedback instead, as test_an_empty_value_clears_its_key holds.
            if not os.path.isdir(FOLDER):
                self.session()
            # When: the conductor keeps it in the state.
            self.ran("state", f"feedback={feedback}")
            # Then: the state gives it back as it was given.
            self.assertEqual(self.ran("state")["feedback"], feedback)


if __name__ == "__main__":
    unittest.main()

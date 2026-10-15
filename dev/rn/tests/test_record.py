import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from test_form import FOLDER, HOOKS, PLAN, PLAN_FORM

sys.path.insert(0, HOOKS)

import posttooluse
import record
import stop
from checks import Record, open_names, steering_form, trace

RN = os.path.dirname(HOOKS)
# A plan in the current form holding only what the hooks read of it to find a session's record: its
# rn field and the path of its verification document.
CURRENT = "---\nrn: 0.9.0\nverification: docs/verification.md\n---\n"
NO_PYTHON = "rn: its checks need python3 (3.9 or later); install it and run again\n"
NO_PR = (
    f'rn: in "Working out the plan" of conduct.md, {FOLDER}/steering.md has no `pr` key in its'
    f" front matter; add `pr` as the template in rn's checklists/plan.md gives it, {PLAN_FORM}\n"
)


def git(top, *args):
    subprocess.run(
        ["git", "-C", top, "-c", "user.name=rn", "-c", "user.email=rn@example.com"]
        + ["-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
        check=True,
        capture_output=True,
    )


def write(top, files):
    for path, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(top, path)), exist_ok=True)
        with open(os.path.join(top, path), "w", encoding="utf-8") as f:
            f.write(text)


def repository(case, base, branch, removed=(), default_branch=True):
    """`base` is committed on main and `branch` on a branch from it, so what the branch changed,
    which is how a session is found, stands apart from what main already held."""
    top = tempfile.mkdtemp()
    case.addClassCleanup(shutil.rmtree, top)
    git(top, "init", "-q", "-b", "main")
    write(top, base)
    git(top, "add", "-A")
    git(top, "commit", "-q", "--allow-empty", "-m", "base")
    if default_branch:
        git(top, "update-ref", "refs/remotes/origin/HEAD", "HEAD")
    git(top, "checkout", "-q", "-b", "work")
    write(top, branch)
    for path in removed:
        git(top, "rm", "-q", path)
    git(top, "add", "-A")
    git(top, "commit", "-q", "-m", "work")
    return os.path.realpath(top)


def run(entry, event):
    """Runs an entry file in this process, so a test of where and when the checks run takes
    milliseconds; `hook` alone runs the command as Claude Code does."""
    err = io.StringIO()
    code = 0
    with contextlib.redirect_stderr(err):
        try:
            entry.main(io.StringIO(event if isinstance(event, str) else json.dumps(event)))
        except SystemExit as stopped:
            code = stopped.code
    return code, err.getvalue()


def write_event(top, path):
    return {"cwd": top, "tool_input": {"file_path": os.path.join(top, path)}}


def hook(event_name, cwd, event, path):
    """Runs the command hooks.json gives in `sh`, as Claude Code does, with PATH deciding whether
    python3 is found, so the guard without it is tried as it would run."""
    with open(os.path.join(HOOKS, "hooks.json"), encoding="utf-8") as f:
        command = json.load(f)["hooks"][event_name][0]["hooks"][0]["command"]
    done = subprocess.run(
        [shutil.which("sh") or "sh", "-c", command],
        input=json.dumps(event),
        cwd=cwd,
        env=dict(os.environ, PATH=path, CLAUDE_PLUGIN_ROOT=RN),
        capture_output=True,
        text=True,
        check=False,
    )
    return done.returncode, done.stderr


# A check standing in for the form checks, so that a test of where and when the checks run fails
# only when that breaks, and not when a check of the form does.
STAND_IN = (lambda found: [f"rn: {found.folder} checked."],)


def checked(folder):
    return f"rn: {folder} checked.\n"


def stand_in(case):
    for entry in (posttooluse, stop):
        patcher = mock.patch.object(entry, "CHECKS", STAND_IN)
        patcher.start()
        case.addCleanup(patcher.stop)


def without_python(case):
    """A PATH with git and grep but no python3, so the guard in `sh`, not the entry file, is what
    answers."""
    folder = tempfile.mkdtemp()
    case.addClassCleanup(shutil.rmtree, folder)
    for tool in ("git", "grep"):
        os.symlink(shutil.which(tool) or tool, os.path.join(folder, tool))
    return folder


class EventTest(unittest.TestCase):
    def test_an_event_that_is_not_a_json_object_with_a_folder_is_let_through(self):
        # Given: what Claude Code hands the hook is not JSON, not an object, or names no folder
        # When: the hook reads it
        # Then: there is no event to judge
        for text in ("not json", "[]", '{"tool_name": "Write"}'):
            with self.subTest(text=text):
                self.assertIsNone(record.read_event(io.StringIO(text)))

    def test_a_hook_given_what_is_not_json_lets_the_call_through(self):
        # Given: what Claude Code hands the hook is not JSON
        # When: the hook runs after a write, or at the end of the turn
        # Then: nothing is stopped and nothing is said
        for entry in (posttooluse, stop):
            with self.subTest(entry=entry.__name__):
                self.assertEqual(run(entry, "not json"), (0, ""))

    def test_an_event_naming_its_folder_is_read(self):
        # Given: an event that is a JSON object naming the folder the session works in
        # When: the hook reads it
        # Then: the event is read as given
        event = {"cwd": "/work"}
        self.assertEqual(record.read_event(io.StringIO(json.dumps(event))), event)

    def test_nothing_is_stopped_where_git_is_missing(self):
        # Given: a machine where git cannot be found
        # When: the turn ends in a folder
        # Then: nothing is stopped and nothing is said
        with mock.patch.dict(os.environ, {"PATH": ""}):
            self.assertEqual(run(stop, {"cwd": HOOKS}), (0, ""))

    def test_a_stop_writes_each_sentence_to_standard_error_and_exits_2(self):
        # Given: two sentences of a stop
        # When: they are reported
        # Then: each is written on a line of its own to standard error, and the hook exits 2
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as stopped:
            record.report(["rn: one.", "rn: two."])
        self.assertEqual((stopped.exception.code, err.getvalue()), (2, "rn: one.\nrn: two.\n"))

    def test_nothing_to_report_says_nothing(self):
        # Given: no sentence of a stop
        # When: they are reported
        # Then: nothing is written and the hook goes on
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            record.report([])
        self.assertEqual(err.getvalue(), "")


class SessionsTest(unittest.TestCase):
    """Two plans the branch adds, one it deletes and one main already holds: each way a plan can
    stand to the branch, so the sessions found are seen to be the added two alone."""

    OTHER = ".rn/20261003-other"

    @classmethod
    def setUpClass(cls):
        cls.top = repository(
            cls,
            {".rn/20260901-merged/steering.md": "Merged.\n", ".rn/20260902-gone/steering.md": ""},
            {f"{FOLDER}/steering.md": "Added.\n", f"{cls.OTHER}/steering.md": "Added.\n"},
            removed=(".rn/20260902-gone/steering.md",),
        )

    def test_the_open_sessions_are_the_unfinished_plans_the_branch_changed_and_holds(self):
        # Given: a branch that added two plans and deleted a third, on a main holding a fourth
        # When: the open sessions are found
        # Then: they are the two the branch added
        self.assertEqual(set(record.sessions(self.top)), {FOLDER, self.OTHER})


class BuildTest(unittest.TestCase):
    """A session with every part the record has, one whose verification document is not yet written
    and one an earlier rn started with neither, so `build` is seen to give each part where it is
    and None where it is not."""

    OLDER = ".rn/20261003-older"
    UNWRITTEN = ".rn/20261004-unwritten"

    @classmethod
    def setUpClass(cls):
        cls.top = tempfile.mkdtemp()
        cls.addClassCleanup(shutil.rmtree, cls.top)
        write(
            cls.top,
            {
                f"{FOLDER}/steering.md": CURRENT,
                f"{FOLDER}/open/01-notes-question.md": "Serves: goal\n",
                "docs/verification.md": "Scenes.\n",
                f"{cls.UNWRITTEN}/steering.md": "---\nverification: docs/unwritten.md\n---\n",
                f"{cls.OLDER}/steering.md": "# Goal\n",
            },
        )

    def test_a_sessions_record_holds_its_plan_items_verification_document_and_rn(self):
        # Given: a session with an item in open/ and the verification document its plan names
        # When: its record is built
        # Then: the record holds the plan, each item by name, the document and the rn field
        self.assertEqual(
            record.build(self.top, FOLDER),
            Record(
                FOLDER, CURRENT, {"01-notes-question.md": "Serves: goal\n"}, "Scenes.\n", "0.9.0"
            ),
        )

    def test_a_record_without_items_or_a_verification_document_holds_none(self):
        # Given: a session with no open/ folder and a plan naming no verification document
        # When: its record is built
        # Then: the record holds no item, no document and no rn field
        self.assertEqual(
            record.build(self.top, self.OLDER), Record(self.OLDER, "# Goal\n", {}, None, None)
        )

    def test_a_record_whose_verification_document_is_not_yet_written_holds_none(self):
        # Given: a session whose plan names a verification document that does not exist yet
        # When: its record is built
        # Then: the record holds no document
        self.assertIsNone(record.build(self.top, self.UNWRITTEN).verification)


class WriteTest(unittest.TestCase):
    """A session in the current form beside one an earlier rn started, so each write is seen to be
    checked or passed by according to which session it belongs to."""

    OLDER = ".rn/20261003-older"

    @classmethod
    def setUpClass(cls):
        cls.top = repository(
            cls, {}, {f"{FOLDER}/steering.md": CURRENT, f"{cls.OLDER}/steering.md": "# Goal\n"}
        )

    def setUp(self):
        stand_in(self)

    def test_a_write_to_a_plan_an_item_or_the_verification_document_is_checked(self):
        # Given: a session in the current form
        # When: its plan, an item of its open/, or the verification document its plan names is
        #   written
        # Then: the write is stopped with what the checks say of that session
        for path in (
            f"{FOLDER}/steering.md",
            f"{FOLDER}/open/02-notes-question.md",
            "docs/verification.md",
        ):
            with self.subTest(path=path):
                event = write_event(self.top, path)
                self.assertEqual(run(posttooluse, event), (2, checked(FOLDER)))

    def test_a_write_named_through_another_path_to_the_repository_is_checked(self):
        # Given: a session in the current form, and a link to its repository
        # When: its plan is written by a path through the link
        # Then: the write is stopped with what the checks say of that session
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        link = os.path.join(folder, "link")
        os.symlink(self.top, link)
        event = write_event(link, f"{FOLDER}/steering.md")
        self.assertEqual(run(posttooluse, event), (2, checked(FOLDER)))

    def test_a_write_outside_the_record_is_let_through(self):
        # Given: a session in the current form
        # When: a file outside its record is written
        # Then: nothing is stopped and nothing is said
        self.assertEqual(run(posttooluse, write_event(self.top, "README.md")), (0, ""))

    def test_a_write_to_an_older_sessions_plan_is_checked(self):
        # Given: a session an earlier rn started
        # When: its plan is written
        # Then: the write is stopped with what the checks say of that session
        event = write_event(self.top, f"{self.OLDER}/steering.md")
        self.assertEqual(run(posttooluse, event), (2, checked(self.OLDER)))

    def test_a_write_to_an_older_sessions_item_is_let_through(self):
        # Given: a session an earlier rn started
        # When: an item of its open/ is written
        # Then: nothing is stopped and nothing is said
        event = write_event(self.top, f"{self.OLDER}/open/01-notes-pause.md")
        self.assertEqual(run(posttooluse, event), (0, ""))


class EntryTest(unittest.TestCase):
    def test_each_entry_runs_the_checks_of_the_plan_the_names_of_open_and_the_references(self):
        # Given: the hook run after a write, and the hook run at the end of the turn
        # When: what each runs on a session's record is read
        # Then: it runs the check of the plan's form, that of the names in open/, and that of
        #   the criteria the record refers to
        for entry in (posttooluse, stop):
            for check in (steering_form, open_names, trace):
                with self.subTest(entry=entry.__name__, check=check.__name__):
                    self.assertIn(check.check, entry.CHECKS)


class TurnEndTest(unittest.TestCase):
    def setUp(self):
        stand_in(self)

    def test_the_end_of_a_turn_passes_an_older_session_by(self):
        # Given: a session an earlier rn started
        # When: the turn ends
        # Then: nothing is said of it
        self.assertEqual(stop.at_turn_end(Record(FOLDER, "", {}, None, None)), [])

    def test_the_end_of_a_turn_checks_a_session_from_rn_0_9_0_on(self):
        # Given: a session rn 0.9.0 started
        # When: the turn ends
        # Then: what the checks say of it is given
        found = Record(FOLDER, "", {}, None, "0.9.0")
        self.assertEqual(stop.at_turn_end(found), [checked(FOLDER).strip()])


class BrokenSessionTest(unittest.TestCase):
    """A plan lacking its `pr` key, the smallest breach of the form, so a stop is seen to reach
    standard error and exit 2 through each entry file as Claude Code runs it."""

    @classmethod
    def setUpClass(cls):
        cls.top = repository(
            cls,
            {},
            {f"{FOLDER}/steering.md": PLAN.replace("pr: https://github.com/o/r/pull/1\n", "")},
        )
        cls.no_python = without_python(cls)

    def test_the_end_of_a_turn_is_stopped_with_what_the_checks_say_of_an_open_session(self):
        # Given: an open session
        # When: the turn ends
        # Then: the turn is stopped with what the checks say of that session
        stand_in(self)
        event = {"cwd": self.top}
        self.assertEqual(run(stop, event), (2, checked(FOLDER)))

    def test_nothing_is_stopped_outside_a_repository_even_when_run_from_one(self):
        # Given: a folder that is in no git repository, and the hook itself started from a
        #   repository whose session breaks its form
        # When: the turn ends in that folder
        # Then: nothing is stopped and nothing is said
        stand_in(self)
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.top)
        self.assertEqual(run(stop, {"cwd": folder}), (0, ""))

    def test_a_write_hook_run_as_claude_code_runs_it_stops_a_write_breaking_the_form(self):
        # Given: a session whose plan lacks a key of its form, and python3 on the machine
        # When: Claude Code runs the hook after the plan is written
        # Then: the hook exits 2 with the sentence naming the missing key
        event = write_event(self.top, f"{FOLDER}/steering.md")
        self.assertEqual(hook("PostToolUse", self.top, event, os.environ["PATH"]), (2, NO_PR))

    def test_a_turn_end_hook_run_as_claude_code_runs_it_stops_a_record_breaking_the_form(self):
        # Given: a session whose plan lacks a key of its form, and python3 on the machine
        # When: Claude Code runs the hook at the end of the turn
        # Then: the hook exits 2 with the sentence naming the missing key
        event = {"cwd": self.top}
        self.assertEqual(hook("Stop", self.top, event, os.environ["PATH"]), (2, NO_PR))

    def test_without_python3_a_running_session_is_stopped_with_how_to_install_it(self):
        # Given: a working tree holding a running session's plan, and no python3
        # When: Claude Code runs the hook after a write, or at the end of the turn
        # Then: the hook exits 2 saying python3 is needed and to install it
        for event_name, event in (
            ("PostToolUse", write_event(self.top, "README.md")),
            ("Stop", {"cwd": self.top}),
        ):
            with self.subTest(event_name=event_name):
                self.assertEqual(hook(event_name, self.top, event, self.no_python), (2, NO_PYTHON))

    def test_without_python3_the_second_end_of_the_turn_is_let_through(self):
        # Given: a working tree holding a running session's plan, no python3, and a turn already
        #   stopped once for it
        # When: Claude Code runs the hook at the end of the turn again
        # Then: the turn ends, with nothing said
        event = {"cwd": self.top, "stop_hook_active": True}
        self.assertEqual(hook("Stop", self.top, event, self.no_python), (0, ""))


class FinishedSessionTest(unittest.TestCase):
    """A finished session, so the hooks are seen to stop nothing on a branch whose only session is
    closed, with or without python3."""

    @classmethod
    def setUpClass(cls):
        finished = PLAN.replace("status: running", "status: finished")
        cls.top = repository(cls, {}, {f"{FOLDER}/steering.md": finished})
        cls.no_python = without_python(cls)

    def test_a_finished_session_is_not_open(self):
        # Given: a branch whose only plan is finished
        # When: the open sessions are found
        # Then: there is none
        self.assertEqual(record.sessions(self.top), [])

    def test_without_python3_nothing_is_stopped_where_no_session_runs(self):
        # Given: no python3, in a repository whose sessions are all finished, or in a folder in
        #   no repository
        # When: Claude Code runs the hook after a write, or at the end of the turn
        # Then: nothing is stopped and nothing is said
        outside = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outside)
        for cwd in (self.top, outside):
            for event_name, event in (
                ("PostToolUse", write_event(cwd, "README.md")),
                ("Stop", {"cwd": cwd}),
            ):
                with self.subTest(cwd=cwd, event_name=event_name):
                    self.assertEqual(hook(event_name, cwd, event, self.no_python), (0, ""))


class NoDefaultBranchTest(unittest.TestCase):
    """A running session where origin/HEAD was never set, so the hooks are seen to stop nothing
    rather than guess the default branch, which the conductor sets as each session starts."""

    @classmethod
    def setUpClass(cls):
        cls.top = repository(cls, {}, {f"{FOLDER}/steering.md": PLAN}, default_branch=False)

    def test_no_session_is_open_without_a_default_branch_to_compare_with(self):
        # Given: a branch adding a running plan, where origin's default branch is not known
        # When: the open sessions are found
        # Then: there is none
        self.assertEqual(record.sessions(self.top), [])


if __name__ == "__main__":
    unittest.main()

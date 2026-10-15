import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
HOOKS = ROOT / "rn" / "hooks"
sys.path.insert(0, str(HOOKS))

import record
from test_form import PLAN, VERIFICATION

INSTALL = "rn: its checks need python3 (3.9 or later); install it and run again"
HOOKS_JSON = json.loads((HOOKS / "hooks.json").read_text())["hooks"]


def git(cwd, *args):
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "-c",
            "commit.gpgsign=false",
            "-C",
            str(cwd),
            *args,
        ],
        check=True,
        capture_output=True,
    )


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class Repository(unittest.TestCase):
    """One repository for the class: a session on the default branch, and on the branch `work` a
    running session with a misnamed item of open/, a finished one, two from an earlier rn, and one
    plan written but not committed."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(os.path.realpath(tempfile.mkdtemp()))
        origin, cls.top = cls.tmp / "origin.git", cls.tmp / "work"
        git(cls.tmp, "init", "--bare", str(origin))
        git(origin, "symbolic-ref", "HEAD", "refs/heads/main")
        git(cls.tmp, "clone", str(origin), str(cls.top))
        git(cls.top, "checkout", "-b", "main")
        write(cls.top / ".rn/20260901-main/steering.md", PLAN)
        git(cls.top, "add", ".")
        git(cls.top, "commit", "-m", "main")
        git(cls.top, "push", "origin", "main")
        git(cls.top, "checkout", "-b", "work")
        write(cls.top / ".rn/20261001-open/steering.md", PLAN)
        write(cls.top / ".rn/20261001-open/open/01-note-plan.md", "Where the plan stands.\n")
        write(cls.top / "docs/verification.md", VERIFICATION)
        write(
            cls.top / ".rn/20261002-finished/steering.md",
            PLAN.replace("status: running", "status: finished"),
        )
        write(cls.top / ".rn/20261003-old/steering.md", "Rn version: 0.8.0\n\n# Goal\n")
        write(cls.top / ".rn/20261004-lower/steering.md", PLAN.replace("rn: 0.9.0", "rn: 0.8.9"))
        git(cls.top, "add", ".")
        git(cls.top, "commit", "-m", "sessions")
        write(
            cls.top / ".rn/20261005-new/steering.md",
            PLAN.replace("docs/verification.md", "docs/none.md"),
        )
        cls.with_python3, cls.without_python3 = cls.tmp / "with", cls.tmp / "without"
        for folder, tools in (
            (cls.with_python3, {"git": shutil.which("git"), "python3": sys.executable}),
            (cls.without_python3, {"git": shutil.which("git")}),
        ):
            folder.mkdir()
            for tool, target in tools.items():
                (folder / tool).symlink_to(target or tool)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def found(self):
        return [rec.session for rec in record.records({"cwd": str(self.top)})]

    def test_a_running_session_the_branch_changed_is_found(self):
        # Given: a running session whose plan the branch changed
        # When: the hooks look for the open session
        # Then: that session is found
        self.assertIn(".rn/20261001-open", self.found())

    def test_a_plan_written_but_not_yet_committed_is_found(self):
        # Given: a plan the conductor wrote on the branch and has not committed
        # When: the hooks look for the open session
        # Then: that session is found
        self.assertIn(".rn/20261005-new", self.found())

    def test_a_finished_session_is_not_found(self):
        # Given: a session the branch changed whose status is finished
        # When: the hooks look for the open session
        # Then: that session is not found
        self.assertNotIn(".rn/20261002-finished", self.found())

    def test_a_session_started_under_an_earlier_rn_is_not_found(self):
        # Given: a session the branch changed whose plan has no rn field, and one whose rn field is below 0.9
        # When: the hooks look for the open session
        # Then: neither is found, since /rn:up brings such a record to the current form
        for session in (".rn/20261003-old", ".rn/20261004-lower"):
            with self.subTest(session=session):
                self.assertNotIn(session, self.found())

    def test_a_session_the_branch_did_not_change_is_not_found(self):
        # Given: a running session on the default branch that this branch left as it was
        # When: the hooks look for the open session
        # Then: that session is not found
        self.assertNotIn(".rn/20260901-main", self.found())

    def test_the_record_holds_the_plan_the_items_of_open_the_verification_document_and_the_rn_field(
        self,
    ):
        # Given: the running session, with an item of open/ and the verification document its plan names
        # When: its record is built
        # Then: the record holds the plan, each item by its name, the verification document and the rn field
        rec = record.build(str(self.top), ".rn/20261001-open")
        assert rec is not None
        self.assertEqual(
            (rec.plan, rec.items, rec.verification, rec.rn),
            (PLAN, {"01-note-plan.md": "Where the plan stands.\n"}, VERIFICATION, "0.9.0"),
        )

    def test_a_verification_document_that_does_not_exist_is_read_as_none(self):
        # Given: a plan naming a verification document that does not exist, and no open/
        # When: its record is built
        # Then: the record holds no verification document and no item
        rec = record.build(str(self.top), ".rn/20261005-new")
        assert rec is not None
        self.assertEqual((rec.verification, rec.items), (None, {}))

    def test_a_write_to_the_record_is_checked(self):
        # Given: a write to the plan, an item of open/ or the verification document the plan names
        # When: the hook asks whether the write is the record's
        # Then: it is
        rec = record.build(str(self.top), ".rn/20261001-open")
        assert rec is not None
        for path in (
            ".rn/20261001-open/steering.md",
            ".rn/20261001-open/open/02-notes-question.md",
            "docs/verification.md",
            str(self.top / "docs/verification.md"),
        ):
            with self.subTest(path=path):
                self.assertTrue(
                    record.written({"cwd": str(self.top), "tool_input": {"file_path": path}}, rec)
                )

    def test_a_write_elsewhere_is_not_checked(self):
        # Given: a write outside the record, to another session's plan, or with no file named
        # When: the hook asks whether the write is the record's
        # Then: it is not
        rec = record.build(str(self.top), ".rn/20261001-open")
        assert rec is not None
        for tool_input in (
            {"file_path": "src/app.py"},
            {"file_path": ".rn/20261005-new/steering.md"},
            {"file_path": "docs/design.md"},
            {},
        ):
            with self.subTest(tool_input=tool_input):
                self.assertFalse(
                    record.written({"cwd": str(self.top), "tool_input": tool_input}, rec)
                )

    def test_a_directory_outside_any_repository_lets_every_call_through(self):
        # Given: an event from a directory in no repository, while the hook itself runs in a repository with an open session
        # When: the hooks look for the open session
        # Then: none is found, since only the event's directory says which repository it concerns
        outside = self.tmp / "outside"
        outside.mkdir()
        self.addCleanup(outside.rmdir)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.top)
        self.assertEqual(record.records({"cwd": str(outside)}), [])

    def test_an_entry_of_open_that_is_not_a_file_is_left_out_of_the_record(self):
        # Given: the running session, with a folder inside its open/
        # When: its record is built
        # Then: the record holds no item for the folder
        folder = self.top / ".rn/20261001-open/open/drafts"
        folder.mkdir()
        self.addCleanup(folder.rmdir)
        rec = record.build(str(self.top), ".rn/20261001-open")
        assert rec is not None
        self.assertNotIn("drafts", rec.items)

    def test_an_item_of_open_not_in_utf_8_is_read_with_its_broken_bytes_replaced(self):
        # Given: the running session, with an item of open/ holding a byte that is not UTF-8
        # When: its record is built
        # Then: the record holds the item, the byte replaced and the rest as written
        item = self.top / ".rn/20261001-open/open/02-notes-plan.md"
        item.write_bytes(b"Where \xff stands.\n")
        self.addCleanup(item.unlink)
        rec = record.build(str(self.top), ".rn/20261001-open")
        assert rec is not None
        self.assertEqual(rec.items["02-notes-plan.md"], "Where \ufffd stands.\n")

    def test_the_write_hook_is_run_only_after_a_write_or_an_edit(self):
        # Given: the hooks rn gives Claude Code
        # When: Claude Code picks the tool calls the write hook is run after
        # Then: they are Write and Edit, each by its exact name, and no other
        matcher = HOOKS_JSON["PostToolUse"][0]["matcher"]
        self.assertRegex(matcher, r"^[A-Za-z|]+$")
        self.assertEqual(sorted(matcher.split("|")), ["Edit", "Write"])

    def test_the_write_hook_checks_a_write_to_the_record_and_lets_a_write_elsewhere_through(self):
        # Given: the running session, with an item of open/ not named by the form, and python3 found
        # When: Claude Code runs the write hook's command after a write to that item, and after a write outside the record
        # Then: the first exits 2 with a sentence naming the item on standard error; the second exits 0 and says nothing
        for path, code, said in (
            (
                ".rn/20261001-open/open/01-note-plan.md",
                2,
                "rn: .rn/20261001-open/open/01-note-plan.md",
            ),
            ("src/app.py", 0, ""),
        ):
            with self.subTest(path=path):
                done = self.run_command(
                    "PostToolUse",
                    self.top,
                    self.with_python3,
                    {
                        "cwd": str(self.top),
                        "tool_name": "Write",
                        "tool_input": {"file_path": str(self.top / path)},
                    },
                )
                self.assertEqual(done.returncode, code)
                self.assertEqual(done.stderr[: len(said)], said)
                self.assertEqual(bool(done.stderr), bool(said))

    def test_the_end_of_turn_hook_stops_while_the_form_is_broken(self):
        # Given: the running session, with an item of open/ not named by the form, and python3 found
        # When: Claude Code runs the end of turn hook's command
        # Then: it exits 2 with a sentence naming the item on standard error
        done = self.run_command("Stop", self.top, self.with_python3, {"cwd": str(self.top)})
        self.assertEqual(done.returncode, 2)
        self.assertIn("rn: .rn/20261001-open/open/01-note-plan.md", done.stderr)

    def test_without_python3_a_repository_with_rn_is_told_to_install_it(self):
        # Given: a machine without python3, in a repository with .rn/
        # When: Claude Code runs each hook's command
        # Then: it exits 2, saying python3 is needed and how to go on
        for event in sorted(HOOKS_JSON):
            with self.subTest(event=event):
                done = self.run_command(event, self.top, self.without_python3, {})
                self.assertEqual((done.returncode, done.stderr.strip()), (2, INSTALL))

    def test_without_python3_nothing_is_stopped_outside_a_repository_with_rn(self):
        # Given: a machine without python3, in a directory outside any repository with .rn/
        # When: Claude Code runs each hook's command
        # Then: it exits 0 and says nothing
        for event in sorted(HOOKS_JSON):
            with self.subTest(event=event):
                done = self.run_command(event, self.tmp, self.without_python3, {})
                self.assertEqual((done.returncode, done.stderr), (0, ""))

    def run_command(self, event, cwd, path, data):
        """The hook's command as Claude Code runs it: by a shell, in the session's directory, with
        the plugin's folder in CLAUDE_PLUGIN_ROOT and the event on standard input."""
        return subprocess.run(
            ["/bin/sh", "-c", HOOKS_JSON[event][0]["hooks"][0]["command"]],
            cwd=cwd,
            env={"PATH": str(path), "CLAUDE_PLUGIN_ROOT": str(HOOKS.parent)},
            input=json.dumps(data),
            capture_output=True,
            text=True,
            check=False,
        )


class NoSession(unittest.TestCase):
    def test_an_event_that_is_not_a_json_object_lets_the_call_through(self):
        # Given: an event on standard input that is not JSON, or JSON that is not an object
        # When: the hook reads it
        # Then: no record is found to check
        for text in ("not json", "[]"):
            with self.subTest(text=text):
                self.assertEqual(record.records(record.event(text)), [])

    def test_a_repository_without_rn_is_left_as_it_was(self):
        # Given: a repository with no .rn/ directory, whose remote's default branch it has not yet asked
        # When: the hooks look for the open session
        # Then: none is found, and the repository has still not asked its remote
        with tempfile.TemporaryDirectory() as tmp:
            origin, top = Path(tmp) / "origin.git", Path(tmp) / "work"
            git(tmp, "init", "--bare", str(origin))
            git(tmp, "init", str(top))
            git(top, "commit", "--allow-empty", "-m", "first")
            git(top, "push", str(origin), "HEAD:refs/heads/main")
            git(origin, "symbolic-ref", "HEAD", "refs/heads/main")
            git(top, "remote", "add", "origin", str(origin))
            git(top, "-c", "remote.origin.followRemoteHEAD=never", "fetch", "origin")
            self.assertEqual(record.records({"cwd": str(top)}), [])
            asked = subprocess.run(
                ["git", "-C", str(top), "symbolic-ref", "refs/remotes/origin/HEAD"],
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(asked.returncode, 0)

    def test_a_repository_whose_default_branch_cannot_be_found_lets_every_call_through(self):
        # Given: a repository with .rn/ and no remote to tell its default branch
        # When: the hooks look for the open session
        # Then: none is found
        with tempfile.TemporaryDirectory() as tmp:
            git(tmp, "init")
            write(Path(tmp) / ".rn/20261001-a/steering.md", PLAN)
            self.assertEqual(record.records({"cwd": tmp}), [])

    def test_a_machine_without_git_lets_every_call_through(self):
        # Given: a machine where git cannot be found
        # When: the hooks look for the open session
        # Then: none is found
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"PATH": tmp}):
            self.assertEqual(record.records({"cwd": tmp}), [])


class Report(unittest.TestCase):
    def test_a_call_with_nothing_broken_exits_0_and_says_nothing(self):
        # Given: no check stopped the call
        # When: the hook reports
        # Then: it exits 0 and writes nothing to standard error
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as end:
            record.report([])
        self.assertEqual((end.exception.code, err.getvalue()), (0, ""))

    def test_a_stop_writes_each_sentence_to_standard_error_and_exits_2(self):
        # Given: two checks each stopped the call with a sentence
        # When: the hook reports
        # Then: it exits 2 with each sentence on its own line of standard error
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as end:
            record.report(["rn: one.", "rn: two."])
        self.assertEqual((end.exception.code, err.getvalue()), (2, "rn: one.\nrn: two.\n"))


if __name__ == "__main__":
    unittest.main()

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import pretooluse
from helpers import ROOT, Repo, ccs, fill, form, run, started

WORK = "# Note\n\nRun make.\n"


def pre(repo, tool, given, session="s1"):
    """Runs the PreToolUse entry as Claude Code does before a tool call; returns its exit code and what
    it told Claude."""
    data = {
        "cwd": repo.path,
        "session_id": session,
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": given,
    }
    err = io.StringIO()
    with mock.patch("sys.stdin", io.StringIO(json.dumps(data))), contextlib.redirect_stderr(err):
        code = pretooluse.main()
    return code, err.getvalue()


def commit(repo, message="more"):
    for args in (
        ["add", "-A"],
        ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message],
    ):
        subprocess.run(["git", "-C", repo.path, *args], check=True)


class StartLeavesWorkAlone(unittest.TestCase):
    """A run starts only where it can leave the user's work as git holds it, and with the tools it
    needs."""

    def setUp(self):
        self.repo = Repo()
        self.repo.write("in.json", json.dumps(ccs()))

    def tearDown(self):
        self.repo.close()

    def start(self):
        return run(self.repo, "start", "in.json", "out.json", "s1")

    def test_a_run_is_refused_without_jq_saying_what_to_install(self):
        # Given: a machine where jq is not installed
        empty = tempfile.TemporaryDirectory()
        with mock.patch.dict(os.environ, {"PATH": empty.name}):
            # When: a run starts
            code, out = self.start()
        empty.cleanup()
        # Then: it ends before any work, saying what to install
        self.assertEqual(code, 1)
        self.assertIn("jq is not installed", out)
        self.assertFalse(self.repo.exists(".turn"))

    def test_a_run_is_refused_where_the_work_goes_holds_changes_git_does_not(self):
        cases = [("a committed file changed", True), ("a file never committed", False)]
        for name, committed in cases:
            with self.subTest(name):
                # Given: a file where the work goes whose present text git does not hold
                self.repo.close()
                self.setUp()
                self.repo.write("docs/note.md", "kept\n")
                if committed:
                    commit(self.repo)
                    self.repo.write("docs/note.md", "kept, then changed\n")
                # When: a run starts
                code, out = self.start()
                # Then: it ends saying why, and the file is as it was
                self.assertEqual(code, 1)
                self.assertIn("docs/note.md has changes git does not hold", out)
                self.assertFalse(self.repo.exists(".turn"))
                self.assertTrue(self.repo.read("docs/note.md").startswith("kept"))

    def test_a_run_starts_where_a_committed_file_was_removed(self):
        # Given: a file where the work goes, committed and then removed
        self.repo.write("docs/note.md", "kept\n")
        commit(self.repo)
        os.remove(os.path.join(self.repo.path, "docs/note.md"))
        # When: a run starts
        code, out = self.start()
        # Then: it starts, since git holds what was there
        self.assertEqual(code, 0, out)

    def test_a_run_is_refused_where_the_work_goes_is_ignored_by_git(self):
        # Given: a file where the work goes that git is told to ignore
        self.repo.write(".gitignore", "docs/\n")
        commit(self.repo)
        self.repo.write("docs/note.md", "kept\n")
        # When: a run starts
        code, out = self.start()
        # Then: it ends saying why
        self.assertEqual(code, 1)
        self.assertIn("docs/note.md has changes git does not hold", out)

    def test_a_run_starts_where_git_holds_the_work_as_it_stands(self):
        # Given: a file where the work goes, committed as it stands
        self.repo.write("docs/note.md", "kept\n")
        commit(self.repo)
        # When: a run starts
        code, out = self.start()
        # Then: it starts
        self.assertEqual(code, 0, out)

    def test_a_run_is_refused_outside_a_git_repository(self):
        # Given: the work in a folder git does not keep
        subprocess.run(["rm", "-rf", os.path.join(self.repo.path, ".git")], check=True)
        # When: a run starts
        code, out = self.start()
        # Then: it ends saying what git said
        self.assertEqual(code, 1)
        self.assertIn("not a git repository", out)


class WritesKeptToTheRun(unittest.TestCase):
    """During a run, files are written only where the work goes and in the run's evidence."""

    def setUp(self):
        self.repo = Repo()
        started(self.repo)

    def tearDown(self):
        self.repo.close()

    def at(self, rel):
        return os.path.join(self.repo.path, rel)

    def test_a_write_where_the_work_goes_or_in_the_run_s_evidence_goes_on(self):
        cases = [
            ("the work in the run", "Write", {"file_path": self.at(".turn/out/note.md")}),
            ("a form", "Edit", {"file_path": self.at(form("first-user"))}),
            ("where the work goes", "Write", {"file_path": self.at("docs/note.md")}),
        ]
        for name, tool, given in cases:
            with self.subTest(name):
                # Given: an open run
                # When: a file there is written
                code, said = pre(self.repo, tool, given)
                # Then: the write goes on
                self.assertEqual((code, said), (0, ""))

    def test_a_write_anywhere_else_is_stopped_saying_where_a_run_writes(self):
        cases = [
            ("a source", "Edit", {"file_path": self.at("notes.md")}),
            ("the checklist", "Write", {"file_path": self.at("checklists/note.md")}),
            ("a notebook", "NotebookEdit", {"notebook_path": self.at("a.ipynb")}),
            ("outside the repository", "Write", {"file_path": "/tmp/x.md"}),
            ("beside the run's evidence", "Write", {"file_path": self.at(".turn/out-other/x")}),
        ]
        for name, tool, given in cases:
            with self.subTest(name):
                # Given: an open run
                # When: a file elsewhere is written
                code, said = pre(self.repo, tool, given)
                # Then: the write is stopped, told where a run writes
                self.assertEqual(code, 2)
                self.assertIn("a run writes only docs/note.md and .turn/out/", said)

    def test_a_git_commit_or_push_in_a_run_is_stopped(self):
        for command in (
            "git commit -am x",
            "git -C . push origin main",
            "jq . a.json && git commit -m x",
            "git -c user.name=t commit -m x",
        ):
            with self.subTest(command):
                # Given: an open run
                # When: a shell command commits or pushes
                code, said = pre(self.repo, "Bash", {"command": command})
                # Then: it is stopped, told the user commits
                self.assertEqual(code, 2)
                self.assertIn("a run never commits or pushes", said)

    def test_other_shell_commands_in_a_run_go_on(self):
        for command in (
            "git status --short",
            "git clone -q . /tmp/x",
            "git commit-tree x",
            "jq . a.json",
        ):
            with self.subTest(command):
                # Given: an open run
                # When: a shell command that neither commits nor pushes is run
                code, said = pre(self.repo, "Bash", {"command": command})
                # Then: it goes on
                self.assertEqual((code, said), (0, ""))

    def test_nothing_is_stopped_outside_the_run(self):
        cases = [("another session", "s2"), ("no run open", None)]
        for name, session in cases:
            with self.subTest(name):
                # Given: a write and a commit made outside the run
                if session is None:
                    fill(
                        self.repo,
                        form("orchestrator"),
                        {
                            "note B-1": {"met": True, "lines": "3", "note": "x"},
                            "note F-1": {"met": True, "lines": "1", "note": "x"},
                        },
                    )
                    self.repo.write(".turn/out/note.md", WORK)
                    self.assertEqual(run(self.repo, "end", ".turn/out")[0], 0)
                # When: they are made
                done = [
                    pre(self.repo, "Write", {"file_path": self.at("notes.md")}, session or "s1"),
                    pre(self.repo, "Bash", {"command": "git commit -m x"}, session or "s1"),
                ]
                # Then: they go on
                self.assertEqual(done, [(0, ""), (0, "")])

    def test_the_hooks_do_nothing_without_python3(self):
        # Given: each command Claude Code runs for turn's hooks, on a machine without python3
        with open(os.path.join(ROOT, "turn", "hooks", "hooks.json")) as f:
            commands = [
                h["command"]
                for event in json.load(f)["hooks"].values()
                for m in event
                for h in m["hooks"]
            ]
        empty = tempfile.TemporaryDirectory()
        for command in commands:
            with self.subTest(command):
                # When: Claude Code runs it in a session with a run open
                done = subprocess.run(
                    ["/bin/sh", "-c", command],
                    check=False,
                    input="{}",
                    capture_output=True,
                    text=True,
                    cwd=self.repo.path,
                    env={"PATH": empty.name, "CLAUDE_PLUGIN_ROOT": ROOT},
                )
                # Then: it lets the session go on, saying nothing
                self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""))
        empty.cleanup()

    def test_the_entry_run_as_claude_code_runs_it_stops_a_write_elsewhere(self):
        # Given: the hook's entry file, and an open run
        entry = os.path.join(ROOT, "turn", "hooks", "pretooluse.py")
        data = {
            "cwd": self.repo.path,
            "session_id": "s1",
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": self.at("notes.md")},
        }
        # When: Claude Code runs it before the write
        done = subprocess.run(
            [sys.executable, entry],
            check=False,
            input=json.dumps(data),
            capture_output=True,
            text=True,
        )
        # Then: it stops the write
        self.assertEqual(done.returncode, 2)
        self.assertIn("a run writes only", done.stderr)


class ChangesElsewhereNamed(unittest.TestCase):
    """When a run returns, the user is told of each file changed since it started outside where the
    work goes and the run's evidence."""

    def setUp(self):
        self.repo = Repo()
        self.repo.write("draft.md", "left as it was\n")
        self.repo.write("log.txt", "before\n")
        started(self.repo)
        self.repo.write(".turn/out/note.md", WORK)
        fill(
            self.repo,
            form("orchestrator"),
            {
                "note B-1": {"met": True, "lines": "3", "note": "x"},
                "note F-1": {"met": True, "lines": "1", "note": "x"},
            },
        )

    def tearDown(self):
        self.repo.close()

    def test_a_returned_run_names_each_file_changed_elsewhere_and_no_other(self):
        for command in (("end", ".turn/out"), ("stop", ".turn/out")):
            with self.subTest(command[0]):
                # Given: during the run, a command left a new file, changed one already changed, deleted a
                # committed one, and left another as it was
                self.repo.write("build/out.txt", "left by tests\n")
                self.repo.write("log.txt", "after\n")
                os.remove(os.path.join(self.repo.path, "notes.md"))
                # When: the run returns
                code, out = run(self.repo, *command)
                # Then: the user is told of those three files, and of none turn wrote or that was left
                self.assertEqual(code, 0, out)
                self.assertEqual(
                    out.splitlines()[-1],
                    "Also changed during the run, outside the work: build/out.txt, log.txt, notes.md",
                )
                self.repo.close()
                self.setUp()

    def test_a_returned_run_that_changed_nothing_elsewhere_says_nothing_of_it(self):
        # Given: a run during which nothing outside the work changed
        # When: the run returns
        code, out = run(self.repo, "end", ".turn/out")
        # Then: nothing is said of other files
        self.assertEqual(code, 0, out)
        self.assertNotIn("Also changed", out)


if __name__ == "__main__":
    unittest.main()

import contextlib
import io
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

import helpers
import pretooluse
import stop
from helpers import Repo, laid, run, settle


def hook(entry, repo, **data):
    """Runs a hook's entry as Claude Code does; returns its exit code and what it told Claude."""
    data.setdefault("cwd", repo.path)
    data.setdefault("session_id", "s1")
    err = io.StringIO()
    with mock.patch("sys.stdin", io.StringIO(json.dumps(data))), contextlib.redirect_stderr(err):
        code = entry.main()
    return code, err.getvalue()


def call_turn(repo, args, session="s1"):
    return hook(
        pretooluse,
        repo,
        session_id=session,
        tool_name="Skill",
        tool_input={"skill": "turn:up", "args": args},
    )


def write(repo, path, tool="Write", session="s1"):
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    return hook(pretooluse, repo, session_id=session, tool_name=tool, tool_input={key: path})


class TurnCalled(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.folder = laid(self.repo, "doc")
        settle(self.repo, self.folder)
        _, self.lines = run(self.repo, "ccs", self.folder)

    def tearDown(self):
        self.repo.close()

    def test_turn_called_with_the_ccs_the_script_wrote_goes_on(self):
        # Given: the CCS the script wrote from the settled form
        # When: turn is called with the two lines the script printed
        code, said = call_turn(self.repo, self.lines)
        # Then: the call goes on
        self.assertEqual((code, said), (0, ""))

    def test_turn_called_with_a_ccs_changed_after_the_script_wrote_it_is_stopped(self):
        # Given: the CCS was changed by hand after the script wrote it
        path = f"{self.folder}/in-1.json"
        ccs = self.repo.json(path)
        ccs["focal_entities"][1] = {"receiver": "someone else"}
        self.repo.write(path, json.dumps(ccs))
        # When: turn is called with it
        code, said = call_turn(self.repo, self.lines)
        # Then: the call is stopped, saying which step makes the CCS
        self.assertEqual(code, 2)
        self.assertIn(f"step 5: settle the form, and run `up.py ccs {self.folder}`", said)

    def test_turn_called_with_any_other_ccs_is_stopped(self):
        # Given: a CCS written by hand beside the job's
        self.repo.write("mine.json", self.repo.read(f"{self.folder}/in-1.json"))
        # When: turn is called with it
        code, said = call_turn(self.repo, "in: mine.json\nout: back.json")
        # Then: the call is stopped
        self.assertEqual(code, 2)
        self.assertIn("step 5", said)

    def test_the_hook_run_as_claude_code_runs_it_stops_the_call(self):
        # Given: the hook's entry file, and a call of turn with a CCS of no job
        entry = os.path.join(helpers.ROOT, "writ", "hooks", "pretooluse.py")
        data = {
            "cwd": self.repo.path,
            "session_id": "s1",
            "tool_name": "Skill",
            "tool_input": {"skill": "turn:up", "args": "in: mine.json\nout: back.json"},
        }
        # When: Claude Code runs it
        done = subprocess.run(
            [sys.executable, entry],
            check=False,
            input=json.dumps(data),
            capture_output=True,
            text=True,
        )
        # Then: it stops the call, naming writ
        self.assertEqual(done.returncode, 2)
        self.assertTrue(done.stderr.startswith("writ: step 5"))


class WriteInJob(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.folder = laid(self.repo, "doc")

    def tearDown(self):
        self.repo.close()

    def test_writ_writing_its_own_job_files_goes_on(self):
        # Given: a job is open
        # When: writ writes in its job's folder, with each tool that writes
        for tool in ("Write", "Edit", "NotebookEdit"):
            code, said = write(
                self.repo, os.path.join(self.repo.path, self.folder, "notes.md"), tool
            )
            # Then: it goes on
            self.assertEqual((code, said), (0, ""))

    def test_writ_writing_the_document_or_any_other_file_is_stopped(self):
        # Given: a job is open
        for path in ("README.md", "LICENSE", ".writ/checklists/notes.md"):
            # When: writ writes it itself
            code, said = write(self.repo, path)
            # Then: it is stopped, told that turn writes the document and every checklist
            self.assertEqual(code, 2)
            self.assertIn(f"a job writes only {self.folder}/", said)
            self.assertIn("the document and every checklist are written by turn", said)

    def test_a_write_while_turn_s_run_is_open_is_left_to_turn(self):
        # Given: turn's run is open in this session
        self.repo.write(".turn/run.json", json.dumps({"session": "s1"}))
        # When: the document is written
        code, said = write(self.repo, "README.md")
        # Then: writ's hook lets it go on, as turn's own hooks keep the run to its files
        self.assertEqual((code, said), (0, ""))


class Ended(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.folder = laid(self.repo, "doc")

    def tearDown(self):
        self.repo.close()

    def stops(self, **data):
        return hook(stop, self.repo, hook_event_name="Stop", **data)

    def test_writ_stopping_while_its_job_is_open_is_kept_at_it_once(self):
        # Given: a job is open, and no question waits on the user
        # When: writ stops, and stops again after being told
        code, said = self.stops()
        again, _ = self.stops(stop_hook_active=True)
        # Then: it is kept at work once, told how the job ends
        self.assertEqual(code, 2)
        self.assertIn(
            f"step 10: the job is open; go on with its steps, and end it with `up.py end {self.folder}`",
            said,
        )
        self.assertEqual(again, 0)

    def test_the_hook_run_as_claude_code_runs_it_keeps_writ_at_its_job(self):
        # Given: the hook's entry file, and a job open with no question waiting
        entry = os.path.join(helpers.ROOT, "writ", "hooks", "stop.py")
        data = {"cwd": self.repo.path, "session_id": "s1", "hook_event_name": "Stop"}
        # When: Claude Code runs it as writ stops
        done = subprocess.run(
            [sys.executable, entry],
            check=False,
            input=json.dumps(data),
            capture_output=True,
            text=True,
        )
        # Then: it keeps writ at work, naming writ
        self.assertEqual(done.returncode, 2)
        self.assertTrue(done.stderr.startswith("writ: step 10"))

    def test_writ_stopping_to_wait_on_the_user_s_answer_goes_on(self):
        # Given: the form says a question waits on the user
        form = self.repo.json(f"{self.folder}/form.json")
        form["asking"] = "Which license is the tool under?"
        self.repo.write(f"{self.folder}/form.json", json.dumps(form))
        # When: writ stops
        code, said = self.stops()
        # Then: it stops
        self.assertEqual((code, said), (0, ""))

    def test_writ_stopping_before_its_form_is_laid_goes_on(self):
        # Given: a job has started, and writ asks which checklist to write to before laying a form
        os.remove(os.path.join(self.repo.path, self.folder, "form.json"))
        # When: writ stops to wait on the answer
        code, said = self.stops()
        # Then: it stops
        self.assertEqual((code, said), (0, ""))

    def test_writ_stopping_while_turn_s_run_is_open_is_left_to_turn(self):
        # Given: turn's run is open in this session
        self.repo.write(".turn/run.json", json.dumps({"session": "s1"}))
        # When: Claude stops
        code, said = self.stops()
        # Then: writ's hook says nothing, as turn's own keeps its run going
        self.assertEqual((code, said), (0, ""))


class OutsideAJob(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_nothing_is_stopped_where_no_job_of_this_session_is_open(self):
        # Given: no job is open, and then a job open in another session
        for other in (False, True):
            if other:
                laid(self.repo, "doc")
            # When: a file is written, turn is called, and Claude stops, in session s2
            got = [
                write(self.repo, "README.md", session="s2"),
                call_turn(self.repo, "in: x.json\nout: y.json", session="s2"),
                hook(stop, self.repo, session_id="s2", hook_event_name="Stop"),
            ]
            # Then: nothing is stopped
            self.assertEqual(got, [(0, "")] * 3)

    def test_another_skill_or_tool_is_not_looked_at(self):
        # Given: a job is open
        laid(self.repo, "doc")
        # When: another skill is called, and a file is read
        got = [
            hook(pretooluse, self.repo, tool_name="Skill", tool_input={"skill": "other:up"}),
            hook(pretooluse, self.repo, tool_name="Read", tool_input={"file_path": "x"}),
        ]
        # Then: nothing is stopped
        self.assertEqual(got, [(0, "")] * 2)

    def test_without_python3_the_hooks_do_nothing(self):
        # Given: the hooks as Claude Code runs them, on a machine without python3
        with open(os.path.join(helpers.ROOT, "writ", "hooks", "hooks.json")) as f:
            commands = [
                h["command"]
                for entries in json.load(f)["hooks"].values()
                for entry in entries
                for h in entry["hooks"]
            ]
        for command in commands:
            # When: one runs with no python3 on the PATH
            done = subprocess.run(
                ["/bin/sh", "-c", command],
                check=False,
                env={
                    "PATH": "/nonexistent",
                    "CLAUDE_PLUGIN_ROOT": os.path.join(helpers.ROOT, "writ"),
                },
                capture_output=True,
            )
            # Then: it lets everything go on
            self.assertEqual(done.returncode, 0, command)

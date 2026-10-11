"""Tests for the check run before each tool call, fed what Claude Code feeds it."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
HOOK = os.path.join(PLUGIN_ROOT, "hooks", "pretooluse.py")
UP = os.path.join(PLUGIN_ROOT, "scripts", "up.py")
ACCEPTANCE = "Starts the app by following the guide alone"

CCS = {
    "focal_entities": [{"deliverable": "SETUP.md"}, {"receiver": "A new team member"}],
    "goal_orientation": [{"acceptance": ACCEPTANCE}],
    "retrieved_artifacts": [{"viewpoint": "viewpoint.md"}],
    "constraints": [], "episodic_trace": [], "semantic_gist": [], "relational_map": [],
    "predictive_cue": [], "uncertainty_signal": [],
}


class PreToolUseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = os.path.realpath(tempfile.mkdtemp())
        cls.repo = os.path.join(cls.root, "repo")
        cls.session = str(uuid.uuid4())
        os.makedirs(cls.repo)
        for path, text in (("viewpoint.md", "- Steps run as typed.\n"), (".t/in.json", json.dumps(CCS))):
            os.makedirs(os.path.dirname(os.path.join(cls.repo, path)), exist_ok=True)
            with open(os.path.join(cls.repo, path), "w", encoding="utf-8") as f:
                f.write(text)
        run = lambda *a: subprocess.run(a, cwd=cls.repo, check=True, capture_output=True, text=True)  # noqa
        run("git", "init", "-q")
        run("git", "add", "-A")
        run("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "s")
        with open(os.path.join(cls.repo, "SETUP.md"), "w", encoding="utf-8") as f:
            f.write("# Setup\n")
        cls.work = run(sys.executable, UP, "start", ".t/in.json", ".t/out.json", cls.session).stdout.splitlines()[0][6:]
        cls.copy = run(sys.executable, UP, "copy", cls.work).stdout.strip()

    @classmethod
    def tearDownClass(cls):
        for path in (cls.root, cls.work, cls.copy):
            shutil.rmtree(path, True)

    def call(self, tool, given, agent=None, cwd=None, session=None):
        data = {"session_id": session or self.session, "hook_event_name": "PreToolUse", "tool_name": tool,
                "tool_input": given, "cwd": cwd or self.repo}
        if agent:
            data.update(agent_id="a1", agent_type=agent)
        result = subprocess.run([sys.executable, HOOK], input=json.dumps(data), capture_output=True, text=True)
        self.assertIn(result.returncode, (0, 2), result.stderr)
        return result.stderr.strip() if result.returncode == 2 else None

    def test_outside_a_turn_of_this_session_every_call_goes_through(self):
        # Given: a session with no turn running
        given = {"command": "git commit -m x"}
        # When: the generator asks to commit
        reason = self.call("Bash", given, agent="turn:generator", session=str(uuid.uuid4()))
        # Then: it goes through
        self.assertIsNone(reason)

    def test_the_first_user_works_on_files_inside_its_copy_only(self):
        # Given: the first user's file and agent calls: reading and writing in its copy, reading and searching outside it, editing the deliverable, and starting an agent
        cases = [("Read", {"file_path": os.path.join(self.copy, "viewpoint.md")}, None),
                 ("Read", {"file_path": "viewpoint.md"}, "outside"),
                 ("Grep", {"pattern": "x", "path": self.repo}, "outside"),
                 ("Glob", {"pattern": "*.md"}, "outside"),
                 ("Write", {"file_path": os.path.join(self.copy, "var/log"), "content": ""}, None),
                 ("Edit", {"file_path": os.path.join(self.copy, "SETUP.md")}, "the deliverable"),
                 ("Agent", {"subagent_type": "Explore", "prompt": "look"}, None)]
        for tool, given, said in cases:
            with self.subTest(tool=tool, given=given):
                # When: each is asked for
                reason = self.call(tool, given, agent="turn:first-user")
                # Then: those inside the copy and the agent go through, those outside are stopped as outside, and editing the deliverable is stopped
                if said is None:
                    self.assertIsNone(reason)
                else:
                    self.assertIn(said, reason)

    def test_the_first_user_writes_its_report_in_the_work_folder_and_touches_nothing_else_there(self):
        # Given: the first user writing its report, and writing and reading should.md, in the work folder
        cases = [("Write", {"file_path": os.path.join(self.work, "first-user-1.md"), "content": ""}, None),
                 ("Write", {"file_path": os.path.join(self.work, "should.md"), "content": ""}, "outside"),
                 ("Read", {"file_path": os.path.join(self.work, "should.md")}, "outside")]
        for tool, given, said in cases:
            with self.subTest(tool=tool, given=given):
                # When: each is asked for
                reason = self.call(tool, given, agent="turn:first-user")
                # Then: the report goes through, and should.md is stopped as outside both times
                if said is None:
                    self.assertIsNone(reason)
                else:
                    self.assertIn(said, reason)

    def test_the_first_user_runs_commands_inside_its_copy_only(self):
        # Given: the first user's commands: one that moves into the copy first, one run from the copy, one run from the repository, one that reads a file in the repository, and one into the copy with an unclosed quote
        cases = [({"command": f"cd {self.copy} && npm start"}, self.repo, None),
                 ({"command": "npm start"}, self.copy, None),
                 ({"command": "npm start"}, self.repo, "cd into"),
                 ({"command": f"cat {self.repo}/viewpoint.md"}, self.copy, "outside"),
                 ({"command": f'cd {self.copy} && echo "unclosed'}, self.repo, None)]
        for given, cwd, said in cases:
            with self.subTest(given=given, cwd=cwd):
                # When: each is asked for
                reason = self.call("Bash", given, agent="turn:first-user", cwd=cwd)
                # Then: those in the copy go through, the one from the repository is told to move into the copy, and the one reading outside is stopped as outside
                if said is None:
                    self.assertIsNone(reason)
                else:
                    self.assertIn(said, reason)

    def test_the_generator_changes_nothing_in_the_repository_but_the_deliverable(self):
        # Given: the generator writing the deliverable, editing another file in the repository, writing outside the repository, and reading in it
        outside = os.path.join(self.root, "scratch", "try.sh")
        cases = [("Write", {"file_path": os.path.join(self.repo, "SETUP.md")}, None),
                 ("Edit", {"file_path": os.path.join(self.repo, "viewpoint.md")}, "only the deliverable"),
                 ("Write", {"file_path": outside}, None),
                 ("Read", {"file_path": os.path.join(self.repo, "viewpoint.md")}, None)]
        for tool, given, said in cases:
            with self.subTest(tool=tool, given=given):
                # When: each is asked for
                reason = self.call(tool, given, agent="turn:generator")
                # Then: all go through but the edit, which is stopped as not the deliverable
                if said is None:
                    self.assertIsNone(reason)
                else:
                    self.assertIn(said, reason)

    def test_only_the_generator_changes_the_deliverable(self):
        # Given: the learner and the evaluator editing and writing the deliverable, writing their own files in the work folder, and reading the deliverable
        deliverable = os.path.join(self.repo, "SETUP.md")
        cases = [("turn:learner", "Edit", {"file_path": deliverable}, True),
                 ("turn:evaluator", "Write", {"file_path": deliverable}, True),
                 ("turn:learner", "Write", {"file_path": os.path.join(self.work, "learner-1.json")}, False),
                 ("turn:evaluator", "Write", {"file_path": os.path.join(self.work, "evaluator-1.json")}, False),
                 ("turn:evaluator", "Read", {"file_path": deliverable}, False)]
        for agent, tool, given, stopped in cases:
            with self.subTest(agent=agent, tool=tool, given=given):
                # When: each is asked for
                reason = self.call(tool, given, agent=agent)
                # Then: every change to the deliverable is stopped, and the rest go through
                self.assertEqual(reason is not None and "only the generator changes the deliverable" in reason,
                                 stopped)

    def test_no_agent_of_turn_commits_or_pushes(self):
        # Given: commits and pushes by the generator, evaluator and learner, one inside a longer command and one with an unclosed quote, beside git status and a commit by an agent not of turn
        cases = [("git commit -m x", "turn:generator", True), ("git -C . push", "turn:evaluator", True),
                 ("npm test && git commit -am y", "turn:learner", True), ("git status", "turn:generator", False),
                 ("git commit -m x", "Explore", False), ('git commit -m "unclosed', "turn:generator", True)]
        for command, agent, stopped in cases:
            with self.subTest(command=command, agent=agent):
                # When: each command is asked for
                reason = self.call("Bash", {"command": command}, agent=agent)
                # Then: every commit or push by an agent of turn is stopped, and the other two go through
                self.assertEqual(reason is not None and "commit or push" in reason, stopped)

    def test_the_first_user_is_never_handed_the_acceptance_criteria(self):
        # Given: the first user started with the acceptance in its prompt, the first user started without it, and the evaluator started with it
        cases = [({"subagent_type": "turn:first-user", "prompt": f"Use SETUP.md. {ACCEPTANCE}."}, True),
                 ({"subagent_type": "turn:first-user", "prompt": "Use SETUP.md as a new team member."}, False),
                 ({"subagent_type": "turn:evaluator", "prompt": ACCEPTANCE}, False)]
        for given, stopped in cases:
            with self.subTest(given=given):
                # When: each agent is started
                reason = self.call("Agent", given)
                # Then: only the first user given the acceptance is stopped
                self.assertEqual(reason is not None and "acceptance" in reason, stopped)

    def handback(self, agent, entries):
        """An agent handing back its report, with its record where Claude Code keeps it."""
        main = os.path.join(self.root, "projects", f"{self.session}.jsonl")
        record = os.path.join(self.root, "projects", self.session, "subagents", "agent-a1.jsonl")
        os.makedirs(os.path.dirname(record), exist_ok=True)
        with open(record, "w", encoding="utf-8") as f:
            f.write("".join(json.dumps(e) + "\n" for e in entries))
        data = {"session_id": self.session, "hook_event_name": "PreToolUse", "tool_name": "SubagentHandback",
                "tool_input": {"message": "done"}, "cwd": self.repo, "transcript_path": main,
                "agent_id": "a1", "agent_type": agent}
        result = subprocess.run([sys.executable, HOOK], input=json.dumps(data), capture_output=True, text=True)
        self.assertIn(result.returncode, (0, 2), result.stderr)
        return result.stderr.strip() if result.returncode == 2 else None

    def test_an_agent_handing_back_before_it_did_its_job_is_kept_running(self):
        # Given: the generator, the first user and an agent not of turn, each with an empty record
        cases = [("turn:generator", "should.md (not read)"), ("turn:first-user", None), ("Explore", None)]
        for agent, said in cases:
            with self.subTest(agent=agent):
                # When: each hands back its report
                reason = self.handback(agent, [])
                # Then: the generator is kept running, told it has not read should.md, and the other two go through
                if said is None:
                    self.assertIsNone(reason)
                else:
                    self.assertIn(said, reason)


if __name__ == "__main__":
    unittest.main()

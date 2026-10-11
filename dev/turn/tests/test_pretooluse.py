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
    "retrieved_artifacts": [{"viewpoint": "setup.md"}],
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
        for path, text in (("setup.md", "- Steps run as typed.\n"), (".t/in.json", json.dumps(CCS))):
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
        # Given
        given = {"command": "git commit -m x"}
        # When
        reason = self.call("Bash", given, agent="turn:generator", session=str(uuid.uuid4()))
        # Then
        self.assertIsNone(reason)

    def test_the_first_user_works_on_files_inside_its_copy_only(self):
        # Given
        cases = [("Read", {"file_path": os.path.join(self.copy, "setup.md")}, None),
                 ("Read", {"file_path": "setup.md"}, "outside"),
                 ("Grep", {"pattern": "x", "path": self.repo}, "outside"),
                 ("Glob", {"pattern": "*.md"}, "outside"),
                 ("Write", {"file_path": os.path.join(self.copy, "var/log"), "content": ""}, None),
                 ("Edit", {"file_path": os.path.join(self.copy, "SETUP.md")}, "the deliverable")]
        for tool, given, said in cases:
            with self.subTest(tool=tool, given=given):
                # When
                reason = self.call(tool, given, agent="turn:first-user")
                # Then
                if said is None:
                    self.assertIsNone(reason)
                else:
                    self.assertIn(said, reason)

    def test_the_first_user_runs_commands_inside_its_copy_only(self):
        # Given
        cases = [({"command": f"cd {self.copy} && npm start"}, self.repo, None),
                 ({"command": "npm start"}, self.copy, None),
                 ({"command": "npm start"}, self.repo, "cd into"),
                 ({"command": f"cat {self.repo}/setup.md"}, self.copy, "outside")]
        for given, cwd, said in cases:
            with self.subTest(given=given, cwd=cwd):
                # When
                reason = self.call("Bash", given, agent="turn:first-user", cwd=cwd)
                # Then
                if said is None:
                    self.assertIsNone(reason)
                else:
                    self.assertIn(said, reason)

    def test_the_generator_changes_nothing_in_the_repository_but_the_deliverable(self):
        # Given
        outside = os.path.join(self.root, "scratch", "try.sh")
        cases = [("Write", {"file_path": os.path.join(self.repo, "SETUP.md")}, None),
                 ("Edit", {"file_path": os.path.join(self.repo, "setup.md")}, "only the deliverable"),
                 ("Write", {"file_path": outside}, None),
                 ("Read", {"file_path": os.path.join(self.repo, "setup.md")}, None)]
        for tool, given, said in cases:
            with self.subTest(tool=tool, given=given):
                # When
                reason = self.call(tool, given, agent="turn:generator")
                # Then
                if said is None:
                    self.assertIsNone(reason)
                else:
                    self.assertIn(said, reason)

    def test_no_agent_of_turn_commits_or_pushes(self):
        # Given
        cases = [("git commit -m x", "turn:generator", True), ("git -C . push", "turn:evaluator", True),
                 ("npm test && git commit -am y", "turn:learner", True), ("git status", "turn:generator", False),
                 ("git commit -m x", "Explore", False)]
        for command, agent, stopped in cases:
            with self.subTest(command=command, agent=agent):
                # When
                reason = self.call("Bash", {"command": command}, agent=agent)
                # Then
                self.assertEqual(reason is not None and "commit or push" in reason, stopped)

    def test_the_first_user_is_never_handed_the_acceptance_criteria(self):
        # Given
        cases = [({"subagent_type": "turn:first-user", "prompt": f"Use SETUP.md. {ACCEPTANCE}."}, True),
                 ({"subagent_type": "turn:first-user", "prompt": "Use SETUP.md as a new team member."}, False),
                 ({"subagent_type": "turn:evaluator", "prompt": ACCEPTANCE}, False)]
        for given, stopped in cases:
            with self.subTest(given=given):
                # When
                reason = self.call("Agent", given)
                # Then
                self.assertEqual(reason is not None and "acceptance" in reason, stopped)


if __name__ == "__main__":
    unittest.main()

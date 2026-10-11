"""Tests for writing episodic_trace, run as turn runs it: the script, from inside the repository."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
ENTRY = os.path.join(PLUGIN_ROOT, "scripts", "trace.py")
SESSION = "11111111-2222-3333-4444-555555555555"


def tool(name, given):
    return {"type": "assistant", "message": {"content": [
        {"type": "text", "text": "working"}, {"type": "tool_use", "name": name, "input": given}]}}


class TraceTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.home = os.path.join(self.root, "home")
        self.repo = os.path.join(self.root, "repo")
        os.makedirs(self.repo)
        self.git("init", "-q")
        self.write(os.path.join(self.repo, "package.json"), "{}\n")
        self.git("add", "package.json")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "start")
        self.start = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, capture_output=True,
                                    text=True).stdout.strip()
        self.out = os.path.join(self.repo, ".setup", "task-2.json")
        self.write(self.out, json.dumps({"episodic_trace": [{"generator-1": "my own account"}],
                                         "predictive_cue": [{"next": "done"}]}))

    def tearDown(self):
        shutil.rmtree(self.root)

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True)

    def write(self, path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def agent(self, agent, entries):
        path = os.path.join(self.home, ".claude", "projects", "-repo", SESSION, "subagents",
                            f"agent-{agent}.jsonl")
        self.write(path, "".join(json.dumps(e) + "\n" for e in entries))

    def run_trace(self, *pairs):
        env = dict(os.environ, HOME=self.home)
        return subprocess.run([sys.executable, ENTRY, self.out, SESSION, self.start, *pairs],
                              cwd=self.repo, env=env, capture_output=True, text=True)

    def trace(self):
        with open(self.out, encoding="utf-8") as f:
            return json.load(f)["episodic_trace"]

    def test_each_round_gets_what_its_agent_read_wrote_and_ran_from_its_record(self):
        # Given: a generator's record that reads one file twice, searches, writes the deliverable and runs two commands, and a first user's record that reads the deliverable
        self.agent("a1", [
            {"type": "user", "message": {"content": "the task"}},
            tool("Read", {"file_path": "package.json"}),
            tool("Read", {"file_path": "package.json"}),
            tool("Grep", {"pattern": "start"}),
            tool("Write", {"file_path": "SETUP.md", "content": "# Setup"}),
            tool("Bash", {"command": "npm start\necho done"}),
            tool("Bash", {"command": "ls var"}),
        ])
        self.agent("a2", [tool("Read", {"file_path": "SETUP.md"})])
        # When: the records are written into the CCS to return
        result = self.run_trace("generator-1=a1", "first-user-1=a2")
        # Then: it prints nothing, the generator's line lists the file read once, the file written and both commands, and the first user's line lists the file read
        self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)
        trace = self.trace()
        self.assertEqual(trace[0], {"generator-1": "read: package.json; wrote: SETUP.md; ran: npm start | ls var"})
        self.assertEqual(trace[1], {"first-user-1": "read: SETUP.md"})

    def test_the_git_entry_says_what_changed_since_the_turn_started(self):
        # Given: a generator whose record has no tool call, and the deliverable left uncommitted in the repository
        self.agent("a1", [{"type": "user", "message": {"content": "the task"}}])
        self.write(os.path.join(self.repo, "SETUP.md"), "# Setup\n")
        # When: the records are written into the CCS to return
        result = self.run_trace("generator-1=a1")
        # Then: the generator's line says it used no tools, and the git line says no commits since the turn started and names what changed
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.trace(), [
            {"generator-1": "used no tools"},
            {"git": f"commits since {self.start[:7]}: 0; changed: .setup/, SETUP.md"}])

    def test_the_git_entry_names_a_changed_tracked_file_whole(self):
        # Given: a generator whose record has no tool call, and the file committed at the start changed but not staged
        self.agent("a1", [{"type": "user", "message": {"content": "the task"}}])
        self.write(os.path.join(self.repo, "package.json"), '{"name": "app"}\n')
        # When: the records are written into the CCS to return
        result = self.run_trace("generator-1=a1")
        # Then: the git line names the changed file with its whole path, before what is new
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.trace()[-1],
                         {"git": f"commits since {self.start[:7]}: 0; changed: package.json, .setup/"})

    def test_a_round_whose_record_is_missing_stops_and_leaves_the_ccs_as_it_was(self):
        # Given: a generator with a record and a first user with none
        self.agent("a1", [])
        # When: the records are written into the CCS to return
        result = self.run_trace("generator-1=a1", "first-user-1=gone")
        # Then: it fails, says whose record is missing, and leaves the CCS as it was
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.strip(), "no conversation record for first-user-1 (gone)")
        self.assertEqual(self.trace(), [{"generator-1": "my own account"}])

    def test_a_call_without_the_three_values_shows_how_to_call_it(self):
        # Given: a call with only the CCS to return, and one with an agent not given as round and record
        cases = [[sys.executable, ENTRY, self.out], [sys.executable, ENTRY, self.out, SESSION, self.start, "a1"]]
        for command in cases:
            with self.subTest(command=command[2:]):
                # When: each is made
                result = subprocess.run(command, cwd=self.repo, capture_output=True, text=True)
                # Then: each fails and shows how to call it
                self.assertEqual(result.returncode, 2)
                self.assertIn("trace.py <out> <session id>", result.stdout)


if __name__ == "__main__":
    unittest.main()

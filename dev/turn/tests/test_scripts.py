import os
import unittest

import harness

DONE = harness.RECORD + 'predictive_cue:\n  - next: "done"\n'


class Trace(unittest.TestCase):
    def setUp(self):
        self.repo = harness.Repo()

    def tearDown(self):
        self.repo.close()

    def test_what_each_agent_read_wrote_and_ran_is_written_from_the_records(self):
        # Given
        self.repo.write(".caller/1.yaml", harness.RECORD + 'episodic_trace:\n  - maker-1: "earlier"\n')
        self.repo.turn_up()
        self.repo.agent("maker", "m1", [("Read", {"file_path": os.path.join(self.repo.work, "app.py")}),
                                        ("Write", {"file_path": "SETUP.md"}), ("Grep", {})])
        self.repo.tool("SendMessage", {"to": "m1", "message": "go"})
        self.repo.agent("first-user", "u1", [("Bash", {"command": "./start.sh\necho"}), ("Bash", {})])
        self.repo.agent("learner", "l1")
        self.repo.tool("Agent", {"subagent_type": "turn:learner"})
        self.repo.write("SETUP.md", "x")
        self.repo.write(".caller/2.yaml", DONE + 'episodic_trace:\n  - x: "said by the conductor"\n')
        # When
        r = self.repo.script("trace.py", ".caller/1.yaml", ".caller/2.yaml")
        # Then
        self.assertEqual(r.returncode, 0, r.stderr)
        out = self.repo.read(".caller/2.yaml")
        self.assertIn('episodic_trace:\n  - maker-1: "earlier"\n  - maker-1: "read app.py"\n'
                      '  - maker-1: "wrote SETUP.md"\n  - first-user-1: "ran ./start.sh"\n'
                      '  - first-user-1: "ran "\n', out)
        self.assertIn('  - git: "changed SETUP.md"', out)
        self.assertNotIn("said by the conductor", out)
        self.assertEqual(self.repo.read(".caller/1.yaml").count("earlier"), 1)

    def test_a_turn_ending_done_without_a_use_is_stopped_and_nothing_written(self):
        # Given
        self.repo.turn_up()
        self.repo.agent("maker", "m1")
        self.repo.tool("SendMessage", {"to": "m1", "message": "go"})
        self.repo.write(".caller/2.yaml", DONE)
        # When
        r = self.repo.script("trace.py", ".caller/1.yaml", ".caller/2.yaml")
        # Then
        self.assertEqual(r.returncode, 2)
        self.assertIn("use what was made", r.stderr)
        self.assertEqual(self.repo.read(".caller/2.yaml"), DONE)

    def test_a_stopped_turn_returns_without_a_use(self):
        # Given: no turn:up found, and next is not done
        self.repo.add({"type": "user", "message": {"content": "hello"}})
        self.repo.write(".caller/2.yaml", harness.RECORD + 'predictive_cue:\n  - next: "use"\n')
        # When
        r = self.repo.script("trace.py", ".caller/1.yaml", ".caller/2.yaml")
        # Then
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("episodic_trace:", self.repo.read(".caller/2.yaml"))

    def test_a_wrong_call_or_an_unknown_conversation_is_refused(self):
        for args, env, want in (([], None, "usage"),
                                (["a", "b"], dict(self.repo.env(), CLAUDE_CODE_SESSION_ID=""), "not found")):
            with self.subTest(want=want):
                # Given / When
                r = self.repo.script("trace.py", *args, env=env)
                # Then
                self.assertEqual(r.returncode, 2)
                self.assertIn(want, r.stderr)


class Records(unittest.TestCase):
    def setUp(self):
        self.repo = harness.Repo()

    def tearDown(self):
        self.repo.close()

    def test_the_records_of_the_use_just_made_are_listed(self):
        # Given
        self.repo.turn_up()
        self.repo.agent("first-user", "u1")
        self.repo.agent("learner", "l1")
        self.repo.agent("maker", "m1")
        self.repo.tool("SendMessage", {"to": "m1", "message": "go"})
        self.repo.agent("first-user", "u2")
        # When
        r = self.repo.script("records.py")
        # Then
        lines = r.stdout.splitlines()
        self.assertEqual(lines[0], "conversation: " + self.repo.transcript)
        self.assertEqual([l.split(":")[0] for l in lines[1:]], ["maker", "first-user"])
        self.assertTrue(lines[2].endswith("agent-u2.jsonl"))

    def test_without_a_turn_only_the_conversation_is_listed(self):
        # Given
        self.repo.add({"type": "user", "message": {"content": "hello"}})
        # When
        r = self.repo.script("records.py")
        # Then
        self.assertEqual(r.stdout, "conversation: " + self.repo.transcript + "\n")

    def test_an_unknown_conversation_is_refused(self):
        # Given / When
        r = self.repo.script("records.py", env=dict(self.repo.env(), CLAUDE_CODE_SESSION_ID=""))
        # Then
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()

import unittest

import harness


class Hook(unittest.TestCase):
    def setUp(self):
        self.repo = harness.Repo()

    def tearDown(self):
        self.repo.close()

    def test_calls_outside_a_turn_or_not_to_turns_agents_pass(self):
        cases = [
            ("Agent", {"subagent_type": "turn:learner"}, {"agent_type": "turn:maker"}),
            ("Agent", {"subagent_type": "turn:learner"}, {"transcript_path": ""}),
            ("Agent", {"subagent_type": "general-purpose"}, {}),
            ("Agent", {"subagent_type": "turn:learner"}, {}),
        ]
        for tool, inp, extra in cases:
            with self.subTest(inp=inp, extra=extra):
                # Given: no turn:up in the conversation
                self.repo.add({"type": "user", "message": {"content": "hello"}})
                # When
                r = self.repo.hook(tool, inp, **extra)
                # Then
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_learner_before_any_use_is_stopped(self):
        # Given
        self.repo.turn_up()
        # When
        r = self.repo.hook("Agent", {"subagent_type": "turn:learner"})
        # Then
        self.assertEqual(r.returncode, 2)
        self.assertIn("nothing to learn", r.stderr)

    def test_a_maker_with_a_record_short_of_what_is_needed_is_stopped(self):
        # Given
        self.repo.write(".caller/1.yaml", "focal_entities:\n")
        self.repo.turn_up()
        # When
        r = self.repo.hook("Task", {"subagent_type": "turn:maker"})
        # Then
        self.assertEqual(r.returncode, 2)
        self.assertIn("focal_entities.work", r.stderr)

    def test_telling_a_maker_to_go_on_before_the_last_use_is_learned_is_stopped(self):
        # Given
        self.repo.turn_up()
        self.repo.agent("maker", "m1")
        self.repo.tool("SendMessage", {"to": "m1", "message": "go"})
        self.repo.agent("first-user", "u1")
        self.repo.agent("maker", "m2")
        # When
        r = self.repo.hook("SendMessage", {"to": "m2", "message": "go"})
        # Then
        self.assertEqual(r.returncode, 2)
        self.assertIn("learn from the last use", r.stderr)

    def test_a_message_to_another_agent_passes(self):
        # Given
        self.repo.turn_up()
        self.repo.agent("first-user", "u1")
        # When
        r = self.repo.hook("SendMessage", {"to": "someone", "message": "hi"})
        # Then
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_turn_typed_as_a_command_is_followed_from_its_arguments(self):
        # Given
        self.repo.add({"type": "user", "message": {"content": [{"type": "text", "text":
            "<command-name>/turn:up</command-name><command-args>" + harness.ARGS + "</command-args>"}]}})
        # When
        r = self.repo.hook("Agent", {"subagent_type": "turn:first-user"})
        # Then
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_turn_typed_as_a_command_without_arguments_is_sent_back(self):
        # Given
        self.repo.add({"type": "user", "message": {"content": "<command-name>/turn:up</command-name>"}})
        # When
        r = self.repo.hook("Agent", {"subagent_type": "turn:first-user"})
        # Then
        self.assertEqual(r.returncode, 2)
        self.assertIn("no record", r.stderr)


if __name__ == "__main__":
    unittest.main()

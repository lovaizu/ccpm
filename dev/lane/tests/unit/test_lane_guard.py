"""The guard's decision on a call: which call of a role goes on, and what each stop says."""

from __future__ import annotations

import unittest

from domain import guard
from lanetest import WRITER_LAID, bash

STOPPED = (
    "changelog: Run only `git log --oneline`.\n"
    "The commands you may run, each word for word: `git log --oneline`."
)
RELAY = "The maker of changelog must lay its proposal again with lay.py write."


class Goes(unittest.TestCase):
    def test_a_named_command_of_the_role_goes_on(self) -> None:
        self.assertIsNone(guard.decide(bash("git log --oneline"), WRITER_LAID, "changelog"))

    def test_a_call_of_the_main_conversation_goes_on(self) -> None:
        self.assertIsNone(guard.decide(bash("git commit", agent=None), WRITER_LAID, "changelog"))

    def test_a_call_of_a_role_of_another_plugin_goes_on(self) -> None:
        self.assertIsNone(
            guard.decide(bash("git commit", "other:writer"), WRITER_LAID, "changelog")
        )

    def test_a_call_of_a_role_with_no_rule_goes_on(self) -> None:
        self.assertIsNone(
            guard.decide(bash("git commit", "changelog:reviewer"), WRITER_LAID, "changelog")
        )

    def test_a_call_of_a_role_with_no_steps_goes_on(self) -> None:
        laid = {**WRITER_LAID, "subagents": {"writer": {"steps": []}}}
        self.assertIsNone(guard.decide(bash("git commit"), laid, "changelog"))

    def test_a_call_of_another_tool_goes_on(self) -> None:
        event = {**bash(""), "tool_name": "Read", "tool_input": {"file_path": "/repo/x"}}
        self.assertIsNone(guard.decide(event, WRITER_LAID, "changelog"))

    def test_the_main_conversation_goes_on_while_the_rules_cant_be_read(self) -> None:
        wrong = "isn't JSON"
        self.assertIsNone(guard.decide(bash("git commit", agent=None), wrong, "changelog"))


class Stops(unittest.TestCase):
    def test_another_command_of_the_role_stops_with_the_step_and_its_commands(self) -> None:
        self.assertEqual(guard.decide(bash("git commit -m x"), WRITER_LAID, "changelog"), STOPPED)

    def test_a_stop_names_the_first_steps_sentence_and_every_command(self) -> None:
        two = {"lane": "run_only", "takes": ["git diff"]}
        laid = {
            **WRITER_LAID,
            "subagents": {
                "writer": {
                    "steps": [
                        *WRITER_LAID["subagents"]["writer"]["steps"],
                        {"step": 3, "lanes": [two]},
                    ]
                }
            },
        }
        self.assertEqual(
            guard.decide(bash("git commit"), laid, "changelog"),
            "changelog: Run only `git log --oneline`.\n"
            "The commands you may run, each word for word: `git log --oneline`, `git diff`.",
        )


class CantCheck(unittest.TestCase):
    def test_an_event_that_isnt_an_object_stops(self) -> None:
        self.assertEqual(
            guard.decide([], WRITER_LAID, "changelog"),
            "changelog: Lane can't check this call, as Claude Code handed it no JSON object."
            " Run Claude Code 2.1.319 or later.",
        )

    def test_a_command_that_isnt_text_stops(self) -> None:
        self.assertEqual(
            guard.decide(bash(3), WRITER_LAID, "changelog"),
            "changelog: Lane can't check the call of writer, as its command isn't text."
            " Run Claude Code 2.1.319 or later.",
        )

    def test_a_call_of_a_role_stops_while_the_rules_cant_be_read(self) -> None:
        self.assertEqual(
            guard.decide(bash("git log --oneline"), "hooks/lanes.json isn't JSON", "changelog"),
            "changelog: Lane can't check the call of writer, as hooks/lanes.json isn't JSON. "
            + RELAY,
        )


if __name__ == "__main__":
    unittest.main()

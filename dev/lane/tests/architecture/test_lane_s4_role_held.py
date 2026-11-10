"""S2 and S4 joined: lay.py write lays the rules, and the hook entry it wrote, run as Claude Code
runs it, holds writer to its commands."""

from __future__ import annotations

import json
import subprocess

from lanetest import WRITER_RUN_ONLY, RepositoryTest, bash


class RoleHeld(RepositoryTest):
    def setUp(self) -> None:
        super().setUp()
        self.assertEqual(self.lay("write", self.propose(WRITER_RUN_ONLY)).returncode, 0)
        hooks = json.loads(self.read("changelog", "hooks", "hooks.json"))
        self.entry = hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    def call(self, event: object) -> str:
        """What the hook entry prints for the event, run by sh with the plugin's folder as
        CLAUDE_PLUGIN_ROOT, as Claude Code runs a plugin's hook."""
        env = {**self.env, "CLAUDE_PLUGIN_ROOT": self.path("changelog")}
        ran = subprocess.run(
            ["sh", "-c", self.entry],
            input=json.dumps(event),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(ran.returncode, 0, ran.stderr)
        return ran.stdout

    def test_a_named_command_goes_on(self) -> None:
        self.assertEqual(self.call(bash("git log --oneline")), "")

    def test_git_commit_stops_with_the_sentence_of_step_2(self) -> None:
        decision = json.loads(self.call(bash("git commit -m x")))["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertEqual(
            decision["permissionDecisionReason"],
            "changelog: Run only `git log --oneline`.\n"
            "The commands you may run, each word for word: `git log --oneline`.",
        )

    def test_a_call_the_guard_cant_check_stops(self) -> None:
        decision = json.loads(self.call(bash(3)))["hookSpecificOutput"]
        self.assertIn("Lane can't check the call of writer", decision["permissionDecisionReason"])

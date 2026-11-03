"""The hook's command `lay.py write` writes, run in `sh` as Claude Code runs it, on events in the
fields the hooks reference documents: its answer JSON, and, where Python cannot run, the shell's
own answer for a subagent with lanes."""

import json
import os
import subprocess
import unittest

import helpers
from helpers import entries, placed

# A stand-in for a python3 older than 3.9, or missing, which fails the command's check.
OLD_PYTHON = "#!/bin/sh\nexit 1\n"
INSTALL = "changelog: install Python 3.9 or later, run as python3, for its hooks to run"


class TestCommand(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay()
        placed.code_put(self.plugin)
        self.env = {**os.environ, "CLAUDE_PLUGIN_ROOT": self.plugin}

    def run_hook(self, event: dict, compact: bool = False) -> subprocess.CompletedProcess:
        """The hook's command run in sh on the event, as JSON with a blank after each colon, or
        none."""
        text = json.dumps(event, separators=(",", ":") if compact else None)
        command = entries.command("changelog", ["writer"])
        return subprocess.run(
            ["sh", "-c", command],
            input=text,
            capture_output=True,
            text=True,
            env=self.env,
            check=False,
        )

    def test_a_break_is_denied_with_the_sentence(self):
        # Given: writer with the README's lanes laid and lane's code put in
        # When: writer's git commit reaches the hook's command
        done = self.run_hook(self.bash("git commit -m m"))
        # Then: it exits 0 printing the denial with run_only's sentence
        self.assertEqual(done.returncode, 0)
        output = json.loads(done.stdout)["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertTrue(
            output["permissionDecisionReason"].startswith(f"changelog: {helpers.RUN}\n")
        )

    def test_calls_the_lanes_allow_and_calls_of_no_subagent_print_nothing(self):
        for event in (
            self.bash("git log --oneline"),
            self.written(os.path.join(self.base, "CHANGELOG.md")),
            self.bash("git commit", None),
        ):
            with self.subTest(event=event):
                # Given: writer's git log --oneline, its write of CHANGELOG.md, or the main
                # conversation's git commit
                # When: it reaches the hook's command
                done = self.run_hook(event)
                # Then: it exits 0 printing nothing, so the call goes on
                self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""))

    def test_without_python_a_subagent_with_lanes_is_denied_and_others_go_on(self):
        folder = os.path.join(self.base, "bin")
        self.write(os.path.join(folder, "python3"), OLD_PYTHON)
        os.chmod(os.path.join(folder, "python3"), 0o755)
        self.env["PATH"] = folder + os.pathsep + self.env["PATH"]
        for event, compact, denied in (
            (self.bash("git log --oneline"), False, True),
            (self.bash("git log --oneline"), True, True),
            (self.bash("ls", "changelog:reviewer"), False, False),
            (self.bash("ls", None), False, False),
        ):
            with self.subTest(event=event, compact=compact):
                # Given: python3 that fails the command's check
                # When: a call of writer, written with blanks or without, of reviewer, or of the
                # main conversation, reaches the hook's command
                done = self.run_hook(event, compact)
                # Then: writer's is denied, telling it and the user to install Python, and the
                # others print nothing
                self.assertEqual(done.returncode, 0)
                found = json.loads(done.stdout) if denied else {}
                if denied:
                    self.assertEqual(found["systemMessage"], INSTALL)
                    self.assertEqual(
                        found["hookSpecificOutput"]["permissionDecisionReason"], INSTALL
                    )
                else:
                    self.assertEqual(done.stdout, "")


if __name__ == "__main__":
    unittest.main()

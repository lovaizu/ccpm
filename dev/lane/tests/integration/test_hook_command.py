"""The hooks' commands `lay.py write` writes, run in `sh` as Claude Code runs them, on events in
the fields the hooks reference documents: their answer JSON, the calls kept in the system's
temporary folder from one event to the next, and, where Python cannot run, the shell's own answer
for a subagent with lanes; and the result script run as a step writes it."""

import json
import os
import subprocess
import unittest

import helpers
from helpers import entries, placed

# A stand-in for a python3 older than 3.9, or missing, which fails the command's check.
OLD_PYTHON = "#!/bin/sh\nexit 1\n"
INSTALL = "changelog: install Python 3.9 or later, run as python3, for its hooks to run"


class CommandTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.lay()
        placed.code_put(self.plugin)
        self.env = {**os.environ, "CLAUDE_PLUGIN_ROOT": self.plugin}

    def run_hook(
        self, event: dict, compact: bool = False, held: str = "PreToolUse"
    ) -> subprocess.CompletedProcess:
        """The command of the hook of the event held, PreToolUse by default, run in sh on the
        event, as JSON with a blank after each colon, or none."""
        text = json.dumps(event, separators=(",", ":") if compact else None)
        command = entries.command("changelog", ["writer"], held)
        return subprocess.run(
            ["sh", "-c", command],
            input=text,
            capture_output=True,
            text=True,
            env=self.env,
            check=False,
        )


class TestCommand(CommandTest):
    def test_a_break_is_denied_with_the_sentence(self):
        # Given: writer with the README's lanes laid and lane's code put in
        # When: writer's git commit reaches the hook's command
        done = self.run_hook(self.bash("git commit -m m"))
        # Then: it exits 0 printing the denial with run_only's sentence, writing no compiled
        # file into the plugin
        self.assertEqual(done.returncode, 0)
        found = [d for _, ds, _ in os.walk(self.plugin) for d in ds if d == "__pycache__"]
        self.assertEqual(found, [])
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

    def test_without_python_every_other_event_goes_on(self):
        folder = os.path.join(self.base, "bin")
        self.write(os.path.join(folder, "python3"), OLD_PYTHON)
        os.chmod(os.path.join(folder, "python3"), 0o755)
        self.env["PATH"] = folder + os.pathsep + self.env["PATH"]
        for held in ("PostToolUse", "PostToolUseFailure", "SubagentStart", "SubagentStop"):
            with self.subTest(held=held):
                # Given: python3 that fails the command's check
                # When: writer's event reaches the event's command
                done = self.run_hook(self.subagent(held, "writer", "a1"), held=held)
                # Then: it exits 0 printing nothing, as PreToolUse's stops each call meanwhile
                self.assertEqual((done.returncode, done.stdout), (0, ""))


class TestRoutesCommands(CommandTest):
    def setUp(self) -> None:
        super().setUp()
        self.route()
        self.env["TMPDIR"] = self.base
        self.gives = f"python3 {self.plugin}/hooks/lane/result.py writer"

    def told(self, event: dict, held: str) -> dict:
        """What the hook of the event says of it, run in sh."""
        done = self.run_hook(event, held=held)
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        return json.loads(done.stdout) if done.stdout else {}

    def test_a_run_of_writer_tells_lead_reviewer_next_from_event_to_event(self):
        # Given: the routes laid
        # When: lead starts, and starts reviewer
        started = self.told(self.subagent("SubagentStart", "lead", "lead1"), "SubagentStart")
        stopped = self.told(self.start("reviewer"), "PreToolUse")
        # Then: it is told to start writer, and the start of reviewer is denied
        context = started["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(context, "changelog: Start `changelog:writer`.")
        self.assertEqual(stopped["hookSpecificOutput"]["permissionDecision"], "deny")
        # When: lead starts writer, which gives `written` and ends, and the start comes back
        self.assertEqual(self.told(self.start("writer"), "PreToolUse"), {})
        self.told(self.subagent("SubagentStart", "writer", "w1"), "SubagentStart")
        gave = self.came_back(f"{self.gives} written", agent_id="w1")
        self.assertEqual(self.told(gave, "PostToolUse"), {})
        self.assertEqual(
            self.told(self.subagent("SubagentStop", "writer", "w1"), "SubagentStop"), {}
        )
        back = self.told(self.start("writer", "PostToolUse", helpers.back("w1")), "PostToolUse")
        # Then: lead is told reviewer next
        self.assertEqual(
            back["hookSpecificOutput"]["additionalContext"],
            "changelog: writer gave `written`. Start `changelog:reviewer`.",
        )

    def test_the_result_script_run_as_the_step_writes_it_exits_by_the_routes(self):
        for on, code in (("written", 0), ("good", 1)):
            with self.subTest(on=on):
                # Given: the routes laid and lane's code put in
                # When: writer runs its result command in sh, or one of a result no route is on
                done = subprocess.run(
                    ["sh", "-c", f"{self.gives} {on}"],
                    capture_output=True,
                    text=True,
                    env=self.env,
                    check=False,
                )
                # Then: it exits 0 saying nothing, or 1 saying what it may end by, writing no
                # compiled file into the plugin
                self.assertEqual(done.returncode, code)
                self.assertEqual(done.stdout, "")
                self.assertEqual(bool(done.stderr), bool(code))
                found = [d for _, ds, _ in os.walk(self.plugin) for d in ds if d == "__pycache__"]
                self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()

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


class TestLanesCommands(CommandTest):
    def setUp(self) -> None:
        super().setUp()
        self.env["TMPDIR"] = self.base

    def test_a_held_command_is_asked_and_a_result_with_work_missing_is_denied(self):
        # Given: writer holding git push, and ending once report.md is made
        self.lay_lanes(
            [
                {"step": 2, "lanes": [{"lane": "hold", "takes": ["git push"]}]},
                {"step": 3, "lanes": [{"lane": "end_when", "takes": ["report.md"]}]},
            ]
        )
        # When: its git push, and its result command, reach the hook's command in sh
        held = self.run_hook(self.bash("git push"))
        ended = self.run_hook(self.bash(f"python3 {self.plugin}/hooks/lane/result.py writer done"))
        # Then: the push is asked of the person, and the result denied naming what is missing
        asked = json.loads(held.stdout)["hookSpecificOutput"]
        self.assertEqual(asked["permissionDecision"], "ask")
        self.assertEqual(
            json.loads(ended.stdout)["hookSpecificOutput"]["permissionDecisionReason"],
            "changelog: End only once `report.md` is made.\n`report.md` not there",
        )
        # And: once report.md is made, the result script run as the step writes it exits 0
        self.write("report.md", "x")
        self.assertEqual(
            self.run_hook(
                self.bash(f"python3 {self.plugin}/hooks/lane/result.py writer done")
            ).stdout,
            "",
        )
        done = subprocess.run(
            ["sh", "-c", f"python3 {self.plugin}/hooks/lane/result.py writer done"],
            capture_output=True,
            text=True,
            env=self.env,
            check=False,
        )
        self.assertEqual((done.returncode, done.stderr), (0, ""))

    def test_a_value_given_in_the_main_conversations_prompt_holds_writer_from_event_to_event(self):
        # Given: writer writing only {work}
        self.lay_lanes([{"step": 3, "lanes": [{"lane": "write_only", "takes": ["{work}"]}]}])
        call = {
            **self.event(
                "Agent", {"prompt": '{"work": "a.md"}', "subagent_type": "changelog:writer"}, None
            ),
            "tool_use_id": "t1",
        }
        back = {
            **call,
            "hook_event_name": "PostToolUse",
            "tool_response": helpers.back("a1", "async_launched"),
        }
        # When: the main conversation starts writer with a.md as its work, the start coming back
        # launched in the background as writer starts, and writer writes a.md and b.md, each event
        # through the hooks' commands in sh
        self.assertEqual(self.run_hook(call).stdout, "")
        self.run_hook(self.subagent("SubagentStart", "writer", "a1"), held="SubagentStart")
        self.assertEqual(self.run_hook(back, held="PostToolUse").stdout, "")
        wrote_a = self.run_hook(self.written("a.md"))
        wrote_b = self.run_hook(self.written("b.md"))
        # Then: a.md goes through, and b.md is denied with the sentence as the step says it
        self.assertEqual(wrote_a.stdout, "")
        reason = json.loads(wrote_b.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertEqual(reason, "changelog: Write only `{work}`.")

    def test_a_command_of_a_dependencys_skill_is_held_to_its_folder_from_event_to_event(self):
        # Given: writer running only checker's command, checker declared in the plugin's manifest
        # and installed in a folder of its own
        manifest = {"name": "changelog", "version": "0.1.0", "dependencies": ["checker"]}
        self.write_json(self.manifest(), manifest)
        installed = os.path.join(self.base, "cache", "checker", "1.0.0")
        self.write_json(
            os.path.join(installed, ".claude-plugin", "plugin.json"), {"name": "checker"}
        )
        take = "python3 ${dependency:checker}/scripts/check.py CHANGELOG.md"
        self.lay_lanes([{"step": 2, "lanes": [{"lane": "run_only", "takes": [take]}]}])
        # When: writer runs it by that folder, and by a copy with no manifest, through the hook's
        # command in sh
        ran = self.run_hook(self.bash(f"python3 {installed}/scripts/check.py CHANGELOG.md"))
        copy = self.run_hook(self.bash(f"python3 {self.base}/copy/scripts/check.py CHANGELOG.md"))
        # Then: the first goes through, and the copy is denied with the sentence
        self.assertEqual(ran.stdout, "")
        reason = json.loads(copy.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertTrue(reason.startswith(f"changelog: Run only `{take}`."), reason)


if __name__ == "__main__":
    unittest.main()

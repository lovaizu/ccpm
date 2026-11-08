"""The cases of entries.py's contract: the hook entries that run the guard on each event, merged
with the plugin's own entries."""

import json
import os
import subprocess

from helpers import entries, testing

HELD = ("changelog:writer",)
# Each event that the guard reads, as the architecture's sequences draw them.
EVENTS = (
    "PreToolUse PostToolUse SubagentStart SubagentStop UserPromptExpansion UserPromptSubmit Stop"
)
OWN = {"type": "command", "command": "echo own"}


def commands(hooks, event):
    return [h["command"] for g in hooks["hooks"][event] for h in g["hooks"]]


class TestLaid(testing.FolderTest):
    def test_each_event_the_guard_reads_has_an_entry(self):
        self.assertEqual(list(entries.laid("changelog", HELD)["hooks"]), EVENTS.split())

    def test_each_entry_runs_the_guard_with_the_plugins_name(self):
        command = commands(entries.laid("changelog", HELD), "Stop")[0]
        self.assertTrue(
            command.endswith('exec python3 -B "${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py" changelog')
        )

    def test_each_tool_and_subagent_entry_matches_every_tool_and_type(self):
        hooks = entries.laid("changelog", HELD)["hooks"]
        self.assertEqual(
            [hooks[e][0].get("matcher") for e in EVENTS.split()],
            ["*", "*", "*", "*", None, None, None],
        )

    def test_a_pre_tool_use_entry_that_fails_blocks_the_call(self):
        hook = entries.laid("changelog", HELD)["hooks"]["PreToolUse"][0]["hooks"][0]
        self.assertEqual(hook["onFailure"], "block")


class TestWithoutPython(testing.FolderTest):
    def run_entry(self, event, given):
        """Runs the entry of the event in sh where python3 fails, as where Python 3.9 is missing."""
        os.makedirs("bin")
        self.write("bin/python3", "#!/bin/sh\nexit 1\n")
        os.chmod("bin/python3", 0o755)
        command = commands(entries.laid("changelog", HELD), event)[0]
        env = {"PATH": f"{self.base}/bin:/usr/bin:/bin"}
        return subprocess.run(
            ["sh", "-c", command],
            input=json.dumps(given),
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

    def test_a_call_of_a_held_role_is_denied_with_what_to_install(self):
        done = self.run_entry("PreToolUse", {"agent_type": "changelog:writer"})
        told = "changelog: install Python 3.9 or later, run as python3, for its hooks to run"
        said = json.loads(done.stdout)
        decision = said["hookSpecificOutput"]
        self.assertEqual(
            (
                said["systemMessage"],
                decision["permissionDecision"],
                decision["permissionDecisionReason"],
            ),
            (told, "deny", told),
        )

    def test_a_call_of_another_role_goes_on(self):
        done = self.run_entry("PreToolUse", {"agent_type": "changelog:reviewer"})
        self.assertEqual((done.stdout, done.returncode), ("", 0))

    def test_another_event_goes_on(self):
        done = self.run_entry("Stop", {"agent_type": "changelog:writer"})
        self.assertEqual((done.stdout, done.returncode), ("", 0))


class TestMerged(testing.FolderTest):
    def test_the_plugins_own_entries_are_kept_beside_lanes(self):
        own = {"hooks": {"Stop": [{"hooks": [OWN]}], "Notification": [{"hooks": [OWN]}]}}
        found = entries.merged(own, "changelog", HELD)
        self.assertEqual(
            (commands(found, "Stop")[0], commands(found, "Notification")),
            ("echo own", ["echo own"]),
        )

    def test_lanes_entries_laid_before_are_replaced(self):
        old = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/stop.py"'
                                " changelog",
                            }
                        ]
                    }
                ]
            }
        }
        found = entries.merged(old, "changelog", HELD)
        self.assertEqual(found, entries.laid("changelog", HELD))

    def test_no_entries_before_gives_lanes_alone(self):
        self.assertEqual(entries.merged(None, "changelog", HELD), entries.laid("changelog", HELD))


class TestCurrent(testing.FolderTest):
    def test_entries_as_lane_lays_them_now_are_current(self):
        laid = entries.merged({"hooks": {"Stop": [{"hooks": [OWN]}]}}, "changelog", HELD)
        self.assertTrue(entries.current(laid, "changelog", HELD))

    def test_entries_in_another_form_are_not_current(self):
        old = {
            "hooks": {
                "Stop": [{"hooks": [{"type": "command", "command": "x /hooks/lane/stop.py"}]}]
            }
        }
        self.assertFalse(entries.current(old, "changelog", HELD))

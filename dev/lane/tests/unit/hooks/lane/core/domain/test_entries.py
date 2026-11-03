"""lane's entry in a plugin's hooks/hooks.json: one PreToolUse entry for the plugin, run on every
tool call, its command checking for Python first, every other entry left as it was."""

import os
import unittest

import helpers
from helpers import entries, proposal

# An entry of the plugin's own, which lane leaves as it is.
OWN = {"matcher": "Bash", "hooks": [{"type": "command", "command": "sh own.sh"}]}
# lane's entries of the old shape, one for each subagent and event.
RUNS = 'exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/'
OLD = {"matcher": "Bash", "hooks": [{"type": "command", "command": RUNS + 'pretooluse.py" a:b'}]}
OLD_STOP = {
    "matcher": "a:b",
    "hooks": [{"type": "command", "command": RUNS + 'subagentstop.py" a:b'}],
}


class TestEntry(unittest.TestCase):
    def test_the_entry_runs_lanes_code_on_every_call_naming_the_plugin(self):
        # Given: changelog with lanes laid in writer
        # When: its entry is made
        # Then: it matches every tool, gives the plugin's name, and blocks the call where the
        # hook fails
        self.assertEqual(entries.entry("changelog", ["writer"]), helpers.ENTRY)

    def test_without_python_each_subagent_with_lanes_is_matched_in_the_event(self):
        # Given: changelog with lanes laid in writer and reviewer
        # When: its command is made
        command = entries.command("changelog", ["writer", "reviewer"])
        # Then: the event's agent_type is looked for as either subagent, with a blank after the
        # colon or none
        self.assertIn(
            """*'"agent_type":"changelog:writer"'*|*'"agent_type": "changelog:writer"'*"""
            """|*'"agent_type":"changelog:reviewer"'*|*'"agent_type": "changelog:reviewer"'*)""",
            command,
        )


class TestPut(unittest.TestCase):
    def test_the_entry_is_put_into_hooks_with_none(self):
        # Given: no hooks
        # When: changelog's entry is put in
        # Then: it is PreToolUse's one entry
        self.assertEqual(
            entries.put({"hooks": {}}, "changelog", ["writer"]),
            {"hooks": {"PreToolUse": [helpers.ENTRY]}},
        )

    def test_lanes_old_entries_give_way_to_the_one_at_the_place_of_the_first(self):
        # Given: the plugin's entry between two of lane's old shape, and one at SubagentStop
        hooks = {
            "hooks": {"PreToolUse": [OLD, OWN, OLD], "SubagentStop": [OLD_STOP], "Stop": [OWN]}
        }
        # When: changelog's entry is put in
        # Then: it is in the first one's place, the others of lane's gone, SubagentStop, which
        # held lane's alone, left out, and the plugin's own as they were
        self.assertEqual(
            entries.put(hooks, "changelog", ["writer"]),
            {"hooks": {"PreToolUse": [helpers.ENTRY, OWN], "Stop": [OWN]}},
        )

    def test_with_no_subagent_laid_lanes_entry_is_taken_out(self):
        # Given: lane's entry beside the plugin's own
        hooks = {"hooks": {"PreToolUse": [OWN, helpers.ENTRY]}}
        # When: the entry is put in for no subagent
        # Then: lane's is gone, the plugin's own kept
        self.assertEqual(entries.put(hooks, "changelog", []), {"hooks": {"PreToolUse": [OWN]}})


class TestRead(helpers.PluginTest):
    def path(self) -> str:
        """The plugin's hooks.json."""
        return os.path.join(self.plugin, "hooks", "hooks.json")

    def test_hooks_are_read_and_written_back_as_they_are(self):
        # Given: no hooks.json
        # When: it is read, and the entry written into it
        # Then: it is read as empty, and back as written, indented by two
        self.assertEqual(entries.read(self.plugin), {"hooks": {}})
        entries.written(self.plugin, {"hooks": {"PreToolUse": [helpers.ENTRY]}})
        self.assertEqual(entries.read(self.plugin), {"hooks": {"PreToolUse": [helpers.ENTRY]}})
        self.assertTrue(self.read(self.path()).startswith('{\n  "hooks": {\n'))

    def test_hooks_not_in_claude_codes_shape_are_refused(self):
        for text in (
            "{",
            "[]",
            '{"hooks": []}',
            '{"hooks": {"PreToolUse": {}}}',
            '{"hooks": {"Stop": [1]}}',
            '{"hooks": {"Stop": [{"hooks": [1]}]}}',
        ):
            with self.subTest(text=text):
                # Given: hooks.json of no JSON, no object, no object of events, an event of no
                # list, an entry of no object, or a hook of no object
                self.write(self.path(), text)
                # When: it is read
                with self.assertRaises(proposal.Stop) as stop:
                    entries.read(self.plugin)
                # Then: it is refused, naming it
                self.assertEqual(
                    str(stop.exception),
                    f"lay.py: {self.path()} is not in the shape Claude Code reads; fix it and run"
                    " again.",
                )


if __name__ == "__main__":
    unittest.main()

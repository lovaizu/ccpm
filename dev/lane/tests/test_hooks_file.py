"""The hook commands lane:up writes in a plugin's hooks/hooks.json and the file read: each lane laid
written for the command and read back from it, the words a command gives its event's script, and
what each lane of a kind takes in a subagent, read from the file."""

import json
import os
import unittest

import helpers
from helpers import hooks_file


class TestTaken(helpers.PluginTest):
    # A hook's command laying start_with on step 1 and hands_off on step 3 of the subagent.
    COMMAND = (
        'exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py" notes:changelog-writer'
        " '1:start_with:python3 scripts/given.py' 3:hands_off:git"
    )

    def taken(self, hooks, lane="start_with"):
        """What each lane of the kind takes in changelog-writer, read from the hooks written."""
        if hooks is not None:
            self.write(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        return hooks_file.taken(self.plugin, helpers.AGENT, lane)

    def entry(self, command):
        return {"matcher": ".*", "hooks": [{"type": "command", "command": command}]}

    def test_what_each_lane_of_the_kind_takes_in_the_subagent_is_read_from_its_hooks(self):
        # Given: the subagent's hook laying start_with and hands_off, beside the hooks of
        # other subagents, and one lane does not read
        others = [self.COMMAND.replace("changelog-writer", n) for n in ("a", "z")]
        wrong = self.COMMAND.replace("3:hands_off:git", "3:no_lane:git")
        entries = [self.entry(c) for c in (*others, wrong, self.COMMAND)]
        hooks = json.dumps({"hooks": {"PreToolUse": entries}})
        for lane, takes in (
            ("start_with", [["python3 scripts/given.py"]]),
            ("hands_off", [["git"]]),
        ):
            with self.subTest(lane=lane):
                # When: what its lanes of the kind take is read
                # Then: it is what its lane of the kind takes in the hook lane reads, once
                self.assertEqual(self.taken(hooks, lane), takes)

    def test_hooks_not_there_or_not_json_give_none(self):
        for hooks in (None, "{", "[]"):
            with self.subTest(hooks=hooks):
                # Given: no hooks.json, one not JSON, or one holding no hook
                # When: what start_with takes is read
                # Then: there is nothing
                self.assertEqual(self.taken(hooks), [])


class TestWords(unittest.TestCase):
    COMMAND = (
        'check || exit 2; exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py"'
        " notes:changelog-writer '3:hands_off:git commit,git push'"
    )

    def test_the_words_a_hooks_command_gives_its_event_script_are_read(self):
        # Given: a hook's command as lane:up writes it
        # When: its words for PreToolUse are read
        # Then: they are the subagent, then each lane laid
        self.assertEqual(
            hooks_file.words(self.COMMAND, "PreToolUse"),
            ["notes:changelog-writer", "3:hands_off:git commit,git push"],
        )

    def test_a_command_of_another_event_no_subagent_or_unread_words_gives_none(self):
        for command, event in (
            (self.COMMAND, "SubagentStop"),
            (self.COMMAND.replace("notes:changelog-writer", "writer"), "PreToolUse"),
            (self.COMMAND + " 'open", "PreToolUse"),
            (None, "PreToolUse"),
        ):
            with self.subTest(command=command, event=event):
                # Given: a command running another event's script, naming no subagent as
                # <plugin>:<name>, giving words the shell cannot read, or none at all
                # When: its words are read
                # Then: there are none
                self.assertEqual(hooks_file.words(command, event), [])


class TestWord(unittest.TestCase):
    def test_a_lane_is_written_as_its_step_its_name_and_what_it_takes(self):
        # Given: hands_off on step 3 taking two commands
        # When: it is written for the hook's command
        # Then: it reads `<step>:<lane>:<what it takes>`, the things taken joined by commas
        self.assertEqual(
            hooks_file.word(3, "hands_off", ["git commit", "git push"]),
            "3:hands_off:git commit,git push",
        )


if __name__ == "__main__":
    unittest.main()

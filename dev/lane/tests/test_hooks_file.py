"""The hook commands `lay.py write` writes in a plugin's hooks/hooks.json and the file read, and the
lanes laid read from its hooks/lanes.json: the words a command gives its event's script, the lanes
laid in a subagent, and what each lane of a kind takes in it."""

from __future__ import annotations

import json
import os
import unittest

import helpers
from helpers import hooks_file

# hooks/lanes.json laying start_with on step 1 and hands_off on step 3 of changelog-writer, and
# hands_off on step 2 of a subagent named before it in order and one after.
LAID = {
    "subagents": [
        {
            "name": "a-first",
            "steps": [{"step": 2, "lanes": [{"lane": "hands_off", "takes": ["git"]}]}],
        },
        {
            "name": "other",
            "steps": [{"step": 2, "lanes": [{"lane": "hands_off", "takes": ["git"]}]}],
        },
        {
            "name": "changelog-writer",
            "steps": [
                {"step": 1, "lanes": [{"lane": "start_with", "takes": ["scripts/given.py"]}]},
                {"step": 3, "lanes": [{"lane": "hands_off", "takes": ["git commit, -a", "x"]}]},
            ],
        },
    ]
}


class LanesTest(helpers.PluginTest):
    def lanes(self, text: str | None) -> None:
        """Writes the text as the plugin's hooks/lanes.json, or none where it is None."""
        if text is not None:
            self.write(os.path.join(self.plugin, "hooks", "lanes.json"), text)


class TestLaidIn(LanesTest):
    def test_the_lanes_of_the_subagent_are_read_each_take_as_written(self):
        # Given: hooks/lanes.json laying lanes in changelog-writer and another subagent, a thing
        # taken holding a comma
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), LAID)
        # When: the lanes laid in changelog-writer are read
        # Then: they are its own, each its step, the lane and what it takes, the comma kept
        self.assertEqual(
            hooks_file.laid_in(self.plugin, "changelog-writer"),
            [
                (1, "start_with", ["scripts/given.py"], None),
                (3, "hands_off", ["git commit, -a", "x"], None),
            ],
        )

    def test_the_adapters_named_are_read(self):
        # Given: hooks/lanes.json naming the values adapter of changelog-writer and the items
        # adapter of its every_item
        lane = {"lane": "every_item", "takes": ["r.md"], "adapter": "hooks/adapters/items-h.py"}
        steps = [{"step": 3, "lanes": [lane]}]
        agent = {
            "name": "changelog-writer",
            "adapter": "hooks/adapters/values-w.py",
            "steps": steps,
        }
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), {"subagents": [agent]})
        # When: the lanes laid in it are read
        # Then: each lane gives its adapter, and the subagent its own
        self.assertEqual(
            hooks_file.laid_in(self.plugin, "changelog-writer"),
            [(3, "every_item", ["r.md"], "hooks/adapters/items-h.py")],
        )
        self.assertEqual(hooks_file.subagent(self.plugin, "changelog-writer"), agent)

    def test_lanes_json_not_as_lay_py_write_writes_it_stops_saying_what_is_wrong(self):
        lane = {"lane": "hands_off", "takes": ["git"]}

        def laying(*lanes: object, name: str = "changelog-writer") -> str:
            steps = [{"step": 3, "lanes": list(lanes)}]
            return json.dumps({"subagents": [{"name": name, "steps": steps}]})

        for what, text, named in (
            ("not there", None, "hooks/lanes.json is not there"),
            ("no JSON", "{", "hooks/lanes.json holds no JSON"),
            ("no subagents", "{}", '$: expected the key "subagents"'),
            ("a key beside them", '{"subagents": [], "x": 1}', 'found the key "x"'),
            (
                "a key beside a subagent's",
                '{"subagents": [{"name": "a", "steps": [], "x": 1}]}',
                "$.subagents[0]: expected only",
            ),
            (
                "a key beside a step's",
                '{"subagents": [{"name": "a", "steps": [{"step": 1, "lanes": [], "x": 1}]}]}',
                "$.subagents[0].steps[0]: expected only",
            ),
            ("a key beside a lane's", laying({**lane, "x": 1}), ".lanes[0]: expected only"),
            ("a lane lane has not", laying({"lane": "x", "takes": ["a"]}), "$.subagents[0]"),
            ("takes that are no list", laying({"lane": "hands_off", "takes": "a"}), "takes"),
            ("a thing taken empty", laying({"lane": "hands_off", "takes": [""]}), "hands_off on"),
            ("takes too few", laying({"lane": "in_form", "takes": ["a.json"]}), "in_form on"),
            ("no lanes in it", laying(lane, name="other"), "lays no lanes in changelog-writer"),
            (
                "an adapter of a lane reading no port",
                laying({**lane, "adapter": "hooks/adapters/items-x.py"}),
                "names an adapter for hands_off on step 3 of changelog-writer `hooks/adapters/",
            ),
            (
                "an adapter of another port",
                laying({"lane": "every_item", "takes": ["r.md"], "adapter": "x/move-x.py"}),
                "`x/move-x.py`, not hooks/adapters/items-<name>.py",
            ),
            (
                "a values adapter of another port",
                json.dumps(
                    {
                        "subagents": [
                            {"name": "a", "adapter": "hooks/adapters/items-x.py", "steps": []}
                        ]
                    }
                ),
                "names an adapter for a `hooks/adapters/items-x.py`, not hooks/adapters/values-",
            ),
        ):
            with self.subTest(what=what):
                # Given: hooks/lanes.json in another shape, or laying no lanes in the subagent
                os.makedirs(os.path.join(self.plugin, "hooks"), exist_ok=True)
                path = os.path.join(self.plugin, "hooks", "lanes.json")
                if os.path.exists(path):
                    os.remove(path)
                self.lanes(text)
                # When: the lanes laid in changelog-writer are read
                # Then: it stops, saying what is wrong
                with self.assertRaises(ValueError) as stop:
                    hooks_file.laid_in(self.plugin, "changelog-writer")
                self.assertIn(named, str(stop.exception))


class TestTaken(LanesTest):
    def test_what_each_lane_of_the_kind_takes_in_the_subagent_is_read_from_its_lanes(self):
        # Given: hooks/lanes.json laying start_with and hands_off in changelog-writer
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), LAID)
        for lane, takes in (
            ("start_with", [["scripts/given.py"]]),
            ("hands_off", [["git commit, -a", "x"]]),
        ):
            with self.subTest(lane=lane):
                # When: what its lanes of the kind take is read
                # Then: it is what its lane of the kind takes
                self.assertEqual(hooks_file.taken(self.plugin, "changelog-writer", lane), takes)

    def test_lanes_json_not_there_or_not_json_give_none(self):
        for text in (None, "{"):
            with self.subTest(text=text):
                # Given: no hooks/lanes.json, or one holding no JSON
                self.lanes(text)
                # When: what start_with takes is read
                # Then: there is nothing
                self.assertEqual(
                    hooks_file.taken(self.plugin, "changelog-writer", "start_with"), []
                )


class TestWords(unittest.TestCase):
    COMMAND = hooks_file.command("notes", helpers.AGENT, "PreToolUse")
    # A hook's command as an older lane wrote it, giving each lane laid after the subagent.
    OLDER = (
        'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py" notes:changelog-writer'
        " '3:hands_off:git commit,git push'"
    )

    def test_the_words_a_hooks_command_gives_its_event_script_are_read(self):
        for command, words in (
            (self.COMMAND, ["notes:changelog-writer"]),
            (self.OLDER, ["notes:changelog-writer", "3:hands_off:git commit,git push"]),
        ):
            with self.subTest(command=command):
                # Given: a hook's command as `lay.py write` writes it, or as an older lane wrote it
                # When: its words for PreToolUse are read
                # Then: they are the subagent, then each lane an older lane gave
                self.assertEqual(hooks_file.words(command, "PreToolUse"), words)

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


if __name__ == "__main__":
    unittest.main()

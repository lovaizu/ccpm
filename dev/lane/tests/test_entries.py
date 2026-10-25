"""The entries the layer writes in the plugin's hooks.json: one for each subagent and each event its
lanes are held on, matching the tools they watch, every other entry as it was."""

import json
import os
import unittest

import helpers
from helpers import entries
from laying import COMMAND, END_ENTRY, ENTRY, KEPT, LANES, TESTED, LayTest


class TestWriteHooks(LayTest):
    def test_a_plugin_without_hooks_gets_one_entry_for_the_subagent(self):
        # Given: a plugin with no hooks.json
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: hooks.json holds the subagent's entry, and those its calls are kept by
        self.assertEqual(self.hooks(), {"hooks": {"PreToolUse": [ENTRY], **KEPT}})

    def test_hand_on_and_wait_lanes_watch_their_tools_and_keep_all_they_take(self):
        # Given: as_printed and wait_for on step 3, wait_for holding back a command
        laid = [
            {"lane": "as_printed", "takes": ["lay.py print"]},
            {"lane": "wait_for", "takes": ["OK", "lay.py write"]},
        ]
        self.propose(self.proposal(laid))
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: the hook watches every tool, and hooks/lanes.json gives each lane with all it
        # takes, the command held back among them
        entry = self.hooks()["hooks"]["PreToolUse"][0]
        self.assertEqual(entry["matcher"], ".*|Bash")
        self.assertEqual(self.laid()["subagents"][0]["steps"][0]["lanes"], laid)

    def test_every_other_entry_stays_as_it_was(self):
        # Given: hooks.json with a description, an entry of the building AI's own, and one of
        # another event
        own = {"matcher": "Write", "hooks": [{"type": "command", "command": "own.sh"}]}
        stop = {"hooks": [{"type": "command", "command": "stop.sh"}]}
        hooks: dict = {"description": "d", "hooks": {"PreToolUse": [own], "Stop": [stop]}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: they stay as they were, the subagent's entry after them
        hooks["hooks"]["PreToolUse"].append(ENTRY)
        hooks["hooks"].update(KEPT)
        self.assertEqual(self.hooks(), hooks)

    def test_the_subagents_entry_written_before_is_replaced_in_its_place(self):
        # Given: hooks.json with two entries the layer wrote for the subagent among others, one of
        # them written by the layer for another subagent of the plugin whose name begins with this
        # one's
        second = helpers.STEPS.replace("name: changelog-writer", "name: changelog-writer-2")
        self.write(os.path.join(self.plugin, "agents", "writer-2.md"), second)
        own = {"matcher": "Write", "hooks": [{"type": "command", "command": "own.sh"}]}
        older = {"matcher": "Bash", "hooks": [{"type": "command", "command": COMMAND + " x"}]}
        other = json.loads(json.dumps(ENTRY).replace("changelog-writer", "changelog-writer-2"))
        written = [own, older, other, older]
        self.write_json(
            os.path.join(self.plugin, "hooks", "hooks.json"), {"hooks": {"PreToolUse": written}}
        )
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: the entry stands where the first stood, the second gone, the others as they were
        self.assertEqual(self.hooks()["hooks"]["PreToolUse"], [own, ENTRY, other])

    def test_the_entries_of_a_subagent_the_plugin_no_longer_has_are_taken_out(self):
        # Given: hooks.json with an entry of the building AI's own, one the layer wrote for a
        # subagent of another plugin, and the entries the layer wrote for a subagent agents/ no
        # longer has, on both events
        own = {"matcher": "Write", "hooks": [{"type": "command", "command": "own.sh"}]}
        other = json.loads(json.dumps(ENTRY).replace("notes:changelog-writer", "memo:summarizer"))
        gone = json.loads(json.dumps(ENTRY).replace("changelog-writer", "summarizer"))
        ended = json.loads(json.dumps(END_ENTRY).replace("changelog-writer", "summarizer"))
        hooks = {"hooks": {"PreToolUse": [own, other, gone], "SubagentStop": [ended]}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        # When: the proposal is written
        _, said = self.lay("write", self.proposal_file)
        # Then: they are taken out and said, the other entries as they were
        kept = {"PreToolUse": [own, other, ENTRY], "SubagentStop": [], **KEPT}
        self.assertEqual(self.hooks(), {"hooks": kept})
        self.assertIn("Took out the hooks of summarizer, which agents/ no longer has.", said)

    def test_hooks_json_is_written_indented_by_two_its_text_as_written(self):
        # Given: hooks.json whose description is not ASCII
        hooks: dict = {"description": "変更履歴", "hooks": {}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: the file is the hooks indented by two, the description as it was written
        hooks["hooks"].update({"PreToolUse": [ENTRY], **KEPT})
        self.assertEqual(
            self.read(os.path.join(self.plugin, "hooks", "hooks.json")),
            json.dumps(hooks, indent=2, ensure_ascii=False) + "\n",
        )

    def test_hooks_not_in_claude_codes_shape_stop_before_anything_is_written(self):
        wrong = {
            "no JSON": "{",
            "no object": "[]",
            "hooks that are no object": '{"hooks": []}',
            "PreToolUse entries that are no list": '{"hooks": {"PreToolUse": {}}}',
            "an entry that is no object": '{"hooks": {"PreToolUse": [1]}}',
            "an entry whose hooks are no list": '{"hooks": {"PreToolUse": [{"hooks": {}}]}}',
            "a hook that is no object": '{"hooks": {"PreToolUse": [{"hooks": [1]}]}}',
        }
        for what, text in wrong.items():
            with self.subTest(what=what):
                # Given: hooks.json in another shape
                self.write(os.path.join(self.plugin, "hooks", "hooks.json"), text)
                # When: the proposal is written
                code, said = self.lay("write", self.proposal_file)
                # Then: it exits 1 naming the file and what to do, the step left as it was
                self.assertEqual(code, 1)
                self.assertIn("hooks/hooks.json", said)
                self.assertIn("fix it", said)
                self.assertEqual(self.read(self.agent_file), helpers.STEPS)


class TestWriteEndHooks(LayTest):
    """Lanes held as the subagent is about to end, written into an entry of SubagentStop."""

    def test_a_lane_held_at_the_end_gets_a_subagentstop_entry_alone(self):
        # Given: test_after alone on step 3
        self.propose(self.proposal([TESTED]))
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: hooks.json holds a SubagentStop entry matching the subagent, running its entry
        # with the lane, and no PreToolUse entry, beside those its calls are kept by
        self.assertEqual(self.hooks(), {"hooks": {"SubagentStop": [END_ENTRY], **KEPT}})

    def test_lanes_of_both_events_get_an_entry_each(self):
        # Given: hands_off and test_after on step 3
        self.propose(self.proposal([*LANES, TESTED]))
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: each event's entry gives its lanes alone
        self.assertEqual(
            self.hooks(),
            {"hooks": {"PreToolUse": [ENTRY], "SubagentStop": [END_ENTRY], **KEPT}},
        )

    def test_a_lane_held_on_both_events_goes_into_each_entry(self):
        # Given: as_printed on step 3, held on a tool call and as the subagent is about to end
        self.propose(self.proposal([{"lane": "as_printed", "takes": ["lay.py print"]}]))
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: each event has an entry of the subagent, PreToolUse's matching every tool,
        # SubagentStop's the subagent
        events = self.hooks()["hooks"]
        for event, matcher in (
            ("PreToolUse", ".*"),
            ("SubagentStop", "notes:changelog-writer"),
        ):
            with self.subTest(event=event):
                entry = events[event][0]
                self.assertEqual(entry["matcher"], matcher)
                self.assertTrue(entry["hooks"][0]["command"].endswith(" notes:changelog-writer"))

    def test_an_entry_of_an_event_no_lane_is_held_on_now_is_taken_out(self):
        # Given: hooks.json holding the subagent's entries of both events from before, beside an
        # entry of the building AI's own
        own = {"hooks": [{"type": "command", "command": "own.sh"}]}
        hooks = {"hooks": {"PreToolUse": [ENTRY], "SubagentStop": [own, END_ENTRY]}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        # When: a proposal of hands_off alone is written
        self.lay("write", self.proposal_file)
        # Then: the SubagentStop entry the layer wrote is gone, the building AI's kept
        self.assertEqual(
            self.hooks(), {"hooks": {"PreToolUse": [ENTRY], "SubagentStop": [own], **KEPT}}
        )

    def test_subagentstop_entries_not_in_claude_codes_shape_stop(self):
        for text in ('{"hooks": {"SubagentStop": {}}}', '{"hooks": {"SubagentStop": [1]}}'):
            with self.subTest(text=text):
                # Given: hooks.json whose SubagentStop entries are no list, or no objects
                self.write(os.path.join(self.plugin, "hooks", "hooks.json"), text)
                # When: the proposal is written
                code, said = self.lay("write", self.proposal_file)
                # Then: it exits 1 naming the file
                self.assertEqual(code, 1)
                self.assertIn("hooks/hooks.json", said)


class TestMatcher(unittest.TestCase):
    def test_a_subagents_entry_matches_each_tool_its_lanes_watch_once(self):
        form = ["entry.json", "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"]
        for laid, matcher in (
            ([("in_form", form)], "Write|Edit|Bash"),
            (
                [("hands_off", ["git commit"]), ("write_only", ["CHANGELOG.md"])],
                "Bash|Write|Edit|NotebookEdit",
            ),
        ):
            with self.subTest(laid=laid):
                # Given: the lanes laid on a step, two of them watching Bash
                lanes = [{"lane": lane, "takes": takes} for lane, takes in laid]
                agent = {"name": "writer", "steps": [{"step": 3, "lanes": lanes}]}
                # When: the layer makes the subagent's entry of PreToolUse
                entry = entries.entry("notes", agent, "PreToolUse")
                # Then: its matcher names each tool they watch, once, in the order laid
                self.assertEqual((entry or {}).get("matcher"), matcher)


if __name__ == "__main__":
    unittest.main()

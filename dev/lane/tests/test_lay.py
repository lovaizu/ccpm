"""The layer: the proposal printed for the building AI's OK, and written word for word into the plugin,
with every other entry of its hooks.json as it was, lane's code put beside them, and the plugin
checked by Claude Code."""

import contextlib
import io
import json
import os
import runpy
import shutil
import sys
from unittest import mock

import helpers
from helpers import lay

# The proposal of lane's README: hands_off on step 3 of changelog-writer.
LANES = [{"lane": "hands_off", "takes": ["git commit", "git push"]}]
# The hook's command lane:up writes for it.
COMMAND = (
    'python3 -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null'
    ' || { e=; while IFS= read -r l || [ -n "$l" ]; do e="$e$l"; l=; done; case "$e" in'
    """ *'"agent_type":"notes:changelog-writer"'*|*'"agent_type": "notes:changelog-writer"'*)"""
    ' echo "notes: install Python 3.9 or later, run as python3, for its hooks to run" >&2;'
    ' exit 2;; esac; exit 0; }; exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py"'
    " notes:changelog-writer '3:hands_off:git commit,git push'"
)
ENTRY = {"matcher": "Bash", "hooks": [{"type": "command", "timeout": 10, "command": COMMAND}]}
# test_after on step 3, held as the subagent is about to end, and its entry of SubagentStop, which
# matches the subagent, exits 1 where Python is missing, and runs that event's entry.
TESTED = {"lane": "test_after", "takes": ["CHANGELOG.md", "python3 check.py"]}
END_COMMAND = (
    COMMAND.replace("pretooluse.py", "subagentstop.py")
    .replace("exit 2;", "exit 1;")
    .replace("'3:hands_off:git commit,git push'", "'3:test_after:CHANGELOG.md,python3 check.py'")
)
END_ENTRY = {
    "matcher": "notes:changelog-writer",
    "hooks": [{"type": "command", "timeout": 10, "command": END_COMMAND}],
}
# What `print` shows the building AI for it.
PRINTED = """Lanes on step 3 of changelog-writer, each hook acting in changelog-writer alone:
  run: Do not run `git commit` or `git push`.  hook hands_off

3. Write the new entries into `CHANGELOG.md`. Do not run `git commit` or `git push`.
"""
# hands_off on step 3 taking `git push` alone, and its sentence.
PUSH = [{"lane": "hands_off", "takes": ["git push"]}]
PUSHED = "Do not run `git push`."
# A stand-in for Claude Code's command, which keeps what it was asked and exits as the test sets.
CLAUDE = """#!/bin/sh
echo "$@" > "$(dirname "$0")/asked"
echo "validated"
exit "${CLAUDE_EXIT:-0}"
"""


class LayTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.proposal_file = os.path.join(self.base, "data", "notes.json")
        self.propose(self.proposal())
        self.bin = os.path.join(self.base, "bin")
        self.write(os.path.join(self.bin, "claude"), CLAUDE)
        os.chmod(os.path.join(self.bin, "claude"), 0o755)
        path = mock.patch.dict(os.environ, {"PATH": self.bin + os.pathsep + os.environ["PATH"]})
        path.start()
        self.addCleanup(path.stop)

    def proposal(self, lanes=LANES, name="changelog-writer", number=3):
        return {
            "plugin": self.plugin,
            "subagents": [{"name": name, "steps": [{"step": number, "lanes": lanes}]}],
        }

    def propose(self, proposal):
        self.write_json(self.proposal_file, proposal)

    def lay(self, *argv):
        """lay.py run with the arguments; what it exits with and what it prints."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = lay.main(list(argv))
        return code, out.getvalue()

    def hooks(self):
        return self.read_json(os.path.join(self.plugin, "hooks", "hooks.json"))


class TestPrint(LayTest):
    def test_the_proposal_is_printed_as_the_building_ai_reads_it(self):
        # Given: the proposal of hands_off on step 3 of changelog-writer
        # When: it is printed
        # Then: the lane shows under its action with its hook, and the step as it would read
        self.assertEqual(self.lay("print", self.proposal_file), (0, PRINTED))

    def test_printing_changes_nothing(self):
        # Given: the proposal
        # When: it is printed
        self.lay("print", self.proposal_file)
        # Then: the subagent's file is as it was, no hooks are written, and the proposal is kept
        self.assertEqual(self.read(self.agent_file), helpers.STEPS)
        self.assertFalse(os.path.exists(os.path.join(self.plugin, "hooks")))
        self.assertTrue(os.path.exists(self.proposal_file))

    def test_each_step_is_printed_apart(self):
        # Given: lanes on two steps
        proposal = self.proposal()
        proposal["subagents"][0]["steps"].insert(0, {"step": 1, "lanes": LANES})
        self.propose(proposal)
        # When: it is printed
        # Then: each step is printed as one alone is, a blank line between them
        one = PRINTED.replace("step 3", "step 1").replace(
            "3. Write the new entries into `CHANGELOG.md`.",
            "1. Read the commits since the last release.",
        )
        self.assertEqual(self.lay("print", self.proposal_file), (0, one + "\n" + PRINTED))

    def test_lanes_of_several_actions_line_up(self):
        # Given: two lanes on one step, standing in for lanes of two actions
        two = [*LANES, {"lane": "hands_off", "takes": ["npm publish"]}]
        self.propose(self.proposal(two))
        # When: it is printed
        # Then: each lane is a line of its own, their hooks lined up
        self.assertIn(
            "  run: Do not run `git commit` or `git push`.  hook hands_off\n"
            "  run: Do not run `npm publish`.               hook hands_off\n",
            self.lay("print", self.proposal_file)[1],
        )

    def test_what_a_hook_holds_beyond_its_sentence_is_printed_beside_it(self):
        # Given: wait_for on step 3, taking the approval and two commands it holds back
        wait = [{"lane": "wait_for", "takes": ["OK", "lay.py write", "git push"]}]
        self.propose(self.proposal(wait))
        # When: it is printed
        # Then: the sentence shows the approval alone, and the commands held back follow its hook
        self.assertIn(
            "  wait: Do not go on until `OK`.  hook wait_for, holding back `lay.py write`,"
            " `git push`\n",
            self.lay("print", self.proposal_file)[1],
        )


class TestWriteStep(LayTest):
    def test_the_sentence_is_put_at_the_end_of_the_step(self):
        # Given: the proposal
        # When: it is written
        self.assertEqual(self.lay("write", self.proposal_file)[0], 0)
        # Then: step 3 ends with the sentence, before its Out line, the rest as it was
        self.assertEqual(
            self.read(self.agent_file),
            helpers.LAID,
        )

    def test_a_step_over_several_lines_gets_the_sentence_on_its_last(self):
        # Given: step 3 going on over a second line
        two_lines = helpers.STEPS.replace(
            "`CHANGELOG.md`.\n", "`CHANGELOG.md`,\n   newest first.\n"
        )
        self.write(self.agent_file, two_lines)
        # When: the proposal is printed and written
        printed = self.lay("print", self.proposal_file)[1]
        self.lay("write", self.proposal_file)
        # Then: the step reads with its first line as it was and the sentence after its last
        step = "3. Write the new entries into `CHANGELOG.md`,\n   newest first. " + helpers.SENTENCE
        self.assertTrue(printed.endswith("\n\n" + step + "\n"), printed)
        self.assertEqual(
            self.read(self.agent_file),
            two_lines.replace("newest first.\n", f"newest first. {helpers.SENTENCE}\n"),
        )

    def test_a_sentence_the_step_already_says_is_not_written_again(self):
        # Given: the proposal written once
        self.lay("write", self.proposal_file)
        laid = self.read(self.agent_file)
        self.propose(self.proposal())
        # When: it is written again
        self.lay("write", self.proposal_file)
        # Then: the step says the sentence once
        self.assertEqual(self.read(self.agent_file), laid)

    def test_a_sentence_said_on_a_line_before_the_steps_last_is_not_written_again(self):
        # Given: step 3 saying the sentence on its first line, going on over a second
        said = helpers.STEPS.replace(
            "`CHANGELOG.md`.\n", f"`CHANGELOG.md`. {helpers.SENTENCE}\n   Newest first.\n"
        )
        self.write(self.agent_file, said)
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: the step is as it was
        self.assertEqual(self.read(self.agent_file), said)


class TestLayAgain(LayTest):
    """Laying again: the sentence of each lane the subagent's hook held before and the proposal no
    longer lays on its step taken out of the step, the rest of it as it was."""

    def lay_again(self, proposal):
        """Writes the proposal of lane's README, then proposes the one given."""
        self.lay("write", self.proposal_file)
        self.propose(proposal)

    def test_a_lane_laid_again_taking_other_things_has_its_old_sentence_taken_out(self):
        # Given: hands_off laid on step 3 taking `git commit` and `git push`, proposed again taking
        # `git push` alone
        self.lay_again(self.proposal(PUSH))
        # When: it is printed and written
        printed = self.lay("print", self.proposal_file)[1]
        self.lay("write", self.proposal_file)
        # Then: the step says the new sentence alone, as printed, the rest as it was
        laid = helpers.STEPS.replace("`CHANGELOG.md`.\n", f"`CHANGELOG.md`. {PUSHED}\n")
        self.assertEqual(self.read(self.agent_file), laid)
        self.assertTrue(
            printed.endswith(f"\n\n3. Write the new entries into `CHANGELOG.md`. {PUSHED}\n"),
            printed,
        )

    def test_a_lane_on_a_step_the_proposal_no_longer_has_is_taken_out_of_it(self):
        # Given: hands_off laid on steps 1 and 3, proposed again on step 3 alone
        proposal = self.proposal()
        proposal["subagents"][0]["steps"].insert(0, {"step": 1, "lanes": LANES})
        self.propose(proposal)
        self.lay_again(self.proposal())
        # When: it is printed and written
        printed = self.lay("print", self.proposal_file)[1]
        self.lay("write", self.proposal_file)
        # Then: step 1 reads as before any lane was laid, shown so after step 3, and step 3 keeps
        # its sentence
        self.assertEqual(self.read(self.agent_file), helpers.LAID)
        self.assertTrue(
            printed.endswith(
                PRINTED
                + "\nNo lanes on step 1 of changelog-writer now, their sentences taken out:\n"
                "\n1. Read the commits since the last release.\n"
            ),
            printed,
        )

    def test_a_lane_held_on_a_step_the_steps_no_longer_have_is_passed_over(self):
        # Given: the subagent's hook holding a lane on step 9, which its Steps do not have
        held = json.loads(json.dumps(ENTRY).replace("'3:hands_off", "'9:hands_off"))
        self.write_json(
            os.path.join(self.plugin, "hooks", "hooks.json"), {"hooks": {"PreToolUse": [held]}}
        )
        # When: the proposal is printed and written
        printed = self.lay("print", self.proposal_file)
        self.lay("write", self.proposal_file)
        # Then: step 3 alone is printed and written, the rest of the file as it was
        self.assertEqual(printed, (0, PRINTED))
        self.assertEqual(self.read(self.agent_file), helpers.LAID)

    def test_a_sentence_no_hook_of_the_subagent_held_stays(self):
        # Given: step 3 saying the sentence, held by the hook of another subagent alone, and
        # hands_off proposed on step 3 taking `git push` alone
        self.write(self.agent_file, helpers.LAID)
        other = json.loads(json.dumps(ENTRY).replace("changelog-writer", "other"))
        hooks = {"hooks": {"PreToolUse": [other]}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        self.propose(self.proposal(PUSH))
        # When: it is written
        self.lay("write", self.proposal_file)
        # Then: the step keeps the sentence and gets the new one after it
        self.assertEqual(
            self.read(self.agent_file),
            helpers.LAID.replace(f"{helpers.SENTENCE}\n", f"{helpers.SENTENCE} {PUSHED}\n"),
        )

    def test_a_sentence_kept_by_the_proposal_stays_in_its_place(self):
        # Given: two lanes laid on step 3, proposed again with the first taking other things and
        # the second as it was
        two = [*LANES, {"lane": "hands_off", "takes": ["npm publish"]}]
        self.propose(self.proposal(two))
        self.lay_again(self.proposal([*PUSH, two[1]]))
        # When: it is written
        self.lay("write", self.proposal_file)
        # Then: the second's sentence stays where it was, the new one after it
        self.assertEqual(
            self.read(self.agent_file),
            helpers.STEPS.replace(
                "`CHANGELOG.md`.\n",
                f"`CHANGELOG.md`. Do not run `npm publish`. {PUSHED}\n",
            ),
        )


class TestWriteHooks(LayTest):
    def test_a_plugin_without_hooks_gets_one_entry_for_the_subagent(self):
        # Given: a plugin with no hooks.json
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: hooks.json holds the subagent's entry alone
        self.assertEqual(self.hooks(), {"hooks": {"PreToolUse": [ENTRY]}})

    def test_hand_on_and_wait_lanes_watch_their_tools_and_keep_all_they_take(self):
        # Given: as_printed and wait_for on step 3, wait_for holding back a command
        laid = [
            {"lane": "as_printed", "takes": ["lay.py print"]},
            {"lane": "wait_for", "takes": ["OK", "lay.py write"]},
        ]
        self.propose(self.proposal(laid))
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: the hook watches the tools that hand on and Bash, and gives each lane with all it
        # takes, the command held back among them
        entry = self.hooks()["hooks"]["PreToolUse"][0]
        self.assertEqual(entry["matcher"], "Agent|SendMessage|Bash")
        words = "notes:changelog-writer '3:as_printed:lay.py print' '3:wait_for:OK,lay.py write'"
        self.assertTrue(entry["hooks"][0]["command"].endswith(words))

    def test_every_other_entry_stays_as_it_was(self):
        # Given: hooks.json with a description, an entry of the building AI's own, and one of another
        # event
        own = {"matcher": "Write", "hooks": [{"type": "command", "command": "own.sh"}]}
        stop = {"hooks": [{"type": "command", "command": "stop.sh"}]}
        hooks: dict = {"description": "d", "hooks": {"PreToolUse": [own], "Stop": [stop]}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: they stay as they were, the subagent's entry after them
        hooks["hooks"]["PreToolUse"].append(ENTRY)
        self.assertEqual(self.hooks(), hooks)

    def test_the_subagents_entry_written_before_is_replaced_in_its_place(self):
        # Given: hooks.json with two entries lane:up wrote for the subagent among others, one of
        # them written by lane:up for another subagent of the plugin whose name begins with this
        # one's
        second = helpers.STEPS.replace("name: changelog-writer", "name: changelog-writer-2")
        self.write(os.path.join(self.plugin, "agents", "writer-2.md"), second)
        own = {"matcher": "Write", "hooks": [{"type": "command", "command": "own.sh"}]}
        older = {"matcher": "Bash", "hooks": [{"type": "command", "command": COMMAND + " x"}]}
        other = json.loads(json.dumps(ENTRY).replace("changelog-writer", "changelog-writer-2"))
        entries = [own, older, other, older]
        self.write_json(
            os.path.join(self.plugin, "hooks", "hooks.json"), {"hooks": {"PreToolUse": entries}}
        )
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: the entry stands where the first stood, the second gone, the others as they were
        self.assertEqual(self.hooks()["hooks"]["PreToolUse"], [own, ENTRY, other])

    def test_the_entries_of_a_subagent_the_plugin_no_longer_has_are_taken_out(self):
        # Given: hooks.json with an entry of the building AI's own, one lane:up wrote for a
        # subagent of another plugin, and the entries lane:up wrote for a subagent agents/ no
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
        kept = {"PreToolUse": [own, other, ENTRY], "SubagentStop": []}
        self.assertEqual(self.hooks(), {"hooks": kept})
        self.assertIn("Took out the hooks of summarizer, which agents/ no longer has.", said)

    def test_hooks_json_is_written_indented_by_two_its_text_as_written(self):
        # Given: hooks.json whose description is not ASCII
        hooks: dict = {"description": "変更履歴", "hooks": {}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: the file is the hooks indented by two, the description as it was written
        hooks["hooks"]["PreToolUse"] = [ENTRY]
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
        # with the lane, and no PreToolUse entry
        self.assertEqual(self.hooks(), {"hooks": {"SubagentStop": [END_ENTRY]}})

    def test_lanes_of_both_events_get_an_entry_each(self):
        # Given: hands_off and test_after on step 3
        self.propose(self.proposal([*LANES, TESTED]))
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: each event's entry gives its lanes alone
        self.assertEqual(
            self.hooks(), {"hooks": {"PreToolUse": [ENTRY], "SubagentStop": [END_ENTRY]}}
        )

    def test_a_lane_held_on_both_events_goes_into_each_entry(self):
        # Given: as_printed on step 3, held on a tool call and as the subagent is about to end
        self.propose(self.proposal([{"lane": "as_printed", "takes": ["lay.py print"]}]))
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: each event's entry gives the lane, PreToolUse's matching the tools that hand on,
        # SubagentStop's the subagent
        events = self.hooks()["hooks"]
        word = "notes:changelog-writer '3:as_printed:lay.py print'"
        for event, matcher in (
            ("PreToolUse", "Agent|SendMessage"),
            ("SubagentStop", "notes:changelog-writer"),
        ):
            with self.subTest(event=event):
                entry = events[event][0]
                self.assertEqual(entry["matcher"], matcher)
                self.assertTrue(entry["hooks"][0]["command"].endswith(word))

    def test_an_entry_of_an_event_no_lane_is_held_on_now_is_taken_out(self):
        # Given: hooks.json holding the subagent's entries of both events from before, beside an
        # entry of the building AI's own
        own = {"hooks": [{"type": "command", "command": "own.sh"}]}
        hooks = {"hooks": {"PreToolUse": [ENTRY], "SubagentStop": [own, END_ENTRY]}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        # When: a proposal of hands_off alone is written
        self.lay("write", self.proposal_file)
        # Then: the SubagentStop entry lane:up wrote is gone, the building AI's kept
        self.assertEqual(self.hooks(), {"hooks": {"PreToolUse": [ENTRY], "SubagentStop": [own]}})

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


class TestWriteCode(LayTest):
    def code(self):
        return os.path.join(self.plugin, "hooks", "lane")

    def test_lanes_code_is_copied_with_its_version(self):
        # Given: a plugin outside the ccpm marketplace
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: lane's code is copied into hooks/lane/, each file as lane's, with VERSION holding
        # the version of lane's plugin.json
        for name in (
            "pretooluse.py",
            "hook.py",
            "call.py",
            "shell.py",
            "step.py",
            "lanes/hands_off.py",
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    self.read(os.path.join(self.code(), name)),
                    self.read(os.path.join(helpers.CODE, name)),
                )
        version = self.read_json(os.path.join(helpers.LANE, ".claude-plugin", "plugin.json"))
        self.assertEqual(self.read(os.path.join(self.code(), "VERSION")), version["version"] + "\n")
        self.assertFalse(os.path.islink(self.code()))

    def test_a_copy_there_before_is_replaced(self):
        # Given: a copy of lane's code there before, holding a file lane no longer has
        self.write(os.path.join(self.code(), "old.py"), "")
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: the copy is lane's code as it is now
        self.assertFalse(os.path.exists(os.path.join(self.code(), "old.py")))
        self.assertTrue(os.path.exists(os.path.join(self.code(), "pretooluse.py")))

    def test_a_plugin_of_the_ccpm_marketplace_links_to_lanes_code(self):
        # Given: the plugin in a clone of the ccpm marketplace, lane beside it
        self.write_json(
            os.path.join(self.base, ".claude-plugin", "marketplace.json"), {"name": "ccpm"}
        )
        os.makedirs(os.path.join(self.base, "lane", "hooks", "lane"))
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: hooks/lane is a relative link to lane's code beside it, with no VERSION
        self.assertEqual(
            os.readlink(self.code()), os.path.join("..", "..", "lane", "hooks", "lane")
        )

    def test_a_link_there_before_is_made_again(self):
        # Given: the plugin in a clone of the ccpm marketplace, its lanes written once
        self.write_json(
            os.path.join(self.base, ".claude-plugin", "marketplace.json"), {"name": "ccpm"}
        )
        os.makedirs(os.path.join(self.base, "lane", "hooks", "lane"))
        self.lay("write", self.proposal_file)
        self.propose(self.proposal())
        # When: the proposal is written again
        # Then: it is written, hooks/lane the same link
        self.assertEqual(self.lay("write", self.proposal_file)[0], 0)
        self.assertEqual(
            os.readlink(self.code()), os.path.join("..", "..", "lane", "hooks", "lane")
        )

    def test_a_plugin_of_another_marketplace_or_without_lane_beside_it_gets_a_copy(self):
        for name, beside in (
            ('{"name": "ccpm"}', False),
            ('{"name": "acme"}', True),
            ('{"name": "zeta"}', True),
            ("[]", True),
            ("{", True),
        ):
            with self.subTest(marketplace=name, lane_beside=beside):
                # Given: the plugin in ccpm without lane beside it, or in another marketplace, or
                # in one whose manifest names none, with lane beside it
                self.write(os.path.join(self.base, ".claude-plugin", "marketplace.json"), name)
                if beside:
                    os.makedirs(os.path.join(self.base, "lane", "hooks", "lane"), exist_ok=True)
                self.propose(self.proposal())
                # When: the proposal is written
                self.lay("write", self.proposal_file)
                # Then: lane's code is copied
                self.assertFalse(os.path.islink(self.code()))
                self.assertTrue(os.path.exists(os.path.join(self.code(), "VERSION")))

    def test_only_lanes_code_itself_is_lanes_own(self):
        for place, own in ((helpers.CODE, True), (os.path.dirname(helpers.CODE), False)):
            with self.subTest(place=place):
                # Given: lane's code, or the folder it is in
                # When: whether it is lane's own code is read
                # Then: it is for lane's code alone
                self.assertEqual(lay.lanes_own(place), own)

    def test_lanes_own_code_is_left_as_it_is_on_lane_itself(self):
        # Given: the plugin is lane itself, its hooks/lane/ the code the layer runs on
        own = os.path.join(self.code(), "pretooluse.py")
        self.write(own, "lane's own")
        with mock.patch.object(lay, "CODE", self.code()):
            # When: the proposal is written
            self.lay("write", self.proposal_file)
        # Then: lane's code is left where it is, unremoved, with no VERSION put in it
        self.assertEqual(self.read(own), "lane's own")
        self.assertFalse(os.path.exists(os.path.join(self.code(), "VERSION")))


class TestWriteEnd(LayTest):
    def test_the_plugin_is_validated_and_the_proposal_removed(self):
        # Given: the proposal
        # When: it is written
        code, said = self.lay("write", self.proposal_file)
        # Then: Claude Code validated the plugin, the proposal is removed, and what was written is
        # said
        self.assertEqual(code, 0)
        self.assertEqual(
            self.read(os.path.join(self.bin, "asked")), f"plugin validate {self.plugin}\n"
        )
        self.assertFalse(os.path.exists(self.proposal_file))
        self.assertEqual(
            said,
            "Wrote step 3 of changelog-writer into agents/writer.md.\n"
            "Wrote the hook of changelog-writer into hooks/hooks.json.\n"
            "Put lane's code in hooks/lane/.\n"
            "claude plugin validate passed.\n"
            f"Removed the proposal {self.proposal_file}.\n",
        )

    def test_a_plugin_claude_code_finds_malformed_keeps_the_proposal(self):
        # Given: Claude Code finding the plugin malformed
        with mock.patch.dict(os.environ, {"CLAUDE_EXIT": "1"}):
            # When: the proposal is written
            code, said = self.lay("write", self.proposal_file)
        # Then: it exits 1 with what Claude Code said and what to do, the proposal kept
        self.assertEqual(
            (code, said),
            (
                1,
                (
                    f"lay.py: claude plugin validate found {self.plugin} malformed:\nvalidated\n"
                    f"fix what it names, then run `lay.py write {self.proposal_file}` again.\n"
                ),
            ),
        )
        self.assertTrue(os.path.exists(self.proposal_file))

    def test_without_claude_on_path_the_proposal_is_kept(self):
        # Given: no claude on PATH
        with mock.patch.dict(os.environ, {"PATH": os.path.join(self.base, "none")}):
            # When: the proposal is written
            code, said = self.lay("write", self.proposal_file)
        # Then: it exits 1 saying to install Claude Code, the proposal kept
        self.assertEqual(code, 1)
        self.assertIn("install Claude Code", said)
        self.assertTrue(os.path.exists(self.proposal_file))


class TestProposal(LayTest):
    def test_a_proposal_not_as_lane_up_writes_it_stops_naming_what_is_wrong(self):
        plugin = self.proposal()
        wrong = {
            "no proposal file": (None, "no file"),
            "no JSON": ("{", "no JSON"),
            "no object": ([], "plugin"),
            "a plugin of no folder": (dict(plugin, plugin=os.path.join(self.base, "x")), "plugin"),
            "no subagents": (dict(plugin, subagents=[]), "subagents"),
            "a subagent of no name": (self.proposal(name=""), "name"),
            "a subagent that is no object": (dict(plugin, subagents=[1]), "name"),
            "a subagent of no steps": (
                dict(plugin, subagents=[{"name": "changelog-writer", "steps": []}]),
                "no steps",
            ),
            "a step that is no object": (
                dict(plugin, subagents=[{"name": "changelog-writer", "steps": [1]}]),
                "no number",
            ),
            "a lane that is no object": (self.proposal([1]), "no lane"),
            "a subagent of a name no file has": (self.proposal(name="other"), "other"),
            "a step the file has not": (self.proposal(number=9), "step 9"),
            "a step of no number": (self.proposal(number="3"), "step"),
            "no lanes": (self.proposal([]), "lanes"),
            "a lane lane has not": (self.proposal([{"lane": "x", "takes": ["a"]}]), "x"),
            "a lane taking nothing": (self.proposal([{"lane": "hands_off", "takes": []}]), "takes"),
            "takes that are no list": (
                self.proposal([{"lane": "hands_off", "takes": "git push"}]),
                "no takes",
            ),
            "a thing taken with a comma": (
                self.proposal([{"lane": "hands_off", "takes": ["a,b"]}]),
                "takes",
            ),
            "a lane taking fewer things than its wording shows": (
                self.proposal([{"lane": "in_form", "takes": ["out.json"]}]),
                "takes",
            ),
            "a thing taken that is empty": (
                self.proposal([{"lane": "hands_off", "takes": [""]}]),
                "takes",
            ),
            "a lane taking nothing for its last place": (
                self.proposal([{"lane": "test_after", "takes": ["CHANGELOG.md"]}]),
                "test_after on step 3 of changelog-writer takes of another count",
            ),
            "nothing held beyond what the sentence shows": (
                self.proposal([{"lane": "wait_for", "takes": ["OK"]}]),
                "wait_for on step 3 of changelog-writer takes of another count",
            ),
        }
        for what, (proposal, named) in wrong.items():
            with self.subTest(what=what):
                # Given: a proposal in another shape
                if proposal is None:
                    os.remove(self.proposal_file)
                elif isinstance(proposal, str):
                    self.write(self.proposal_file, proposal)
                else:
                    self.propose(proposal)
                # When: it is printed or written
                for action in ("print", "write"):
                    code, said = self.lay(action, self.proposal_file)
                    # Then: it exits 1 naming what is wrong and saying to write it again, nothing
                    # written
                    self.assertEqual(code, 1)
                    self.assertIn(named, said)
                    self.assertIn("write the proposal again", said)
                self.assertEqual(self.read(self.agent_file), helpers.STEPS)

    def test_a_plugin_whose_name_cannot_head_a_hook_stops(self):
        for text in ('{"name": ""}', '{"name": "no\\"tes"}', "{}", "[]"):
            with self.subTest(manifest=text):
                # Given: a plugin whose manifest names it so a hook's command cannot carry it, or
                # names it not at all
                self.write(os.path.join(self.plugin, ".claude-plugin", "plugin.json"), text)
                # When: the proposal is printed
                code, said = self.lay("print", self.proposal_file)
                # Then: it exits 1 naming the manifest
                self.assertEqual(code, 1)
                self.assertIn("plugin.json", said)

    def test_a_manifest_holding_no_json_stops_saying_so(self):
        # Given: a plugin whose manifest holds no JSON
        self.write(os.path.join(self.plugin, ".claude-plugin", "plugin.json"), "{")
        # When: the proposal is printed
        code, said = self.lay("print", self.proposal_file)
        # Then: it exits 1 saying the manifest holds no JSON
        self.assertEqual(code, 1)
        self.assertIn("plugin.json holds no JSON", said)


class TestRunValue(LayTest):
    """A proposal of write_only taking `{work}`, a value given for each run."""

    def setUp(self) -> None:
        super().setUp()
        self.propose(self.proposal([{"lane": "write_only", "takes": ["{work}"]}]))

    def test_a_take_given_for_each_run_is_printed_as_written(self):
        # Given: the proposal
        # When: it is printed
        # Then: the sentence shows `{work}` as written, in the lane's line and in the step
        said = self.lay("print", self.proposal_file)[1]
        self.assertIn("  write: Write only `{work}`.  hook write_only\n", said)
        self.assertIn("`CHANGELOG.md`. Write only `{work}`.\n", said)

    def test_a_take_given_for_each_run_is_written_as_written(self):
        # Given: the proposal
        # When: it is written
        self.lay("write", self.proposal_file)
        # Then: the step says `{work}`, and the hook's command gives it as written
        self.assertIn("`CHANGELOG.md`. Write only `{work}`.\n", self.read(self.agent_file))
        command = self.hooks()["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.assertTrue(command.endswith(" '3:write_only:{work}'"), command)


class TestInForm(LayTest):
    """A proposal of in_form, taking an output and its form, a file of the plugin."""

    def in_form(self, form):
        return self.proposal([{"lane": "in_form", "takes": ["entry.json", form]}])

    def test_a_form_lane_reads_is_laid(self):
        for form, text in (
            ("${CLAUDE_PLUGIN_ROOT}/forms/entry.json", '{"type": "object"}'),
            ("${CLAUDE_PLUGIN_ROOT}/forms/entry.md", "## A\n"),
        ):
            with self.subTest(form=form):
                # Given: a proposal of in_form whose form is a schema or a template of the plugin
                self.write(os.path.join(self.plugin, form.split("/", 1)[1]), text)
                self.propose(self.in_form(form))
                # When: it is written
                code, _ = self.lay("write", self.proposal_file)
                # Then: it is laid, its sentence put into the step
                self.assertEqual(code, 0)
                self.assertIn(
                    f"Write `entry.json` in the form of `{form}`.", self.read(self.agent_file)
                )

    def test_the_hook_gives_the_form_as_the_step_names_it_unexpanded_by_the_shell(self):
        # Given: a proposal of in_form whose form is named from the plugin's folder
        form = "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"
        self.write(os.path.join(self.plugin, "forms", "entry.json"), "{}")
        self.propose(self.in_form(form))
        # When: it is written
        self.lay("write", self.proposal_file)
        # Then: the hook's command gives the lane in single quotes, so the guard reads the form as
        # the step names it
        command = self.hooks()["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.assertTrue(command.endswith(f" '3:in_form:entry.json,{form}'"), command)

    def test_a_form_lane_cannot_read_stops_naming_it_before_anything_is_written(self):
        self.write(os.path.join(self.base, "outside.json"), "{}")
        self.write(os.path.join(self.plugin, "forms", "bad.json"), '{"format": "date"}')
        self.write(os.path.join(self.plugin, "forms", "entry.yaml"), "a: b\n")
        for form, named in (
            ("${CLAUDE_PLUGIN_ROOT}/forms/none.json", "cannot be read"),
            ("${CLAUDE_PLUGIN_ROOT}/forms/bad.json", "`format` is no keyword"),
            ("${CLAUDE_PLUGIN_ROOT}/forms/entry.yaml", "neither a .json schema nor a .md template"),
            ("${CLAUDE_PLUGIN_ROOT}/../outside.json", "out of the plugin"),
            ("forms/bad.json", "named as ${CLAUDE_PLUGIN_ROOT}/<path in the plugin>"),
            ("{form}", "named as ${CLAUDE_PLUGIN_ROOT}/<path in the plugin>"),
        ):
            with self.subTest(form=form):
                # Given: a proposal of in_form whose form is not there, not of the keywords lane
                # reads, of no kind lane reads, out of the plugin, or given for each run
                self.propose(self.in_form(form))
                for action in ("print", "write"):
                    # When: it is printed or written
                    code, said = self.lay(action, self.proposal_file)
                    # Then: it exits 1 naming the form and why, and saying to fix it, nothing
                    # written
                    self.assertEqual(code, 1)
                    on = "in_form on step 3 of changelog-writer"
                    self.assertIn(f"{on} names the form {form}, which", said)
                    self.assertIn(named, said)
                    self.assertIn("fix it or the proposal", said)
                self.assertEqual(self.read(self.agent_file), helpers.STEPS)


class TestUp(LayTest):
    """`lay.py up <plugin>`: an older copy of lane's code brought up, with the hooks lane:up wrote
    in the current form and the same lanes."""

    # The hook's command for hands_off as an older version of lane wrote it, with no Python check.
    OLDER = (
        'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py" notes:changelog-writer'
        " '3:hands_off:git commit,git push'"
    )

    def setUp(self) -> None:
        super().setUp()
        # Step 3 as lane:up wrote it, and lane's code as a copy of the version 0.1.0, with lane at
        # 0.10.0, so a comparison of the versions as text would take the copy for the newer.
        self.write(self.agent_file, helpers.LAID)
        self.code = os.path.join(self.plugin, "hooks", "lane")
        self.write(os.path.join(self.code, "VERSION"), "0.1.0\n")
        self.write(os.path.join(self.code, "old.py"), "")
        current = mock.patch.object(lay, "lane_version", return_value="0.10.0")
        current.start()
        self.addCleanup(current.stop)

    def hooks_of(self, *entries, event="PreToolUse"):
        """Writes hooks.json holding the entries of the event, each a command or an entry."""
        given = [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": e}]}
            if isinstance(e, str)
            else e
            for e in entries
        ]
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), {"hooks": {event: given}})

    def up(self):
        return self.lay("up", self.plugin)

    def test_an_older_copy_and_its_hooks_are_brought_up_with_the_same_lanes(self):
        # Given: the copy of 0.1.0, its hook in the older form between two entries of the building AI's
        # own
        own = {"matcher": "Write", "hooks": [{"type": "command", "command": "own.sh"}]}
        self.hooks_of(own, self.OLDER, own)
        # When: it is brought up
        code, said = self.up()
        # Then: the hook is in the current form in its place, the building AI's entries and the step
        # as they were, the copy lane's code with lane's version, and what was done is said
        self.assertEqual(code, 0)
        self.assertEqual(self.hooks(), {"hooks": {"PreToolUse": [own, ENTRY, own]}})
        self.assertEqual(self.read(self.agent_file), helpers.LAID)
        self.assertEqual(self.read(os.path.join(self.code, "VERSION")), "0.10.0\n")
        self.assertFalse(os.path.exists(os.path.join(self.code, "old.py")))
        self.assertEqual(
            said,
            "Brought lane's code in hooks/lane/ up from 0.1.0 to 0.10.0.\n"
            "Wrote the hook of changelog-writer into hooks/hooks.json with the lanes it held.\n",
        )

    def test_hooks_of_both_events_are_brought_up_each_lane_once(self):
        # Given: the hooks of as_printed, held on both events, and test_after, as written now, then
        # left with an older copy
        laid = [{"lane": "as_printed", "takes": ["lay.py print"]}, TESTED]
        self.propose(self.proposal(laid))
        self.lay("write", self.proposal_file)
        written = self.hooks()
        self.write(os.path.join(self.code, "VERSION"), "0.1.0\n")
        # When: it is brought up
        self.up()
        # Then: the hooks are as written from the same lanes, each lane in each entry once
        self.assertEqual(self.hooks(), written)

    def test_a_copy_with_no_readable_version_is_brought_up(self):
        for version, was in ((None, "a copy with no VERSION"), ("one\n", "one")):
            with self.subTest(version=version):
                # Given: a copy with no VERSION, or one holding no version
                path = os.path.join(self.code, "VERSION")
                if version is None:
                    os.remove(path)
                else:
                    self.write(path, version)
                self.hooks_of(self.OLDER)
                # When: it is brought up
                code, said = self.up()
                # Then: the copy is lane's version, and what it was is said
                self.assertEqual(code, 0)
                self.assertTrue(
                    said.startswith(f"Brought lane's code in hooks/lane/ up from {was}")
                )
                self.assertEqual(self.read(path), "0.10.0\n")

    def test_code_not_an_older_copy_is_left_as_it_is(self):
        for what in ("the same version", "a newer version", "a link", "no code", "lane's own"):
            with self.subTest(what=what):
                # Given: a copy of lane's version or a newer, a link, no code, or lane itself
                self.hooks_of(self.OLDER)
                own = mock.patch.object(lay, "CODE", self.code if what == "lane's own" else "x")
                if os.path.islink(self.code):
                    os.remove(self.code)
                shutil.rmtree(self.code, ignore_errors=True)
                version = {"the same version": "0.10.0\n", "a newer version": "0.11.0\n"}
                if what == "a link":
                    os.symlink(helpers.CODE, self.code)
                elif what != "no code":
                    self.write(os.path.join(self.code, "VERSION"), version.get(what, "0.1.0\n"))
                # When: it is brought up
                with own:
                    code, said = self.up()
                # Then: nothing is brought up, and it says so
                self.assertEqual(code, 0)
                self.assertEqual(said, "hooks/lane/ holds no older copy of lane's code.\n")
                self.assertEqual(
                    self.hooks()["hooks"]["PreToolUse"][0]["hooks"][0]["command"], self.OLDER
                )

    def test_a_lane_this_version_does_not_lay_is_left_out_and_said(self):
        # Given: a hook laying hands_off beside a lane lane has not and in_form taking too few, and
        # another subagent's hook laying only a lane lane has not
        gone, short = "'2:gone:x'", "'3:in_form:entry.json'"
        self.hooks_of(
            f"{self.OLDER} {gone} {short}",
            'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py" notes:other 1:gone:y',
        )
        # When: it is brought up
        code, said = self.up()
        # Then: the hooks lay the lanes this version lays, the other subagent's hook taken out, and
        # each lane left out is said, for lane:up to put to the building AI
        self.assertEqual(code, 0)
        self.assertEqual(self.hooks(), {"hooks": {"PreToolUse": [ENTRY]}})
        for agent, word in (
            ("changelog-writer", "2:gone:x"),
            ("changelog-writer", "3:in_form:entry.json"),
            ("other", "1:gone:y"),
        ):
            with self.subTest(word=word):
                self.assertIn(
                    f"Left out `{word}` from the hook of {agent}, as lane 0.10.0 lays no such lane;"
                    " ask the building AI whether to lay it again or leave it out.\n",
                    said,
                )

    def test_a_lane_left_out_of_the_hooks_of_both_events_is_said_once(self):
        # Given: a lane lane has not, in the hook of each event
        hooks = {}
        for event in ("PreToolUse", "SubagentStop"):
            script = f'"${{CLAUDE_PLUGIN_ROOT}}/hooks/lane/{event.lower()}.py"'
            command = f"python3 {script} notes:changelog-writer 2:gone:x"
            hooks[event] = [{"hooks": [{"type": "command", "command": command}]}]
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), {"hooks": hooks})
        # When: it is brought up
        said = self.up()[1]
        # Then: it is said once
        self.assertEqual(said.count("Left out `2:gone:x`"), 1)

    def test_a_command_giving_no_subagent_lane_can_read_is_left_as_it_is(self):
        # Given: commands running lane's script with no words, a subagent with no plugin, or words
        # the shell cannot read, beside the hook of changelog-writer
        script = 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py"'
        others = [script, f"{script} changelog-writer", f"{script} notes:changelog-writer 'x"]
        self.hooks_of(*others, self.OLDER)
        # When: it is brought up
        self.up()
        # Then: those are left as they were, and the hook of changelog-writer is brought up
        commands = [e["hooks"][0]["command"] for e in self.hooks()["hooks"]["PreToolUse"]]
        self.assertEqual(commands, [*others, COMMAND])

    def test_hooks_not_in_claude_codes_shape_stop(self):
        # Given: hooks.json holding no JSON
        self.write(os.path.join(self.plugin, "hooks", "hooks.json"), "{")
        # When: it is brought up
        code, said = self.up()
        # Then: it exits 1 naming the file, the copy left as it was
        self.assertEqual(code, 1)
        self.assertIn("hooks/hooks.json", said)
        self.assertEqual(self.read(os.path.join(self.code, "VERSION")), "0.1.0\n")


class TestMain(LayTest):
    def test_any_other_arguments_print_how_to_run_it(self):
        for argv in ([], ["print"], ["up"], ["lay", self.proposal_file], ["print", "a", "b"]):
            with self.subTest(argv=argv):
                # Given: arguments lay.py does not take
                # When: it is run with them
                # Then: it exits 1 printing how to run it
                self.assertEqual(self.lay(*argv), (1, lay.USAGE + "\n"))

    def test_lanes_own_code_is_taken_before_modules_of_the_same_name(self):
        # Given: modules named as lane's code's, found first on sys.path, none yet imported
        shadow = os.path.join(self.base, "shadow")
        for name in ("lanes", "step", "call"):
            self.write(os.path.join(shadow, f"{name}.py"), "raise ImportError('not lane')\n")
        script = os.path.join(helpers.SCRIPTS, "lay.py")
        path = mock.patch.object(sys, "path", [shadow, *sys.path])
        modules = mock.patch.dict(sys.modules)
        argv = mock.patch.object(sys, "argv", [script, "print", self.proposal_file])
        out = io.StringIO()
        with path, modules, argv, contextlib.redirect_stdout(out):
            for name in ("lanes", "lanes.hands_off", "step", "call"):
                sys.modules.pop(name, None)
            # When: lay.py is run
            with self.assertRaises(SystemExit) as done:
                runpy.run_path(script, run_name="__main__")
        # Then: it runs on lane's code, printing the proposal
        self.assertEqual((done.exception.code, out.getvalue()), (0, PRINTED))

    def test_the_script_exits_with_what_main_gives(self):
        # Given: lay.py run as a script, in this process so that the coverage counts it
        script = os.path.join(helpers.SCRIPTS, "lay.py")
        out = io.StringIO()
        argv = mock.patch.object(sys, "argv", [script, "print", self.proposal_file])
        with argv, contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as done:
            runpy.run_path(script, run_name="__main__")
        # When: it prints the proposal
        # Then: it exits 0 with the print
        self.assertEqual((done.exception.code, out.getvalue()), (0, PRINTED))

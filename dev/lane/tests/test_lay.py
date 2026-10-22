"""The layer: the proposal printed for the builder's OK, and written word for word into the plugin,
with every other entry of its hooks.json as it was, lane's code put beside them, and the plugin
checked by Claude Code."""

import contextlib
import io
import json
import os
import runpy
import sys
from unittest import mock

import helpers
from helpers import lay

# The proposal of lane's README: hands_off on step 3 of changelog-writer.
LANES = [{"lane": "hands_off", "takes": ["git commit", "git push"]}]
# The hook's command lane:up writes for it.
COMMAND = (
    'python3 -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null'
    ' || { echo "notes: install Python 3.9 or later, run as python3, for its hooks to run" >&2;'
    ' exit 2; }; exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py"'
    " notes:changelog-writer '3:hands_off:git commit,git push'"
)
ENTRY = {"matcher": "Bash", "hooks": [{"type": "command", "timeout": 10, "command": COMMAND}]}
# What `print` shows the builder for it.
PRINTED = """Lanes on step 3 of changelog-writer, each hook acting in changelog-writer alone:
  run: Do not run `git commit` or `git push`.  hook hands_off

3. Write the new entries into `CHANGELOG.md`. Do not run `git commit` or `git push`.
"""
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
    def test_the_proposal_is_printed_as_the_builder_reads_it(self):
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
        # Given: hooks.json with a description, an entry of the builder's own, and one of another
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
        # them written by lane:up for another subagent whose name begins with this one's
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
                # Given: the plugin in ccpm without lane beside it, or in another marketplace,
                # its name sorting before ccpm or after, or in one whose manifest names none,
                # with lane beside it
                self.write(os.path.join(self.base, ".claude-plugin", "marketplace.json"), name)
                if beside:
                    os.makedirs(os.path.join(self.base, "lane", "hooks", "lane"), exist_ok=True)
                self.propose(self.proposal())
                # When: the proposal is written
                self.lay("write", self.proposal_file)
                # Then: lane's code is copied
                self.assertFalse(os.path.islink(self.code()))
                self.assertTrue(os.path.exists(os.path.join(self.code(), "VERSION")))


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
            "claude plugin validate passed.\n",
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
            "a thing taken with a comma": (
                self.proposal([{"lane": "hands_off", "takes": ["a,b"]}]),
                "takes",
            ),
            "a thing taken that is empty": (
                self.proposal([{"lane": "hands_off", "takes": [""]}]),
                "takes",
            ),
            "nothing held beyond what the sentence shows": (
                self.proposal([{"lane": "wait_for", "takes": ["OK"]}]),
                "nothing after what its sentence shows",
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
        for text in ('{"name": ""}', '{"name": "no\\"tes"}', "{}", "[]", "{"):
            with self.subTest(manifest=text):
                # Given: a plugin whose manifest names it so a hook's command cannot carry it, or
                # names it not at all
                self.write(os.path.join(self.plugin, ".claude-plugin", "plugin.json"), text)
                # When: the proposal is printed
                code, said = self.lay("print", self.proposal_file)
                # Then: it exits 1 naming the manifest
                self.assertEqual(code, 1)
                self.assertIn("plugin.json", said)


class TestMain(LayTest):
    def test_any_other_arguments_print_how_to_run_it(self):
        for argv in ([], ["print"], ["lay", self.proposal_file], ["print", "a", "b"]):
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

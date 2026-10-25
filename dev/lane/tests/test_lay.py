"""The layer as the building AI runs it: the plugin written checked by Claude Code and the proposal
removed; an older copy of lane's code brought up with the hooks the layer wrote before; any other
arguments answered with how to run it."""

from __future__ import annotations

import contextlib
import io
import json
import os
import runpy
import shutil
import sys
import unittest
from unittest import mock

import helpers
from helpers import lay, placed
from laying import (
    COMMAND,
    ENTRY,
    KEPT,
    LAID,
    LANES,
    PRINTED,
    TESTED,
    LayTest,
)


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
            "Wrote the lanes laid into hooks/lanes.json.\n"
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


class TestWriteLanes(LayTest):
    def test_the_lanes_of_other_subagents_are_kept_and_those_of_one_gone_taken_out(self):
        # Given: hooks/lanes.json laying lanes in changelog-writer, in another subagent the plugin
        # has, and in one agents/ no longer has
        second = helpers.STEPS.replace("name: changelog-writer", "name: summarizer")
        self.write(os.path.join(self.plugin, "agents", "summarizer.md"), second)
        steps = [{"step": 2, "lanes": [{"lane": "hands_off", "takes": ["git push"]}]}]
        before = [
            {"name": "summarizer", "steps": steps},
            {"name": "changelog-writer", "steps": steps},
            {"name": "gone", "steps": steps},
        ]
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), {"subagents": before})
        # When: the proposal of changelog-writer is written
        self.lay("write", self.proposal_file)
        # Then: the other subagent's lanes are kept, changelog-writer's are the proposal's, in
        # their place, and the gone one's are taken out, each with its hooks
        self.assertEqual(
            self.laid(),
            {"subagents": [before[0], LAID["subagents"][0]]},
        )
        names = {e["matcher"] for e in self.hooks()["hooks"]["PreToolUse"]}
        self.assertEqual(names, {"Bash"})
        self.assertEqual(len(self.hooks()["hooks"]["PreToolUse"]), 2)


class TestUp(LayTest):
    """`lay.py up <plugin>`: an older copy of lane's code brought up, with the hooks the layer wrote
    in the current form and the same lanes; and each lane laid before said, for the building AI to
    keep in its proposal or leave out."""

    # The hook's command for hands_off as an older version of lane wrote it, with no Python check.
    OLDER = (
        'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py" notes:changelog-writer'
        " '3:hands_off:git commit,git push'"
    )
    # What `up` says of hands_off laid before on step 3, as the proposal gives the lane.
    LAID = (
        "Laid before on step 3 of changelog-writer:"
        ' {"lane": "hands_off", "takes": ["git commit", "git push"]}\n'
    )

    def setUp(self) -> None:
        super().setUp()
        # Step 3 as the layer wrote it, and lane's code as a copy of the version 0.1.0, with lane at
        # 0.10.0, so a comparison of the versions as text would take the copy for the newer.
        self.write(self.agent_file, helpers.LAID)
        self.code = os.path.join(self.plugin, "hooks", "lane")
        self.write(os.path.join(self.code, "VERSION"), "0.1.0\n")
        self.write(os.path.join(self.code, "old.py"), "")
        current = mock.patch.object(placed, "lane_version", return_value="0.10.0")
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

    def up(self) -> tuple:
        """What `lay.py up` on the plugin exits with and prints."""
        return self.lay("up", self.plugin)

    def test_an_older_copy_and_its_hooks_are_brought_up_with_the_same_lanes(self):
        # Given: the copy of 0.1.0, its hook in the older form between two entries of the building
        # AI's own
        own = {"matcher": "Write", "hooks": [{"type": "command", "command": "own.sh"}]}
        self.hooks_of(own, self.OLDER, own)
        # When: it is brought up
        code, said = self.up()
        # Then: the hook is in the current form in its place, the building AI's entries and the step
        # as they were, the copy lane's code with lane's version, and what was done is said
        self.assertEqual(code, 0)
        self.assertEqual(self.hooks(), {"hooks": {"PreToolUse": [own, ENTRY, own], **KEPT}})
        self.assertEqual(self.laid(), LAID)
        self.assertEqual(self.read(self.agent_file), helpers.LAID)
        self.assertEqual(self.read(os.path.join(self.code, "VERSION")), "0.10.0\n")
        self.assertFalse(os.path.exists(os.path.join(self.code, "old.py")))
        self.assertEqual(
            said,
            "Brought lane's code in hooks/lane/ up from 0.1.0 to 0.10.0.\n"
            "Wrote the hook of changelog-writer into hooks/hooks.json with the lanes it held.\n"
            + self.LAID,
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

    def code_gone(self) -> None:
        """Takes out of the plugin's hooks/lane/ whatever is there, a copy or a link."""
        if os.path.islink(self.code):
            os.remove(self.code)
        shutil.rmtree(self.code, ignore_errors=True)

    def code_as(self, version: str | None) -> None:
        """Puts in the plugin's hooks/lane/, in place of what is there, a copy holding the version
        as its VERSION, or nothing where it is None."""
        self.code_gone()
        if version is not None:
            self.write(os.path.join(self.code, "VERSION"), version)

    def code_linked(self) -> None:
        """Puts a link to lane's code in the plugin's hooks/lane/, in place of what is there."""
        self.code_gone()
        os.symlink(helpers.CODE, self.code)

    def code_kinds(self) -> tuple:
        """What hooks/lane/ may hold that is no older copy, each a name, how it is made and what
        lane's own code is taken to be: a copy of lane's version or a newer, a link, no code, or
        lane itself."""
        return (
            ("the same version", lambda: self.code_as("0.10.0\n"), "x"),
            ("a newer version", lambda: self.code_as("0.11.0\n"), "x"),
            ("a link", self.code_linked, "x"),
            ("no code", lambda: self.code_as(None), "x"),
            ("lane's own", lambda: None, self.code),
        )

    def test_hooks_in_an_older_form_are_brought_up_wherever_the_code_is_no_older_copy(self):
        for what, made, own in self.code_kinds():
            with self.subTest(what=what):
                # Given: the hook in an older form, and code that is no older copy
                self.hooks_of(self.OLDER)
                made()
                # When: it is brought up
                with mock.patch.object(placed, "CODE", own):
                    code, said = self.up()
                # Then: the hook is in the current form with the same lanes, the code left as it
                # was, and what was written is said, with the lane laid before
                self.assertEqual(code, 0)
                self.assertEqual(self.hooks(), {"hooks": {"PreToolUse": [ENTRY], **KEPT}})
                wrote = "Wrote the hook of changelog-writer into hooks/hooks.json with the lanes"
                self.assertEqual(said, f"{wrote} it held.\n" + self.LAID)

    def test_hooks_in_the_current_form_and_code_no_older_copy_are_left_as_they_are(self):
        for what, made, own in self.code_kinds():
            with self.subTest(what=what):
                # Given: the hook in the current form, and code that is no older copy
                hooks = {"hooks": {"PreToolUse": [ENTRY], **KEPT}}
                self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
                self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), LAID)
                written = self.hooks()
                made()
                # When: it is brought up
                with mock.patch.object(placed, "CODE", own):
                    code, said = self.up()
                # Then: nothing is written, and it says so, and the lane laid before
                self.assertEqual(code, 0)
                no_copy = "hooks/lane/ holds no older copy of lane's code.\n"
                self.assertEqual(said, no_copy + self.LAID)
                self.assertEqual(self.hooks(), written)

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
        # each lane left out is said, for the building AI to weigh
        self.assertEqual(code, 0)
        self.assertEqual(self.hooks(), {"hooks": {"PreToolUse": [ENTRY], **KEPT}})
        for agent, word in (
            ("changelog-writer", "2:gone:x"),
            ("changelog-writer", "3:in_form:entry.json"),
            ("other", "1:gone:y"),
        ):
            with self.subTest(word=word):
                self.assertIn(
                    f"Left out `{word}` from the hook of {agent}, as lane 0.10.0 lays no such lane;"
                    " propose a lane of docs/lanes.md that keeps its step, or leave it out.\n",
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

    def test_a_lane_whose_step_no_longer_says_its_sentence_is_said_so(self):
        # Given: hands_off laid before on step 3, which no longer says its sentence
        self.write(self.agent_file, helpers.STEPS)
        self.hooks_of(self.OLDER)
        # When: the plugin is brought up
        said = self.up()[1]
        # Then: the lane is said with the sentence its step no longer says
        gone = ', whose step no longer says "Do not run `git commit` or `git push`.":'
        self.assertIn(self.LAID.replace(":", gone, 1), said)

    def test_a_plugin_with_no_hooks_has_no_lanes_laid_before(self):
        # Given: a plugin with no hooks.json and no copy of lane's code
        shutil.rmtree(self.code)
        # When: it is brought up
        # Then: it says there is no older copy, and nothing more
        no_copy = "hooks/lane/ holds no older copy of lane's code.\n"
        self.assertEqual(self.up(), (0, no_copy))

    def test_a_folder_with_no_manifest_stops_with_nothing_brought_up(self):
        # Given: the older copy and its hook, in a folder with no .claude-plugin/plugin.json
        self.hooks_of(self.OLDER)
        os.remove(os.path.join(self.plugin, ".claude-plugin", "plugin.json"))
        # When: it is brought up
        code, said = self.up()
        # Then: it exits 1 saying the folder is no plugin's and to name one, the copy and the
        # hook left as they were
        stop = (
            f"lay.py: {self.plugin} holds no .claude-plugin/plugin.json, so it is no plugin's"
            " folder; name the folder of the plugin to lay lanes on.\n"
        )
        self.assertEqual((code, said), (1, stop))
        self.assertEqual(self.read(os.path.join(self.code, "VERSION")), "0.1.0\n")
        command = self.hooks()["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.assertEqual(command, self.OLDER)

    def test_a_manifest_naming_no_plugin_stops(self):
        # Given: a manifest giving the plugin no name
        self.write_json(os.path.join(self.plugin, ".claude-plugin", "plugin.json"), {})
        # When: it is brought up
        code, said = self.up()
        # Then: it exits 1 naming the manifest, the copy left as it was
        self.assertEqual(code, 1)
        self.assertIn("plugin.json names the plugin by no name", said)
        self.assertEqual(self.read(os.path.join(self.code, "VERSION")), "0.1.0\n")

    def test_the_lanes_an_older_lane_gave_on_one_step_are_kept_on_it_together(self):
        # Given: the hook in the older form giving hands_off and write_only on step 3
        self.hooks_of(f"{self.OLDER} '3:write_only:CHANGELOG.md'")
        # When: it is brought up
        self.up()
        # Then: hooks/lanes.json gives step 3 once, with both lanes
        write = {"lane": "write_only", "takes": ["CHANGELOG.md"]}
        steps = [{"step": 3, "lanes": [*LANES, write]}]
        self.assertEqual(self.laid(), {"subagents": [{"name": "changelog-writer", "steps": steps}]})

    def test_the_lanes_an_older_lane_gave_are_kept_on_each_step_by_its_number(self):
        # Given: the hook in the older form giving lanes on step 3, then step 1, then step 3 again
        self.hooks_of(f"{self.OLDER} '1:hands_off:git tag' '3:write_only:CHANGELOG.md'")
        # When: it is brought up
        self.up()
        # Then: hooks/lanes.json gives step 3 with both its lanes, and step 1 with its own
        write = {"lane": "write_only", "takes": ["CHANGELOG.md"]}
        tag = {"lane": "hands_off", "takes": ["git tag"]}
        steps = [{"step": 3, "lanes": [*LANES, write]}, {"step": 1, "lanes": [tag]}]
        self.assertEqual(self.laid(), {"subagents": [{"name": "changelog-writer", "steps": steps}]})

    def test_lanes_json_is_written_indented_by_two_its_text_as_written(self):
        # Given: the hook in the older form giving a command that is not ASCII
        self.hooks_of(f"{self.OLDER} '1:hands_off:echo 変更'")
        # When: it is brought up
        self.up()
        # Then: hooks/lanes.json is the lanes indented by two, the command as it was written
        tag = {"lane": "hands_off", "takes": ["echo 変更"]}
        steps = [{"step": 3, "lanes": LANES}, {"step": 1, "lanes": [tag]}]
        laid = {"subagents": [{"name": "changelog-writer", "steps": steps}]}
        self.assertEqual(
            self.read(os.path.join(self.plugin, "hooks", "lanes.json")),
            json.dumps(laid, indent=2, ensure_ascii=False) + "\n",
        )

    def test_lanes_json_that_cannot_be_read_stops(self):
        # Given: hooks/lanes.json holding no JSON
        self.write(os.path.join(self.plugin, "hooks", "lanes.json"), "{")
        # When: it is brought up
        code, said = self.up()
        # Then: it exits 1 naming the file and what is wrong, the copy left as it was
        self.assertEqual(code, 1)
        self.assertIn(f"{self.plugin}/hooks/lanes.json holds no JSON; fix it", said)
        self.assertEqual(self.read(os.path.join(self.code, "VERSION")), "0.1.0\n")

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
        for argv in (
            [],
            ["print"],
            ["up"],
            ["up", self.plugin, "data"],
            ["lay", self.proposal_file],
            ["print", "a", "b"],
        ):
            with self.subTest(argv=argv):
                # Given: arguments lay.py does not take
                # When: it is run with them
                # Then: it exits 1 printing how to run it
                self.assertEqual(self.lay(*argv), (1, lay.USAGE + "\n"))

    def test_lanes_own_code_is_taken_before_modules_of_the_same_name(self):
        # Given: modules named as lane's code's, found first on sys.path, none yet imported, and
        # lay.py run as a script in this process, so that the coverage counts it
        shadow = os.path.join(self.base, "shadow")
        for name in ("lanes", "step", "call"):
            self.write(os.path.join(shadow, f"{name}.py"), "raise ImportError('not lane')\n")
        script = os.path.join(helpers.SCRIPTS, "lay.py")
        path = mock.patch.object(sys, "path", [shadow, *sys.path])
        modules = mock.patch.dict(sys.modules)
        argv = mock.patch.object(sys, "argv", [script, "print", self.proposal_file])
        out = io.StringIO()
        with path, modules, argv, contextlib.redirect_stdout(out):
            # The layer's own modules too, as each imports lane's code as it is first imported.
            layer = ("entries", "placed", "proposal", "steps", "hooks_file", "hook", "template")
            for name in ("lanes", "lanes.hands_off", "step", "call", *layer):
                sys.modules.pop(name, None)
            # When: lay.py is run
            with self.assertRaises(SystemExit) as done:
                runpy.run_path(script, run_name="__main__")
        # Then: it runs on lane's code, printing the proposal
        self.assertEqual((done.exception.code, out.getvalue()), (0, PRINTED))


if __name__ == "__main__":
    unittest.main()

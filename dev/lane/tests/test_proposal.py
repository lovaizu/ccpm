"""The proposal the layer takes: read and checked to be as lane:up writes it, each stop naming what is
wrong before anything is written, a take given for each run and in_form's form among what is
checked."""

import os
import unittest

import helpers
from laying import LayTest


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


if __name__ == "__main__":
    unittest.main()

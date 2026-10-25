"""The proposal the layer takes: read and checked to be as lane:up writes it, each stop naming what
is wrong before anything is written, a take given for each run and in_form's form among what is
checked."""

import os
import unittest

import helpers
from laying import LANES, PUSH, LayTest


class TestProposal(LayTest):
    def test_a_proposal_not_as_lane_up_writes_it_stops_naming_what_is_wrong(self):
        plugin = self.proposal()
        wrong = {
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
            "a step given twice": (
                dict(
                    plugin,
                    subagents=[
                        {
                            "name": "changelog-writer",
                            "steps": [{"step": 3, "lanes": LANES}, {"step": 3, "lanes": PUSH}],
                        }
                    ],
                ),
                "gives step 3 of changelog-writer twice",
            ),
            "a subagent given twice": (
                dict(plugin, subagents=plugin["subagents"] * 2),
                "gives changelog-writer twice",
            ),
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

    def test_each_subagent_and_each_step_given_once_is_taken(self):
        # Given: a proposal of two subagents, each with two steps
        second = helpers.STEPS.replace("name: changelog-writer", "name: changelog-writer-2")
        self.write(os.path.join(self.plugin, "agents", "writer-2.md"), second)
        steps = [{"step": n, "lanes": PUSH} for n in (3, 2)]
        self.propose(
            {
                "plugin": self.plugin,
                "subagents": [
                    {"name": "changelog-writer", "steps": steps},
                    {"name": "changelog-writer-2", "steps": steps},
                ],
            }
        )
        # When: it is printed
        code, said = self.lay("print", self.proposal_file)
        # Then: it is taken, each step of each subagent printed
        self.assertEqual(code, 0)
        self.assertEqual(said.count("Lanes on step"), 4)

    def test_a_proposal_not_there_or_holding_no_json_stops_saying_so(self):
        for what, made, named in (
            ("none", lambda: os.remove(self.proposal_file), "no file"),
            ("no JSON", lambda: self.write(self.proposal_file, "{"), "no JSON"),
        ):
            with self.subTest(what=what):
                # Given: no proposal file, or one holding no JSON
                made()
                # When: it is printed
                code, said = self.lay("print", self.proposal_file)
                # Then: it exits 1 saying so and to write it again
                self.assertEqual(code, 1)
                self.assertIn(named, said)
                self.assertIn("write the proposal again", said)

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


class TestComma(LayTest):
    def test_a_thing_taken_holding_a_comma_is_written_as_it_is(self):
        # Given: a proposal of hands_off taking a command holding a comma
        self.propose(self.proposal([{"lane": "hands_off", "takes": ["git commit -m a,b"]}]))
        # When: it is written
        code, _ = self.lay("write", self.proposal_file)
        # Then: the step says it, and hooks/lanes.json gives it as it is
        self.assertEqual(code, 0)
        self.assertIn("Do not run `git commit -m a,b`.", self.read(self.agent_file))
        [lane] = self.laid()["subagents"][0]["steps"][0]["lanes"]
        self.assertEqual(lane["takes"], ["git commit -m a,b"])


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
        # Then: the step says `{work}`, and hooks/lanes.json gives it as written
        self.assertIn("`CHANGELOG.md`. Write only `{work}`.\n", self.read(self.agent_file))
        [lane] = self.laid()["subagents"][0]["steps"][0]["lanes"]
        self.assertEqual(lane, {"lane": "write_only", "takes": ["{work}"]})


class TestInForm(LayTest):
    """A proposal of in_form, taking an output and its form, a file of the plugin."""

    def in_form(self, form: str) -> dict:
        """A proposal of in_form on step 3, holding entry.json to the form."""
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

    def test_the_lanes_give_the_form_as_the_step_names_it(self):
        # Given: a proposal of in_form whose form is named from the plugin's folder
        form = "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"
        self.write(os.path.join(self.plugin, "forms", "entry.json"), "{}")
        self.propose(self.in_form(form))
        # When: it is written
        self.lay("write", self.proposal_file)
        # Then: hooks/lanes.json gives the form as the step names it, for the guard to read so
        [lane] = self.laid()["subagents"][0]["steps"][0]["lanes"]
        self.assertEqual(lane["takes"], ["entry.json", form])

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

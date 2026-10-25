"""The proposal the layer takes: read and checked to be in the shape docs/lanes.md gives, each stop
naming what is wrong before anything is written, a take given for each run and in_form's form among
what is checked."""

import json
import os
import unittest

import helpers
from helpers import proposal
from laying import AGAIN, LANES, LANES_MD, PUSH, LayTest

# Where the proposal's first subagent, its first step and the first lane on it are.
SUBAGENT = ("subagents", 0)
STEP = (*SUBAGENT, "steps", 0)
LANE = (*STEP, "lanes", 0)
# What a key a case removes is set to.
GONE = object()


def edited(given: dict, path: tuple, value: object) -> dict:
    """A copy of the proposal given with the value at the path, the key removed where it is
    GONE."""
    copied = json.loads(json.dumps(given))
    *above, last = path
    at = copied
    for step in above:
        at = at[step]
    if value is GONE:
        del at[last]
    else:
        at[last] = value
    return copied


class TestProposal(LayTest):
    def stops(self, given: object, named: str) -> None:
        """Checks that the proposal, printed or written, exits 1 naming what is wrong and saying to
        write it again in its shape, with nothing written."""
        self.propose(given)
        for action in ("print", "write"):
            code, said = self.lay(action, self.proposal_file)
            self.assertEqual(code, 1)
            self.assertIn(named, said)
            self.assertTrue(said.endswith(f"; {AGAIN}.\n"), said)
        self.assertEqual(self.read(self.agent_file), helpers.STEPS)

    def test_a_proposal_out_of_its_schema_stops_naming_the_point(self):
        plugin = self.proposal()
        cases = {
            "no plugin": (("plugin",), GONE, '$: expected the key "plugin"'),
            "no subagents": (("subagents",), GONE, '$: expected the key "subagents"'),
            "a subagent of no name": (
                (*SUBAGENT, "name"),
                GONE,
                '$.subagents[0]: expected the key "name"',
            ),
            "a subagent of no steps": (
                (*SUBAGENT, "steps"),
                GONE,
                '$.subagents[0]: expected the key "steps"',
            ),
            "a step of no number": (
                (*STEP, "step"),
                GONE,
                '$.subagents[0].steps[0]: expected the key "step"',
            ),
            "a step of no lanes": (
                (*STEP, "lanes"),
                GONE,
                '$.subagents[0].steps[0]: expected the key "lanes"',
            ),
            "a lane of no name": (
                (*LANE, "lane"),
                GONE,
                '$.subagents[0].steps[0].lanes[0]: expected the key "lane"',
            ),
            "a lane of no takes": (
                (*LANE, "takes"),
                GONE,
                '$.subagents[0].steps[0].lanes[0]: expected the key "takes"',
            ),
            "a plugin of no text": (("plugin",), 1, "$.plugin: expected a string, found 1"),
            "subagents of no list": (
                ("subagents",),
                {},
                "$.subagents: expected an array, found {}",
            ),
            "a subagent of no object": (SUBAGENT, 1, "$.subagents[0]: expected an object, found 1"),
            "a name of no text": ((*SUBAGENT, "name"), 1, "$.subagents[0].name: expected a string"),
            "a values adapter of no text": (
                (*SUBAGENT, "adapter"),
                1,
                "$.subagents[0].adapter: expected a string",
            ),
            "steps of no list": (
                (*SUBAGENT, "steps"),
                "3",
                "$.subagents[0].steps: expected an array",
            ),
            "a step of no object": (
                STEP,
                1,
                "$.subagents[0].steps[0]: expected an object, found 1",
            ),
            "a number of a text": (
                (*STEP, "step"),
                "3",
                '$.subagents[0].steps[0].step: expected an integer, found "3"',
            ),
            "lanes of no list": (
                (*STEP, "lanes"),
                {},
                "$.subagents[0].steps[0].lanes: expected an array, found {}",
            ),
            "a lane of no object": (
                LANE,
                1,
                "$.subagents[0].steps[0].lanes[0]: expected an object, found 1",
            ),
            "a lane lane has not": (
                (*LANE, "lane"),
                "x",
                '$.subagents[0].steps[0].lanes[0].lane: expected one of "start_with"',
            ),
            "takes of no list": (
                (*LANE, "takes"),
                "git push",
                '$.subagents[0].steps[0].lanes[0].takes: expected an array, found "git push"',
            ),
            "a take of no text": (
                (*LANE, "takes"),
                [1],
                "$.subagents[0].steps[0].lanes[0].takes[0]: expected a string, found 1",
            ),
            "a lane's adapter of no text": (
                (*LANE, "adapter"),
                1,
                "$.subagents[0].steps[0].lanes[0].adapter: expected a string",
            ),
            "a key beside the proposal's": (
                ("x",),
                1,
                '$: expected only the keys "plugin", "subagents", found the key "x"',
            ),
            "a key beside a subagent's": (
                (*SUBAGENT, "x"),
                1,
                '$.subagents[0]: expected only the keys "name", "adapter", "steps", found the key "x"',
            ),
            "a key beside a step's": (
                (*STEP, "x"),
                1,
                '$.subagents[0].steps[0]: expected only the keys "step", "lanes", found the key "x"',
            ),
            "a key beside a lane's": (
                (*LANE, "x"),
                1,
                '$.subagents[0].steps[0].lanes[0]: expected only the keys "lane", "takes", "adapter", found the key "x"',
            ),
            "no subagent": (
                ("subagents",),
                [],
                "$.subagents: expected at least 1 item, found none",
            ),
            "no step": ((*SUBAGENT, "steps"), [], "$.subagents[0].steps: expected at least 1 item"),
            "no lane": (
                (*STEP, "lanes"),
                [],
                "$.subagents[0].steps[0].lanes: expected at least 1 item",
            ),
        }
        for what, (path, value, point) in cases.items():
            with self.subTest(what=what):
                # Given: a proposal with a key missing, of another type, beside its keys, or a list
                # holding none
                # When: it is printed or written
                # Then: it exits 1 naming the point it is out of its schema by, nothing written
                self.stops(
                    edited(plugin, path, value), f"the proposal is out of its shape at {point}"
                )
        with self.subTest(what="no object"):
            # Given: a proposal of a list
            # When: it is printed or written
            # Then: it exits 1 saying it is no object, nothing written
            self.stops([], "the proposal is out of its shape at $: expected an object, found []")

    def test_a_proposal_its_schema_holds_that_cannot_be_laid_stops_naming_what_is_wrong(self):
        plugin = self.proposal()
        wrong = {
            "a plugin of no folder": (dict(plugin, plugin=os.path.join(self.base, "x")), "plugin"),
            "a subagent of no name": (self.proposal(name=""), "gives a subagent no name"),
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
            "a lane taking nothing": (self.proposal([{"lane": "hands_off", "takes": []}]), "takes"),
            "a lane taking fewer things than its wording shows": (
                self.proposal([{"lane": "in_form", "takes": ["out.json"]}]),
                "takes",
            ),
            "a thing taken that is empty": (
                self.proposal([{"lane": "hands_off", "takes": [""]}]),
                "gives hands_off on step 3 of changelog-writer a take that is empty",
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
        for what, (given, named) in wrong.items():
            with self.subTest(what=what):
                # Given: a proposal its schema holds, naming what the plugin has not or giving what
                # its lane cannot take
                # When: it is printed or written
                # Then: it exits 1 naming what is wrong, nothing written
                self.stops(given, named)

    def test_the_proposals_schema_is_the_one_docs_lanes_md_gives(self):
        # Given: the proposal's JSON Schema docs/lanes.md gives under The proposal
        with open(LANES_MD, encoding="utf-8") as f:
            text = f.read().split("## The proposal")[1].split("\n## ")[0]
        shown = json.loads(text.split("```json\n")[1].split("```")[0])
        # When: the proposal's is read in lane's code
        # Then: they are the same
        self.assertEqual(shown, proposal.PROPOSAL)

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
                self.assertTrue(said.endswith(f"; {AGAIN}.\n"), said)

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

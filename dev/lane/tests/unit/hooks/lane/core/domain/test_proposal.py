"""The proposal the developer AI writes for lay.py: read and held to the JSON Schema docs/lanes.md
gives, then checked against the plugin's files; what this version does not lay yet, and anything
that cannot be laid, refused with what is wrong and what to do."""

import json
import os
import unittest

import helpers
from helpers import proposal


class ProposalTest(helpers.LayTest):
    def refused(self, given: object) -> str:
        """What lay.py says of the proposal given, refusing it."""
        path = self.propose(given)
        with self.assertRaises(proposal.Stop) as stop:
            proposal.proposal(path)
        return str(stop.exception)


class TestRead(ProposalTest):
    def test_the_readmes_proposal_is_read_with_each_step_found_in_its_file(self):
        # Given: the README's proposal
        # When: it is read
        found = proposal.proposal(helpers.PROPOSED)
        # Then: it gives the plugin, its name, and writer with its file, its lines and each step
        # with where it is among them
        self.assertEqual((found["plugin"], found["name"]), ("changelog", "changelog"))
        (writer,) = found["subagents"]
        file = os.path.join("changelog", "agents", "writer.md")
        self.assertEqual((writer["name"], writer["file"]), ("writer", file))
        self.assertEqual(writer["lines"], helpers.WRITER.splitlines(keepends=True))
        self.assertEqual(
            [(s["step"], s["span"]) for s in writer["steps"]], [(2, (8, 9)), (3, (9, 10))]
        )

    def test_the_proposals_schema_is_the_one_docs_lanes_md_gives(self):
        # Given: the proposal's JSON Schema docs/lanes.md gives under The proposal
        with open(os.path.join(helpers.LANE, "docs", "lanes.md"), encoding="utf-8") as f:
            text = f.read().split("## The proposal")[1].split("\n## ")[0]
        shown = json.loads(text.split("```json\n")[1].split("```")[0])
        # When: lay.py's is read
        # Then: they are the same
        self.assertEqual(proposal.PROPOSAL, shown)


class TestRefused(ProposalTest):
    def test_a_proposal_that_cannot_be_read_is_refused(self):
        for given, said in (
            ("{", f"lay.py: {helpers.PROPOSED} holds no JSON;"),
            ({"subagents": []}, "lay.py: the proposal is out of its shape at $: expected the key"),
        ):
            with self.subTest(given=given):
                # Given: a proposal that is no JSON, or out of its shape
                # When: it is read
                # Then: it is refused, pointing to the shape docs/lanes.md gives
                told = self.refused(given)
                self.assertTrue(told.startswith(said), told)
                self.assertIn(os.path.join(helpers.LANE, "docs", "lanes.md"), told)

    def test_a_proposal_not_there_is_refused(self):
        # Given: no file at the path
        # When: it is read
        with self.assertRaises(proposal.Stop) as stop:
            proposal.proposal("gone.json")
        # Then: it is refused, saying so
        self.assertTrue(str(stop.exception).startswith("lay.py: there is no file gone.json;"))

    def test_what_this_version_does_not_lay_yet_is_refused(self):
        read_only = [{"step": 1, "lanes": [{"lane": "read_only", "takes": ["CHANGELOG.md"]}]}]
        with_adapter = [
            {"step": 2, "lanes": [{**helpers.STEPS[0]["lanes"][0], "adapter": "hooks/a.py"}]}
        ]
        routes = {"orchestrator": "lead", "step": 1, "routes": []}
        given_run = [{"step": 3, "lanes": [{"lane": "write_only", "takes": ["{work}"]}]}]
        for given, said in (
            (self.proposal(steps=read_only), "read_only on step 1 of writer"),
            (self.proposal(steps=with_adapter), "an adapter on step 2 of writer"),
            (self.proposal(adapter="hooks/adapters/values-w.py"), "an adapter for writer"),
            ({"plugin": "changelog", "routes": routes}, "routes"),
            (self.proposal(steps=given_run), "`{work}`, given for each run, on step 3 of writer"),
        ):
            with self.subTest(said=said):
                # Given: a lane, an adapter, routes or a thing given for each run, which this
                # version does not lay yet
                # When: the proposal is read
                # Then: it is refused, naming what and telling to leave it out
                told = self.refused(given)
                self.assertIn(said, told)
                self.assertIn("which this version of lane does not lay yet; leave it out", told)

    def test_a_lane_taking_nothing_or_an_empty_thing_is_refused(self):
        for takes, said in (([], "with no take"), (["git log", ""], "with a take that is empty")):
            with self.subTest(takes=takes):
                # Given: run_only on step 2 taking no command, or an empty one beside another
                steps = [{"step": 2, "lanes": [{"lane": "run_only", "takes": takes}]}]
                # When: the proposal is read
                # Then: it is refused
                self.assertIn(
                    f"gives run_only on step 2 of writer {said}",
                    self.refused(self.proposal(steps=steps)),
                )

    def test_a_plugin_that_cannot_be_found_or_named_is_refused(self):
        for manifest, said in (
            (None, "names changelog as the plugin, which has no"),
            ("{", "holds no JSON; fix it and run again."),
            ('{"name": "change log"}', "names the plugin by no name of letters, digits and -._"),
            ("[]", "names the plugin by no name of letters, digits and -._"),
        ):
            with self.subTest(manifest=manifest):
                # Given: a plugin with no manifest, one of no JSON, a name of a blank, or none
                if os.path.exists(self.manifest()):
                    os.remove(self.manifest())
                if manifest is not None:
                    self.write(self.manifest(), manifest)
                # When: the proposal is read
                # Then: it is refused
                self.assertIn(said, self.refused(helpers.PROPOSAL))

    def test_a_subagent_or_step_that_cannot_be_laid_is_refused(self):
        twice = {"name": "writer", "steps": helpers.STEPS}
        step_twice = [helpers.STEPS[0], helpers.STEPS[0]]
        no_step = [{"step": 9, "lanes": helpers.STEPS[0]["lanes"]}]
        for given, said in (
            (
                {"plugin": "changelog", "subagents": [{**twice, "name": "a b"}]},
                "gives a subagent no name",
            ),
            (
                {"plugin": "changelog", "subagents": [{**twice, "name": "lead"}]},
                "gives lead, which no file in agents/ names",
            ),
            ({"plugin": "changelog", "subagents": [twice, twice]}, "gives writer twice"),
            (self.proposal(steps=step_twice), "gives step 2 of writer twice"),
            (self.proposal(steps=no_step), "gives step 9, which the Steps of writer do not have"),
        ):
            with self.subTest(said=said):
                # Given: a subagent of a name no hook can carry, one no file gives, one given
                # twice, a step given twice, or a step its file does not have
                # When: the proposal is read
                # Then: it is refused, saying which
                self.assertIn(said, self.refused(given))


if __name__ == "__main__":
    unittest.main()

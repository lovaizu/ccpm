"""The lanes laid read from a plugin's hooks/lanes.json: the lanes laid in a subagent, and what each
lane of a kind takes in it."""

from __future__ import annotations

import json
import os
import unittest

import helpers
from flowing import FLOW
from helpers import lanes_json

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


class TestShape(unittest.TestCase):
    def test_the_shapes_of_the_lanes_laid_and_the_proposal_are_schemas_lane_reads(self):
        # Given: the shape hooks/lanes.json holds and the shape of a proposal
        # When: each is read as a schema of the keywords lane holds a plugin's forms to
        # Then: each is read whole, as structured outputs would take it
        for shape in (lanes_json.LAID, helpers.proposal.PROPOSAL):
            with self.subTest(shape=shape["required"]):
                helpers.schema.checked(shape)


class TestLaidIn(LanesTest):
    def test_the_lanes_of_the_subagent_are_read_each_take_as_written(self):
        # Given: hooks/lanes.json laying lanes in changelog-writer and another subagent, a thing
        # taken holding a comma
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), LAID)
        # When: the lanes laid in changelog-writer are read
        # Then: they are its own, each its step, the lane and what it takes, the comma kept
        self.assertEqual(
            lanes_json.lanes_of(
                lanes_json.subagent(lanes_json.laid(self.plugin), "changelog-writer")
            ),
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
            lanes_json.lanes_of(
                lanes_json.subagent(lanes_json.laid(self.plugin), "changelog-writer")
            ),
            [(3, "every_item", ["r.md"], "hooks/adapters/items-h.py")],
        )
        self.assertEqual(
            lanes_json.subagent(lanes_json.laid(self.plugin), "changelog-writer"), agent
        )

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
                    lanes_json.lanes_of(
                        lanes_json.subagent(lanes_json.laid(self.plugin), "changelog-writer")
                    )
                self.assertIn(named, str(stop.exception))


def flow_md() -> str:
    """lane's docs/flow.md."""
    with open(os.path.join(helpers.LANE, "docs", "flow.md"), encoding="utf-8") as f:
        return f.read()


class TestFlowShape(unittest.TestCase):
    def test_the_flows_schema_is_the_one_docs_flow_md_gives(self):
        # Given: the flow's JSON Schema docs/flow.md gives under The flow
        text = flow_md().split("## The flow")[1].split("\n## ")[0]
        shown = json.loads(text.split("```json\n")[1].split("```")[0])
        # When: the flow's is read in lane's code
        # Then: they are the same
        self.assertEqual(shown, lanes_json.FLOW)


class TestFlowLaid(LanesTest):
    def laid_with(self, flow: object) -> None:
        """Writes hooks/lanes.json laying LAID's lanes with the flow."""
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), {"flow": flow, **LAID})

    def test_a_flow_in_its_form_is_read_with_the_lanes(self):
        for what, flow in {
            "with a back": FLOW,
            "with no back": {k: v for k, v in FLOW.items() if k != "back"},
            "with a subagent twice and two backs": {
                **FLOW,
                "order": ["a", "b", "a", "b"],
                "back": [
                    {"from": 2, "to": 1, "while": "more"},
                    {"from": 4, "to": 3, "while": "  **again** "},
                ],
            },
        }.items():
            with self.subTest(what=what):
                # Given: hooks/lanes.json holding a flow in its form
                self.laid_with(flow)
                # When: it is read
                # Then: the flow is read as written, beside the lanes
                self.assertEqual(lanes_json.laid(self.plugin), {"flow": flow, **LAID})

    def test_a_flow_out_of_its_form_stops_saying_what_is_wrong(self):
        back = FLOW["back"][0]
        for what, flow, named in (
            ("no object", [], "$.flow: expected an object"),
            ("no orchestrator", {**FLOW, "orchestrator": None}, "$.flow.orchestrator"),
            ("step 0", {**FLOW, "step": 0}, "$.flow.step: expected a number of at least 1"),
            ("an empty order", {**FLOW, "order": []}, "$.flow.order: expected at least 1"),
            (
                "a from of no position",
                {**FLOW, "back": [{**back, "from": "changelog-reviewer"}]},
                ".back[0].from: expected",
            ),
            (
                "a to of position 0",
                {**FLOW, "back": [{**back, "to": 0}]},
                ".back[0].to: expected a number of at least 1",
            ),
            ("an empty while", {**FLOW, "back": [{**back, "while": ""}]}, ".back[0].while"),
            ("a key beside", {**FLOW, "x": 1}, "$.flow: expected only the keys"),
            (
                "the orchestrator in its order",
                {**FLOW, "order": ["notes-lead", *FLOW["order"]]},
                "gives a flow whose order names its orchestrator notes-lead",
            ),
            (
                "a from past its order",
                {**FLOW, "back": [{**back, "from": 3}]},
                "gives a flow whose back names position 3, which its order of 2 does not have",
            ),
            (
                "a from and a to past its order",
                {**FLOW, "back": [{**back, "from": 4, "to": 3}]},
                "gives a flow whose back names position 4, which its order of 2 does not have",
            ),
            (
                "a to past its order",
                {**FLOW, "back": [{**back, "from": 2, "to": 3}]},
                "gives a flow whose back names position 3, which its order of 2 does not have",
            ),
            (
                "a to after its from",
                {**FLOW, "back": [{**back, "from": 1, "to": 2}]},
                (
                    "gives a flow whose back from position 1 goes to position 2, which does not"
                    " come before it"
                ),
            ),
            (
                "a to the same as its from",
                {**FLOW, "back": [{**back, "to": 2}]},
                (
                    "gives a flow whose back from position 2 goes to position 2, which does not"
                    " come before it"
                ),
            ),
            (
                "two backs from one position",
                {**FLOW, "back": [back, back]},
                "gives a flow with two backs from position 2",
            ),
            (
                "a while over two lines",
                {**FLOW, "back": [{**back, "while": "more\nentries"}]},
                "gives a flow whose back from position 2 answers a while of more than one line",
            ),
            (
                "a while ending in a line break",
                {**FLOW, "back": [{**back, "while": "more\r"}]},
                "answers a while of more than one line",
            ),
        ):
            with self.subTest(what=what):
                # Given: hooks/lanes.json holding a flow out of its form
                self.laid_with(flow)
                # When: it is read
                # Then: it stops, saying what is wrong
                with self.assertRaises(ValueError) as stop:
                    lanes_json.laid(self.plugin)
                self.assertIn(named, str(stop.exception))
                self.assertTrue(str(stop.exception).startswith("hooks/lanes.json "))

    def test_the_flows_lane_laid_where_the_flow_is_not_stops(self):
        lane = {"lane": "follow_flow", "takes": []}
        for what, flow, name, number in (
            ("no flow", None, "notes-lead", 1),
            ("another subagent", FLOW, "changelog-writer", 1),
            ("another step", FLOW, "notes-lead", 2),
        ):
            with self.subTest(what=what):
                # Given: hooks/lanes.json laying follow_flow on the step of the subagent
                given = {
                    "subagents": [{"name": name, "steps": [{"step": number, "lanes": [lane]}]}]
                }
                path = os.path.join(self.plugin, "hooks", "lanes.json")
                self.write_json(path, {**({"flow": flow} if flow else {}), **given})
                # When: it is read
                # Then: it stops, naming the lane
                with self.assertRaises(ValueError) as stop:
                    lanes_json.laid(self.plugin)
                on = f"follow_flow on step {number} of {name}"
                said = f"hooks/lanes.json lays {on}, where no flow is laid"
                self.assertEqual(str(stop.exception), said)

    def test_the_froms_are_the_subagents_at_the_from_of_each_back_once_each(self):
        # Given: a flow naming the reviewer twice, each the from of a back, and no flow
        flow = {
            **FLOW,
            "order": ["w", "r", "w", "r"],
            "back": [{"from": 2, "to": 1, "while": "x"}, {"from": 4, "to": 3, "while": "y"}],
        }
        # When: its froms are read
        # Then: each is named once, and none of no flow
        self.assertEqual(lanes_json.froms(flow), ["r"])
        self.assertEqual(lanes_json.froms(None), [])


if __name__ == "__main__":
    unittest.main()

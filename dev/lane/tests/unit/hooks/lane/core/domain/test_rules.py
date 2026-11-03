"""The rules laid in a plugin, its hooks/lanes.json in the shape of a proposal's subagents and its
routes: written by lay.py write and read by the guard, anything out of that shape refused, saying
where."""

import json
import os
import unittest

import helpers
from helpers import rules


def laid(lane: str, takes: list) -> str:
    """hooks/lanes.json laying the lane, taking the things, on step 2 of writer."""
    steps = [{"step": 2, "lanes": [{"lane": lane, "takes": takes}]}]
    return json.dumps({"subagents": [{"name": "writer", "steps": steps}]})


class TestRead(helpers.PluginTest):
    def test_the_lanes_laid_are_read_by_subagent_and_step(self):
        # Given: the README's lanes laid in writer
        self.lay()
        # When: the rules are read, and writer's lanes among them
        laid = rules.read(self.plugin)
        # Then: each lane comes with its step and what it takes
        self.assertEqual(
            rules.of(laid, "writer"),
            [
                rules.Laid(2, "run_only", ["git log --oneline"]),
                rules.Laid(3, "write_only", ["CHANGELOG.md"]),
            ],
        )

    def test_a_subagent_laid_with_no_lanes_has_none(self):
        # Given: the README's lanes laid in writer
        self.lay()
        # When: the lanes of another subagent are asked for
        # Then: there are none
        self.assertIsNone(rules.of(rules.read(self.plugin), "reviewer"))

    def test_each_subagents_lanes_are_read_by_its_name_alone(self):
        # Given: lanes laid in author and in writer, author listed first
        steps = [{"step": 2, "lanes": [{"lane": "run_only", "takes": ["ls"]}]}]
        given = {
            "subagents": [
                {"name": "author", "steps": steps},
                {"name": "writer", "steps": helpers.STEPS},
            ]
        }
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), given)
        # When: writer's lanes are asked for
        # Then: they are writer's
        found = rules.of(rules.read(self.plugin), "writer")
        self.assertEqual([g.takes for g in found or []], [["git log --oneline"], ["CHANGELOG.md"]])

    def test_a_take_of_one_character_and_no_subagent_left_are_read(self):
        for given in (
            json.loads(laid("run_only", ["x"])),
            {"subagents": [], "routes": helpers.ROUTES},
        ):
            with self.subTest(given=given):
                # Given: a lane taking one character, or no subagent with lanes beside the
                # routes, as once every subagent's lanes are gone
                self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), given)
                # When: it is read
                # Then: it is read as it was given
                self.assertEqual(rules.read(self.plugin), given)

    def test_a_file_that_cannot_be_read_is_refused_saying_why(self):
        path = os.path.join(self.plugin, "hooks", "lanes.json")
        for text, why in (
            (None, "hooks/lanes.json is not there"),
            ("{", "hooks/lanes.json holds no JSON"),
            ("[]", "hooks/lanes.json is out of its shape at $: expected an object"),
            ('{"subagents": [{"name": "writer", "steps": []}]}', "$.subagents[0].steps"),
            (laid("hands_off", ["git commit"]), "$.subagents[0].steps[0].lanes[0].lane"),
            (laid("run_only", [""]), "$.subagents[0].steps[0].lanes[0].takes[0]"),
            (laid("run_only", []), "$.subagents[0].steps[0].lanes[0].takes"),
        ):
            with self.subTest(text=text):
                # Given: hooks/lanes.json not there, not JSON, not an object, a subagent of no
                # step, a lane lane does not lay, a take empty, or a lane taking nothing
                if text is not None:
                    self.write(path, text)
                # When: it is read
                with self.assertRaises(ValueError) as refused:
                    rules.read(self.plugin)
                # Then: it is refused, saying why and where
                self.assertIn(why, str(refused.exception))


class TestRoutes(helpers.PluginTest):
    def test_the_routes_schema_is_the_one_docs_routes_md_gives(self):
        # Given: the routes' JSON Schema docs/routes.md gives under The routes
        with open(os.path.join(helpers.LANE, "docs", "routes.md"), encoding="utf-8") as f:
            text = f.read().split("## The routes")[1].split("\n## ")[0]
        shown = json.loads(text.split("```json\n")[1].split("```")[0])
        # When: lane's is read
        # Then: they are the same
        self.assertEqual(rules.ROUTES, shown)

    def test_the_routes_laid_are_read_back_and_none_where_none_are(self):
        # Given: the routes laid, and then the README's lanes alone
        self.route()
        # When: the routes are read
        # Then: they are docs/routes.md's, and none once the lanes alone are laid
        self.assertEqual(rules.routes_of(rules.read(self.plugin)), helpers.ROUTES)
        self.lay()
        self.assertIsNone(rules.routes_of(rules.read(self.plugin)))

    def test_routes_out_of_their_shape_are_refused(self):
        path = os.path.join(self.plugin, "hooks", "lanes.json")
        for routes, why in (
            ({**helpers.ROUTES, "routes": helpers.ROUTES["routes"][:1]}, "$.routes.routes"),
            ({**helpers.ROUTES, "step": 0}, "$.routes.step"),
            (
                {**helpers.ROUTES, "routes": [{"from": "a", "on": "More"}] * 2},
                "$.routes.routes[0].on",
            ),
        ):
            with self.subTest(routes=routes):
                # Given: routes of one route, of step 0, or of a result in capitals
                self.write_json(path, {**helpers.RULES, "routes": routes})
                # When: hooks/lanes.json is read
                with self.assertRaises(ValueError) as refused:
                    rules.read(self.plugin)
                # Then: it is refused, saying where
                self.assertIn(why, str(refused.exception))


class TestWrite(helpers.PluginTest):
    def test_the_lanes_written_are_read_back_as_they_were_given(self):
        # Given: a plugin with no hooks/ folder
        # When: the README's lanes are written into it
        rules.write(self.plugin, helpers.RULES["subagents"])
        # Then: they are read back the same, the file indented by two for its reader
        self.assertEqual(rules.read(self.plugin), helpers.RULES)
        text = self.read(os.path.join(self.plugin, "hooks", "lanes.json"))
        self.assertTrue(text.startswith('{\n  "subagents": [\n'), text)
        self.assertTrue(text.endswith("}\n"))

    def test_the_routes_are_written_beside_the_lanes(self):
        # Given: a plugin with no hooks/ folder
        # When: the README's lanes and docs/routes.md's routes are written into it
        rules.write(self.plugin, helpers.RULES["subagents"], helpers.ROUTES)
        # Then: both are read back
        self.assertEqual(rules.read(self.plugin), {**helpers.RULES, "routes": helpers.ROUTES})

    def test_a_take_is_written_as_it_is_given(self):
        # Given: a lane taking a command of a non-ASCII word
        steps = [{"step": 2, "lanes": [{"lane": "run_only", "takes": ["echo café"]}]}]
        # When: it is written
        rules.write(self.plugin, [{"name": "writer", "steps": steps}])
        # Then: the file holds the word as it is
        self.assertIn("echo café", self.read(os.path.join(self.plugin, "hooks", "lanes.json")))


class TestGives(unittest.TestCase):
    def test_the_results_are_the_routes_ons_or_done_with_a_lane_of_the_end(self):
        for routes, name, kinds, ons in (
            (helpers.ROUTES, "reviewer", [], ["more", "good"]),
            (helpers.ROUTES, "writer", ["end_when"], ["written"]),
            (helpers.ROUTES, "lead", ["every_item"], ["done"]),
            (None, "writer", ["run_only", "read_whole"], ["done"]),
            (None, "writer", ["run_only"], []),
        ):
            with self.subTest(name=name, kinds=kinds):
                # Given: the routes or none, and the subagent's lanes of the kinds
                # When: the results it gives are read
                # Then: they are the routes' from it, or done where none is and a lane is checked
                # at the end, or none
                self.assertEqual(rules.gives(routes, name, kinds), ons)


class TestAdapters(helpers.PluginTest):
    def test_a_subagents_and_a_lanes_adapters_are_read(self):
        # Given: writer with a values adapter, and every_item read by an items adapter
        lane = {"lane": "every_item", "takes": ["r.md"], "adapter": "hooks/adapters/items-f.py"}
        agent = {
            "name": "writer",
            "adapter": "hooks/adapters/values-w.py",
            "steps": [{"step": 3, "lanes": [lane]}],
        }
        author = {"name": "author", "steps": [{"step": 1, "lanes": [lane]}]}
        self.write_json(
            os.path.join(self.plugin, "hooks", "lanes.json"), {"subagents": [author, agent]}
        )
        laid = rules.read(self.plugin)
        # When: they are read
        # Then: each is given, and none for a subagent laid with none, author before writer
        # naming none
        self.assertEqual(rules.adapter_of(laid, "writer"), "hooks/adapters/values-w.py")
        self.assertIsNone(rules.adapter_of(laid, "author"))
        self.assertIsNone(rules.adapter_of(laid, "reviewer"))
        self.assertEqual(
            rules.of(laid, "writer"),
            [rules.Laid(3, "every_item", ["r.md"], "hooks/adapters/items-f.py")],
        )


if __name__ == "__main__":
    unittest.main()

"""The ports lane reads a plugin's text at, each by its JSON in and out, a JSON Schema each, and
lane's one reading of it: the values a subagent started from, the items of an input and the move a
script printed."""

import json
import unittest

from helpers import ports, schema

# A run's JSON as a prompt or a script gives it, naming the work and a checklist.
RUN = {"work": ["a.md", "b.md"], "checklist": "c.md"}


def values(texts: list) -> dict:
    """The run's values lane reads at the values port in the texts."""
    return ports.read("values", {"texts": texts})["values"]


class TestValues(unittest.TestCase):
    def test_a_json_object_gives_each_text_and_each_list_of_texts_under_its_name(self):
        # Given: a prompt that is a JSON object of a list and a text
        # When: the values are read
        # Then: the list stands for its texts, the text for itself
        self.assertEqual(
            values([json.dumps(RUN)]), {"work": ["a.md", "b.md"], "checklist": ["c.md"]}
        )

    def test_the_later_json_gives_a_name_over_the_earlier(self):
        # Given: a prompt naming the work, then a script's print naming it again and more
        texts = ['{"work": "a.md"}', '{"work": "b.md", "has": "h.md"}']
        # When: the values are read
        # Then: the later gives the work, the earlier what the later leaves
        self.assertEqual(values(texts), {"work": ["b.md"], "has": ["h.md"]})

    def test_json_printed_over_several_lines_is_read_whole(self):
        # Given: a print of one JSON object indented over lines, with an object of its own inside
        text = json.dumps({"work": "a.md", "item": {"x": "y"}}, indent=2)
        # When: the values are read
        # Then: the object's names alone are read
        self.assertEqual(values([text]), {"work": ["a.md"]})

    def test_a_print_of_lines_gives_each_line_that_is_a_json_object(self):
        # Given: a print of a line of words, a line of a JSON list and a line of a JSON object
        text = 'Started.\n["x"]\n{"work": "a.md"}'
        # When: the values are read
        # Then: the line that is an object gives its names
        self.assertEqual(values([text]), {"work": ["a.md"]})

    def test_a_value_neither_a_text_nor_a_list_gives_nothing(self):
        # Given: names of a number, an object and null, and a list of texts and a number
        text = '{"n": 1, "o": {}, "z": null, "l": ["a.md", 2]}'
        # When: the values are read
        # Then: the list gives its texts alone, and the others nothing
        self.assertEqual(values([text]), {"l": ["a.md"]})

    def test_text_that_holds_no_json_object_gives_nothing(self):
        for text in ("Do your steps.", "", '["a.md"]', "1"):
            with self.subTest(text=text):
                # Given: a prompt of words, of nothing, of a JSON list or a number
                # When: the values are read
                # Then: none is given
                self.assertEqual(values([text]), {})


class TestSchemas(unittest.TestCase):
    def test_lanes_reading_of_each_port_gives_what_its_out_holds(self):
        for port, given in (
            ("values", {"texts": [json.dumps(RUN), "x"]}),
            ("items", {"input": "r.md", "text": "- B-1: fix\n- plain\n"}),
            ("move", {"output": 'Next:\n{"tool": "Bash", "input": {"command": "ls"}}'}),
            ("move", {"output": "done"}),
        ):
            with self.subTest(port=port, given=given):
                # Given: the port's JSON in, held to its schema
                self.assertIsNone(schema.held(ports.PORTS[port]["in"], given))
                # When: lane reads it
                found = ports.read(port, given)
                # Then: what it gives back holds to the port's out
                self.assertIsNone(schema.held(ports.PORTS[port]["out"], found), found)

    def test_an_answer_out_of_a_ports_out_is_found_with_its_point(self):
        for port, found, point in (
            ("values", {"values": {"work": "a.md"}}, "$.values.work: expected an array"),
            ("values", {"values": {"work": [1]}}, "$.values.work[0]: expected a string"),
            ("items", {"items": "B-1"}, "$.items: expected an array"),
            ("items", {}, '$: expected the key "items"'),
            ("move", {"move": {"tool": "Bash"}}, "$.move: expected"),
            ("move", {"move": None, "more": 1}, 'found the key "more"'),
        ):
            with self.subTest(port=port, found=found):
                # Given: an answer out of the port's out
                # When: it is held to it
                out = schema.held(ports.PORTS[port]["out"], found)
                # Then: the point it is out by is found
                self.assertIn(point, out.told() if out else "")


class TestMove(unittest.TestCase):
    def test_the_move_is_the_tool_call_itself_or_none(self):
        line = '{"tool": "Agent", "input": {"prompt": "p"}}'
        for output, move in (
            (f"Next move:\n{line}\n", {"tool": "Agent", "input": {"prompt": "p"}}),
            ('{"tool": 1, "input": {}}', None),
            ('{"returned": "r.md"}', None),
        ):
            with self.subTest(output=output):
                # Given: a print holding a tool call as one JSON line, one of no tool's name, or
                # none
                # When: lane reads it at the move port
                # Then: it is the tool call, or none
                self.assertEqual(ports.read("move", {"output": output}), {"move": move})


class TestItems(unittest.TestCase):
    def test_the_items_are_the_ids_top_level_list_items_begin_with(self):
        # Given: a review of two items keyed by IDs, a nested one and one of no ID
        text = "- B-1: fix\n  - B-9: nested\n1. **R33** pass\n- fix the hook\n"
        # When: lane reads it at the items port
        # Then: they are the IDs of the top-level items, in order
        self.assertEqual(
            ports.read("items", {"input": "r.md", "text": text}), {"items": ["B-1", "R33"]}
        )


if __name__ == "__main__":
    unittest.main()

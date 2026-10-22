"""What a subagent started from: a take written `{<name>}` stands for the value under that name in
the JSON the subagent starts from, its prompt and what a script start_with takes prints, the later
over the earlier; a list for each of its texts, a text for itself."""

import json
import unittest

import helpers
from helpers import call, started

# A run's JSON as a prompt or a script gives it, naming the work and a checklist.
RUN = {"work": ["a.md", "b.md"], "checklist": "c.md"}
# A run's values as they are put in: the work of two files, an empty list and a test.
VALUES = {"work": ["a.md", "b.md"], "none": [], "test": ["make"]}


class TestNames(unittest.TestCase):
    def test_each_name_written_in_braces_is_named_once_in_order(self):
        # Given: takes fixed and given for each run, a name given twice
        takes = ["CHANGELOG.md", "{work}", "{sent back}", "{work}"]
        # When: the names are read
        # Then: each name in braces is named once, in the order taken
        self.assertEqual(started.names(takes), ["work", "sent back"])

    def test_a_take_braces_do_not_wrap_whole_names_nothing(self):
        for take in ("x{work}", "{work}.md", "{}", "{a}{b}", "work"):
            with self.subTest(take=take):
                # Given: a take that braces do not wrap whole, around a name
                # When: the names are read
                # Then: it names nothing, being fixed
                self.assertEqual(started.names([take]), [])


class TestValues(unittest.TestCase):
    def test_a_json_object_gives_each_text_and_each_list_of_texts_under_its_name(self):
        # Given: a prompt that is a JSON object of a list and a text
        # When: the values are read
        # Then: the list stands for its texts, the text for itself
        self.assertEqual(
            started.values([json.dumps(RUN)]), {"work": ["a.md", "b.md"], "checklist": ["c.md"]}
        )

    def test_the_later_json_gives_a_name_over_the_earlier(self):
        # Given: a prompt naming the work, then a script's print naming it again and more
        texts = ['{"work": "a.md"}', '{"work": "b.md", "has": "h.md"}']
        # When: the values are read
        # Then: the later gives the work, the earlier what the later leaves
        self.assertEqual(started.values(texts), {"work": ["b.md"], "has": ["h.md"]})

    def test_json_printed_over_several_lines_is_read_whole(self):
        # Given: a print of one JSON object indented over lines, with an object of its own inside
        text = json.dumps({"work": "a.md", "item": {"x": "y"}}, indent=2)
        # When: the values are read
        # Then: the object's names alone are read
        self.assertEqual(started.values([text]), {"work": ["a.md"]})

    def test_a_print_of_lines_gives_each_line_that_is_a_json_object(self):
        # Given: a print of a line of words, a line of a JSON list and a line of a JSON object
        text = 'Started.\n["x"]\n{"work": "a.md"}'
        # When: the values are read
        # Then: the line that is an object gives its names
        self.assertEqual(started.values([text]), {"work": ["a.md"]})

    def test_a_value_neither_a_text_nor_a_list_gives_nothing(self):
        # Given: names of a number, an object and null, and a list of texts and a number
        text = '{"n": 1, "o": {}, "z": null, "l": ["a.md", 2]}'
        # When: the values are read
        # Then: the list gives its texts alone, and the others nothing
        self.assertEqual(started.values([text]), {"l": ["a.md"]})

    def test_text_that_holds_no_json_object_gives_nothing(self):
        for text in ("Do your steps.", "", '["a.md"]', "1"):
            with self.subTest(text=text):
                # Given: a prompt of words, of nothing, of a JSON list or a number
                # When: the values are read
                # Then: none is given
                self.assertEqual(started.values([text]), {})


class TestResolved(unittest.TestCase):
    def test_fixed_takes_are_checked_once_as_they_are(self):
        # Given: takes all fixed
        # When: they are put in
        # Then: the lane is checked once on them
        self.assertEqual(started.resolved(["x", "y"], VALUES, 1), [["x", "y"]])

    def test_a_list_in_a_place_taking_the_rest_stands_for_its_texts_side_by_side(self):
        # Given: a lane of one place taking a fixed thing and `{work}`, its place taking the rest
        # When: it is put in
        # Then: the lane is checked once on every text of the work
        self.assertEqual(started.resolved(["x", "{work}"], VALUES, 0), [["x", "a.md", "b.md"]])

    def test_a_list_in_a_place_taking_one_thing_is_checked_once_for_each_text(self):
        # Given: test_after taking `{work}` for its output, a place of one thing, then a test
        # When: it is put in
        # Then: the lane is checked for each output in turn
        self.assertEqual(
            started.resolved(["{work}", "{test}"], VALUES, 1),
            [["a.md", "make"], ["b.md", "make"]],
        )

    def test_an_empty_list_in_a_place_taking_one_thing_is_checked_on_nothing(self):
        # Given: an output given as an empty list
        # When: it is put in
        # Then: the lane is checked on nothing
        self.assertEqual(started.resolved(["{none}", "make"], VALUES, 1), [])

    def test_an_empty_list_in_a_place_taking_the_rest_stands_for_nothing(self):
        # Given: write_only taking `{none}`, an empty list
        # When: it is put in
        # Then: the lane is checked once, taking nothing
        self.assertEqual(started.resolved(["{none}"], VALUES, 0), [[]])


class TestTold(unittest.TestCase):
    def test_the_value_is_told_after_its_name(self):
        for texts, told in (
            (["a.md", "b.md"], "`{work}` is `a.md`, `b.md`."),
            (["a.md"], "`{work}` is `a.md`."),
            ([], "`{work}` is an empty list."),
        ):
            with self.subTest(texts=texts):
                # Given: the run's value of `{work}`
                # When: it is told
                # Then: each text stands in quotes of its own after the name
                self.assertEqual(started.told("work", texts), told)


class TestStarted(helpers.PluginTest):
    def texts(self):
        """What the subagent started from, the calls that run `start.py` taken as its script."""

        def runs(made: call.Call) -> bool:
            return made.what[:1] == [["python3", "start.py"]]

        return started.texts(self.event("ls"), runs)

    def test_the_prompt_and_the_print_of_each_script_run_are_read_in_order(self):
        # Given: a record begun by a prompt of JSON, then a call of another command, the script
        # run, and another command
        calls = [
            ("Bash", {"command": "ls"}, "x.md"),
            ("Bash", {"command": "python3 start.py"}, '{"work": "a.md"}'),
            ("Bash", {"command": "cat x.md"}, "text"),
        ]
        self.record(calls, '{"run": "/r"}')
        # When: what the subagent started from is read
        # Then: it is the prompt, then what the script printed
        self.assertEqual(self.texts(), ['{"run": "/r"}', '{"work": "a.md"}'])

    def test_no_record_found_is_not_known(self):
        # Given: no record of the subagent
        # When: what it started from is read
        # Then: it is not known
        self.assertIsNone(self.texts())


if __name__ == "__main__":
    unittest.main()

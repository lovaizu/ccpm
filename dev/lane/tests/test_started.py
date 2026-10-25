"""What a subagent started from, for a take written `{<name>}`: the texts it started from, its prompt
and what a script start_with takes prints, whose values the values port reads; those values put in
the places of a lane's sentence, and told."""

import unittest

import helpers
from helpers import call, started

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


class TestPut(unittest.TestCase):
    def test_the_runs_texts_are_put_in_for_each_take_given_for_each_run(self):
        # Given: a place of a fixed thing and `{work}`, and a place of `{test}`
        # When: the run's values are put in
        # Then: each place holds its texts in the order taken
        self.assertEqual(
            started.put([["x", "{work}"], ["{test}"]], VALUES), [["x", "a.md", "b.md"], ["make"]]
        )

    def test_a_place_of_a_take_not_given_holds_none(self):
        # Given: a place of `{other}`, which the run does not give, and one of `{none}`, given empty
        # When: the run's values are put in
        # Then: the first holds None, told apart from the second's empty list
        self.assertEqual(started.put([["{other}", "x"], ["{none}"]], VALUES), [None, []])


class TestResolved(unittest.TestCase):
    def test_fixed_takes_are_checked_once_as_they_are(self):
        # Given: one place of two fixed things
        # When: the lists checked on are made
        # Then: the lane is checked once on them
        self.assertEqual(started.resolved([["x", "y"]], 0), [["x", "y"]])

    def test_a_list_in_a_place_taking_one_thing_is_checked_once_for_each_text(self):
        # Given: test_after's two places, its output, a place of one thing, holding two texts
        # When: the lists checked on are made
        # Then: the lane is checked for each output in turn
        self.assertEqual(
            started.resolved([["a.md", "b.md"], ["make"]], 1),
            [["a.md", "make"], ["b.md", "make"]],
        )


class TestTold(unittest.TestCase):
    def test_the_value_is_told_after_its_name(self):
        for texts, told in (
            (["a.md", "b.md"], "`{work}` is `a.md`, `b.md`."),
            (["a.md"], "`{work}` is `a.md`."),
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
            # Whether the call runs `python3 start.py`, as the script start_with takes.
            return made.what[:1] == [["python3", "start.py"]]

        event = self.event("ls")
        return started.texts(helpers.record.entries(event), event["cwd"], runs)

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

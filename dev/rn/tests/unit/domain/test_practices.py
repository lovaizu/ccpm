"""domain/practices.py, a kind's best practice as rn's roles take it: where it lies, its intents in
the groups the evaluators judge, the kind of a deliverable's turn of how it reads, and the steps of
its practices in the form of Lane's steps port."""

from __future__ import annotations

import os
import unittest

import helpers
from helpers import practices

DATA = {
    "goal": "g",
    "inputs": [],
    "preconditions": [],
    "necessary_conditions": [
        {"id": "Q1", "about": "a", "what": "?"},
        {"id": "Q2", "about": "b", "what": "?"},
        {"id": "Q3", "about": "the whole, a", "what": "?"},
        {"id": "Q4", "about": "c, b", "what": "?"},
        {"id": "Q5", "about": "a, c", "what": "?"},
    ],
    "practices": [
        {
            "intent": "Q1",
            "thinking": "t",
            "steps": [{"text": "Run it.", "trace": {"action": "run", "takes": ["{tests}"]}}],
        },
        {"intent": "Q2", "thinking": "t", "steps": []},
        {
            "intent": "Q3",
            "thinking": "t",
            "steps": [
                {"text": "Where so, judge it."},
                {"text": "Read it.", "trace": {"action": "read", "takes": ["{inputs}"]}},
            ],
        },
        {
            "intent": "Q4",
            "thinking": "t",
            "steps": [{"text": "Make it.", "trace": {"action": "write", "takes": ["{proposal}"]}}],
        },
        {"intent": "Q5", "thinking": "t", "steps": []},
    ],
}


class Found(helpers.testing.FolderTest):
    def test_the_runs_own_first_then_rns_then_an_earlier_runs_the_newest_first(self):
        # Given: rn's own readme, and none of the kind man-page
        run = os.path.join(".rn", "20261109-b")
        own = os.path.join(practices.OWN, "readme", "best-practice.json")
        # When: rn looks for each
        # Then: rn's own readme, and no man-page
        self.assertEqual(practices.found("readme", run), own)
        self.assertIsNone(practices.found("man-page", run))
        # And: an earlier run's, the newest of them, once two runs made one
        for name in ("20261107-a", "20261108-a"):
            self.write(
                os.path.join(".rn", name, "best-practices", "man-page", "best-practice.json"), "{}"
            )
        newest = os.path.join(
            ".", ".rn", "20261108-a", "best-practices", "man-page", "best-practice.json"
        )
        self.assertEqual(practices.found("man-page", run), newest)
        # And: the run's own before every other, rn's own readme among them
        for kind in ("man-page", "readme"):
            mine = os.path.join(run, "best-practices", kind, "best-practice.json")
            self.write(mine, "{}")
            self.assertEqual(practices.found(kind, run), mine)

    def test_a_best_practice_is_held_to_its_form(self):
        self.write_json("bp.json", {"goal": "g"})
        with self.assertRaises(helpers.files.Unreadable) as stop:
            practices.read("bp.json")
        self.assertIn("bp.json is out of its form", str(stop.exception))
        self.write_json("bp.json", DATA)
        self.assertEqual(
            practices.intents(practices.read("bp.json")), ["Q1", "Q2", "Q3", "Q4", "Q5"]
        )


class Groups(unittest.TestCase):
    def test_intents_of_a_part_in_common_go_together_and_the_whole_alone(self):
        # Given: Q1 and Q5 of a, Q2 and Q4 of b, Q4 and Q5 of c, joining every one, Q3 of the whole
        # When: they're grouped
        # Then: the whole alone, after the group of its parts, in the order of each first intent
        self.assertEqual(practices.groups(DATA), [["Q1", "Q2", "Q4", "Q5"], ["Q3"]])

    def test_each_part_its_own_group(self):
        data = {"necessary_conditions": [{"id": "Q1", "about": "b"}, {"id": "Q2", "about": "a"}]}
        self.assertEqual(practices.groups(data), [["Q1"], ["Q2"]])


class Reading(unittest.TestCase):
    def test_code_reads_by_refactor_code_and_a_document_by_refactor_doc(self):
        self.assertEqual(
            [practices.reading(k) for k in ("code", "plugin", "readme", "man-page")],
            ["refactor-code", "refactor-code", "refactor-doc", "refactor-doc"],
        )


class Steps(unittest.TestCase):
    def test_each_practice_with_steps_a_list_each_trace_its_lane(self):
        found = practices.steps(DATA, None)
        self.assertEqual(
            found,
            [
                {
                    "list": "Q1",
                    "steps": [
                        {"says": "Run it.", "lanes": [{"lane": "run_step", "takes": ["{tests}"]}]}
                    ],
                },
                {
                    "list": "Q3",
                    "steps": [
                        {"says": "Where so, judge it.", "lanes": []},
                        {
                            "says": "Read it.",
                            "lanes": [{"lane": "read_whole", "takes": ["{inputs}"]}],
                        },
                    ],
                },
                {
                    "list": "Q4",
                    "steps": [
                        {
                            "says": "Make it.",
                            "lanes": [{"lane": "write_step", "takes": ["{proposal}"]}],
                        }
                    ],
                },
            ],
        )

    def test_only_the_intents_chosen(self):
        self.assertEqual([x["list"] for x in practices.steps(DATA, ["Q4", "Q2"])], ["Q4"])

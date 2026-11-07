"""domain/runs.py, a run's files: its folder's name, what its temporary folder keeps for this
repository, the runs listed, its turns and rounds, and where a round stands."""

from __future__ import annotations

import os
from unittest import mock

import helpers
from helpers import RUN, runs


def made(made=("README.md",), open_=()):
    return {"made": list(made), "decided": [], "open": list(open_)}


def answers(met=(), not_met=(), open_=()):
    return {
        "met": [{"question": q, "lines": ["x"]} for q in met],
        "not_met": [{"question": q, "lacks": "l"} for q in not_met],
        "open": [{"question": q, "about": "a", "what": "w"} for q in open_],
    }


class Names(helpers.RunTest):
    def test_a_new_run_is_named_by_the_date_and_its_first_words(self):
        with mock.patch.object(runs, "today", return_value="20261108"):
            self.assertEqual(
                runs.new("Tidy should show what it would move!"),
                ".rn/20261108-tidy-should-show-what-it",
            )
            self.assertEqual(runs.new("¿?"), ".rn/20261108-work")
            # And: a name taken, by a folder or a change waiting, gets the next number
            os.makedirs(".rn/20261108-a")
            self.assertEqual(runs.new("a"), ".rn/20261108-a-2")
            runs.keep(".rn/20261108-a-2", runs.CHANGE, {})
            self.assertEqual(runs.new("a"), ".rn/20261108-a-3")

    def test_today_is_the_date_as_a_name_begins(self):
        self.assertRegex(runs.today(), r"^20[0-9]{6}$")


class Kept(helpers.RunTest):
    def test_kept_for_this_repository_alone(self):
        # Given: a change kept for the run
        runs.keep(RUN, runs.CHANGE, {"change": 1})
        self.assertEqual(runs.pending(RUN), {"change": 1})
        self.assertEqual(runs.handed(), RUN)
        # When: another repository keeps one under the same run's name
        path = os.path.join(runs.temporary(RUN), runs.CHANGE)
        self.write_json(path, {"repo": "/elsewhere", "data": {}})
        # Then: this one finds none
        self.assertIsNone(runs.pending(RUN))
        self.assertIsNone(runs.handed())
        self.write(path, "{")
        self.assertIsNone(runs.kept(RUN, runs.CHANGE))

    def test_the_change_handed_last_where_two_are(self):
        runs.keep(".rn/a", runs.CHANGE, {})
        os.utime(os.path.join(runs.temporary(".rn/a"), runs.CHANGE), (1, 1))
        runs.keep(".rn/b", runs.CHANGE, {})
        self.assertEqual(runs.handed(), ".rn/b")

    def test_drop_removes_what_is_kept(self):
        runs.keep(RUN, runs.EDIT, 1)
        runs.drop(RUN, runs.EDIT, runs.CHANGE)
        self.assertIsNone(runs.kept(RUN, runs.EDIT))

    def test_the_runs_with_a_tree_in_order(self):
        self.lays(helpers.walkthrough(), ".rn/b")
        self.lays(helpers.walkthrough(), ".rn/a")
        os.makedirs(".rn/c")
        self.assertEqual(runs.listed(), [".rn/a", ".rn/b"])


class Turns(helpers.RunTest):
    def test_a_turn_of_each_kind_numbered_in_the_run(self):
        self.assertIsNone(runs.turn_of(RUN, "README.md", False))
        first = runs.new_turn(RUN, "README.md", False)
        self.assertEqual(first, os.path.join(RUN, "turns", "01-readme-md"))
        os.makedirs(first)
        second = runs.new_turn(RUN, "README.md", True)
        self.assertEqual(second, os.path.join(RUN, "turns", "02-readme-md-reading"))
        os.makedirs(second)
        self.assertEqual(runs.turn_of(RUN, "README.md", False), first)
        self.assertEqual(runs.turn_of(RUN, "README.md", True), second)
        self.assertEqual(runs.rounds(None), [])
        self.assertEqual(runs.next_round(first), os.path.join(first, "01"))

    def test_where_a_round_stands(self):
        round_ = os.path.join(RUN, "turns", "01-readme-md", "01")
        groups = ["G1", "G2"]
        os.makedirs(round_)
        self.assertEqual(runs.outcome(round_, groups), "making")
        self.write_json(
            os.path.join(round_, runs.MADE),
            made(open_=[{"intent": "Q1", "about": "a", "what": "w"}]),
        )
        self.assertEqual(runs.outcome(round_, groups), "open")
        self.write_json(os.path.join(round_, runs.MADE), made())
        self.assertEqual(runs.outcome(round_, groups), "judging")
        self.write_json(os.path.join(round_, "evaluator-G1.json"), answers(met=["Q1"]))
        self.write_json(os.path.join(round_, "evaluator-G2.json"), answers(not_met=["Q2"]))
        self.write_json(os.path.join(round_, "evaluator-x.json"), answers())
        self.write_json(os.path.join(round_, "evaluator-G1-old.json"), answers(not_met=["Q1"]))
        self.assertEqual(runs.outcome(round_, groups), "more")
        self.assertEqual(runs.shortfalls(round_), [("Q2", "l")])
        self.write_json(os.path.join(round_, "evaluator-G1.json"), answers(open_=["Q1"]))
        self.assertEqual(runs.outcome(round_, groups), "open")
        self.assertEqual(runs.points(round_), [{"intent": "Q1", "about": "a", "what": "w"}])
        self.write_json(os.path.join(round_, "evaluator-G1.json"), answers(met=["Q1"]))
        self.write_json(os.path.join(round_, "evaluator-G2.json"), answers(met=["Q2"]))
        self.assertEqual(runs.outcome(round_, groups), "good")

    def test_the_points_of_the_generator_and_of_a_round_with_no_record(self):
        round_ = os.path.join(RUN, "turns", "01-readme-md", "01")
        os.makedirs(round_)
        self.assertEqual(runs.points(round_), [])
        self.write_json(
            os.path.join(round_, runs.MADE),
            made(open_=[{"intent": "Q2", "about": "b", "what": "v"}]),
        )
        self.assertEqual(runs.points(round_), [{"intent": "Q2", "about": "b", "what": "v"}])

"""How phases.py settles a work's rounds and checks the Answers of each, by the classes of its
contract: the phase by its table, one test for each rule; a round settled after one met or fell
short, its files kept apart; the shortfalls of a round, each joined to the decisions that serve its
question; and the Answers of the generator and of each run of the evaluator, every question
answered once with lines the work holds, and the result each gives."""

import json
import os
import unittest

import helpers
from helpers import TREE, files, met, phases, runs, short

RUN = helpers.RUN
VERIFICATION = os.path.join(RUN, "verification")
GENERATOR = os.path.join(VERIFICATION, "generator.json")
# The groups of the note's content questions, as practices.groups gives them.
CONTENT_GROUPS = [
    {"id": "G1", "questions": ["note/Q1"]},
    {"id": "G2", "questions": ["note/Q2"]},
    {"id": "G3", "questions": ["note/Q3"]},
]


def settled_round():
    """The next round of the run, settled, where one is left."""
    made = phases.settle(RUN)
    assert made is not None
    return made


class Phase(unittest.TestCase):
    """The phase table: whether a content round was made and on the design as it is, whether it met
    every question, and whether the last reading round since met every question."""

    def test_r1_no_content_round_yet_gives_content(self):
        self.assertEqual(phases.phase(None, True, "d"), "content")

    def test_r2_a_design_changed_since_the_content_round_gives_content(self):
        self.assertEqual(phases.phase({"design": "c", "met": True}, True, "d"), "content")

    def test_r3_a_content_round_that_fell_short_gives_content(self):
        self.assertEqual(phases.phase({"design": "d", "met": False}, None, "d"), "content")

    def test_r4_content_met_and_no_reading_round_gives_reading(self):
        self.assertEqual(phases.phase({"design": "d", "met": True}, None, "d"), "reading")

    def test_r5_content_met_and_a_reading_round_that_fell_short_gives_reading(self):
        self.assertEqual(phases.phase({"design": "d", "met": True}, False, "d"), "reading")

    def test_r6_content_and_reading_met_gives_none(self):
        self.assertIsNone(phases.phase({"design": "d", "met": True}, True, "d"))


class Serving(unittest.TestCase):
    def test_each_decision_that_reaches_the_question_in_the_trees_order(self):
        self.assertEqual(phases.serving(TREE, "note/Q2"), ["D2", "D3"])
        self.assertEqual(phases.serving(TREE, "note/Q3"), ["D1"])

    def test_a_join_that_comes_back_to_itself_is_followed_once(self):
        tree = {
            "decisions": [
                {"id": "D1", "contributes_to": ["D2"]},
                {"id": "D2", "contributes_to": ["D1", "Q1"]},
            ]
        }
        self.assertEqual(phases.serving(tree, "Q1"), ["D1", "D2"])

    def test_a_question_nothing_reaches(self):
        self.assertEqual(phases.serving(TREE, "note/Q9"), [])


class Settle(helpers.RoundsTest):
    def test_the_first_round_is_of_the_content_and_groups_its_questions(self):
        settled = settled_round()
        self.assertEqual(
            settled,
            {
                "round": 1,
                "phase": "content",
                "design": phases.design_hash(RUN),
                "groups": CONTENT_GROUPS,
                "content": None,
                "reading_met": None,
            },
        )
        self.assertEqual(self.round(), settled)

    def test_a_content_round_met_is_followed_by_a_reading_round_its_files_kept_apart(self):
        # Given: a content round whose every group met its question
        self.content_round(met("note/Q1"), met("note/Q2"), met("note/Q3"))
        # When: the next round is settled
        settled = settled_round()
        # Then: it reads, its one group asking how the note reads, and the round before lies in
        # verification/1/ with its Answers
        self.assertEqual(settled["phase"], "reading")
        self.assertEqual(settled["groups"], [{"id": "G1", "questions": ["refactor-doc/Q1"]}])
        self.assertEqual(
            (settled["round"], settled["content"], settled["reading_met"]),
            (2, {"design": phases.design_hash(RUN), "met": True}, None),
        )
        kept = os.path.join(VERIFICATION, "1")
        self.assertEqual(
            sorted(os.listdir(kept)),
            ["G1.json", "G2.json", "G3.json", "generator.json", "round.json"],
        )
        self.assertEqual(sorted(os.listdir(VERIFICATION)), ["1", "round.json"])

    def test_a_round_kept_into_a_folder_already_there_keeps_its_files(self):
        # Given: a content round met, and its folder verification/1/ made by a run that stopped
        self.content_round(met("note/Q1"), met("note/Q2"), met("note/Q3"))
        os.makedirs(os.path.join(VERIFICATION, "1"))
        # When: the next round is settled
        settled_round()
        # Then: the round before lies in verification/1/ with its Answers
        self.assertEqual(
            sorted(os.listdir(os.path.join(VERIFICATION, "1"))),
            ["G1.json", "G2.json", "G3.json", "generator.json", "round.json"],
        )

    def test_a_content_round_short_of_one_question_is_followed_by_content(self):
        self.content_round(met("note/Q1"), short("note/Q2"), met("note/Q3"))
        settled = settled_round()
        self.assertEqual((settled["phase"], settled["content"]["met"]), ("content", False))

    def test_a_content_round_whose_runs_did_not_all_answer_falls_short(self):
        self.content_round(met("note/Q1"), met("note/Q2"))
        self.assertEqual(settled_round()["phase"], "content")

    def test_answers_out_of_their_form_fall_short(self):
        self.content_round(met("note/Q1"), met("note/Q2"), {"met": []})
        self.assertEqual(settled_round()["phase"], "content")

    def test_a_design_changed_after_its_content_was_met_is_made_again(self):
        self.content_round(met("note/Q1"), met("note/Q2"), met("note/Q3"))
        self.write_json(
            os.path.join(RUN, "design-tree.json"), {**TREE, "goal": {"what": "x", "grounds": []}}
        )
        self.assertEqual(settled_round()["phase"], "content")

    def test_a_reading_round_short_or_met(self):
        # Given: a content round met, then a reading round short of its question
        self.content_round(met("note/Q1"), met("note/Q2"), met("note/Q3"))
        phases.settle(RUN)
        self.answers("G1.json", short("refactor-doc/Q1"))
        # When: the next is settled, it reads again, the content met kept
        again = settled_round()
        self.assertEqual(
            (again["phase"], again["content"]["met"], again["reading_met"]),
            ("reading", True, False),
        )
        # And: once that one is met, no round is left, and nothing is moved
        self.answers("G1.json", met("refactor-doc/Q1"))
        self.assertIsNone(phases.settle(RUN))
        self.assertEqual(self.round()["round"], 3)
        self.assertTrue(os.path.exists(os.path.join(VERIFICATION, "G1.json")))

    def test_a_reading_round_that_finds_what_the_work_says_must_change_falls_short(self):
        self.content_round(met("note/Q1"), met("note/Q2"), met("note/Q3"))
        phases.settle(RUN)
        self.answers(
            "G1.json",
            {**met("refactor-doc/Q1"), "open": [{"question": "refactor-doc/Q1", "what": "w"}]},
        )
        self.assertEqual(settled_round()["reading_met"], False)

    def test_a_work_not_in_its_rounds_has_none_due(self):
        for at in ("pin", "waits"):
            with self.subTest(at=at):
                self.lay_run([helpers.work(at=at)])
                with self.assertRaises(files.Unreadable) as raised:
                    phases.settle(RUN)
                self.assertEqual(
                    str(raised.exception), f"no round of note is due: the work is at {at}"
                )

    def test_a_design_file_missing_cannot_be_settled_on(self):
        os.remove(os.path.join(RUN, "design-tree.json"))
        with self.assertRaises(files.Unreadable):
            phases.settle(RUN)


class Shortfalls(helpers.RoundsTest):
    def test_each_question_not_met_and_each_point_open_in_the_runs_order(self):
        phases.settle(RUN)
        self.answers(
            "generator.json",
            {
                **met("note/Q1", "note/Q2", "note/Q3"),
                "open": [{"question": "note/Q2", "what": "which folder"}],
            },
        )
        self.answers("G1.json", met("note/Q1"))
        self.answers("G2.json", short("note/Q2"))
        self.assertEqual(
            phases.shortfalls(RUN, self.round()),
            [
                ("note/Q2", "note/Q2, left open: which folder"),
                ("note/Q2", "note/Q2: note/Q2 lacks"),
            ],
        )

    def test_none_where_no_round_was_settled_or_every_run_met(self):
        self.assertEqual(phases.shortfalls(RUN, None), [])
        self.content_round(met("note/Q1"), met("note/Q2"), met("note/Q3"))
        self.assertEqual(phases.shortfalls(RUN, self.round()), [])


class Where(helpers.RoundsTest):
    def test_none_before_the_first_round(self):
        self.assertEqual(phases.where(RUN), "none")

    def test_going_while_the_runs_have_not_all_answered(self):
        self.content_round(met("note/Q1"))
        self.assertEqual(phases.where(RUN), "going")

    def test_short_where_a_run_fell_short(self):
        self.content_round(met("note/Q1"), short("note/Q2"))
        self.assertEqual(phases.where(RUN), "short")

    def test_going_where_a_content_round_met_every_question(self):
        self.content_round(met("note/Q1"), met("note/Q2"), met("note/Q3"))
        self.assertEqual(phases.where(RUN), "going")

    def test_finished_where_a_reading_round_met_every_question(self):
        self.content_round(met("note/Q1"), met("note/Q2"), met("note/Q3"))
        phases.settle(RUN)
        self.answers("G1.json", met("refactor-doc/Q1"))
        self.assertEqual(phases.where(RUN), "finished")


class EvaluatorValues(unittest.TestCase):
    def test_a_run_out_of_ascii_is_written_as_it_is(self):
        settled = {"phase": "content", "groups": [{"id": "G1", "questions": ["note/Q1"]}]}
        (values,) = phases.evaluator_values("ノート", helpers.work(), settled)
        self.assertIn('"run": "ノート"', values)


class Check(helpers.RoundsTest):
    def setUp(self) -> None:
        super().setUp()
        phases.settle(RUN)

    def checked(self, name, data):
        """The check of the Answers of the name, written as data."""
        self.answers(name, data)
        return phases.check(RUN, os.path.join(VERIFICATION, name))

    def test_the_generator_meeting_every_question_gives_made_and_a_run_for_each_group(self):
        faults, result, lines = self.checked("generator.json", met("note/Q1", "note/Q2", "note/Q3"))
        self.assertEqual((faults, result), ([], "made"))
        self.assertEqual(
            lines,
            [
                helpers.line(
                    {
                        "run": RUN,
                        "phase": "content",
                        "work": ["NOTES.md"],
                        "standard": os.path.join(RUN, "standard.json"),
                        "questions": g["questions"],
                        "answers": os.path.join(VERIFICATION, f"{g['id']}.json"),
                    }
                )
                for g in CONTENT_GROUPS
            ],
        )

    def test_the_generator_with_a_point_open_gives_open_and_no_run(self):
        data = {
            **short("note/Q1", "note/Q2", "note/Q3"),
            "open": [{"question": "note/Q1", "what": "w"}],
        }
        self.assertEqual(self.checked("generator.json", data), ([], "open", []))

    def test_an_evaluator_in_the_content_phase_gives_met_or_more_and_the_generators_line(self):
        line = runs.generator_values(RUN, helpers.work())
        self.assertEqual(self.checked("G2.json", met("note/Q2")), ([], "met", [line]))
        self.assertEqual(self.checked("G2.json", short("note/Q2")), ([], "more", [line]))

    def test_an_evaluator_in_the_content_phase_has_no_point_open(self):
        data = {**met("note/Q2"), "open": [{"question": "note/Q2", "what": "w"}]}
        faults, _, _ = self.checked("G2.json", data)
        self.assertEqual(faults, ["open is the generator's, or the evaluator's in a reading round"])

    def test_an_evaluator_in_the_reading_phase_gives_good_reword_or_more(self):
        self.answers("generator.json", met("note/Q1", "note/Q2", "note/Q3"))
        for n in (1, 2, 3):
            self.answers(f"G{n}.json", met(f"note/Q{n}"))
        phases.settle(RUN)
        said = {"question": "refactor-doc/Q1", "what": "a fact must go"}
        for data, result in (
            (met("refactor-doc/Q1"), "good"),
            (short("refactor-doc/Q1"), "reword"),
            ({**short("refactor-doc/Q1"), "open": [said]}, "more"),
        ):
            with self.subTest(result=result):
                self.assertEqual(self.checked("G1.json", data)[:2], ([], result))

    def test_each_fault_of_the_answers_in_order(self):
        data = {
            "met": [
                {"question": "note/Q1", "lines": ["NOTES.md:1", "NOTES.md:9", "README.md:1"]},
                {"question": "note/Q1", "lines": ["NOTES.md"]},
                {"question": "note/Q9", "lines": ["NOTES.md:2-1"]},
            ],
            "not_met": [],
            "open": [{"question": "note/Q8", "what": "w"}],
        }
        faults, result, lines = self.checked("generator.json", data)
        self.assertEqual(
            faults,
            [
                "note/Q1 is answered more than once",
                "note/Q9 was not given to this run",
                "note/Q8, left open, was not given to this run",
                "note/Q1: NOTES.md:9 runs past NOTES.md's 7 lines",
                "note/Q1: README.md:1 lies in none of the work's paths",
                "note/Q1: NOTES.md is not as <path>:<line> or <path>:<from>-<to>",
                "note/Q9: NOTES.md:2-1 ends before it begins",
                "note/Q2 has no answer",
                "note/Q3 has no answer",
            ],
        )
        self.assertEqual((result, lines), ("", []))

    def test_a_line_or_lines_in_order_lie_in_the_work(self):
        data = met("note/Q1", "note/Q2", line="NOTES.md:2-7")
        data["met"].append({"question": "note/Q3", "lines": ["NOTES.md:3-3", "NOTES.md:7"]})
        self.assertEqual(self.checked("generator.json", data)[:2], ([], "made"))

    def test_a_line_before_the_first_or_of_a_file_not_there(self):
        self.lay_run([helpers.work(paths=["NOTES.md", "GONE.md"])])
        data = met("note/Q1", "note/Q2", line="NOTES.md:0")
        data["met"].append({"question": "note/Q3", "lines": ["GONE.md:1"]})
        faults, _, _ = self.checked("generator.json", data)
        self.assertEqual(
            faults,
            [
                "note/Q1: NOTES.md:0 begins before the file's first line",
                "note/Q2: NOTES.md:0 begins before the file's first line",
                "note/Q3: GONE.md:1 names a file that is not there",
            ],
        )

    def test_a_best_practice_made_is_held_to_its_form(self):
        made = runs.practice_in(runs.REPOSITORY, "man-page")
        self.lay_run([helpers.work(kind="meta", paths=[made])])
        phases.settle(RUN)
        self.write(made, "{}")
        data = met("meta/Q1", "meta/Q2", "meta/Q3", line=f"{made}:1")
        faults, _, _ = self.checked("generator.json", data)
        self.assertEqual(len(faults), 1)
        self.assertTrue(faults[0].startswith(f"{made} is out of its form"), faults)

    def test_a_best_practice_made_in_form_passes(self):
        made = runs.practice_in(runs.REPOSITORY, "man-page")
        self.lay_run([helpers.work(kind="meta", paths=[made])])
        phases.settle(RUN)
        self.write(made, json.dumps(helpers.PRACTICE, indent=1))
        data = met("meta/Q1", "meta/Q2", "meta/Q3", line=f"{made}:1")
        self.assertEqual(self.checked("generator.json", data)[:2], ([], "made"))

    def test_a_work_of_another_kind_is_not_held_to_the_form_of_a_best_practice(self):
        for kind in ("man-page", "readme"):
            with self.subTest(kind=kind):
                self.assertEqual(phases.made_faults(helpers.work(kind=kind)), [])

    def test_a_file_of_no_run_is_refused(self):
        for name in ("G9.json", "other.json"):
            with self.subTest(name=name), self.assertRaises(files.Unreadable) as raised:
                self.checked(name, met("note/Q1"))
            self.assertIn("is no Answers of round 1", str(raised.exception))

    def test_answers_before_any_round_are_refused(self):
        os.remove(os.path.join(VERIFICATION, "round.json"))
        with self.assertRaises(files.Unreadable) as raised:
            self.checked("G1.json", met("note/Q1"))
        self.assertEqual(str(raised.exception), "no round of note was settled: run rounds.py round")

    def test_answers_out_of_their_form_are_refused(self):
        with self.assertRaises(files.Unreadable):
            self.checked("G1.json", {"met": []})


if __name__ == "__main__":
    unittest.main()

"""scripts/rounds.py, what the generator and the evaluator run on a run's folder: round settles the
next round of the work and says what it asks, 0, or that none is left, 1; check says whether an
Answers file holds, with the result to give and the lines to end with, 0, each fault, 1, or why it
could not check, 2."""

import contextlib
import io
import os
import runpy
import unittest
from unittest import mock

import helpers
from helpers import met, phases, rounds, runs, short

RUN = helpers.RUN
VERIFICATION = os.path.join(RUN, "verification")
USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rounds.py round <run>\n"
    "       python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rounds.py check <run> <answers>\n"
)


def ran(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = rounds.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class Usage(unittest.TestCase):
    def test_a_call_it_does_not_take_gives_2_and_its_usage(self):
        for argv in ((), ("round",), ("round", "a", "b"), ("check", "a"), ("go", "a")):
            with self.subTest(argv=argv):
                self.assertEqual(ran(*argv), (2, "", USAGE))

    def test_the_script_takes_the_arguments_after_its_own_path(self):
        with (
            mock.patch.object(rounds.sys, "argv", ["rounds.py"]),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit) as end,
        ):
            runpy.run_path(rounds.__file__, run_name="__main__")
        self.assertEqual(end.exception.code, 2)


class Round(helpers.RoundsTest):
    def test_a_content_round_names_its_best_practice_design_answers_and_questions(self):
        self.assertEqual(
            ran("round", RUN),
            (
                0,
                (
                    "rounds.py: round 1 of note is of what the work says.\n"
                    f"Best practice: {helpers.NOTE}\n"
                    f"Design: {os.path.join(RUN, 'design-tree.json')}\n"
                    f"Answers: {os.path.join(VERIFICATION, 'generator.json')}, in the form of"
                    f" {os.path.join(helpers.files.FORMS, 'answers.json')}\n"
                    "Questions:\n"
                    "- note/Q1: Can the reader say what it asks?\n"
                    "- note/Q2: Can the reader take each step?\n"
                    "- note/Q3: Does each answer come when needed?\n"
                ),
                "",
            ),
        )

    def test_a_reading_round_after_one_that_fell_short_names_its_shortfalls(self):
        phases.settle(RUN)
        for n in (1, 2, 3):
            self.answers(f"G{n}.json", met(f"note/Q{n}"))
        phases.settle(RUN)
        self.answers("G1.json", short("refactor-doc/Q1"))
        code, out, _ = ran("round", RUN)
        self.assertEqual(code, 0)
        self.assertEqual(
            out,
            "rounds.py: round 3 of note is of how the work reads.\n"
            f"Best practice: {os.path.join(runs.OWN, 'refactor-doc.json')}\n"
            f"Answers: {os.path.join(VERIFICATION, 'generator.json')}, in the form of"
            f" {os.path.join(helpers.files.FORMS, 'answers.json')}\n"
            "Questions:\n"
            "- refactor-doc/Q1: Is each fact said once?\n"
            "Shortfalls of the last round:\n"
            "- refactor-doc/Q1: refactor-doc/Q1 lacks\n",
        )

    def test_no_round_left_gives_1(self):
        phases.settle(RUN)
        for n in (1, 2, 3):
            self.answers(f"G{n}.json", met(f"note/Q{n}"))
        phases.settle(RUN)
        self.answers("G1.json", met("refactor-doc/Q1"))
        self.assertEqual(
            ran("round", RUN),
            (
                1,
                "rounds.py: every question of note and of refactor-doc is met: no round is left.\n",
                "",
            ),
        )

    def test_a_work_not_in_its_rounds_gives_2(self):
        self.lay_run([helpers.work(at="pin")])
        self.assertEqual(
            ran("round", RUN),
            (
                2,
                "",
                (
                    f"rounds.py: could not settle a round of {RUN}: no round of note is due: the"
                    " work is at pin\n"
                ),
            ),
        )


class Check(helpers.RoundsTest):
    def setUp(self) -> None:
        super().setUp()
        phases.settle(RUN)

    def test_the_generators_answers_holding_give_made_and_the_evaluators_lines(self):
        path = os.path.join(VERIFICATION, "generator.json")
        self.answers("generator.json", met("note/Q1", "note/Q2", "note/Q3"))
        work = helpers.work()
        settled = phases.last(work)
        assert settled is not None
        lines = phases.evaluator_values(RUN, work, settled)
        self.assertEqual(
            ran("check", RUN, path),
            (
                0,
                f"rounds.py: {path} answers each question it was given. Give `made`, and end with"
                " these lines, one for each run of the evaluator:\n" + "\n".join(lines) + "\n",
                "",
            ),
        )

    def test_the_generator_leaving_a_point_open_gives_open(self):
        path = os.path.join(VERIFICATION, "generator.json")
        data = {
            **met("note/Q1", "note/Q2", "note/Q3"),
            "open": [{"question": "note/Q1", "what": "w"}],
        }
        self.answers("generator.json", data)
        code, out, _ = ran("check", RUN, path)
        self.assertEqual(
            (code, out),
            (0, f"rounds.py: {path} answers each question it was given. Give `open`.\n"),
        )

    def test_an_evaluators_answers_holding_give_its_result_and_the_generators_line(self):
        path = os.path.join(VERIFICATION, "G2.json")
        self.answers("G2.json", short("note/Q2"))
        self.assertEqual(
            ran("check", RUN, path),
            (
                0,
                f"rounds.py: {path} answers each question it was given. Give `more`, and end with"
                " this line, for up to start the generator with:\n"
                + runs.generator_values(RUN, helpers.work())
                + "\n",
                "",
            ),
        )

    def test_answers_that_do_not_hold_give_1_and_each_fault(self):
        path = os.path.join(VERIFICATION, "G2.json")
        self.answers("G2.json", met())
        self.assertEqual(
            ran("check", RUN, path),
            (1, f"rounds.py: {path} does not hold:\n- note/Q2 has no answer\n", ""),
        )

    def test_answers_it_cannot_read_give_2(self):
        path = os.path.join(VERIFICATION, "G2.json")
        code, out, err = ran("check", RUN, path)
        self.assertEqual((code, out), (2, ""))
        self.assertIn(f"rounds.py: could not check {path}: there is no file {path}", err)


if __name__ == "__main__":
    unittest.main()

"""answering.py: the questions a run of a step was given, told by the name of its answers file;
and its answers, each question it was given answered once, each good with lines that lie in the
work, and content from proofreader alone."""

import unittest

import helpers
from helpers import answering, decision, question


def given(**lists):
    """Answers holding the lists given, good and more empty where not given."""
    made = {"good": [], "more": []}
    made.update(lists)
    return made


def good(n, *lines):
    return {"question": question(n), "lines": list(lines) or ["README.md:1"]}


def more(n):
    return {"question": question(n), "good_when": "the reader gets it"}


class TestAssigned(helpers.RunTest):
    def test_a_part_s_run_answers_what_its_decisions_reach(self):
        # Given: D1 serves Q1 and Q3, D3 serves D2, which serves Q2
        made = helpers.run()
        made["work.json"]["parts"] = [
            {"id": "P1", "decisions": ["D1"], "paths": ["README.md"]},
            {"id": "P2", "decisions": ["D2", "D3"], "paths": ["README.md"]},
        ]
        self.lay(made)
        # Then: P1 answers Q1 and Q3, P2 Q2, each in the tree's order
        self.assertEqual(
            answering.assigned(self.folder, "self-check/P1.json"), [question(1), question(3)]
        )
        self.assertEqual(answering.assigned(self.folder, "self-check/P2.json"), [question(2)])

    def test_a_decision_reaching_a_question_through_another_reaches_it_once(self):
        made = helpers.run()
        made["design-tree.json"]["decisions"] = [
            decision("D1", [question(1)]),
            decision("D2", ["D1", question(1)]),
            decision("D3", ["D2", "D1"]),
        ]
        made["work.json"]["parts"] = [{"id": "P1", "decisions": ["D3"], "paths": ["README.md"]}]
        self.lay(made)
        self.assertEqual(answering.assigned(self.folder, "self-check/P1.json"), [question(1)])

    def test_a_group_s_run_answers_its_group(self):
        self.lay()
        self.assertEqual(answering.assigned(self.folder, "verification/G2.json"), [question(2)])
        self.assertEqual(
            answering.assigned(self.folder, "proofreading/G1.json"), ["refactor-doc/Q1"]
        )

    def test_refactorer_answers_every_question_of_the_refactoring_template(self):
        self.lay()
        self.assertEqual(
            answering.assigned(self.folder, "refactor-check.json"), ["refactor-doc/Q1"]
        )

    def test_a_part_or_group_the_run_has_not_is_refused(self):
        self.lay()
        for name, why in (
            ("self-check/P9.json", "work.json has no part P9"),
            ("verification/G9.json", "run.json has no group G9 under groups"),
            ("proofreading/G9.json", "run.json has no group G9 under refactoring_groups"),
        ):
            with self.subTest(name=name), self.assertRaises(helpers.files.Unreadable) as refused:
                answering.assigned(self.folder, name)
            self.assertEqual(str(refused.exception), f"{self.folder}/{why}")

    def test_a_run_whose_groups_are_not_yet_written_is_refused(self):
        made = helpers.run()
        del made["run.json"]["groups"]
        self.lay(made)
        with self.assertRaises(helpers.files.Unreadable) as refused:
            answering.assigned(self.folder, "verification/G1.json")
        self.assertEqual(
            str(refused.exception), f"{self.folder}/run.json has no group G1 under groups"
        )

    def test_a_name_that_is_no_answers_file_is_refused(self):
        self.lay()
        for name in (
            "verification.json",
            "self-check/P1.txt",
            "other/G1.json",
            "self-check/a/P1.json",
        ):
            with self.subTest(name=name), self.assertRaises(helpers.files.Unreadable) as refused:
                answering.assigned(self.folder, name)
            self.assertEqual(
                str(refused.exception),
                f"{name} is no answers file of a run: self-check/<part>.json,"
                " verification/<group>.json, refactor-check.json or proofreading/<group>.json",
            )


class TestFaults(helpers.RunTest):
    def setUp(self):
        super().setUp()
        self.lay()

    def faults(self, answers, assigned=(1, 2), content=False):
        return answering.faults(answers, [question(n) for n in assigned], ["README.md"], content)

    def test_every_question_answered_once_with_lines_in_the_work_has_none(self):
        self.assertEqual(self.faults(given(good=[good(1, "README.md:1-3")], more=[more(2)])), [])

    def test_a_question_unanswered_twice_answered_or_not_given(self):
        answers = given(good=[good(1), good(3)], more=[more(1)])
        self.assertEqual(
            self.faults(answers),
            [
                "readme/Q1 is answered more than once",
                "readme/Q3 was not given to this run",
                "readme/Q2 has no answer",
            ],
        )

    def test_content_is_proofreader_s_alone(self):
        answers = given(good=[good(1)], content=[more(2)])
        self.assertEqual(self.faults(answers), ["content is proofreader's alone"])
        self.assertEqual(self.faults(answers, content=True), [])

    def test_each_way_a_line_fails_to_lie_in_the_work(self):
        # Given: the work, README.md, of 7 lines
        lines = [
            "README.md",
            "README.md:0",
            "README.md:4-2",
            "README.md:7-8",
            "other.md:1",
            "README.md:7",
        ]
        self.assertEqual(
            self.faults(given(good=[good(1, *lines)], more=[more(2)])),
            [
                "readme/Q1: README.md is not as <path>:<line> or <path>:<from>-<to>",
                "readme/Q1: README.md:0 begins before the file's first line",
                "readme/Q1: README.md:4-2 ends before it begins",
                "readme/Q1: README.md:7-8 runs past README.md's 7 lines",
                "readme/Q1: other.md:1 lies in none of the work's paths",
            ],
        )

    def test_a_line_of_a_work_s_path_that_is_not_there(self):
        self.assertEqual(
            answering.faults(given(good=[good(1, "gone.md:1")]), [question(1)], ["gone.md"], False),
            ["readme/Q1: gone.md:1 names a file that is not there"],
        )

    def test_a_line_under_a_folder_of_the_work(self):
        self.write("src/a.py", "x = 1\n")
        self.assertEqual(
            answering.faults(given(good=[good(1, "src/a.py:1")]), [question(1)], ["src"], False), []
        )
        self.assertEqual(
            answering.faults(given(good=[good(1, "srcx/a.py:1")]), [question(1)], ["src"], False),
            ["readme/Q1: srcx/a.py:1 lies in none of the work's paths"],
        )


class TestCheck(helpers.RunTest):
    def test_answers_of_a_group_checked_against_the_work(self):
        self.lay()
        path = f"{self.folder}/verification/G1.json"
        self.write_json(path, given(more=[more(2)]))
        self.assertEqual(
            answering.check(self.folder, path),
            ["readme/Q2 was not given to this run", "readme/Q1 has no answer"],
        )

    def test_proofreader_may_give_content(self):
        self.lay()
        path = f"{self.folder}/proofreading/G1.json"
        self.write_json(
            path, given(content=[{"question": "refactor-doc/Q1", "good_when": "said once"}])
        )
        self.assertEqual(answering.check(self.folder, path), [])

    def test_answers_out_of_their_form_cannot_be_checked(self):
        self.lay()
        path = f"{self.folder}/refactor-check.json"
        self.write_json(path, {"good": []})
        with self.assertRaises(helpers.files.Unreadable) as refused:
            answering.check(self.folder, path)
        self.assertIn("refactor-check.json is out of its form", str(refused.exception))


if __name__ == "__main__":
    unittest.main()

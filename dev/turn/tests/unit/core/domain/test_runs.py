"""runs.py: the run values of each run of a step, read from the run's folder, so the role before
the step hands them to up, which Lane lets start roles alone while a start is due."""

import unittest

import helpers
from helpers import files, runs

RUN = helpers.RunTest.folder
COMMANDS = helpers.RUN["work.json"]["commands"]


class TestRuns(helpers.RunTest):
    def test_builder_runs_once_for_each_part(self):
        made = helpers.run()
        made["work.json"]["paths"] = ["a.md", "b.md"]
        made["work.json"]["parts"] = [
            {"id": "P1", "decisions": ["D1"], "paths": ["a.md"]},
            {"id": "P2", "decisions": ["D2", "D3"], "paths": ["b.md"]},
        ]
        self.lay(made)
        self.assertEqual(
            runs.runs(RUN, "builder"),
            [
                {
                    "run": RUN,
                    "work": ["a.md"],
                    "decisions": ["D1"],
                    "commands": COMMANDS,
                    "answers": f"{RUN}/self-check/P1.json",
                    "open": f"{RUN}/open/P1.json",
                },
                {
                    "run": RUN,
                    "work": ["b.md"],
                    "decisions": ["D2", "D3"],
                    "commands": COMMANDS,
                    "answers": f"{RUN}/self-check/P2.json",
                    "open": f"{RUN}/open/P2.json",
                },
            ],
        )

    def test_after_a_remake_builder_runs_for_the_parts_it_reaches_alone(self):
        made = helpers.run()
        made["work.json"]["parts"] = [
            {"id": "P1", "decisions": ["D1"], "paths": ["README.md"]},
            {"id": "P2", "decisions": ["D2", "D3"], "paths": ["README.md"]},
        ]
        made["remake.json"] = {
            "decisions": [{"decision": "D3", "question": "readme/Q2", "good_when": "w"}]
        }
        self.lay(made)
        self.assertEqual([r["decisions"] for r in runs.runs(RUN, "builder")], [["D2", "D3"]])

    def test_evaluator_and_proofreader_run_once_for_each_group(self):
        self.lay()
        self.assertEqual(
            runs.runs(RUN, "evaluator")[1],
            {
                "run": RUN,
                "work": ["README.md"],
                "commands": COMMANDS,
                "questions": ["readme/Q2"],
                "standard": f"{RUN}/standard.json",
                "answers": f"{RUN}/verification/G2.json",
            },
        )
        self.assertEqual(len(runs.runs(RUN, "evaluator")), 3)
        self.assertEqual(
            runs.runs(RUN, "proofreader"),
            [
                {
                    "run": RUN,
                    "work": ["README.md"],
                    "commands": COMMANDS,
                    "questions": ["refactor-doc/Q1"],
                    "standard": f"{RUN}/refactoring-standard.json",
                    "answers": f"{RUN}/proofreading/G1.json",
                }
            ],
        )

    def test_refactorer_runs_once(self):
        self.lay()
        self.assertEqual(
            runs.runs(RUN, "refactorer"),
            [
                {
                    "run": RUN,
                    "work": ["README.md"],
                    "commands": COMMANDS,
                    "answers": f"{RUN}/refactor-check.json",
                }
            ],
        )

    def test_a_role_that_runs_no_step_of_its_own_is_refused(self):
        self.lay()
        with self.assertRaises(files.Unreadable) as refused:
            runs.runs(RUN, "planner")
        self.assertEqual(
            str(refused.exception),
            "planner is not builder, evaluator, refactorer or proofreader, whose runs this gives",
        )

    def test_a_run_without_its_groups_is_refused(self):
        made = helpers.run()
        del made["run.json"]["refactoring_groups"]
        self.lay(made)
        with self.assertRaises(files.Unreadable) as refused:
            runs.runs(RUN, "proofreader")
        self.assertEqual(str(refused.exception), f"{RUN}/run.json has no refactoring_groups yet")


if __name__ == "__main__":
    unittest.main()

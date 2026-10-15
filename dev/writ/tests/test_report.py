import unittest

from helpers import Repo, run

LIST = {
    "checklists": [
        {"checklist": "doc", "version": "0.2.0", "opening": "A document is read."},
        {"checklist": "readme", "version": "0.2.0", "opening": "A README is read."},
    ],
    "items": [
        {"id": "doc B-2", "title": "The picture as meant", "text": "Does the reader hold it?"},
        {"id": "doc B-3", "title": "Each idea taken in whole", "text": "Can they take it whole?"},
        {"id": "doc B-4", "title": "Every part used", "text": "Is each part used?"},
        {"id": "readme B-1", "title": "What they gain", "text": "Can they tell the gain?"},
    ],
}
DECIDED = {
    "doc B-2": {"met": True, "lines": "1-4", "note": "one picture"},
    "doc B-3": {"met": False, "lines": "", "note": ""},
    "doc B-4": {"met": True, "lines": "README.md:5-8", "note": "each part serves"},
    "readme B-1": {"met": True, "lines": "1-2", "note": "the gain"},
}
BACK = {
    "focal_entities": [{"deliverable": "README.md"}, {"receiver": "a developer"}],
    "goal_orientation": [{"use": "to decide"}, {"acceptance": "they can start"}],
    "retrieved_artifacts": [
        {"checklist": "x/doc.md"},
        {"content": ".writ/content/README.content.md"},
    ],
    "constraints": [],
    "predictive_cue": [{"next": "ask the user"}],
    "uncertainty_signal": [],
    "semantic_gist": [
        {"question": "Which license is the tool under?"},
        {"unmet": "doc B-3 (Can they take it whole?): say what the tool keeps of each file"},
        {"rule": "Name the license beside the install line."},
    ],
    "relational_map": [],
    "episodic_trace": [
        {"evidence": ".turn/README-1/list.json"},
        {"evidence": ".turn/README-1/orchestrator.json"},
    ],
}
JUDGED = {
    "decided": [{"point": "No tool to compare with is named", "ground": "the notes name none"}],
    "questions": [
        {"question": "Which license is the tool under?", "judged": "asked you; you said MIT"}
    ],
    "unmet": [
        {
            "item": "doc B-3",
            "judged": "left; what the tool keeps does not change whether a developer starts",
        }
    ],
    "changed": [{"lines": "README.md:12", "why": "put in the license you named"}],
}
REPORT = """Decided for you
  No tool to compare with is named: the notes name none
  Question: Which license is the tool under?: asked you; you said MIT
  Not met: doc B-3 Each idea taken in whole: left; what the tool keeps does not change whether a developer starts
    turn: say what the tool keeps of each file
  Rule from turn: Name the license beside the install line.
  Changed after turn: README.md:12: put in the license you named

doc 0.2.0
  ✅ B-2 The picture as meant: 1-4
  ⬜ B-3 Each idea taken in whole
  ✅ B-4 Every part used: README.md:5-8

readme 0.2.0
  ✅ B-1 What they gain: 1-2

The document: README.md
What it says, item by item: .writ/content/README.content.md
"""


class Report(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.repo.write(".turn/README-1/list.json", LIST)
        self.repo.write(".turn/README-1/orchestrator.json", DECIDED)
        self.repo.write(".writ/tasks/README-1.back.json", BACK)
        self.repo.write(".writ/tasks/README-1.judged.json", JUDGED)

    def tearDown(self):
        self.repo.close()

    def report(self):
        return run(
            self.repo,
            "report",
            ".writ/tasks/README-1.back.json",
            ".writ/tasks/README-1.judged.json",
        )

    def test_the_report_puts_first_what_the_caller_decides_then_each_item_as_turn_decided_it(self):
        # Given: turn's evidence with two items met and one not, its CCS back with a question, that
        # item and a rule, and writ's judgment on each and on a point it settled and a line it changed
        # When: the report is made
        code, out = self.report()
        # Then: it puts first the point, the question, the item, the rule and the change, each with
        # the judgment, and then each item met with turn's lines and each not met without, and where
        # the document and its content are
        self.assertEqual((code, out), (0, REPORT))

    def test_a_report_with_nothing_for_the_caller_to_decide_says_so(self):
        # Given: turn's CCS back saying done, with every item met, and no judgment to make
        self.repo.write(
            ".turn/README-1/orchestrator.json",
            {
                i: {"met": True, "lines": "1", "note": "x"}
                for i in ("doc B-2", "doc B-3", "doc B-4", "readme B-1")
            },
        )
        self.repo.write(
            ".writ/tasks/README-1.back.json",
            dict(BACK, predictive_cue=[{"next": "done"}], semantic_gist=[]),
        )
        self.repo.write(".writ/tasks/README-1.judged.json", {})
        # When: the report is made
        code, out = self.report()
        # Then: the first part says nothing was decided for the caller
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("Decided for you\n  Nothing.\n\ndoc 0.2.0\n  ✅ B-2"), out)

    def test_a_report_is_stopped_when_a_question_or_item_turn_returned_is_not_judged(self):
        cases = [
            (
                dict(JUDGED, questions=[]),
                "judge the question first: Which license is the tool under?",
            ),
            (dict(JUDGED, unmet=[]), "judge the item first: doc B-3"),
        ]
        for judged, said in cases:
            with self.subTest(said):
                # Given: writ's judgments missing one thing turn returned
                self.repo.write(".writ/tasks/README-1.judged.json", judged)
                # When: the report is made
                code, out = self.report()
                # Then: it is stopped, naming what to judge, so nothing turn returned is dropped
                self.assertEqual(code, 1)
                self.assertIn(said, out)

    def test_an_item_shown_met_is_one_turn_decided_met(self):
        # Given: turn's evidence with an item not met, and a judgment that says nothing of it
        self.repo.write(
            ".turn/README-1/orchestrator.json",
            dict(DECIDED, **{"doc B-2": {"met": False, "lines": "", "note": ""}}),
        )
        # When: the report is made
        code, out = self.report()
        # Then: that item is shown not met, whatever writ wrote
        self.assertEqual(code, 0)
        self.assertIn("  ⬜ B-2 The picture as meant\n", out)
        self.assertNotIn("✅ B-2", out)

    def test_a_judgments_file_that_is_not_json_is_stopped(self):
        # Given: writ's judgments written as something other than JSON
        self.repo.write(".writ/tasks/README-1.judged.json", "{")
        # When: the report is made
        code, out = self.report()
        # Then: it is stopped, naming the file
        self.assertEqual(code, 1)
        self.assertIn(".writ/tasks/README-1.judged.json is not JSON", out)

    def test_a_report_on_a_ccs_that_names_no_evidence_is_stopped(self):
        # Given: a CCS back with no evidence, as turn writes when it was stopped
        self.repo.write(
            ".writ/tasks/README-1.back.json",
            dict(BACK, predictive_cue=[{"next": "stopped: write"}], episodic_trace=[]),
        )
        # When: the report is made
        code, out = self.report()
        # Then: it is stopped, saying there is no evidence to report from
        self.assertEqual(code, 1)
        self.assertIn("names no evidence; turn was stopped", out)


if __name__ == "__main__":
    unittest.main()

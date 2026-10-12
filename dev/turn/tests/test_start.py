import json
import unittest

from helpers import Repo, ccs, run, started


class Start(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_a_run_lays_out_the_list_and_an_empty_form_for_each_role(self):
        # Given: a task to be written in English, naming a checklist with two items and a fenced example
        # When: a run starts
        got = started(self.repo, ccs(constraints=[{"language": "English"}]))
        # Then: the list holds the checklist's opening and both items, not the example
        listed = self.repo.json(got["list"])
        self.assertEqual(listed["checklists"][0]["checklist"], "note")
        self.assertTrue(listed["checklists"][0]["opening"].startswith("A note is read by a teammate"))
        self.assertEqual([i["id"] for i in listed["items"]], ["note B-1", "note F-1"])
        self.assertIn("Why: a note is for acting.", listed["items"][0]["text"])
        # Then: each role's form has a place for every item, the evaluator's and the learner's none to start with
        forms = got["forms"]
        self.assertEqual(self.repo.json(forms["generator"]),
                         {"note B-1": {"lines": ""}, "note F-1": {"lines": ""}})
        self.assertEqual(self.repo.json(forms["first-user"]), {})
        self.assertEqual(self.repo.json(forms["hand-on"])["note B-1"], {"met": None, "lines": "", "note": ""})
        self.assertEqual(self.repo.json(forms["evaluator"]), {})
        self.assertEqual(self.repo.json(forms["learner"]), {})
        self.assertEqual(self.repo.json(forms["orchestrator"])["note F-1"],
                         {"met": None, "lines": "", "note": ""})
        # Then: what the agents are handed is given, and the work goes in the run's folder
        self.assertEqual(got["receiver"], "a new teammate")
        self.assertEqual(got["use"], "to start work")
        self.assertEqual(got["acceptance"], ["they can start alone"])
        self.assertEqual(got["sources"], ["notes.md"])
        self.assertEqual(got["constraints"], ["language: English"])
        self.assertEqual(got["folder"], ".turn/out")
        self.assertEqual(got["work"], ".turn/out/1/note.md")
        self.assertFalse(self.repo.exists("out.json"))

    def test_a_task_without_a_use_is_run_with_none(self):
        # Given: a task that names no use
        c = ccs(goal_orientation=[{"acceptance": "they can start alone"}])
        # When: a run starts
        got = started(self.repo, c)
        # Then: the use is empty
        self.assertEqual(got["use"], "")

    def test_a_task_is_refused_when_out_already_exists(self):
        # Given: a file already where the CCS would be written back
        self.repo.write("in.json", json.dumps(ccs()))
        self.repo.write("out.json", "keep")
        # When: a run starts
        code, out = run(self.repo, "start", "in.json", "out.json", "s1")
        # Then: it ends saying why, and writes nothing
        self.assertEqual(code, 1)
        self.assertIn("out.json already exists", out)
        self.assertEqual(self.repo.read("out.json"), "keep")
        self.assertFalse(self.repo.exists(".turn"))

    def test_a_task_is_refused_when_its_ccs_does_not_match_the_form(self):
        cases = [
            ("not JSON", "{", "in.json is not JSON"),
            ("a part missing", {k: v for k, v in ccs().items() if k != "episodic_trace"},
             "episodic_trace is missing"),
            ("a part not a list", ccs(constraints={}), "constraints is not a list"),
            ("an entry of two kinds", ccs(constraints=[{"language": "a", "rule": "b"}]),
             "constraints has an entry that is not one kind and a string"),
            ("an unknown kind", ccs(constraints=[{"colour": "red"}]),
             "constraints has a kind it cannot hold: colour"),
            ("no checklist", ccs(retrieved_artifacts=[]), "retrieved_artifacts needs a viewpoint"),
            ("two deliverables",
             ccs(focal_entities=[{"deliverable": "a.md"}, {"deliverable": "b.md"},
                                 {"receiver": "r"}]),
             "focal_entities needs one deliverable"),
            ("no receiver", ccs(focal_entities=[{"deliverable": "a.md"}]),
             "focal_entities needs a receiver"),
            ("no acceptance", ccs(goal_orientation=[{"use": "u"}]),
             "goal_orientation needs an acceptance"),
            ("a checklist that is not there",
             ccs(retrieved_artifacts=[{"viewpoint": "checklists/none.md"}]),
             "checklists/none.md does not exist"),
            ("a source that is not there",
             ccs(retrieved_artifacts=[{"viewpoint": "checklists/note.md"}, {"source": "gone.md"}]),
             "gone.md does not exist"),
            ("a deliverable outside the repository",
             ccs(focal_entities=[{"deliverable": "../x.md"}, {"receiver": "r"}]),
             "../x.md is outside the repository"),
        ]
        for name, c, said in cases:
            with self.subTest(name):
                # Given: a task whose CCS has this fault
                self.repo.write("in.json", c if isinstance(c, str) else json.dumps(c))
                # When: a run starts
                code, out = run(self.repo, "start", "in.json", "out.json", "s1")
                # Then: it ends saying what is wrong, and starts nothing
                self.assertEqual(code, 1)
                self.assertIn(said, out)
                self.assertFalse(self.repo.exists(".turn"))


if __name__ == "__main__":
    unittest.main()

import json
import unittest

from helpers import Repo, ccs, form, run, started


class Start(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_a_run_lays_out_the_list_and_an_empty_form_for_each_role(self):
        # Given: a task naming a checklist with two items and a fenced example
        # When: a run starts
        got = started(self.repo)
        # Then: the list holds the checklist's opening and both items, not the example
        listed = self.repo.json(got["list"])
        self.assertEqual(
            (listed["checklists"][0]["checklist"], listed["checklists"][0]["version"]),
            ("note", "1.2.0"),
        )
        self.assertTrue(
            listed["checklists"][0]["opening"].startswith("A note is read by a teammate")
        )
        self.assertEqual([i["id"] for i in listed["items"]], ["note B-1", "note F-1"])
        self.assertIn("Why: a note is for acting.", listed["items"][0]["text"])
        # Then: each role's form has a place for every item, the agents' that write per item none
        # to start with
        self.assertEqual(
            self.repo.json(form("generator")),
            {"note B-1": {"lines": ""}, "note F-1": {"lines": ""}},
        )
        for role in ("first-user", "evaluator", "learner"):
            self.assertEqual(self.repo.json(form(role)), {})
        for role in ("hand-on", "orchestrator"):
            self.assertEqual(
                self.repo.json(form(role))["note F-1"], {"met": None, "lines": "", "note": ""}
            )
        # Then: the orchestrator is given what it decides from and where it writes, and no more
        self.assertEqual(
            got,
            {
                "folder": ".turn/out",
                "list": ".turn/out/list.json",
                "work": ".turn/out/note.md",
                "hand-on": form("hand-on"),
                "orchestrator": form("orchestrator"),
                "questions": ".turn/out/questions.json",
                "receiver": "a new teammate",
                "use": "to start work",
                "acceptance": ["they can start alone"],
                "content": ["notes.md"],
                "references": [],
                "constraints": [],
            },
        )
        self.assertFalse(self.repo.exists("out.json"))

    def test_each_item_is_named_by_its_checklist_s_name_not_by_the_file_s(self):
        # Given: the checklist kept in a file named otherwise than the name it gives itself
        self.repo.write("checklists/handover.md", self.repo.read("checklists/note.md"))
        # When: a run starts on it
        got = started(self.repo, ccs(retrieved_artifacts=[{"checklist": "checklists/handover.md"}]))
        # Then: its items are named by the checklist's own name
        self.assertEqual(
            [i["id"] for i in self.repo.json(got["list"])["items"]], ["note B-1", "note F-1"]
        )

    def test_a_folder_may_be_a_reference_or_what_the_receiver_opens(self):
        # Given: a task naming a folder as a reference and one as what the receiver opens
        self.repo.write("src/tidy.py", "print(1)\n")
        self.repo.write("docs/guide/a.md", "A\n")
        c = ccs(
            retrieved_artifacts=[
                {"checklist": "checklists/note.md"},
                {"content": "notes.md"},
                {"reference": "src"},
                {"receiver_opens": "docs/guide"},
            ]
        )
        # When: a run starts
        got = started(self.repo, c)
        # Then: it starts, and the orchestrator is given the reference
        self.assertEqual(got["references"], ["src"])

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
            (
                "a part missing",
                {k: v for k, v in ccs().items() if k != "episodic_trace"},
                "episodic_trace is missing",
            ),
            ("a part not a list", ccs(constraints={}), "constraints is not a list"),
            (
                "an entry of two kinds",
                ccs(constraints=[{"language": "a", "rule": "b"}]),
                "constraints has an entry that is not one kind and a string",
            ),
            (
                "an unknown kind",
                ccs(constraints=[{"colour": "red"}]),
                "constraints has a kind it cannot hold: colour",
            ),
            ("no checklist", ccs(retrieved_artifacts=[]), "retrieved_artifacts needs a checklist"),
            (
                "two deliverables",
                ccs(
                    focal_entities=[
                        {"deliverable": "a.md"},
                        {"deliverable": "b.md"},
                        {"receiver": "r"},
                    ]
                ),
                "focal_entities needs one deliverable",
            ),
            (
                "no receiver",
                ccs(focal_entities=[{"deliverable": "a.md"}]),
                "focal_entities needs a receiver",
            ),
            (
                "no acceptance",
                ccs(goal_orientation=[{"use": "u"}]),
                "goal_orientation needs an acceptance",
            ),
            (
                "a checklist without its name and version",
                ccs(retrieved_artifacts=[{"checklist": "notes.md"}]),
                "notes.md: open the checklist with front matter giving its name and version",
            ),
            (
                "a checklist without its version",
                ccs(retrieved_artifacts=[{"checklist": "nameonly.md"}]),
                "nameonly.md: open the checklist with front matter giving its name and version",
            ),
            (
                "a checklist that is not there",
                ccs(retrieved_artifacts=[{"checklist": "checklists/none.md"}]),
                "checklists/none.md does not exist",
            ),
            (
                "a content file that is not there",
                ccs(
                    retrieved_artifacts=[
                        {"checklist": "checklists/note.md"},
                        {"content": "gone.md"},
                    ]
                ),
                "gone.md does not exist",
            ),
            (
                "a reference that is not there",
                ccs(
                    retrieved_artifacts=[
                        {"checklist": "checklists/note.md"},
                        {"reference": "src/"},
                    ]
                ),
                "src/ does not exist",
            ),
            (
                "what the receiver opens, not there",
                ccs(
                    retrieved_artifacts=[
                        {"checklist": "checklists/note.md"},
                        {"receiver_opens": "LICENSE"},
                    ]
                ),
                "LICENSE does not exist",
            ),
            (
                "a kind of 0.1.0",
                ccs(retrieved_artifacts=[{"viewpoint": "checklists/note.md"}]),
                "retrieved_artifacts has a kind it cannot hold: viewpoint",
            ),
            (
                "a deliverable outside the repository",
                ccs(focal_entities=[{"deliverable": "../x.md"}, {"receiver": "r"}]),
                "../x.md is outside the repository",
            ),
        ]
        self.repo.write("nameonly.md", "---\nname: note\n---\n\n# Note\n")
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

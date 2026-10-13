import json
import os
import subprocess
import sys
import unittest

from helpers import form, ROOT, Repo, fill, run, started

WORK = "# Note\n\nRun make.\n"


def seen(repo, f1=True):
    """The orchestrator's form before the reading, with F-1 seen given or not."""
    fill(repo, form("hand-on"), {
        "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
        "note F-1": {"met": True, "lines": "1-3", "note": "three lines"} if f1 else
        {"met": False, "aim": "the teammate takes it in at a glance", "way": "cut it to one line", "reach": "1-3"}})


class Coverage(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], WORK)

    def tearDown(self):
        self.repo.close()

    def test_the_lines_with_text_that_no_item_names_are_shown(self):
        cases = [("generator", {"note B-1": {"lines": "3"}, "note F-1": {"lines": "3"}},
                  "lines no item names: 1"),
                 ("generator", {"note B-1": {"lines": "1"}, "note F-1": {"lines": "3"}},
                  "every line is named"),
                 ("evaluator", {"note B-1": {"lines": "3", "grounds": "says run make"}},
                  "lines no item names: 1")]
        for role, filled, said in cases:
            with self.subTest(role=role, said=said):
                # Given: the role's form naming these lines
                fill(self.repo, form(role), filled)
                # When: the coverage is asked for
                code, out = run(self.repo, "coverage", ".turn/out", "1", role)
                # Then: the lines with text that no place names are shown, blank lines left out
                self.assertEqual((code, out.strip()), (0, said))


class Check(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], WORK)

    def tearDown(self):
        self.repo.close()

    def check(self, role):
        return run(self.repo, "check", ".turn/out", "1", role)

    def test_a_form_filled_for_every_item_on_lines_the_work_holds_passes(self):
        # Given: each role's form filled as its steps ask
        fill(self.repo, form("generator"), {"note B-1": {"lines": "3"}, "note F-1": {"lines": "1-3"}})
        fill(self.repo, form("first-user"), {
            "note B-1": {"took": "run make", "lines": "3"}})
        fill(self.repo, form("evaluator"), {"note B-1": {"lines": "3", "grounds": "says run make"}})
        fill(self.repo, form("orchestrator"), {
            "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
            "note F-1": {"met": False, "lines": "", "note": ""}})
        seen(self.repo)
        for role in ("generator", "hand-on", "first-user", "evaluator", "orchestrator"):
            with self.subTest(role):
                # When: the form is checked
                code, out = self.check(role)
                # Then: it passes
                self.assertEqual((code, out.strip()), (0, "filled"))

    def test_a_form_with_a_place_left_or_wrong_is_stopped_saying_which(self):
        cases = [
            ("generator", "generator", {"note B-1": {"lines": "3"}, "note F-1": {"lines": ""}},
             "note F-1: lines are not given"),
            ("generator", "generator", {"note B-1": {"lines": "3"}, "note F-1": {"lines": "2-9"}},
             "note F-1: lines 2-9 are not in the work"),
            ("generator", "generator", {"note B-1": {"lines": "3"}, "note F-1": {"lines": "end"}},
             "note F-1: lines end are not in the work"),
            ("generator", "generator", {"note B-1": {"lines": "3"}},
             "note F-1: not filled"),
            ("generator", "generator", {"note B-1": {"lines": "3"}, "note F-1": {"lines": "3"},
                                        "note X-1": {"lines": "3"}},
             "note X-1: not an item of the list"),
            ("first user", "first-user", {"note B-1": {"took": "", "lines": "3"}},
             "note B-1: what was taken is not given"),
            ("first user without lines", "first-user", {"note B-1": {"took": "run make", "lines": ""}},
             "note B-1: lines are not given"),
            ("evaluator", "evaluator", {"note B-1": {"lines": "3", "grounds": ""}},
             "note B-1: grounds are not given"),
            ("orchestrator", "orchestrator", {
                "note B-1": {"met": None, "lines": "", "note": "x"},
                "note F-1": {"met": True, "lines": "", "note": "x"}},
             "note B-1: not decided"),
            ("orchestrator met without lines", "orchestrator", {
                "note B-1": {"met": False, "lines": "", "note": "x"},
                "note F-1": {"met": True, "lines": "", "note": "x"}},
             "note F-1: lines are not given"),
            ("orchestrator met without a note", "orchestrator", {
                "note B-1": {"met": True, "lines": "3", "note": ""},
                "note F-1": {"met": False, "lines": "", "note": ""}},
             "note B-1: the note is not given"),
            ("hand-on without the aim", "hand-on", {
                "note B-1": {"met": False, "aim": "", "way": "say what make does", "reach": "3"},
                "note F-1": {"met": True, "lines": "1", "note": "x"}},
             "note B-1: the aim is not given"),
            ("hand-on with a way made from lines", "hand-on", {
                "note B-1": {"met": False, "aim": "they know what to run", "way": "add to line 3", "reach": "3"},
                "note F-1": {"met": True, "lines": "1", "note": "x"}},
             "note B-1: the way names lines; say it from the aim"),
            ("hand-on with a reach outside the work", "hand-on", {
                "note B-1": {"met": False, "aim": "they know what to run", "way": "say what make does",
                             "reach": "9"},
                "note F-1": {"met": True, "lines": "1", "note": "x"}},
             "note B-1: reach 9 is not in the work"),
            ("not JSON", "generator", "{", "the form is not JSON"),
        ]
        for name, role, filled, said in cases:
            with self.subTest(name):
                # Given: the form with this place left or wrong
                self.repo.write(form(role), filled if isinstance(filled, str) else json.dumps(filled))
                # When: it is checked
                code, out = self.check(role)
                # Then: it is stopped, naming the place
                self.assertEqual(code, 1)
                self.assertIn(said, out)

    def test_a_form_is_stopped_when_the_work_is_not_written(self):
        # Given: the work removed
        os.remove(os.path.join(self.repo.path, self.got["work"]))
        # When: the generator's form is checked
        code, out = self.check("generator")
        # Then: it is stopped saying the work is missing
        self.assertEqual(code, 1)
        self.assertIn(".turn/out/1/note.md is not written", out)


class End(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], WORK)

    def tearDown(self):
        self.repo.close()

    def decide(self, b1, f1):
        fill(self.repo, form("orchestrator"), {
            "note B-1": {"met": b1, "lines": "3" if b1 else "", "note": "the step is given"},
            "note F-1": {"met": f1, "lines": "1-3" if f1 else "", "note": "the title is short" if f1 else ""}})

    def test_a_run_with_every_item_met_returns_the_work_and_done(self):
        # Given: every item decided met
        self.decide(True, True)
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out", "1")
        # Then: the work is where it goes, and the CCS says done with the caller's parts unchanged
        self.assertEqual(code, 0)
        self.assertEqual(self.repo.read("docs/note.md"), WORK)
        back = self.repo.json("out.json")
        sent = self.repo.json("in.json")
        for part in ("focal_entities", "goal_orientation", "retrieved_artifacts", "constraints"):
            self.assertEqual(back[part], sent[part])
        self.assertEqual(back["predictive_cue"], [{"next": "done"}])
        self.assertEqual(back["semantic_gist"], [])
        self.assertEqual(back["episodic_trace"], [{"evidence": ".turn/out/1/orchestrator.json"}])
        self.assertEqual(out.splitlines()[0], "done")

    def test_a_run_does_not_return_before_every_item_is_decided(self):
        # Given: the orchestrator's form with an item undecided
        self.decide(True, None)
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out", "1")
        # Then: it is stopped, and nothing is written back
        self.assertEqual(code, 1)
        self.assertIn("note F-1: not decided", out)
        self.assertFalse(self.repo.exists("out.json"))
        self.assertFalse(self.repo.exists("docs/note.md"))


class Usage(unittest.TestCase):
    def test_an_unknown_command_says_how_to_call(self):
        # Given: a call with no command turn knows
        repo = Repo()
        # When: it is run
        code, out = run(repo, "fly")
        # Then: it ends with how to call it
        self.assertEqual(code, 1)
        self.assertIn("usage:", out)
        repo.close()

    def test_the_script_run_on_its_own_says_how_to_call(self):
        # Given: the script, as the skill runs it
        script = os.path.join(ROOT, "turn", "scripts", "up.py")
        # When: it is run with no command
        done = subprocess.run([sys.executable, script], capture_output=True, text=True)
        # Then: it ends with how to call it
        self.assertEqual(done.returncode, 1)
        self.assertIn("usage:", done.stdout)


if __name__ == "__main__":
    unittest.main()

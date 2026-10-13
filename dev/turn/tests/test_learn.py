import json
import unittest

from helpers import form, Repo, fill, run, started

WORK = "# Note\n\nRun make.\n"
WORK_WAY = "the work: say what make builds"
CALLER_WAY = "what the work should be: name the receiver's machine"
RULE = "read the sources for what each command does"
AIM = "the teammate knows what make gives them"


def decide(repo, folder, f1, b1=True):
    fill(repo, f"{folder}/orchestrator.json", {
        "note B-1": {"met": b1, "lines": "3" if b1 else "", "note": "the step is given" if b1 else ""},
        "note F-1": {"met": f1, "lines": "1-3" if f1 else "", "note": "three lines" if f1 else ""}})


def learn(repo, folder, ways, making=None):
    """The learner's form: for each item, its way to a Good, where the way lies, and what in making
    such work would have given it."""
    fill(repo, f"{folder}/learner.json",
         {i: {"aim": AIM, "way": w.partition(": ")[2], "reach": "3", "in": w.partition(": ")[0],
              "making": (making or {}).get(i, "")} for i, w in ways.items()})


PLACE = {"aim": AIM, "way": "say what make builds", "reach": "3", "in": "the work", "making": ""}


class Learner(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], WORK)
        decide(self.repo, ".turn/out/1", f1=False)

    def tearDown(self):
        self.repo.close()

    def check(self):
        return run(self.repo, "check", ".turn/out", "1", "learner")

    def test_a_way_given_for_every_item_without_a_good_passes(self):
        # Given: the one item left without a Good given a way, in the work
        learn(self.repo, ".turn/out/1", {"note F-1": WORK_WAY})
        # When: the learner's form is checked
        code, out = self.check()
        # Then: it passes
        self.assertEqual((code, out.strip()), (0, "filled"))

    def test_a_learner_form_with_a_place_left_or_wrong_is_stopped_saying_which(self):
        cases = [
            ("no place", {}, "note F-1: not filled"),
            ("no way", {"note F-1": dict(PLACE, way="")}, "note F-1: the way is not given"),
            ("no aim", {"note F-1": dict(PLACE, aim="")}, "note F-1: the aim is not given"),
            ("an aim made from lines", {"note F-1": dict(PLACE, aim="lines 1-3 say it")},
             "note F-1: the aim names lines; say it of the whole work"),
            ("no reach", {"note F-1": dict(PLACE, reach="")}, "note F-1: reach is not given"),
            ("nowhere", {"note F-1": dict(PLACE, **{"in": "luck"})}, "note F-1: in must be one of"),
            ("making not a text", {"note F-1": {k: v for k, v in PLACE.items() if k != "making"}},
             "note F-1: making is not given"),
            ("an item with a Good", {"note F-1": PLACE, "note B-1": PLACE}, "note B-1: has a Good"),
        ]
        for name, filled, said in cases:
            with self.subTest(name):
                # Given: the learner's form with this place left or wrong
                fill(self.repo, ".turn/out/1/learner.json", filled)
                # When: it is checked
                code, out = self.check()
                # Then: it is stopped, naming the place
                self.assertEqual(code, 1)
                self.assertIn(said, out)


class SecondRound(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], WORK)

    def tearDown(self):
        self.repo.close()

    def test_the_second_round_starts_from_the_work_of_the_first(self):
        # Given: round 1 decided with an item without a Good, given a way in the work
        decide(self.repo, ".turn/out/1", f1=False)
        learn(self.repo, ".turn/out/1", {"note F-1": WORK_WAY})
        # When: the second round is started
        code, out = run(self.repo, "round", ".turn/out")
        # Then: the work of round 1 is where the generator makes it again, with fresh forms
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out), {"round": 2, "work": ".turn/out/2/note.md"})
        self.assertEqual(self.repo.read(".turn/out/2/note.md"), WORK)
        self.assertEqual(self.repo.json(form("generator", 2)),
                         {"note B-1": {"lines": ""}, "note F-1": {"lines": ""}})
        self.assertEqual(self.repo.json(".turn/run.json")["round"], 2)

    def test_items_one_way_serves_are_handed_to_the_generator_together(self):
        # Given: one way given for both items, and something learned of making for one
        decide(self.repo, ".turn/out/1", f1=False, b1=False)
        learn(self.repo, ".turn/out/1", {"note F-1": WORK_WAY, "note B-1": WORK_WAY},
              making={"note B-1": RULE})
        run(self.repo, "round", ".turn/out")
        # When: the generator's brief for round 2 is made
        code, out = run(self.repo, "brief", ".turn/out", "2", "generator")
        # Then: the way is handed on once, with both items, and the rule with the constraints
        self.assertEqual(code, 0, out)
        got = self.repo.json(out.strip())
        self.assertEqual(got["ways"], [{"way": "say what make builds", "items": ["note B-1", "note F-1"],
                                        "aims": [AIM], "reach": ["3"]}])
        self.assertEqual(got["constraints"], [f"rule: {RULE}"])

    def test_there_is_no_third_round(self):
        # Given: a second round already started
        decide(self.repo, ".turn/out/1", f1=False)
        learn(self.repo, ".turn/out/1", {"note F-1": WORK_WAY})
        run(self.repo, "round", ".turn/out")
        # When: another round is asked for
        code, out = run(self.repo, "round", ".turn/out")
        # Then: it is refused
        self.assertEqual(code, 1)
        self.assertIn("a run has two rounds at most", out)

    def test_a_second_round_is_not_started_before_the_ways_are_given(self):
        # Given: round 1 decided, the learner's form empty
        decide(self.repo, ".turn/out/1", f1=False)
        # When: the second round is started
        code, out = run(self.repo, "round", ".turn/out")
        # Then: it is refused, naming the place
        self.assertEqual(code, 1)
        self.assertIn("note F-1: not filled", out)
        self.assertFalse(self.repo.exists(".turn/out/2/note.md"))

    def test_a_second_round_is_not_started_when_nothing_in_turn_would_change(self):
        cases = [("every item met", True, {}),
                 ("only what the caller wrote", False,
                  {"note F-1": CALLER_WAY})]
        for name, f1, ways in cases:
            with self.subTest(name):
                # Given: round 1 decided, with no way the generator could take
                decide(self.repo, ".turn/out/1", f1=f1)
                learn(self.repo, ".turn/out/1", ways)
                # When: the second round is started
                code, out = run(self.repo, "round", ".turn/out")
                # Then: it is refused, since round 2 would make nothing again
                self.assertEqual(code, 1)
                self.assertIn("no way for the generator", out)


class EndAfterLearning(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], WORK)

    def tearDown(self):
        self.repo.close()

    def second_round(self, ways, making=None):
        decide(self.repo, ".turn/out/1", f1=False, b1=False)
        learn(self.repo, ".turn/out/1", ways, making)
        code, out = run(self.repo, "round", ".turn/out")
        assert code == 0, out
        self.repo.write(".turn/out/2/note.md", WORK + "\nmake builds the site.\n")

    def test_a_first_round_with_a_way_for_the_generator_does_not_return(self):
        # Given: round 1 left an item without a Good, with a way in the work
        decide(self.repo, ".turn/out/1", f1=False)
        learn(self.repo, ".turn/out/1", {"note F-1": WORK_WAY})
        # When: the run is ended after round 1
        code, out = run(self.repo, "end", ".turn/out", "1")
        # Then: it is refused, so the way is tried in a second round first
        self.assertEqual(code, 1)
        self.assertIn("start the second round", out)
        self.assertFalse(self.repo.exists("out.json"))

    def test_a_run_does_not_return_an_item_without_a_good_before_its_way_is_given(self):
        # Given: round 2 decided with an item without a Good, and no way given for it
        self.second_round({"note F-1": WORK_WAY, "note B-1": WORK_WAY})
        decide(self.repo, ".turn/out/2", f1=False)
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out", "2")
        # Then: it is refused, naming the item
        self.assertEqual(code, 1)
        self.assertIn("note F-1: not filled", out)

    def test_more_returns_with_how_it_would_get_a_good_and_rules_learned_carry_on(self):
        # Given: round 1 learned, for B-1, something of making such work, round 2 met B-1, and F-1
        # is left with a way in the work
        self.second_round({"note F-1": WORK_WAY, "note B-1": WORK_WAY}, making={"note B-1": RULE})
        decide(self.repo, ".turn/out/2", f1=False)
        learn(self.repo, ".turn/out/2", {"note F-1": "the work: cut the second line"})
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out", "2")
        # Then: the work of round 2 is returned, the user asked about F-1 with how it would get a
        # Good, and the rule learned added after the caller's constraints
        self.assertEqual((code, out.strip()), (0, "ask the user"))
        self.assertIn("make builds the site.", self.repo.read("docs/note.md"))
        back = self.repo.json("out.json")
        self.assertEqual(back["semantic_gist"],
                         [{"difference": "note F-1 (Is it short?): cut the second line"}])
        self.assertEqual(back["constraints"], [{"rule": RULE}])
        self.assertEqual(back["episodic_trace"], [{"evidence": ".turn/out/2/orchestrator.json"},
                                                  {"evidence": ".turn/out/2/learner.json"}])

    def test_more_whose_way_lies_in_what_the_caller_wrote_goes_to_the_caller(self):
        # Given: round 2 left F-1 with a way only the caller can take
        self.second_round({"note F-1": WORK_WAY, "note B-1": WORK_WAY})
        decide(self.repo, ".turn/out/2", f1=False)
        learn(self.repo, ".turn/out/2", {"note F-1": CALLER_WAY})
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out", "2")
        # Then: the CCS goes to the caller, saying which item and how
        self.assertEqual(code, 0)
        self.assertEqual(self.repo.json("out.json")["predictive_cue"],
                         [{"next": "to the caller: note F-1: name the receiver's machine"}])

    def test_a_first_round_whose_only_ways_lie_with_the_caller_returns_to_the_caller(self):
        # Given: round 1 left F-1 with a way only the caller can take, and something learned of making
        decide(self.repo, ".turn/out/1", f1=False)
        learn(self.repo, ".turn/out/1", {"note F-1": CALLER_WAY}, making={"note F-1": RULE})
        # When: the run ends after round 1
        code, out = run(self.repo, "end", ".turn/out", "1")
        # Then: it returns to the caller, with what was learned of making as a rule
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("to the caller: note F-1"))
        self.assertEqual(self.repo.json("out.json")["constraints"], [{"rule": RULE}])


if __name__ == "__main__":
    unittest.main()

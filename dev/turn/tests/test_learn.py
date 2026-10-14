import json
import os
import unittest

from helpers import Repo, ccs, fill, run, started

WORK = "# Note\n\nRun make.\n"
WORK_WAY = "the work: say what make builds"
CALLER_WAY = "what the work should be: name the receiver's machine"
RULE = "read the sources for what each command does"
AIM = "the teammate knows what make gives them"


def decide(repo, folder, f1, b1=True):
    fill(
        repo,
        f"{folder}/orchestrator.json",
        {
            "note B-1": {
                "met": b1,
                "lines": "3" if b1 else "",
                "note": "the step is given" if b1 else "",
            },
            "note F-1": {
                "met": f1,
                "lines": "1-3" if f1 else "",
                "note": "three lines" if f1 else "",
            },
        },
    )


def learn(repo, folder, ways, making=None):
    """The learner's form: for each item, its way to a Good, where the way lies, and what in making
    such work would have given it."""
    fill(
        repo,
        f"{folder}/learner.json",
        {
            i: {
                "aim": AIM,
                "way": w.partition(": ")[2],
                "reach": "3",
                "in": w.partition(": ")[0],
                "making": (making or {}).get(i, ""),
            }
            for i, w in ways.items()
        },
    )


PLACE = {"aim": AIM, "way": "say what make builds", "reach": "3", "in": "the work", "making": ""}


class Learner(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], WORK)
        decide(self.repo, ".turn/out", f1=False)

    def tearDown(self):
        self.repo.close()

    def check(self):
        return run(self.repo, "check", ".turn/out", "learner")

    def test_a_way_given_for_every_item_without_a_good_passes(self):
        # Given: the one item left without a Good given a way, in the work
        learn(self.repo, ".turn/out", {"note F-1": WORK_WAY})
        # When: the learner's form is checked
        code, out = self.check()
        # Then: it passes
        self.assertEqual((code, out.strip()), (0, "filled"))

    def test_a_learner_form_with_a_place_left_or_wrong_is_stopped_saying_which(self):
        cases = [
            ("no place", {}, "note F-1: not filled"),
            ("no way", {"note F-1": dict(PLACE, way="")}, "note F-1: the way is not given"),
            ("no aim", {"note F-1": dict(PLACE, aim="")}, "note F-1: the aim is not given"),
            (
                "an aim made from lines",
                {"note F-1": dict(PLACE, aim="lines 1-3 say it")},
                "note F-1: the aim names lines; say it of the whole work",
            ),
            ("no reach", {"note F-1": dict(PLACE, reach="")}, "note F-1: reach is not given"),
            ("nowhere", {"note F-1": dict(PLACE, **{"in": "luck"})}, "note F-1: in must be one of"),
            (
                "making not a text",
                {"note F-1": {k: v for k, v in PLACE.items() if k != "making"}},
                "note F-1: making is not given",
            ),
            ("an item with a Good", {"note F-1": PLACE, "note B-1": PLACE}, "note B-1: has a Good"),
        ]
        for name, filled, said in cases:
            with self.subTest(name):
                # Given: the learner's form with this place left or wrong
                fill(self.repo, ".turn/out/learner.json", filled)
                # When: it is checked
                code, out = self.check()
                # Then: it is stopped, naming the place
                self.assertEqual(code, 1)
                self.assertIn(said, out)


class End(unittest.TestCase):
    """A run has the work read and decided once, and returns each item without a Good with its way,
    for the caller to decide whether to run again."""

    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], WORK)

    def tearDown(self):
        self.repo.close()

    def test_a_run_does_not_return_an_item_without_a_good_before_its_way_is_given(self):
        # Given: the run decided with an item without a Good, and no way given for it
        decide(self.repo, ".turn/out", f1=False)
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: it is refused, naming the item, and nothing is written back
        self.assertEqual(code, 1)
        self.assertIn("note F-1: not filled", out)
        self.assertFalse(self.repo.exists("out.json"))

    def test_more_whose_way_lies_in_the_work_returns_for_the_caller_to_run_again(self):
        # Given: the run decided with F-1 left without a Good, given a way in the work, and
        # something learned of making such work
        decide(self.repo, ".turn/out", f1=False)
        learn(self.repo, ".turn/out", {"note F-1": WORK_WAY}, making={"note F-1": RULE})
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: the user is told where the work is and that running again can give what is not
        # yet there; the work read is where it goes; the CCS asks the user, with F-1 and how it
        # would get a Good, the rule after the caller's constraints, the work and the evidence
        self.assertEqual(code, 0, out)
        self.assertEqual(
            out.splitlines(),
            ["The work is at docs/note.md; running again can give what is not yet there."],
        )
        self.assertEqual(self.repo.read("docs/note.md"), WORK)
        back = self.repo.json("out.json")
        self.assertEqual(back["predictive_cue"], [{"next": "ask the user"}])
        self.assertEqual(
            back["semantic_gist"], [{"difference": "note F-1 (Is it short?): say what make builds"}]
        )
        self.assertEqual(back["constraints"], [{"rule": RULE}])
        self.assertEqual(
            back["episodic_trace"],
            [
                {"work": ".turn/out/note.md"},
                {"evidence": ".turn/out/list.json"},
                {"evidence": ".turn/out/orchestrator.json"},
                {"evidence": ".turn/out/learner.json"},
            ],
        )

    def test_a_rule_the_caller_already_carries_is_returned_once(self):
        # Given: a task carrying a rule an earlier run learned, and this run learning it again
        self.repo.close()
        self.repo = Repo()
        self.repo.write("in.json", json.dumps(ccs(constraints=[{"rule": RULE}])))
        self.assertEqual(run(self.repo, "start", "in.json", "out.json", "s1")[0], 0)
        self.repo.write(".turn/out/note.md", WORK)
        decide(self.repo, ".turn/out", f1=False)
        learn(self.repo, ".turn/out", {"note F-1": WORK_WAY}, making={"note F-1": RULE})
        # When: the run ends
        run(self.repo, "end", ".turn/out")
        # Then: the caller gets the rule once
        self.assertEqual(self.repo.json("out.json")["constraints"], [{"rule": RULE}])

    def test_more_whose_way_lies_in_what_the_caller_wrote_goes_to_the_caller(self):
        # Given: the run left F-1 with a way only the caller can take, and B-1 with a way in the
        # work
        decide(self.repo, ".turn/out", f1=False, b1=False)
        learn(self.repo, ".turn/out", {"note F-1": CALLER_WAY, "note B-1": WORK_WAY})
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: the CCS goes to the caller, saying which item and how, and the user is told so
        self.assertEqual(code, 0)
        said = "to the caller: note F-1: name the receiver's machine"
        self.assertEqual(self.repo.json("out.json")["predictive_cue"], [{"next": said}])
        self.assertEqual(out.splitlines()[0], said)


class RunAgain(unittest.TestCase):
    """A run called again on what a run returned makes the work again on the ways that lie in it,
    from the work as it stands."""

    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], WORK)

    def tearDown(self):
        self.repo.close()

    def again(self):
        """Calls turn again on the CCS the run returned, and makes the generator's brief."""
        self.repo.write("again.json", json.dumps(self.repo.json("out.json")))
        code, out = run(self.repo, "start", "again.json", "out-2.json", "s1")
        assert code == 0, out
        run(self.repo, "aim", ".turn/out-2", AIM)
        code, out = run(self.repo, "brief", ".turn/out-2", "generator")
        assert code == 0, out
        return self.repo.json(out.strip())

    def test_the_generator_is_handed_the_ways_in_the_work_the_earlier_run_gave(self):
        # Given: a run that returned B-1 and F-1 on one way in the work, with something learned
        # of making
        decide(self.repo, ".turn/out", f1=False, b1=False)
        learn(
            self.repo,
            ".turn/out",
            {"note F-1": WORK_WAY, "note B-1": WORK_WAY},
            making={"note B-1": RULE},
        )
        self.assertEqual(run(self.repo, "end", ".turn/out")[0], 0)
        # When: turn is called again on the CCS it returned, and the generator's brief is made
        got = self.again()
        # Then: the generator makes the work again from the work returned, on the way, handed
        # once with both items, and with the rule among the constraints
        self.assertEqual(got["started from"], ".turn/out/note.md")
        self.assertEqual(self.repo.read(got["work"]), WORK)
        self.assertEqual(
            got["ways"],
            [
                {
                    "way": "say what make builds",
                    "items": ["note B-1", "note F-1"],
                    "aims": [AIM],
                    "reach": ["3"],
                }
            ],
        )
        self.assertEqual(got["constraints"], [f"rule: {RULE}"])

    def test_a_way_in_what_the_work_should_be_is_not_handed_to_the_generator(self):
        # Given: a run that returned F-1 with a way only the caller can take
        decide(self.repo, ".turn/out", f1=False)
        learn(self.repo, ".turn/out", {"note F-1": CALLER_WAY})
        self.assertEqual(run(self.repo, "end", ".turn/out")[0], 0)
        # When: turn is called again on the CCS it returned, and the generator's brief is made
        got = self.again()
        # Then: the generator is handed no way
        self.assertEqual(got["ways"], [])

    def test_a_run_whose_earlier_ways_are_gone_is_not_started(self):
        # Given: a run that returned F-1 with a way in the work, and its learner's form removed
        decide(self.repo, ".turn/out", f1=False)
        learn(self.repo, ".turn/out", {"note F-1": WORK_WAY})
        self.assertEqual(run(self.repo, "end", ".turn/out")[0], 0)
        os.remove(os.path.join(self.repo.path, ".turn/out/learner.json"))
        self.repo.write("again.json", json.dumps(self.repo.json("out.json")))
        # When: turn is called again on the CCS it returned
        code, out = run(self.repo, "start", "again.json", "out-2.json", "s1")
        # Then: it ends before any work, saying why
        self.assertEqual(code, 1)
        self.assertIn(".turn/out/learner.json is not there", out)
        self.assertFalse(self.repo.exists(".turn/out-2"))

    def test_a_ccs_an_earlier_version_returned_is_carried_on_with_its_ways(self):
        # Given: a CCS turn 0.1.0 returned, whose work and learner's form lie in its round folders
        self.repo.write(".turn/old/2/note.md", WORK)
        self.repo.write(".turn/old/2/learner.json", json.dumps({"note F-1": PLACE}))
        returned = ccs(
            predictive_cue=[{"next": "ask the user"}],
            episodic_trace=[
                {"work": ".turn/old/2/note.md"},
                {"evidence": ".turn/old/list.json"},
                {"evidence": ".turn/old/2/orchestrator.json"},
                {"evidence": ".turn/old/2/learner.json"},
            ],
        )
        self.repo.write("again.json", json.dumps(returned))
        # When: turn is called on it, and the generator's brief is made
        self.assertEqual(run(self.repo, "start", "again.json", "out-2.json", "s1")[0], 0)
        run(self.repo, "aim", ".turn/out-2", AIM)
        code, out = run(self.repo, "brief", ".turn/out-2", "generator")
        # Then: the generator makes the work again from that work, on its way in the work
        self.assertEqual(code, 0, out)
        got = self.repo.json(out.strip())
        self.assertEqual(got["started from"], ".turn/old/2/note.md")
        self.assertEqual([w["way"] for w in got["ways"]], ["say what make builds"])


if __name__ == "__main__":
    unittest.main()

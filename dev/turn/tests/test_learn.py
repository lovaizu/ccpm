import json
import unittest

from helpers import Repo, ccs, fill, run, started

WORK = "# Note\n\nRun make.\n"
WORK_WAY = "the work: say what make builds"
CALLER_WAY = "what the work should be: name the receiver's machine"
RULE = "read the sources for what each command does"
AIM = "the teammate knows what make gives them"
LICENSE = "Which license is the note under? The notes do not say."


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


SECOND = ".turn/out/2"


def second(repo, ways, making=None):
    """The first round of the run ended on ways in the work, and the second begun, its work made
    again."""
    decide(repo, ".turn/out", f1=False, b1="note B-1" not in ways)
    learn(repo, ".turn/out", ways, making)
    code, out = run(repo, "end", ".turn/out")
    assert code == 0, out
    repo.write(f"{SECOND}/work/docs/note.md", WORK)


PLACE = {"aim": AIM, "way": "say what make builds", "reach": "3", "in": "the work", "making": ""}


class Learner(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"][0], WORK)
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
        self.repo.write(self.got["work"][0], WORK)

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

    def test_more_whose_way_lies_in_the_work_starts_the_runs_second_reading(self):
        # Given: the first round decided with F-1 left without a Good, given a way in the work,
        # and something learned of making such work
        decide(self.repo, ".turn/out", f1=False)
        learn(self.repo, ".turn/out", {"note F-1": WORK_WAY}, making={"note F-1": RULE})
        # When: the reading ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: nothing is returned to the caller yet, and nothing is where the work goes; the
        # second reading begins in its own folder, its generator handed the way and the work read,
        # and the rule is kept out of the constraints
        self.assertEqual(code, 0, out)
        self.assertFalse(self.repo.exists("out.json"))
        self.assertFalse(self.repo.exists("docs/note.md"))
        self.assertEqual(json.loads(out)["folder"], SECOND)
        self.assertEqual(run(self.repo, "aim", SECOND, AIM)[0], 0)
        code, out = run(self.repo, "brief", SECOND, "generator")
        self.assertEqual(code, 0, out)
        got = self.repo.json(out.strip())
        self.assertEqual(self.repo.read(got["work"][0]), WORK)
        self.assertEqual([w["way"] for w in got["ways"]], ["say what make builds"])
        self.assertEqual(got["constraints"], [])

    def test_more_after_the_second_reading_returns_for_the_caller_to_decide(self):
        # Given: a second round that again left F-1 without a Good, given a way in the work
        second(self.repo, {"note F-1": WORK_WAY}, making={"note F-1": RULE})
        decide(self.repo, SECOND, f1=False)
        learn(self.repo, SECOND, {"note F-1": WORK_WAY}, making={"note F-1": RULE})
        # When: the reading ends
        code, out = run(self.repo, "end", SECOND)
        # Then: the user is told where the work is and that the CCS holds what it does not give
        # yet; the CCS asks the user, with F-1 unmet and how it would get a Good, the rule once in
        # turn's part, the caller's parts as given, and the second round's evidence
        self.assertEqual(code, 0, out)
        self.assertEqual(
            out.splitlines(),
            ["The work is at docs/note.md, with what it does not give yet in the CCS."],
        )
        back = self.repo.json("out.json")
        sent = self.repo.json("in.json")
        for part in ("focal_entities", "goal_orientation", "retrieved_artifacts", "constraints"):
            self.assertEqual(back[part], sent[part])
        self.assertEqual(back["predictive_cue"], [{"next": "ask the user"}])
        self.assertEqual(
            back["semantic_gist"],
            [{"unmet": "note F-1 (Is it short?): say what make builds"}, {"rule": RULE}],
        )
        self.assertEqual(
            back["episodic_trace"],
            [
                {"evidence": f"{SECOND}/list.json"},
                {"evidence": f"{SECOND}/orchestrator.json"},
                {"evidence": f"{SECOND}/learner.json"},
            ],
        )

    def test_a_second_reading_with_every_item_met_returns_done(self):
        # Given: a second round that met every item
        second(self.repo, {"note F-1": WORK_WAY})
        decide(self.repo, SECOND, f1=True)
        # When: the reading ends
        code, out = run(self.repo, "end", SECOND)
        # Then: the work is returned done
        self.assertEqual(code, 0, out)
        self.assertEqual(self.repo.json("out.json")["predictive_cue"], [{"next": "done"}])

    def test_a_rule_learned_in_both_rounds_is_returned_once_and_the_caller_s_rules_kept(self):
        # Given: a task carrying a rule of the caller's, and both rounds learning another
        self.repo.close()
        self.repo = Repo()
        mine = {"rule": "write for a first day"}
        self.repo.write("in.json", json.dumps(ccs(constraints=[mine])))
        self.assertEqual(run(self.repo, "start", "in.json", "out.json", "s1")[0], 0)
        self.repo.write(".turn/out/work/docs/note.md", WORK)
        second(self.repo, {"note F-1": WORK_WAY}, making={"note F-1": RULE})
        decide(self.repo, SECOND, f1=False)
        learn(self.repo, SECOND, {"note F-1": WORK_WAY}, making={"note F-1": RULE})
        # When: the run ends
        run(self.repo, "end", SECOND)
        # Then: the caller gets the learned rule once in turn's part, and its own rules as given
        back = self.repo.json("out.json")
        self.assertEqual([e for e in back["semantic_gist"] if "rule" in e], [{"rule": RULE}])
        self.assertEqual(back["constraints"], [mine])

    def test_a_rule_learned_in_the_first_reading_alone_is_returned(self):
        # Given: the first round learned a rule, and the second met every item
        second(self.repo, {"note F-1": WORK_WAY}, making={"note F-1": RULE})
        decide(self.repo, SECOND, f1=True)
        # When: the run ends
        run(self.repo, "end", SECOND)
        # Then: the caller gets the rule
        self.assertEqual(self.repo.json("out.json")["semantic_gist"], [{"rule": RULE}])

    def test_a_question_left_open_is_carried_into_the_second_reading_and_asked_at_the_end(self):
        # Given: the first round left F-1 with a way in the work, and a question left open
        fill(self.repo, ".turn/out/questions.json", [{"question": LICENSE, "ask": True}])
        second(self.repo, {"note F-1": WORK_WAY})
        # When: the second round meets every item and ends
        self.assertEqual(
            self.repo.json(f"{SECOND}/questions.json"), [{"question": LICENSE, "ask": True}]
        )
        decide(self.repo, SECOND, f1=True)
        code, out = run(self.repo, "end", SECOND)
        # Then: the question is still open, and the user is asked it at the end
        self.assertEqual(code, 0, out)
        self.assertEqual(out.splitlines()[1], f"❓ {LICENSE}")
        back = self.repo.json("out.json")
        self.assertEqual(back["predictive_cue"], [{"next": "ask the user"}])
        self.assertEqual(back["semantic_gist"], [{"question": LICENSE}])

    def test_a_second_reading_stopped_returns_to_the_caller(self):
        # Given: the second round begun
        second(self.repo, {"note F-1": WORK_WAY})
        # When: the user stops it
        code, out = run(self.repo, "stop", SECOND)
        # Then: the caller gets a CCS saying so
        self.assertEqual(code, 0, out)
        back = self.repo.json("out.json")
        self.assertEqual(back["predictive_cue"], [{"next": "stopped: write"}])
        self.assertEqual(back["episodic_trace"], [])

    def test_more_whose_way_lies_in_what_the_caller_wrote_goes_to_the_caller(self):
        # Given: the first round left F-1 with a way only the caller can take, and nothing in the
        # work
        decide(self.repo, ".turn/out", f1=False)
        learn(self.repo, ".turn/out", {"note F-1": CALLER_WAY})
        # When: the reading ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: no second round begins; the CCS goes to the caller, saying which item and how,
        # and the user is told so
        self.assertEqual(code, 0)
        said = "to the caller: note F-1: name the receiver's machine"
        self.assertEqual(self.repo.json("out.json")["predictive_cue"], [{"next": said}])
        self.assertEqual(out.splitlines()[0], said)
        self.assertFalse(self.repo.exists(SECOND))

    def test_a_way_in_what_the_caller_wrote_waits_for_the_second_reading_to_end(self):
        # Given: the first round left F-1 with a way only the caller can take, and B-1 with a
        # way in the work
        decide(self.repo, ".turn/out", f1=False, b1=False)
        learn(self.repo, ".turn/out", {"note F-1": CALLER_WAY, "note B-1": WORK_WAY})
        # When: the reading ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: the second round begins, and nothing goes to the caller yet
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["folder"], SECOND)
        self.assertFalse(self.repo.exists("out.json"))


class RunAgain(unittest.TestCase):
    """A run called again makes the work anew from the caller's inputs; the work an earlier run
    returned is not one of them."""

    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"][0], WORK)
        second(self.repo, {"note F-1": WORK_WAY})
        decide(self.repo, SECOND, f1=False)
        learn(self.repo, SECOND, {"note F-1": WORK_WAY})
        assert run(self.repo, "end", SECOND)[0] == 0

    def tearDown(self):
        self.repo.close()

    def test_called_again_the_generator_makes_the_work_anew_with_no_way(self):
        # Given: a run that returned F-1 unmet with a way in the work
        # When: turn is called again on the same task, and the generator's brief is made
        code, out = run(self.repo, "start", "in.json", "out-2.json", "s1")
        self.assertEqual(code, 0, out)
        run(self.repo, "aim", ".turn/out-2", AIM)
        code, out = run(self.repo, "brief", ".turn/out-2", "generator")
        # Then: the generator is handed no way and no work to start from
        self.assertEqual(code, 0, out)
        got = self.repo.json(out.strip())
        self.assertEqual(got["ways"], [])
        self.assertFalse(self.repo.exists(".turn/out-2/work/docs/note.md"))

    def test_the_work_a_run_returned_is_written_over_while_unchanged_and_kept_once_changed(self):
        cases = [("unchanged", None, 0), ("changed by the user since", "# Mine\n", 1)]
        for name, edited, code in cases:
            with self.subTest(name):
                # Given: the work the run returned where it goes, not committed, edited or not
                if edited:
                    self.repo.write("docs/note.md", edited)
                # When: turn is called again
                got, out = run(self.repo, "start", "in.json", f"out-{name[0]}.json", "s1")
                # Then: it starts while the run's evidence keeps the file as it stands, and ends
                # before any work once the user changed it
                self.assertEqual(got, code, out)
                if code:
                    self.assertIn("docs/note.md has changes git does not hold", out)


if __name__ == "__main__":
    unittest.main()

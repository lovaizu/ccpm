import unittest

from helpers import Repo, ccs, fill, form, run, started

WORK = "# Note\n\nRun make.\n"
LICENSE = "Which license is the note under? The notes do not say, so the note leaves it out."
NAME = "What is the tool called? The notes do not say."


def decided(repo, n=1):
    """Every item decided met, before the reading and after it."""
    for role in ("hand-on", "orchestrator"):
        fill(repo, form(role, n), {
            "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
            "note F-1": {"met": True, "lines": "1-3", "note": "three lines"}})


class Questions(unittest.TestCase):
    """What the sources leave open is asked of the user, and nothing else."""

    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"], WORK)
        fill(self.repo, form("generator"), {"note B-1": {"lines": "3"}, "note F-1": {"lines": "1-3"}})

    def tearDown(self):
        self.repo.close()

    def check(self, role):
        return run(self.repo, "check", ".turn/out", "1", role)

    def test_a_run_starts_with_no_question_and_says_where_they_are_kept(self):
        # Given: a run just started
        # When: the generator's brief is made
        code, out = run(self.repo, "brief", ".turn/out", "1", "generator")
        # Then: the questions are an empty list, and both the orchestrator and the generator are
        # told where they are
        self.assertEqual(self.repo.json(form("questions")), [])
        self.assertEqual(self.got["questions"], form("questions"))
        self.assertEqual(self.repo.json(out.strip())["questions"], form("questions"))

    def test_a_question_without_its_words_is_stopped(self):
        cases = [("no question", [{"question": ""}], "question 1: the question is not given"),
                 ("not a list", {"question": LICENSE}, "the questions are not a list")]
        for name, questions, said in cases:
            with self.subTest(name):
                # Given: the generator's questions with a question left empty, or not a list
                fill(self.repo, form("questions"), questions)
                # When: the generator's form is checked
                code, out = self.check("generator")
                # Then: it is stopped, naming the question
                self.assertEqual(code, 1)
                self.assertIn(said, out)

    def test_each_question_must_be_decided_before_the_work_is_handed_on(self):
        decided(self.repo)
        cases = [
            ("asked", [{"question": LICENSE, "ask": True, "answered": ""}], None),
            ("dropped with where it is answered",
             [{"question": NAME, "ask": False, "answered": "notes.md 1 names it"}], None),
            ("undecided", [{"question": LICENSE}], "question 1: not decided"),
            ("dropped without where it is answered", [{"question": NAME, "ask": False, "answered": ""}],
             "question 1: where it is answered is not given"),
        ]
        for name, questions, said in cases:
            with self.subTest(name):
                # Given: the questions decided so
                fill(self.repo, form("questions"), questions)
                # When: the orchestrator's form before the reading is checked
                code, out = self.check("hand-on")
                # Then: it passes only when each question is asked, or dropped with where it is answered
                if said is None:
                    self.assertEqual((code, out.strip()), (0, "filled"))
                else:
                    self.assertEqual(code, 1)
                    self.assertIn(said, out)

    def test_only_the_questions_asked_go_back_to_the_user(self):
        # Given: every item met, one question asked and one dropped as answered
        decided(self.repo)
        fill(self.repo, form("questions"), [
            {"question": LICENSE, "ask": True, "answered": ""},
            {"question": NAME, "ask": False, "answered": "notes.md 1 names it"}])
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out", "1")
        # Then: the user is asked the one question, and it is shown with ❓
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines(), ["ask the user", f"❓ {LICENSE}"])
        back = self.repo.json("out.json")
        self.assertEqual(back["predictive_cue"], [{"next": "ask the user"}])
        self.assertEqual(back["uncertainty_signal"], [{"gap": LICENSE}])

    def test_a_run_does_not_return_with_a_question_undecided(self):
        # Given: every item met, and a question not decided
        decided(self.repo)
        fill(self.repo, form("questions"), [{"question": LICENSE}])
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out", "1")
        # Then: it is refused, and nothing is written back
        self.assertEqual(code, 1)
        self.assertIn("question 1: not decided", out)
        self.assertFalse(self.repo.exists("out.json"))

    def test_the_users_answer_reaches_the_generator(self):
        # Given: a task carrying the user's answer to a question asked before
        repo = Repo()
        self.addCleanup(repo.close)
        started(repo, ccs(constraints=[{"answer": "MIT"}]))
        # When: the generator's brief is made
        code, out = run(repo, "brief", ".turn/out", "1", "generator")
        # Then: the answer is among what the work should be
        self.assertEqual(repo.json(out.strip())["constraints"], ["answer: MIT"])

    def test_the_second_round_starts_from_the_questions_of_the_first(self):
        # Given: round 1 asked a question and left F-1 with a way in the work
        fill(self.repo, form("questions"), [{"question": LICENSE, "ask": True, "answered": ""}])
        fill(self.repo, form("orchestrator"), {
            "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
            "note F-1": {"met": False, "lines": "", "note": ""}})
        fill(self.repo, form("learner"), {"note F-1": {"way": "cut it", "in": "the work", "making": ""}})
        # When: the second round starts
        code, out = run(self.repo, "round", ".turn/out")
        # Then: its questions are the first round's, for the generator to keep or settle
        self.assertEqual(code, 0, out)
        self.assertEqual(self.repo.json(form("questions", 2)),
                         [{"question": LICENSE, "ask": True, "answered": ""}])


if __name__ == "__main__":
    unittest.main()

import os
import tempfile
import unittest
from unittest import mock

from helpers import Repo, ccs, fill, form, run, started
from repo import drop

import stop
from test_step_hooks import hook

WORK = "# Note\n\nRun make.\n"
QUESTIONS = ".turn/out/questions.json"
LICENSE = "Which license is the note under? The notes do not say, so the note leaves it out."
NAME = "What is the tool called? The notes do not say."
OPEN = {"question": LICENSE, "ask": True}
ANSWERED = {"question": LICENSE, "ask": True, "answer": "MIT"}


def seen(repo, f1=None):
    """The orchestrator's form before the reading, with F-1 met, or waiting on question 1 when not."""
    fill(repo, form("hand-on"), {
        "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
        "note F-1": {"met": True, "lines": "1-3", "note": "three lines"} if f1 is None else
        {"met": False, "aim": "the teammate knows the terms", "way": "name the license", "reach": "1",
         "question": f1}})


def decided(repo, f1=True):
    fill(repo, form("orchestrator"), {
        "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
        "note F-1": {"met": f1, "lines": "1-3" if f1 else "", "note": "three lines" if f1 else ""}})


class Questions(unittest.TestCase):
    """What the sources leave open is asked of the user at once, and the answer reaches the work."""

    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo, ccs(constraints=[{"language": "English"}]))
        run(self.repo, "aim", ".turn/out", "1", "a new teammate can start work alone")
        self.repo.write(self.got["work"], WORK)
        fill(self.repo, form("generator"), {"note B-1": {"lines": "3"}, "note F-1": {"lines": "1-3"}})

    def tearDown(self):
        self.repo.close()

    def check(self, role):
        return run(self.repo, "check", ".turn/out", "1", role)

    def test_a_run_starts_with_no_question_and_the_orchestrator_is_given_what_settles_them(self):
        # Given: a run just started
        # When: the generator's brief is made
        code, out = run(self.repo, "brief", ".turn/out", "1", "generator")
        # Then: the questions are an empty list kept for the whole run, and the orchestrator is
        # given the sources and constraints to see what they leave open
        self.assertEqual(self.repo.json(QUESTIONS), [])
        self.assertEqual(self.got["questions"], QUESTIONS)
        self.assertEqual((self.got["sources"], self.got["constraints"]), (["notes.md"], ["language: English"]))
        self.assertEqual(self.repo.json(out.strip())["questions"], QUESTIONS)

    def test_a_question_without_its_words_or_naming_an_item_is_stopped(self):
        cases = [("no question", [{"question": ""}], "question 1: the question is not given"),
                 ("not a list", {"question": LICENSE}, "the questions are not a list"),
                 ("an item named", [{"question": f"{LICENSE} (note F-1)"}],
                  "question 1: names note F-1; say in plain words what the work leaves out")]
        for name, questions, said in cases:
            with self.subTest(name):
                # Given: the questions with one left without its words, naming an item, or not a list
                fill(self.repo, QUESTIONS, questions)
                # When: the generator's form is checked
                code, out = self.check("generator")
                # Then: it is stopped, naming the question
                self.assertEqual(code, 1)
                self.assertIn(said, out)

    def test_each_question_and_each_item_waiting_on_one_must_be_decided_before_the_reading(self):
        cases = [
            ("asked", [OPEN], None, None),
            ("dropped with where it is answered", [{"question": NAME, "ask": False, "answered": "notes.md 1"}],
             None, None),
            ("an item waiting on a question asked", [OPEN], 1, None),
            ("undecided", [{"question": LICENSE}], None, "question 1: not decided"),
            ("dropped without where it is answered", [{"question": NAME, "ask": False}], None,
             "question 1: where it is answered is not given"),
            ("an item waiting on no question asked", [OPEN], 2, "note F-1: question 2 is not asked"),
        ]
        for name, questions, waits, said in cases:
            with self.subTest(name):
                # Given: the questions decided so, and F-1 met or waiting on a question
                fill(self.repo, QUESTIONS, questions)
                seen(self.repo, waits)
                # When: the orchestrator's form before the reading is checked
                code, out = self.check("hand-on")
                # Then: it passes only when each question is asked or shown answered, and an item
                # waits only on a question asked
                if said is None:
                    self.assertEqual((code, out.strip()), (0, "filled"))
                else:
                    self.assertEqual(code, 1)
                    self.assertIn(said, out)

    def test_the_users_answers_reach_the_generator(self):
        # Given: the user has answered a question
        fill(self.repo, QUESTIONS, [ANSWERED, {"question": NAME, "ask": False, "answered": "notes.md 1"}])
        # When: the generator's brief is made
        code, out = run(self.repo, "brief", ".turn/out", "1", "generator")
        # Then: the answer is among what the work should be
        self.assertEqual(self.repo.json(out.strip())["constraints"],
                         ["language: English", f"answer: {LICENSE} MIT"])

    def test_the_work_is_not_read_while_a_question_waits_for_the_user(self):
        cases = [("open", [OPEN], None, "question 1 is not answered"),
                 ("answered", [ANSWERED], None, None),
                 ("answered, with an item still waiting on it", [ANSWERED], 1, "not yet: note F-1")]
        for name, questions, waits, said in cases:
            with self.subTest(name):
                # Given: a question so, and F-1 met or waiting on it
                fill(self.repo, QUESTIONS, questions)
                seen(self.repo, waits)
                # When: the first user's brief is asked for
                code, out = run(self.repo, "brief", ".turn/out", "1", "first-user")
                # Then: it is made only once the user has answered, and no item waits on an answer
                # given
                if said is None:
                    self.assertEqual(code, 0, out)
                    drop(self.repo.json(out.strip())["copy"])
                else:
                    self.assertEqual(code, 1)
                    self.assertIn(said, out)

    def test_answers_return_in_the_ccs_after_the_callers_constraints(self):
        # Given: one question answered, one answered by the notes, and every item met
        fill(self.repo, QUESTIONS, [ANSWERED, {"question": NAME, "ask": False, "answered": "notes.md 1"}])
        seen(self.repo)
        decided(self.repo)
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out", "1")
        # Then: the user's answer follows the caller's constraints, and nothing is left for the user
        self.assertEqual(code, 0, out)
        self.assertEqual(out.splitlines()[0], "done")
        back = self.repo.json("out.json")
        self.assertEqual(back["constraints"], [{"language": "English"}, {"answer": f"{LICENSE} MIT"}])
        self.assertEqual(back["uncertainty_signal"], [])

    def test_a_run_does_not_return_with_a_question_open(self):
        for name, questions, said in [("undecided", [{"question": LICENSE}], "question 1: not decided"),
                                      ("not answered", [OPEN], "question 1 is not answered"),
                                      ("marked as left", [dict(OPEN, left=True)], "question 1 is not answered")]:
            with self.subTest(name):
                # Given: every item met, and a question not decided or not answered
                seen(self.repo)
                decided(self.repo)
                fill(self.repo, QUESTIONS, questions)
                # When: the run ends
                code, out = run(self.repo, "end", ".turn/out", "1")
                # Then: it is refused, and nothing is written back
                self.assertEqual(code, 1)
                self.assertIn(said, out)
                self.assertFalse(self.repo.exists("out.json"))

    def test_the_orchestrator_may_stop_while_it_waits_for_the_user_or_the_generator(self):
        run(self.repo, "brief", ".turn/out", "1", "generator")
        fill(self.repo, form("generator"), {"note B-1": {"lines": "3"}, "note F-1": {"lines": "1-3"}})
        cases = [("a question open", [OPEN], False, 0),
                 ("the generator at work", [ANSWERED], True, 0),
                 ("nothing to wait for", [ANSWERED], False, 2)]
        for name, questions, at_work, kept in cases:
            with self.subTest(name):
                # Given: the questions so, and the generator handed its brief after its form or not
                fill(self.repo, QUESTIONS, questions)
                brief = os.path.join(self.repo.path, ".turn/out/1/generator-brief.json")
                later = os.path.getmtime(os.path.join(self.repo.path, form("generator"))) + (1 if at_work else -1)
                os.utime(brief, (later, later))
                # When: the orchestrator stops
                code, said = hook(stop, self.repo, hook_event_name="Stop", stop_hook_active=False)
                # Then: it may stop while it waits, and is kept at work otherwise
                self.assertEqual(code, kept, said)


class LearnersQuestions(unittest.TestCase):
    """A way to a Good that needs what only the user can decide is asked before the second round."""

    def setUp(self):
        self.repo = Repo()
        self.home = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"HOME": self.home.name})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(self.home.cleanup)
        self.addCleanup(self.repo.close)
        started(self.repo)
        self.repo.write(".turn/out/1/note.md", WORK)
        seen(self.repo)
        decided(self.repo, f1=False)
        fill(self.repo, form("learner"), {"note F-1": {
            "aim": "the teammate knows the terms", "way": "say the terms, from the answer to question 1",
            "reach": "1", "in": "the work", "making": ""}})

    def test_the_learner_is_told_where_the_questions_are(self):
        # Given: the records of the run's agents
        folder = os.path.join(self.home.name, ".claude/projects/p/s1/subagents")
        os.makedirs(folder)
        for role in ("first-user", "generator"):
            with open(os.path.join(folder, f"agent-{role}.meta.json"), "w") as f:
                f.write('{"agentType": "turn:%s"}' % role)
            open(os.path.join(folder, f"agent-{role}.jsonl"), "w").close()
        # When: the learner's brief is made
        code, out = run(self.repo, "brief", ".turn/out", "1", "learner")
        # Then: it says where to add a question
        self.assertEqual(code, 0, out)
        self.assertEqual(self.repo.json(out.strip())["questions"], QUESTIONS)

    def test_a_learners_question_without_its_words_is_stopped(self):
        # Given: the learner added a question without its words
        fill(self.repo, QUESTIONS, [{"question": ""}])
        # When: the learner's form is checked
        code, out = run(self.repo, "check", ".turn/out", "1", "learner")
        # Then: it is stopped, naming the question
        self.assertEqual(code, 1)
        self.assertIn("question 1: the question is not given", out)

    def test_the_second_round_starts_only_once_each_question_is_decided(self):
        for name, questions, said in [("undecided", [{"question": LICENSE}], "question 1: not decided"),
                                      ("asked", [OPEN], None)]:
            with self.subTest(name):
                # Given: the learner's question, decided by the orchestrator or not
                fill(self.repo, QUESTIONS, questions)
                # When: the second round is asked for
                code, out = run(self.repo, "round", ".turn/out")
                # Then: it starts only once the question is decided; the generator may work while
                # the user answers
                if said is None:
                    self.assertEqual(code, 0, out)
                else:
                    self.assertEqual(code, 1)
                    self.assertIn(said, out)


if __name__ == "__main__":
    unittest.main()

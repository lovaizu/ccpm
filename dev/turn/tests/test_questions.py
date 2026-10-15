import json
import os
import tempfile
import unittest
from unittest import mock

import stop
from helpers import Repo, ccs, fill, form, run, started
from test_step_hooks import hook

WORK = "# Note\n\nRun make.\n"
QUESTIONS = ".turn/out/questions.json"
LICENSE = "Which license is the note under? The notes do not say, so the note leaves it out."
NAME = "What is the tool called? The notes do not say."
OPEN = {"question": LICENSE, "ask": True}


def seen(repo, f1=None):
    """The orchestrator's form before the reading, with F-1 met, waiting on question f1 when it is
    a number, or not met and waiting on no question when it is 0."""
    unmet = {
        "met": False,
        "aim": "the teammate knows the terms",
        "way": "name the license",
        "reach": "1",
    }
    fill(
        repo,
        form("hand-on"),
        {
            "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
            "note F-1": {"met": True, "lines": "1-3", "note": "three lines"}
            if f1 is None
            else unmet
            if f1 == 0
            else dict(unmet, question=f1),
        },
    )


def decided(repo, f1=True):
    fill(
        repo,
        form("orchestrator"),
        {
            "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
            "note F-1": {
                "met": f1,
                "lines": "1-3" if f1 else "",
                "note": "three lines" if f1 else "",
            },
        },
    )


class Questions(unittest.TestCase):
    """What the sources leave open is left out of the work, and asked of the user only at the end."""

    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo, ccs(constraints=[{"language": "English"}]))
        run(self.repo, "aim", ".turn/out", "a new teammate can start work alone")
        self.repo.write(self.got["work"], WORK)
        fill(
            self.repo, form("generator"), {"note B-1": {"lines": "3"}, "note F-1": {"lines": "1-3"}}
        )

    def tearDown(self):
        self.repo.close()

    def check(self, role):
        return run(self.repo, "check", ".turn/out", role)

    def test_a_run_starts_with_no_question_and_the_orchestrator_is_given_what_settles_them(self):
        # Given: a run just started
        # When: the generator's brief is made
        _code, out = run(self.repo, "brief", ".turn/out", "generator")
        # Then: the questions are an empty list kept for the whole run, and the orchestrator is
        # given the content, the references and the constraints to see what they leave open
        self.assertEqual(self.repo.json(QUESTIONS), [])
        self.assertEqual(self.got["questions"], QUESTIONS)
        self.assertEqual(
            (self.got["content"], self.got["references"], self.got["constraints"]),
            (["notes.md"], [], ["language: English"]),
        )
        self.assertEqual(self.repo.json(out.strip())["questions"], QUESTIONS)

    def test_a_question_without_its_words_or_naming_an_item_is_stopped(self):
        cases = [
            ("no question", [{"question": ""}], "question 1: the question is not given"),
            ("not a list", {"question": LICENSE}, "the questions are not a list"),
            (
                "an item named",
                [{"question": f"{LICENSE} (note F-1)"}],
                "question 1: names note F-1; say in plain words what the work leaves out",
            ),
        ]
        for name, questions, said in cases:
            with self.subTest(name):
                # Given: the questions with one left without its words, naming an item, or not a list
                fill(self.repo, QUESTIONS, questions)
                # When: the generator's form is checked
                code, out = self.check("generator")
                # Then: it is stopped, naming the question
                self.assertEqual(code, 1)
                self.assertIn(said, out)

    def test_the_generator_names_for_an_item_left_out_the_question_it_waits_on(self):
        cases = [
            ("waiting on the question it added", {"question": 1}, None),
            ("neither lines nor a question", {}, "note F-1: lines are not given"),
            ("waiting on a question not added", {"question": 2}, "note F-1: question 2 is not"),
        ]
        for name, place, said in cases:
            with self.subTest(name):
                # Given: the generator left F-1 out of the work, added the question it waits on,
                # and wrote of F-1 the question, no lines, or a question it did not add
                fill(self.repo, QUESTIONS, [{"question": LICENSE}])
                fill(self.repo, form("generator"), {"note B-1": {"lines": "3"}, "note F-1": place})
                # When: the generator's form is checked
                code, out = self.check("generator")
                # Then: it passes only with a question added, and otherwise says to give the lines
                # or the question's number
                if said is None:
                    self.assertEqual((code, out.strip()), (0, "filled"))
                else:
                    self.assertEqual(code, 1)
                    self.assertIn(said, out)
                    self.assertIn("or, where the work leaves the item out until a question", out)

    def test_each_question_and_each_item_waiting_on_one_must_be_decided_before_the_reading(self):
        cases = [
            ("asked", [OPEN], None, None),
            (
                "dropped with where it is answered",
                [{"question": NAME, "ask": False, "answered": "notes.md 1"}],
                None,
                None,
            ),
            ("an item waiting on a question asked", [OPEN], 1, None),
            ("undecided", [{"question": LICENSE}], None, "question 1: not decided"),
            (
                "dropped without where it is answered",
                [{"question": NAME, "ask": False}],
                None,
                "question 1: where it is answered is not given",
            ),
            (
                "an item waiting on no question asked",
                [OPEN],
                2,
                "note F-1: question 2 is not asked",
            ),
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

    def test_the_work_is_read_with_a_question_left_open_but_not_with_an_item_unseen(self):
        cases = [
            ("a question left open", [OPEN], None, None),
            ("an item waiting on the question left open", [OPEN], 1, None),
            ("an item not seen given, waiting on no question", [OPEN], 0, "not yet: note F-1"),
        ]
        for name, questions, waits, said in cases:
            with self.subTest(name):
                # Given: a question left open, and F-1 met, waiting on it, or not seen given
                fill(self.repo, QUESTIONS, questions)
                seen(self.repo, waits)
                # When: the first user's brief is asked for
                code, out = run(self.repo, "brief", ".turn/out", "first-user")
                # Then: the work goes to the reading without waiting for the user, and goes back to
                # the generator only for an item that waits on no question
                if said is None:
                    self.assertEqual(code, 0, out)
                else:
                    self.assertEqual(code, 1)
                    self.assertIn(said, out)

    def test_a_question_left_open_ends_the_run_by_asking_the_user(self):
        # Given: every item met, one question left open, and one answered by the notes
        fill(
            self.repo,
            QUESTIONS,
            [OPEN, {"question": NAME, "ask": False, "answered": "notes.md 1"}],
        )
        seen(self.repo)
        decided(self.repo)
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: the work is written, the user is asked the question left open and nothing else,
        # and the CCS returns it for the caller to put to the user, its own constraints as given
        self.assertEqual(code, 0, out)
        self.assertEqual(
            out.splitlines(),
            ["The work is at docs/note.md, waiting on you for one point.", f"❓ {LICENSE}"],
        )
        self.assertTrue(self.repo.exists("docs/note.md"))
        back = self.repo.json("out.json")
        self.assertEqual(back["predictive_cue"], [{"next": "ask the user"}])
        self.assertEqual(back["semantic_gist"], [{"question": LICENSE}])
        self.assertEqual(back["constraints"], [{"language": "English"}])

    def test_called_again_with_the_answer_in_the_content_the_run_makes_the_work_anew(self):
        # Given: a run that ended asking the user, and the caller adding the answer to the content
        fill(self.repo, QUESTIONS, [OPEN])
        seen(self.repo)
        decided(self.repo)
        run(self.repo, "end", ".turn/out")
        self.repo.write("notes.md", "Run make.\nThe note is under MIT.\n")
        # When: turn is called again on the same task, the returned work not committed
        code, out = run(self.repo, "start", "in.json", "out-2.json", "s1")
        # Then: the new run starts with no work yet, and the orchestrator is given the content
        # holding the answer
        self.assertEqual(code, 0, out)
        got = json.loads(out)
        self.assertFalse(self.repo.exists(got["work"]))
        self.assertIn("MIT", self.repo.read(got["content"][0]))

    def test_called_again_after_the_returned_work_was_changed_the_run_is_refused(self):
        # Given: a run that ended asking the user, and its work changed since, not committed
        fill(self.repo, QUESTIONS, [OPEN])
        seen(self.repo)
        decided(self.repo)
        run(self.repo, "end", ".turn/out")
        self.repo.write("docs/note.md", WORK + "A line of the user's.\n")
        self.repo.write("again.json", json.dumps(self.repo.json("out.json")))
        # When: turn is called again on the CCS it returned
        code, out = run(self.repo, "start", "again.json", "out-2.json", "s1")
        # Then: it is refused, so the user's line is not written over
        self.assertEqual(code, 1)
        self.assertIn("docs/note.md has changes git does not hold", out)

    def test_a_run_with_every_question_answered_by_the_sources_is_done(self):
        # Given: every item met, and the one question answered by the notes
        fill(self.repo, QUESTIONS, [{"question": NAME, "ask": False, "answered": "notes.md 1"}])
        seen(self.repo)
        decided(self.repo)
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: it is done, and nothing is left for the user
        self.assertEqual((code, out.splitlines()[0]), (0, "done"))
        self.assertEqual(self.repo.json("out.json")["semantic_gist"], [])

    def test_a_run_does_not_return_with_a_question_undecided(self):
        # Given: every item met, and a question not decided
        seen(self.repo)
        decided(self.repo)
        fill(self.repo, QUESTIONS, [{"question": LICENSE}])
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: it is refused, and nothing is written back
        self.assertEqual(code, 1)
        self.assertIn("question 1: not decided", out)
        self.assertFalse(self.repo.exists("out.json"))

    def test_the_orchestrator_is_kept_at_work_while_the_run_is_open(self):
        for name, at_work in [("an agent briefed", "generator"), ("nothing briefed", None)]:
            with self.subTest(name):
                # Given: a question left open, and the generator handed its brief after its form
                # was written, or no agent briefed
                fill(self.repo, QUESTIONS, [OPEN])
                if at_work:
                    self.repo.write(f".turn/out/{at_work}-brief.json", "{}")
                    brief = os.path.join(self.repo.path, f".turn/out/{at_work}-brief.json")
                    later = os.path.getmtime(os.path.join(self.repo.path, form(at_work))) + 1
                    os.utime(brief, (later, later))
                # When: the orchestrator stops
                code, said = hook(stop, self.repo, hook_event_name="Stop", stop_hook_active=False)
                # Then: it is kept at work, since it waits for no one while the run is open
                self.assertEqual(code, 2, said)


class LearnersQuestions(unittest.TestCase):
    """A way to a Good that needs what only the user can decide is asked of the user at the end."""

    def setUp(self):
        self.repo = Repo()
        self.home = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"HOME": self.home.name})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(self.home.cleanup)
        self.addCleanup(self.repo.close)
        started(self.repo)
        self.repo.write(".turn/out/note.md", WORK)
        seen(self.repo)
        decided(self.repo, f1=False)
        fill(
            self.repo,
            form("learner"),
            {
                "note F-1": {
                    "aim": "the teammate knows the terms",
                    "way": "say the terms, from the answer to question 1",
                    "reach": "1",
                    "in": "what the work should be",
                    "making": "",
                }
            },
        )

    def test_the_learner_is_told_where_the_questions_are(self):
        # Given: the records of the run's agents
        folder = os.path.join(self.home.name, ".claude/projects/p/s1/subagents")
        os.makedirs(folder)
        for role in ("first-user", "generator"):
            with open(os.path.join(folder, f"agent-{role}.meta.json"), "w") as f:
                json.dump({"agentType": f"turn:{role}"}, f)
            open(os.path.join(folder, f"agent-{role}.jsonl"), "w").close()
        # When: the learner's brief is made
        code, out = run(self.repo, "brief", ".turn/out", "learner")
        # Then: it says where to add a question
        self.assertEqual(code, 0, out)
        self.assertEqual(self.repo.json(out.strip())["questions"], QUESTIONS)

    def test_a_learners_question_without_its_words_is_stopped(self):
        # Given: the learner added a question without its words
        fill(self.repo, QUESTIONS, [{"question": ""}])
        # When: the learner's form is checked
        code, out = run(self.repo, "check", ".turn/out", "learner")
        # Then: it is stopped, naming the question
        self.assertEqual(code, 1)
        self.assertIn("question 1: the question is not given", out)

    def test_a_way_waiting_on_the_users_answer_ends_the_run_by_asking_the_user(self):
        # Given: the learner's question left open
        fill(self.repo, QUESTIONS, [OPEN])
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: the user is asked the question, and the caller gets it with the way it gives
        self.assertEqual(code, 0, out)
        self.assertEqual(out.splitlines()[1], f"❓ {LICENSE}")
        back = self.repo.json("out.json")
        self.assertEqual(back["predictive_cue"], [{"next": "ask the user"}])
        self.assertEqual(back["semantic_gist"][0], {"question": LICENSE})
        self.assertIn("from the answer to question 1", back["semantic_gist"][1]["unmet"])


if __name__ == "__main__":
    unittest.main()

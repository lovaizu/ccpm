import os
import tempfile
import unittest
from unittest import mock

from helpers import Repo, fill, form, run, started, up

WORK = "# Note\n\nRun make.\n"
AIM = "a new teammate can start work alone"
PLAN = "Plan: 1 write → 2 read → 3 check   (once more if something is missing; two rounds at most)"
LICENSE = "Which license is the note under? The notes do not say."
WAY = {"aim": "the teammate takes it in at a glance", "way": "cut it to one line", "reach": "1-3",
       "in": "the work", "making": ""}


def met(repo, role, f1=True, n=1):
    fill(repo, form(role, n), {
        "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
        "note F-1": {"met": True, "lines": "1-3", "note": "three lines"} if f1 else {"met": False}})


class Console(unittest.TestCase):
    """The console shows how far a run has come, each line once, by round and step."""

    def setUp(self):
        self.repo = Repo()
        self.home = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"HOME": self.home.name})
        self.env.start()
        started(self.repo)

    def tearDown(self):
        self.env.stop()
        self.repo.close()
        self.home.cleanup()

    def say(self, *args):
        code, out = run(self.repo, *args)
        self.assertEqual(code, 0, out)
        return out.splitlines()

    def ran(self, role):
        folder = os.path.join(self.home.name, ".claude/projects/p/s1/subagents")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f"agent-{role}.meta.json"), "w") as f:
            f.write(f'{{"agentType": "turn:{role}"}}')
        open(os.path.join(folder, f"agent-{role}.jsonl"), "w").close()

    def read(self, n=1, f1=True):
        """Round n made, seen given, read and decided, with F-1 met or not."""
        met(self.repo, "hand-on", n=n)
        if n == 1:
            self.repo.write(".turn/out/1/note.md", WORK)
        copy = self.repo.json(self.say("brief", ".turn/out", str(n), "first-user")[0])["copy"]
        self.addCleanup(lambda: os.path.isdir(copy) and up.drop(copy))
        self.ran("first-user")
        fill(self.repo, form("first-user", n), {"note B-1": {"took": "run make", "lines": "3"}})
        met(self.repo, "orchestrator", f1, n)

    def test_the_aim_is_shown_with_the_plan_before_anything_is_written(self):
        # Given: a run just started, with a question the sources leave open
        fill(self.repo, ".turn/out/questions.json", [{"question": LICENSE, "ask": True}])
        # When: the orchestrator sets what the work will let its receiver do
        said = self.say("aim", ".turn/out", "1", AIM)
        # Then: the plan, the round, the aim and the question are shown, in that order
        self.assertEqual(said, [PLAN, "Round 1", f"  1 write   To make: {AIM}", f"            ❓ {LICENSE}"])

    def test_a_question_naming_an_item_is_not_shown(self):
        # Given: a question that names an item of the list
        fill(self.repo, ".turn/out/questions.json", [{"question": f"{LICENSE} (note F-1)", "ask": True}])
        # When: the console is asked for
        code, out = run(self.repo, "console", ".turn/out")
        # Then: it is refused, saying to put it in plain words
        self.assertEqual(code, 1)
        self.assertIn("question 1: names note F-1", out)

    def test_no_work_is_written_before_its_aim_is_shown(self):
        # Given: a run just started, with no aim set
        # When: the generator's brief is asked for
        code, out = run(self.repo, "brief", ".turn/out", "1", "generator")
        # Then: it is refused, naming the step that sets the aim
        self.assertEqual(code, 1)
        self.assertIn("step 4: set the aim", out)
        # Given: the aim set
        self.say("aim", ".turn/out", "1", AIM)
        # When: the generator's brief is asked for again
        # Then: it is made
        self.assertEqual(self.say("brief", ".turn/out", "1", "generator"), [".turn/out/1/generator-brief.json"])

    def test_an_aim_is_set_only_for_the_round_now_running(self):
        # Given: round 1 running
        # When: an aim is set for round 2
        code, out = run(self.repo, "aim", ".turn/out", "2", AIM)
        # Then: it is refused, naming the round running
        self.assertEqual((code, out.strip()), (1, "round 1 is running"))

    def test_each_line_is_shown_once_as_the_run_reaches_it(self):
        # Given: the aim shown
        self.say("aim", ".turn/out", "1", AIM)
        # When: the console is asked for with nothing new
        # Then: nothing is shown again
        self.assertEqual(self.say("console", ".turn/out"), [])
        # When: a question raised in the making is asked
        fill(self.repo, ".turn/out/questions.json", [{"question": LICENSE, "ask": True, "answer": "MIT"},
                                                     {"question": "What is it called?", "ask": False,
                                                      "answered": "notes.md 1"}])
        # Then: only the question asked is shown
        self.assertEqual(self.say("console", ".turn/out"), [f"            ❓ {LICENSE}"])
        # When: the work is handed to the first user, and read
        met(self.repo, "hand-on")
        self.repo.write(".turn/out/1/note.md", WORK)
        copy = self.repo.json(self.say("brief", ".turn/out", "1", "first-user")[0])["copy"]
        self.addCleanup(lambda: os.path.isdir(copy) and up.drop(copy))
        # Then: the work's path and the reading are shown
        self.assertEqual(self.say("console", ".turn/out"),
                         ["            .turn/out/1/note.md", "  2 read    Read as a new teammate."])
        fill(self.repo, form("first-user"), {"note B-1": {"took": "run make", "lines": "3"}})
        self.assertEqual(self.say("console", ".turn/out"), ["            .turn/out/1/first-user.json"])

    def check_shown(self, f1, learned):
        self.read(f1=f1)
        fill(self.repo, form("learner"), learned)
        return [x for x in self.say("console", ".turn/out") if x.startswith("  3 check") or "⚠️" in x]

    def test_the_check_shows_nothing_missing_when_every_item_is_met(self):
        # Given: round 1 read, with every item decided met
        # When: the console is asked for
        # Then: nothing missing is shown
        self.assertEqual(self.check_shown(True, {}), ["  3 check   ✅ Nothing missing."])

    def test_the_check_shows_in_plain_words_what_is_still_to_give_once_learned(self):
        # Given: round 1 read, with an item not met and no way learned yet
        # When: the console is asked for
        # Then: no check is shown yet
        self.assertEqual(self.check_shown(False, {}), [])
        # Given: the learner's way for it
        fill(self.repo, form("learner"), {"note F-1": WAY})
        # When: the console is asked for
        lines = self.say("console", ".turn/out")
        # Then: what the work is still to give is shown in the learner's words, with no item named
        self.assertEqual(lines, [f"  3 check   ⚠️ Not yet: {WAY['aim']}"])

    def test_the_second_round_is_shown_under_its_own_heading(self):
        # Given: round 1 read with a way for the generator, and round 2 begun
        self.say("aim", ".turn/out", "1", AIM)
        self.read(f1=False)
        fill(self.repo, form("learner"), {"note F-1": WAY})
        self.say("console", ".turn/out")
        self.say("round", ".turn/out")
        # When: the aim of round 2 is set, and its work read
        said = self.say("aim", ".turn/out", "2", "the same, cut to one line")
        self.read(n=2)
        # Then: round 2 has its heading and aim, and is read again as the same receiver
        self.assertEqual(said, ["Round 2", "  1 write   To make: the same, cut to one line"])
        self.assertEqual(self.say("console", ".turn/out")[:2],
                         ["            .turn/out/2/note.md", "  2 read    Read again, as a new teammate."])

    def test_the_end_says_where_the_work_is(self):
        # Given: round 1 read, with every item decided met
        self.read()
        # When: the run ends
        # Then: the next move and where the work is are shown
        self.assertEqual(self.say("end", ".turn/out", "1"), ["done", "The work is at docs/note.md."])

    def test_the_end_asks_the_user_what_only_they_decide_when_something_is_left(self):
        # Given: both rounds read, with an item left without a Good
        self.say("aim", ".turn/out", "1", AIM)
        self.read(f1=False)
        fill(self.repo, form("learner"), {"note F-1": WAY})
        self.say("round", ".turn/out")
        self.say("aim", ".turn/out", "2", AIM)
        self.read(n=2, f1=False)
        fill(self.repo, form("learner", 2), {"note F-1": WAY})
        # When: the run ends
        # Then: the next move, where the work is, and what the user must decide are shown
        self.assertEqual(self.say("end", ".turn/out", "2"),
                         ["ask the user", "The work is at docs/note.md.",
                          "❓ Run turn again on what is still missing, or take the work as it is?"])

if __name__ == "__main__":
    unittest.main()

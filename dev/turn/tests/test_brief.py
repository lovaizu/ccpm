import json
import os
import tempfile
import unittest
from unittest import mock

from helpers import Repo, fill, form, run, started
from repo import drop

WORK = "# Note\n\nRun make.\n"


def seen(repo, f1=True):
    """The orchestrator's form before the reading, with F-1 seen given or not."""
    fill(
        repo,
        form("hand-on"),
        {
            "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
            "note F-1": {"met": True, "lines": "1-3", "note": "three lines"}
            if f1
            else {
                "met": False,
                "aim": "the teammate takes it in at a glance",
                "way": "cut it to one line",
                "reach": "1-3",
            },
        },
    )


def decided(repo, f1):
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


class Briefs(unittest.TestCase):
    """Each agent is handed one file the script writes, so what it gets is the same on every run."""

    def setUp(self):
        self.repo = Repo()
        self.home = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"HOME": self.home.name})
        self.env.start()
        self.got = started(self.repo)
        run(self.repo, "aim", ".turn/out", "a new teammate can start work alone")
        self.repo.write(self.got["work"], WORK)

    def tearDown(self):
        self.env.stop()
        self.repo.close()
        self.home.cleanup()

    def brief(self, role):
        code, out = run(self.repo, "brief", ".turn/out", role)
        return code, out.strip()

    def handed(self, role):
        code, out = self.brief(role)
        assert code == 0, out
        self.assertEqual(out, f".turn/out/{role}-brief.json")
        got = self.repo.json(out)
        if role == "first-user":
            self.addCleanup(lambda: os.path.isdir(got["copy"]) and drop(got["copy"]))
        return got

    def ran(self, role, agent):
        """The records Claude Code keeps for an agent of the run's session."""
        folder = os.path.join(self.home.name, ".claude/projects/p/s1/subagents")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f"agent-{agent}.meta.json"), "w") as f:
            json.dump({"agentType": f"turn:{role}"}, f)
        path = os.path.join(folder, f"agent-{agent}.jsonl")
        open(path, "w").close()
        return path

    def test_the_generator_is_handed_what_the_work_should_be_and_no_way_at_first(self):
        # Given: a run just started
        # When: the generator's brief is made
        got = self.handed("generator")
        # Then: it holds what the work should be, where it is made, its form and how to check it
        self.assertEqual(got["list"], ".turn/out/list.json")
        self.assertEqual(got["work"], ".turn/out/note.md")
        self.assertEqual(got["form"], form("generator"))
        self.assertTrue(got["check"].endswith('up.py" check .turn/out generator'))
        self.assertEqual((got["receiver"], got["use"]), ("a new teammate", "to start work"))
        self.assertEqual(got["acceptance"], ["they can start alone"])
        self.assertEqual(got["sources"], ["notes.md"])
        self.assertEqual(got["constraints"], [])
        self.assertEqual(got["ways"], [])

    def test_work_sent_back_is_handed_with_how_each_item_not_seen_given_would_be_given(self):
        # Given: the orchestrator did not see F-1 given before the reading
        seen(self.repo, f1=False)
        # When: the generator's brief is made again
        got = self.handed("generator")
        # Then: it holds F-1 with how it would be given
        self.assertEqual(
            got["ways"],
            [
                {
                    "way": "cut it to one line",
                    "items": ["note F-1"],
                    "aims": ["the teammate takes it in at a glance"],
                    "reach": ["1-3"],
                }
            ],
        )

    def test_the_first_user_is_handed_a_fresh_copy_holding_only_what_the_receiver_has(self):
        # Given: the work seen to give every item, and a file the user has not committed
        seen(self.repo)
        self.repo.write("draft.md", "not committed")
        # When: the first user's brief is made
        got = self.handed("first-user")
        # Then: it names a copy with what is committed and the work at its place, and nothing else
        copy = got["copy"]
        with open(os.path.join(copy, got["deliverable"])) as f:
            self.assertEqual(f.read(), WORK)
        self.assertTrue(os.path.exists(os.path.join(copy, "notes.md")))
        self.assertFalse(os.path.exists(os.path.join(copy, "draft.md")))
        self.assertFalse(os.path.exists(os.path.join(copy, ".turn")))
        # Then: it holds the receiver, the use and the list, and nothing of the sources or acceptance
        self.assertEqual(
            sorted(got), ["check", "copy", "deliverable", "form", "list", "receiver", "use"]
        )
        self.assertTrue(os.path.isabs(got["list"]))

    def test_the_first_user_is_not_handed_the_work_before_every_item_is_seen_given(self):
        # Given: F-1 not yet seen given
        seen(self.repo, f1=False)
        # When: the first user's brief is made
        code, out = self.brief("first-user")
        # Then: it is refused, naming the step and the item
        self.assertEqual(code, 1)
        self.assertIn("step 8", out)
        self.assertIn("note F-1", out)

    def test_the_evaluator_is_handed_the_reading_and_its_records_and_the_copy_is_dropped(self):
        # Given: the first user has read the copy and filled its form
        seen(self.repo)
        copy = self.handed("first-user")["copy"]
        records = self.ran("first-user", "a1")
        fill(self.repo, form("first-user"), {"note B-1": {"took": "run make", "lines": "3"}})
        # When: the evaluator's brief is made
        got = self.handed("evaluator")
        # Then: it holds the reading and the first user's records, and the copy is gone
        self.assertEqual(got["reading"], form("first-user"))
        self.assertEqual(got["records"], records)
        self.assertEqual(got["acceptance"], ["they can start alone"])
        self.assertFalse(os.path.exists(copy))

    def test_the_evaluator_is_handed_its_brief_again_once_the_copy_is_dropped(self):
        # Given: the evaluator's brief was made, and the copy dropped with it
        seen(self.repo)
        self.handed("first-user")
        records = self.ran("first-user", "a1")
        fill(self.repo, form("first-user"), {"note B-1": {"took": "run make", "lines": "3"}})
        self.handed("evaluator")
        # When: the evaluator's brief is made again
        got = self.handed("evaluator")
        # Then: it holds the same reading and records
        self.assertEqual(got["reading"], form("first-user"))
        self.assertEqual(got["records"], records)

    def test_the_evaluator_is_not_handed_a_reading_that_is_not_there(self):
        cases = [
            ("no reading made", False, False, "step 9"),
            ("a reading without records", True, False, "no records of the first user"),
            ("a reading with its form left", True, True, "what was taken is not given"),
        ]
        for name, briefed, recorded, said in cases:
            with self.subTest(name):
                # Given: the first user not run, run without records, or with its form wrong
                seen(self.repo)
                if briefed:
                    self.handed("first-user")
                    fill(self.repo, form("first-user"), {"note B-1": {"took": "", "lines": "3"}})
                if recorded:
                    self.ran("first-user", "a2")
                # When: the evaluator's brief is made
                code, out = self.brief("evaluator")
                # Then: it is refused, saying what is missing
                self.assertEqual(code, 1)
                self.assertIn(said, out)

    def test_the_learner_is_handed_the_decisions_and_both_records(self):
        # Given: the run decided with F-1 not met, and the agents' records kept
        made = self.ran("generator", "g1")
        read = self.ran("first-user", "f1")
        decided(self.repo, f1=False)
        # When: the learner's brief is made
        got = self.handed("learner")
        # Then: it holds what the work should be, the reading, the decisions and both records
        self.assertEqual(got["decisions"], form("orchestrator"))
        self.assertEqual(got["reading"], form("first-user"))
        self.assertEqual(got["records"], {"first user": read, "generator": made})
        self.assertEqual(got["sources"], ["notes.md"])

    def test_the_learner_is_not_handed_a_run_with_nothing_to_learn(self):
        cases = [
            ("every item met", True, "every item is met"),
            ("an item undecided", None, "note F-1: not decided"),
        ]
        for name, f1, said in cases:
            with self.subTest(name):
                # Given: the run decided with every item met, or with one undecided
                decided(self.repo, f1=f1)
                # When: the learner's brief is made
                code, out = self.brief("learner")
                # Then: it is refused
                self.assertEqual(code, 1)
                self.assertIn(said, out)

    def test_a_brief_is_made_only_for_an_agent_of_turn(self):
        # Given: an open run
        # When: a brief is asked for a role that is no agent
        code, out = self.brief("orchestrator")
        # Then: it is refused, naming the agents that have briefs
        self.assertEqual(code, 1)
        self.assertIn("no brief for orchestrator; briefs are for generator", out)

    def test_only_a_copy_turn_made_is_dropped(self):
        # Given: a first user's brief naming a folder turn did not make
        seen(self.repo)
        self.handed("first-user")
        other = tempfile.mkdtemp()
        brief = self.repo.json(form("first-user-brief"))
        brief["copy"] = other
        fill(self.repo, form("first-user-brief"), brief)
        self.ran("first-user", "a3")
        fill(self.repo, form("first-user"), {})
        # When: the evaluator's brief is made
        code, out = self.brief("evaluator")
        # Then: it is refused, and the folder is left alone
        self.assertEqual(code, 1)
        self.assertIn("not a copy turn made", out)
        self.assertTrue(os.path.exists(other))
        os.rmdir(other)


if __name__ == "__main__":
    unittest.main()

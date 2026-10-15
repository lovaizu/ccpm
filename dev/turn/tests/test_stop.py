import json
import os
import unittest

from helpers import Repo, ccs, fill, form, run, started
from state import RUN

WORK = "# Note\n\nRun make.\n"
AIM = "a new teammate can start work alone"


def met(repo, role):
    fill(
        repo,
        form(role),
        {
            "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
            "note F-1": {"met": True, "lines": "1-3", "note": "three lines"},
        },
    )


class Stop(unittest.TestCase):
    """A stopped run returns a CCS saying where it was, and the next run makes the work anew from
    the task rewritten from what the user said."""

    def setUp(self):
        self.repo = Repo()
        self.task = ccs(constraints=[{"language": "English"}])
        started(self.repo, self.task)
        fill(self.repo, ".turn/out/questions.json", [{"question": "Which license?", "ask": True}])
        run(self.repo, "aim", ".turn/out", AIM)

    def tearDown(self):
        self.repo.close()

    def stop(self):
        code, out = run(self.repo, "stop", ".turn/out")
        self.assertEqual(code, 0, out)
        return out.strip(), self.repo.json("out.json")

    def to_reading(self):
        self.repo.write(".turn/out/note.md", WORK)
        met(self.repo, "hand-on")
        code, out = run(self.repo, "brief", ".turn/out", "first-user")
        assert code == 0, out

    def test_a_run_stopped_on_its_aim_returns_no_work_of_that_aim(self):
        # Given: the run with its aim shown, and the generator's work begun
        self.repo.write(".turn/out/note.md", "# Half\n")
        # When: the user stops the run
        said, back = self.stop()
        # Then: the CCS says where it stopped and points to no work, the caller's part comes back
        # as given, the run is closed, and where the work goes is untouched
        self.assertEqual(said, "stopped: write — CCS: out.json")
        self.assertEqual(back["predictive_cue"], [{"next": "stopped: write"}])
        self.assertEqual(back["episodic_trace"], [])
        self.assertEqual(back["constraints"], [{"language": "English"}])
        self.assertEqual(
            {k: back[k] for k in ("focal_entities", "goal_orientation", "retrieved_artifacts")},
            {
                k: self.task[k]
                for k in ("focal_entities", "goal_orientation", "retrieved_artifacts")
            },
        )
        self.assertFalse(self.repo.exists(".turn/run.json"))
        self.assertFalse(self.repo.exists("docs/note.md"))

    def test_a_run_stopped_while_its_work_is_read_or_checked_says_where_it_was(self):
        cases = [("read", False), ("check", True)]
        for step, checked in cases:
            with self.subTest(step):
                # Given: the work handed to the first user, and to the evaluator or not
                self.to_reading()
                if checked:
                    fill(
                        self.repo,
                        form("first-user"),
                        {"note B-1": {"took": "run make", "lines": "3"}},
                    )
                    self.repo.write(".turn/out/evaluator-brief.json", "{}")
                # When: the user stops the run
                _said, back = self.stop()
                # Then: it says where it stopped, points to no work, and leaves where the work goes
                # untouched
                self.assertEqual(back["predictive_cue"], [{"next": f"stopped: {step}"}])
                self.assertEqual(back["episodic_trace"], [])
                self.assertFalse(self.repo.exists("docs/note.md"))
                os.remove(os.path.join(self.repo.path, "out.json"))
                started(self.repo, self.task)
                run(self.repo, "aim", ".turn/out", AIM)

    def test_the_next_run_makes_the_work_anew_from_the_task_rewritten(self):
        # Given: a run stopped while its work was read, and the caller rewriting the receiver from
        # what the user said
        self.to_reading()
        _, back = self.stop()
        back["focal_entities"] = [{"deliverable": "docs/note.md"}, {"receiver": "an operator"}]
        self.repo.write("again.json", json.dumps(back))
        # When: turn is called with it
        code, out = run(self.repo, "start", "again.json", "out-2.json", "s1")
        # Then: the new run starts with no work yet, for the receiver the user named
        self.assertEqual(code, 0, out)
        got = json.loads(out)
        self.assertFalse(self.repo.exists(got["work"]))
        self.assertEqual(got["receiver"], "an operator")

    def test_nothing_is_stopped_when_no_run_is_open(self):
        # Given: no run open
        os.remove(os.path.join(self.repo.path, RUN))
        # When: a stop is asked for
        code, out = run(self.repo, "stop", ".turn/out")
        # Then: it is refused, and nothing is written
        self.assertEqual(code, 1)
        self.assertIn("no run is open", out)
        self.assertFalse(self.repo.exists("out.json"))


if __name__ == "__main__":
    unittest.main()

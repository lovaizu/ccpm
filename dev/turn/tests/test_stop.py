import json
import os
import unittest

from helpers import Repo, ccs, fill, form, run, started
from state import RUN

WORK = "# Note\n\nRun make.\n"
AIM = "a new teammate can start work alone"
WANTED = {"answer": "Write it for the operators, not for new teammates."}


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
    """A stopped run returns a CCS saying where it was, and the next run starts from the work as it
    stands."""

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
        return self.repo.json(out.strip())["copy"]

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

    def test_a_run_stopped_while_its_work_is_read_points_to_that_work(self):
        # Given: the work handed to the first user
        copy = self.to_reading()
        # When: the user stops the run
        _said, back = self.stop()
        # Then: it says where it stopped, points to the work, and drops the first user's copy
        self.assertEqual(back["predictive_cue"], [{"next": "stopped: read"}])
        self.assertEqual(back["episodic_trace"], [{"work": ".turn/out/note.md"}])
        self.assertFalse(os.path.exists(copy))

    def test_a_run_stopped_while_its_reading_is_checked_points_to_that_work(self):
        # Given: the work read, and handed to the evaluator
        self.to_reading()
        fill(self.repo, form("first-user"), {"note B-1": {"took": "run make", "lines": "3"}})
        self.repo.write(".turn/out/evaluator-brief.json", "{}")
        # When: the user stops the run
        _said, back = self.stop()
        # Then: it says where it stopped, and points to the work
        self.assertEqual(back["predictive_cue"], [{"next": "stopped: check"}])
        self.assertEqual(back["episodic_trace"], [{"work": ".turn/out/note.md"}])

    def test_the_next_run_starts_from_the_work_as_it_stands_with_what_the_user_said(self):
        # Given: a run stopped while its work was read, and the caller adding what the user said
        self.to_reading()
        _, back = self.stop()
        back["constraints"].append(WANTED)
        self.repo.write("again.json", json.dumps(back))
        # When: turn is called with it
        code, out = run(self.repo, "start", "again.json", "out-2.json", "s1")
        # Then: the new run's work starts as the work stood, and the user's words are among what the
        # work should be
        self.assertEqual(code, 0, out)
        got = json.loads(out)
        self.assertEqual(self.repo.read(got["work"]), WORK)
        self.assertIn(f"answer: {WANTED['answer']}", got["constraints"])
        run(self.repo, "aim", got["folder"], "operators can run it")
        code, out = run(self.repo, "brief", got["folder"], "generator")
        self.assertEqual(self.repo.json(out.strip())["started from"], ".turn/out/note.md")

    def test_a_run_stopped_again_on_its_aim_points_to_the_work_it_started_from(self):
        # Given: a run started from a stopped one, stopped again on its aim
        self.to_reading()
        _, back = self.stop()
        self.repo.write("again.json", json.dumps(back))
        run(self.repo, "start", "again.json", "out-2.json", "s1")
        run(self.repo, "aim", ".turn/out-2", AIM)
        # When: it is stopped
        code, out = run(self.repo, "stop", ".turn/out-2")
        # Then: it points to the work it started from
        self.assertEqual(code, 0, out)
        self.assertEqual(
            self.repo.json("out-2.json")["episodic_trace"], [{"work": ".turn/out/note.md"}]
        )

    def test_a_ccs_pointing_to_work_that_is_not_there_is_not_run(self):
        # Given: a stopped CCS whose work is gone
        self.repo.write(
            "again.json",
            json.dumps(dict(self.task, episodic_trace=[{"work": ".turn/gone/note.md"}])),
        )
        # When: turn is called with it
        code, out = run(self.repo, "start", "again.json", "out-2.json", "s1")
        # Then: it ends before any work, saying why
        self.assertEqual(code, 1)
        self.assertIn(".turn/gone/note.md is not there", out)

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

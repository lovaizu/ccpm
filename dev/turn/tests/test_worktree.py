import json
import os
import subprocess
import sys
import unittest

from helpers import Repo, ccs, fill, form, run, started
from test_work_alone import commit, pre

NOTE = "# Note\n\nRun make.\n"
TEST = "import lib\n\n\ndef test_make():\n    assert lib.make() == 1\n"
WORK = ".turn/out/work"


def worktrees(repo):
    """The working copies git keeps for the repository, besides the repository itself."""
    out = subprocess.run(
        ["git", "-C", repo.path, "worktree", "list", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [line[len("worktree ") :] for line in out.splitlines() if line.startswith("worktree ")][
        1:
    ]


def met(repo, folder=".turn/out", lines="1-3"):
    fill(
        repo,
        form("orchestrator", folder),
        {
            "note B-1": {"met": True, "lines": lines, "note": "the step is given"},
            "note F-1": {"met": True, "lines": lines, "note": "short"},
        },
    )


class WorkMadeInACopyOfTheRepository(unittest.TestCase):
    """A run makes the work in a working copy of the repository as it is committed, so the tests and
    builds the work needs run there."""

    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_the_work_s_tests_run_where_the_work_is_made(self):
        # Given: a module committed in the repository, and a task whose work is a test of it
        self.repo.write("lib.py", "def make():\n    return 1\n")
        commit(self.repo)
        got = started(
            self.repo,
            ccs(focal_entities=[{"deliverable": "test_lib.py"}, {"receiver": "r"}]),
        )
        # When: the generator writes the test where the work is made and runs it there
        self.repo.write(got["work"][0], TEST)
        done = subprocess.run(
            [sys.executable, "-m", "unittest", "discover"],
            check=False,
            cwd=os.path.join(self.repo.path, WORK),
            capture_output=True,
            text=True,
        )
        # Then: the test finds the module and passes, since the work folder holds the repository
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(self.repo.exists(f"{WORK}/notes.md"))

    def test_a_file_already_where_the_work_goes_is_absent_from_the_copy(self):
        # Given: a file committed where the work goes
        self.repo.write("docs/note.md", "old\n")
        commit(self.repo)
        # When: a run starts
        got = started(self.repo)
        # Then: the work folder holds no file there yet, so the work is made anew
        self.assertFalse(self.repo.exists(got["work"][0]))

    def test_a_repository_with_no_commit_is_stopped_saying_to_commit_first(self):
        # Given: a repository with nothing committed
        subprocess.run(["rm", "-rf", os.path.join(self.repo.path, ".git")], check=True)
        subprocess.run(["git", "-C", self.repo.path, "init", "-q"], check=True)
        self.repo.write("in.json", json.dumps(ccs()))
        # When: a run starts
        code, out = run(self.repo, "start", "in.json", "out.json", "s1")
        # Then: it ends before any work, saying to commit once
        self.assertEqual(code, 1)
        self.assertIn("the repository has no commit yet; commit once", out)
        self.assertFalse(self.repo.exists(".turn"))


class CopyGoneWhenTheRunEnds(unittest.TestCase):
    """When a run returns or is stopped, its working copy is gone and only the work it made is kept,
    so nothing lingers in the repository's list of working copies."""

    def setUp(self):
        self.repo = Repo()
        started(self.repo)

    def tearDown(self):
        self.repo.close()

    def test_a_returned_run_keeps_the_work_and_removes_the_copy(self):
        # Given: the work made and every item met
        self.repo.write(f"{WORK}/docs/note.md", NOTE)
        met(self.repo)
        # When: the run returns
        code, out = run(self.repo, "end", ".turn/out")
        # Then: the work is kept in the evidence, the copy is gone, and git lists no working copy
        self.assertEqual(code, 0, out)
        self.assertEqual(self.repo.read(".turn/out/kept/docs/note.md"), NOTE)
        self.assertFalse(self.repo.exists(WORK))
        self.assertEqual(worktrees(self.repo), [])

    def test_a_stopped_run_keeps_what_was_written_and_removes_the_copy(self):
        cases = [("the work written", True), ("nothing written", False)]
        for name, written in cases:
            with self.subTest(name):
                # Given: a run with its work written or not
                if written:
                    self.repo.write(f"{WORK}/docs/note.md", "# Half\n")
                # When: the user stops the run
                code, out = run(self.repo, "stop", ".turn/out")
                # Then: what was written is kept, the copy is gone, and git lists no working copy
                self.assertEqual(code, 0, out)
                self.assertEqual(self.repo.exists(".turn/out/kept/docs/note.md"), written)
                self.assertFalse(self.repo.exists(WORK))
                self.assertEqual(worktrees(self.repo), [])
                self.repo.close()
                self.setUp()

    def test_the_second_round_s_copy_replaces_the_first_s(self):
        # Given: the first round's work made and ended on a way in the work
        self.repo.write(f"{WORK}/docs/note.md", NOTE)
        fill(
            self.repo,
            form("orchestrator"),
            {
                "note B-1": {"met": True, "lines": "3", "note": "x"},
                "note F-1": {"met": False, "lines": "", "note": ""},
            },
        )
        fill(
            self.repo,
            form("learner"),
            {
                "note F-1": {
                    "aim": "a",
                    "way": "b",
                    "reach": "1-3",
                    "in": "the work",
                    "making": "",
                }
            },
        )
        # When: the first round ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: the second round's copy holds the work, the first's is kept and gone, and git lists
        # the second round's copy alone
        self.assertEqual(code, 0, out)
        self.assertEqual(self.repo.read(".turn/out/2/work/docs/note.md"), NOTE)
        self.assertEqual(self.repo.read(".turn/out/kept/docs/note.md"), NOTE)
        self.assertFalse(self.repo.exists(WORK))
        self.assertEqual(
            worktrees(self.repo), [os.path.join(self.repo.path, ".turn", "out", "2", "work")]
        )


class ReturnedWorkWrittenOver(unittest.TestCase):
    """A file a run returned may be written over by the next run; one edited since may not."""

    def setUp(self):
        self.repo = Repo()
        started(self.repo)
        self.repo.write(f"{WORK}/docs/note.md", NOTE)
        met(self.repo)
        assert run(self.repo, "end", ".turn/out")[0] == 0

    def tearDown(self):
        self.repo.close()

    def test_the_work_a_run_returned_unchanged_is_written_over(self):
        # Given: the work where it goes, as the run returned it
        # When: turn is called again
        code, out = run(self.repo, "start", "in.json", "out-2.json", "s1")
        # Then: the run starts
        self.assertEqual(code, 0, out)

    def test_the_work_edited_since_the_run_returned_is_refused(self):
        # Given: the work where it goes, edited since
        self.repo.write("docs/note.md", NOTE + "and more\n")
        # When: turn is called again
        code, out = run(self.repo, "start", "in.json", "out-2.json", "s1")
        # Then: it is refused, so the edit is not lost
        self.assertEqual(code, 1)
        self.assertIn("docs/note.md has changes git does not hold", out)


class RunCutOffLeavesNoCopy(unittest.TestCase):
    def test_the_next_start_removes_the_copy_a_cut_off_run_left(self):
        # Given: a run cut off with its copy still there
        repo = Repo()
        started(repo)
        self.assertEqual(worktrees(repo), [os.path.join(repo.path, ".turn", "out", "work")])
        # When: turn is called again
        code, out = run(repo, "start", "in.json", "out-2.json", "s1")
        # Then: the new run's copy is the only one, and the cut-off run's is gone
        self.assertEqual(code, 0, out)
        self.assertEqual(worktrees(repo), [os.path.join(repo.path, ".turn", "out-2", "work")])
        self.assertFalse(repo.exists(WORK))
        repo.close()


class OrchestratorReadsOnlyTheWorkInTheCopy(unittest.TestCase):
    """The copy holds the whole repository, but the orchestrator reads in it only the files the work
    is made of."""

    def setUp(self):
        self.repo = Repo()
        started(self.repo)
        self.repo.write(f"{WORK}/docs/note.md", NOTE)

    def tearDown(self):
        self.repo.close()

    def test_a_read_of_the_work_in_the_copy_goes_on(self):
        # Given: an open run
        # When: the orchestrator reads a file of the work in the copy
        code, said = pre(
            self.repo, "Read", {"file_path": os.path.join(self.repo.path, WORK, "docs/note.md")}
        )
        # Then: the read goes on
        self.assertEqual((code, said), (0, ""))

    def test_a_read_of_another_file_in_the_copy_is_stopped(self):
        # Given: an open run
        # When: the orchestrator reads a file of the repository through the copy
        code, said = pre(
            self.repo, "Read", {"file_path": os.path.join(self.repo.path, WORK, "notes.md")}
        )
        # Then: it is stopped, told to read only its inputs
        self.assertEqual(code, 2)
        self.assertIn("reads only its inputs", said)


if __name__ == "__main__":
    unittest.main()

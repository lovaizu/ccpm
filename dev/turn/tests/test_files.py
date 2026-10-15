import json
import os
import tempfile
import unittest
from unittest import mock

from helpers import Repo, ccs, fill, form, run, started
from state import RUN
from test_work_alone import commit, pre

NOTE = "# Note\n\nRun make.\n"
TEST = "def test_make():\n    assert True\n"
WORK = ".turn/out/work"
WAY = {
    "aim": "the teammate takes it in at a glance",
    "way": "cut it to one line",
    "reach": "docs/note.md:1-3",
    "in": "the work",
    "making": "",
}


def two():
    """A task whose work is a note and its test, one purpose in two files."""
    return ccs(
        focal_entities=[
            {"deliverable": "docs/note.md"},
            {"deliverable": "tests/test_note.py"},
            {"receiver": "a new teammate"},
        ]
    )


def decide(repo, folder, lines):
    fill(
        repo,
        form("orchestrator", folder),
        {
            "note B-1": {"met": True, "lines": lines, "note": "the step is given"},
            "note F-1": {"met": True, "lines": lines, "note": "short"},
        },
    )


class SeveralFiles(unittest.TestCase):
    """A run's unit is one purpose with one or more files, made, read and checked together."""

    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_a_work_of_two_files_is_made_at_each_file_s_own_path(self):
        # Given: a task whose work is a note and its test
        # When: a run starts
        got = started(self.repo, two())
        # Then: the orchestrator is told where each file is made, in the task's order
        self.assertEqual(got["work"], [f"{WORK}/docs/note.md", f"{WORK}/tests/test_note.py"])

    def test_two_files_with_one_name_do_not_collide(self):
        # Given: a task whose work is two files named alike in different folders
        c = ccs(
            focal_entities=[
                {"deliverable": "a/README.md"},
                {"deliverable": "b/README.md"},
                {"receiver": "r"},
            ]
        )
        # When: a run starts
        got = started(self.repo, c)
        # Then: each is made at its own path
        self.assertEqual(got["work"], [f"{WORK}/a/README.md", f"{WORK}/b/README.md"])

    def test_the_git_check_is_made_on_each_file(self):
        # Given: the note committed as it stands, and the test holding changes git does not hold
        self.repo.write("docs/note.md", "kept\n")
        commit(self.repo)
        self.repo.write("tests/test_note.py", "mine\n")
        self.repo.write("in.json", json.dumps(two()))
        # When: a run starts
        code, out = run(self.repo, "start", "in.json", "out.json", "s1")
        # Then: it is refused, naming the file that holds them
        self.assertEqual(code, 1)
        self.assertIn("tests/test_note.py has changes git does not hold", out)
        self.assertFalse(self.repo.exists(".turn"))

    def test_a_file_is_kept_only_when_a_run_returned_it_at_that_very_path(self):
        cases = [
            ("at the same path", "docs/note.md", 0),
            ("at another path with the same name", "other/note.md", 1),
        ]
        for name, kept_at, code in cases:
            with self.subTest(name):
                # Given: a run's evidence keeping the file's text at this path, and the file where
                # the work goes with that text, not committed
                self.repo.close()
                self.setUp()
                self.repo.write(f".turn/old/kept/{kept_at}", NOTE)
                self.repo.write("docs/note.md", NOTE)
                self.repo.write("in.json", json.dumps(ccs()))
                # When: a run starts
                got, out = run(self.repo, "start", "in.json", "out.json", "s1")
                # Then: it starts only when a run returned the file at that very path
                self.assertEqual(got, code, out)

    def test_lines_name_each_file_by_its_path(self):
        cases = [
            ("both files", "docs/note.md:3; tests/test_note.py:1-2", None),
            ("one file", "tests/test_note.py: 1", None),
            ("a file not of the work", "docs/other.md:1", "are not in the work"),
            ("no file named", "3", "are not in the work"),
            ("beyond the file", "tests/test_note.py:3", "are not in the work"),
            (
                "a second segment wrong",
                "docs/note.md:1; tests/test_note.py:x",
                "are not in the work",
            ),
        ]
        got = started(self.repo, two())
        self.repo.write(got["work"][0], NOTE)
        self.repo.write(got["work"][1], TEST)
        for name, lines, said in cases:
            with self.subTest(name):
                # Given: the generator's form naming these lines
                fill(
                    self.repo,
                    form("generator"),
                    {"note B-1": {"lines": lines}, "note F-1": {"lines": lines}},
                )
                # When: it is checked
                code, out = run(self.repo, "check", ".turn/out", "generator")
                # Then: it passes only where each segment names a file of the work and lines it holds
                if said is None:
                    self.assertEqual((code, out.strip()), (0, "filled"), out)
                else:
                    self.assertEqual(code, 1)
                    self.assertIn(f"note B-1: lines {lines} {said}", out)

    def test_a_reach_names_each_file_by_its_path(self):
        # Given: the orchestrator's form before the reading, with a reach in a file not of the work
        got = started(self.repo, two())
        self.repo.write(got["work"][0], NOTE)
        self.repo.write(got["work"][1], TEST)
        fill(
            self.repo,
            form("hand-on"),
            {
                "note B-1": {"met": True, "lines": "docs/note.md:3", "note": "x"},
                "note F-1": {"met": False, "aim": "a", "way": "b", "reach": "docs/x.md:1"},
            },
        )
        # When: it is checked
        code, out = run(self.repo, "check", ".turn/out", "hand-on")
        # Then: it is stopped, naming the reach
        self.assertEqual(code, 1)
        self.assertIn("note F-1: reach docs/x.md:1 is not in the work", out)

    def test_coverage_is_counted_for_each_file(self):
        cases = [
            (
                {"note B-1": {"lines": "docs/note.md:3"}, "note F-1": {"lines": "docs/note.md:1"}},
                "lines no item names: tests/test_note.py: 1, 2",
            ),
            (
                {
                    "note B-1": {"lines": "docs/note.md:1-3"},
                    "note F-1": {"lines": "tests/test_note.py:1"},
                },
                "lines no item names: tests/test_note.py: 2",
            ),
            (
                {
                    "note B-1": {"lines": "docs/note.md:1-3"},
                    "note F-1": {"lines": "tests/test_note.py:1-2"},
                },
                "every line is named",
            ),
            (
                {
                    "note B-1": {"lines": "nowhere"},
                    "note F-1": {"lines": "docs/note.md:1-3; tests/test_note.py:1-2"},
                },
                "every line is named",
            ),
        ]
        got = started(self.repo, two())
        self.repo.write(got["work"][0], NOTE)
        self.repo.write(got["work"][1], TEST)
        for filled, said in cases:
            with self.subTest(said):
                # Given: the generator's form naming these lines
                fill(self.repo, form("generator"), filled)
                # When: the coverage is asked for
                code, out = run(self.repo, "coverage", ".turn/out", "generator")
                # Then: each file with lines no place names is shown with them, blank lines left out
                self.assertEqual((code, out.strip()), (0, said))

    def test_a_form_is_stopped_when_a_file_of_the_work_is_not_written(self):
        # Given: the note written and the test not
        got = started(self.repo, two())
        self.repo.write(got["work"][0], NOTE)
        # When: the generator's form is checked
        code, out = run(self.repo, "check", ".turn/out", "generator")
        # Then: it is stopped, naming the file
        self.assertEqual(code, 1)
        self.assertIn(f"{WORK}/tests/test_note.py is not written", out)

    def test_every_file_reaches_its_place_when_the_run_returns(self):
        # Given: both files made, and every item decided met
        got = started(self.repo, two())
        self.repo.write(got["work"][0], NOTE)
        self.repo.write(got["work"][1], TEST)
        decide(self.repo, ".turn/out", "docs/note.md:1-3; tests/test_note.py:1-2")
        # When: the run ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: each file is where it goes, and the user is told where both are
        self.assertEqual(code, 0, out)
        self.assertEqual(self.repo.read("docs/note.md"), NOTE)
        self.assertEqual(self.repo.read("tests/test_note.py"), TEST)
        self.assertEqual(out.splitlines()[1], "The work is at docs/note.md, tests/test_note.py.")

    def test_the_second_round_starts_from_every_file_of_the_first(self):
        # Given: both files made, and the first round ended on a way in the work
        got = started(self.repo, two())
        self.repo.write(got["work"][0], NOTE)
        self.repo.write(got["work"][1], TEST)
        fill(
            self.repo,
            form("orchestrator"),
            {
                "note B-1": {"met": True, "lines": "tests/test_note.py:1-2", "note": "x"},
                "note F-1": {"met": False, "lines": "", "note": ""},
            },
        )
        fill(self.repo, form("learner"), {"note F-1": WAY})
        # When: the first round ends
        code, out = run(self.repo, "end", ".turn/out")
        # Then: the second round holds both files as the first made them, and neither is where it
        # goes yet
        self.assertEqual(code, 0, out)
        self.assertEqual(self.repo.read(".turn/out/2/work/docs/note.md"), NOTE)
        self.assertEqual(self.repo.read(".turn/out/2/work/tests/test_note.py"), TEST)
        self.assertFalse(self.repo.exists("docs/note.md"))
        self.assertFalse(self.repo.exists("tests/test_note.py"))


class WorkReadIsWorkReturned(unittest.TestCase):
    """Once the work is handed to the first user, it is not changed in that round, so the version read
    is the version returned."""

    def setUp(self):
        self.repo = Repo()
        self.got = started(self.repo)
        self.repo.write(self.got["work"][0], NOTE)
        fill(
            self.repo,
            form("hand-on"),
            {
                "note B-1": {"met": True, "lines": "3", "note": "x"},
                "note F-1": {"met": True, "lines": "1-3", "note": "x"},
            },
        )

    def tearDown(self):
        self.repo.close()

    def at(self, rel):
        return os.path.join(self.repo.path, rel)

    def test_a_write_to_the_work_before_the_reading_goes_on(self):
        # Given: the work not yet handed to the first user
        # When: a file of the work is written
        code, said = pre(self.repo, "Write", {"file_path": self.at(f"{WORK}/docs/note.md")})
        # Then: the write goes on
        self.assertEqual((code, said), (0, ""))

    def test_a_write_to_the_work_after_the_reading_is_stopped_saying_why(self):
        # Given: the work handed to the first user
        assert run(self.repo, "brief", ".turn/out", "first-user")[0] == 0
        # When: a file of the work is written
        code, said = pre(self.repo, "Edit", {"file_path": self.at(f"{WORK}/docs/note.md")})
        # Then: it is stopped, told the version read is the version returned
        self.assertEqual(code, 2)
        self.assertIn("step 9: the work has been handed to the first user", said)
        self.assertIn("the version read is the version returned", said)

    def test_a_form_is_written_after_the_reading(self):
        # Given: the work handed to the first user
        assert run(self.repo, "brief", ".turn/out", "first-user")[0] == 0
        # When: a form in the run's folder is written
        code, said = pre(self.repo, "Write", {"file_path": self.at(form("first-user"))})
        # Then: the write goes on
        self.assertEqual((code, said), (0, ""))

    def test_the_second_round_s_work_is_written_before_its_own_reading(self):
        # Given: the first round read and ended on a way in the work, so the second begun
        assert run(self.repo, "brief", ".turn/out", "first-user")[0] == 0
        fill(
            self.repo,
            form("orchestrator"),
            {
                "note B-1": {"met": True, "lines": "3", "note": "x"},
                "note F-1": {"met": False, "lines": "", "note": ""},
            },
        )
        fill(self.repo, form("learner"), {"note F-1": dict(WAY, reach="1-3")})
        assert run(self.repo, "end", ".turn/out")[0] == 0
        # When: the second round's work is written
        code, said = pre(
            self.repo, "Write", {"file_path": self.at(".turn/out/2/work/docs/note.md")}
        )
        # Then: the write goes on
        self.assertEqual((code, said), (0, ""))


class RunCutOff(unittest.TestCase):
    """A run cut off leaves where the work goes as it was, and the next run starts."""

    def setUp(self):
        self.repo = Repo()

    def tearDown(self):
        self.repo.close()

    def test_the_next_run_starts_after_a_run_cut_off_and_nothing_reached_where_the_work_goes(self):
        # Given: a run cut off with its work half written and its run file left
        got = started(self.repo)
        self.repo.write(got["work"][0], "# Half\n")
        self.assertTrue(self.repo.exists(RUN))
        # When: turn is called again
        code, out = run(self.repo, "start", "in.json", "out-2.json", "s1")
        # Then: the new run starts in its own folder, and where the work goes is untouched
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["folder"], ".turn/out-2")
        self.assertEqual(self.repo.json(RUN)["out"], "out-2.json")
        self.assertFalse(self.repo.exists("docs/note.md"))


class ToolsMissing(unittest.TestCase):
    def test_a_hook_outside_a_run_does_nothing_without_jq(self):
        # Given: a repository with no run, on a machine without jq
        repo = Repo()
        empty = tempfile.TemporaryDirectory()
        with mock.patch.dict(os.environ, {"PATH": empty.name}):
            # When: a file is written there
            done = pre(repo, "Write", {"file_path": os.path.join(repo.path, "notes.md")})
        # Then: the write goes on
        self.assertEqual(done, (0, ""))
        empty.cleanup()
        repo.close()


class CallersParts(unittest.TestCase):
    def test_the_caller_s_parts_come_back_as_given_and_turn_s_parts_fresh(self):
        # Given: a task whose CCS is one an earlier run returned, turn's parts filled
        repo = Repo()
        c = ccs(
            constraints=[{"language": "English"}, {"rule": "write for a first day"}],
            predictive_cue=[{"next": "ask the user"}],
            uncertainty_signal=[{"doubt": "x"}],
            semantic_gist=[{"question": "Which license?"}],
            relational_map=[{"link": "y"}],
            episodic_trace=[{"evidence": ".turn/old/list.json"}],
        )
        got = started(repo, c)
        repo.write(got["work"][0], NOTE)
        decide(repo, ".turn/out", "1-3")
        # When: the run ends
        code, out = run(repo, "end", ".turn/out")
        # Then: the caller's four parts are in the CCS written back as in the one received, byte
        # for byte, and turn's five hold only what this run found
        self.assertEqual(code, 0, out)
        sent, back = repo.json("in.json"), repo.json("out.json")
        for part in ("focal_entities", "goal_orientation", "retrieved_artifacts", "constraints"):
            self.assertEqual(json.dumps(back[part]), json.dumps(sent[part]))
        self.assertEqual(back["predictive_cue"], [{"next": "done"}])
        self.assertEqual((back["uncertainty_signal"], back["relational_map"]), ([], []))
        self.assertEqual(back["semantic_gist"], [])
        self.assertEqual(
            back["episodic_trace"],
            [{"evidence": ".turn/out/list.json"}, {"evidence": ".turn/out/orchestrator.json"}],
        )
        repo.close()


if __name__ == "__main__":
    unittest.main()

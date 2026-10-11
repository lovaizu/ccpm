"""Tests for the check run as each of turn's agents hands back its report, fed what Claude Code feeds it."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
HOOK = os.path.join(PLUGIN_ROOT, "hooks", "pretooluse.py")
UP = os.path.join(PLUGIN_ROOT, "scripts", "up.py")

CCS = {
    "focal_entities": [{"deliverable": "SETUP.md"}, {"receiver": "A new team member"}],
    "goal_orientation": [{"acceptance": "Starts the app by following the guide alone"}],
    "retrieved_artifacts": [{"viewpoint": "views/setup.md"}, {"source": "src"}],
    "constraints": [], "episodic_trace": [], "semantic_gist": [], "relational_map": [],
    "predictive_cue": [], "uncertainty_signal": [],
}


class HandbackTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.repo = os.path.join(self.root, "repo")
        self.session = str(uuid.uuid4())
        os.makedirs(self.repo)
        self.write("views/setup.md", "- Steps run as typed.\n- One step per line.\n")
        self.write("src/app.py", "print('hi')\n")
        self.write("src/lib/util.py", "x = 1\n")
        self.write(".t/in.json", json.dumps(CCS))
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "s"],
                       cwd=self.repo, check=True)
        self.write("SETUP.md", "# Setup\n\nRun npm start.\n")
        started = subprocess.run([sys.executable, UP, "start", ".t/in.json", ".t/out.json", self.session],
                                 cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        self.work = started.stdout.splitlines()[0][len("work: "):]
        self.addCleanup(shutil.rmtree, self.work, True)
        self.n = 0

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)

    def put(self, name, data):
        with open(os.path.join(self.work, name), "w", encoding="utf-8") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))

    def read(self, path, lines=None, error=False):
        """A Read call and its result, as a record holds them; lines are the line numbers shown."""
        self.n += 1
        with open(path, encoding="utf-8") as f:
            text = f.read().splitlines()
        shown = lines or range(1, len(text) + 1)
        return [{"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "id": f"r{self.n}", "name": "Read", "input": {"file_path": path}}]}},
                {"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": f"r{self.n}", "is_error": error,
                     "content": "<error>no</error>" if error else
                     "\n".join(f"{i}\t{text[i - 1]}" for i in shown)}]}}]

    def stop(self, agent, entries, session=None):
        """The agent hands back its report, with its record as Claude Code keeps it beside the session's."""
        session = session or self.session
        agent_id = uuid.uuid4().hex
        path = os.path.join(self.root, "records", session, "subagents", f"agent-{agent_id}.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(json.dumps(e) + "\n" for e in entries))
        data = {"session_id": session, "hook_event_name": "PreToolUse", "tool_name": "SubagentHandback",
                "tool_input": {"message": "done"}, "agent_id": agent_id, "agent_type": agent, "cwd": self.repo,
                "transcript_path": os.path.join(self.root, "records", f"{session}.jsonl")}
        return subprocess.run([sys.executable, HOOK], input=json.dumps(data), capture_output=True, text=True)

    def blocked(self, result):
        self.assertIn(result.returncode, (0, 2), result.stderr)
        return result.stderr.strip() if result.returncode == 2 else None

    def generator_reads(self):
        return [e for p in (os.path.join(self.work, "should.md"), os.path.join(self.repo, "views/setup.md"),
                            os.path.join(self.repo, "src/app.py"), os.path.join(self.repo, "src/lib/util.py"))
                for e in self.read(p)]

    def round_one_files(self):
        self.put("steps-generator-1.md", "# Steps of generator-1\n")
        self.put("steps-generator-1.json", [{"step": "generator-1#1", "did": "Write SETUP.md", "came_out": "",
                                             "error": False}])
        self.put("steps-first-user-1.md", "# Steps of first-user-1\n\n## first-user-1#2 (error)\n")
        self.put("steps-first-user-1.json", [
            {"step": "first-user-1#1", "did": "Read SETUP.md", "came_out": "", "error": False},
            {"step": "first-user-1#2", "did": "Bash npm start", "came_out": "no var/", "error": True}])
        self.put("first-user-1.md", "1. Ran npm start; it stopped.\n")
        self.put("learner-1.json", {"learnings": [{"learning": "var/ was assumed", "grounds": ["first-user-1#2"]}]})

    def learner_reads(self):
        return [e for p in [os.path.join(self.work, p) for p in
                            ("should.md", "first-user-1.md", "steps-generator-1.md", "steps-first-user-1.md")]
                + [os.path.join(self.repo, "views/setup.md")] for e in self.read(p)]

    def evaluator_reads(self):
        paths = ["should.md", "steps-generator-1.md", "steps-first-user-1.md", "first-user-1.md", "learner-1.json"]
        return [e for p in [os.path.join(self.work, p) for p in paths]
                + [os.path.join(self.repo, "views/setup.md"), os.path.join(self.repo, "SETUP.md")]
                for e in self.read(p)]

    def judge(self, grounds, point=CCS["goal_orientation"][0]["acceptance"]):
        self.put("evaluator-1.json", {"points": [{"point": point, "judgment": "more",
                                                  "fell_short": "npm start stopped", "grounds": grounds}]})

    def test_an_agent_not_of_turn_is_let_through(self):
        # Given: an agent not of turn that read nothing
        entries = []
        # When: it hands back its report
        result = self.stop("Explore", entries)
        # Then: it is let through
        self.assertIsNone(self.blocked(result))

    def test_a_turn_agent_outside_a_turn_of_this_session_is_let_through(self):
        # Given: a session with no turn running
        entries = []
        # When: the generator hands back its report having read nothing
        result = self.stop("turn:generator", entries, session=str(uuid.uuid4()))
        # Then: it is let through
        self.assertIsNone(self.blocked(result))

    def test_a_generator_that_read_everything_it_must_whole_finishes(self):
        # Given: a generator that read should.md, the viewpoint and every file in the source folder whole
        entries = self.generator_reads()
        # When: it hands back its report
        result = self.stop("turn:generator", entries)
        # Then: it is let through
        self.assertIsNone(self.blocked(result))

    def test_a_generator_that_left_a_file_unread_is_kept_running_and_told_which(self):
        # Given: a generator that read all but one file in the source folder
        entries = self.generator_reads()[:-2]
        # When: it hands back its report
        reason = self.blocked(self.stop("turn:generator", entries))
        # Then: it is kept running and told that file is not read, and not the file it did read
        self.assertIn(os.path.join(self.repo, "src/lib/util.py") + " (not read)", reason)
        self.assertNotIn("app.py", reason)

    def test_lines_left_unread_and_a_read_that_failed_are_not_counted(self):
        # Given: a generator that read only some lines of should.md and whose read of the viewpoint failed
        should = os.path.join(self.work, "should.md")
        view = os.path.join(self.repo, "views/setup.md")
        entries = (self.generator_reads()[4:] + self.read(should, lines=[1, 2]) + self.read(should, lines=[5])
                   + self.read(view, error=True))
        # When: it hands back its report
        reason = self.blocked(self.stop("turn:generator", entries))
        # Then: it is told which lines of should.md are not read and that the viewpoint is not read
        self.assertIn(f"{should} (lines 3-4, 6-7 not read)", reason)
        self.assertIn(f"{view} (not read)", reason)

    def test_a_generator_with_something_to_remake_from_must_read_it(self):
        # Given: a turn in round 2 with what to remake the deliverable from, and a generator that read everything else
        self.put("remake-2.md", "# What to remake the deliverable from\n\n## More\n\n- x: y\n")
        with open(os.path.join(self.work, "turn.json"), encoding="utf-8") as f:
            s = json.load(f)
        self.put("turn.json", dict(s, round=2))
        # When: it hands back its report
        reason = self.blocked(self.stop("turn:generator", self.generator_reads()))
        # Then: it is told what to remake from is not read
        self.assertIn(os.path.join(self.work, "remake-2.md") + " (not read)", reason)

    def test_the_first_user_is_not_asked_to_read_anything_whole(self):
        # Given: a first user that read nothing
        entries = []
        # When: it hands back its report
        result = self.stop("turn:first-user", entries)
        # Then: it is let through
        self.assertIsNone(self.blocked(result))

    def test_a_learner_that_read_everything_and_grounded_each_learning_finishes(self):
        # Given: round 1's files and a learning resting on a step that exists, with the learner having read what the deliverable should be, the viewpoint, the report and both steps files
        self.round_one_files()
        entries = self.learner_reads()
        # When: it hands back its report
        result = self.stop("turn:learner", entries)
        # Then: it is let through
        self.assertIsNone(self.blocked(result))

    def test_a_learner_that_did_not_read_what_the_deliverable_should_be_is_told_so(self):
        # Given: round 1's files, and a learner that read everything but should.md
        self.round_one_files()
        entries = self.learner_reads()[2:]
        # When: it hands back its report
        reason = self.blocked(self.stop("turn:learner", entries))
        # Then: it is told should.md is not read
        self.assertIn(os.path.join(self.work, "should.md") + " (not read)", reason)

    def test_a_learner_whose_learnings_are_out_of_form_or_ungrounded_is_told_what_is_wrong(self):
        # Given: a learner that read everything, with learnings that are not JSON, a learning missing its grounds, learnings that are not a list, and a learning resting on a step that does not exist
        self.round_one_files()
        entries = self.learner_reads()
        cases = {"{no": "is not in the form", '{"learnings": [{"learning": "x"}]}': "is not in the form",
                 '{"learnings": "x"}': "is not in the form",
                 json.dumps({"learnings": [{"learning": "y", "grounds": ["first-user-1#9"]}]}):
                     "first-user-1#9 is not a step"}
        for text, said in cases.items():
            with self.subTest(text=text):
                self.put("learner-1.json", text)
                # When: it hands back its report with each
                reason = self.blocked(self.stop("turn:learner", entries))
                # Then: it is told the learnings are out of form, or which step does not exist
                self.assertIn(said, reason)

    def test_an_evaluator_that_read_everything_and_grounded_each_judgment_finishes(self):
        # Given: round 1's files and judgments of the acceptance and of a viewpoint line, resting on a step and a line of the deliverable, with the evaluator having read every file of the round, the viewpoint and the deliverable
        self.round_one_files()
        self.put("evaluator-1.json", {"points": [
            {"point": CCS["goal_orientation"][0]["acceptance"], "judgment": "more", "fell_short": "it stopped",
             "grounds": ["first-user-1#2", "SETUP.md:3"]},
            {"point": "views/setup.md:2", "judgment": "good", "grounds": ["SETUP.md:3"]}]})
        # When: it hands back its report
        result = self.stop("turn:evaluator", self.evaluator_reads())
        # Then: it is let through
        self.assertIsNone(self.blocked(result))

    def test_an_evaluator_with_no_judgment_is_told_to_write_it(self):
        # Given: round 1's files and an evaluator that read them but wrote no judgment
        self.round_one_files()
        # When: it hands back its report
        reason = self.blocked(self.stop("turn:evaluator", self.evaluator_reads()))
        # Then: it is told its judgment is not in the form
        self.assertIn("evaluator-1.json is not in the form", reason)

    def test_an_evaluator_naming_grounds_that_do_not_exist_is_told_which(self):
        # Given: an evaluator that read everything, with a judgment resting on a step of a round not run, a line past the deliverable's end, a span of lines, a line of a file not the deliverable, and words that are neither
        self.round_one_files()
        self.judge(["first-user-1#2", "generator-3#1", "SETUP.md:9", "SETUP.md:3-4", "README.md:1", "somewhere"])
        # When: it hands back its report
        reason = self.blocked(self.stop("turn:evaluator", self.evaluator_reads()))
        # Then: it is told each of the five does not exist
        for said in ("generator-3#1 is not a step", "SETUP.md:9 is not a line of the deliverable",
                     "SETUP.md:3-4 is not a line of the deliverable",
                     "README.md:1 is not a line of the deliverable", "somewhere is not a step"):
            self.assertIn(said, reason)

    def test_an_evaluator_judging_a_point_that_is_not_one_of_what_the_deliverable_should_be_is_told_which(self):
        # Given: an evaluator that read everything, judging a reworded acceptance, a line past the viewpoint's end, and a line of a file not a viewpoint
        self.round_one_files()
        cases = ["Starts the app", "views/setup.md:3", "SETUP.md:1"]
        for point in cases:
            with self.subTest(point=point):
                self.judge(["first-user-1#2"], point=point)
                # When: it hands back its report
                reason = self.blocked(self.stop("turn:evaluator", self.evaluator_reads()))
                # Then: it is told the point is neither an acceptance criterion as written nor a line of a viewpoint file
                self.assertIn(f"{point} is neither an acceptance criterion as written nor a line of a viewpoint file",
                              reason)

    def test_an_evaluator_that_left_an_acceptance_criterion_unjudged_is_told_which(self):
        # Given: an evaluator that read everything and judged only a point of the viewpoint, leaving out the acceptance criterion
        self.round_one_files()
        self.judge(["first-user-1#2"], point="views/setup.md:1")
        # When: it hands back its report
        reason = self.blocked(self.stop("turn:evaluator", self.evaluator_reads()))
        # Then: it is told the acceptance criterion has no judgment
        self.assertIn(f"{CCS['goal_orientation'][0]['acceptance']} is an acceptance criterion with no judgment",
                      reason)

    def test_a_deliverable_folder_must_be_read_file_by_file_and_its_lines_can_be_grounds(self):
        # Given: a turn whose deliverable is a folder, and an evaluator that read everything but the file in it and rests a judgment on a line of that file
        with open(os.path.join(self.repo, ".t/in.json"), encoding="utf-8") as f:
            ccs = json.load(f)
        ccs["focal_entities"][0] = {"deliverable": "docs"}
        self.write(".t/in2.json", json.dumps(ccs))
        self.write("docs/a.md", "one\n")
        shutil.rmtree(self.work)
        subprocess.run([sys.executable, UP, "start", ".t/in2.json", ".t/out.json", self.session],
                       cwd=self.repo, check=True, capture_output=True)
        self.round_one_files()
        self.judge(["first-user-1#2", "docs/a.md:1"])
        entries = [e for e in self.evaluator_reads() if "SETUP.md" not in json.dumps(e)]
        # When: it hands back its report
        reason = self.blocked(self.stop("turn:evaluator", entries))
        # Then: it is told that file is not read, and the line is taken as a ground
        self.assertIn(os.path.join(self.repo, "docs/a.md") + " (not read)", reason)
        self.assertNotIn("is not a line", reason)


if __name__ == "__main__":
    unittest.main()

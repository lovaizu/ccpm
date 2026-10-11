"""Tests for the check run as each of turn's agents tries to finish, fed what Claude Code feeds it."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
HOOK = os.path.join(PLUGIN_ROOT, "hooks", "subagentstop.py")
UP = os.path.join(PLUGIN_ROOT, "scripts", "up.py")

CCS = {
    "focal_entities": [{"deliverable": "SETUP.md"}, {"receiver": "A new team member"}],
    "goal_orientation": [{"acceptance": "Starts the app by following the guide alone"}],
    "retrieved_artifacts": [{"viewpoint": "views/setup.md"}, {"source": "src"}],
    "constraints": [], "episodic_trace": [], "semantic_gist": [], "relational_map": [],
    "predictive_cue": [], "uncertainty_signal": [],
}


class SubagentStopTest(unittest.TestCase):

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

    def record(self, entries):
        path = os.path.join(self.root, f"agent-{uuid.uuid4().hex}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(json.dumps(e) + "\n" for e in entries))
        return path

    def stop(self, agent, entries, session=None):
        data = {"session_id": session or self.session, "hook_event_name": "SubagentStop",
                "stop_hook_active": False, "agent_id": "a1", "agent_type": agent, "cwd": self.repo,
                "agent_transcript_path": self.record(entries), "last_assistant_message": "done"}
        return subprocess.run([sys.executable, HOOK], input=json.dumps(data), capture_output=True, text=True)

    def blocked(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)["reason"] if result.stdout.strip() else None

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
        self.put("learner-1.json", {"causes": [{"stumble": "npm start stopped", "cause": "var/ assumed",
                                                "way_of_working": True, "grounds": ["first-user-1#2"]}]})

    def evaluator_reads(self, decided=True):
        paths = ["should.md", "steps-generator-1.md", "steps-first-user-1.md", "first-user-1.md",
                 "learner-1.json"] + (["evaluator-1.json"] if decided else [])
        return [e for p in [os.path.join(self.work, p) for p in paths]
                + [os.path.join(self.repo, "views/setup.md"), os.path.join(self.repo, "SETUP.md")]
                for e in self.read(p)]

    def decide(self, grounds):
        self.put("evaluator-1.json", {"endings": [{"stumble": "npm start stopped", "cause": "var/ assumed",
                                                   "ending": "fixed", "grounds": grounds}],
                                      "rules": [], "gaps": [], "links": []})

    def test_an_agent_not_of_turn_is_let_through(self):
        # Given
        entries = []
        # When
        result = self.stop("Explore", entries)
        # Then
        self.assertIsNone(self.blocked(result))

    def test_a_turn_agent_outside_a_turn_of_this_session_is_let_through(self):
        # Given
        entries = []
        # When
        result = self.stop("turn:generator", entries, session=str(uuid.uuid4()))
        # Then
        self.assertIsNone(self.blocked(result))

    def test_a_generator_that_read_everything_it_must_whole_finishes(self):
        # Given
        entries = self.generator_reads()
        # When
        result = self.stop("turn:generator", entries)
        # Then
        self.assertIsNone(self.blocked(result))

    def test_a_generator_that_left_a_file_unread_is_kept_running_and_told_which(self):
        # Given
        entries = self.generator_reads()[:-2]
        # When
        reason = self.blocked(self.stop("turn:generator", entries))
        # Then
        self.assertIn(os.path.join(self.repo, "src/lib/util.py") + " (not read)", reason)
        self.assertNotIn("app.py", reason)

    def test_lines_left_unread_and_a_read_that_failed_are_not_counted(self):
        # Given
        should = os.path.join(self.work, "should.md")
        view = os.path.join(self.repo, "views/setup.md")
        entries = (self.generator_reads()[4:] + self.read(should, lines=[1, 2]) + self.read(should, lines=[5])
                   + self.read(view, error=True))
        # When
        reason = self.blocked(self.stop("turn:generator", entries))
        # Then
        self.assertIn(f"{should} (lines 3-4, 6-7 not read)", reason)
        self.assertIn(f"{view} (not read)", reason)

    def test_a_generator_in_a_later_round_must_read_the_earlier_decisions(self):
        # Given
        self.decide(["first-user-1#2"])
        with open(os.path.join(self.work, "turn.json"), encoding="utf-8") as f:
            s = json.load(f)
        self.put("turn.json", dict(s, round=2))
        # When
        reason = self.blocked(self.stop("turn:generator", self.generator_reads()))
        # Then
        self.assertIn(os.path.join(self.work, "evaluator-1.json") + " (not read)", reason)

    def test_the_first_user_is_not_asked_to_read_anything_whole(self):
        # Given
        entries = []
        # When
        result = self.stop("turn:first-user", entries)
        # Then
        self.assertIsNone(self.blocked(result))

    def test_a_learner_that_read_everything_and_grounded_each_cause_finishes(self):
        # Given
        self.round_one_files()
        entries = [e for p in ("first-user-1.md", "steps-generator-1.md", "steps-first-user-1.md")
                   for e in self.read(os.path.join(self.work, p))] + self.read(os.path.join(self.repo, "views/setup.md"))
        # When
        result = self.stop("turn:learner", entries)
        # Then
        self.assertIsNone(self.blocked(result))

    def test_a_learner_whose_causes_are_out_of_form_or_ungrounded_is_told_what_is_wrong(self):
        # Given
        self.round_one_files()
        entries = [e for p in ("first-user-1.md", "steps-generator-1.md", "steps-first-user-1.md")
                   for e in self.read(os.path.join(self.work, p))] + self.read(os.path.join(self.repo, "views/setup.md"))
        cases = {"{no": "is not in the form", '{"causes": [{"stumble": "x"}]}': "is not in the form",
                 '{"causes": "x"}': "is not in the form",
                 json.dumps({"causes": [{"stumble": "x", "cause": "y", "way_of_working": False,
                                         "grounds": ["first-user-1#9"]}]}): "first-user-1#9 is not a step"}
        for text, said in cases.items():
            with self.subTest(text=text):
                self.put("learner-1.json", text)
                # When
                reason = self.blocked(self.stop("turn:learner", entries))
                # Then
                self.assertIn(said, reason)

    def test_an_evaluator_that_read_everything_and_grounded_each_ending_finishes(self):
        # Given
        self.round_one_files()
        self.decide(["first-user-1#2", "SETUP.md:3"])
        # When
        result = self.stop("turn:evaluator", self.evaluator_reads())
        # Then
        self.assertIsNone(self.blocked(result))

    def test_an_evaluator_with_no_decision_is_told_to_write_it(self):
        # Given
        self.round_one_files()
        # When
        reason = self.blocked(self.stop("turn:evaluator", self.evaluator_reads(decided=False)))
        # Then
        self.assertIn("evaluator-1.json is not in the form", reason)

    def test_an_evaluator_naming_grounds_that_do_not_exist_is_told_which(self):
        # Given
        self.round_one_files()
        self.decide(["first-user-1#2", "generator-3#1", "SETUP.md:9", "README.md:1", "somewhere"])
        # When
        reason = self.blocked(self.stop("turn:evaluator", self.evaluator_reads()))
        # Then
        for said in ("generator-3#1 is not a step", "SETUP.md:9 is not a line of the deliverable",
                     "README.md:1 is not a line of the deliverable", "somewhere is not a step"):
            self.assertIn(said, reason)

    def test_an_evaluator_that_left_an_error_step_of_the_first_user_without_an_ending_is_told_which(self):
        # Given
        self.round_one_files()
        self.decide(["first-user-1#1"])
        # When
        reason = self.blocked(self.stop("turn:evaluator", self.evaluator_reads()))
        # Then
        self.assertIn("first-user-1#2 ended in an error and no ending names it", reason)

    def test_a_deliverable_folder_must_be_read_file_by_file_and_its_lines_can_be_grounds(self):
        # Given
        with open(os.path.join(self.repo, ".t/in.json"), encoding="utf-8") as f:
            ccs = json.load(f)
        ccs["focal_entities"][0] = {"deliverable": "docs"}
        self.write(".t/in2.json", json.dumps(ccs))
        self.write("docs/a.md", "one\n")
        shutil.rmtree(self.work)
        subprocess.run([sys.executable, UP, "start", ".t/in2.json", ".t/out.json", self.session],
                       cwd=self.repo, check=True, capture_output=True)
        self.round_one_files()
        self.decide(["first-user-1#2", "docs/a.md:1"])
        entries = [e for e in self.evaluator_reads() if "SETUP.md" not in json.dumps(e)]
        # When
        reason = self.blocked(self.stop("turn:evaluator", entries))
        # Then
        self.assertIn(os.path.join(self.repo, "docs/a.md") + " (not read)", reason)
        self.assertNotIn("is not a line", reason)


if __name__ == "__main__":
    unittest.main()

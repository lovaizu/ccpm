"""Tests for building the CCS to return from the one received and the evaluator's decisions."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
ENTRY = os.path.join(PLUGIN_ROOT, "scripts", "assemble.py")

GIVEN = {
    "focal_entities": [{"deliverable": "SETUP.md"}, {"receiver": "A new team member"}],
    "goal_orientation": [{"acceptance": "Starts the app without asking anyone"}],
    "retrieved_artifacts": [{"viewpoint": "/plugin/viewpoints/setup.md"}],
    "constraints": [{"language": "English"}, {"rule": "Type each step first"}],
    "episodic_trace": [{"generator-1": "from the turn before"}],
    "semantic_gist": [{"difference": "from the turn before → fixed"}],
    "relational_map": [{"link": "from the turn before"}],
    "predictive_cue": [{"next": "stopped: first-user-1"}],
    "uncertainty_signal": [],
}


class AssembleTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.work = os.path.join(self.root, "work")
        os.makedirs(self.work)
        self.in_path = os.path.join(self.root, "task-1.json")
        self.out_path = os.path.join(self.root, "task-2.json")
        with open(self.in_path, "w", encoding="utf-8") as f:
            json.dump(GIVEN, f)

    def tearDown(self):
        shutil.rmtree(self.root)

    def decide(self, n, text):
        with open(os.path.join(self.work, f"evaluator-{n}.json"), "w", encoding="utf-8") as f:
            f.write(text if isinstance(text, str) else json.dumps(text))

    def run_assemble(self, *extra):
        return subprocess.run([sys.executable, ENTRY, self.in_path, self.out_path, self.work, *extra],
                              capture_output=True, text=True)

    def returned(self):
        with open(self.out_path, encoding="utf-8") as f:
            return json.load(f)

    def test_a_round_with_no_stumble_returns_done_and_keeps_what_the_plugin_wrote(self):
        # Given
        self.decide(1, {"endings": [], "rules": [], "gaps": [], "links": ["SETUP.md ← app.py"]})
        # When
        result = self.run_assemble()
        # Then
        self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)
        out = self.returned()
        for part in ("focal_entities", "goal_orientation", "retrieved_artifacts", "constraints"):
            self.assertEqual(out[part], GIVEN[part])
        self.assertEqual(out["predictive_cue"], [{"next": "done"}])
        self.assertEqual(out["semantic_gist"], [])
        self.assertEqual(out["uncertainty_signal"], [])
        self.assertEqual(out["relational_map"], [{"link": "SETUP.md ← app.py"}])
        self.assertEqual(out["episodic_trace"], [])

    def test_every_round_s_endings_and_new_rules_are_kept_and_the_last_round_s_gaps_ask_the_user(self):
        # Given
        self.decide(1, {"endings": [{"stumble": "Stopped at step 4: var/ missing", "ending": "fixed"}],
                        "rules": ["Type each step first", "Run each step in a fresh clone"],
                        "gaps": [], "links": []})
        self.decide(2, {"endings": [{"stumble": "No source for the token", "ending": "to the caller: ask the user"}],
                        "rules": [], "gaps": ["Who gives the API token?"], "links": ["SETUP.md ← app.py"]})
        # When
        result = self.run_assemble()
        # Then
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = self.returned()
        self.assertEqual(out["semantic_gist"], [
            {"difference": "Stopped at step 4: var/ missing → fixed"},
            {"difference": "No source for the token → to the caller: ask the user"}])
        self.assertEqual(out["constraints"], GIVEN["constraints"] + [{"rule": "Run each step in a fresh clone"}])
        self.assertEqual(out["uncertainty_signal"], [{"gap": "Who gives the API token?"}])
        self.assertEqual(out["predictive_cue"], [{"next": "ask the user"}])

    def test_rounds_are_read_in_number_order(self):
        # Given
        for n in (1, 2, 10):
            self.decide(n, {"endings": [{"stumble": f"round {n}", "ending": "fixed"}], "rules": [],
                            "gaps": [], "links": []})
        # When
        self.run_assemble("stopped: generator-11")
        # Then
        self.assertEqual([d["difference"] for d in self.returned()["semantic_gist"]],
                         ["round 1 → fixed", "round 2 → fixed", "round 10 → fixed"])

    def test_a_reason_for_the_caller_comes_before_questions_for_the_user(self):
        # Given
        self.decide(1, {"endings": [
            {"stumble": "Docker or not", "ending": "to the caller: the acceptance says nothing on Docker"},
            {"stumble": "Same cause after remake", "ending": "to the caller: the cause remains"},
            {"stumble": "No token", "ending": "to the caller: ask the user"}],
            "rules": [], "gaps": ["Who gives the API token?"], "links": []})
        # When
        self.run_assemble()
        # Then
        self.assertEqual(self.returned()["predictive_cue"], [
            {"next": "to the caller: the acceptance says nothing on Docker; the cause remains"}])

    def test_a_stopped_turn_returns_stopped_with_the_rounds_decided_so_far(self):
        # Given
        self.decide(1, {"endings": [{"stumble": "var/ missing", "ending": "fixed"}], "rules": [],
                        "gaps": [], "links": []})
        # When
        result = self.run_assemble("stopped: generator-2")
        # Then
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = self.returned()
        self.assertEqual(out["predictive_cue"], [{"next": "stopped: generator-2"}])
        self.assertEqual(out["semantic_gist"], [{"difference": "var/ missing → fixed"}])

    def test_a_turn_stopped_before_any_decision_returns_stopped_and_nothing_else_new(self):
        # Given
        work = self.work
        # When
        result = self.run_assemble("stopped: first-user-1")
        # Then
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = self.returned()
        self.assertEqual(out["predictive_cue"], [{"next": "stopped: first-user-1"}])
        self.assertEqual((out["semantic_gist"], out["relational_map"]), ([], []))
        self.assertEqual(os.listdir(work), [])

    def test_no_decision_and_no_stop_writes_nothing(self):
        # Given
        work = self.work
        # When
        result = self.run_assemble()
        # Then
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"no evaluator decision in {work}", result.stdout)
        self.assertFalse(os.path.exists(self.out_path))

    def test_a_decision_out_of_form_names_its_file_and_writes_nothing(self):
        # Given
        cases = ["{not json", {"endings": [{"stumble": "x"}], "rules": [], "gaps": [], "links": []},
                 {"endings": [], "rules": "one", "gaps": [], "links": []}, {"endings": []},
                 {"endings": [{"stumble": "x", "ending": "patched"}], "rules": [], "gaps": [], "links": []}]
        for text in cases:
            with self.subTest(text=text):
                self.decide(1, text)
                # When
                result = self.run_assemble()
                # Then
                self.assertEqual(result.returncode, 1)
                self.assertIn("evaluator-1.json", result.stdout)
                self.assertFalse(os.path.exists(self.out_path))

    def test_a_call_without_in_out_and_work_shows_how_to_call_it(self):
        # Given
        command = [sys.executable, ENTRY, self.in_path, self.out_path]
        # When
        result = subprocess.run(command, capture_output=True, text=True)
        # Then
        self.assertEqual(result.returncode, 2)
        self.assertIn("assemble.py <in> <out> <work>", result.stdout)


if __name__ == "__main__":
    unittest.main()

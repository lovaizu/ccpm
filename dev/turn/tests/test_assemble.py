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
        # Given: one round whose decision has no stumble and one link
        self.decide(1, {"endings": [], "rules": [], "gaps": [], "links": ["SETUP.md ← app.py"]})
        # When: the CCS to return is built
        result = self.run_assemble()
        # Then: it keeps the deliverable, receiver, goal, sources and constraints as received, says next is done, holds the link, and drops the earlier differences, gaps and records
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
        # Given: two rounds, the first with a fix and a new rule beside one already given, the second with a question for the user
        self.decide(1, {"endings": [{"stumble": "Stopped at step 4: var/ missing", "ending": "fixed", "grounds": ["first-user-1#2"]}],
                        "rules": ["Type each step first", "Run each step in a fresh clone"],
                        "gaps": [], "links": []})
        self.decide(2, {"endings": [{"stumble": "No source for the token", "ending": "to the caller: ask the user", "grounds": ["first-user-1#2"]}],
                        "rules": [], "gaps": ["Who gives the API token?"], "links": ["SETUP.md ← app.py"]})
        # When: the CCS to return is built
        result = self.run_assemble()
        # Then: it holds both rounds' differences, adds only the new rule, carries the last round's question, and says next is to ask the user
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = self.returned()
        self.assertEqual(out["semantic_gist"], [
            {"difference": "Stopped at step 4: var/ missing → fixed"},
            {"difference": "No source for the token → to the caller: ask the user"}])
        self.assertEqual(out["constraints"], GIVEN["constraints"] + [{"rule": "Run each step in a fresh clone"}])
        self.assertEqual(out["uncertainty_signal"], [{"gap": "Who gives the API token?"}])
        self.assertEqual(out["predictive_cue"], [{"next": "ask the user"}])

    def test_a_question_or_reason_for_the_caller_from_an_earlier_round_is_kept_to_the_end(self):
        # Given: round 1 with a fix, a question for the user and a reason for the caller, and round 2 with nothing left to fix
        self.decide(1, {"endings": [{"stumble": "var/ missing", "ending": "fixed", "grounds": ["first-user-1#2"]},
                                    {"stumble": "No source for the token", "ending": "to the caller: ask the user", "grounds": ["first-user-1#3"]},
                                    {"stumble": "Docker or not", "ending": "to the caller: the acceptance says nothing on Docker", "grounds": ["first-user-1#4"]}],
                        "rules": [], "gaps": ["Who gives the API token?"], "links": []})
        self.decide(2, {"endings": [], "rules": [], "gaps": [], "links": []})
        # When: the CCS to return is built
        result = self.run_assemble()
        # Then: the question and the reason are still returned, the reason as next
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = self.returned()
        self.assertEqual(out["uncertainty_signal"], [{"gap": "Who gives the API token?"}])
        self.assertEqual(out["predictive_cue"], [{"next": "to the caller: the acceptance says nothing on Docker"}])

    def test_rounds_are_read_in_number_order(self):
        # Given: decisions for rounds 1, 2 and 10
        for n in (1, 2, 10):
            self.decide(n, {"endings": [{"stumble": f"round {n}", "ending": "fixed", "grounds": ["first-user-1#2"]}], "rules": [],
                            "gaps": [], "links": []})
        # When: the CCS to return is built for a turn stopped at the generator of round 11
        self.run_assemble("stopped: generator-11")
        # Then: the differences follow the rounds in number order, 10 last
        self.assertEqual([d["difference"] for d in self.returned()["semantic_gist"]],
                         ["round 1 → fixed", "round 2 → fixed", "round 10 → fixed"])

    def test_a_reason_for_the_caller_comes_before_questions_for_the_user(self):
        # Given: a round with two reasons for the caller and one question for the user
        self.decide(1, {"endings": [
            {"stumble": "Docker or not", "ending": "to the caller: the acceptance says nothing on Docker", "grounds": ["first-user-1#2"]},
            {"stumble": "Same cause after remake", "ending": "to the caller: the cause remains", "grounds": ["first-user-1#2"]},
            {"stumble": "No token", "ending": "to the caller: ask the user", "grounds": ["first-user-1#2"]}],
            "rules": [], "gaps": ["Who gives the API token?"], "links": []})
        # When: the CCS to return is built
        self.run_assemble()
        # Then: next gives the two reasons for the caller, joined, and not the question
        self.assertEqual(self.returned()["predictive_cue"], [
            {"next": "to the caller: the acceptance says nothing on Docker; the cause remains"}])

    def test_a_stopped_turn_returns_stopped_with_the_rounds_decided_so_far(self):
        # Given: a turn with round 1 decided
        self.decide(1, {"endings": [{"stumble": "var/ missing", "ending": "fixed", "grounds": ["first-user-1#2"]}], "rules": [],
                        "gaps": [], "links": []})
        # When: the CCS to return is built for a turn stopped at the generator of round 2
        result = self.run_assemble("stopped: generator-2")
        # Then: next says where it stopped, and round 1's difference is kept
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = self.returned()
        self.assertEqual(out["predictive_cue"], [{"next": "stopped: generator-2"}])
        self.assertEqual(out["semantic_gist"], [{"difference": "var/ missing → fixed"}])

    def test_a_turn_stopped_before_any_decision_returns_stopped_and_nothing_else_new(self):
        # Given: a turn with no decision yet
        work = self.work
        # When: the CCS to return is built for a turn stopped at the first user of round 1
        result = self.run_assemble("stopped: first-user-1")
        # Then: next says where it stopped, there are no differences or links, and nothing is added to the work folder
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        out = self.returned()
        self.assertEqual(out["predictive_cue"], [{"next": "stopped: first-user-1"}])
        self.assertEqual((out["semantic_gist"], out["relational_map"]), ([], []))
        self.assertEqual(os.listdir(work), [])

    def test_no_decision_and_no_stop_writes_nothing(self):
        # Given: a turn with no decision that was not stopped
        work = self.work
        # When: the CCS to return is built
        result = self.run_assemble()
        # Then: it fails, says the work folder has no decision, and writes no CCS
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"no evaluator decision in {work}", result.stdout)
        self.assertFalse(os.path.exists(self.out_path))

    def test_a_decision_out_of_form_names_its_file_and_writes_nothing(self):
        # Given: decisions out of form: not JSON, a part missing or not a list, an ending missing, not one of the allowed endings or with words after asking the user, and grounds missing, empty or not text
        cases = ["{not json", {"endings": [{"stumble": "x", "grounds": ["a#1"]}], "rules": [], "gaps": [], "links": []},
                 {"endings": [], "rules": "one", "gaps": [], "links": []}, {"endings": []},
                 {"endings": [{"stumble": "x", "ending": "patched", "grounds": ["first-user-1#2"]}], "rules": [], "gaps": [], "links": []},
                 {"endings": [{"stumble": "x", "ending": "to the caller: ask the user. The viewpoint says so",
                               "grounds": ["first-user-1#2"]}], "rules": [], "gaps": ["Who?"], "links": []},
                 {"endings": [{"stumble": "x", "ending": "fixed"}], "rules": [], "gaps": [], "links": []},
                 {"endings": [{"stumble": "x", "ending": "fixed", "grounds": []}], "rules": [], "gaps": [],
                  "links": []},
                 {"endings": [{"stumble": "x", "ending": "fixed", "grounds": [3]}], "rules": [], "gaps": [],
                  "links": []}]
        for text in cases:
            with self.subTest(text=text):
                self.decide(1, text)
                # When: the CCS to return is built on each
                result = self.run_assemble()
                # Then: each fails, names the decision's file, and writes no CCS
                self.assertEqual(result.returncode, 1)
                self.assertIn("evaluator-1.json", result.stdout)
                self.assertFalse(os.path.exists(self.out_path))

    def test_a_call_without_in_out_and_work_shows_how_to_call_it(self):
        # Given: a call that gives the CCS received and the place to write but no work folder
        command = [sys.executable, ENTRY, self.in_path, self.out_path]
        # When: it is made
        result = subprocess.run(command, capture_output=True, text=True)
        # Then: it fails and shows how to call it
        self.assertEqual(result.returncode, 2)
        self.assertIn("assemble.py <in> <out> <work>", result.stdout)


if __name__ == "__main__":
    unittest.main()

"""Tests for building the CCS to return from the one received and each round's judgments and learnings."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
ENTRY = os.path.join(PLUGIN_ROOT, "scripts", "assemble.py")

STARTS = "Starts the app without asking anyone"
TYPED = "/plugin/viewpoints/setup.md:1"
GIVEN = {
    "focal_entities": [{"deliverable": "SETUP.md"}, {"receiver": "A new team member"}],
    "goal_orientation": [{"acceptance": STARTS}],
    "retrieved_artifacts": [{"viewpoint": "/plugin/viewpoints/setup.md"}],
    "constraints": [{"language": "English"}, {"answer": "Ask Sato for the token"}],
    "episodic_trace": [{"generator-1": "from the turn before"}],
    "semantic_gist": [],
    "relational_map": [{"learning": "from the turn before"}],
    "predictive_cue": [{"next": "stopped: first-user-1"}],
    "uncertainty_signal": [{"more": f"{STARTS}: from the turn before"}],
}


def good(point):
    return {"point": point, "judgment": "good", "grounds": ["first-user-1#1"]}


def more(point, short="step 3 needs var/"):
    return {"point": point, "judgment": "more", "fell_short": short, "grounds": ["first-user-1#2"]}


def unsettled(point, why, question=None):
    p = {"point": point, "judgment": "unsettled", "why": why, "grounds": ["SETUP.md:3"]}
    return dict(p, question=question) if question else p


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

    def put(self, name, data):
        with open(os.path.join(self.work, name), "w", encoding="utf-8") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))

    def judge(self, n, *points):
        self.put(f"evaluator-{n}.json", {"points": list(points)})

    def learn(self, n, *learnings):
        self.put(f"learner-{n}.json", {"learnings": [{"learning": text, "grounds": ["generator-1#1"]}
                                                     for text in learnings]})

    def run_assemble(self, *extra):
        return subprocess.run([sys.executable, ENTRY, self.in_path, self.out_path, self.work, *extra],
                              capture_output=True, text=True)

    def returned(self):
        result = self.run_assemble()
        self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)
        with open(self.out_path, encoding="utf-8") as f:
            return json.load(f)

    def test_every_point_good_returns_done_and_keeps_what_the_plugin_wrote(self):
        # Given: one round in which every point is Good
        self.judge(1, good(STARTS), good(TYPED))
        self.learn(1)
        # When: the CCS to return is built
        out = self.returned()
        # Then: next is done, nothing is carried on, and the parts the plugin wrote are as received
        self.assertEqual(out["predictive_cue"], [{"next": "done"}])
        self.assertEqual((out["uncertainty_signal"], out["relational_map"], out["semantic_gist"],
                          out["episodic_trace"]), ([], [], [], []))
        for part in ("focal_entities", "goal_orientation", "retrieved_artifacts", "constraints"):
            self.assertEqual(out[part], GIVEN[part])

    def test_a_point_only_the_user_can_settle_asks_the_user_with_its_question(self):
        # Given: one round in which every point is Good but one only the user can settle
        self.judge(1, good(STARTS), unsettled(TYPED, "no source says who hands out the token", "Who gives the token?"))
        self.learn(1, "The token step rests on a fact no source gives")
        # When: the CCS to return is built
        out = self.returned()
        # Then: next asks the user, the question is a gap, and the round's learning is carried on
        self.assertEqual(out["predictive_cue"], [{"next": "ask the user"}])
        self.assertEqual(out["uncertainty_signal"], [{"gap": "Who gives the token?"}])
        self.assertEqual(out["relational_map"], [{"learning": "The token step rests on a fact no source gives"}])

    def test_a_point_what_it_should_be_does_not_settle_goes_to_the_caller_before_the_user(self):
        # Given: one round with a point the measure does not settle, and a question for the user
        self.judge(1, unsettled(STARTS, "the acceptance says nothing on Docker"),
                   unsettled(TYPED, "no source says who hands out the token", "Who gives the token?"))
        self.learn(1)
        # When: the CCS to return is built
        out = self.returned()
        # Then: next goes to the caller with the point and why, and the question is still a gap
        self.assertEqual(out["predictive_cue"],
                         [{"next": f"to the caller: {STARTS}: the acceptance says nothing on Docker"}])
        self.assertEqual(out["uncertainty_signal"], [{"gap": "Who gives the token?"}])

    def test_a_remake_that_brings_it_closer_returns_the_last_version_s_judgments(self):
        # Given: round 1 with two Mores, and round 2 that turned one into Good and the other no worse
        self.judge(1, more(STARTS), more(TYPED, "step 2 was never typed"))
        self.learn(1, "round 1's learning")
        self.judge(2, good(STARTS), good(TYPED))
        self.learn(2, "round 2's learning")
        # When: the CCS to return is built
        out = self.returned()
        # Then: it is done, with round 2's learning
        self.assertEqual(out["predictive_cue"], [{"next": "done"}])
        self.assertEqual(out["relational_map"], [{"learning": "round 2's learning"}])

    def test_a_remake_that_brings_it_no_closer_returns_the_version_before_it_to_the_caller(self):
        # Given: round 1 with a More and a Good, and round 2 that turned the More into Good and the Good into More
        self.judge(1, more(STARTS), good(TYPED))
        self.learn(1, "round 1's learning")
        self.judge(2, good(STARTS), more(TYPED, "step 2 was never typed"))
        self.learn(2, "round 2's learning")
        # When: the CCS to return is built
        out = self.returned()
        # Then: it goes to the caller, saying the remake brought it no closer, with round 1's More and learning
        self.assertEqual(out["predictive_cue"],
                         [{"next": "to the caller: a remake brought the deliverable no closer"}])
        self.assertEqual(out["uncertainty_signal"], [{"more": f"{STARTS}: step 3 needs var/"}])
        self.assertEqual(out["relational_map"], [{"learning": "round 1's learning"}])

    def test_a_remake_that_turns_no_more_into_good_brings_it_no_closer(self):
        # Given: round 1 with a More, and round 2 in which it is still More
        self.judge(1, more(STARTS), good(TYPED))
        self.learn(1)
        self.judge(2, more(STARTS, "step 4 needs var/"), good(TYPED))
        self.learn(2)
        # When: the CCS to return is built
        out = self.returned()
        # Then: it goes to the caller with round 1's More
        self.assertEqual(out["predictive_cue"],
                         [{"next": "to the caller: a remake brought the deliverable no closer"}])
        self.assertEqual(out["uncertainty_signal"], [{"more": f"{STARTS}: step 3 needs var/"}])

    def test_rounds_are_read_in_number_order(self):
        # Given: eleven rounds, the tenth bringing it no closer than the ninth and the eleventh closer than the tenth
        for n in range(1, 12):
            self.judge(n, more(STARTS) if n in (9, 10) else good(STARTS), more(TYPED) if n < 11 else good(TYPED))
            self.learn(n, f"round {n}")
        # When: the CCS to return is built
        out = self.returned()
        # Then: round 11 is compared with round 10, not round 2 with round 11, and is returned
        self.assertEqual(out["relational_map"], [{"learning": "round 11"}])

    def test_a_stopped_turn_returns_stopped_with_the_last_judged_version_s_judgments(self):
        # Given: a turn stopped after round 1 was judged with a More
        self.judge(1, more(STARTS), good(TYPED))
        self.learn(1, "round 1's learning")
        # When: the CCS to return is built as stopped
        result = self.run_assemble("stopped: first-user-2")
        # Then: next says where to carry on from, with round 1's More and learning
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with open(self.out_path, encoding="utf-8") as f:
            out = json.load(f)
        self.assertEqual(out["predictive_cue"], [{"next": "stopped: first-user-2"}])
        self.assertEqual(out["uncertainty_signal"], [{"more": f"{STARTS}: step 3 needs var/"}])
        self.assertEqual(out["relational_map"], [{"learning": "round 1's learning"}])

    def test_a_turn_stopped_before_any_judgment_returns_the_judgments_it_received(self):
        # Given: a turn stopped before any round was judged
        work = self.work
        # When: the CCS to return is built as stopped
        result = subprocess.run([sys.executable, ENTRY, self.in_path, self.out_path, work, "stopped: first-user-1"],
                                capture_output=True, text=True)
        # Then: next says where to carry on from, and the received Mores and learnings are kept
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with open(self.out_path, encoding="utf-8") as f:
            out = json.load(f)
        self.assertEqual(out["predictive_cue"], [{"next": "stopped: first-user-1"}])
        self.assertEqual(out["uncertainty_signal"], GIVEN["uncertainty_signal"])
        self.assertEqual(out["relational_map"], GIVEN["relational_map"])

    def test_no_judgment_and_no_stop_writes_nothing(self):
        # Given: a turn with no judgment that was not stopped
        work = self.work
        # When: the CCS to return is built
        result = self.run_assemble()
        # Then: it fails, says the work folder has no judgment, and writes no CCS
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"no evaluator judgment in {work}", result.stdout)
        self.assertFalse(os.path.exists(self.out_path))

    def test_a_judgment_out_of_form_names_its_file_and_writes_nothing(self):
        # Given: judgments out of form: not JSON, no list of points, a point not text, a judgment not one of the three, a More without what fell short, an unsettled point without why or with a question not text, and grounds missing, empty or not text
        cases = ["{not json", {"judgments": []}, {"points": [dict(good(STARTS), point=3)]},
                 {"points": [dict(good(STARTS), judgment="fixed")]},
                 {"points": [{"point": STARTS, "judgment": "more", "grounds": ["first-user-1#1"]}]},
                 {"points": [{"point": STARTS, "judgment": "unsettled", "grounds": ["first-user-1#1"]}]},
                 {"points": [unsettled(STARTS, "x", 3)]},
                 {"points": [{"point": STARTS, "judgment": "good"}]}, {"points": [dict(good(STARTS), grounds=[])]},
                 {"points": [dict(good(STARTS), grounds=[3])]}]
        self.learn(1)
        for text in cases:
            with self.subTest(text=text):
                self.put("evaluator-1.json", text)
                # When: the CCS to return is built on each
                result = self.run_assemble()
                # Then: each fails, names the judgment's file, and writes no CCS
                self.assertEqual(result.returncode, 1)
                self.assertIn("evaluator-1.json", result.stdout)
                self.assertFalse(os.path.exists(self.out_path))

    def test_learnings_out_of_form_name_their_file_and_write_nothing(self):
        # Given: a judged round whose learnings are missing, not a list, or a learning without grounds
        self.judge(1, good(STARTS))
        cases = [None, {"learnings": "one"}, {"learnings": [{"learning": "x"}]}]
        for data in cases:
            with self.subTest(data=data):
                path = os.path.join(self.work, "learner-1.json")
                if data is None:
                    if os.path.exists(path):
                        os.remove(path)
                else:
                    self.put("learner-1.json", data)
                # When: the CCS to return is built on each
                result = self.run_assemble()
                # Then: each fails, names the learner's file, and writes no CCS
                self.assertEqual(result.returncode, 1)
                self.assertIn("learner-1.json", result.stdout)
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

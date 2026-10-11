"""Tests for the steps of a turn that a script does, run as turn:up runs them."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "turn")
ENTRY = os.path.join(PLUGIN_ROOT, "scripts", "up.py")
SESSION = "11111111-2222-3333-4444-555555555555"

CCS = {
    "focal_entities": [{"deliverable": "SETUP.md"}, {"receiver": "A new team member"}],
    "goal_orientation": [{"acceptance": "Starts the app by following the guide alone"},
                         {"use": "Run the steps from the top"}],
    "retrieved_artifacts": [{"viewpoint": "setup.md"}],
    "constraints": [{"language": "English"}],
    "episodic_trace": [], "semantic_gist": [], "relational_map": [], "predictive_cue": [],
    "uncertainty_signal": [],
}
LET_GO = {"endings": [{"stumble": "the title is plain", "ending": "let go: it still works", "grounds": ["first-user-1#1"]}],
          "rules": [], "gaps": [], "links": []}
CAUSES = {"causes": [{"stumble": "no var/", "cause": "assumed var/", "way_of_working": True,
                     "grounds": ["first-user-1#1"]}]}
FIX = {"endings": [{"stumble": "no var/", "cause": "assumed var/", "ending": "fixed", "grounds": ["first-user-1#1"]}],
       "rules": [], "gaps": [], "links": []}


class UpTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.home = os.path.join(self.root, "home")
        self.repo = os.path.join(self.root, "repo")
        os.makedirs(self.repo)
        self.git("init", "-q")
        self.write("setup.md", "- Steps run as typed.\n")
        self.write(".t/in.json", json.dumps(CCS))
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "start")

    def tearDown(self):
        shutil.rmtree(self.root)

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True)

    def write(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def run_up(self, *args, env=None):
        env = env or dict(os.environ, HOME=self.home)
        return subprocess.run([sys.executable, ENTRY, *args], cwd=self.repo, env=env,
                              capture_output=True, text=True)

    def start(self):
        result = self.run_up("start", ".t/in.json", ".t/out.json", SESSION)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        work = result.stdout.splitlines()[0][len("work: "):]
        self.addCleanup(shutil.rmtree, work, True)
        return work

    def copy(self, work):
        self.write("SETUP.md", "# Setup\n")
        result = self.run_up("copy", work)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        folder = result.stdout.strip()
        self.addCleanup(shutil.rmtree, folder, True)
        return folder

    def decide(self, work, n, decision):
        with open(os.path.join(work, f"evaluator-{n}.json"), "w", encoding="utf-8") as f:
            f.write(decision if isinstance(decision, str) else json.dumps(decision))

    def agent(self, agent):
        path = os.path.join(self.home, ".claude", "projects", "-repo", SESSION, "subagents",
                            f"agent-{agent}.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Read", "input": {"file_path": "app.py"}}]}}) + "\n")

    def returned(self):
        with open(os.path.join(self.repo, ".t", "out.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_start_makes_the_session_s_work_folder_and_shows_what_to_pass_on(self):
        # Given
        given = ".t/in.json"
        # When
        result = self.run_up("start", given, ".t/out.json", SESSION)
        lines = result.stdout.splitlines()
        self.addCleanup(shutil.rmtree, lines[0][len("work: "):], True)
        # Then
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(lines[0], "work: " + os.path.join(tempfile.gettempdir(), "turn-try-" + SESSION))
        self.assertEqual(lines[1:], ["deliverable: SETUP.md", "receiver: A new team member",
                                     "use: Run the steps from the top", "viewpoint: setup.md"])

    def test_start_writes_out_what_the_deliverable_should_be_to_be_read_whole(self):
        # Given
        self.write(".t/in.json", json.dumps(dict(CCS, constraints=[
            {"language": "English"}, {"rule": "Type each step first"}, {"answer": "Ask Sato"}],
            retrieved_artifacts=[{"viewpoint": "setup.md"}, {"source": "setup.md"}])))
        # When
        work = self.start()
        # Then
        with open(os.path.join(work, "should.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "# What the deliverable should be\n\n"
                             "- deliverable: SETUP.md\n- receiver: A new team member\n"
                             "- acceptance: Starts the app by following the guide alone\n"
                             "- use: Run the steps from the top\n- viewpoint: setup.md\n- source: setup.md\n"
                             "- language: English\n- rule: Type each step first\n- answer: Ask Sato\n")

    def test_start_replaces_the_work_folder_of_a_turn_cut_off_in_the_same_session(self):
        # Given
        work = self.start()
        with open(os.path.join(work, "evaluator-1.json"), "w", encoding="utf-8") as f:
            f.write("{}")
        # When
        again = self.start()
        # Then
        self.assertEqual(again, work)
        self.assertFalse(os.path.exists(os.path.join(work, "evaluator-1.json")))

    def test_start_on_a_ccs_out_of_form_shows_the_problems_and_makes_no_work_folder(self):
        # Given
        self.write(".t/in.json", json.dumps(dict(CCS, focal_entities=[])))
        before = set(os.listdir(tempfile.gettempdir()))
        # When
        result = self.run_up("start", ".t/in.json", ".t/out.json", SESSION)
        # Then
        self.assertEqual((result.returncode, result.stdout),
                         (1, "focal_entities has no deliverable\nfocal_entities has no receiver\n"))
        self.assertEqual(set(os.listdir(tempfile.gettempdir())), before)

    def test_start_without_jq_says_how_to_install_it(self):
        # Given
        tools = os.path.join(self.root, "bin")
        os.makedirs(tools)
        os.symlink(shutil.which("git"), os.path.join(tools, "git"))
        env = dict(os.environ, HOME=self.home, PATH=tools)
        # When
        result = self.run_up("start", ".t/in.json", ".t/out.json", SESSION, env=env)
        # Then
        self.assertEqual(result.returncode, 1)
        self.assertIn("jq is not installed", result.stdout)

    def test_copy_is_a_fresh_clone_with_the_deliverable_added(self):
        # Given
        work = self.start()
        # When
        folder = self.copy(work)
        # Then
        self.assertTrue(os.path.isfile(os.path.join(folder, "SETUP.md")))
        self.assertTrue(os.path.isfile(os.path.join(folder, "setup.md")))

    def test_copy_without_the_deliverable_says_so_fails_and_leaves_nothing(self):
        # Given
        self.write(".t/in.json", json.dumps(dict(CCS, focal_entities=[{"deliverable": "GUIDE.md"}, {"receiver": "A new team member"}])))
        work = self.start()
        # When
        result = self.run_up("copy", work)
        # Then
        self.assertEqual(result.returncode, 1)
        self.assertIn("deliverable GUIDE.md does not exist", result.stdout)
        self.assertFalse(os.path.exists(work))

    def test_steps_turns_the_round_s_generator_and_first_user_records_into_numbered_steps(self):
        # Given
        work = self.start()
        self.agent("g1")
        self.agent("u1")
        # When
        result = self.run_up("steps", work, "g1", "u1")
        # Then
        self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)
        for name in ("generator-1", "first-user-1"):
            with open(os.path.join(work, f"steps-{name}.json"), encoding="utf-8") as f:
                self.assertEqual([s["step"] for s in json.load(f)], [f"{name}#1"])
            self.assertTrue(os.path.isfile(os.path.join(work, f"steps-{name}.md")))

    def test_steps_without_a_record_says_whose_is_missing(self):
        # Given
        work = self.start()
        self.agent("g1")
        # When
        result = self.run_up("steps", work, "g1", "u9")
        # Then
        self.assertEqual((result.returncode, result.stdout), (1, "no conversation record for first-user-1 (u9)\n"))

    def test_a_round_with_a_stumble_to_fix_goes_to_the_next_round_and_deletes_the_copy(self):
        # Given
        work = self.start()
        folder = self.copy(work)
        self.decide(work, 1, FIX)
        # When
        result = self.run_up("round", work)
        # Then
        self.assertEqual((result.returncode, result.stdout), (0, "next round\n"))
        self.assertFalse(os.path.exists(folder))
        self.decide(work, 2, LET_GO)
        self.assertEqual(self.run_up("round", work).stdout, "end\n")

    def test_a_round_with_nothing_to_fix_ends_the_turn(self):
        # Given
        work = self.start()
        self.copy(work)
        self.decide(work, 1, LET_GO)
        # When
        result = self.run_up("round", work)
        # Then
        self.assertEqual((result.returncode, result.stdout), (0, "end\n"))

    def test_a_decision_out_of_form_is_shown_and_the_copy_is_kept(self):
        # Given
        work = self.start()
        folder = self.copy(work)
        self.decide(work, 1, "{not json")
        # When
        result = self.run_up("round", work)
        # Then
        self.assertEqual(result.returncode, 1)
        self.assertIn("evaluator-1.json is not a decision", result.stdout)
        self.assertTrue(os.path.isdir(folder))

    def test_end_writes_the_ccs_to_return_and_deletes_the_work_folder(self):
        # Given
        work = self.start()
        self.copy(work)
        self.decide(work, 1, LET_GO)
        self.run_up("round", work)
        for agent in ("g1", "u1", "l1", "e1"):
            self.agent(agent)
        # When
        result = self.run_up("end", work, "generator-1=g1", "first-user-1=u1",
                             "learner-1=l1", "evaluator-1=e1")
        # Then
        self.assertEqual((result.returncode, result.stdout),
                         (0, f"next: done\nccs: {os.path.join(self.repo, '.t', 'out.json')}\n"))
        out = self.returned()
        self.assertEqual(out["episodic_trace"][:4] + out["episodic_trace"][5:],
                         [{"generator-1": "read: app.py"}, {"first-user-1": "read: app.py"},
                          {"learner-1": "read: app.py"}, {"evaluator-1": "read: app.py"},
                          {"evidence": ".t/out.evidence.json"}])
        self.assertFalse(os.path.exists(work))

    def test_end_writes_the_evidence_of_every_round_beside_the_returned_ccs(self):
        # Given
        work = self.start()
        for agent in ("g1", "u1", "l1", "e1", "g2", "u2", "l2", "e2"):
            self.agent(agent)
        self.run_up("steps", work, "g1", "u1")
        with open(os.path.join(work, "learner-1.json"), "w", encoding="utf-8") as f:
            json.dump(CAUSES, f)
        self.decide(work, 1, FIX)
        self.run_up("round", work)
        self.run_up("steps", work, "g2", "u2")
        self.decide(work, 2, LET_GO)
        self.run_up("round", work)
        # When
        result = self.run_up("end", work, "generator-1=g1", "first-user-1=u1", "learner-1=l1",
                             "evaluator-1=e1", "generator-2=g2", "first-user-2=u2", "learner-2=l2",
                             "evaluator-2=e2")
        # Then
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with open(os.path.join(self.repo, ".t", "out.evidence.json"), encoding="utf-8") as f:
            evidence = json.load(f)
        self.assertEqual([r["round"] for r in evidence["rounds"]], [1, 2])
        self.assertEqual([s["step"] for s in evidence["rounds"][0]["steps"]],
                         ["generator-1#1", "first-user-1#1"])
        self.assertEqual(evidence["rounds"][0]["causes"], CAUSES["causes"])
        self.assertEqual(evidence["rounds"][1]["causes"], [])
        self.assertEqual(evidence["rounds"][1]["endings"], LET_GO["endings"])

    def test_end_when_stopped_returns_where_to_carry_on_and_deletes_the_copy(self):
        # Given
        work = self.start()
        folder = self.copy(work)
        self.agent("g1")
        # When
        result = self.run_up("end", work, "stopped: first-user-1", "generator-1=g1")
        # Then
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], "next: stopped: first-user-1")
        self.assertFalse(os.path.exists(folder))
        self.assertFalse(os.path.exists(work))

    def test_end_that_meets_a_problem_shows_it_and_leaves_no_ccs(self):
        # Given
        work = self.start()
        self.decide(work, 1, LET_GO)
        # When
        result = self.run_up("end", work, "generator-1=missing")
        # Then
        self.assertEqual(result.returncode, 1)
        self.assertIn("no conversation record for generator-1", result.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".t", "out.json")))
        self.assertFalse(os.path.exists(work))

    def test_a_call_not_in_the_four_forms_shows_how_to_call_it(self):
        # Given
        calls = [[], ["start", ".t/in.json", ".t/out.json"], ["steps", "w", "g1"], ["round"], ["end"],
                 ["other"]]
        # When
        results = [self.run_up(*args) for args in calls]
        # Then
        for result in results:
            self.assertEqual(result.returncode, 2)
            self.assertIn("up.py start <in> <out> <session id>", result.stdout)


if __name__ == "__main__":
    unittest.main()

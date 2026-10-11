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
        # Given: a CCS in good form
        given = ".t/in.json"
        # When: a turn starts on it
        result = self.run_up("start", given, ".t/out.json", SESSION)
        lines = result.stdout.splitlines()
        self.addCleanup(shutil.rmtree, lines[0][len("work: "):], True)
        # Then: it gets a work folder named by the session and prints the deliverable, receiver, use and viewpoint to hand on
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(lines[0], "work: " + os.path.join(tempfile.gettempdir(), "turn-try-" + SESSION))
        self.assertEqual(lines[1:], ["deliverable: SETUP.md", "receiver: A new team member",
                                     "use: Run the steps from the top", "viewpoint: setup.md"])

    def test_start_writes_out_what_the_deliverable_should_be_to_be_read_whole(self):
        # Given: a CCS with a rule, a user's answer and a source
        self.write(".t/in.json", json.dumps(dict(CCS, constraints=[
            {"language": "English"}, {"rule": "Type each step first"}, {"answer": "Ask Sato"}],
            retrieved_artifacts=[{"viewpoint": "setup.md"}, {"source": "setup.md"}])))
        # When: a turn starts on it
        work = self.start()
        # Then: should.md holds every line of what the deliverable should be, the rule and the answer among them
        with open(os.path.join(work, "should.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "# What the deliverable should be\n\n"
                             "- deliverable: SETUP.md\n- receiver: A new team member\n"
                             "- acceptance: Starts the app by following the guide alone\n"
                             "- use: Run the steps from the top\n- viewpoint: setup.md\n- source: setup.md\n"
                             "- language: English\n- rule: Type each step first\n- answer: Ask Sato\n")

    def test_start_replaces_the_work_folder_of_a_turn_cut_off_in_the_same_session(self):
        # Given: a turn of this session was cut off and left a decision behind
        work = self.start()
        with open(os.path.join(work, "evaluator-1.json"), "w", encoding="utf-8") as f:
            f.write("{}")
        # When: the turn starts again
        again = self.start()
        # Then: it gets the same work folder, empty of what the cut-off turn left
        self.assertEqual(again, work)
        self.assertFalse(os.path.exists(os.path.join(work, "evaluator-1.json")))

    def test_start_on_a_ccs_out_of_form_shows_the_problems_and_makes_no_work_folder(self):
        # Given: a CCS with no deliverable and no receiver
        self.write(".t/in.json", json.dumps(dict(CCS, focal_entities=[])))
        before = set(os.listdir(tempfile.gettempdir()))
        # When: a turn starts on it
        result = self.run_up("start", ".t/in.json", ".t/out.json", SESSION)
        # Then: it prints both problems, fails, and makes no work folder
        self.assertEqual((result.returncode, result.stdout),
                         (1, "focal_entities has no deliverable\nfocal_entities has no receiver\n"))
        self.assertEqual(set(os.listdir(tempfile.gettempdir())), before)

    def test_start_without_jq_says_how_to_install_it(self):
        # Given: a machine with git but no jq
        tools = os.path.join(self.root, "bin")
        os.makedirs(tools)
        os.symlink(shutil.which("git"), os.path.join(tools, "git"))
        env = dict(os.environ, HOME=self.home, PATH=tools)
        # When: a turn starts
        result = self.run_up("start", ".t/in.json", ".t/out.json", SESSION, env=env)
        # Then: it fails and says jq is not installed
        self.assertEqual(result.returncode, 1)
        self.assertIn("jq is not installed", result.stdout)

    def test_copy_is_a_fresh_clone_with_the_deliverable_added(self):
        # Given: a turn whose deliverable has been made
        work = self.start()
        # When: the copy for the first user is made
        folder = self.copy(work)
        # Then: the copy holds the repository's files and the deliverable
        self.assertTrue(os.path.isfile(os.path.join(folder, "SETUP.md")))
        self.assertTrue(os.path.isfile(os.path.join(folder, "setup.md")))

    def test_copy_without_the_deliverable_says_so_fails_and_leaves_nothing(self):
        # Given: a turn whose deliverable was never made
        self.write(".t/in.json", json.dumps(dict(CCS, focal_entities=[{"deliverable": "GUIDE.md"}, {"receiver": "A new team member"}])))
        work = self.start()
        # When: the copy for the first user is made
        result = self.run_up("copy", work)
        # Then: it says the deliverable does not exist, fails, and the work folder is gone
        self.assertEqual(result.returncode, 1)
        self.assertIn("deliverable GUIDE.md does not exist", result.stdout)
        self.assertFalse(os.path.exists(work))

    def test_steps_turns_the_round_s_generator_and_first_user_records_into_numbered_steps(self):
        # Given: the generator's and the first user's records of round 1
        work = self.start()
        self.agent("g1")
        self.agent("u1")
        # When: their steps are written
        result = self.run_up("steps", work, "g1", "u1")
        # Then: each has a steps file, its steps numbered by agent and round
        self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)
        for name in ("generator-1", "first-user-1"):
            with open(os.path.join(work, f"steps-{name}.json"), encoding="utf-8") as f:
                self.assertEqual([s["step"] for s in json.load(f)], [f"{name}#1"])
            self.assertTrue(os.path.isfile(os.path.join(work, f"steps-{name}.md")))

    def test_steps_without_a_record_says_whose_is_missing(self):
        # Given: the generator has a record but the first user named has none
        work = self.start()
        self.agent("g1")
        # When: their steps are written
        result = self.run_up("steps", work, "g1", "u9")
        # Then: it fails and names the first user's record as missing
        self.assertEqual((result.returncode, result.stdout), (1, "no conversation record for first-user-1 (u9)\n"))

    def test_a_round_with_a_stumble_to_fix_goes_to_the_next_round_and_deletes_the_copy(self):
        # Given: round 1's decision has a stumble to fix
        work = self.start()
        folder = self.copy(work)
        self.decide(work, 1, FIX)
        # When: the round is closed
        result = self.run_up("round", work)
        # Then: the turn goes on to round 2, the copy is gone, and a round 2 with nothing to fix ends the turn
        self.assertEqual((result.returncode, result.stdout), (0, "next round\n"))
        self.assertFalse(os.path.exists(folder))
        self.decide(work, 2, LET_GO)
        self.assertEqual(self.run_up("round", work).stdout, "end\n")

    def test_a_round_with_nothing_to_fix_ends_the_turn(self):
        # Given: round 1's decision has nothing to fix
        work = self.start()
        self.copy(work)
        self.decide(work, 1, LET_GO)
        # When: the round is closed
        result = self.run_up("round", work)
        # Then: the turn ends
        self.assertEqual((result.returncode, result.stdout), (0, "end\n"))

    def test_a_decision_out_of_form_is_shown_and_the_copy_is_kept(self):
        # Given: round 1's decision file is not valid JSON
        work = self.start()
        folder = self.copy(work)
        self.decide(work, 1, "{not json")
        # When: the round is closed
        result = self.run_up("round", work)
        # Then: it fails, names the file, and keeps the copy for a new evaluator
        self.assertEqual(result.returncode, 1)
        self.assertIn("evaluator-1.json is not a decision", result.stdout)
        self.assertTrue(os.path.isdir(folder))

    def test_end_writes_the_ccs_to_return_and_deletes_the_work_folder(self):
        # Given: a turn that ended with nothing to fix, with the record of each agent
        work = self.start()
        self.copy(work)
        self.decide(work, 1, LET_GO)
        self.run_up("round", work)
        for agent in ("g1", "u1", "l1", "e1"):
            self.agent(agent)
        # When: the turn is ended
        result = self.run_up("end", work, "generator-1=g1", "first-user-1=u1",
                             "learner-1=l1", "evaluator-1=e1")
        # Then: it prints next and the CCS's place, the CCS names what each agent read and the evidence, and the work folder is gone
        self.assertEqual((result.returncode, result.stdout),
                         (0, f"next: done\nccs: {os.path.join(self.repo, '.t', 'out.json')}\n"))
        out = self.returned()
        self.assertEqual(out["episodic_trace"][:4] + out["episodic_trace"][5:],
                         [{"generator-1": "read: app.py"}, {"first-user-1": "read: app.py"},
                          {"learner-1": "read: app.py"}, {"evaluator-1": "read: app.py"},
                          {"evidence": ".t/out.evidence.json"}])
        self.assertFalse(os.path.exists(work))

    def test_end_writes_the_evidence_of_every_round_beside_the_returned_ccs(self):
        # Given: a turn of two rounds, the first with a cause to fix
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
        # When: the turn is ended
        result = self.run_up("end", work, "generator-1=g1", "first-user-1=u1", "learner-1=l1",
                             "evaluator-1=e1", "generator-2=g2", "first-user-2=u2", "learner-2=l2",
                             "evaluator-2=e2")
        # Then: the evidence file beside the CCS holds both rounds, with their steps, causes and endings
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
        # Given: the user stopped the turn after the generator of round 1
        work = self.start()
        folder = self.copy(work)
        self.agent("g1")
        # When: the turn is ended as stopped
        result = self.run_up("end", work, "stopped: first-user-1", "generator-1=g1")
        # Then: next says to carry on from the first user of round 1, and the copy and work folder are gone
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], "next: stopped: first-user-1")
        self.assertFalse(os.path.exists(folder))
        self.assertFalse(os.path.exists(work))

    def test_end_that_meets_a_problem_shows_it_and_leaves_no_ccs(self):
        # Given: a turn whose generator has no conversation record
        work = self.start()
        self.decide(work, 1, LET_GO)
        # When: the turn is ended
        result = self.run_up("end", work, "generator-1=missing")
        # Then: it fails, says whose record is missing, writes no CCS and leaves no work folder
        self.assertEqual(result.returncode, 1)
        self.assertIn("no conversation record for generator-1", result.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".t", "out.json")))
        self.assertFalse(os.path.exists(work))

    def test_a_call_not_in_the_four_forms_shows_how_to_call_it(self):
        # Given: calls with missing or unknown arguments
        calls = [[], ["start", ".t/in.json", ".t/out.json"], ["steps", "w", "g1"], ["round"], ["end"],
                 ["other"]]
        # When: each is made
        results = [self.run_up(*args) for args in calls]
        # Then: each fails and shows how to call it
        for result in results:
            self.assertEqual(result.returncode, 2)
            self.assertIn("up.py start <in> <out> <session id>", result.stdout)


if __name__ == "__main__":
    unittest.main()

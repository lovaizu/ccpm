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
    "retrieved_artifacts": [{"viewpoint": "viewpoint.md"}],
    "constraints": [{"language": "English"}],
    "episodic_trace": [], "semantic_gist": [], "relational_map": [], "predictive_cue": [],
    "uncertainty_signal": [],
}
GOOD = {"points": [{"point": "Starts the app by following the guide alone", "judgment": "good",
                    "grounds": ["first-user-1#1"]}]}
MORE = {"points": [{"point": "Starts the app by following the guide alone", "judgment": "more",
                    "fell_short": "step 3 needs var/", "grounds": ["first-user-1#1"]}]}
LEARNINGS = {"learnings": [{"learning": "The steps were written where var/ already existed",
                            "grounds": ["generator-1#1"]}]}


class UpTest(unittest.TestCase):

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.home = os.path.join(self.root, "home")
        self.repo = os.path.join(self.root, "repo")
        os.makedirs(self.repo)
        self.git("init", "-q")
        self.write("viewpoint.md", "- Steps run as typed.\n")
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

    def copy(self, work, text="# Setup\n"):
        self.make(text)
        result = self.run_up("copy", work)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        folder = result.stdout.strip()
        self.addCleanup(shutil.rmtree, folder, True)
        return folder

    def judge(self, work, n, judgment, learnings=None):
        with open(os.path.join(work, f"evaluator-{n}.json"), "w", encoding="utf-8") as f:
            f.write(judgment if isinstance(judgment, str) else json.dumps(judgment))
        with open(os.path.join(work, f"learner-{n}.json"), "w", encoding="utf-8") as f:
            json.dump(learnings or LEARNINGS, f)

    def make(self, text):
        """The generator makes or remakes the deliverable."""
        self.write("SETUP.md", text)

    def deliverable(self):
        with open(os.path.join(self.repo, "SETUP.md"), encoding="utf-8") as f:
            return f.read()

    def report(self, work, name, text):
        with open(os.path.join(work, name), "w", encoding="utf-8") as f:
            f.write(text)

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
        # Then: it gets a work folder named by the session and prints the deliverable, receiver and use to hand on
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(lines[0], "work: " + os.path.join(tempfile.gettempdir(), "turn-try-" + SESSION))
        self.assertEqual(lines[1:], ["deliverable: SETUP.md", "receiver: A new team member",
                                     "use: Run the steps from the top"])

    def test_start_writes_out_what_the_deliverable_should_be_to_be_read_whole(self):
        # Given: a CCS with a rule, a user's answer and a source
        self.write(".t/in.json", json.dumps(dict(CCS, constraints=[
            {"language": "English"}, {"rule": "Type each step first"}, {"answer": "Ask Sato"}],
            retrieved_artifacts=[{"viewpoint": "viewpoint.md"}, {"source": "viewpoint.md"}])))
        # When: a turn starts on it
        work = self.start()
        # Then: should.md holds every line of what the deliverable should be, the rule and the answer among them
        with open(os.path.join(work, "should.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "# What the deliverable should be\n\n"
                             "- deliverable: SETUP.md\n- receiver: A new team member\n"
                             "- acceptance: Starts the app by following the guide alone\n"
                             "- use: Run the steps from the top\n- viewpoint: viewpoint.md\n- source: viewpoint.md\n"
                             "- language: English\n- rule: Type each step first\n- answer: Ask Sato\n")

    def test_start_hands_round_one_the_mores_and_learnings_of_the_ccs_received(self):
        # Given: a CCS returned by an earlier turn, with a More and a learning
        self.write(".t/in.json", json.dumps(dict(
            CCS, uncertainty_signal=[{"more": "Starts the app: step 3 needs var/"}, {"gap": "Who gives the token?"}],
            relational_map=[{"learning": "The steps were written where var/ already existed"}])))
        # When: a turn starts on it
        result = self.run_up("start", ".t/in.json", ".t/out.json", SESSION)
        work = result.stdout.splitlines()[0][len("work: "):]
        self.addCleanup(shutil.rmtree, work, True)
        # Then: it names remake-1.md last, which holds the learning first and the More after for round 1's generator, and not the question
        self.assertEqual(result.stdout.splitlines()[-1], "remake: " + os.path.join(work, "remake-1.md"))
        with open(os.path.join(work, "remake-1.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "# What to remake the deliverable from\n\n## Why the last version came out away from what it should be\n\n"
                             "- The steps were written where var/ already existed\n\n## Where that showed\n\n"
                             "- Starts the app: step 3 needs var/\n")

    def test_start_on_a_ccs_with_no_mores_or_learnings_hands_round_one_nothing_to_remake_from(self):
        # Given: a CCS with no More and no learning
        given = CCS
        # When: a turn starts on it
        work = self.start()
        # Then: there is no remake-1.md
        self.assertEqual(given["uncertainty_signal"], [])
        self.assertFalse(os.path.exists(os.path.join(work, "remake-1.md")))

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

    def test_copy_is_a_fresh_clone_with_the_deliverable_added_and_keeps_the_version_used(self):
        # Given: a turn whose deliverable has been made
        work = self.start()
        # When: the copy for the first user is made
        folder = self.copy(work, "# Setup v1\n")
        # Then: the copy holds the repository's files and the deliverable, and the work folder keeps that version
        self.assertTrue(os.path.isfile(os.path.join(folder, "SETUP.md")))
        self.assertTrue(os.path.isfile(os.path.join(folder, "viewpoint.md")))
        with open(os.path.join(work, "version-1"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "# Setup v1\n")

    def test_copy_leaves_out_every_committed_file_that_holds_the_acceptance(self):
        # Given: a turn whose CCS, holding the acceptance, is committed in the repository
        work = self.start()
        # When: the copy for the first user is made
        folder = self.copy(work)
        # Then: the copy has no CCS, and keeps the deliverable and the other files
        self.assertFalse(os.path.exists(os.path.join(folder, ".t", "in.json")))
        self.assertTrue(os.path.isfile(os.path.join(folder, "SETUP.md")))
        self.assertTrue(os.path.isfile(os.path.join(folder, "viewpoint.md")))

    def test_copy_keeps_the_deliverable_even_when_it_quotes_the_acceptance(self):
        # Given: a turn whose deliverable quotes the acceptance
        work = self.start()
        self.write("SETUP.md", "# Setup\n\nStarts the app by following the guide alone.\n")
        # When: the copy for the first user is made
        result = self.run_up("copy", work)
        folder = result.stdout.strip()
        self.addCleanup(shutil.rmtree, folder, True)
        # Then: the deliverable is in the copy as it was made
        with open(os.path.join(folder, "SETUP.md"), encoding="utf-8") as f:
            self.assertIn("Starts the app by following the guide alone", f.read())

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

    def test_a_round_with_a_more_goes_on_hands_the_next_generator_what_to_remake_from_and_deletes_the_copy(self):
        # Given: round 1 judged with a More
        work = self.start()
        folder = self.copy(work)
        self.judge(work, 1, MORE)
        # When: the round is closed
        result = self.run_up("round", work)
        # Then: the turn goes on to round 2, whose generator gets the learning first and the More after, and the copy is gone
        self.assertEqual((result.returncode, result.stdout), (0, "next round\n"))
        with open(os.path.join(work, "remake-2.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "# What to remake the deliverable from\n\n## Why the last version came out away from what it should be\n\n"
                             "- The steps were written where var/ already existed\n\n## Where that showed\n\n"
                             "- Starts the app by following the guide alone: step 3 needs var/\n")
        self.assertFalse(os.path.exists(folder))

    def test_a_round_with_no_more_ends_the_turn(self):
        # Given: round 1 judged with every point Good
        work = self.start()
        self.copy(work)
        self.judge(work, 1, GOOD)
        # When: the round is closed
        result = self.run_up("round", work)
        # Then: the turn ends
        self.assertEqual((result.returncode, result.stdout), (0, "end\n"))

    def test_a_remake_that_brings_it_closer_goes_on_while_a_more_is_left(self):
        # Given: round 1 with two Mores, and round 2 that turned one into Good
        work = self.start()
        two = {"points": MORE["points"] + [dict(MORE["points"][0], point="viewpoint.md:1")]}
        self.copy(work)
        self.judge(work, 1, two)
        self.run_up("round", work)
        self.copy(work)
        self.judge(work, 2, {"points": GOOD["points"] + two["points"][1:]})
        # When: round 2 is closed
        result = self.run_up("round", work)
        # Then: the turn goes on to round 3
        self.assertEqual((result.returncode, result.stdout), (0, "next round\n"))

    def test_a_remake_that_brings_it_no_closer_ends_the_turn(self):
        # Given: round 1 with a More, and round 2 in which it is still More
        work = self.start()
        self.copy(work)
        self.judge(work, 1, MORE)
        self.run_up("round", work)
        self.copy(work)
        self.judge(work, 2, MORE)
        # When: round 2 is closed
        result = self.run_up("round", work)
        # Then: the turn ends
        self.assertEqual((result.returncode, result.stdout), (0, "end\n"))

    def test_a_judgment_out_of_form_is_shown_and_the_copy_is_kept(self):
        # Given: round 1's judgment file is not valid JSON
        work = self.start()
        folder = self.copy(work)
        self.judge(work, 1, "{not json")
        # When: the round is closed
        result = self.run_up("round", work)
        # Then: it fails, names the file, and keeps the copy for a new evaluator
        self.assertEqual(result.returncode, 1)
        self.assertIn("evaluator-1.json is not a judgment", result.stdout)
        self.assertTrue(os.path.isdir(folder))

    def test_a_round_closed_before_its_judgment_is_written_says_so_and_keeps_the_copy(self):
        # Given: round 1's copy made, and no judgment written
        work = self.start()
        folder = self.copy(work)
        # When: the round is closed
        result = self.run_up("round", work)
        # Then: it fails, says round 1 has no judgment, and keeps the copy for an evaluator
        self.assertEqual((result.returncode, result.stdout), (1, f"no judgment of round 1 in {work}\n"))
        self.assertTrue(os.path.isdir(folder))

    def test_end_writes_the_ccs_to_return_and_deletes_the_work_folder(self):
        # Given: a turn that ended with every point Good, with the record of each agent
        work = self.start()
        self.copy(work)
        self.judge(work, 1, GOOD)
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

    def test_end_after_a_remake_that_brought_it_no_closer_puts_back_the_version_before_it(self):
        # Given: round 1's version judged with a More, and round 2's remake still More
        work = self.start()
        self.copy(work, "# Setup v1\n")
        self.judge(work, 1, MORE)
        self.run_up("round", work)
        self.copy(work, "# Setup v2\n")
        self.judge(work, 2, MORE)
        self.run_up("round", work)
        for agent in ("g1", "u1", "l1", "e1", "g2", "u2", "l2", "e2"):
            self.agent(agent)
        # When: the turn is ended
        result = self.run_up("end", work, "generator-1=g1", "first-user-1=u1", "learner-1=l1", "evaluator-1=e1",
                             "generator-2=g2", "first-user-2=u2", "learner-2=l2", "evaluator-2=e2")
        # Then: the deliverable is round 1's version, and next goes to the caller
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.deliverable(), "# Setup v1\n")
        self.assertEqual(self.returned()["predictive_cue"],
                         [{"next": "to the caller: a remake brought the deliverable no closer"}])

    def test_end_when_stopped_after_a_remake_puts_back_the_last_version_used(self):
        # Given: round 1's version judged with a More, and the user stopped the turn after round 2's generator
        work = self.start()
        self.copy(work, "# Setup v1\n")
        self.judge(work, 1, MORE)
        self.run_up("round", work)
        self.make("# Setup v2, never used\n")
        for agent in ("g1", "u1", "l1", "e1", "g2"):
            self.agent(agent)
        # When: the turn is ended as stopped
        result = self.run_up("end", work, "stopped: first-user-2", "generator-1=g1", "first-user-1=u1",
                             "learner-1=l1", "evaluator-1=e1", "generator-2=g2")
        # Then: the deliverable is round 1's version, next says where to carry on, and round 1's More is returned
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines()[0], "next: stopped: first-user-2")
        self.assertEqual(self.deliverable(), "# Setup v1\n")
        self.assertEqual(self.returned()["uncertainty_signal"],
                         [{"more": "Starts the app by following the guide alone: step 3 needs var/"}])

    def test_end_when_stopped_before_any_judgment_puts_back_the_deliverable_as_the_turn_found_it(self):
        # Given: a deliverable from an earlier turn, and the user stopped this turn after round 1's generator
        self.make("# Setup from the turn before\n")
        work = self.start()
        folder = self.copy(work, "# Setup v1, never judged\n")
        self.agent("g1")
        # When: the turn is ended as stopped
        result = self.run_up("end", work, "stopped: first-user-1", "generator-1=g1")
        # Then: the deliverable is as the turn found it, and the copy and work folder are gone
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.deliverable(), "# Setup from the turn before\n")
        self.assertFalse(os.path.exists(folder))
        self.assertFalse(os.path.exists(work))

    def test_end_when_stopped_before_any_judgment_of_a_new_deliverable_leaves_none(self):
        # Given: no deliverable yet, and the user stopped the turn after round 1's generator made one
        work = self.start()
        self.make("# Setup v1, never judged\n")
        self.agent("g1")
        # When: the turn is ended as stopped
        result = self.run_up("end", work, "stopped: first-user-1", "generator-1=g1")
        # Then: no deliverable is left
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "SETUP.md")))

    def test_end_when_stopped_puts_back_a_deliverable_folder_as_the_turn_found_it(self):
        # Given: a deliverable folder from an earlier turn, and the user stopped this turn after round 1's generator rewrote it
        self.write(".t/in.json", json.dumps(dict(CCS, focal_entities=[{"deliverable": "docs"},
                                                                      {"receiver": "A new team member"}])))
        self.write("docs/a.md", "from the turn before\n")
        work = self.start()
        os.remove(os.path.join(self.repo, "docs", "a.md"))
        self.write("docs/b.md", "never judged\n")
        self.agent("g1")
        # When: the turn is ended as stopped
        result = self.run_up("end", work, "stopped: first-user-1", "generator-1=g1")
        # Then: the folder holds what the turn found, and nothing the generator wrote
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(os.listdir(os.path.join(self.repo, "docs")), ["a.md"])

    def test_end_with_a_judgment_out_of_form_shows_it_and_leaves_no_ccs(self):
        # Given: a turn whose round 1 judgment is not valid JSON
        work = self.start()
        self.judge(work, 1, "{not json")
        # When: the turn is ended
        result = self.run_up("end", work, "generator-1=g1")
        # Then: it fails, names the file, writes no CCS and leaves no work folder
        self.assertEqual(result.returncode, 1)
        self.assertIn("evaluator-1.json is not a judgment", result.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".t", "out.json")))
        self.assertFalse(os.path.exists(work))

    def test_end_writes_the_evidence_of_every_round_beside_the_returned_ccs(self):
        # Given: a turn of two rounds, the first with a More, each with both agents' reports
        work = self.start()
        for agent in ("g1", "u1", "l1", "e1", "g2", "u2", "l2", "e2"):
            self.agent(agent)
        for n, judgment in ((1, MORE), (2, GOOD)):
            self.copy(work)
            self.report(work, f"generator-{n}.md", f"made v{n}\n")
            self.report(work, f"first-user-{n}.md", f"ran it {n}\n")
            self.run_up("steps", work, f"g{n}", f"u{n}")
            self.judge(work, n, judgment)
            self.run_up("round", work)
        # When: the turn is ended
        result = self.run_up("end", work, "generator-1=g1", "first-user-1=u1", "learner-1=l1",
                             "evaluator-1=e1", "generator-2=g2", "first-user-2=u2", "learner-2=l2",
                             "evaluator-2=e2")
        # Then: the evidence beside the CCS says round 2 was returned, and holds each round's steps, reports, learnings and judgments
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with open(os.path.join(self.repo, ".t", "out.evidence.json"), encoding="utf-8") as f:
            evidence = json.load(f)
        self.assertEqual(evidence["returned_round"], 2)
        self.assertEqual([r["round"] for r in evidence["rounds"]], [1, 2])
        first = evidence["rounds"][0]
        self.assertEqual([s["step"] for s in first["steps"]], ["generator-1#1", "first-user-1#1"])
        self.assertEqual((first["generator_report"], first["first_user_report"]), ("made v1\n", "ran it 1\n"))
        self.assertEqual(first["learnings"], LEARNINGS["learnings"])
        self.assertEqual(first["judgments"], MORE["points"])
        self.assertEqual(evidence["rounds"][1]["judgments"], GOOD["points"])

    def test_end_that_meets_a_problem_shows_it_and_leaves_no_ccs(self):
        # Given: a turn whose generator has no conversation record
        work = self.start()
        self.judge(work, 1, GOOD)
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

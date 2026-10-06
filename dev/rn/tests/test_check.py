"""Each of rn's checks stops its breaking case and lets its passing case through.

Run from the plugin's parent directory: python3 -m unittest discover -s dev/rn/tests
"""
import json
import os
import re
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.join(HERE, "..", "..", "..", "rn")
CHECK = os.path.join(PLUGIN, "hooks", "check.py")

STEERING = """---
rn: 0.9.0
pr: https://github.com/you/repo/pull/1
status: running
artifact-language: English
conversation-language: Japanese
readme: README.md
design: docs/design.md
verification: docs/verification.md
---

# Goal

A wrong type fails the build.

# Acceptance criteria

## Attractive quality

- A1: Code reproducing each bug fails the build

## Must-be quality

- M1: The app builds as before

# Assumptions

# Rules

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off
"""

VERIFICATION = """# verification

## Scenes

### A1: Code reproducing each bug fails the build

- A scene.

    Passes when it fails the build, and M1 holds.

## Machine checks
"""

SDIR = ".rn/20261003-typescript"


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout


class Repo:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.remote = os.path.join(self.tmp.name, "remote.git")
        self.dir = os.path.join(self.tmp.name, "work")
        self.data = os.path.join(self.tmp.name, "data")
        sh(self.tmp.name, "git", "init", "-q", "--bare", "-b", "main", self.remote)
        sh(self.tmp.name, "git", "clone", "-q", self.remote, self.dir)
        sh(self.dir, "git", "config", "user.name", "t")
        sh(self.dir, "git", "config", "user.email", "t@example.com")
        self.write("README.md", "app\n")
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-qm", "init")
        sh(self.dir, "git", "push", "-qu", "origin", "main")
        sh(self.dir, "git", "remote", "set-head", "origin", "main")
        sh(self.dir, "git", "switch", "-qc", "session")
        self.write(f"{SDIR}/steering.md", STEERING)
        self.write("docs/verification.md", VERIFICATION)
        self.commit("rn: start\n\n● plan ── started → working out the plan")
        sh(self.dir, "git", "push", "-qu", "origin", "session")

    def write(self, rel, text):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text)
        return p

    def commit(self, msg):
        sh(self.dir, "git", "add", "-A")
        sh(self.dir, "git", "commit", "-qm", msg)

    def hook(self, event, **data):
        data.setdefault("cwd", self.dir)
        data.setdefault("session_id", "s1")
        env = dict(os.environ, CLAUDE_PLUGIN_DATA=self.data)
        r = subprocess.run(["python3", CHECK, event], input=json.dumps(data), cwd=self.dir,
                           capture_output=True, text=True, env=env)
        return r.returncode, r.stdout + r.stderr

    def after_commit(self):
        return self.hook("post", tool_name="Bash", tool_input={"command": "git commit -F m"})


PROPOSE = "rn: propose\n\n● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off"
PAUSE = "rn: pause\n\n● #3 cart ── half → paused at #3 cart"
REPORT = "# Report\n\nDoing as written, the build failed at cart.ts:3.\n"
PROPOSAL = ("rn: propose\n\n### What you get\n- Good A1: the build stops each bug, at a.ts:3\n"
            "- More: the key is unchecked, at b.ts:9\n\n"
            "● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off")
FINISHED = STEERING.replace("status: running", "status: finished") \
    .replace("### [ ] #1:", "### [x] #1:").replace("### [ ] #2:", "### [x] #2:")
QUOTING = STEERING.replace("### [ ] #2: Design sign-off",
                           "### [x] #2: Design sign-off\n### [ ] #3: Apply the discount before "
                           "the coupon\n\nServes: A1, M1")
PAUSED_MAP = ("── typescript: A wrong type fails the build. ──\n"
              "✅ #1 Plan sign-off / #2 Design sign-off\n"
              "👉 #3 Apply the discount before the coupon ── ここで一時停止\n\n"
              "● #3 Apply the discount before the coupon ── half → paused at #3 Apply the discount "
              "before the coupon\n\n次: /clear してから /rn:up")


class Checks(unittest.TestCase):
    def setUp(self):
        self.r = Repo()

    def tearDown(self):
        self.r.tmp.cleanup()

    def post_write(self, rel):
        return self.r.hook("post", tool_name="Write",
                           tool_input={"file_path": os.path.join(self.r.dir, rel)})

    def settle_report_whole(self):
        self.r.write(f"{SDIR}/open/01-report-task-3.md", REPORT)
        self.r.commit("rn: report\n\n● #3 cart ── report in → settle")
        os.remove(os.path.join(self.r.dir, SDIR, "open/01-report-task-3.md"))
        self.r.commit("rn: settle\n\n01-report-task-3.md:\n    # Report\n\n    Doing as written, the "
                      "build failed at cart.ts:3.\n\n● #3 cart ── purpose fulfilled → #4")

    def move_main_ahead(self):
        sh(self.r.dir, "git", "switch", "-q", "main")
        self.r.write("b.txt", "b\n")
        self.r.commit("main moves")
        sh(self.r.dir, "git", "push", "-q", "origin", "main")
        sh(self.r.dir, "git", "switch", "-q", "session")

    def pause_after_dn(self):
        self.r.hook("prompt", command_name="rn:dn")
        self.r.write("a.txt", "a\n")
        self.r.commit(PAUSE)
        self.r.after_commit()
        sh(self.r.dir, "git", "commit", "-q", "--amend", "-m",
           "rn: pause at #3\n\n● #3 cart ── half → paused at #3 cart")

    def commit_quoting_record_and_push(self):
        self.r.write(f"{SDIR}/steering.md", QUOTING)
        self.r.commit("rn: pause\n\n● #3 Apply the discount before the coupon ── half → paused at #3 "
                      "Apply the discount before the coupon")
        sh(self.r.dir, "git", "push", "-q")

    def first_user_write(self, path):
        return self.r.hook("pre", agent_type="rn:first-user", agent_id="f1", tool_name="Write",
                           tool_input={"file_path": path})

    def first_user_pre(self, tool, inp):
        return self.r.hook("pre", agent_type="rn:first-user", agent_id="f2", tool_name=tool,
                           tool_input=inp)

    # Check 1
    def test_steering_in_its_form_passes(self):
        # Given the steering.md the session started with
        # When it is written
        code, _ = self.post_write(f"{SDIR}/steering.md")
        # Then it passes
        self.assertEqual(code, 0)

    def test_steering_with_a_task_heading_out_of_form_is_stopped(self):
        # Given a task heading without its box and name
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("### [ ] #2:", "### #2"))
        # When it is written
        code, out = self.post_write(f"{SDIR}/steering.md")
        # Then it is stopped, naming the task heading
        self.assertEqual(code, 2)
        self.assertIn("task heading", out)

    def test_steering_repeating_a_task_id_is_stopped(self):
        # Given a second task #2
        self.r.write(f"{SDIR}/steering.md", STEERING + "### [ ] #2: again\n")
        # When it is written
        code, _ = self.post_write(f"{SDIR}/steering.md")
        # Then it is stopped
        self.assertEqual(code, 2)

    # Check 2
    def test_open_item_of_a_known_kind_passes(self):
        # Given an open/ item named as notes
        self.r.write(f"{SDIR}/open/01-notes-design.md", "x\n")
        # When it is written
        code, _ = self.post_write(f"{SDIR}/open/01-notes-design.md")
        # Then it passes
        self.assertEqual(code, 0)

    def test_open_item_of_an_unknown_kind_is_stopped(self):
        # Given an open/ item of a kind rn does not have
        self.r.write(f"{SDIR}/open/01-evaluation-design.md", "x\n")
        # When it is written
        code, out = self.post_write(f"{SDIR}/open/01-evaluation-design.md")
        # Then it is stopped, naming the file
        self.assertEqual(code, 2)
        self.assertIn("01-evaluation-design.md", out)

    # Check 3
    def test_verification_naming_an_undefined_criterion_is_stopped(self):
        # Given a verification document naming A9, which steering.md does not define
        self.r.write("docs/verification.md", VERIFICATION + "\n| a | A9 |\n")
        # When it is written
        code, out = self.post_write("docs/verification.md")
        # Then it is stopped, naming A9
        self.assertEqual(code, 2)
        self.assertIn("A9", out)

    def test_attractive_criterion_without_a_scene_is_stopped(self):
        # Given a verification document with no scene for A1
        self.r.write("docs/verification.md", VERIFICATION.replace("### A1:", "### X:"))
        # When it is written
        code, _ = self.post_write("docs/verification.md")
        # Then it is stopped
        self.assertEqual(code, 2)

    def test_criterion_served_by_no_task_is_stopped_once_tasks_are_planned(self):
        # Given a planned task serving A1 only
        self.r.write(f"{SDIR}/steering.md", STEERING + "### [ ] #3: move cart\n\nServes: A1\n")
        # When it is written
        code, out = self.post_write(f"{SDIR}/steering.md")
        # Then it is stopped, naming M1
        self.assertEqual(code, 2)
        self.assertIn("M1", out)

    def test_planned_tasks_serving_every_criterion_pass(self):
        # Given a planned task serving A1 and M1
        self.r.write(f"{SDIR}/steering.md", STEERING + "### [ ] #3: move cart\n\nServes: A1, M1\n")
        # When it is written
        code, _ = self.post_write(f"{SDIR}/steering.md")
        # Then it passes
        self.assertEqual(code, 0)

    def test_question_offering_ways_for_an_unwritten_criterion_is_stopped(self):
        # Given a question resting on A2, which steering.md does not define
        self.r.write(f"{SDIR}/open/01-notes-question.md", "Serves: A2\n\nWhich way for names?\n")
        # When it is written
        code, out = self.post_write(f"{SDIR}/open/01-notes-question.md")
        # Then it is stopped, naming A2
        self.assertEqual(code, 2)
        self.assertIn("A2", out)

    def test_question_without_a_serves_line_is_stopped(self):
        # Given a question that names nothing it rests on
        self.r.write(f"{SDIR}/open/01-notes-question.md", "Which way for names?\n")
        # When it is written
        code, out = self.post_write(f"{SDIR}/open/01-notes-question.md")
        # Then it is stopped, asking for the Serves line
        self.assertEqual(code, 2)
        self.assertIn("Serves:", out)

    def test_question_on_a_written_criterion_or_the_goal_passes(self):
        for first in ("Serves: A1, M1", "Serves: goal"):
            # Given a question resting on written criteria, or asking about the goal
            self.r.write(f"{SDIR}/open/01-notes-question.md", first + "\n\nWhich way?\n")
            # When it is written
            code, out = self.post_write(f"{SDIR}/open/01-notes-question.md")
            # Then it passes
            self.assertEqual(code, 0, out)

    # Check 4
    def test_commit_ending_in_a_decision_line_passes(self):
        # Given a commit whose last line is a decision line
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● #3 cart ── decided: fix → #3 cart")
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)

    def test_decision_line_followed_by_trailers_passes(self):
        # Given a decision line with a Co-Authored-By trailer after it
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● #3 cart ── decided: fix → #3 cart\n\n"
                      "Co-Authored-By: Claude <noreply@anthropic.com>")
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)

    def test_commit_without_a_decision_line_is_stopped(self):
        # Given a commit with no decision line
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a")
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it is stopped, asking for the decision line
        self.assertEqual(code, 2)
        self.assertIn("decision line", out)

    # Check 5
    def test_settled_report_quoted_whole_in_the_commit_passes(self):
        # Given a report removed from open/ by a commit that quotes it whole
        self.settle_report_whole()
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)

    def test_settled_report_cut_short_in_the_commit_is_stopped(self):
        # Given, after a whole settle, a report removed by a commit that quotes only part of it
        self.settle_report_whole()
        self.r.after_commit()
        self.r.write(f"{SDIR}/open/02-report-task-4.md", REPORT)
        self.r.commit("rn: report\n\n● #4 x ── report in → settle")
        os.remove(os.path.join(self.r.dir, SDIR, "open/02-report-task-4.md"))
        self.r.commit("rn: settle\n\n02-report-task-4.md: the build failed\n\n● #4 x ── done → #5")
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it is stopped, naming the report
        self.assertEqual(code, 2)
        self.assertIn("02-report-task-4.md", out)

    # Check 6
    def test_sign_off_with_a_report_left_open_is_stopped(self):
        # Given a sign-off commit with a report still in open/
        self.r.write(f"{SDIR}/open/01-report-plan.md", "x\n")
        self.r.commit(PROPOSE)
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it is stopped, naming the report
        self.assertEqual(code, 2)
        self.assertIn("01-report-plan.md", out)

    def test_sign_off_behind_the_default_branch_is_stopped(self):
        # Given main moved on and a sign-off commit without it
        self.move_main_ahead()
        self.r.write("c.txt", "c\n")
        self.r.commit(PROPOSE)
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it is stopped, saying main is not merged
        self.assertEqual(code, 2)
        self.assertIn("not merged", out)

    def test_sign_off_after_merging_the_default_branch_passes(self):
        # Given main moved on, then merged in before the sign-off commit
        self.move_main_ahead()
        self.r.write("c.txt", "c\n")
        self.r.commit(PROPOSE)
        self.r.after_commit()
        sh(self.r.dir, "git", "merge", "-q", "--no-edit", "origin/main")
        sh(self.r.dir, "git", "commit", "-q", "--allow-empty", "-m", PROPOSE)
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)

    def test_proposal_point_naming_no_criterion_is_stopped(self):
        # Given a proposal whose More point names no criterion
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSAL)
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it is stopped, quoting that point
        self.assertEqual(code, 2)
        self.assertIn("More: the key", out)

    def test_proposal_whose_every_point_names_a_criterion_passes(self):
        # Given the proposal amended so its More point names M1
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSAL)
        self.r.after_commit()
        sh(self.r.dir, "git", "commit", "-q", "--amend", "-m",
           PROPOSAL.replace("- More:", "- More M1:"))
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)

    # Check 7
    def test_sign_off_marked_without_ty_is_stopped(self):
        # Given a sign-off marked done with no /rn:ty typed
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("### [ ] #1:", "### [x] #1:"))
        self.r.commit("rn: approve\n\n● #1 Plan sign-off ── approved → #2 Design sign-off")
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it is stopped, naming /rn:ty
        self.assertEqual(code, 2)
        self.assertIn("/rn:ty", out)

    def test_sign_off_marked_after_ty_passes(self):
        # Given a sign-off marked done, and the user typed /rn:ty
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("### [ ] #1:", "### [x] #1:"))
        self.r.commit("rn: approve\n\n● #1 Plan sign-off ── approved → #2 Design sign-off")
        self.r.after_commit()
        self.r.hook("prompt", command_name="rn:ty")
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)

    def test_pause_without_dn_is_stopped(self):
        # Given a pause commit with no /rn:dn typed
        self.r.write("a.txt", "a\n")
        self.r.commit(PAUSE)
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it is stopped
        self.assertEqual(code, 2)

    def test_pause_after_dn_passes(self):
        # Given the user typed /rn:dn, then a pause commit
        self.r.hook("prompt", command_name="rn:dn")
        self.r.write("a.txt", "a\n")
        self.r.commit(PAUSE)
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)

    def test_amending_a_typed_pause_passes(self):
        # Given a pause made after /rn:dn, then amended
        self.pause_after_dn()
        # When the amended commit is checked
        code, _ = self.r.after_commit()
        # Then it passes without another /rn:dn
        self.assertEqual(code, 0)

    def test_second_pause_on_one_dn_is_stopped(self):
        # Given a pause made after /rn:dn and amended, then a second pause commit
        self.pause_after_dn()
        self.r.after_commit()
        self.r.write("b.txt", "b\n")
        self.r.commit("rn: pause\n\n● #3 cart ── more → paused at #3 cart")
        # When the second pause is checked
        code, _ = self.r.after_commit()
        # Then it is stopped
        self.assertEqual(code, 2)

    def test_finishing_without_ty_is_stopped(self):
        # Given a finishing commit with no /rn:ty typed
        self.r.write(f"{SDIR}/steering.md", FINISHED)
        self.r.commit("rn: finish\n\n● #2 Design sign-off ── approved → finished")
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it is stopped, naming /rn:ty
        self.assertEqual(code, 2)
        self.assertIn("/rn:ty", out)

    def test_finishing_after_ty_passes(self):
        # Given a finishing commit, and the user typed /rn:ty
        self.r.write(f"{SDIR}/steering.md", FINISHED)
        self.r.commit("rn: finish\n\n● #2 Design sign-off ── approved → finished")
        self.r.after_commit()
        self.r.hook("prompt", command_name="rn:ty")
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)

    # Checks 4–7 run between commit and push.
    def test_conductor_committing_and_pushing_in_one_command_is_stopped(self):
        for cmd in ("git commit -m x && git push", "git commit -m x; git push -u origin session",
                    "git add -A\ngit commit -m x\ngit push"):
            # Given the conductor about to commit and push in one command
            # When the command is checked
            code, out = self.r.hook("pre", tool_name="Bash", tool_input={"command": cmd})
            # Then it is stopped, asking for separate commands
            self.assertEqual(code, 2, cmd)
            self.assertIn("separate commands", out)

    def test_conductor_committing_or_pushing_alone_passes(self):
        for cmd in ("git commit -m x", "git push", "git add -A && git commit -F - <<'EOF'\n"
                    "rn: x\n\npush it later with git push\n\n● a ── b → c\nEOF"):
            # Given the conductor about to commit or push alone, `git push` at most in the message
            # When the command is checked
            code, _ = self.r.hook("pre", tool_name="Bash", tool_input={"command": cmd})
            # Then it passes
            self.assertEqual(code, 0, cmd)

    # Check 12
    def test_conductor_starting_an_agent_in_the_background_is_stopped(self):
        # Given the conductor about to start the generator in the background
        inp = {"subagent_type": "rn:generator", "prompt": "x", "run_in_background": True}
        # When the start is checked
        code, out = self.r.hook("pre", tool_name="Agent", tool_input=inp)
        # Then it is stopped, asking for the foreground
        self.assertEqual(code, 2)
        self.assertIn("foreground", out)

    def test_conductor_starting_an_agent_in_the_foreground_passes(self):
        # Given the conductor about to start the generator in the foreground
        inp = {"subagent_type": "rn:generator", "prompt": "x", "run_in_background": False}
        # When the start is checked
        code, _ = self.r.hook("pre", tool_name="Agent", tool_input=inp)
        # Then it passes
        self.assertEqual(code, 0)

    def test_conductor_continuing_an_agent_by_message_is_stopped(self):
        # Given the conductor about to continue an agent by message
        # When the message is checked
        code, out = self.r.hook("pre", tool_name="SendMessage",
                                tool_input={"to": "a1", "message": "carry on"})
        # Then it is stopped, asking for the foreground
        self.assertEqual(code, 2)
        self.assertIn("foreground", out)

    # Check 8
    def test_unpushed_commit_blocks_the_end(self):
        # Given a sign-off commit not pushed
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then the end is blocked
        self.assertIn('"decision": "block"', out)

    def test_pushed_commit_lets_the_end_through(self):
        # Given a sign-off commit pushed
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_unpushed_commit_blocks_the_second_end_too(self):
        # Given a commit not pushed
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● design ── agreed → writ rewrites the documents")
        # When the turn ends a second time
        _, out = self.r.hook("stop", stop_hook_active=True)
        # Then the end is blocked, saying it is not pushed
        self.assertIn("not pushed", out)

    def test_pushed_commit_lets_the_second_end_through(self):
        # Given a commit pushed
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a\n\n● design ── agreed → writ rewrites the documents")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends a second time
        _, out = self.r.hook("stop", stop_hook_active=True)
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_unpushed_finishing_commit_blocks_the_end(self):
        # Given the commit finishing the session, not pushed
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("status: running", "status: finished"))
        self.r.commit("rn: finish\n\n● #2 Design sign-off ── approved → finished")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then the end is blocked, saying it is not pushed
        self.assertIn("not pushed", out)

    def test_pushed_finishing_commit_lets_the_end_through(self):
        # Given the commit finishing the session, pushed
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("status: running", "status: finished"))
        self.r.commit("rn: finish\n\n● #2 Design sign-off ── approved → finished")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    # Check 13
    def test_ending_a_turn_with_nothing_for_the_user_is_blocked(self):
        # Given a pushed commit that leaves nothing for the user to decide
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: agree\n\n● design ── agreed → writ rewrites the documents")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then the end is blocked, saying to go on
        self.assertIn('"decision": "block"', out)
        self.assertIn("go on", out)

    def test_ending_a_turn_again_with_nothing_for_the_user_passes(self):
        # Given a pushed commit that leaves nothing for the user to decide
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: agree\n\n● design ── agreed → writ rewrites the documents")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends a second time
        _, out = self.r.hook("stop", stop_hook_active=True)
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_ending_a_turn_at_a_stop_passes(self):
        for line in ("● #1 Plan sign-off ── proposed → waiting for #1 Plan sign-off",
                     "● #1 Plan sign-off ── approved → #2 Design sign-off",
                     "● #3 cart ── half → paused at #3 cart"):
            # Given a pushed commit stopping for the user
            self.r.write("a.txt", line + "\n")
            self.r.commit("rn: x\n\n" + line + "\n\nCo-Authored-By: Claude <noreply@anthropic.com>")
            sh(self.r.dir, "git", "push", "-q")
            # When the turn ends
            _, out = self.r.hook("stop")
            # Then nothing is said
            self.assertEqual(out.strip(), "", line)

    def test_ending_a_turn_with_a_question_open_passes(self):
        # Given a pushed commit that leaves a question in open/
        self.r.write(f"{SDIR}/open/01-notes-question.md", "Serves: A1\n\nWhich way?\n")
        self.r.commit("rn: ask\n\n● design ── question written → asking the user")
        sh(self.r.dir, "git", "push", "-q")
        # When the turn ends
        _, out = self.r.hook("stop")
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    # Check 14
    def test_ending_a_turn_in_another_language_is_blocked_even_the_second_time(self):
        # Given a pushed sign-off and a Japanese conversation
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        sh(self.r.dir, "git", "push", "-q")
        english = "Which word should come before the code? I recommend A, since it matches the screen."
        for active in (False, True):
            # When the turn ends, the first time or the second, with an English message
            _, out = self.r.hook("stop", last_assistant_message=english, stop_hook_active=active)
            # Then the end is blocked, naming Japanese
            self.assertIn('"decision": "block"', out)
            self.assertIn("Japanese", out)

    def test_ending_a_turn_in_the_conversation_language_passes(self):
        # Given a pushed sign-off and a Japanese conversation
        self.r.write("a.txt", "a\n")
        self.r.commit(PROPOSE)
        sh(self.r.dir, "git", "push", "-q")
        for text in ("`src/account` を TypeScript にすることで、何を得たいですか？ "
                     "推奨は A です。`DISPLAY_NAME_KEY` を設定しないとアプリは起動しません。",
                     "── typescript: 型の誤りがビルドで止まる ──\n✅ #1 Plan sign-off\n"
                     "👉 #2 Design sign-off ── PR で読んで /rn:ty で承認、/rn:gm で修正依頼\n\n"
                     "メールだけで登録したユーザーにも、ちゃんとした名前を出します。",
                     "OK"):
            # When the turn ends with a Japanese message, or one too short to judge
            _, out = self.r.hook("stop", last_assistant_message=text)
            # Then nothing is said
            self.assertEqual(out.strip(), "", text)

    def test_japanese_map_quoting_the_record_passes(self):
        # Given a pushed pause whose task name is English
        self.commit_quoting_record_and_push()
        # When the turn ends with a Japanese map quoting the goal, task names and decision line
        _, out = self.r.hook("stop", last_assistant_message=PAUSED_MAP)
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_japanese_list_of_quoted_decision_lines_passes(self):
        # Given a pushed pause whose task name is English
        self.commit_quoting_record_and_push()
        bullets = "前回の承認からの変更:\n" + "".join(
            f"- ● #{n} Apply the discount before the coupon ── half → paused at #{n} Apply the "
            "discount before the coupon\n" for n in range(3, 9)) + "確認してください。"
        # When the turn ends with a Japanese list of quoted decision lines
        _, out = self.r.hook("stop", last_assistant_message=bullets)
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    def test_english_around_text_quoted_from_the_record_is_blocked(self):
        # Given a pushed pause whose task name is English
        self.commit_quoting_record_and_push()
        english = PAUSED_MAP.replace("ここで一時停止", "paused here").replace(
            "次: /clear してから /rn:up", "Next: clear the conversation, then take it up again.")
        # When the turn ends with the same map, its own words in English
        _, out = self.r.hook("stop", last_assistant_message=english)
        # Then the end is blocked, naming Japanese
        self.assertIn("Japanese", out)

    # After a summary
    def test_after_compact_the_record_is_read_again(self):
        # Given a running session
        # When the conversation is summarized
        code, out = self.r.hook("compact", source="compact")
        # Then the conductor is told to read steering.md and open/ again
        self.assertEqual(code, 0)
        self.assertIn(f"{SDIR}/steering.md", out)
        self.assertIn("open/", out)

    def test_after_compact_with_no_session_nothing_is_said(self):
        # Given no session on the branch
        sh(self.r.dir, "git", "rm", "-rq", ".rn")
        self.r.commit("drop")
        # When the conversation is summarized
        _, out = self.r.hook("compact", source="compact")
        # Then nothing is said
        self.assertEqual(out.strip(), "")

    # Check 9
    def test_subagent_committing_is_stopped(self):
        for agent in ("rn:generator", "rn:first-user", "general-purpose"):
            # Given a subagent
            # When it is about to commit
            code, _ = self.r.hook("pre", agent_type=agent, tool_name="Bash",
                                  tool_input={"command": "git commit -m x"})
            # Then it is stopped
            self.assertEqual(code, 2, agent)

    def test_conductor_committing_passes(self):
        # Given the conductor
        # When it is about to commit
        code, _ = self.r.hook("pre", tool_name="Bash", tool_input={"command": "git commit -m x"})
        # Then it passes
        self.assertEqual(code, 0)

    # Checks 9 and 11
    def test_agent_git_outside_the_sessions_repository_passes(self):
        # Given a clone of the session's repository for an agent to try the work in
        clone = os.path.join(self.r.tmp.name, "try")
        sh(self.r.tmp.name, "git", "clone", "-q", self.r.dir, clone)
        for agent in ("rn:generator", "rn:first-user"):
            for cmd in (f"cd {clone} && git commit -qam try", f"git -C {clone} log -3",
                        "grep -rn 'git push' docs", "rg 'git log' README.md"):
                # When an agent runs git in the clone, or only names git in text it searches for
                code, _ = self.r.hook("pre", agent_type=agent, agent_id="f3", tool_name="Bash",
                                      tool_input={"command": cmd})
                # Then it passes
                self.assertEqual(code, 0, (agent, cmd))

    def test_agent_git_on_the_sessions_repository_is_stopped(self):
        # Given a clone of the session's repository for an agent to try the work in
        clone = os.path.join(self.r.tmp.name, "try")
        sh(self.r.tmp.name, "git", "clone", "-q", self.r.dir, clone)
        for agent in ("rn:generator", "rn:first-user"):
            for cmd in (f"cd {clone} && git log; cd {self.r.dir} && git commit -m x",
                        f"git -C {self.r.dir} commit -m x"):
                # When an agent commits on the session's repository
                code, _ = self.r.hook("pre", agent_type=agent, agent_id="f3", tool_name="Bash",
                                      tool_input={"command": cmd})
                # Then it is stopped
                self.assertEqual(code, 2, (agent, cmd))

    # Check 10
    def test_first_user_writing_outside_open_is_stopped(self):
        # Given a first user that has written nothing
        # When it is about to write a source file
        code, _ = self.first_user_write(os.path.join(self.r.dir, "src.ts"))
        # Then it is stopped
        self.assertEqual(code, 2)

    def test_first_user_writing_its_new_report_passes(self):
        # Given a first user that has written nothing
        # When it is about to write a new report in open/
        code, _ = self.first_user_write(os.path.join(self.r.dir, SDIR, "open/03-report-task-3.md"))
        # Then it passes
        self.assertEqual(code, 0)

    def test_first_user_writing_its_report_again_passes(self):
        # Given a first user that has written its report
        mine = os.path.join(self.r.dir, SDIR, "open/03-report-task-3.md")
        self.first_user_write(mine)
        # When it is about to write that report again
        code, _ = self.first_user_write(mine)
        # Then it passes
        self.assertEqual(code, 0)

    def test_first_user_writing_another_report_is_stopped(self):
        # Given a first user that has written its report
        self.first_user_write(os.path.join(self.r.dir, SDIR, "open/03-report-task-3.md"))
        # When it is about to write another report
        code, _ = self.first_user_write(os.path.join(self.r.dir, SDIR, "open/04-report-task-4.md"))
        # Then it is stopped
        self.assertEqual(code, 2)

    # Check 11
    def test_first_user_reading_notes_is_blocked(self):
        # Given a first user
        # When it is about to read the generator's notes
        notes = os.path.join(self.r.dir, SDIR, "open/01-notes-task-3.md")
        code, _ = self.first_user_pre("Read", {"file_path": notes})
        # Then it is stopped
        self.assertEqual(code, 2)

    def test_first_user_reading_git_history_is_blocked(self):
        # Given a first user
        # When it is about to read the git log
        code, _ = self.first_user_pre("Bash", {"command": "git log -3"})
        # Then it is stopped
        self.assertEqual(code, 2)

    def test_first_user_reading_a_question_or_proposal_passes(self):
        for name in ("01-notes-question.md", "03-notes-proposal.md"):
            # Given a first user
            # When it is about to read the question or proposal it is given
            given = os.path.join(self.r.dir, SDIR, "open", name)
            code, _ = self.first_user_pre("Read", {"file_path": given})
            # Then it passes
            self.assertEqual(code, 0, name)

    def test_first_user_reading_the_readme_passes(self):
        # Given a first user
        # When it is about to read the README
        code, _ = self.first_user_pre("Read", {"file_path": os.path.join(self.r.dir, "README.md")})
        # Then it passes
        self.assertEqual(code, 0)

    # No session: nothing is checked.
    def test_ending_a_turn_with_no_session_passes(self):
        # Given no session on the branch
        sh(self.r.dir, "git", "rm", "-rq", ".rn")
        self.r.commit("drop")
        # When the turn ends
        code, _ = self.r.hook("stop")
        # Then it passes
        self.assertEqual(code, 0)

    def test_committing_with_no_session_passes(self):
        # Given no session on the branch, removed by a commit with no decision line
        sh(self.r.dir, "git", "rm", "-rq", ".rn")
        self.r.commit("drop")
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)


class Agents(unittest.TestCase):
    def front(self, name):
        text = open(os.path.join(PLUGIN, "agents", name)).read()
        return text.split("---")[1]

    def test_first_user_starts_without_claude_md(self):
        # Given the first user's definition
        # When its front matter is read
        front = self.front("first-user.md")
        # Then it skips CLAUDE.md
        self.assertRegex(front, r"(?m)^omitClaudeMd: true$")

    def test_generator_cannot_start_an_agent(self):
        # Given the generator's definition
        # When its front matter is read
        front = self.front("generator.md")
        # Then the Agent tool is disallowed
        self.assertRegex(front, r"(?m)^disallowedTools: .*\bAgent\b")


if __name__ == "__main__":
    unittest.main()

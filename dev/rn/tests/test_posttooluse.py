"""rn's PostToolUse hook: checks 1 to 3 after a record file is written, and checks 4 to 7
on a commit right after it is made."""
import os
import unittest

from harness import (FEEDBACK, FINISHED, PAUSE, PROPOSAL, PROPOSE, REPORT, SDIR, STEERING,
                     VERIFICATION, Session, sh)


class PostToolUse(Session):
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

    def test_steering_missing_a_front_matter_key_is_stopped(self):
        # Given a front matter that does not say where the verification document is
        self.r.write(f"{SDIR}/steering.md",
                     STEERING.replace("verification: docs/verification.md\n", ""))
        # When it is written
        code, out = self.post_write(f"{SDIR}/steering.md")
        # Then it is stopped, naming the key
        self.assertEqual(code, 2)
        self.assertIn("front matter has no `verification`", out)

    def test_steering_with_a_status_other_than_running_or_finished_is_stopped(self):
        # Given a status rn does not have
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("status: running", "status: paused"))
        # When it is written
        code, out = self.post_write(f"{SDIR}/steering.md")
        # Then it is stopped, naming the status
        self.assertEqual(code, 2)
        self.assertIn("`status`", out)

    def test_steering_missing_a_heading_is_stopped(self):
        # Given a steering.md without its `# Tasks` heading
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("# Tasks\n", ""))
        # When it is written
        code, out = self.post_write(f"{SDIR}/steering.md")
        # Then it is stopped, naming the heading
        self.assertEqual(code, 2)
        self.assertIn("heading `# Tasks` is missing", out)

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

    def test_task_serving_an_undefined_criterion_is_stopped(self):
        # Given a planned task serving A9, which no acceptance criterion has
        self.r.write(f"{SDIR}/steering.md",
                     STEERING + "### [ ] #3: move cart\n\nServes: A1, M1, A9\n")
        # When it is written
        code, out = self.post_write(f"{SDIR}/steering.md")
        # Then it is stopped, naming A9
        self.assertEqual(code, 2)
        self.assertIn("task refers to A9", out)

    def test_verification_missing_one_of_its_headings_is_stopped(self):
        for heading in ("## Scenes", "## Machine checks"):
            # Given a verification document without that heading
            self.r.write("docs/verification.md", VERIFICATION.replace(heading + "\n", ""))
            # When it is written
            code, out = self.post_write("docs/verification.md")
            # Then it is stopped, naming the heading
            self.assertEqual(code, 2, heading)
            self.assertIn(f"`{heading}` is missing", out)

    def test_must_be_criterion_named_in_no_scene_or_check_is_stopped(self):
        # Given a verification document that names M1 nowhere
        self.r.write("docs/verification.md", VERIFICATION.replace(", and M1 holds", ""))
        # When it is written
        code, out = self.post_write("docs/verification.md")
        # Then it is stopped, naming M1
        self.assertEqual(code, 2)
        self.assertIn("must-be criterion M1", out)

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

    def test_feedback_stop_with_no_feedback_item_is_stopped(self):
        # Given the user typed /rn:gm, then a feedback stop commit with no feedback item in open/
        self.r.hook("userpromptexpansion", command_name="rn:gm")
        self.r.write("a.txt", "a\n")
        self.r.commit(FEEDBACK)
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it is stopped, saying the feedback item is missing
        self.assertEqual(code, 2)
        self.assertIn("no feedback item", out)

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
        self.r.hook("userpromptexpansion", command_name="rn:ty")
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
        self.r.hook("userpromptexpansion", command_name="rn:dn")
        self.r.write("a.txt", "a\n")
        self.r.commit(PAUSE)
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)

    def test_pause_after_another_command_is_stopped(self):
        # Given the user typed /rn:up, not /rn:dn, then a pause commit
        self.r.hook("userpromptexpansion", command_name="rn:up")
        self.r.write("a.txt", "a\n")
        self.r.commit(PAUSE)
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it is stopped, naming /rn:dn
        self.assertEqual(code, 2)
        self.assertIn("/rn:dn", out)

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
        self.r.hook("userpromptexpansion", command_name="rn:ty")
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)

    def test_feedback_without_gm_is_stopped(self):
        # Given a feedback stop commit with its feedback item, and no /rn:gm typed
        self.r.write(f"{SDIR}/open/01-feedback-plan.md", "Name the screen first.\n")
        self.r.commit(FEEDBACK)
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it is stopped, naming /rn:gm
        self.assertEqual(code, 2)
        self.assertIn("/rn:gm", out)

    def test_feedback_after_gm_passes(self):
        # Given the user typed /rn:gm, then a feedback stop commit with its feedback item
        self.r.hook("userpromptexpansion", command_name="rn:gm")
        self.r.write(f"{SDIR}/open/01-feedback-plan.md", "Name the screen first.\n")
        self.r.commit(FEEDBACK)
        # When the commit is checked
        code, out = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0, out)

    # Checks 4 to 7 run on commits only.
    def test_command_other_than_a_commit_is_not_checked_after_it_runs(self):
        # Given a commit with no decision line
        self.r.write("a.txt", "a\n")
        self.r.commit("rn: a")
        # When a command that makes no commit has run
        code, _ = self.r.hook("posttooluse", tool_name="Bash", tool_input={"command": "ls"})
        # Then it passes
        self.assertEqual(code, 0)

    # No session: nothing is checked.
    def test_committing_with_no_session_passes(self):
        # Given no session on the branch, removed by a commit with no decision line
        sh(self.r.dir, "git", "rm", "-rq", ".rn")
        self.r.commit("drop")
        # When the commit is checked
        code, _ = self.r.after_commit()
        # Then it passes
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()

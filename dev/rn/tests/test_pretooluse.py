"""rn's PreToolUse hook: checks 9 to 12, the conductor's commit and push kept apart,
and checks 1 to 3 before the first user is called."""
import os
import unittest

from harness import SDIR, STEERING, Session, sh


class PreToolUse(Session):
    # Checks 4–7 run between commit and push.
    def test_conductor_committing_and_pushing_in_one_command_is_stopped(self):
        for cmd in ("git commit -m x && git push", "git commit -m x; git push -u origin session",
                    "git add -A\ngit commit -m x\ngit push"):
            # Given the conductor about to commit and push in one command
            # When the command is checked
            code, out = self.r.hook("pretooluse", tool_name="Bash", tool_input={"command": cmd})
            # Then it is stopped, asking for separate commands
            self.assertEqual(code, 2, cmd)
            self.assertIn("separate commands", out)

    def test_conductor_committing_or_pushing_alone_passes(self):
        for cmd in ("git commit -m x", "git push", "git add -A && git commit -F - <<'EOF'\n"
                    "rn: x\n\npush it later with git push\n\n● a ── b → c\nEOF"):
            # Given the conductor about to commit or push alone, `git push` at most in the message
            # When the command is checked
            code, _ = self.r.hook("pretooluse", tool_name="Bash", tool_input={"command": cmd})
            # Then it passes
            self.assertEqual(code, 0, cmd)

    # Check 12
    def test_conductor_starting_an_agent_in_the_background_is_stopped(self):
        # Given the conductor about to start the generator in the background
        inp = {"subagent_type": "rn:generator", "prompt": "x", "run_in_background": True}
        # When the start is checked
        code, out = self.r.hook("pretooluse", tool_name="Agent", tool_input=inp)
        # Then it is stopped, asking for the foreground
        self.assertEqual(code, 2)
        self.assertIn("foreground", out)

    def test_conductor_starting_an_agent_in_the_foreground_passes(self):
        # Given the conductor about to start the generator in the foreground
        inp = {"subagent_type": "rn:generator", "prompt": "x", "run_in_background": False}
        # When the start is checked
        code, _ = self.r.hook("pretooluse", tool_name="Agent", tool_input=inp)
        # Then it passes
        self.assertEqual(code, 0)

    def test_conductor_continuing_an_agent_by_message_is_stopped(self):
        # Given the conductor about to continue an agent by message
        # When the message is checked
        code, out = self.r.hook("pretooluse", tool_name="SendMessage",
                                tool_input={"to": "a1", "message": "carry on"})
        # Then it is stopped, asking for the foreground
        self.assertEqual(code, 2)
        self.assertIn("foreground", out)

    # Check 9
    def test_subagent_committing_is_stopped(self):
        for agent in ("rn:generator", "rn:first-user", "general-purpose"):
            # Given a subagent
            # When it is about to commit
            code, _ = self.r.hook("pretooluse", agent_type=agent, tool_name="Bash",
                                  tool_input={"command": "git commit -m x"})
            # Then it is stopped
            self.assertEqual(code, 2, agent)

    def test_subagent_committing_behind_a_prefix_an_option_or_unusual_quoting_is_stopped(self):
        for cmd in ("GIT_EDITOR=true git commit -m x", "env git commit -m x",
                    "git -c user.name=x commit -m x", "echo $'it\\'s' && git commit -m x"):
            # Given a subagent
            # When it is about to commit by a command that does more than name git
            code, _ = self.r.hook("pretooluse", agent_type="rn:generator", tool_name="Bash",
                                  tool_input={"command": cmd})
            # Then it is stopped
            self.assertEqual(code, 2, cmd)

    def test_conductor_committing_passes(self):
        # Given the conductor
        # When it is about to commit
        code, _ = self.r.hook("pretooluse", tool_name="Bash", tool_input={"command": "git commit -m x"})
        # Then it passes
        self.assertEqual(code, 0)

    # Checks 9 and 11
    def test_agent_git_outside_the_sessions_repository_passes(self):
        # Given a clone of the session's repository for an agent to try the work in
        clone = os.path.join(self.r.tmp.name, "try")
        sh(self.r.tmp.name, "git", "clone", "-q", self.r.dir, clone)
        for agent in ("rn:generator", "rn:first-user"):
            for cmd in (f"cd {clone} && git commit -qam try", f"(cd {clone} && git commit -qam try)",
                        f"git -C {clone} log -3", "grep -rn 'git push' docs",
                        "rg 'git log' README.md"):
                # When an agent runs git in the clone, or only names git in text it searches for
                code, _ = self.r.hook("pretooluse", agent_type=agent, agent_id="f3", tool_name="Bash",
                                      tool_input={"command": cmd})
                # Then it passes
                self.assertEqual(code, 0, (agent, cmd))

    def test_agent_git_on_the_sessions_repository_is_stopped(self):
        # Given a clone of the session's repository for an agent to try the work in
        clone = os.path.join(self.r.tmp.name, "try")
        sh(self.r.tmp.name, "git", "clone", "-q", self.r.dir, clone)
        for agent in ("rn:generator", "rn:first-user"):
            for cmd in (f"cd {clone} && git log; cd {self.r.dir} && git commit -m x",
                        f"(cd {clone} && git log) && git commit -m x",
                        f"git -C {self.r.dir} commit -m x"):
                # When an agent commits on the session's repository
                code, _ = self.r.hook("pretooluse", agent_type=agent, agent_id="f3", tool_name="Bash",
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


    # Checks 1 to 3 before the first user is called
    def test_calling_the_first_user_while_the_record_is_out_of_form_is_stopped(self):
        # Given a task heading without its box and name
        self.r.write(f"{SDIR}/steering.md", STEERING.replace("### [ ] #2:", "### #2"))
        # When the conductor is about to call the first user
        code, out = self.r.hook("pretooluse", tool_name="Agent",
                                tool_input={"subagent_type": "rn:first-user", "prompt": "x"})
        # Then it is stopped, naming the task heading
        self.assertEqual(code, 2)
        self.assertIn("task heading", out)

    def test_calling_the_first_user_with_the_record_in_form_passes(self):
        # Given the steering.md the session started with
        # When the conductor is about to call the first user
        code, _ = self.r.hook("pretooluse", tool_name="Agent",
                              tool_input={"subagent_type": "rn:first-user", "prompt": "x"})
        # Then it passes
        self.assertEqual(code, 0)

    # No session: nothing is checked.
    def test_tool_call_outside_any_git_repository_passes(self):
        # Given a directory that is in no git repository
        # When the conductor is about to continue an agent by message there
        code, _ = self.r.hook("pretooluse", cwd=self.r.tmp.name, tool_name="SendMessage",
                              tool_input={"to": "a1", "message": "carry on"})
        # Then it passes
        self.assertEqual(code, 0)

if __name__ == "__main__":
    unittest.main()

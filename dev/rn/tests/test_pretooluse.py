"""rn's PreToolUse hook: checks 9 and 12, and the conductor's commit and push kept apart."""

import os
import unittest

from harness import Session, sh


class PreToolUse(Session):
    # Checks 4–7 run between commit and push.
    def test_conductor_committing_and_pushing_in_one_command_is_stopped(self):
        for cmd in (
            "git commit -m x && git push",
            "git commit -m x; git push -u origin session",
            "git add -A\ngit commit -m x\ngit push",
        ):
            # Given the conductor about to commit and push in one command
            # When the command is checked
            code, out = self.r.hook("pretooluse", tool_name="Bash", tool_input={"command": cmd})
            # Then it is stopped, saying when and why to keep them apart
            self.assertEqual(code, 2, cmd)
            self.assertIn("separate commands", out)
            self.assertIn("before it is pushed", out)

    def test_conductor_committing_or_pushing_alone_passes(self):
        for cmd in (
            "git commit -m x",
            "git push",
            (
                "git add -A && git commit -F - <<'EOF'\n"
                "rn: x\n\npush it later with git push\n\n● a ── b → c\nEOF"
            ),
        ):
            # Given the conductor about to commit or push alone, `git push` at most in the message
            # When the command is checked
            code, _ = self.r.hook("pretooluse", tool_name="Bash", tool_input={"command": cmd})
            # Then it passes
            self.assertEqual(code, 0, cmd)

    # Check 12
    def test_conductor_starting_an_agent_in_the_background_is_stopped(self):
        # Given the conductor about to start an agent in the background
        inp = {"subagent_type": "general-purpose", "prompt": "x", "run_in_background": True}
        # When the start is checked
        code, out = self.r.hook("pretooluse", tool_name="Agent", tool_input=inp)
        # Then it is stopped, asking for the foreground and saying why
        self.assertEqual(code, 2)
        self.assertIn("foreground", out)
        self.assertIn("turn that has already ended", out)

    def test_conductor_starting_an_agent_in_the_foreground_passes(self):
        # Given the conductor about to start an agent in the foreground, as turn's orchestrator does
        inp = {"subagent_type": "turn:generator", "prompt": "x", "run_in_background": False}
        # When the start is checked
        code, _ = self.r.hook("pretooluse", tool_name="Agent", tool_input=inp)
        # Then it passes
        self.assertEqual(code, 0)

    def test_conductor_continuing_an_agent_by_message_is_stopped(self):
        # Given the conductor about to continue an agent by message
        # When the message is checked
        code, out = self.r.hook(
            "pretooluse", tool_name="SendMessage", tool_input={"to": "a1", "message": "carry on"}
        )
        # Then it is stopped, asking for the foreground
        self.assertEqual(code, 2)
        self.assertIn("foreground", out)

    # Check 9
    def test_subagent_committing_is_stopped(self):
        for agent in ("turn:generator", "turn:first-user", "general-purpose"):
            # Given a subagent
            # When it is about to commit
            code, out = self.r.hook(
                "pretooluse",
                agent_type=agent,
                tool_name="Bash",
                tool_input={"command": "git commit -m x"},
            )
            # Then it is stopped, saying why only the conductor commits
            self.assertEqual(code, 2, agent)
            self.assertIn("records a decision", out)

    def test_subagent_committing_behind_a_prefix_an_option_or_unusual_quoting_is_stopped(self):
        for cmd in (
            "GIT_EDITOR=true git commit -m x",
            "env git commit -m x",
            "git -c user.name=x commit -m x",
            "echo $'it\\'s' && git commit -m x",
        ):
            # Given a subagent
            # When it is about to commit by a command that does more than name git
            code, _ = self.r.hook(
                "pretooluse",
                agent_type="turn:generator",
                tool_name="Bash",
                tool_input={"command": cmd},
            )
            # Then it is stopped
            self.assertEqual(code, 2, cmd)

    def test_conductor_committing_passes(self):
        # Given the conductor
        # When it is about to commit
        code, _ = self.r.hook(
            "pretooluse", tool_name="Bash", tool_input={"command": "git commit -m x"}
        )
        # Then it passes
        self.assertEqual(code, 0)

    def test_agent_git_outside_the_sessions_repository_passes(self):
        # Given a clone of the session's repository for an agent to try the work in
        clone = os.path.join(self.r.tmp.name, "try")
        sh(self.r.tmp.name, "git", "clone", "-q", self.r.dir, clone)
        for agent in ("turn:generator", "turn:first-user"):
            for cmd in (
                f"cd {clone} && git commit -qam try",
                f"(cd {clone} && git commit -qam try)",
                f"git -C {clone} log -3",
                "grep -rn 'git push' docs",
                "rg 'git log' README.md",
            ):
                # When an agent runs git in the clone, or only names git in text it searches for
                code, _ = self.r.hook(
                    "pretooluse",
                    agent_type=agent,
                    agent_id="f3",
                    tool_name="Bash",
                    tool_input={"command": cmd},
                )
                # Then it passes
                self.assertEqual(code, 0, (agent, cmd))

    def test_agent_git_on_the_sessions_repository_is_stopped(self):
        # Given a clone of the session's repository for an agent to try the work in
        clone = os.path.join(self.r.tmp.name, "try")
        sh(self.r.tmp.name, "git", "clone", "-q", self.r.dir, clone)
        for agent in ("turn:generator", "turn:first-user"):
            for cmd in (
                f"cd {clone} && git log; cd {self.r.dir} && git commit -m x",
                f"(cd {clone} && git log) && git commit -m x",
                f"git -C {self.r.dir} commit -m x",
            ):
                # When an agent commits on the session's repository
                code, _ = self.r.hook(
                    "pretooluse",
                    agent_type=agent,
                    agent_id="f3",
                    tool_name="Bash",
                    tool_input={"command": cmd},
                )
                # Then it is stopped
                self.assertEqual(code, 2, (agent, cmd))

    # No session: nothing is checked.
    def test_tool_call_outside_any_git_repository_passes(self):
        # Given a directory that is in no git repository
        # When the conductor is about to continue an agent by message there
        code, _ = self.r.hook(
            "pretooluse",
            cwd=self.r.tmp.name,
            tool_name="SendMessage",
            tool_input={"to": "a1", "message": "carry on"},
        )
        # Then it passes
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()

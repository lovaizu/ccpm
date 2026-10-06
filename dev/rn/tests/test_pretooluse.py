"""rn's PreToolUse hook: only the conductor commits or pushes on the session's repository."""
import os
import unittest

from harness import Session, sh


class PreToolUse(Session):
    def agent_runs(self, cmd, agent="rn:generator"):
        return self.r.hook("pretooluse", agent_type=agent, tool_name="Bash",
                           tool_input={"command": cmd})

    def test_agent_committing_or_pushing_is_stopped(self):
        for agent in ("rn:generator", "writ:first-user", "general-purpose"):
            for cmd in ("git commit -m x", "git push"):
                # Given an agent the rn conversation started
                # When it is about to commit or push
                code, out = self.agent_runs(cmd, agent)
                # Then it is stopped, naming the agent
                self.assertEqual(code, 2, (agent, cmd))
                self.assertIn(agent, out)

    def test_agent_committing_behind_a_prefix_an_option_or_unusual_quoting_is_stopped(self):
        for cmd in ("GIT_EDITOR=true git commit -m x", "env git commit -m x",
                    "git -c user.name=x commit -m x", "echo $'it\\'s' && git commit -m x"):
            # Given an agent
            # When it is about to commit by a command that does more than name git
            code, _ = self.agent_runs(cmd)
            # Then it is stopped
            self.assertEqual(code, 2, cmd)

    def test_agent_naming_git_only_in_text_passes(self):
        for cmd in ("grep -rn 'git push' docs", "cat > notes.txt <<'EOF'\ngit commit -m x\nEOF"):
            # Given an agent
            # When it runs a command that only names git in text it searches for or writes
            code, _ = self.agent_runs(cmd)
            # Then it passes
            self.assertEqual(code, 0, cmd)

    def test_conductor_committing_and_pushing_passes(self):
        # Given the conductor
        # When it is about to commit and push
        code, _ = self.r.hook("pretooluse", tool_name="Bash",
                              tool_input={"command": "git commit -m x && git push"})
        # Then it passes
        self.assertEqual(code, 0)

    def test_agent_git_outside_the_sessions_repository_passes(self):
        # Given a clone of the session's repository for an agent to try the work in
        clone = os.path.join(self.r.tmp.name, "try")
        sh(self.r.tmp.name, "git", "clone", "-q", self.r.dir, clone)
        for cmd in (f"cd {clone} && git commit -qam try", f"(cd {clone} && git commit -qam try)",
                    f"git -C {clone} commit -qam try"):
            # When an agent commits in the clone
            code, _ = self.agent_runs(cmd)
            # Then it passes
            self.assertEqual(code, 0, cmd)

    def test_agent_git_on_the_sessions_repository_after_leaving_a_clone_is_stopped(self):
        # Given a clone of the session's repository for an agent to try the work in
        clone = os.path.join(self.r.tmp.name, "try")
        sh(self.r.tmp.name, "git", "clone", "-q", self.r.dir, clone)
        for cmd in (f"cd {clone} && git log; cd {self.r.dir} && git commit -m x",
                    f"(cd {clone} && git log) && git commit -m x",
                    f"git -C {self.r.dir} commit -m x"):
            # When an agent commits on the session's repository
            code, _ = self.agent_runs(cmd)
            # Then it is stopped
            self.assertEqual(code, 2, cmd)

    def test_agent_committing_outside_any_git_repository_passes(self):
        # Given a directory that is in no git repository
        # When an agent is about to commit there
        code, _ = self.r.hook("pretooluse", cwd=self.r.tmp.name, agent_type="rn:generator",
                              tool_name="Bash", tool_input={"command": "git commit -m x"})
        # Then it passes
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()

"""rn's hooks act only in a conversation where the user typed an rn command, and on the agents it
started; another conversation in the same repository is left alone."""
import unittest

from harness import PROPOSE, Session


class Scope(Session):
    def test_hooks_in_a_conversation_that_runs_no_rn_do_nothing(self):
        # Given an unpushed commit with no decision line, in a conversation (s2) that typed no rn command
        self.r.write("a.txt", "a\n")
        self.r.commit("not rn")
        other = {"session_id": "s2"}
        # When each hook runs for that conversation
        runs = {
            "agent commit": self.r.hook("pretooluse", agent_type="general-purpose", tool_name="Bash",
                                        tool_input={"command": "git commit -m x"}, **other),
            "commit": self.r.hook("posttooluse", tool_name="Bash",
                                  tool_input={"command": "git commit -m x"}, **other),
            "turn end": self.r.hook("stop", **other),
            "summary": self.r.hook("sessionstart", source="compact", **other),
        }
        # Then none of them stops or says anything
        for name, (code, out) in runs.items():
            self.assertEqual((code, out.strip()), (0, ""), name)

    def test_each_rn_command_marks_the_conversation_as_rns(self):
        for i, name in enumerate(("rn:on", "rn:up", "rn:dn", "rn:ty", "rn:gm", "up")):
            sid = f"t{i}"
            # Given a conversation where the user typed an rn command
            self.r.hook("userpromptexpansion", command_name=name, session_id=sid)
            # When an agent it started is about to commit
            code, _ = self.r.hook("pretooluse", agent_type="rn:generator", tool_name="Bash",
                                  tool_input={"command": "git commit -m x"}, session_id=sid)
            # Then it is stopped
            self.assertEqual(code, 2, name)

    def test_another_command_does_not_mark_the_conversation(self):
        for i, name in enumerate(("other:up", "rn:other", "review")):
            sid = f"u{i}"
            # Given a conversation where the user typed only a command that is not rn's
            self.r.hook("userpromptexpansion", command_name=name, session_id=sid)
            # When the turn ends with a commit unpushed
            self.r.write(f"{sid}.txt", "x\n")
            self.r.commit(PROPOSE)
            _, out = self.r.hook("stop", session_id=sid)
            # Then nothing is said
            self.assertEqual(out.strip(), "", name)


if __name__ == "__main__":
    unittest.main()

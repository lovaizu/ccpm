"""rn's hooks act only in a conversation where the user typed an rn command; another conversation
in the same repository is left alone."""
import unittest

from harness import Session


class Scope(Session):
    def test_a_conversation_that_runs_no_rn_hears_nothing_after_a_summary(self):
        # Given a running session, and another conversation (s2) that typed no rn command
        other = {"session_id": "s2"}
        # When that conversation is summarized
        code, out = self.r.hook("sessionstart", source="compact", **other)
        # Then nothing is said to it
        self.assertEqual((code, out.strip()), (0, ""))

    def test_each_rn_command_marks_the_conversation_as_rns(self):
        for i, name in enumerate(("rn:on", "rn:up", "rn:dn", "rn:ty", "rn:gm", "up")):
            sid = f"t{i}"
            # Given a conversation where the user typed an rn command
            self.r.hook("userpromptexpansion", command_name=name, session_id=sid)
            # When it is summarized
            _, out = self.r.hook("sessionstart", source="compact", session_id=sid)
            # Then it is told to read the record again
            self.assertIn("steering.md", out, name)

    def test_another_command_does_not_mark_the_conversation(self):
        for i, name in enumerate(("other:up", "rn:other", "review")):
            sid = f"u{i}"
            # Given a conversation where the user typed only a command that is not rn's
            self.r.hook("userpromptexpansion", command_name=name, session_id=sid)
            # When it is summarized
            _, out = self.r.hook("sessionstart", source="compact", session_id=sid)
            # Then nothing is said
            self.assertEqual(out.strip(), "", name)


if __name__ == "__main__":
    unittest.main()

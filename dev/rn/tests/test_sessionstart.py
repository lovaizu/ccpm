"""rn's SessionStart hook: after a summary, the conductor reads the record again."""
import unittest

from harness import Session, sh, SDIR


class SessionStart(Session):
    # After a summary
    def test_after_compact_the_record_is_read_again(self):
        # Given a running session
        # When the conversation is summarized
        code, out = self.r.hook("sessionstart", source="compact")
        # Then the conductor is told to read steering.md and open/ again
        self.assertEqual(code, 0)
        self.assertIn(f"{SDIR}/steering.md", out)
        self.assertIn("open/", out)

    def test_after_compact_with_no_session_nothing_is_said(self):
        # Given no session on the branch
        sh(self.r.dir, "git", "rm", "-rq", ".rn")
        self.r.commit("drop")
        # When the conversation is summarized
        _, out = self.r.hook("sessionstart", source="compact")
        # Then nothing is said
        self.assertEqual(out.strip(), "")


if __name__ == "__main__":
    unittest.main()

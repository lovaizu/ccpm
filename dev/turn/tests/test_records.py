"""Each record of a run as the learner is shown it, read from what Claude Code keeps of an agent's
conversation."""

import json
import unittest

from helpers import RepoTest, records


class TestShown(RepoTest):
    def test_a_line_still_being_written_is_left_out(self):
        # Given: a record whose last line is half written, as one Claude Code is still writing
        path = self.given_record("a1", "{}")
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": {"content": "late"}})[:20])
        # When: it is shown as text
        shown = records.as_text(path)
        # Then: every whole entry is shown, the half-written line left out
        self.assertEqual(shown, "[user] {}\n[text] I open it.\n[text] I open it.\n")


if __name__ == "__main__":
    unittest.main()

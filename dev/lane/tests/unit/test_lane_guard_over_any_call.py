"""What holds for every call the specification allows, tried over many calls, as N7 of the code
best practice says."""

from __future__ import annotations

import unittest

from domain import guard
from lanetest import WRITER_LAID, bash

try:
    from hypothesis import given  # pyrefly: ignore[missing-import]
    from hypothesis import strategies as st  # pyrefly: ignore[missing-import]
except ImportError:
    raise unittest.SkipTest(
        "hypothesis isn't installed. It comes with pyproject.toml's test-quality group, on Python"
        " 3.11 or later"
    ) from None


class OverAnyCall(unittest.TestCase):
    @given(st.text().filter(lambda name: name != "Bash"))
    def test_a_call_of_any_tool_but_bash_goes_on(self, name: str) -> None:
        event = {**bash("git commit"), "tool_name": name}
        self.assertIsNone(guard.decide(event, WRITER_LAID, "changelog"))

    @given(st.text())
    def test_a_command_goes_on_only_where_its_rule_names_it_whole(self, command: str) -> None:
        went = guard.decide(bash(command), WRITER_LAID, "changelog") is None
        self.assertEqual(went, command.strip() == "git log --oneline")


if __name__ == "__main__":
    unittest.main()

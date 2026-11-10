"""The hook entry's script: the event and the rules laid read in, and the guard's decision given
back in the form Claude Code reads."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

import hook
from lanetest import WRITER_LAID, bash

NO_PLUGIN = (
    "lane: Lane can't check this call, as its hook entry doesn't end in hook.py and one plugin's"
    " name. The maker of the plugin must lay its proposal again with lay.py write."
)


class Hook(unittest.TestCase):
    def setUp(self) -> None:
        hooks = os.path.realpath(tempfile.mkdtemp(prefix="lane-hook-"))
        self.addCleanup(shutil.rmtree, hooks)
        self.laid = os.path.join(hooks, "lanes.json")
        self.folder = os.path.join(hooks, "lane")
        os.mkdir(self.folder)

    def lay(self, text: str) -> None:
        with open(self.laid, "w", encoding="utf-8") as f:
            f.write(text)

    def stopped(self, given: object, argv: tuple[str, ...] = ("hook.py", "changelog")) -> str:
        """The reason the hook gives for a stop, failing where it lets the call go."""
        out = hook.main(list(argv), json.dumps(given), self.folder)
        decision = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(decision["hookEventName"], "PreToolUse")
        self.assertEqual(decision["permissionDecision"], "deny")
        return decision["permissionDecisionReason"]

    def test_a_call_that_goes_on_gives_nothing(self) -> None:
        self.lay(json.dumps(WRITER_LAID))
        self.assertEqual(
            hook.main(["hook.py", "changelog"], json.dumps(bash("git log --oneline")), self.folder),
            "",
        )

    def test_a_stop_is_a_denial_with_the_guards_reason(self) -> None:
        self.lay(json.dumps(WRITER_LAID))
        self.assertTrue(
            self.stopped(bash("git commit")).startswith("changelog: Run only `git log --oneline`.")
        )

    def test_rules_not_laid_stop_a_role(self) -> None:
        self.assertIn("as hooks/lanes.json isn't there.", self.stopped(bash("git log --oneline")))

    def test_rules_that_arent_json_stop_a_role(self) -> None:
        self.lay("{")
        self.assertIn("as hooks/lanes.json isn't JSON.", self.stopped(bash("git log --oneline")))

    def test_rules_out_of_their_form_stop_a_role(self) -> None:
        self.lay(json.dumps({"plugin": "changelog", "subagents": {"writer": {"steps": 2}}}))
        self.assertIn(
            "as hooks/lanes.json isn't in the form lay.py write writes.",
            self.stopped(bash("git log --oneline")),
        )

    def test_an_event_that_isnt_json_stops(self) -> None:
        self.lay(json.dumps(WRITER_LAID))
        out = hook.main(["hook.py", "changelog"], "{", self.folder)
        reason = json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("handed it no JSON object", reason)

    def test_an_entry_that_names_no_plugin_stops(self) -> None:
        self.lay(json.dumps(WRITER_LAID))
        self.assertEqual(self.stopped(bash("git log --oneline"), ("hook.py",)), NO_PLUGIN)

    def test_an_entry_with_a_word_after_the_plugin_stops(self) -> None:
        self.lay(json.dumps(WRITER_LAID))
        argv = ("hook.py", "changelog", "again")
        self.assertEqual(self.stopped(bash("git log --oneline"), argv), NO_PLUGIN)


if __name__ == "__main__":
    unittest.main()

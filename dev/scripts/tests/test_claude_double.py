"""The tests of claude_double.py, the double of Claude Code that the tests of trial.py run: each of
its outputs that trial.py reads has the form that the real Claude Code 2.1.322 gave in
claude-code-2.1.322-clear.jsonl, the hook events of a /clear that a trial's records kept, and in
`claude -p --output-format json --json-schema`."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from helpers import FolderTest

DOUBLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude_double.py")
# The session's first SessionStart and that of its /clear, as a trial run of Claude Code 2.1.322
# recorded them in its hooks.jsonl.
CLEARED = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "claude-code-2.1.322-clear.jsonl"
)
# The hook adds each event it gets to events.jsonl, as trial.py's hook adds it to the records.
KEEP = 'import sys; open("events.jsonl", "a").write(sys.stdin.read() + chr(10))'
HOOK = f"{sys.executable} -c '{KEEP}'"


class ClaudeDoubleTest(FolderTest):
    def setUp(self) -> None:
        super().setUp()
        hooks = {
            e: [{"hooks": [{"type": "command", "command": HOOK}]}]
            for e in ("SessionStart", "UserPromptSubmit")
        }
        self.write_json("config/settings.json", {"hooks": hooks})
        os.makedirs("tmp")
        self.env = dict(
            os.environ,
            TRIAL_DOUBLE=os.path.join(self.base, "plan.json"),
            CLAUDE_CONFIG_DIR=os.path.join(self.base, "config"),
            TMPDIR=os.path.join(self.base, "tmp"),
        )

    def run_double(self, *argv: str) -> str:
        done = subprocess.run(
            [sys.executable, DOUBLE, *argv],
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
        )
        return done.stdout

    def test_the_stand_ins_reply_lies_in_structured_output_as_claude_p_gives_it(self):
        self.write_json("plan.json", {"stand_in": [{"done": True}], "turns": []})
        reply = json.loads(self.run_double("-p", "--json-schema", "{}", "screen"))
        self.assertEqual(reply["structured_output"], {"done": True})

    def test_a_turn_that_clears_sends_sessionstart_with_a_new_conversation_as_the_record_shows(
        self,
    ):
        self.write_json("plan.json", {"stand_in": [], "turns": [{"session": "new"}]})
        self.run_double("-p", "--resume", "old", "/clear")
        sent = [json.loads(line) for line in self.read("events.jsonl").splitlines()]
        self.assertEqual(sent[0], {"hook_event_name": "SessionStart", "session_id": "new"})
        with open(CLEARED, encoding="utf-8") as f:
            recorded = [json.loads(line)["payload"] for line in f]
        cleared = [
            p for p in recorded if p["hook_event_name"] == "SessionStart" and p["source"] == "clear"
        ]
        (real,) = cleared
        self.assertNotEqual(real["session_id"], recorded[0]["session_id"])

"""The tests of the hook scripts every plugin carries as identical copies: the CCS check before a
Return starts, and the facts written from its agent's JSONL when it stops. Each plugin's tests run
them against its own copy, with the CCS its own Return requires."""

import importlib
import io
import json
import os
import runpy
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest import mock

DEV = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = "docs/guide.md"


def suite(plugin):
    """The plugin's test classes, run against its own copy of the scripts."""
    sys.path.insert(0, os.path.join(DEV, "..", plugin, "scripts"))
    ccs, check_in, facts = (importlib.import_module(m) for m in ("ccs", "check_in", "facts"))
    (skill, (required, agent)), = ccs.returns().items()
    with open(required) as f:
        entries = json.load(f)
    ready = {}
    for r in entries:
        value = WORK if r["type"] == "work" else f"/{r['type']}"
        ready.setdefault(r["component"], []).append((r["type"], value))
    ready.setdefault("retrieved_artifacts", []).append(("read", "old.md"))
    first = entries[0]

    def run(module, hook):
        """Run the hook's script as Claude Code runs it, with the hook input on stdin."""
        with mock.patch("sys.stdin", io.StringIO(json.dumps(hook))):
            runpy.run_path(module.__file__, run_name="__main__")

    class Repo(unittest.TestCase):
        def setUp(self):
            self.dir = tempfile.TemporaryDirectory()
            self.root = os.path.realpath(self.dir.name)
            os.makedirs(os.path.join(self.root, f".{plugin}"))
            self.ccs = os.path.join(self.root, f".{plugin}", "guide.yaml")

        def tearDown(self):
            self.dir.cleanup()

        def write_ccs(self, state):
            ccs.dump(state, self.ccs)

        def check(self, args, called=skill):
            """The check's exit status and what it said."""
            err = io.StringIO()
            with redirect_stderr(err):
                try:
                    run(check_in, {"cwd": self.root, "tool_input": {"skill": called, "args": args}})
                except SystemExit as stop:
                    return stop.code, err.getvalue()
            return 0, err.getvalue()

    class CheckIn(Repo):
        def test_a_ready_ccs_lets_the_return_start(self):
            # Given
            self.write_ccs(ready)
            # When
            code, said = self.check(self.ccs)
            # Then
            self.assertEqual((code, said), (0, ""))

        def test_a_missing_entry_stops_the_call_and_says_where_it_comes_from(self):
            # Given
            lacking = {c: [e for e in es if e[0] != first["type"]] for c, es in ready.items()}
            self.write_ccs(lacking)
            # When
            code, said = self.check(self.ccs)
            # Then
            self.assertEqual(code, 2)
            self.assertIn(f"{first['component']}: {first['type']} (from {first['from']})", said)

        def test_an_open_gap_stops_the_call(self):
            # Given
            self.write_ccs({**ready, "uncertainty_signal": [("gap", "whether cli/ is included")]})
            # When
            code, said = self.check(self.ccs)
            # Then
            self.assertEqual(code, 2)
            self.assertIn("Open gaps: whether cli/ is included", said)

        def test_a_call_without_a_ccs_path_is_stopped(self):
            # Given
            self.write_ccs(ready)
            # When
            code, said = self.check(f"use {WORK}")
            # Then
            self.assertEqual(code, 2)
            self.assertIn("Hand the path of its CCS", said)

        def test_a_ccs_is_found_from_its_path_relative_to_the_repository(self):
            # Given
            self.write_ccs(ready)
            # When
            code, said = self.check(f".{plugin}/guide.yaml")
            # Then
            self.assertEqual((code, said), (0, ""))

        def test_another_skill_is_never_stopped(self):
            # Given no CCS at all
            # When
            code, said = self.check("anything", called="other:skill")
            # Then
            self.assertEqual((code, said), (0, ""))

    class Facts(Repo):
        def transcript(self, entries):
            path = os.path.join(self.root, "agent.jsonl")
            with open(path, "w") as f:
                for e in entries:
                    f.write(json.dumps(e) + "\n")
            return path

        def use(self, uid, name, args):
            return {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "id": uid, "name": name, "input": args}]}}

        def result(self, uid, content, error=False):
            return {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": uid, "content": content, "is_error": error}]}}

        def agent_run(self):
            return self.transcript([
                {"type": "user", "message": {"content": self.ccs}},
                self.use("a", "Read", {"file_path": os.path.join(self.root, "docs/architecture.md")}),
                self.result("a", "the architecture"),
                self.use("a2", "Read", {"file_path": os.path.join(self.root, "docs/architecture.md")}),
                self.result("a2", "the architecture"),
                self.use("b", "Bash", {"command": "claude -p " + "x" * 200}),
                self.result("b", "NO_COMMENT"),
                self.use("b2", "Bash", {"command": "cat docs/typing-guide.md"}),
                self.result("b2", "the guide"),
                self.use("c", "Bash", {"command": "ls /nonexistent"}),
                self.result("c", "Exit code 1\nls: /nonexistent: No such file", error=True),
                self.use("d", "Bash", {"command": "false"}),
                self.result("d", [{"type": "text", "text": "failed"}], error=True),
                self.use("e", "Bash", {"command": "sleep 999"}),
                self.use("f", "Write", {"file_path": os.path.join(self.root, "notes.md")}),
                self.result("f", "ok"),
                self.use("g", "Edit", {"file_path": "/tmp/elsewhere.md"}),
                self.result("g", "ok"),
                {"type": "attachment"},
            ])

        def test_what_the_agent_did_is_written_from_its_jsonl(self):
            # Given
            self.write_ccs(ready)
            transcript = self.agent_run()
            # When
            run(facts, {"agent_type": agent, "agent_transcript_path": transcript, "cwd": self.root})
            # Then
            state = ccs.load(self.ccs)
            self.assertEqual(state["episodic_trace"], [
                ("executed", "claude -p " + "x" * 150 + "… → exit 0"),
                ("executed", "cat docs/typing-guide.md → exit 0"),
                ("failed", "ls /nonexistent → exit 1"),
                ("failed", "false → exit 1"),
                ("failed", "sleep 999 → exit None"),
                ("wrote", os.path.join(self.root, "notes.md")),
                ("wrote_outside", "/tmp/elsewhere.md"),
            ])
            handed = [e for e in ready["retrieved_artifacts"] if e[0] != "read"]
            self.assertEqual(state["retrieved_artifacts"],
                             handed + [("read", "docs/architecture.md"), ("transcript", transcript)])
            self.assertEqual(state["relational_map"], [])

        def test_another_agent_leaves_the_ccs_untouched(self):
            # Given
            self.write_ccs(ready)
            with open(self.ccs) as f:
                before = f.read()
            transcript = self.agent_run()
            # When
            run(facts, {"agent_type": "", "agent_transcript_path": transcript, "cwd": self.root})
            # Then
            with open(self.ccs) as f:
                self.assertEqual(f.read(), before)

        def test_an_agent_handed_no_ccs_writes_nothing(self):
            # Given
            transcript = self.transcript([{"type": "user", "message": {"content": [{"type": "text", "text": "no path"}]}}])
            # When
            run(facts, {"agent_type": agent, "agent_transcript_path": transcript, "cwd": self.root})
            # Then
            self.assertFalse(os.path.exists(self.ccs))

    return CheckIn, Facts

"""The tests of the double of Claude Code, as Lane's integration tests rest on it: it sends each
event as the recorded run of Claude Code 2.1.322 shows, and reads what a hook gives as Claude Code's
hooks reference says. A plugin of the test's own logs each payload that the double sends."""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from typing import Any

from claude_code import (
    COMPACT,
    RECORDED,
    RUN,
    SEND_MESSAGE,
    SKILL,
    Conversation,
    lines,
    record_lines,
    run_python,
)


def payloads(record: str) -> dict[str, dict[str, Any]]:
    """A copy of each payload of the record in recorded/, by the name of its event."""
    return {r["event"]: copy.deepcopy(r["payload"]) for r in record_lines(record) if "payload" in r}


def recorded() -> dict[str, dict[str, Any]]:
    """Each payload of the recorded run of Claude Code 2.1.322, by the name of its event."""
    return payloads(RUN)


def skill_call() -> dict[str, dict[str, Any]]:
    """Each payload of the record of a call of a plugin's skill by the Skill tool."""
    return payloads(SKILL)


def send_message() -> dict[str, dict[str, Any]]:
    """Each payload of the record of a subagent resumed by SendMessage."""
    return payloads(SEND_MESSAGE)


def compaction() -> list[tuple[str, dict[str, Any]]]:
    """Each event that /compact sends, by its name in the record, from PreCompact to PostCompact."""
    sent = lines(COMPACT, "the person compacts the conversation", "the conversation is compacted")
    return [(r["event"], r["payload"]) for r in sent]


def lines_of(record: str) -> dict[str, dict[str, Any]]:
    """A copy of each line of the record claude-code-2.1.323-<record>.jsonl, by its event."""
    found = record_lines(f"claude-code-2.1.323-{record}.jsonl")
    return {r["event"]: copy.deepcopy(r) for r in found}


EVENTS = [
    "SessionStart",
    "PreCompact",
    "PostCompact",
    "UserPromptSubmit",
    "UserPromptExpansion",
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "SubagentStart",
    "SubagentStop",
    "Stop",
]

# The hook of the logging plugin: it adds each payload to the log, and does what the payload's
# command asks of a hook, so that a test sees how the double reads it.
LOG = """import json, os, sys
payload = json.load(sys.stdin)
with open(os.environ["LOG"], "a") as f:
    f.write(json.dumps(payload) + "\\n")
with open(os.environ["LOG"] + ".where", "a") as f:
    f.write(json.dumps([os.getcwd(), os.environ["CLAUDE_PROJECT_DIR"]]) + "\\n")
tool_input = payload.get("tool_input") or {}
command = (tool_input.get("command") or tool_input.get("new_string") or tool_input.get("message")
    or tool_input.get("prompt") or tool_input.get("args", ""))
denied = payload.get("tool_name") in os.environ.get("DENY", "").split(",")
if payload["hook_event_name"] == "PreToolUse" and ("deny me" in command or denied):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Run only `git log --oneline`."}}))
if payload["hook_event_name"] == "PreToolUse" and "exit 2" in command:
    print("stopped by exit 2", file=sys.stderr)
    sys.exit(2)
if payload["hook_event_name"] == "UserPromptSubmit" and payload["prompt"] == "context":
    print("plain output read as context")
if payload["hook_event_name"] == "SubagentStop" and payload["last_assistant_message"] == "stop me":
    print(json.dumps({"decision": "block", "reason": "Give your result first."}))
"""

# The values of each payload that the record fixes, beyond its fields' names.
FIXED = [
    "hook_event_name",
    "permission_mode",
    "effort",
    "source",
    "expansion_type",
    "command_source",
    "tool_name",
    "stop_hook_active",
    "session_crons",
    "is_interrupt",
    "trigger",
]


class ClaudeCodeDoubleTest(unittest.TestCase):
    def setUp(self):
        self.temp = os.path.realpath(tempfile.mkdtemp(prefix="lane-double-"))
        self.addCleanup(shutil.rmtree, self.temp)
        self.repo = os.path.join(self.temp, "repo")
        self.plugin = os.path.join(self.repo, "changelog")
        os.makedirs(os.path.join(self.plugin, ".claude-plugin"))
        os.makedirs(os.path.join(self.plugin, "hooks"))
        os.makedirs(os.path.join(self.plugin, "skills", "write"))
        self.write("changelog/.claude-plugin/plugin.json", json.dumps({"name": "changelog"}))
        self.write("changelog/skills/write/SKILL.md", "---\nname: write\n---\n")
        self.write("changelog/hooks/log.py", LOG)
        entry = {
            "type": "command",
            "command": "python3",
            "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/log.py"],
        }
        hooks = {e: [{"hooks": [entry]}] for e in EVENTS}
        self.write("changelog/hooks/hooks.json", json.dumps({"hooks": hooks}))
        self.log = os.path.join(self.temp, "log.jsonl")
        env = dict(os.environ, LOG=self.log, TMPDIR=self.temp)
        self.conversation = Conversation(self.repo, [self.plugin], env, self.temp)

    def write(self, path, text):
        with open(os.path.join(self.repo, path), "w", encoding="utf-8") as f:
            f.write(text)

    def sent(self):
        with open(self.log, encoding="utf-8") as f:
            return [json.loads(line) for line in f]

    def assert_sent_as_recorded(self, names, records=None):
        records = records or recorded()
        sent = self.sent()
        self.assertEqual(len(sent), len(names), "the double sends one event for each recorded")
        for name, payload in zip(names, sent):
            with self.subTest(event=name):
                record = records[name]
                self.assertEqual(sorted(payload), sorted(record), f"{name}: fields as recorded")
                for key in FIXED:
                    self.assertEqual(
                        payload.get(key), record.get(key), f"{name}: {key} as recorded"
                    )
                if "tool_response" in record:
                    self.assertEqual(
                        sorted(payload["tool_response"]), sorted(record["tool_response"])
                    )
                if "tool_input" in record:
                    self.assertEqual(sorted(payload["tool_input"]), sorted(record["tool_input"]))
                folder = record["cwd"].replace("<repo>", self.repo)
                self.assertEqual(payload["cwd"], folder, f"{name}: the conversation's folder")
                self.assertEqual(payload["session_id"], self.conversation.session_id)
                for agent in self.conversation.agents:
                    if payload.get("agent_type") == agent.type:
                        self.assertEqual(payload["agent_id"], agent.id, f"{name}: the agent's ID")

    def test_typing_a_command_and_running_bash_send_the_events_recorded(self):
        self.conversation.type("/changelog:write")
        self.conversation.bash("true")
        self.conversation.type("yes")
        self.assert_sent_as_recorded(
            [
                "session started",
                "a person types /lane:up changelog",
                "the typed /lane:up expands",
                "the main conversation runs lay.py print",
                "lay.py print ran",
                "a person replies yes",
            ]
        )

    def test_typing_a_command_the_model_cannot_call_after_a_stop_sends_the_events_recorded(self):
        os.makedirs(os.path.join(self.plugin, "skills", "approve"))
        self.write(
            "changelog/skills/approve/SKILL.md",
            "---\nname: approve\ndisable-model-invocation: true\n---\n",
        )
        self.conversation.stop("written")
        self.conversation.type("/changelog:approve")
        self.assert_sent_as_recorded(
            [
                "session started",
                "the main conversation stops",
                "a person types /changelog:approve after the main conversation stops",
                "the typed /changelog:approve expands",
            ]
        )
        self.assertEqual(self.sent()[-1]["command_name"], "changelog:approve")

    def test_a_hooks_file_written_in_the_conversation_holds_only_after_reload_plugins(self):
        self.write("changelog/hooks/hooks.json", json.dumps({"hooks": {}}))
        self.conversation.type("before the reload")
        self.assert_sent_as_recorded(["session started", "a person types /lane:up changelog"])
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write")
        assert agent is not None  # No hook of the test's plugin stops the start.
        agent.bash("true")
        self.assertIn(agent.id, {p.get("agent_id") for p in self.sent()}, "the old hooks hold")
        before = len(self.sent())
        self.conversation.type("/reload-plugins")
        self.conversation.type("after the reload")
        self.assertEqual(len(self.sent()), before, "no hook runs on or after /reload-plugins")

    def test_compact_sends_the_events_recorded_in_the_same_conversation(self):
        self.conversation.compact()
        self.assert_sent_as_recorded(
            [
                "session started",
                "the person compacts the conversation",
                "the compaction's summary ends",
                "the compacted conversation starts",
                "the conversation is compacted",
            ],
            {**recorded(), **dict(compaction())},
        )
        self.assertEqual(self.sent()[2]["agent_type"], "", "the summary's subagent has no type")

    def test_a_command_typed_after_compact_goes_on_in_the_same_conversation_as_recorded(self):
        path = os.path.join(RECORDED, "claude-code-2.1.322-compact.jsonl")
        with open(path, encoding="utf-8") as f:
            kept = {json.loads(line)["payload"]["session_id"] for line in f}
        self.assertEqual(len(kept), 1, "the record keeps one session_id through /compact")
        self.conversation.type("/changelog:write")
        self.conversation.compact()
        self.conversation.type("/changelog:write")
        self.assertEqual(
            {payload["session_id"] for payload in self.sent()},
            {self.conversation.session_id},
            "the double keeps the conversation's session_id through /compact",
        )

    def test_a_subagent_started_and_ended_sends_the_events_recorded(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        self.conversation.stop("started writer")
        agent.bash("git --version")
        agent.end("written")
        self.conversation.stop("done")
        self.assert_sent_as_recorded(
            [
                "session started",
                "the main conversation starts writer in the background",
                "writer starts",
                "writer runs in the background",
                "the main conversation stops while writer runs",
                "writer runs git log",
                "git log ran",
                "writer ends",
                "writer's end reaches the main conversation",
                "the main conversation stops",
            ]
        )

    def test_a_subagents_start_that_a_hook_denies_carries_the_subagent_and_starts_none(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        answer, started = agent.start("changelog:reviewer", "deny me", "Review entries")
        self.assertTrue(answer.blocked, "a PreToolUse deny stops the subagent's start")
        self.assertEqual(answer.said, "Run only `git log --oneline`.")
        self.assertIsNone(started, "no subagent starts")
        call = self.sent()[-1]
        recorded_start = recorded()["the main conversation starts writer in the background"]
        self.assertEqual(
            sorted(call),
            sorted([*recorded_start, "agent_id", "agent_type"]),
            "the main conversation's start, with the subagent's fields as each of its calls has",
        )
        self.assertEqual((call["agent_id"], call["agent_type"]), (agent.id, agent.type))
        self.assertEqual(call["tool_input"]["subagent_type"], "changelog:reviewer")

    def test_a_subagent_that_ends_reaches_the_main_conversation_with_its_last_message(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        agent.end("written")
        prompt = self.sent()[-1]["prompt"]
        self.assertTrue(prompt.startswith("<task-notification>"), prompt)
        self.assertIn(f"<task-id>{agent.id}</task-id>", prompt)
        self.assertIn("<result>written</result>", prompt)

    def test_a_command_that_fails_sends_the_failure_recorded(self):
        answer = self.conversation.bash("python3 missing.py")
        self.assertEqual(answer.exit_code, 2)
        self.assert_sent_as_recorded(
            ["session started", "the main conversation runs lay.py print", "a command fails"]
        )
        self.assertTrue(
            self.sent()[-1]["error"].startswith("Exit code 2\npython3: can't open file")
        )

    def test_a_bash_command_of_the_main_conversation_gets_its_session_id_as_recorded(self):
        answer = self.conversation.bash('echo "$CLAUDE_CODE_SESSION_ID"')
        self.assertEqual(answer.output, f"{self.conversation.session_id}\n")

    def test_a_bash_command_of_a_subagent_gets_the_conversations_session_id_as_recorded(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        answer = agent.bash('echo "$CLAUDE_CODE_SESSION_ID"')
        self.assertEqual(answer.output, f"{self.conversation.session_id}\n")
        self.assertEqual(self.sent()[-1]["session_id"], self.conversation.session_id)

    def test_a_denial_stops_the_call_with_its_reason(self):
        answer = self.conversation.bash("echo deny me")
        self.assertTrue(answer.blocked, "a PreToolUse deny stops the call")
        self.assertEqual(answer.said, "Run only `git log --oneline`.")
        self.assertIsNone(answer.exit_code, "the command never ran")

    def test_exit_2_stops_the_call_with_its_standard_error(self):
        answer = self.conversation.bash("echo exit 2")
        self.assertTrue(answer.blocked, "exit 2 stops a PreToolUse")
        self.assertEqual(answer.said, "stopped by exit 2")

    def test_plain_output_on_a_prompt_is_what_the_main_conversation_reads(self):
        answer = self.conversation.type("context")
        self.assertFalse(answer.blocked)
        self.assertEqual(answer.said, "plain output read as context")

    def test_a_subagent_that_writes_a_file_sends_the_events_recorded(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        path = os.path.join(self.repo, "CHANGELOG.md")
        answer = agent.write(path, "## 0.1.0\n")
        self.assertFalse(answer.blocked)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "## 0.1.0\n", "the Write let through writes the file")
        self.assert_sent_as_recorded(
            [
                "session started",
                "the main conversation starts writer in the background",
                "writer starts",
                "writer runs in the background",
                "writer writes CHANGELOG.md",
                "CHANGELOG.md written",
            ]
        )
        self.assertEqual(self.sent()[-2]["tool_input"]["file_path"], path)

    def test_a_subagent_that_reads_a_file_sends_the_pre_tool_use_that_the_hooks_reference_gives(
        self,
    ):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        path = os.path.join(self.repo, "CHANGELOG.md")
        answer = agent.read(path)
        self.assertFalse(answer.blocked)
        self.assert_sent_as_recorded(
            [
                "session started",
                "the main conversation starts writer in the background",
                "writer starts",
                "writer runs in the background",
                "writer writes CHANGELOG.md",
            ],
            dict(recorded(), **{"writer writes CHANGELOG.md": self.read_record()}),
        )
        self.assertEqual(self.sent()[-1]["tool_input"], {"file_path": path})

    @staticmethod
    def read_record():
        """The recorded PreToolUse of a subagent's call, with Read's name and the field of its
        input that the hooks reference gives."""
        return dict(
            recorded()["writer writes CHANGELOG.md"], tool_name="Read", tool_input={"file_path": 0}
        )

    def test_a_write_of_the_main_conversation_sends_its_own_calls_events_with_writes_fields(self):
        path = os.path.join(self.temp, "lesson.json")
        answer = self.conversation.write(None, path, "{}")
        self.assertFalse(answer.blocked)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "{}", "the Write let through writes the file")
        before, after = "the main conversation runs lay.py print", "lay.py print ran"
        self.assert_sent_as_recorded(
            ["session started", before, after],
            dict(
                recorded(), **{before: self.write_record(before), after: self.write_record(after)}
            ),
        )
        self.assertEqual(self.sent()[-1]["tool_input"], {"file_path": path, "content": "{}"})

    @staticmethod
    def write_record(name):
        """The recorded event of a call of the main conversation, with Write's name, and the fields
        of the input and of the response that the record of a subagent's Write holds."""
        records = recorded()
        write = {**records["writer writes CHANGELOG.md"], **records["CHANGELOG.md written"]}
        fields = {
            key: write[key] for key in ("tool_input", "tool_response") if key in records[name]
        }
        return dict(records[name], tool_name="Write", **fields)

    def test_an_edit_of_the_main_conversation_sends_the_tool_input_that_the_hooks_reference_gives(
        self,
    ):
        path = os.path.join(self.plugin, "skills", "write", "SKILL.md")
        answer = self.conversation.edit(path, "name: write", "name: write\ndescription: Writes.")
        self.assertFalse(answer.blocked)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "---\nname: write\ndescription: Writes.\n---\n")
        self.assert_sent_as_recorded(
            ["session started", "the main conversation runs lay.py print"],
            dict(recorded(), **{"the main conversation runs lay.py print": self.edit_record()}),
        )
        self.assertEqual(
            self.sent()[-1]["tool_input"],
            {
                "file_path": path,
                "old_string": "name: write",
                "new_string": "name: write\ndescription: Writes.",
                "replace_all": False,
            },
        )

    def test_a_write_that_a_hook_denies_writes_no_file(self):
        # Given: the logging plugin denies each call of Write.
        env = dict(self.conversation.env, DENY="Write")
        conversation = Conversation(self.repo, [self.plugin], env, self.temp)
        path = os.path.join(self.temp, "lesson.json")
        # When: the main conversation writes a file.
        answer = conversation.write(None, path, "{}")
        # Then: the call is stopped, and no file is there.
        self.assertTrue(answer.blocked, "a PreToolUse deny stops the Write")
        self.assertFalse(os.path.exists(path), "the denied Write writes nothing")

    def test_an_edit_that_a_hook_denies_leaves_the_file(self):
        path = os.path.join(self.plugin, "skills", "write", "SKILL.md")
        answer = self.conversation.edit(path, "name: write", "deny me")
        self.assertTrue(answer.blocked, "a PreToolUse deny stops the Edit")
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "---\nname: write\n---\n", "the denied Edit changes nothing")

    @staticmethod
    def edit_record():
        """The recorded PreToolUse of a call of the main conversation, with Edit's name and the
        fields of its input, as the hooks reference gives them."""
        fields = ["file_path", "old_string", "new_string", "replace_all"]
        return dict(
            recorded()["the main conversation runs lay.py print"],
            tool_name="Edit",
            tool_input=dict.fromkeys(fields),
        )

    def test_a_skill_call_of_the_main_conversation_sends_the_events_recorded_with_its_input(self):
        answer = self.conversation.skill("changelog:write", "the entries")
        self.assertFalse(answer.blocked)
        self.assert_sent_as_recorded(
            [
                "session started",
                "the main conversation calls lane:up by the Skill tool",
                "the Skill call of lane:up ran",
            ],
            {**recorded(), **skill_call()},
        )
        called, ran = self.sent()[1:]
        self.assertEqual(called["tool_input"], {"skill": "changelog:write", "args": "the entries"})
        self.assertEqual(ran["tool_response"], {"success": True, "commandName": "changelog:write"})
        self.assertEqual(ran["tool_use_id"], called["tool_use_id"], "one call's two events")

    def test_a_skill_call_that_a_hook_denies_is_stopped_with_its_reason(self):
        answer = self.conversation.skill("changelog:write", "deny me")
        self.assertTrue(answer.blocked, "a PreToolUse deny stops the Skill call")
        self.assertEqual(answer.said, "Run only `git log --oneline`.")
        self.assertEqual(len(self.sent()), 2, "a Skill call stopped sends no PostToolUse")

    def test_a_subagent_whose_end_was_stopped_ends_again_with_stop_hook_active(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        stopped, notified = agent.end("stop me")
        self.assertTrue(stopped.blocked, "a SubagentStop block stops the end")
        self.assertEqual(stopped.said, "Give your result first.")
        self.assertIsNone(notified, "a stopped end doesn't reach the main conversation")
        agent.end("written")
        self.assert_sent_as_recorded(
            [
                "session started",
                "the main conversation starts writer in the background",
                "writer starts",
                "writer runs in the background",
                "writer ends",
                "writer ends again after its end was stopped",
                "writer's end reaches the main conversation",
            ]
        )

    def test_a_subagent_resumed_by_send_message_sends_the_events_recorded(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        agent.end("one")
        resumed = self.conversation.resume(agent, "Reply with the word two.", "Ask for two")
        self.conversation.stop("waiting")
        _, notified = agent.end("two")
        self.assertFalse(resumed.blocked)
        self.assertIsNotNone(notified, "the resumed agent's end reaches the main conversation")
        self.assert_sent_as_recorded(
            [
                "session started",
                "the main conversation starts writer in the background",
                "writer starts",
                "writer runs in the background",
                "writer ends",
                "writer's end reaches the main conversation",
                "the main conversation resumes helper by SendMessage",
                "the SendMessage call ran",
                "helper starts again on the message",
                "the main conversation stops while helper runs again",
                "helper ends again",
                "helper's second end reaches the main conversation",
            ],
            {**recorded(), **send_message()},
        )
        sent = self.sent()
        called, ran, started = sent[6:9]
        self.assertEqual(
            called["tool_input"],
            {
                "to": agent.id,
                "summary": "Ask for two",
                "message": "Reply with the word two.",
                "type": "message",
                "recipient": agent.id,
                "recipient_kind": "agent",
                "content": "Reply with the word two.",
            },
        )
        self.assertEqual(ran["tool_use_id"], called["tool_use_id"], "one call's two events")
        self.assertEqual(ran["tool_response"]["resumedAgentId"], agent.id)
        self.assertEqual(started["agent_id"], agent.id, "the same agent starts again")
        self.assertEqual(sent[9]["background_tasks"][0]["id"], agent.id, "it runs again")
        self.assertIn(f"<tool-use-id>{called['tool_use_id']}</tool-use-id>", sent[-1]["prompt"])
        self.assertIn("<result>two</result>", sent[-1]["prompt"])

    def test_a_send_message_that_a_hook_denies_resumes_no_subagent(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        agent.end("one")
        answer = self.conversation.resume(agent, "exit 2")
        self.assertTrue(answer.blocked, "exit 2 stops the SendMessage call")
        self.assertFalse(agent.running, "the agent stays ended")
        self.assertEqual(self.sent()[-1]["tool_name"], "SendMessage", "no event after the stop")

    # A command of a skill's SKILL.md that runs as the skill loads, which prints what the record's
    # command printed: its plugin's folder filled in its text, the same name in its environment, its
    # folder, and the session's ID.
    LOADED = (
        '!`echo "text-root=${CLAUDE_PLUGIN_ROOT}"; echo "env-root=$(printenv CLAUDE_PLUGIN_ROOT)";'
        ' echo "pwd=$(pwd)"; echo "project=${CLAUDE_PROJECT_DIR:-unset}";'
        ' echo "session=$CLAUDE_CODE_SESSION_ID"`'
    )

    def probe(self, name, front=""):
        os.makedirs(os.path.join(self.plugin, "skills", name))
        self.write(
            f"changelog/skills/{name}/SKILL.md",
            f"---\nname: {name}\n{front}---\n\nWhat it printed:\n\n{self.LOADED}\n\nReply.\n",
        )

    def assert_printed_as_recorded(self, output):
        """The skill's text holds what the command printed, as each of the record's commands
        printed it, with this conversation's folders and session."""
        record = lines_of("skill-command")
        for name in (
            "the command of rec:probe's SKILL.md runs as the typed command expands",
            "the command of rec:probe's SKILL.md runs as claude -p expands it",
            "the command of rec:probecall's SKILL.md runs as the Skill call loads it",
        ):
            printed = record[name]["printed"].split("\n")
            self.assertEqual(printed[:3], ["text-root=<plugin>", "env-root=", "pwd=<repo>"])
            names = {line.partition("=")[0] for line in printed[3:]}
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", names, f"{name}: not in its environment")
            self.assertNotIn("CLAUDE_PROJECT_DIR", names, f"{name}: not in its environment")
        self.assertEqual(
            output,
            "What it printed:\n\n"
            f"text-root={self.plugin}\nenv-root=\npwd={self.repo}\nproject=unset\n"
            f"session={self.conversation.session_id}\n\nReply.\n",
        )

    def test_a_typed_command_runs_its_skills_command_as_it_loads_with_no_event_as_recorded(self):
        self.probe("probe", "disable-model-invocation: true\n")
        answer = self.conversation.type("/changelog:probe")
        self.assertFalse(answer.blocked)
        self.assert_printed_as_recorded(answer.output)
        records = {e: r["payload"] for e, r in lines_of("skill-command").items() if "payload" in r}
        self.assert_sent_as_recorded(
            ["session started", "claude -p submits /rec:probe", "claude -p expands /rec:probe"],
            {**recorded(), **records},
        )

    def test_a_typed_command_whose_skills_command_fails_shows_the_failure_and_calls_no_model(self):
        fails = lines_of("skill-command-fails")
        failed = fails["the command of rec:fails's SKILL.md fails as claude -p expands it"]
        os.makedirs(os.path.join(self.plugin, "skills", "fails"))
        self.write(
            "changelog/skills/fails/SKILL.md",
            "---\nname: fails\ndisable-model-invocation: true\n---\n\nBefore the command.\n\n"
            f"{failed['command']}\n\nAfter the command.\n",
        )

        answer = self.conversation.type("/changelog:fails")

        self.assertFalse(answer.blocked)
        self.assertEqual(answer.shown, failed["said"], "Claude Code's words, as recorded")
        self.assertEqual(answer.output, "", "the skill's text reaches no model")
        self.assertFalse(failed["said_by_model"], "the record shows no model called")
        self.assertNotIn("claude -p stops after /rec:fails", fails, "the record shows no Stop")
        records = {e: r["payload"] for e, r in fails.items() if "payload" in r}
        self.assert_sent_as_recorded(
            ["session started", "claude -p submits /rec:fails", "claude -p expands /rec:fails"],
            {**recorded(), **records},
        )

    def test_a_skill_call_runs_its_skills_command_as_it_loads_as_recorded(self):
        self.probe("probecall")
        answer = self.conversation.skill("changelog:probecall", "the entries")
        self.assertFalse(answer.blocked)
        self.assert_printed_as_recorded(answer.output)
        self.assert_sent_as_recorded(
            [
                "session started",
                "the main conversation calls lane:up by the Skill tool",
                "the Skill call of lane:up ran",
            ],
            {**recorded(), **skill_call()},
        )
        # The record of 2.1.323 holds a call with no arguments, whose input holds `skill` alone.
        record = lines_of("skill-command")
        for name in (
            "the main conversation calls rec:probecall by the Skill tool",
            "the Skill call of rec:probecall ran",
        ):
            fields = record[name]["payload"]
            same = skill_call()[name.replace("rec:probecall", "lane:up")]
            self.assertEqual(sorted(fields), sorted(same), f"{name}: the fields of 2.1.322's")

    def test_a_skill_call_of_a_skill_the_model_cannot_call_fails_with_no_event_as_recorded(self):
        self.probe("probe", "disable-model-invocation: True\n")
        answer = self.conversation.skill("changelog:probe", "")
        self.assertTrue(answer.blocked, "the call fails")
        self.assertTrue(
            answer.said.startswith(
                "<tool_use_error>Skill changelog:probe cannot be used with Skill tool due to"
                " disable-model-invocation. Ask the user to run /changelog:probe themselves"
            ),
            answer.said,
        )
        self.assertEqual(len(self.sent()), 1, "no hook sees the call")
        self.assertEqual(answer.output, "", "the skill's command never ran")

    def git(self, *args):
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
            cwd=self.repo,
            check=True,
            capture_output=True,
        )

    def where(self):
        """The folder each hook ran in, and its CLAUDE_PROJECT_DIR, in the order of the log."""
        with open(self.log + ".where", encoding="utf-8") as f:
            return [tuple(json.loads(line)) for line in f]

    def worktree_records(self):
        return {e: r["payload"] for e, r in lines_of("worktree").items()}

    def test_entering_a_worktree_by_its_name_moves_the_events_and_the_hooks_as_recorded(self):
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        worktree = os.path.join(self.repo, ".claude", "worktrees", "rec-wt")
        self.assertFalse(self.conversation.enter_worktree(name="rec-wt").blocked)
        inside = self.conversation.bash("pwd")
        self.assertEqual(inside.output, f"{worktree}\n", "Bash runs in the worktree")
        self.assertFalse(self.conversation.exit_worktree("remove").blocked)
        after = self.conversation.bash('pwd; echo "${CLAUDE_PROJECT_DIR:-unset}"')
        self.assertEqual(after.output, f"{self.repo}\nunset\n", "Bash runs in the repository")
        self.assertFalse(os.path.exists(worktree), "remove removes the worktree")
        self.assert_sent_as_recorded(
            [
                "session started",
                "the main conversation enters a worktree by EnterWorktree",
                "the EnterWorktree call ran",
                "the main conversation runs a command in the worktree",
                "the command in the worktree ran",
                "the main conversation leaves the worktree by ExitWorktree",
                "the ExitWorktree call ran",
                "the main conversation runs a command after it left the worktree",
                "the command after the worktree ran",
            ],
            {**recorded(), **self.worktree_records()},
        )
        record = lines_of("worktree")
        ran = record["the EnterWorktree call ran"]
        left = record["the ExitWorktree call ran"]
        sent = self.sent()
        self.assertEqual(
            sent[2]["tool_response"],
            json.loads(json.dumps(ran["payload"]["tool_response"]).replace("<repo>", self.repo)),
        )
        self.assertEqual(
            sent[6]["tool_response"],
            json.loads(json.dumps(left["payload"]["tool_response"]).replace("<repo>", self.repo)),
        )
        moved = os.path.join(self.temp, "worktree-transcripts", "rec-wt")
        self.assertEqual(
            [os.path.dirname(p["transcript_path"]) == moved for p in sent],
            [False, False, True, True, True, True, False, False, False],
            "the transcript is the worktree's from the EnterWorktree call's end to ExitWorktree's",
        )
        hooks = [
            tuple(
                r["hook_process"][k].replace("<repo>", self.repo)
                for k in ("cwd", "CLAUDE_PROJECT_DIR")
            )
            for r in record.values()
            if r["event"]
            in {
                "the conversation starts",
                "the main conversation enters a worktree by EnterWorktree",
                "the EnterWorktree call ran",
                "the main conversation runs a command in the worktree",
                "the command in the worktree ran",
                "the main conversation leaves the worktree by ExitWorktree",
                "the ExitWorktree call ran",
                "the main conversation runs a command after it left the worktree",
                "the command after the worktree ran",
            }
        ]
        self.assertEqual(self.where(), hooks, "each hook runs where the record's ran")

    def test_entering_a_worktree_by_its_path_moves_a_subagents_events_as_recorded(self):
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        worktree = os.path.join(self.repo, ".claude", "worktrees", "rec-path")
        self.git("worktree", "add", "-q", "-b", "rec-path", worktree)
        self.conversation.enter_worktree(path=".claude/worktrees/rec-path")
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        self.assertEqual(agent.bash("pwd").output, f"{worktree}\n", "a subagent runs there too")
        agent.end("written")
        self.conversation.exit_worktree("keep")
        self.assertTrue(os.path.isdir(worktree), "keep leaves the worktree")
        sent = self.sent()
        called, ran = sent[1:3]
        self.assertEqual(called["tool_input"], {"path": ".claude/worktrees/rec-path"})
        self.assertEqual(ran["tool_input"], {"path": worktree}, "the path made whole")
        record = self.worktree_records()
        self.assertEqual(
            ran["tool_response"],
            json.loads(
                json.dumps(record["the EnterWorktree call by path ran"]["tool_response"]).replace(
                    "<repo>", self.repo
                )
            ),
        )
        self.assertEqual(
            sent[-1]["tool_response"],
            json.loads(
                json.dumps(
                    record["the ExitWorktree call that keeps the worktree ran"]["tool_response"]
                ).replace("<repo>", self.repo)
            ),
        )
        for payload in sent[2:-1]:
            self.assertEqual(payload["cwd"], worktree, payload["hook_event_name"])
        self.assertEqual(sent[-1]["cwd"], self.repo)
        self.assertEqual(
            {where for where, _ in self.where()[2:-1]}, {worktree}, "each hook runs there"
        )
        self.assertEqual({project for _, project in self.where()}, {self.repo})

    def test_an_enter_worktree_that_a_hook_denies_leaves_the_conversation_where_it_was(self):
        self.conversation.env["DENY"] = "EnterWorktree,ExitWorktree"
        self.assertTrue(self.conversation.enter_worktree(name="rec-wt").blocked)
        self.assertEqual(self.conversation.bash("pwd").output, f"{self.repo}\n")
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".claude")))

    def test_an_exit_worktree_that_a_hook_denies_leaves_the_conversation_in_the_worktree(self):
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        self.conversation.enter_worktree(name="rec-wt")
        self.conversation.env["DENY"] = "ExitWorktree"
        self.assertTrue(self.conversation.exit_worktree("remove").blocked)
        worktree = os.path.join(self.repo, ".claude", "worktrees", "rec-wt")
        self.assertEqual(self.conversation.bash("pwd").output, f"{worktree}\n")

    def test_a_subagent_stopped_by_task_stop_sends_the_events_recorded_and_no_end(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        answer = self.conversation.task_stop(agent)
        self.assertFalse(answer.blocked)
        records = {e: r["payload"] for e, r in lines_of("task-stop").items() if "payload" in r}
        self.assert_sent_as_recorded(
            [
                "session started",
                "the main conversation starts writer in the background",
                "writer starts",
                "writer runs in the background",
                "the main conversation stops sleeper by TaskStop",
                "the TaskStop call ran",
                "the stopped sleeper's notification reaches the main conversation",
            ],
            {**recorded(), **records},
        )
        started, called, ran, notified = self.sent()[1], *self.sent()[4:]
        self.assertEqual(called["tool_input"], {"task_id": agent.id})
        self.assertEqual(ran["tool_use_id"], called["tool_use_id"], "one call's two events")
        self.assertEqual(
            ran["tool_response"],
            {
                "message": f"Successfully stopped task: {agent.id} (Write entries)",
                "task_id": agent.id,
                "task_type": "local_agent",
                "command": "Write entries",
            },
        )
        prompt = notified["prompt"]
        self.assertIn(f"<task-id>{agent.id}</task-id>", prompt)
        self.assertIn(f"<tool-use-id>{started['tool_use_id']}</tool-use-id>", prompt)
        self.assertIn(f"<output-file>{agent.output_file}</output-file>", prompt)
        self.assertIn("<status>killed</status>", prompt)
        self.assertIn('<summary>Agent "Write entries" was stopped by Claude</summary>', prompt)
        self.assertNotIn("<result>", prompt, "a stopped subagent gives no result")
        self.assertEqual(notified["prompt_id"], called["prompt_id"], "it comes in the same turn")
        self.assertFalse(agent.running)
        self.assertEqual(self.conversation.background_tasks(), [], "the agent runs no more")
        with self.assertRaises(AssertionError):
            agent.end("written")

    def test_a_task_stop_of_a_subagent_whose_end_came_fails_with_no_event_as_recorded(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        agent.end("written")
        before = len(self.sent())
        answer = self.conversation.task_stop(agent)
        self.assertTrue(answer.blocked, "the call fails")
        self.assertEqual(
            answer.said,
            f"<tool_use_error>Task {agent.id} is not running (status: completed)</tool_use_error>",
        )
        self.assertEqual(len(self.sent()), before, "no hook sees the call")

    def test_a_task_stop_that_a_hook_denies_leaves_the_subagent_running(self):
        _, agent = self.conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # No hook of the test's plugin stops the start.
        self.conversation.env["DENY"] = "TaskStop"
        answer = self.conversation.task_stop(agent)
        self.assertTrue(answer.blocked, "a PreToolUse deny stops the TaskStop call")
        self.assertEqual(answer.said, "Run only `git log --oneline`.")
        self.assertTrue(agent.running, "the agent runs on")
        self.assertEqual(self.sent()[-1]["tool_name"], "TaskStop", "no event after the stop")

    def hook_failure(self, entry):
        """Puts the entry on the test's plugin's PreToolUse of Bash in place of its own hooks, and
        gives the record of a call that meets such an entry."""
        hooks = {"PreToolUse": [{"matcher": "Bash", "hooks": [entry]}]}
        self.write("changelog/hooks/hooks.json", json.dumps({"hooks": hooks}))
        path = os.path.join(RECORDED, "claude-code-2.1.322-hook-failures.jsonl")
        with open(path, encoding="utf-8") as f:
            records = [json.loads(line) for line in f]
        return next(r for r in records if ("args" in r["entry"]) == ("args" in entry))

    def test_a_hook_in_exec_form_whose_command_is_not_on_the_path_stops_a_call_as_recorded(self):
        missing = "python3-missing-for-rec"
        record = self.hook_failure(
            {
                "type": "command",
                "command": missing,
                "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/log.py"],
                "onFailure": "block",
            }
        )
        conversation = Conversation(self.repo, [self.plugin], self.conversation.env, self.temp)
        _, agent = conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # The entry holds only Bash.
        answer = agent.bash("true")
        self.assertTrue(answer.blocked, "onFailure block stops the call")
        self.assertIsNone(answer.exit_code, "the command never ran")
        self.assertEqual(
            answer.said, record["tool_result"].replace("PreToolUse:Read", "PreToolUse:Bash")
        )

    def test_a_hook_in_shell_form_whose_command_is_not_on_the_path_stops_a_call_as_recorded(self):
        missing = "python3-missing-for-rec"
        record = self.hook_failure(
            {
                "type": "command",
                "command": f"{missing} ${{CLAUDE_PLUGIN_ROOT}}/hooks/log.py",
                "onFailure": "block",
            }
        )
        conversation = Conversation(self.repo, [self.plugin], self.conversation.env, self.temp)
        _, agent = conversation.start("changelog:writer", "/changelog:write", "Write entries")
        assert agent is not None  # The entry holds only Bash.
        answer = agent.bash("true")
        self.assertTrue(answer.blocked, "onFailure block stops the call")
        first, _, error = record["tool_result"].partition("\n")
        said_first, _, said_error = answer.said.partition("\n")
        self.assertEqual(said_first, first.replace("PreToolUse:Edit", "PreToolUse:Bash"))
        # The error is that of the machine's /bin/sh, as Claude Code runs the entry in it.
        self.assertIn(f"{missing}: not found", said_error)
        self.assertTrue(error.endswith(f"{missing}: not found"), error)

    def test_a_python_command_with_no_python_on_the_path_fails_as_a_shell_runs_it(self):
        env = dict(self.conversation.env, PATH=os.path.join(self.temp, "no-python"))
        conversation = Conversation(self.repo, [], env, self.temp)
        answer = conversation.bash("python3 -c pass")
        self.assertEqual(answer.exit_code, 127, f"the shell finds no python3: {answer.output}")

    def test_a_missing_hook_script_stops_a_tool_call(self):
        os.remove(os.path.join(self.plugin, "hooks", "log.py"))
        answer = self.conversation.bash("true")
        self.assertTrue(answer.blocked, "python3 exits 2 on a missing script, which stops the call")
        self.assertIn("No such file or directory", answer.said)

    # How the double reads what a hook gives, as the hooks reference says, each case on one hook
    # of the test's own in place of the logging plugin's.

    def hooked(self, event, script, matcher=None, on_failure=None):
        """A conversation whose one hook runs the Python script on the event, through the matcher
        and with the onFailure given."""
        self.write("changelog/hooks/hook.py", script)
        entry = {
            "type": "command",
            "command": "python3",
            "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/hook.py"],
        }
        if on_failure:
            entry["onFailure"] = on_failure
        group = {"hooks": [entry], **({"matcher": matcher} if matcher else {})}
        self.write("changelog/hooks/hooks.json", json.dumps({"hooks": {event: [group]}}))
        return Conversation(self.repo, [self.plugin], self.conversation.env, self.temp)

    def test_a_plugin_with_no_hooks_file_runs_no_hook(self):
        # Given: the plugin holds no hooks/hooks.json.
        os.remove(os.path.join(self.plugin, "hooks", "hooks.json"))
        before = len(self.sent())
        conversation = Conversation(self.repo, [self.plugin], self.conversation.env, self.temp)
        # When: the main conversation runs a command.
        answer = conversation.bash("true")
        # Then: the call ran, and no hook logged an event.
        self.assertEqual((answer.blocked, answer.exit_code), (False, 0))
        self.assertEqual(len(self.sent()), before, "no hook ran")

    def test_exit_2_on_a_typed_commands_expansion_stops_the_skill(self):
        # Given: a hook that exits 2 on UserPromptExpansion.
        conversation = self.hooked("UserPromptExpansion", "import sys; sys.exit(2)")
        # When: the person types the command of the plugin's skill.
        answer = conversation.type("/changelog:write")
        # Then: the skill is stopped, and its text reaches no model.
        self.assertTrue(answer.blocked, "exit 2 on UserPromptExpansion stops the skill")
        self.assertEqual(answer.output, "", "the skill's text reaches no model")

    def test_a_matcher_beyond_names_matches_as_an_unanchored_regular_expression(self):
        # Given: a hook on PreToolUse whose matcher `as.` holds a character beyond a name list.
        conversation = self.hooked("PreToolUse", "import sys; sys.exit(2)", matcher="as.")
        # When: the main conversation calls Bash.
        answer = conversation.bash("true")
        # Then: the matcher takes Bash, as `as.` matches in it, and the hook stops the call.
        self.assertTrue(answer.blocked, "`as.` matches Bash anywhere in its name")

    def test_exit_2_on_an_event_that_takes_no_block_stops_nothing(self):
        # Given: a hook that exits 2 on PostToolUse, which the hooks reference says can't block.
        conversation = self.hooked("PostToolUse", "import sys; sys.exit(2)")
        # When: the main conversation runs a command.
        answer = conversation.bash("true")
        # Then: the call went through, unstopped.
        self.assertEqual(
            (answer.blocked, answer.exit_code), (False, 0), "PostToolUse takes no block"
        )

    def test_a_missing_script_on_stop_lets_the_stop_through(self):
        # Given: a hook on Stop whose script isn't there, which python3 exits 2 on.
        conversation = self.hooked("Stop", "")
        os.remove(os.path.join(self.plugin, "hooks", "hook.py"))
        # When: the main conversation stops.
        answer = conversation.stop("Done.")
        # Then: the stop goes through, as the hook never ran.
        self.assertFalse(answer.blocked, "a hook that never ran holds no stop")

    def test_a_failed_hook_without_on_failure_block_lets_the_call_through(self):
        # Given: a hook on PreToolUse that exits 1.
        conversation = self.hooked("PreToolUse", "import sys; sys.exit(1)")
        # When: the main conversation calls Bash.
        answer = conversation.bash("true")
        # Then: the call ran, as a failure is a non-blocking error.
        self.assertEqual((answer.blocked, answer.exit_code), (False, 0), "the call goes ahead")

    def test_a_hook_whose_output_is_no_json_fails(self):
        # Given: a hook on PreToolUse, with onFailure block, that prints text opening with `{` that
        # isn't JSON.
        conversation = self.hooked("PreToolUse", "print('{not json')", on_failure="block")
        # When: the main conversation calls Bash.
        answer = conversation.bash("true")
        # Then: the call is stopped, as output that can't be read fails the hook.
        self.assertTrue(answer.blocked, "unreadable output fails a hook with onFailure block")

    def test_a_failed_hook_with_on_failure_block_stops_a_prompt_with_its_error(self):
        # Given: a hook on UserPromptSubmit, with onFailure block, that fails with an error.
        script = "import sys; print('the check broke', file=sys.stderr); sys.exit(1)"
        conversation = self.hooked("UserPromptSubmit", script, on_failure="block")
        # When: the person types a prompt.
        answer = conversation.type("hello")
        # Then: the prompt is stopped with the hook's error.
        self.assertEqual((answer.blocked, answer.said), (True, "the check broke"))

    def test_continue_false_stops_with_its_stop_reason(self):
        # Given: a hook on PreToolUse that gives continue false with a stopReason.
        script = (
            'import json; print(json.dumps({"continue": False, "stopReason": "Build failed."}))'
        )
        conversation = self.hooked("PreToolUse", script)
        # When: the main conversation calls Bash.
        answer = conversation.bash("true")
        # Then: the call is stopped with the reason.
        self.assertEqual((answer.blocked, answer.said), (True, "Build failed."))

    def test_a_skill_call_of_a_skill_no_loaded_plugin_holds_gives_no_text(self):
        # When: the main conversation calls a skill of a plugin that the conversation didn't load.
        answer = self.conversation.skill("other:review", "")
        # Then: the call goes through with no skill text, as the double has none to read.
        self.assertEqual((answer.blocked, answer.output), (False, ""), "no text of another's skill")


class RunPythonTest(unittest.TestCase):
    def test_a_script_run_in_this_process_gets_arguments_of_its_own_as_a_new_process_does(self):
        folder = tempfile.mkdtemp(prefix="run-python-")
        self.addCleanup(shutil.rmtree, folder)
        script = os.path.join(folder, "same.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(
                'import sys\nNAME = "generator"\nprint(sys.argv[1] == NAME, sys.argv[1] is NAME)\n'
            )

        code, out, _ = run_python(script, ["generator"], "", dict(os.environ), folder)

        self.assertEqual((code, out), (0, "True False\n"), "equal, and not the script's constant")

    def test_a_script_that_exits_with_text_prints_it_and_gives_1_as_a_new_process_does(self):
        folder = tempfile.mkdtemp(prefix="run-python-")
        self.addCleanup(shutil.rmtree, folder)
        script = os.path.join(folder, "refuse.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write('import sys\nsys.exit("refused: no plan")\n')

        code, _, err = run_python(script, [], "", dict(os.environ), folder)

        self.assertEqual((code, err), (1, "refused: no plan\n"), "sys.exit with text")

    def test_a_script_that_raises_prints_its_traceback_and_gives_1_as_a_new_process_does(self):
        folder = tempfile.mkdtemp(prefix="run-python-")
        self.addCleanup(shutil.rmtree, folder)
        script = os.path.join(folder, "broken.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write('raise ValueError("broken")\n')

        code, _, err = run_python(script, [], "", dict(os.environ), folder)

        self.assertEqual(code, 1, "an error the script doesn't catch")
        self.assertIn("ValueError: broken", err, "the traceback on standard error")

    def test_a_module_that_a_script_imports_goes_once_it_ends_as_with_its_process(self):
        folder = tempfile.mkdtemp(prefix="run-python-")
        self.addCleanup(shutil.rmtree, folder)
        with open(os.path.join(folder, "beside_double.py"), "w", encoding="utf-8") as f:
            f.write("NAME = 'beside'\n")
        script = os.path.join(folder, "uses.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write("import beside_double\nprint(beside_double.NAME)\n")

        code, out, _ = run_python(script, [], "", dict(os.environ), folder)

        self.assertEqual((code, out), (0, "beside\n"))
        self.assertNotIn("beside_double", sys.modules, "the module goes with the run")


if __name__ == "__main__":
    unittest.main()

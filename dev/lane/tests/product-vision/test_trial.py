"""The judge of trial.py, tried on kept records whose answers the intent settles, before any run
rests on it, as Q9 of the architecture best practice asks of a trial's judge: for each count the
judge makes of writer's practices, of each start's text and of each resume, a record that should
pass and one that should fail. Each record holds the entries Claude Code 2.1.319 keeps, as its
sessions showed them: a tool use in an assistant entry, its result in a user entry with Claude
Code's `toolUseResult` beside it, a prompt the person typed with the origin `human`, and the end of
a background subagent handed to the main conversation as a task-notification naming its ID. These
tests try the check of the person's stand-in on answers whose rightness the person's intent settles;
`trial.py --person` tries the stand-in itself, a model."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from typing import Any
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import trial

# What Claude Code gives back for a call that a PreToolUse hook stopped.
HALTED = "PreToolUse:Bash hook error: [hook]: changelog: Run only `git log --oneline`."
# How Claude Code keeps the decision of a PreToolUse hook that stopped a call.
REJECTED = {
    "decision": "reject",
    "source": "hook",
    "reasonType": "hook",
    "reasonCode": "hook:PreToolUse",
}
RESULT = "python3 /p/changelog/hooks/lane/result.py {name} {on}"
# The plugin's folder, and the command that Lane names for each start, as the routes name it.
ROOT = "/p/changelog"
START = "python3 /p/changelog/scripts/start.py {name}"
WRITER_TEXT = 'Write the entries of the next release into `CHANGELOG.md`.\n{"intents": ["Q1"]}'
REVIEWER_TEXT = "Review the entries under `## Unreleased` of `CHANGELOG.md`."
ROUTES = {
    "orchestrator": "write",
    "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/start.py",
    "routes": [
        {"from": "write", "to": "writer"},
        {"from": "writer", "on": "written", "to": "reviewer"},
        {"from": "reviewer", "on": "more", "to": "writer"},
        {"from": "reviewer", "on": "asks", "waits": True},
        {"from": "reviewer", "on": "good"},
    ],
}


class Record:
    """A record that the test writes as Claude Code keeps one: each call made and come back, each
    prompt and each end handed on, in order."""

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []
        self.number = 0

    def call(
        self,
        tool: str,
        given: dict[str, Any],
        back: str = "",
        error: bool = False,
        stdout: str | None = None,
        made: dict[str, Any] | None = None,
        denied: bool = False,
    ) -> str:
        """Adds a call of the tool with its input, come back with the text, or stopped where error,
        with HALTED as its text; its ID."""
        self.number += 1
        use = f"toolu_{self.number:02d}"
        content = [{"type": "tool_use", "id": use, "name": tool, "input": given}]
        self.entries.append({"type": "assistant", "message": {"content": content}})
        result = {"type": "tool_result", "tool_use_id": use, "content": back, "is_error": error}
        kept = made or ({"stdout": stdout, "stderr": ""} if stdout is not None else {})
        self.entries.append(
            {
                "type": "user",
                "timestamp": f"2026-11-08T00:00:{self.number:02d}.000Z",
                "message": {"content": [result]},
                "toolUseResult": kept,
                **({"permissionDecision": REJECTED} if denied else {}),
            }
        )
        return use

    def stopped(self, tool: str, given: dict[str, Any]) -> str:
        """Adds a call a PreToolUse hook stopped, as Claude Code 2.1.319 keeps it: a SendMessage
        with the hook's words alone, any other tool with them after `PreToolUse:<tool> hook
        error:`, each with the decision of the hook that rejected it."""
        back = HALTED if tool != "SendMessage" else HALTED.split("[hook]: ", 1)[1]
        return self.call(tool, given, back, error=True, denied=True)

    def prompt(self, text: str, printed: bool = False) -> None:
        """Adds a prompt the person typed: in an interactive session, with the origin `human`, or
        in `claude -p` where printed, with no origin, as Claude Code keeps each."""
        entry: dict[str, Any] = {"type": "user", "message": {"content": text}}
        self.entries.append(entry if printed else {**entry, "origin": {"kind": "human"}})

    def sent(self, text: str) -> None:
        """Adds a message the main conversation sent the subagent, which resumes it, as Claude Code
        keeps it in the subagent's record."""
        said = f"The coordinator sent a message while you were working:\n{text}"
        self.entries.append(
            {"type": "user", "message": {"content": said}, "origin": {"kind": "coordinator"}}
        )

    def meta(self, text: str) -> None:
        """Adds a text Claude Code puts in the conversation itself, such as a system reminder."""
        self.entries.append({"type": "user", "message": {"content": text}, "isMeta": True})

    def ended(self, agent: str) -> None:
        """Adds the end of the background subagent of the ID, as handed to the main
        conversation."""
        text = f"<task-notification>\n<task-id>{agent}</task-id>\n<status>completed</status>"
        self.entries.append(
            {
                "type": "user",
                "message": {"content": text},
                "origin": {"kind": "task-notification"},
            }
        )

    def begun(self) -> None:
        """Adds the prompt that a subagent's record begins with, as Claude Code writes it once the
        subagent has started."""
        self.entries.append(
            {"type": "user", "timestamp": "2026-11-08T00:00:00.500Z", "message": {"content": "go"}}
        )

    def saved(self, file: str, kind: str = "", by: str = "") -> str:
        """Writes the record at the path, with its meta file naming the agent type and the call
        that started it where the test names a kind; the path."""
        with open(file, "w", encoding="utf-8") as f:
            f.write("".join(json.dumps(e) + "\n" for e in self.entries))
        if kind:
            meta = {"agentType": kind, "toolUseId": by}
            with open(os.path.splitext(file)[0] + ".meta.json", "w", encoding="utf-8") as f:
                json.dump(meta, f)
        return file


class Kept(unittest.TestCase):
    """A test with a folder of its own for the records it keeps."""

    def setUp(self) -> None:
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder)

    def writer(self, record: Record) -> dict[str, Any]:
        """writer's calls, as the judge reads them from the record kept."""
        file = record.saved(os.path.join(self.folder, "agent-w.jsonl"), "changelog:writer")
        return trial.record_of(file)

    def judged_writer(self, *records: Record) -> list[str]:
        """What went wrong of writer's starts kept in the records, one start each."""
        starts = []
        for number, record in enumerate(records):
            file = record.saved(os.path.join(self.folder, f"agent-w{number}.jsonl"), "w")
            starts += trial.starts_of(trial.record_of(file))
        return trial.writer_judged(starts, self.folder, [], ["written"])["wrong"]


def listed(record: Record) -> None:
    """Adds writer's `git log --oneline`, come back."""
    record.call("Bash", {"command": "git log --oneline"}, "abc Add tags")


def edited(record: Record, path: str = "CHANGELOG.md", stop: bool = False) -> None:
    """Adds writer's Edit of the path, come back, or stopped where stop."""
    given = {"file_path": path, "old_string": "a", "new_string": "b"}
    if stop:
        record.stopped("Edit", given)
    else:
        record.call("Edit", given, "edited")


def gave(record: Record, name: str = "writer", on: str = "written", stop: bool = False) -> None:
    """Adds the result command of the subagent, come back, or stopped where stop."""
    given = {"command": RESULT.format(name=name, on=on)}
    if stop:
        record.stopped("Bash", given)
    else:
        record.call("Bash", given, "")


class TestWriterPractices(Kept):
    """writer's practices of the intent its start names, in their order: `git log --oneline`, then
    a write of CHANGELOG.md, then its result."""

    def test_in_order(self) -> None:
        record = Record()
        listed(record)
        edited(record)
        gave(record)
        self.assertEqual(self.judged_writer(record), [])

    def test_write_before_the_commits_went_through(self) -> None:
        record = Record()
        edited(record)
        listed(record)
        gave(record)
        wrong = self.judged_writer(record)
        self.assertEqual(len(wrong), 1)
        self.assertIn("before `git log --oneline` came back", wrong[0])

    def test_write_before_the_commits_stopped(self) -> None:
        record = Record()
        edited(record, stop=True)
        listed(record)
        edited(record)
        gave(record)
        self.assertEqual(self.judged_writer(record), [])

    def test_result_before_the_write_went_through(self) -> None:
        record = Record()
        listed(record)
        gave(record)
        edited(record)
        wrong = self.judged_writer(record)
        self.assertEqual(len(wrong), 1)
        self.assertIn("before its practices' traces came back", wrong[0])

    def test_result_after_the_practices_stopped(self) -> None:
        record = Record()
        listed(record)
        edited(record)
        gave(record, stop=True)
        wrong = self.judged_writer(record)
        self.assertEqual(len(wrong), 1)
        self.assertIn("an allowed call was stopped", wrong[0])

    def test_each_start_apart(self) -> None:
        first, second = Record(), Record()
        for each in (first,):
            listed(each)
            edited(each)
            gave(each)
        edited(second)
        wrong = self.judged_writer(first, second)
        self.assertEqual(len(wrong), 1)
        self.assertIn("before `git log --oneline` came back", wrong[0])

    def test_a_resumed_start_keeps_its_steps_again(self) -> None:
        record = Record()
        listed(record)
        edited(record)
        gave(record)
        record.sent("Commit CHANGELOG.md now.")
        gave(record, stop=True)
        listed(record)
        edited(record)
        gave(record)
        self.assertEqual(self.judged_writer(record), [])

    def test_other_file_stopped_after_the_commits(self) -> None:
        record = Record()
        listed(record)
        edited(record, "notes.md", stop=True)
        edited(record)
        gave(record)
        self.assertEqual(self.judged_writer(record), [])


class Run(Kept):
    """A run of the plugin's main conversation, with each start's record."""

    def setUp(self) -> None:
        super().setUp()
        self.main = Record()
        self.main.prompt(TYPED)
        self.agents: list[dict[str, Any]] = []

    def ran(self, name: str, text: str | None = None, command: str = START) -> None:
        """Adds the main conversation's run of start.py for the subagent, by the command that
        Lane names or the one given, printing its text."""
        printed = text if text is not None else TEXTS[name]
        self.main.call("Bash", {"command": command.format(name=name)}, printed, stdout=printed)

    def start(
        self, name: str, ons: list[str], prompt: str | None = None, stop: bool = False
    ) -> str:
        """Adds the start of the subagent with the prompt, start.py's text by default, its record
        giving each of the results, ended and handed to the main conversation where it went
        through; the ID of its run."""
        given = {"subagent_type": f"changelog:{name}", "prompt": prompt or TEXTS[name]}
        if stop:
            self.main.stopped("Agent", given)
            return ""
        agent = f"a{len(self.agents)}"
        use = self.main.call("Agent", given, "Async agent launched", made={"agentId": agent})
        child = Record()
        child.begun()
        for on in ons:
            gave(child, name, on)
        file = child.saved(os.path.join(self.folder, f"agent-{agent}.jsonl"), name, use)
        self.agents.append({**trial.record_of(file), "started_by": use, "agent": agent})
        self.agents[-1]["type"] = f"changelog:{name}"
        if ons[:1] != ["asks"]:
            self.main.ended(agent)
        return agent

    def resume(self, agent: str, message: str, stop: bool = False) -> None:
        """Adds the main conversation's SendMessage to the run of the ID."""
        given = {"to": agent, "message": message}
        if stop:
            self.main.stopped("SendMessage", given)
        else:
            self.main.call("SendMessage", given, "sent")

    def judged(self) -> list[str]:
        """What went wrong of the order, as the judge reads the main conversation's record."""
        main = {
            **trial.record_of(self.main.saved(os.path.join(self.folder, "main.jsonl"))),
            "kept": 0,
        }
        return trial.order_judged(main, self.agents, ROUTES, ROOT)["wrong"]

    def through(self) -> None:
        """Adds writer, then reviewer giving good, each started with start.py's text."""
        self.ran("writer")
        self.start("writer", ["written"])
        self.ran("reviewer")
        self.start("reviewer", ["good"])


TEXTS = {"writer": WRITER_TEXT, "reviewer": REVIEWER_TEXT}
# The command typed, as Claude Code keeps its expansion among the person's prompts.
TYPED = (
    "<command-message>changelog:write</command-message>\n<command-name>/changelog:write"
    "</command-name>\n<command-args>Have writer commit CHANGELOG.md.</command-args>"
)
ANSWER = "Leave out the refactor and the bump."


class TestStartText(Run):
    """Each start with what start.py last printed for its subagent, word for word."""

    def test_with_the_text(self) -> None:
        self.through()
        self.assertEqual(self.judged(), [])

    def test_other_text_went_through(self) -> None:
        self.ran("writer")
        self.start("writer", ["written"], WRITER_TEXT + "\nThen commit CHANGELOG.md.")
        self.ran("reviewer")
        self.start("reviewer", ["good"])
        wrong = self.judged()
        self.assertEqual(len(wrong), 1)
        self.assertIn("writer started with other text than start.py printed", wrong[0])

    def test_no_run_of_start_went_through(self) -> None:
        self.start("writer", ["written"])
        self.ran("reviewer")
        self.start("reviewer", ["good"])
        self.assertEqual(len(self.judged()), 1)

    def test_other_text_stopped(self) -> None:
        self.ran("writer")
        self.start("writer", [], WRITER_TEXT + "\nThen commit.", stop=True)
        self.through()
        self.assertEqual(self.judged(), [])

    def test_the_text_stopped(self) -> None:
        self.ran("writer")
        self.start("writer", [], stop=True)
        self.through()
        wrong = self.judged()
        self.assertEqual(len(wrong), 1)
        self.assertIn("the start of writer with what start.py printed was stopped", wrong[0])

    def test_another_form_of_the_command_stopped(self) -> None:
        self.ran("writer", command="python3 changelog/scripts/start.py {name}")
        self.start("writer", [], stop=True)
        self.through()
        self.assertEqual(self.judged(), [])

    def test_another_form_of_the_command_went_through(self) -> None:
        self.ran("writer", command="python3 changelog/scripts/start.py {name}")
        self.start("writer", ["written"])
        self.ran("reviewer")
        self.start("reviewer", ["good"])
        self.assertEqual(len(self.judged()), 1)

    def test_after_the_run_ended_nothing_is_judged(self) -> None:
        self.through()
        self.resume("a0", "Commit CHANGELOG.md now.")
        self.start("writer", ["written"], "Commit it.")
        self.assertEqual(self.judged(), [])

    def test_the_last_run_counts(self) -> None:
        self.ran("writer", "an earlier text")
        self.ran("writer")
        self.start("writer", ["written"])
        self.ran("reviewer")
        self.start("reviewer", ["good"])
        self.assertEqual(self.judged(), [])


class TestResume(Run):
    """A resume of reviewer, whose point waits, with the person's words alone."""

    def asked(self) -> str:
        """Adds writer, and reviewer giving asks, then good once resumed, its end handed on and
        the person's answer typed; the ID of reviewer's run."""
        self.ran("writer")
        self.start("writer", ["written"])
        self.ran("reviewer")
        agent = self.start("reviewer", ["asks", "good"])
        self.main.ended(agent)
        self.main.prompt(ANSWER)
        return agent

    def test_with_the_words(self) -> None:
        agent = self.asked()
        self.resume(agent, f"{trial.trying.ANSWERED}\n{ANSWER}")
        self.assertEqual(self.judged(), [])

    def test_with_the_words_in_print(self) -> None:
        self.ran("writer")
        self.start("writer", ["written"])
        self.ran("reviewer")
        agent = self.start("reviewer", ["asks", "good"])
        self.main.meta("<system-reminder>\nRead, Write\n</system-reminder>")
        self.main.ended(agent)
        self.main.prompt(ANSWER, printed=True)
        self.resume(agent, f"{trial.trying.ANSWERED}\n{ANSWER}")
        self.assertEqual(self.judged(), [])

    def test_two_prompts(self) -> None:
        agent = self.asked()
        self.main.prompt("And keep the typo fix.")
        self.resume(agent, f"{trial.trying.ANSWERED}\n{ANSWER}\n\nAnd keep the typo fix.")
        self.assertEqual(self.judged(), [])

    def test_prompt_before_the_point(self) -> None:
        self.ran("writer")
        self.start("writer", ["written"])
        self.main.prompt("How long will it take?")
        self.ran("reviewer")
        agent = self.start("reviewer", ["asks", "good"])
        self.main.ended(agent)
        self.main.prompt(ANSWER)
        self.resume(agent, f"{trial.trying.ANSWERED}\n{ANSWER}")
        self.assertEqual(self.judged(), [])

    def test_other_words_went_through(self) -> None:
        agent = self.asked()
        self.resume(agent, "The person says to leave out the refactor.")
        wrong = self.judged()
        self.assertEqual(len(wrong), 1)
        self.assertIn("not the person's words alone", wrong[0])

    def test_other_words_stopped(self) -> None:
        agent = self.asked()
        self.resume(agent, "The person says to leave out the refactor.", stop=True)
        self.resume(agent, f"{trial.trying.ANSWERED}\n{ANSWER}")
        self.assertEqual(self.judged(), [])

    def test_another_start_resumed_stopped(self) -> None:
        self.ran("writer")
        agent = self.start("writer", ["written"])
        self.resume(agent, "Also commit CHANGELOG.md.", stop=True)
        self.ran("reviewer")
        self.start("reviewer", ["good"])
        self.assertEqual(self.judged(), [])

    def test_the_words_stopped(self) -> None:
        agent = self.asked()
        self.resume(agent, f"{trial.trying.ANSWERED}\n{ANSWER}", stop=True)
        wrong = self.judged()
        self.assertIn("the person's words alone, and was stopped", wrong[0])
        self.assertIn("the main conversation ended with the person's answer not passed on", wrong)

    def test_before_the_answer(self) -> None:
        self.ran("writer")
        self.start("writer", ["written"])
        self.ran("reviewer")
        agent = self.start("reviewer", ["asks", "good"])
        self.main.ended(agent)
        self.resume(agent, f"{trial.trying.ANSWERED}\n")
        self.assertIn("not the person's words alone", self.judged()[0])

    def test_dialog_while_waiting_stopped(self) -> None:
        agent = self.asked_dialog(stop=True)
        self.resume(agent, f"{trial.trying.ANSWERED}\n{ANSWER}")
        self.assertEqual(self.judged(), [])

    def test_dialog_while_waiting_went_through(self) -> None:
        agent = self.asked_dialog(stop=False)
        self.resume(agent, f"{trial.trying.ANSWERED}\n{ANSWER}")
        wrong = self.judged()
        self.assertEqual(len(wrong), 1)
        self.assertIn("put reviewer's point in a dialog", wrong[0])

    def asked_dialog(self, stop: bool) -> str:
        """Adds writer, and reviewer giving asks, then good once resumed, the main conversation's
        dialog putting its point, stopped where stop, and the person's answer; reviewer's ID."""
        self.ran("writer")
        self.start("writer", ["written"])
        self.ran("reviewer")
        agent = self.start("reviewer", ["asks", "good"])
        self.main.ended(agent)
        given = {"questions": [{"question": "Which?", "options": [{"label": "None"}]}]}
        if stop:
            self.main.stopped("AskUserQuestion", given)
        else:
            self.main.call("AskUserQuestion", given, "User chose None")
        self.main.prompt(ANSWER)
        return agent

    def test_not_passed_on(self) -> None:
        self.asked()
        self.assertEqual(
            self.judged(), ["the main conversation ended with the person's answer not passed on"]
        )

    def test_waiting_unanswered(self) -> None:
        self.ran("writer")
        self.start("writer", ["written"])
        self.ran("reviewer")
        agent = self.start("reviewer", ["asks"])
        self.main.ended(agent)
        self.assertEqual(self.judged(), [])

    def test_start_while_waiting(self) -> None:
        self.asked()
        self.ran("writer")
        self.start("writer", ["written"])
        wrong = self.judged()
        self.assertIn("writer started while the order named the person's answer to reviewer", wrong)

    def test_resumed_then_more(self) -> None:
        self.ran("writer")
        self.start("writer", ["written"])
        self.ran("reviewer")
        agent = self.start("reviewer", ["asks", "more"])
        self.main.ended(agent)
        self.main.prompt(ANSWER)
        self.resume(agent, f"{trial.trying.ANSWERED}\n{ANSWER}")
        self.through()
        self.assertEqual(self.judged(), [])


class TestOrderHeld(unittest.TestCase):
    """The routes laid as the intent's order: reviewer's point waiting for the person's answer."""

    def test_the_intents_order(self) -> None:
        self.assertTrue(trial.order_held(ROUTES))

    def test_no_route_waits(self) -> None:
        given = {**ROUTES, "routes": [r for r in ROUTES["routes"] if not r.get("waits")]}
        self.assertFalse(trial.order_held(given))

    def test_asks_ends_the_run(self) -> None:
        each = [{k: v for k, v in r.items() if k != "waits"} for r in ROUTES["routes"]]
        self.assertFalse(trial.order_held({**ROUTES, "routes": each}))


class TestUnheld(unittest.TestCase):
    """What the rules laid at a commit leave unheld: writer's practices through a steps adapter,
    and start.py as the text of each start."""

    def setUp(self) -> None:
        self.repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo)
        self.write_to = "CHANGELOG.md"
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str) -> str:
        """What git prints, run in the test's repository."""
        who = ["-c", "user.name=t", "-c", "user.email=t@example.com"]
        done = subprocess.run(
            ["git", "-C", self.repo, *who, *args], capture_output=True, text=True, check=True
        )
        return done.stdout.strip()

    def laid(self, adapter: str | None, routed: dict[str, Any]) -> list[str]:
        """What's unheld once the test lays and commits writer's lanes, the adapter's text where
        given, and the routes."""
        steps = [
            {"step": 2, "lanes": [{"lane": "run_only", "takes": ["git log --oneline"]}]},
            {"step": 3, "lanes": [{"lane": "write_only", "takes": [self.write_to]}]},
        ]
        writer: dict[str, Any] = {"name": "writer", "steps": steps}
        files = {"changelog/agents/writer.md": "writer\n"}
        if adapter is not None:
            writer["steps_adapter"] = "hooks/adapters/steps-writer.py"
            files["changelog/hooks/adapters/steps-writer.py"] = adapter
        laid = {"plugin": "changelog", "subagents": [writer], "routes": routed}
        files["changelog/hooks/lanes.json"] = json.dumps(laid)
        for path, text in files.items():
            os.makedirs(os.path.dirname(os.path.join(self.repo, path)), exist_ok=True)
            with open(os.path.join(self.repo, path), "w", encoding="utf-8") as f:
                f.write(text)
        self.git("add", ".")
        self.git("commit", "-q", "-m", "laid")
        return trial.unheld(laid, self.repo, self.git("rev-parse", "HEAD"))

    def test_held(self) -> None:
        self.assertEqual(self.laid(ADAPTER, ROUTES), [])

    def test_no_steps_adapter(self) -> None:
        wrong = self.laid(None, ROUTES)
        self.assertEqual(len(wrong), 1)
        self.assertIn("writer's steps adapter gives nothing", wrong[0])

    def test_adapter_out_of_order(self) -> None:
        wrong = self.laid(ADAPTER.replace("PRACTICES", "PRACTICES[::-1]"), ROUTES)
        self.assertEqual(len(wrong), 1)
        self.assertIn("writer's steps adapter gives", wrong[0])

    def test_the_root_changelog_by_the_plugins_folder(self) -> None:
        named = "${CLAUDE_PLUGIN_ROOT}/../CHANGELOG.md"
        self.write_to = named
        adapter = ADAPTER.replace('"takes": ["CHANGELOG.md"]', f'"takes": ["{named}"]')
        self.assertEqual(self.laid(adapter, ROUTES), [])

    def test_the_plugins_own_changelog(self) -> None:
        self.write_to = "${CLAUDE_PLUGIN_ROOT}/CHANGELOG.md"
        self.assertEqual(len(self.laid(ADAPTER, ROUTES)), 1)

    def test_no_command(self) -> None:
        routed = {k: v for k, v in ROUTES.items() if k != "command"}
        wrong = self.laid(ADAPTER, routed)
        self.assertEqual(len(wrong), 1)
        self.assertIn("name no start.py", wrong[0])


# A steps adapter as the stand-in might write it, giving writer's practices of the intents its
# start names.
ADAPTER = """import json, sys
PRACTICES = [{"says": "List.", "lanes": [{"lane": "run_step", "takes": ["git log --oneline"]}]},
             {"says": "Write.", "lanes": [{"lane": "write_step", "takes": ["CHANGELOG.md"]}]}]
values = json.load(sys.stdin)["values"]
lists = [{"list": q, "steps": PRACTICES} for q in values.get("intents") or [] if q == "Q1"]
print(json.dumps({"lists": lists}))
"""


class TestClaudeCode(Run):
    """What the records show of SubagentStart and of the stdout Lane kept."""

    def test_counts(self) -> None:
        self.through()
        main = trial.record_of(self.main.saved(os.path.join(self.folder, "main.jsonl")))
        os.makedirs(os.path.join(self.folder, "guard"))
        for agent in ("a0", "a1"):
            with open(os.path.join(self.folder, "guard", f"{agent}.jsonl"), "w") as f:
                given = {"kind": "given", "text": "go"}
                lines = [{"kind": "start"}, given] if agent == "a0" else [given, {"kind": "start"}]
                f.write("".join(json.dumps(e) + "\n" for e in lines))
        with open(os.path.join(self.folder, "guard", "run.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"kind": "text", "name": "writer", "text": WRITER_TEXT}) + "\n")
            f.write(json.dumps({"kind": "text", "name": "reviewer", "text": "other"}) + "\n")
        found = trial.claude_code(main, self.agents, self.folder, ROUTES, ROOT)
        self.assertEqual(
            found,
            [
                "a subagent's record begun before its start came back: 2 of 2",
                "SubagentStart kept by Lane before the start's prompt: 1 of 2",
                "start.py's stdout as Lane kept it: 1 of 2 runs (2 kept)",
            ],
        )


class TestPersonHeard(unittest.TestCase):
    """The person's stand-in asked again once where it gives no JSON, as Opus slipped so in a run
    of the trial."""

    def test_asked_again_after_no_json(self) -> None:
        right = {"asks": True, "answer": "Leave the refactor out.", "leaves_out": []}
        with mock.patch.object(
            trial.trying, "stand_in", side_effect=[SystemExit("no JSON"), right]
        ):
            self.assertEqual(trial.person_heard("Which?", [], "."), right)

    def test_no_json_twice_ends_the_trial(self) -> None:
        with (
            mock.patch.object(
                trial.trying, "stand_in", side_effect=[SystemExit("a"), SystemExit("b")]
            ),
            self.assertRaises(SystemExit),
        ):
            trial.person_heard("Which?", [], ".")


class TestPersonRight(unittest.TestCase):
    """The check of the person's stand-in's answer to a point, on answers whose rightness the
    person's intent settles."""

    ASKED = ("Refactor the note store", "Fix a typo in the help text")

    def test_right(self) -> None:
        heard = {"asks": True, "answer": "Leave out the refactor.", "leaves_out": [self.ASKED[0]]}
        self.assertEqual(trial.person_right(heard, list(self.ASKED)), [])

    def test_leaves_out_a_noticed_commit(self) -> None:
        heard = {"asks": True, "answer": "Leave both out.", "leaves_out": list(self.ASKED)}
        self.assertEqual(len(trial.person_right(heard, list(self.ASKED))), 1)

    def test_says_it_is_asked_nothing(self) -> None:
        heard = {"asks": False, "answer": "", "leaves_out": [self.ASKED[0]]}
        self.assertEqual(len(trial.person_right(heard, list(self.ASKED))), 2)


if __name__ == "__main__":
    unittest.main()

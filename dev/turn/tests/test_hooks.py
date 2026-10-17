import contextlib
import io
import json
import os
import runpy
import sys
from unittest import mock

from helpers import (
    CALL,
    GOOD,
    HOOKS,
    QUESTION,
    SENT_BACK,
    TURN,
    WAITS,
    RepoTest,
    pretooluse,
    subagentstop,
)

ID = "a1b2c3"


class HookTest(RepoTest):
    """Each test hands a hook the event Claude Code would, in a session whose transcripts sit in
    the temporary repository."""

    def setUp(self):
        super().setUp()
        self.transcript = os.path.join(self.repo, "session.jsonl")

    def given_prompt(self, agent_id, prompt):
        """Writes what Claude Code keeps of an agent's start: its prompt, as the first record."""
        path = os.path.join(self.repo, "session", "subagents", f"agent-{agent_id}.jsonl")
        record = {"type": "user", "message": {"role": "user", "content": prompt}}
        self.write(path, json.dumps(record) + "\n")
        return path

    def event(self, name, agent_type=None, **fields):
        event = {
            "session_id": "s",
            "transcript_path": self.transcript,
            "cwd": self.repo,
            "hook_event_name": name,
            **fields,
        }
        if agent_type:
            event.update(agent_id=ID, agent_type=agent_type)
        return event

    def tool(self, agent_type, tool_name, **tool_input):
        return self.event("PreToolUse", agent_type, tool_name=tool_name, tool_input=tool_input)

    def hook(self, entry, event):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = entry.main(io.StringIO(json.dumps(event)))
        return code, err.getvalue()

    def stops(self, entry, event, *said):
        code, err = self.hook(entry, event)
        self.assertEqual(code, 2, err)
        for words in said:
            self.assertIn(words, err)

    def passes(self, entry, event):
        self.assertEqual(self.hook(entry, event), (0, ""))


class TestCall(HookTest):
    def call(self, prompt):
        return self.tool(None, "Agent", subagent_type="turn:up", prompt=prompt)

    def test_a_call_turn_can_take_passes(self):
        # Given: a calling AI starting the orchestrator with a call whose CCS holds every kind
        # When: the call is about to be made
        # Then: it goes through
        self.passes(pretooluse, self.call(json.dumps(CALL)))

    def test_a_call_turn_cannot_take_stops_at_the_caller(self):
        # Given: a calling AI starting the orchestrator with a call naming a kind the CCS lacks
        # When: the call is about to be made
        # Then: it is stopped there, saying what is wrong, before any run starts
        call = dict(CALL, kind=dict(CALL["kind"], receiver="reader"))
        self.stops(pretooluse, self.call(json.dumps(call)), '"reader"')
        self.assertFalse(os.path.exists(CALL["result"]))

    def test_other_agents_and_tools_pass(self):
        # Given: a call to an agent that is not turn's, and a tool that is not a call
        # When: it is about to be made
        # Then: it goes through
        self.passes(pretooluse, self.tool(None, "Agent", subagent_type="Explore", prompt="look"))
        self.passes(pretooluse, self.tool(None, "Bash", command="ls"))


class TestStartAsCalled(HookTest):
    def start(self, call):
        command = f"python3 {TURN}/scripts/turn.py start '{json.dumps(call)}'"
        return self.tool("turn:up", "Bash", command=command)

    def test_the_run_started_with_the_call_passes(self):
        # Given: an orchestrator called with a call
        # When: it starts the run with that call
        # Then: it goes through
        self.given_prompt(ID, json.dumps(CALL))
        self.passes(pretooluse, self.start(CALL))

    def test_the_run_started_with_a_changed_call_stops(self):
        # Given: an orchestrator called with a call
        # When: it starts the run with a call that differs from it
        # Then: it is stopped, saying to start the run with the call as it was given
        self.given_prompt(ID, json.dumps(CALL))
        self.stops(pretooluse, self.start(dict(CALL, result="x.json")), "the call as it was given")

    def test_a_start_without_a_call_stops(self):
        # Given: an orchestrator called with a call
        # When: it starts the run with no JSON after the command
        # Then: it is stopped, saying to start the run with the call as it was given
        self.given_prompt(ID, json.dumps(CALL))
        event = self.tool("turn:up", "Bash", command=f"python3 {TURN}/scripts/turn.py start")
        self.stops(pretooluse, event, "the call as it was given")


class TestGeneratorStart(HookTest):
    def generator(self, prompt):
        return self.tool("turn:up", "Agent", subagent_type="turn:generator", prompt=prompt)

    def test_the_generator_started_with_the_prompt_the_script_gave_passes(self):
        # Given: a run started
        # When: the orchestrator starts the generator with the prompt the script printed
        # Then: it goes through
        self.passes(pretooluse, self.generator(self.started()))

    def test_the_generator_started_with_another_prompt_stops(self):
        # Given: a run started
        # When: the orchestrator starts the generator with a prompt that differs, one that is not
        # JSON, or one for a run not going
        # Then: it is stopped, saying to start it with what the script printed last
        prompt = json.loads(self.started())
        changed = json.dumps(dict(prompt, sent_back=[SENT_BACK]))
        elsewhere = json.dumps(dict(prompt, run="other.json"))
        for given in (changed, "make the README", elsewhere):
            with self.subTest(given=given):
                self.stops(pretooluse, self.generator(given), "what turn.py printed last")


class TestGeneratorReply(HookTest):
    def reply(self, message):
        path = self.given_prompt(ID, self.started())
        event = self.event(
            "SubagentStop",
            "turn:generator",
            agent_transcript_path=path,
            last_assistant_message=message,
            stop_hook_active=False,
        )
        return event

    def test_a_reply_naming_lines_or_a_question_for_every_item_passes(self):
        # Given: a generator whose reply names lines for one item and a question for the other
        # When: it ends
        # Then: it ends
        claim = {"checklist": GOOD["checklist"], "item": "F-1", "lines": ["README.md:1"]}
        reply = {"items": [claim, WAITS], "questions": [QUESTION]}
        self.passes(subagentstop, self.reply(json.dumps(reply)))

    def test_a_reply_out_of_its_form_stops(self):
        # Given: a generator whose reply is prose, or leaves an item out
        # When: it ends
        # Then: it is kept going, told what its reply lacks
        claim = {"checklist": GOOD["checklist"], "item": "F-1", "lines": ["README.md:1"]}
        for reply, said in (
            ("Done.", '{"items": [...], "questions": [...]}'),
            (json.dumps({"items": [claim], "questions": []}), "B-1"),
        ):
            with self.subTest(reply=reply):
                self.stops(subagentstop, self.reply(reply), said)

    def test_a_good_in_the_generators_reply_stops(self):
        # Given: a generator whose reply judges an item Good, which is not its to judge
        # When: it ends
        # Then: it is kept going, told the shapes its items take
        reply = {"items": [GOOD, WAITS], "questions": [QUESTION]}
        self.stops(subagentstop, self.reply(json.dumps(reply)), '"lines" or "question"')

    def test_a_generator_of_no_run_going_ends(self):
        # Given: a generator whose run has returned, or was never started
        # When: it ends with a reply out of its form
        # Then: it ends, as no run waits on its reply
        path = self.given_prompt(ID, json.dumps({"run": "none.json"}))
        event = self.event(
            "SubagentStop", "turn:generator", agent_transcript_path=path, last_assistant_message="x"
        )
        self.passes(subagentstop, event)


class TestReturned(HookTest):
    def end(self):
        path = self.given_prompt(ID, json.dumps(CALL))
        return self.event(
            "SubagentStop", "turn:up", agent_transcript_path=path, stop_hook_active=False
        )

    def test_an_orchestrator_ending_with_its_run_going_stops(self):
        # Given: a run started and not returned
        # When: the orchestrator ends
        # Then: it is kept going, told to record its reading until the run returns
        self.started()
        self.stops(subagentstop, self.end(), "turn.py read")

    def test_an_orchestrator_ending_after_its_run_returned_passes(self):
        # Given: a run whose result is written
        # When: the orchestrator ends
        # Then: it ends
        self.started()
        reading = {"items": [GOOD, WAITS], "questions": [QUESTION]}
        self.turn("read", CALL["result"], stdin=json.dumps(reading))
        self.passes(subagentstop, self.end())

    def test_an_orchestrator_whose_call_was_refused_ends(self):
        # Given: an orchestrator whose call never started a run
        # When: it ends
        # Then: it ends
        self.passes(subagentstop, self.end())

    def test_other_agents_end(self):
        # Given: an agent that is not turn's
        # When: it ends
        # Then: it ends
        self.passes(subagentstop, self.event("SubagentStop", "Explore"))


class TestWrites(HookTest):
    def setUp(self):
        super().setUp()
        self.given_prompt(ID, self.started())

    def test_the_generator_writing_the_work_passes(self):
        # Given: a generator of a run
        # When: it writes or edits the work
        # Then: it goes through
        for tool in ("Write", "Edit"):
            with self.subTest(tool=tool):
                event = self.tool("turn:generator", tool, file_path=f"{self.repo}/README.md")
                self.passes(pretooluse, event)

    def test_the_generator_writing_elsewhere_stops(self):
        # Given: a generator of a run
        # When: it writes a file that is not the work, such as a checklist
        # Then: it is stopped, naming where it may write
        event = self.tool("turn:generator", "Write", file_path="checklists/readme.md")
        self.stops(pretooluse, event, "README.md")

    def test_a_generator_of_no_run_going_writes(self):
        # Given: a generator whose run has returned
        # When: it writes a file
        # Then: it goes through, as no run bounds it
        self.given_prompt(ID, json.dumps({"run": "none.json"}))
        self.passes(pretooluse, self.tool("turn:generator", "Write", file_path="other.md"))

    def test_a_role_committing_or_pushing_stops(self):
        # Given: any of turn's agents
        # When: it commits or pushes
        # Then: it is stopped, saying the caller keeps the work in git
        for command in ("git commit -m x", "git add . && git push"):
            with self.subTest(command=command):
                self.stops(pretooluse, self.tool("turn:up", "Bash", command=command), "caller")

    def test_other_commands_pass(self):
        # Given: one of turn's agents
        # When: it runs a command that neither commits nor pushes
        # Then: it goes through
        self.passes(pretooluse, self.tool("turn:up", "Bash", command="git diff"))


class TestReads(HookTest):
    def setUp(self):
        super().setUp()
        self.given_prompt(ID, self.started())
        self.write("secret/notes.md", "x\n")

    def test_reading_what_the_run_was_given_passes(self):
        # Given: a generator of a run
        # When: it reads the CCS, a file the CCS names, the work, or turn's own files
        # Then: it goes through
        for path in (
            CALL["ccs"],
            f"{self.repo}/notes/readme.decisions.md",
            "README.md",
            f"{TURN}/agents/generator.md",
        ):
            with self.subTest(path=path):
                self.passes(pretooluse, self.tool("turn:generator", "Read", file_path=path))

    def test_reading_anything_else_stops(self):
        # Given: a generator of a run
        # When: it reads a file, or searches a folder, the run was not given
        # Then: it is stopped, naming what it may read
        self.stops(
            pretooluse,
            self.tool("turn:generator", "Read", file_path="secret/notes.md"),
            "notes/readme.decisions.md",
        )
        self.stops(pretooluse, self.tool("turn:generator", "Grep", pattern="x", path="secret"))

    def test_a_command_naming_only_what_the_run_was_given_passes(self):
        # Given: a generator of a run
        # When: it runs a command naming the work and a file the CCS names, from the repository's
        # top, or one whose quoting does not close
        # Then: it goes through
        for command in (
            f"cd {self.repo} && cat -n README.md notes/readme.decisions.md",
            "python3 - <<'EOF'\nprint('x)\nEOF",
        ):
            with self.subTest(command=command):
                self.passes(pretooluse, self.tool("turn:generator", "Bash", command=command))

    def test_the_orchestrator_recording_its_reading_passes(self):
        # Given: an orchestrator whose run is going
        # When: it records its reading with the script, naming where the result goes
        # Then: it goes through
        self.given_prompt(ID, json.dumps(CALL))
        command = f"python3 {TURN}/scripts/turn.py read {CALL['result']} <<'EOF'\n{{}}\nEOF"
        self.passes(pretooluse, self.tool("turn:up", "Bash", command=command))

    def test_a_command_naming_a_file_the_run_was_not_given_stops(self):
        # Given: a generator of a run
        # When: it runs a command that reads a file of the repository the run was not given
        # Then: it is stopped, naming what it may read
        event = self.tool("turn:generator", "Bash", command="cat README.md secret/notes.md")
        self.stops(pretooluse, event, "notes/readme.decisions.md")

    def test_a_search_without_a_path_stops(self):
        # Given: a generator of a run
        # When: it searches with no path, which searches the whole repository
        # Then: it is stopped
        self.stops(pretooluse, self.tool("turn:generator", "Glob", pattern="**/*.md"))

    def test_the_orchestrator_reading_its_call_before_starting_passes(self):
        # Given: an orchestrator whose run is not started yet
        # When: it reads the CCS
        # Then: it goes through, as no run bounds it yet
        self.given_prompt(ID, json.dumps(dict(CALL, result="later.json")))
        self.passes(pretooluse, self.tool("turn:up", "Read", file_path="secret/notes.md"))

    def test_an_agent_whose_prompt_names_no_run_reads_freely(self):
        # Given: one of turn's agents started with words, not JSON, or with no record of its start
        # When: it reads a file
        # Then: it goes through, as no run bounds it
        self.given_prompt(ID, "make the README")
        self.passes(pretooluse, self.tool("turn:generator", "Read", file_path="secret/notes.md"))
        os.remove(os.path.join(self.repo, "session", "subagents", f"agent-{ID}.jsonl"))
        self.passes(pretooluse, self.tool("turn:generator", "Read", file_path="secret/notes.md"))


class TestEntries(HookTest):
    def test_each_entry_runs_from_the_shell(self):
        # Given: Claude Code runs each entry file by its path
        # When: it hands it an event that concerns turn not at all
        # Then: it exits without stopping anything
        for name in ("pretooluse.py", "subagentstop.py"):
            with self.subTest(name=name):
                event = json.dumps(self.tool(None, "Bash", command="ls"))
                with (
                    mock.patch.object(sys, "stdin", io.StringIO(event)),
                    self.assertRaises(SystemExit) as end,
                ):
                    runpy.run_path(os.path.join(HOOKS, name), run_name="__main__")
                self.assertEqual(end.exception.code, 0)

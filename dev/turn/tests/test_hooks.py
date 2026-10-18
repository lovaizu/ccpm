import io
import json
import os
import runpy
import sys
from unittest import mock

from helpers import (
    CALL,
    EVALUATED,
    GOOD,
    GOT,
    HOOKS,
    ID,
    LEARNT,
    QUESTION,
    READ_GIVEN,
    SENT_BACK,
    TURN,
    WAITS,
    RepoTest,
    pretooluse,
    subagentstop,
)


class HookTest(RepoTest):
    """Each test hands a hook the event Claude Code would, in a session whose transcripts sit in
    the temporary repository."""

    def given_prompt(self, agent_id, prompt):
        return self.given_record(agent_id, prompt)

    def tool(self, agent_type, tool_name, **tool_input):
        return self.event("PreToolUse", agent_type, tool_name=tool_name, tool_input=tool_input)

    def stops(self, entry, event, *said):
        code, err = self.hook(entry, event)
        self.assertEqual(code, 2, err)
        for words in said:
            self.assertIn(words, err)

    def passes(self, entry, event):
        self.assertEqual(self.hook(entry, event), (0, ""))

    def first_user(self, **call):
        """A run whose first user is to be started next, and the prompt it is to be started with."""
        self.started(dict(CALL, **call))
        return self.next({"items": [GOOD, WAITS], "questions": [QUESTION]})["prompt"]


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


class TestRoleStart(HookTest):
    def role(self, agent_type, prompt):
        return self.tool("turn:up", "Agent", subagent_type=agent_type, prompt=prompt)

    def test_the_generator_started_with_the_prompt_the_script_gave_passes(self):
        # Given: a run started
        # When: the orchestrator starts the generator with the prompt the script printed
        # Then: it goes through
        self.passes(pretooluse, self.role("turn:generator", self.started()))

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
                self.stops(
                    pretooluse,
                    self.role("turn:generator", given),
                    "turn:generator with what turn.py printed last",
                )

    def test_the_first_user_started_with_the_prompt_the_script_gave_passes(self):
        # Given: a run whose findings are recorded
        # When: the orchestrator starts the first user with the prompt the script printed
        # Then: it goes through
        self.passes(pretooluse, self.role("turn:first-user", self.first_user()))

    def test_a_role_started_before_its_turn_stops(self):
        # Given: a run whose generator is to be started next
        # When: the orchestrator starts the first user or the evaluator with the generator's prompt
        # Then: it is stopped, naming the generator as the one to start
        prompt = self.started()
        for agent_type in ("turn:first-user", "turn:evaluator"):
            with self.subTest(agent_type=agent_type):
                self.stops(
                    pretooluse,
                    self.role(agent_type, prompt),
                    "turn:generator with what turn.py printed last",
                )


class TestReplies(HookTest):
    def reply(self, message):
        path = self.given_record(ID, self.started(), *READ_GIVEN)
        event = self.event(
            "SubagentStop",
            "turn:generator",
            agent_transcript_path=path,
            last_assistant_message=message,
            stop_hook_active=False,
        )
        return event

    def test_a_first_users_reply_of_what_it_got_passes(self):
        # Given: a first user whose reply says what it got for one item and where
        # When: it ends
        # Then: it ends
        self.assertEqual(
            self.replied("turn:first-user", self.first_user(), {"items": [GOT]}), (0, "")
        )

    def test_a_learners_reply_leaving_an_item_out_stops(self):
        # Given: a learner of a run whose first reading left an item without Good
        # When: it ends with what makes the Good of one item alone
        # Then: it is kept going, told the item it left out
        self.started()
        self.through(dict(EVALUATED, item="B-1"))
        prompt = self.next({"items": [GOOD, SENT_BACK], "questions": []})["prompt"]
        code, err = self.replied("turn:learner", prompt, {"items": LEARNT[:1]})
        self.assertEqual(code, 2)
        self.assertIn("B-1 is left out", err)

    def test_a_learner_says_nothing_of_an_item_waiting_on_a_question(self):
        # Given: a learner of a run whose first reading left one item without Good and one
        # waiting on the user's answer
        # When: it ends with what makes the Good of the item without Good alone, or with the
        # item waiting on the answer as well
        # Then: the first ends, and the second is kept going, told that item is not its to judge
        self.started()
        self.through()
        unmet = dict(SENT_BACK, item="F-1")
        prompt = self.next({"items": [unmet], "questions": []})["prompt"]
        learnt = {"checklist": unmet["checklist"], "item": "F-1", "learnt": "the name first"}
        self.assertEqual(self.replied("turn:learner", prompt, {"items": [learnt]}), (0, ""))
        waits = dict(learnt, item="B-1")
        code, err = self.replied("turn:learner", prompt, {"items": [learnt, waits]})
        self.assertEqual(code, 2)
        self.assertIn("B-1 is not an item judged here", err)

    def test_a_readers_reply_out_of_its_form_stops(self):
        # Given: a first user replying with prose or with a Good, which is the evaluator's to
        # give, and an evaluator replying with what it got, which is the first user's to say
        # When: it ends
        # Then: it is kept going, told the form it gives
        prompt = self.first_user()
        for agent_type, reply, said in (
            ("turn:first-user", "I read it.", '{"items": [...]}'),
            ("turn:first-user", {"items": [EVALUATED]}, '"got" with "lines"'),
        ):
            with self.subTest(reply=reply):
                code, err = self.replied(agent_type, prompt, reply)
                self.assertEqual(code, 2)
                self.assertIn(said, err)
        self.replied("turn:first-user", prompt, {"items": [GOT]})
        out = self.next()
        code, err = self.replied("turn:evaluator", out["prompt"], {"items": [GOT]})
        self.assertEqual(code, 2)
        self.assertIn('"good" with "lines"', err)

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
        self.stops(subagentstop, self.end(), "turn.py next")

    def test_an_orchestrator_ending_after_its_run_returned_passes(self):
        # Given: a run whose result is written
        # When: the orchestrator ends
        # Then: it ends
        self.started()
        self.through(EVALUATED)
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

    def test_any_other_of_turns_agents_writing_stops(self):
        # Given: the orchestrator and the first user of a run
        # When: either writes the work
        # Then: it is stopped, saying the generator alone writes the work
        self.given_prompt(ID, json.dumps(dict(CALL)))
        self.stops(pretooluse, self.tool("turn:up", "Edit", file_path="README.md"), "generator")
        self.given_prompt(ID, self.first_user())
        event = self.tool("turn:first-user", "Write", file_path="README.md")
        self.stops(pretooluse, event, "generator")

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

    def test_a_first_user_reading_what_the_receiver_has_passes(self):
        # Given: a first user of a run whose receiver opens a page with the work
        # When: it reads the work, the page or the checklist
        # Then: it goes through
        self.given_prompt(ID, self.first_user(kind=dict(CALL["kind"], opens="page")))
        for path in ("README.md", "docs/start.md", "checklists/readme.md"):
            with self.subTest(path=path):
                self.passes(pretooluse, self.tool("turn:first-user", "Read", file_path=path))

    def test_a_first_user_reading_what_the_receiver_does_not_have_stops(self):
        # Given: a first user of a run
        # When: it reads the CCS or the decisions, which the receiver does not have
        # Then: it is stopped, naming what it may read
        self.given_prompt(ID, self.first_user())
        for path in (CALL["ccs"], "notes/readme.decisions.md"):
            with self.subTest(path=path):
                event = self.tool("turn:first-user", "Read", file_path=path)
                self.stops(pretooluse, event, "README.md, checklists/readme.md")

    def test_a_learner_reads_the_records_of_its_run_alone(self):
        # Given: a learner of a run whose first reading left an item without Good
        # When: it reads a role's record, or the work
        # Then: the record goes through, and the work is stopped, naming the records
        self.through(dict(EVALUATED, item="B-1"))
        prompt = self.next({"items": [GOOD, SENT_BACK], "questions": []})["prompt"]
        self.given_prompt(ID, prompt)
        record = json.loads(prompt)["records"][0]
        self.passes(pretooluse, self.tool("turn:learner", "Read", file_path=record))
        self.stops(pretooluse, self.tool("turn:learner", "Read", file_path="README.md"), record)

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
        self.given_record(ID, json.dumps(CALL), *READ_GIVEN)
        command = f"python3 {TURN}/scripts/turn.py next {CALL['result']} <<'EOF'\n{{}}\nEOF"
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


class TestWholeReads(HookTest):
    def setUp(self):
        super().setUp()
        self.generator_prompt = self.started()

    def read(self, path, **part):
        return ("Read", dict(file_path=path, **part))

    def generator_ends(self, *tool_uses):
        claim = {"checklist": GOOD["checklist"], "item": "F-1", "lines": ["README.md:1"]}
        reply = {"items": [claim, WAITS], "questions": [QUESTION]}
        path = self.given_record(ID, self.generator_prompt, *tool_uses)
        event = self.event(
            "SubagentStop",
            "turn:generator",
            agent_transcript_path=path,
            last_assistant_message=json.dumps(reply),
            stop_hook_active=False,
        )
        return self.hook(subagentstop, event)

    def test_a_reader_that_read_the_work_and_the_checklist_whole_ends(self):
        # Given: a first user that read the work and the checklist, each from top to end, one by
        # Read and one by a command
        # When: it ends with its reply
        # Then: it ends
        uses = (self.read("README.md"), ("Bash", {"command": "cat checklists/readme.md"}))
        reply = {"items": [GOT]}
        self.assertEqual(self.replied("turn:first-user", self.first_user(), reply, *uses), (0, ""))

    def test_a_reader_that_read_part_of_the_work_is_kept_going(self):
        # Given: a first user that read the checklist whole but only part of the work, by Read
        # from a line on, by a command printing some lines, by one cut short in a pipe, or by one
        # whose quoting does not close
        # When: it ends with its reply
        # Then: it is kept going, naming the work to read whole
        prompt = self.first_user()
        for part in (
            self.read("README.md", offset=2),
            ("Bash", {"command": "sed -n 1,2p README.md"}),
            ("Bash", {"command": "cat README.md | head -n 2"}),
            ("Bash", {"command": "cat 'README.md"}),
        ):
            with self.subTest(part=part):
                uses = (part, self.read("checklists/readme.md"))
                code, err = self.replied("turn:first-user", prompt, {"items": [GOT]}, *uses)
                self.assertEqual(code, 2)
                self.assertIn("read whole", err)
                self.assertIn("README.md", err)
                self.assertNotIn("checklists/readme.md", err)

    def test_a_generator_that_read_the_work_again_after_its_last_change_ends(self):
        # Given: a generator that read everything it was given, changed the work, and read the
        # work again from top to end
        # When: it ends with its reply
        # Then: it ends
        given = [self.read(p) for p in (CALL["ccs"], "notes/readme.decisions.md", "docs/start.md")]
        given.append(("Bash", {"command": "cat checklists/readme.md README.md"}))
        change = {"file_path": f"{self.repo}/README.md", "old_string": "a", "new_string": "c"}
        edit = ("Edit", change)
        self.assertEqual(self.generator_ends(*given, edit, self.read("README.md")), (0, ""))

    def test_a_generator_that_did_not_read_the_work_after_its_last_change_is_kept_going(self):
        # Given: a generator that read everything it was given, then changed the work and read
        # only part of it after
        # When: it ends with its reply
        # Then: it is kept going, naming the work to read whole
        given = [self.read(p) for p in (CALL["ccs"], "notes/readme.decisions.md", "docs/start.md")]
        given.append(("Bash", {"command": "cat checklists/readme.md README.md"}))
        edit = ("Write", {"file_path": "README.md", "content": "# csvtidy\n"})
        code, err = self.generator_ends(*given, edit, self.read("README.md", offset=30))
        self.assertEqual(code, 2)
        self.assertIn("README.md", err)

    def test_the_orchestrator_recording_a_reading_of_part_of_the_work_stops(self):
        # Given: an orchestrator that read what the run was given, started the generator, and
        # after it read only some lines of the work
        # When: it records its reading with the script
        # Then: it is stopped, naming the work to read whole; once it reads the work whole, it
        # goes through
        given = [
            self.read(p)
            for p in (CALL["ccs"], "README.md", "checklists/readme.md")
            + ("notes/readme.decisions.md", "docs/start.md")
        ]
        generator = ("Agent", {"subagent_type": "turn:generator", "prompt": self.generator_prompt})
        part = ("Bash", {"command": "sed -n '1,10p' README.md"})
        command = f"python3 {TURN}/scripts/turn.py next {CALL['result']} <<'EOF'\n{{}}\nEOF"
        self.given_record(ID, json.dumps(CALL), *given, generator, part)
        self.stops(pretooluse, self.tool("turn:up", "Bash", command=command), "README.md")
        self.given_record(ID, json.dumps(CALL), *given, generator, part, self.read("README.md"))
        self.passes(pretooluse, self.tool("turn:up", "Bash", command=command))

    def test_the_orchestrator_deciding_on_part_of_what_it_decides_from_stops(self):
        # Given: an orchestrator whose run waits on its decision, which saw the items to decide cut
        # short in a pipe or sent to a file, or did not read the work whole
        # When: it records its decision with the script
        # Then: it is stopped, naming what to read whole; once it saw the items as the script
        # printed them and read the work whole, it goes through
        self.through()
        shown = f"cd {self.repo} && python3 {TURN}/scripts/turn.py next {CALL['result']}"
        work = self.read("README.md")
        command = f"python3 {TURN}/scripts/turn.py next {CALL['result']} <<'EOF'\n{{}}\nEOF"
        for uses, said in (
            (
                (("Bash", {"command": shown + " | head -c 500"}), work),
                "see the items to decide whole",
            ),
            (
                (("Bash", {"command": shown + " > /tmp/d.json"}), work),
                "see the items to decide whole",
            ),
            ((("Bash", {"command": shown}), self.read("README.md", limit=5)), "README.md"),
        ):
            with self.subTest(uses=uses):
                self.given_record(ID, json.dumps(CALL), *uses)
                self.stops(pretooluse, self.tool("turn:up", "Bash", command=command), said)
        self.given_record(ID, json.dumps(CALL), work, ("Bash", {"command": shown}))
        self.passes(pretooluse, self.tool("turn:up", "Bash", command=command))

    def test_a_reader_of_no_run_going_ends_without_reading(self):
        # Given: a first user whose run has returned, or was never started
        # When: it ends having read nothing whole
        # Then: it ends, as no run waits on its reading
        prompt = json.dumps({"run": "none.json"})
        part = ("Read", {"file_path": "README.md", "offset": 2})
        self.assertEqual(self.replied("turn:first-user", prompt, {"items": [GOT]}, part), (0, ""))

    def test_the_orchestrator_going_on_after_a_role_needs_no_new_read(self):
        # Given: an orchestrator whose run waits on the first user, not on its own reading
        # When: it runs the script with input, having read nothing whole
        # Then: it goes through, as only a reading of the work rests on the work read whole
        self.first_user()
        self.given_record(ID, json.dumps(CALL))
        command = f"python3 {TURN}/scripts/turn.py next {CALL['result']} <<'EOF'\n{{}}\nEOF"
        self.passes(pretooluse, self.tool("turn:up", "Bash", command=command))

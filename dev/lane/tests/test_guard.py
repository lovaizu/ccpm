"""The guard: in the subagent its command names, and there alone, a call that drifts from a lane is
stopped and the subagent told `<plugin>: <sentence>`; a lane whose step no longer says its sentence
stops the call and says to have the plugin's lanes laid again with `lay.py write`."""

from __future__ import annotations

import contextlib
import io
import json
import os
import runpy
import sys
import time
import unittest
from collections.abc import Sequence
from unittest import mock

import helpers
from helpers import lanes

# hands_off of the README's proposal, on step 3: its step, the lane and what it takes.
HANDS_OFF = (3, "hands_off", ["git commit", "git push"])
# The sentence of start_with laid on step 1, taking the script it runs.
BEGIN = "First run `scripts/log.py`."
# The changelog written by the Write tool, as the record holds it.
CHANGE = helpers.writing("CHANGELOG.md")
# Who must fix what the plugin gives its lanes, laying them again, as the subagent is told to reply.
LAY_AGAIN = (
    "Stop here and reply that the maker of notes must lay its lanes again with `lay.py write`, so"
    " they match its steps."
)
# What the subagent and the user are told where step 3 no longer says the lane's sentence.
GONE = (
    "notes: lane cannot check hands_off on step 3 of changelog-writer: step 3 no longer says: Do"
    " not run `git commit` or `git push`. Stop here and reply that the maker of notes must lay its"
    " lanes again with `lay.py write`, so they match its steps."
)


class GuardTest(helpers.PluginTest):
    """A test of the guard on the lanes LAID, each its step, the lane and what it takes, laid on
    changelog-writer as `lay.py write` lays them."""

    LAID: tuple = (HANDS_OFF,)

    def setUp(self) -> None:
        super().setUp()
        self.lay(*self.LAID)

    def lay(self, *laid: tuple, values: str = "") -> None:
        """Lays the lanes on changelog-writer, each its step, the lane, what it takes and, where a
        fourth is given, the adapter of the port it reads: each lane's sentence put after its
        step's numbered line, and the lanes written into the plugin's hooks/lanes.json, each on its
        own step, with the values adapter where one is given; and `words`, the words a hook's
        command gives the guard, the subagent alone."""
        text = helpers.STEPS
        for number, lane, takes, *_ in laid:
            line = next(s for s in text.splitlines() if s.startswith(f"{number}. "))
            text = text.replace(line, f"{line} {lanes.sentence(lane, takes)}", 1)
        self.write(self.agent_file, text)
        steps = []
        for n, lane, t, *adapter in laid:
            named = {"adapter": adapter[0]} if adapter else {}
            steps.append({"step": n, "lanes": [{"lane": lane, "takes": t, **named}]})
        subagent = {"name": "changelog-writer", **({"adapter": values} if values else {})}
        subagents = [{**subagent, "steps": steps}]
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), {"subagents": subagents})
        self.words = (helpers.AGENT,)

    def guard(
        self,
        stream: str,
        words: Sequence[str] | None = None,
        entry: str = "pretooluse.py",
        plugin: str | None = None,
    ) -> tuple:
        """The event's entry, PreToolUse's where none is named, run as Claude Code runs it, on the
        stream, for the plugin at the folder given, or `notes`, with the words given, or those of
        the lanes laid, in this process so that the coverage of the test run counts it; whom its
        answer tells and what: "told" and what the subagent is told, its tool call denied at
        PreToolUse or kept going at SubagentStop, as Claude Code reads its JSON output on exit 0;
        "user" and what the user is told, the call or the end let go on; or "" and "" where it
        answers nothing."""
        words = self.words if words is None else words
        script = os.path.join(helpers.CODE, entry)
        argv = mock.patch.object(sys, "argv", [script, *words])
        stdin = mock.patch.object(sys, "stdin", io.StringIO(stream))
        folder = self.plugin if plugin is None else plugin
        root = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": folder})
        out = io.StringIO()
        with argv, stdin, root, contextlib.redirect_stdout(out):
            runpy.run_path(script, run_name="__main__")
        return told(out.getvalue(), entry)


def told(out: str, entry: str) -> tuple:
    """Whom the guard's answer on stdout tells and what, as GuardTest.guard gives it, the subagent
    told only by the decision of the entry's event; "error" where the user is told the same as the
    subagent; "other" and the answer for any other."""
    if not out:
        return "", ""
    found = json.loads(out)
    user = found.pop("systemMessage", None)
    if not found:
        return "user", user
    if entry == "pretooluse.py":
        reason = found.get("hookSpecificOutput", {}).get("permissionDecisionReason")
        expected = helpers.denied(reason)
    else:
        reason = found.get("reason")
        expected = {"decision": "block", "reason": reason}
    if found != expected or user not in (None, reason):
        return "other", {**found, "systemMessage": user}
    return ("told" if user is None else "error"), reason


class TestStop(GuardTest):
    def test_a_command_the_step_says_not_to_run_is_stopped_with_its_sentence(self):
        # Given: hands_off on step 3 of changelog-writer
        # When: changelog-writer runs `git commit -m notes`
        # Then: the call is stopped, and the subagent told the sentence headed by the plugin
        self.assertEqual(
            self.guard(self.stream("git commit -m notes")),
            ("told", "notes: Do not run `git commit` or `git push`."),
        )

    def test_a_call_the_sentence_allows_is_let_through(self):
        # Given: hands_off on step 3 of changelog-writer
        # When: changelog-writer runs `git status`
        # Then: the call goes on, nothing said
        self.assertEqual(self.guard(self.stream("git status")), ("", ""))

    def test_a_step_no_longer_saying_the_sentence_stops_the_call(self):
        # Given: step 3 changed by the building AI since the lane was laid
        self.write(self.agent_file, helpers.STEPS)
        # When: changelog-writer makes a call the hook watches, even one the lane allows
        # Then: it is an error: the call is stopped, saying to have the lanes laid again, and the
        # user told the same
        self.assertEqual(self.guard(self.stream("git status")), ("error", GONE))

    def test_with_no_record_found_a_lane_resting_on_it_is_an_error_before_its_check(self):
        for lane, takes, entry in (
            ("start_with", ["scripts/log.py"], "pretooluse.py"),
            ("read_whole", ["notes.md"], "pretooluse.py"),
            ("as_printed", ["scripts/log.py"], "pretooluse.py"),
            ("follow_next", ["scripts/log.py"], "pretooluse.py"),
            ("wait_for", ["OK", "git push"], "pretooluse.py"),
            ("as_printed", ["scripts/log.py"], "subagentstop.py"),
            ("follow_next", ["scripts/log.py"], "subagentstop.py"),
            ("end_when", ["CHANGELOG.md"], "subagentstop.py"),
            ("every_item", ["notes.md"], "subagentstop.py"),
        ):
            with self.subTest(lane=lane, entry=entry):
                # Given: the lane laid on step 3, and no record of changelog-writer
                self.lay((3, lane, takes))
                # When: changelog-writer writes and pushes, or is about to end
                pre = self.called("Bash", {"command": "echo x > notes.md && git push"})
                event = pre if entry == "pretooluse.py" else self.stopped("Done.")
                # Then: it is an error, saying the record is not found, its check never run
                with mock.patch.object(lanes.LANES[lane], "drifts") as drifts:
                    whom, said = self.guard(json.dumps(event), entry=entry)
                self.assertEqual(whom, "error")
                self.assertIn(f"{lane} on step 3 of changelog-writer: its record is not", said)
                drifts.assert_not_called()

    def test_the_subagents_record_is_read_once_for_every_lane(self):
        # Given: hands_off and start_with laid on changelog-writer, and its record
        self.record([helpers.bash("ls")])
        self.lay(HANDS_OFF, (1, "start_with", ["ls"]))
        entries = mock.patch.object(helpers.record, "entries", wraps=helpers.record.entries)
        # When: changelog-writer makes a call
        with entries as read:
            self.guard(self.stream("git status"))
        # Then: its record is read once
        self.assertEqual(read.call_count, 1)


class TestStartWith(GuardTest):
    LAID = ((1, "start_with", ["scripts/log.py"]),)

    def started(self, command: str) -> tuple:
        """What the guard does on a Bash call of the command, start_with laid on step 1."""
        return self.guard(self.stream(command))

    def test_a_first_call_running_anything_but_the_script_is_stopped_with_its_sentence(self):
        # Given: start_with on step 1 of changelog-writer, its record holding no call yet
        self.record([])
        # When: changelog-writer's first call runs something else
        # Then: the call is stopped, and the subagent told the sentence headed by the plugin
        self.assertEqual(self.started("ls"), ("told", f"notes: {BEGIN}"))

    def test_the_script_run_first_goes_on(self):
        # Given: start_with on step 1 of changelog-writer, its record holding no call yet
        self.record([])
        # When: its first call runs the script
        # Then: the call goes on, nothing said
        self.assertEqual(self.started(f"python3 {self.plugin}/scripts/log.py"), ("", ""))

    def test_a_call_after_the_script_ran_goes_on(self):
        # Given: start_with on step 1 of changelog-writer, its record holding the script run
        self.record([helpers.bash(f"python3 {self.plugin}/scripts/log.py")])
        # When: it makes any other call
        # Then: the call goes on, nothing said
        self.assertEqual(self.started("ls"), ("", ""))


class TestEnd(GuardTest):
    """The lanes held as the subagent is about to end: test_after on step 3, end_when on step 4."""

    TESTED = "After changing `CHANGELOG.md`, pass `python3 check.py`."
    ENDED = "End only once `CHANGELOG.md` is made."
    LAID = (
        (3, "test_after", ["CHANGELOG.md", "python3 check.py"]),
        (4, "end_when", ["CHANGELOG.md"]),
    )

    def setUp(self) -> None:
        super().setUp()
        # The changelog there, as a write of it in the record leaves it.
        self.write(os.path.join(self.base, "CHANGELOG.md"), "- Added: lanes\n")

    def ended(self, calls, active=False, agent_type=helpers.AGENT):
        """The SubagentStop entry run on the lanes, the subagent about to end after the calls."""
        if calls is not None:
            self.record(calls)
        stream = json.dumps(self.stopped("Done.", active, agent_type))
        return self.guard(stream, entry="subagentstop.py")

    def test_ending_with_a_change_not_passed_keeps_it_going_with_the_sentence(self):
        # Given: the changelog written and the check never run
        # When: changelog-writer is about to end
        # Then: it is kept going and told test_after's sentence headed by the plugin
        self.assertEqual(self.ended([CHANGE]), ("told", f"notes: {self.TESTED}"))

    def test_ending_with_the_change_passed_and_the_output_made_ends(self):
        # Given: the changelog written, then the check run with no error
        # When: changelog-writer is about to end
        # Then: it ends, nothing said
        self.assertEqual(self.ended([CHANGE, helpers.bash("python3 check.py")]), ("", ""))

    def test_each_lane_not_kept_is_told(self):
        # Given: nothing written, the changelog there from before
        # When: changelog-writer is about to end
        # Then: it is told end_when's sentence alone, as no change waits on the check
        self.assertEqual(self.ended([]), ("told", f"notes: {self.ENDED}"))

    def test_a_command_writing_the_output_that_a_hook_stopped_is_no_change(self):
        # Given: a command writing the changelog, stopped by a hook, so it never ran
        stopped = helpers.Failed("PreToolUse:Bash hook error: [python3 x.py]: notes: Write it.")
        calls = [("Bash", {"command": "echo x > CHANGELOG.md"}, stopped)]
        # When: changelog-writer is about to end
        # Then: it is not told test_after's sentence, as no change waits on the check
        self.assertEqual(self.ended(calls), ("told", f"notes: {self.ENDED}"))

    def test_told_and_answering_in_words_alone_ends(self):
        # Given: a change not passed, told before, and answered with words alone since
        # When: changelog-writer, kept going by the stop hook, is about to end again
        # Then: it ends, nothing said, as it is told and never held for good
        self.assertEqual(self.ended([CHANGE, "told"], active=True), ("", ""))

    def test_told_and_working_since_is_told_again(self):
        # Given: a change not passed, told before, and the check run since, failing
        calls = [CHANGE, "told", helpers.failing("python3 check.py")]
        # When: changelog-writer, kept going by the stop hook, is about to end again
        # Then: it is told again
        self.assertEqual(self.ended(calls, active=True), ("told", f"notes: {self.TESTED}"))

    def test_with_no_record_found_it_is_kept_going_once_with_the_error(self):
        for active, whom in ((False, "error"), (True, "user")):
            with self.subTest(active=active):
                # Given: no record of what changelog-writer did, kept going by a stop hook before
                # or not
                # When: it is about to end
                found, said = self.ended(None, active=active)
                # Then: the first time it is kept going, told the error and who must fix it, the
                # user told too; once kept going, the user alone is told, and it ends
                self.assertEqual(found, whom)
                self.assertIn("test_after on step 3 of changelog-writer: its record is not", said)
                self.assertIn("Claude Code must be updated", said)

    def test_another_agent_ends(self):
        # Given: a change not passed
        # When: another agent is about to end
        # Then: it ends, nothing said
        self.assertEqual(self.ended([CHANGE], agent_type="notes:other"), ("", ""))

    def test_a_step_no_longer_saying_the_sentence_is_told_so(self):
        # Given: step 3 changed by the building AI since the lane was laid
        self.write(self.agent_file, helpers.STEPS)
        # When: changelog-writer is about to end
        whom, said = self.ended([CHANGE])
        # Then: it is an error, telling it to reply that the lanes must be laid again
        self.assertEqual(whom, "error")
        self.assertTrue(said.endswith(LAY_AGAIN), said)

    def test_a_step_no_longer_saying_the_sentence_answered_in_words_alone_ends(self):
        # Given: step 3 changed since the lane was laid, told so, and answered with words alone
        self.write(self.agent_file, helpers.STEPS)
        # When: changelog-writer, kept going by the stop hook, is about to end again
        # Then: it ends, nothing said, as it is told and never held for good
        self.assertEqual(self.ended([CHANGE, "told"], active=True), ("", ""))

    def test_every_item_is_told_on_an_item_unanswered(self):
        # Given: every_item on step 1, taking a review of the item B-1, and a reply not naming it
        self.lay((1, "every_item", ["review.md"]))
        self.write(os.path.join(self.base, "review.md"), "- B-1: fix it\n")
        self.record([])
        # When: changelog-writer is about to end
        stream = json.dumps(self.stopped("Done."))
        # Then: it is kept going and told the sentence
        expected = ("told", "notes: Answer every item of `review.md`.")
        self.assertEqual(self.guard(stream, entry="subagentstop.py"), expected)


class TestRunValues(GuardTest):
    """Lanes taking a value given for each run, `{work}`, from the JSON the subagent starts from."""

    # The run's JSON, as the subagent's prompt or a script's print gives it, naming the work and a
    # file the lane does not take.
    RUN = '{"work": ["a.md", "b.md"], "has": "h.md"}'
    TOLD = "notes: Write only `{work}`.\n`{work}` is `a.md`, `b.md`."
    LAID = ((3, "write_only", ["{work}"]),)

    def wrote(self, path: str) -> tuple:
        """The guard on a Write of the path."""
        event = self.called("Write", {"file_path": path, "content": "x"})
        return self.guard(json.dumps(event))

    def test_a_write_of_a_file_the_runs_value_does_not_name_is_told_with_the_value(self):
        # Given: write_only taking `{work}`, the prompt naming the work
        self.record([], self.RUN)
        # When: changelog-writer writes another file
        # Then: it is stopped, told the sentence as its step says it, the value on the next line
        self.assertEqual(self.wrote("c.md"), ("told", self.TOLD))

    def test_a_write_of_a_file_the_runs_value_names_goes_on(self):
        # Given: write_only taking `{work}`, the prompt naming the work
        self.record([], self.RUN)
        # When: changelog-writer writes a file of the work
        # Then: it goes on, nothing said
        self.assertEqual(self.wrote("b.md"), ("", ""))

    def test_a_value_not_given_or_given_empty_is_an_error(self):
        for prompt, how in (
            (helpers.PROMPT, "not given"),
            ('{"has": "a.md"}', "not given"),
            ('{"work": 1}', "not given"),
            ('{"work": []}', "given empty"),
            ('{"work": ""}', "given empty"),
        ):
            with self.subTest(prompt=prompt):
                # Given: a prompt of words, of JSON naming no work, naming it by no text, by an
                # empty list, or by an empty text
                self.record([], prompt)
                # When: changelog-writer writes any file
                # Then: it is an error, saying so and that the plugin's maker must fix it
                told = (
                    "notes: lane cannot check write_only on step 3 of changelog-writer: `{work}`"
                    f" is {how} in what changelog-writer started from. Stop here and reply that"
                    " the maker of notes must fix it."
                )
                self.assertEqual(self.wrote("c.md"), ("error", told))

    def test_a_value_given_as_null_lets_the_call_through_nothing_told(self):
        for laid, prompt in (
            (self.LAID, '{"work": null}'),
            (((3, "write_only", ["{work}", "{notes}"]),), '{"work": null, "notes": "n.md"}'),
        ):
            with self.subTest(laid=laid):
                # Given: write_only taking `{work}`, or `{work}` and `{notes}`, the prompt giving
                # the work as null, the caller saying there is none
                self.lay(*laid)
                self.record([], prompt)
                # When: changelog-writer writes any file
                # Then: it goes on, nothing said, the lane resting on this run
                self.assertEqual(self.wrote("c.md"), ("", ""))

    def test_a_value_given_as_null_lets_the_end_through_nothing_told(self):
        # Given: end_when taking `{work}` on step 4, the prompt giving the work as null, none made
        self.lay((4, "end_when", ["{work}"]))
        self.record([], '{"work": null}')
        # When: changelog-writer is about to end
        stream = json.dumps(self.stopped("Done."))
        # Then: it ends, nothing said, the lane resting on this run
        self.assertEqual(self.guard(stream, entry="subagentstop.py"), ("", ""))

    def test_with_no_record_found_it_is_an_error(self):
        # Given: no record of what changelog-writer was given
        # When: it writes any file
        whom, said = self.wrote("c.md")
        # Then: it is an error, saying the record is not found and who must fix it
        self.assertEqual(whom, "error")
        self.assertIn("write_only on step 3 of changelog-writer: its record is not found", said)

    def test_a_lane_taking_a_value_is_held_once_the_script_start_with_takes_has_run(self):
        # Given: start_with laid on step 1, taking `scripts/given.py`, which gives the work, not
        # yet run, the prompt naming no work
        self.lay((1, "start_with", ["scripts/given.py"]), *self.LAID)
        self.record([])
        # When: changelog-writer runs the script
        event = self.event(f"python3 {self.plugin}/scripts/given.py")
        # Then: it goes on, write_only not yet held, as the value comes with what the script prints
        self.assertEqual(self.guard(json.dumps(event)), ("", ""))

    def test_a_script_start_with_takes_gives_the_value_over_the_prompt(self):
        # Given: start_with laid on step 1, taking `scripts/given.py`, which printed the work
        # after the prompt named another
        self.lay((1, "start_with", ["scripts/given.py"]), *self.LAID)
        run = ("Bash", {"command": f"python3 {self.plugin}/scripts/given.py"}, '{"work": "c.md"}')
        self.record([run], self.RUN)
        # When: changelog-writer writes the file the script named, then one the prompt named
        # Then: the first goes on, and the second is told with the script's value
        self.assertEqual(self.wrote("c.md"), ("", ""))
        told = "notes: Write only `{work}`.\n`{work}` is `c.md`."
        self.assertEqual(self.wrote("a.md"), ("told", told))

    def test_lanes_json_is_read_once_on_an_event(self):
        # Given: start_with laid on step 1, run, and write_only taking `{work}`, read with the
        # values the script printed by the subagent's adapter
        given = 'print(\'{"values": {"work": ["c.md"]}}\')\n'
        self.write(os.path.join(self.plugin, "hooks", "adapters", "values-run.py"), given)
        start = (1, "start_with", ["scripts/given.py"])
        self.lay(start, *self.LAID, values="hooks/adapters/values-run.py")
        run = ("Bash", {"command": f"python3 {self.plugin}/scripts/given.py"}, "{}")
        self.record([run], self.RUN)
        laid = mock.patch.object(helpers.hooks_file, "laid", wraps=helpers.hooks_file.laid)
        # When: changelog-writer writes a file
        with laid as read:
            found = self.wrote("a.md")
        # Then: hooks/lanes.json is read once for every lane, the values and the scripts run first
        self.assertEqual(found, ("told", "notes: Write only `{work}`.\n`{work}` is `c.md`."))
        self.assertEqual(read.call_count, 1)

    def test_an_output_of_a_list_is_held_to_its_form_one_by_one_the_point_told_last(self):
        # Given: in_form taking `{work}` and a form, the prompt naming two JSON outputs
        form = "${CLAUDE_PLUGIN_ROOT}/forms/entry.json"
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), {"type": "object"})
        sentence = f"Write `{{work}}` in the form of `{form}`."
        self.lay((3, "in_form", ["{work}", form]))
        self.record([], '{"work": ["a.json", "b.json"]}')
        # When: changelog-writer writes the second output out of the form
        event = self.called("Write", {"file_path": "b.json", "content": "[]"})
        said = self.guard(json.dumps(event))
        # Then: it is told the sentence, the value, then the point it is out by
        expanded = sentence.replace("${CLAUDE_PLUGIN_ROOT}", self.plugin)
        value = "`{work}` is `a.json`, `b.json`."
        self.assertEqual(
            said, ("told", f"notes: {expanded}\n{value}\n$: expected an object, found []")
        )

    def test_a_lane_held_at_the_end_takes_the_value_too(self):
        # Given: end_when taking `{work}` on step 4, the prompt naming the work, none made
        ended = "End only once `{work}` is made."
        self.lay((4, "end_when", ["{work}"]))
        self.record([], self.RUN)
        # When: changelog-writer is about to end
        stream = json.dumps(self.stopped("Done."))
        said = self.guard(stream, entry="subagentstop.py")
        # Then: it is kept going, told the sentence and the value
        self.assertEqual(said, ("told", f"notes: {ended}\n`{{work}}` is `a.md`, `b.md`."))


# An adapter of the items port reading a checklist's items as its headings, `### <ID>: <title>`, and
# one of the values port giving the work as the prompt names it in words, `work: <file>`.
HEADINGS = """import json, re, sys
given = json.load(sys.stdin)
print(json.dumps({"items": re.findall(r"^### ([A-Z]+-[0-9]+):", given["text"], re.M)}))
"""
WORDS = """import json, re, sys
given = json.load(sys.stdin)
found = [m for t in given["texts"] for m in re.findall(r"^work: (\\S+)$", t, re.M)]
print(json.dumps({"values": {"work": found} if found else {}}))
"""


class TestAdapters(GuardTest):
    """Lanes reading a plugin's text at a port by the plugin's adapter, named in hooks/lanes.json,
    the hook's time counted from the test's start, as from the guard's in a hook."""

    LAID = ()

    def setUp(self) -> None:
        super().setUp()
        start = mock.patch.object(helpers.ports, "START", time.monotonic())
        start.start()
        self.addCleanup(start.stop)

    def adapter(self, name: str, text: str) -> str:
        """Writes the adapter of the name into the plugin's hooks/adapters/; its path in the
        plugin."""
        path = f"hooks/adapters/{name}"
        self.write(os.path.join(self.plugin, path), text)
        return path

    def ending(self) -> tuple:
        """The guard as changelog-writer is about to end, having made no call."""
        self.record([])
        return self.guard(json.dumps(self.stopped("Done.")), entry="subagentstop.py")

    def test_every_item_reads_the_items_by_the_plugins_adapter(self):
        # Given: every_item on step 1 taking a checklist of headings, read by an adapter
        path = self.adapter("items-headings.py", HEADINGS)
        self.lay((1, "every_item", ["list.md"], path))
        self.write(os.path.join(self.base, "list.md"), "### B-1: the step\n### B-2: the hook\n")
        # When: changelog-writer is about to end with a reply naming B-1 alone
        self.record([])
        stream = json.dumps(self.stopped("B-1 is done."))
        # Then: it is told the sentence, as B-2 is unanswered
        expected = ("told", "notes: Answer every item of `list.md`.")
        self.assertEqual(self.guard(stream, entry="subagentstop.py"), expected)

    def test_the_runs_values_are_read_by_the_subagents_adapter(self):
        # Given: write_only taking `{work}`, the values read by an adapter, the prompt naming the
        # work in words
        path = self.adapter("values-words.py", WORDS)
        self.lay((3, "write_only", ["{work}"]), values=path)
        self.record([], "Do your steps.\nwork: a.md\n")
        # When: changelog-writer writes another file
        event = self.called("Write", {"file_path": "c.md", "content": "x"})
        # Then: it is told the sentence with the work the adapter gave
        told = "notes: Write only `{work}`.\n`{work}` is `a.md`."
        self.assertEqual(self.guard(json.dumps(event)), ("told", told))

    def test_an_adapter_failing_or_answering_out_of_its_port_is_an_error(self):
        for what, text, named in (
            ("exits 1", "import sys\nsys.exit('broken')\n", "exited 1: broken"),
            ("prints no JSON", "print('items')\n", "printed no JSON"),
            ("answers out", "print('{\"items\": 1}')\n", "out of the items port at $.items:"),
            ("is not there", None, "exited 2"),
        ):
            with self.subTest(what=what):
                # Given: every_item read by an adapter that fails, or is not there
                path = "hooks/adapters/items-broken.py"
                if text is not None:
                    self.adapter("items-broken.py", text)
                elif os.path.exists(os.path.join(self.plugin, path)):
                    os.remove(os.path.join(self.plugin, path))
                self.lay((1, "every_item", ["list.md"], path))
                self.write(os.path.join(self.base, "list.md"), "- B-1: x\n")
                # When: changelog-writer is about to end
                whom, said = self.ending()
                # Then: it is an error naming the adapter and what it did, which the plugin's
                # maker must fix
                self.assertEqual(whom, "error")
                expected = (
                    "notes: lane cannot check every_item on step 1 of changelog-writer: the"
                    f" adapter {path} "
                )
                self.assertTrue(said.startswith(expected), said)
                self.assertIn(named, said)
                self.assertTrue(
                    said.endswith(
                        "Stop here and reply that the maker of notes must fix the adapter and lay"
                        " its lanes again with `lay.py write`."
                    ),
                    said,
                )

    def test_an_adapter_answering_after_the_hooks_time_is_an_error(self):
        # Given: every_item read by an adapter that takes longer than the hook leaves it
        path = self.adapter("items-slow.py", "import time\ntime.sleep(5)\n")
        self.lay((1, "every_item", ["list.md"], path))
        self.write(os.path.join(self.base, "list.md"), "- B-1: x\n")
        # When: changelog-writer is about to end, the hook leaving the adapters a tenth of a second
        with mock.patch.object(helpers.ports, "TIME", 0.1):
            whom, said = self.ending()
        # Then: it is an error saying the adapter gave no answer in time
        self.assertEqual(whom, "error")
        self.assertIn("gave no answer within the 0.1 seconds the hook leaves it", said)

    def test_an_adapter_of_a_port_its_lane_does_not_read_is_an_error(self):
        for given in ((1, "hands_off", ["git push"], "hooks/adapters/items-x.py"),):
            with self.subTest(given=given):
                # Given: hooks/lanes.json naming an adapter for a lane that reads no port
                self.lay(given)
                # When: changelog-writer makes a call
                whom, said = self.guard(self.stream("git status"))
                # Then: it is an error, saying so and to have the lanes laid again
                self.assertEqual(whom, "error")
                self.assertIn("names an adapter for hands_off on step 1 of changelog-writer", said)
                self.assertTrue(said.endswith(LAY_AGAIN), said)


class TestOtherAgents(GuardTest):
    def test_the_same_call_in_another_subagent_or_the_main_conversation_goes_on(self):
        for agent_type in ("notes:other", "other:changelog-writer", "changelog-writer", None):
            with self.subTest(agent_type=agent_type):
                # Given: hands_off laid in changelog-writer
                # When: a call it would stop is made where another agent runs
                # Then: it goes on, nothing said
                stream = self.stream("git commit -m notes", agent_type)
                self.assertEqual(self.guard(stream), ("", ""))


class TestCommandLine(GuardTest):
    def test_a_command_line_not_naming_the_subagent_alone_is_an_error(self):
        for words in ([], ["changelog-writer"], [helpers.AGENT, "3:hands_off:git push"]):
            with self.subTest(words=words):
                # Given: a hook's command edited out of the form `lay.py write` writes, or as an
                # older lane wrote it
                # When: the guard is run by it
                whom, said = self.guard(self.stream("git commit"), words)
                # Then: it is an error, naming the words, and to have the lanes laid again, so the
                # hooks are written anew
                self.assertEqual(whom, "error")
                expected = (
                    f"lane: lane cannot check the lanes of this hook: its command gives"
                    f" `{' '.join(words)}`, not the subagent alone as <plugin>:<name>, as"
                    " `lay.py write` writes it. Stop here and reply that the plugin's maker must"
                    " lay its lanes again with `lay.py write`, to write its hooks anew."
                )
                self.assertEqual(said, expected)

    def test_lanes_json_not_as_lay_py_write_writes_it_is_an_error(self):
        path = os.path.join(self.plugin, "hooks", "lanes.json")
        for text, named in (("{", "holds no JSON"), ('{"subagents": []}', "lays no lanes in")):
            with self.subTest(text=text):
                # Given: hooks/lanes.json holding no JSON, or no lanes of the subagent
                self.write(path, text)
                # When: the guard is run on a call of the subagent
                whom, said = self.guard(self.stream("git commit"))
                # Then: it is an error, headed by the plugin, saying what is wrong and to have
                # the lanes laid again
                self.assertEqual(whom, "error")
                expected = (
                    "notes: lane cannot check the lanes of changelog-writer: hooks/lanes.json"
                )
                self.assertTrue(said.startswith(expected), said)
                self.assertIn(named, said)
                self.assertTrue(said.endswith(LAY_AGAIN), said)

    def test_lanes_json_is_read_only_on_an_event_of_its_subagent(self):
        # Given: hooks/lanes.json holding no JSON
        self.write(os.path.join(self.plugin, "hooks", "lanes.json"), "{")
        # When: the guard is run on a call of another agent
        # Then: it answers nothing
        self.assertEqual(self.guard(self.stream("git commit", "notes:other")), ("", ""))

    def test_the_lanes_of_the_subagent_held_on_another_event_are_left(self):
        # Given: hands_off, held on a tool call, laid on changelog-writer
        # When: changelog-writer is about to end
        stream = json.dumps(self.stopped("Done."))
        # Then: it ends, nothing said
        self.assertEqual(self.guard(stream, entry="subagentstop.py"), ("", ""))


if __name__ == "__main__":
    unittest.main()

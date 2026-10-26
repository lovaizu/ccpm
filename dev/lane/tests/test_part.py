"""A subagent whose file is its entry, its frontmatter and a body having it read its part first: its
steps are read from that part, the one file under the plugin's prompts/ the body names in
backticks, where the layer writes each lane's sentence; and the guard holds it to read the part
whole before anything else, telling it the entry's sentence that names the part."""

from __future__ import annotations

import json
import os
import unittest

import helpers
from helpers import entries, step
from laying import PRINTED, LayTest
from test_guard import GuardTest

# The sentence of changelog-writer's entry naming its part.
FIRST = (
    "Read `${CLAUDE_PLUGIN_ROOT}/prompts/writer.md` whole first, and take its steps on what you"
    " are given."
)
# changelog-writer's file as its entry: its frontmatter, and a body naming its part over a line
# break, between sentences of its own.
ENTRY = """---
name: changelog-writer
description: Writes the changelog of a project.
tools: Bash, Read, Write
---

You write the changelog. Read `${CLAUDE_PLUGIN_ROOT}/prompts/writer.md` whole first, and take its
steps on what you are given. Reply in `notes.md`.
"""
# The part: the subagent's file without its frontmatter, its Role and its Steps.
PART = helpers.STEPS.split("---\n", 2)[2]


class PartTest(helpers.PluginTest):
    """A test on the plugin `notes`, changelog-writer's file its entry and its steps in its part,
    prompts/writer.md."""

    def setUp(self) -> None:
        super().setUp()
        self.part = os.path.join(self.plugin, "prompts", "writer.md")
        self.write(self.agent_file, ENTRY)
        self.write(self.part, PART)

    def entry(self, body: str) -> None:
        """Writes changelog-writer's entry with the body after its frontmatter."""
        self.write(self.agent_file, "---\nname: changelog-writer\n---\n\n" + body)


class TestPartNamed(PartTest):
    def test_the_part_is_the_file_the_entry_names_with_its_sentence(self):
        # Given: changelog-writer's entry naming prompts/writer.md in a sentence over a line break
        # When: its part is looked for
        # Then: it is that file, with the sentence naming it, a line break read as a space
        self.assertEqual(step.part(self.plugin, "changelog-writer"), step.Part(self.part, FIRST))

    def test_a_sentence_alone_in_the_body_is_the_part_sentence(self):
        # Given: an entry whose body is the sentence alone, after a heading
        self.entry(f"## Role\n\n{FIRST}\n")
        # When: its part is looked for
        # Then: the sentence is the whole of it
        self.assertEqual(step.part(self.plugin, "changelog-writer"), step.Part(self.part, FIRST))

    def test_a_part_named_twice_is_told_by_the_first_sentence_naming_it(self):
        # Given: an entry naming its part in the sentence, then again in another
        again = "Its steps are those of `${CLAUDE_PLUGIN_ROOT}/prompts/writer.md`."
        self.entry(f"{FIRST}\n\n{again}\n")
        # When: its part is looked for
        # Then: it is told by the first sentence naming it
        self.assertEqual(step.part(self.plugin, "changelog-writer"), step.Part(self.part, FIRST))

    def test_an_entry_naming_no_part_under_prompts_names_none(self):
        for what, body in (
            ("no part", "You write the changelog.\n"),
            ("a file outside prompts/", "Read `${CLAUDE_PLUGIN_ROOT}/scripts/writer.md` first.\n"),
            ("a path out of prompts/", "Read `${CLAUDE_PLUGIN_ROOT}/prompts/../w.md` first.\n"),
            ("a path out of quotes", "Read ${CLAUDE_PLUGIN_ROOT}/prompts/writer.md first.\n"),
            (
                "two parts",
                (
                    "Read `${CLAUDE_PLUGIN_ROOT}/prompts/a.md` and"
                    " `${CLAUDE_PLUGIN_ROOT}/prompts/b.md` first.\n"
                ),
            ),
        ):
            with self.subTest(what=what):
                # Given: changelog-writer's entry naming no one part under prompts/ in backticks
                self.entry(body)
                # When: its part is looked for
                # Then: there is none
                self.assertIsNone(step.part(self.plugin, "changelog-writer"))

    def test_a_part_named_in_the_frontmatter_alone_is_none(self):
        # Given: an entry naming the part in its description alone
        description = "description: Reads `${CLAUDE_PLUGIN_ROOT}/prompts/writer.md`."
        self.write(self.agent_file, f"---\nname: changelog-writer\n{description}\n---\n\nWrite.\n")
        # When: its part is looked for
        # Then: there is none, as the body alone points to the part
        self.assertIsNone(step.part(self.plugin, "changelog-writer"))

    def test_a_subagent_no_entry_names_has_no_part(self):
        # Given: no entry naming the subagent
        # When: its part is looked for
        # Then: there is none
        self.assertIsNone(step.part(self.plugin, "other"))


class TestStepsFile(PartTest):
    def test_the_steps_are_read_from_the_part_the_entry_names(self):
        # Given: changelog-writer's entry naming its part
        # When: the file its steps are read from is looked for
        # Then: it is the part
        self.assertEqual(step.steps_file(self.plugin, "changelog-writer"), self.part)

    def test_the_steps_of_an_entry_naming_no_part_are_read_from_it(self):
        # Given: changelog-writer's file holding its steps, naming no part
        self.write(self.agent_file, helpers.STEPS)
        # When: the file its steps are read from is looked for
        # Then: it is the file itself, as before
        self.assertEqual(step.steps_file(self.plugin, "changelog-writer"), self.agent_file)

    def test_a_subagent_no_entry_names_has_no_steps_file(self):
        # Given: no entry naming the subagent
        # When: the file its steps are read from is looked for
        # Then: there is none
        self.assertIsNone(step.steps_file(self.plugin, "other"))

    def test_a_sentence_the_parts_step_says_holds(self):
        # Given: step 3 of the part saying a sentence the entry does not
        self.write(self.part, PART.replace("`CHANGELOG.md`.\n", "`CHANGELOG.md`. Be brief.\n"))
        # When: whether the step says it is asked
        # Then: it does
        self.assertTrue(step.holds(self.plugin, "changelog-writer", 3, "Be brief."))

    def test_a_part_not_there_holds_no_sentence(self):
        # Given: the part the entry names not there
        os.remove(self.part)
        # When: whether step 3 says its sentence is asked
        # Then: it does not
        self.assertFalse(step.holds(self.plugin, "changelog-writer", 3, "Write the new"))


class TestLaid(PartTest, LayTest):
    def test_the_print_shows_the_parts_step(self):
        # Given: the README's proposal on step 3 of changelog-writer, its steps in its part
        # When: it is printed
        # Then: the step is the part's, as it would read
        self.assertEqual(self.lay("print", self.proposal_file), (0, PRINTED))

    def test_the_sentence_is_written_into_the_part_and_the_entry_left_as_it_was(self):
        # Given: the README's proposal on step 3 of changelog-writer, its steps in its part
        # When: it is written
        code, said = self.lay("write", self.proposal_file)
        # Then: step 3 of the part says the sentence, the entry as it was, and the layer says so
        self.assertEqual(code, 0)
        self.assertIn("Wrote step 3 of changelog-writer into prompts/writer.md.\n", said)
        laid = PART.replace("`CHANGELOG.md`.\n", "`CHANGELOG.md`. " + helpers.SENTENCE + "\n")
        self.assertEqual(self.read(self.part), laid)
        self.assertEqual(self.read(self.agent_file), ENTRY)

    def test_a_part_not_there_stops_naming_it_before_anything_is_written(self):
        # Given: the part changelog-writer's entry names not there
        os.remove(self.part)
        # When: the proposal is written
        # Then: it stops, naming the entry and the part, and nothing is written
        self.assertEqual(
            self.lay("write", self.proposal_file),
            (
                1,
                (
                    f"lay.py: the entry of changelog-writer, {self.agent_file}, names its part"
                    f" {self.part}, which is not there; write it, or name the part there is, and"
                    " run again.\n"
                ),
            ),
        )
        self.assertFalse(os.path.exists(os.path.join(self.plugin, "hooks")))

    def test_its_hook_watches_every_tool_call_though_its_lanes_watch_none(self):
        # Given: test_after alone on step 3 of changelog-writer, held as it is about to end
        tested = {"lane": "test_after", "takes": ["CHANGELOG.md", "python3 check.py"]}
        self.propose(self.proposal([tested]))
        # When: it is written
        self.lay("write", self.proposal_file)
        # Then: changelog-writer has a hook on every tool call, as the guard holds it to read its
        # part first
        [pre] = self.hooks()["hooks"]["PreToolUse"]
        self.assertEqual(pre["matcher"], ".*")
        self.assertEqual(
            pre["hooks"][0]["command"],
            entries.command("notes", helpers.AGENT, "PreToolUse"),
        )

    def test_its_hook_watches_every_tool_call_beside_its_lanes(self):
        # Given: the README's proposal, hands_off watching Bash
        # When: it is written
        self.lay("write", self.proposal_file)
        # Then: changelog-writer's hook on a tool call matches every tool and Bash, and it has
        # none at its end, as no lane is held there
        self.assertEqual(self.hooks()["hooks"]["PreToolUse"][0]["matcher"], ".*|Bash")
        self.assertNotIn("SubagentStop", self.hooks()["hooks"])

    def test_up_keeps_its_hook_watching_every_tool_call(self):
        # Given: the README's proposal laid, then its hook written as a hook watching Bash alone
        self.lay("write", self.proposal_file)
        hooks = self.hooks()
        hooks["hooks"]["PreToolUse"][0]["matcher"] = "Bash"
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        # When: `lay.py up` is run on the plugin
        self.lay("up", self.plugin)
        # Then: the hook is written again watching every tool and Bash
        self.assertEqual(self.hooks()["hooks"]["PreToolUse"][0]["matcher"], ".*|Bash")

    def test_a_subagent_with_a_part_and_no_lanes_has_no_hook(self):
        # Given: changelog-writer, its entry having it read its part first, with no lanes laid,
        # as `lay.py up` keeps a subagent whose lanes it left out
        agent = {"name": "changelog-writer", "steps": [], "part": True}
        for event in entries.EVENTS:
            with self.subTest(event=event):
                # When: its entry of hooks.json for the event is made
                # Then: there is none, as the part is held where lanes are laid
                self.assertIsNone(entries.entry("notes", agent, event))

    def test_an_entry_naming_no_part_keeps_its_hook_to_its_lanes(self):
        # Given: changelog-writer's file holding its steps, naming no part
        self.write(self.agent_file, helpers.STEPS)
        # When: the README's proposal is written
        self.lay("write", self.proposal_file)
        # Then: its hook on a tool call matches Bash alone, as before
        self.assertEqual(self.hooks()["hooks"]["PreToolUse"][0]["matcher"], "Bash")


class TestReadFirst(GuardTest):
    """The guard on changelog-writer, its file its entry and its steps in its part, with the lanes
    LAID."""

    def lay(self, *laid: tuple, values: str = "") -> None:
        """Lays the lanes as GuardTest does, then moves the steps into the part,
        prompts/writer.md, leaving the entry naming it."""
        super().lay(*laid, values=values)
        self.part = os.path.join(self.plugin, "prompts", "writer.md")
        self.write(self.part, self.read(self.agent_file).split("---\n", 2)[2])
        self.write(self.agent_file, ENTRY)

    def told(self) -> str:
        """The entry's sentence as the subagent is told it, the plugin's folder put in."""
        return "notes: " + FIRST.replace("${CLAUDE_PLUGIN_ROOT}", self.plugin)

    def whole(self) -> tuple:
        """A Read of the part whole, as the record holds it."""
        lines = self.read(self.part).splitlines()
        shown = "".join(f"{n}\t{line}\n" for n, line in enumerate(lines, 1))
        return ("Read", {"file_path": self.part}, shown)

    def test_a_first_call_but_reading_the_part_is_told_the_entrys_sentence(self):
        # Given: hands_off on step 3, nothing done yet
        self.record([])
        for what, event in (
            ("a command hands_off allows", self.event("git status")),
            # Files named before the part and after it in order, and none.
            ("a read of another file", self.called("Read", {"file_path": "a.md"})),
            ("a read of a file after it", self.called("Read", {"file_path": "z.md"})),
            ("a read of no file", self.called("Read", {})),
        ):
            with self.subTest(what=what):
                # When: changelog-writer's first call is one hands_off allows
                # Then: it is stopped and told the entry's sentence headed by the plugin
                self.assertEqual(self.guard(json.dumps(event)), ("told", self.told()))

    def test_reading_the_part_first_goes_on_before_any_lane(self):
        # Given: start_with on step 1 and read_only on step 3, nothing done yet
        self.lay((1, "start_with", ["scripts/log.py"]), (3, "read_only", ["notes.md"]))
        self.record([])
        # When: changelog-writer's first call reads the part
        event = self.called("Read", {"file_path": self.part})
        # Then: it goes on, no lane told, as the entry tells it to read the part first
        self.assertEqual(self.guard(json.dumps(event)), ("", ""))

    def test_a_call_after_the_part_read_whole_is_held_to_the_lanes(self):
        # Given: hands_off on step 3, and the part read whole
        self.record([self.whole()])
        for command, said in (
            ("git status", ("", "")),
            ("git commit -m notes", ("told", "notes: Do not run `git commit` or `git push`.")),
        ):
            with self.subTest(command=command):
                # When: changelog-writer runs a command
                # Then: hands_off holds it, as without a part
                self.assertEqual(self.guard(self.stream(command)), said)

    def test_a_call_after_the_part_read_in_part_is_told_the_entrys_sentence(self):
        # Given: the part read up to its first line alone
        self.record([("Read", {"file_path": self.part, "limit": 1}, "1\t## Role\n")])
        # When: changelog-writer runs a command
        # Then: it is told the entry's sentence, as part of the part is left unread
        self.assertEqual(self.guard(self.stream("git status")), ("told", self.told()))

    def test_a_command_reading_the_part_is_held_to_the_lanes(self):
        # Given: hands_off on step 3, nothing done yet
        self.record([])
        # When: changelog-writer reads the part by a command that also commits
        command = f"cat {self.part} && git commit -m notes"
        # Then: hands_off holds it, as a command does more than read
        said = ("told", "notes: Do not run `git commit` or `git push`.")
        self.assertEqual(self.guard(self.stream(command)), said)

    def test_the_end_is_held_to_the_lanes_alone(self):
        # Given: end_when on step 4, the part never read, nothing made
        self.lay((4, "end_when", ["CHANGELOG.md"]))
        self.record([])
        # When: changelog-writer is about to end
        said = self.guard(json.dumps(self.stopped("Done.")), entry="subagentstop.py")
        # Then: it is told end_when's sentence alone, as reading the part first is held on calls
        self.assertEqual(said, ("told", "notes: End only once `CHANGELOG.md` is made."))

    def test_a_part_not_there_is_an_error(self):
        # Given: the part the entry names not there
        os.remove(self.part)
        self.record([])
        # When: changelog-writer makes a call
        # Then: it is an error, naming the part, for the plugin's maker to fix
        said = (
            "notes: lane cannot check the lanes of changelog-writer: its entry names its part"
            " `prompts/writer.md`, which is not there. Stop here and reply that the maker of notes"
            " must fix it."
        )
        self.assertEqual(self.guard(self.stream("git status")), ("error", said))

    def test_with_no_record_found_reading_the_part_first_is_an_error(self):
        # Given: no record of changelog-writer
        # When: changelog-writer makes a call
        # Then: it is an error, saying the record is not found
        whom, said = self.guard(self.stream("git status"))
        self.assertEqual(whom, "error")
        self.assertIn(
            "notes: lane cannot check the lanes of changelog-writer: its record is not found", said
        )


if __name__ == "__main__":
    unittest.main()

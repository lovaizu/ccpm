"""A subagent whose file is its entry, its frontmatter and a body having it read its part first: its
steps are read from that part, the one file under the plugin's prompts/ the body names in
backticks, where the layer writes each lane's sentence and the guard reads it."""

from __future__ import annotations

import json
import os
import unittest

import helpers
from helpers import step
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
# changelog-writer's entry saying where the script and the form its part names by name lie, before
# the sentence naming its part.
BOUND_ENTRY = (
    """---
name: changelog-writer
---

`log.py` below is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/log.py"`, run from where you start.
`entry.json` below is `${CLAUDE_PLUGIN_ROOT}/forms/entry.json`.

"""
    + FIRST.replace(" its steps", "\nits steps")
    + "\n"
)
# What BOUND_ENTRY binds each name to.
BOUND = {
    "log.py": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/log.py"',
    "entry.json": "${CLAUDE_PLUGIN_ROOT}/forms/entry.json",
}
# in_form on step 3, its form named by the name BOUND_ENTRY binds.
FORMED = {"lane": "in_form", "takes": ["CHANGELOG.json", "entry.json"]}


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
        # Then: it is that file
        self.assertEqual(step.part(self.plugin, "changelog-writer"), self.part)

    def test_a_part_named_twice_is_that_file(self):
        # Given: an entry naming its part in the sentence, then again in another
        again = "Its steps are those of `${CLAUDE_PLUGIN_ROOT}/prompts/writer.md`."
        self.entry(f"{FIRST}\n\n{again}\n")
        # When: its part is looked for
        # Then: it is that one file
        self.assertEqual(step.part(self.plugin, "changelog-writer"), self.part)

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


class TestBindings(PartTest):
    """The entry says where each script, file or folder its part names by name lies, and a lane
    taking the name reads it so."""

    def test_each_binding_of_the_entry_is_its_name_and_what_it_stands_for(self):
        # Given: changelog-writer's entry binding log.py and entry.json, before its part's sentence
        self.write(self.agent_file, BOUND_ENTRY)
        # When: its bindings are read
        # Then: each name is what the entry says it stands for, and its part is as before
        self.assertEqual(step.bindings(self.plugin, "changelog-writer"), BOUND)
        self.assertEqual(step.part(self.plugin, "changelog-writer"), self.part)

    def test_a_binding_over_a_line_break_is_read_whole(self):
        # Given: an entry binding a name over a line break
        self.entry("`log.py` below is\n`python3 log.py`, run from where you start.\n")
        # When: its bindings are read
        # Then: the line break is read as a space
        self.assertEqual(
            step.bindings(self.plugin, "changelog-writer"), {"log.py": "python3 log.py"}
        )

    def test_an_entry_binding_nothing_has_no_bindings(self):
        for what, name, text in (
            ("an entry naming its part alone", "changelog-writer", ENTRY),
            (
                "a binding in the frontmatter alone",
                "changelog-writer",
                "---\nname: changelog-writer\ndescription: `log.py` below is `x`.\n---\n\nWrite.\n",
            ),
            ("no entry naming the subagent", "other", ENTRY),
        ):
            with self.subTest(what=what):
                # Given: an entry binding no name in its body, or none naming the subagent
                self.write(self.agent_file, text)
                # When: its bindings are read
                # Then: there are none
                self.assertEqual(step.bindings(self.plugin, name), {})

    def test_a_take_beginning_with_a_bound_name_is_read_as_the_entry_binds_it(self):
        # Given: the takes of lanes, some beginning with a name BOUND binds
        takes = ["log.py --since v1", "entry.json", "git commit", "{work}", "cat log.py"]
        # When: they are read through the bindings
        # Then: a bound name beginning a take is put in as it stands for, every other take left
        self.assertEqual(
            step.bound(takes, BOUND),
            [
                'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/log.py" --since v1',
                "${CLAUDE_PLUGIN_ROOT}/forms/entry.json",
                "git commit",
                "{work}",
                "cat log.py",
            ],
        )


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

    def test_its_hook_watches_the_tools_of_its_lanes_alone(self):
        # Given: the README's proposal, hands_off watching Bash
        # When: it is written
        self.lay("write", self.proposal_file)
        # Then: changelog-writer's hook on a tool call matches Bash alone, as a lane goes only
        # where the proposal lays it
        self.assertEqual(self.hooks()["hooks"]["PreToolUse"][0]["matcher"], "Bash")

    def test_an_entry_naming_no_part_keeps_its_hook_to_its_lanes(self):
        # Given: changelog-writer's file holding its steps, naming no part
        self.write(self.agent_file, helpers.STEPS)
        # When: the README's proposal is written
        self.lay("write", self.proposal_file)
        # Then: its hook on a tool call matches Bash alone, as before
        self.assertEqual(self.hooks()["hooks"]["PreToolUse"][0]["matcher"], "Bash")

    def test_a_form_named_by_a_bound_name_is_laid(self):
        # Given: in_form on step 3 taking its form by the name the entry binds, the form there
        self.write(self.agent_file, BOUND_ENTRY)
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), {"type": "object"})
        self.propose(self.proposal([FORMED]))
        # When: it is printed
        code, said = self.lay("print", self.proposal_file)
        # Then: it is shown with the step, as the form is read where the entry says it lies
        self.assertEqual(code, 0, said)
        self.assertIn("Write `CHANGELOG.json` in the form of `entry.json`.", said)

    def test_a_form_named_by_a_name_no_entry_binds_is_refused(self):
        # Given: in_form on step 3 taking its form by a name the entry does not bind
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), {"type": "object"})
        self.propose(self.proposal([FORMED]))
        # When: it is printed
        code, said = self.lay("print", self.proposal_file)
        # Then: it stops, as no path is known for the form
        self.assertEqual(code, 1)
        self.assertIn("names the form entry.json, which is not named as", said)


class TestBoundGuard(GuardTest):
    """The guard on changelog-writer, its file its entry BOUND_ENTRY, binding the names its part
    uses, and its steps in its part."""

    def lay(self, *laid: tuple, values: str = "") -> None:
        """Lays the lanes as GuardTest does, then moves the steps into the part,
        prompts/writer.md, leaving the entry BOUND_ENTRY naming it."""
        super().lay(*laid, values=values)
        part = os.path.join(self.plugin, "prompts", "writer.md")
        self.write(part, self.read(self.agent_file).split("---\n", 2)[2])
        self.write(self.agent_file, BOUND_ENTRY)
        self.write_json(os.path.join(self.plugin, "forms", "entry.json"), {"type": "object"})

    def test_a_script_named_by_a_bound_name_is_the_one_the_entry_says(self):
        # Given: start_with on step 1 taking log.py, which the entry binds
        self.lay((1, "start_with", ["log.py"]))
        self.record([])
        for what, command, said in (
            (
                "the script where the entry says",
                f'python3 "{self.plugin}/scripts/log.py"',
                ("", ""),
            ),
            (
                "a script of that name elsewhere",
                f"python3 {self.base}/log.py",
                ("told", "notes: First run `log.py`."),
            ),
        ):
            with self.subTest(what=what):
                # When: changelog-writer runs it first
                # Then: the entry's script goes on, and another of the name is told the sentence
                self.assertEqual(self.guard(self.stream(command)), said)

    def test_a_form_named_by_a_bound_name_holds_the_write(self):
        # Given: in_form on step 3 taking its form by the name the entry binds
        self.lay((3, "in_form", FORMED["takes"]))
        self.record([])
        # When: changelog-writer writes the output out of the form
        event = self.called("Write", {"file_path": "CHANGELOG.json", "content": "[]"})
        # Then: it is told the sentence as its step says it, with the point
        whom, said = self.guard(json.dumps(event))
        self.assertEqual(whom, "told")
        self.assertTrue(
            said.startswith("notes: Write `CHANGELOG.json` in the form of `entry.json`.\n")
        )

    def test_the_form_named_by_a_bound_name_may_be_read(self):
        # Given: read_only on step 1 and in_form on step 3 taking its form by a bound name
        self.lay((1, "read_only", ["notes.md"]), (3, "in_form", FORMED["takes"]))
        self.record([])
        # When: changelog-writer reads the form where the entry says it lies
        form = os.path.join(self.plugin, "forms", "entry.json")
        event = self.called("Read", {"file_path": form})
        # Then: it goes on, as read_only lets it read the form of its in_form lane
        self.assertEqual(self.guard(json.dumps(event)), ("", ""))


if __name__ == "__main__":
    unittest.main()

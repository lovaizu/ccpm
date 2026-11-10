"""dev/scripts/practices.py, what a person or CI runs on rn's best practices: faults names each
fault of a best practice's form, markdown_of makes the Markdown a person reads, and copies makes the
copy of its example. form names those faults, its Markdown and the copy left behind, and each file
in its folder none of them holds. markdown writes its Markdown beside it, and example writes the
copy of its example from its source."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import os
import sys
import unittest
from typing import Any

import helpers

sys.path.insert(0, os.path.join(helpers.TOP, "dev", "scripts"))

import practices


def ran(*argv):
    """What practices.py gives on the arguments: its exit code, what it printed, and its errors."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = practices.main(list(argv))
    return code, out.getvalue(), err.getvalue()


DATA: dict[str, Any] = {
    "goal": "The reader gets it.",
    "inputs": [],
    "preconditions": [],
    "parts": [{"id": "a", "what": "A.", "parts": [{"id": "b", "what": "B."}]}],
    "necessary_conditions": [
        {"id": "N1", "about": "a", "what": "Does it?"},
        {"id": "N2", "about": "b, the whole", "what": "After N1, does all?"},
    ],
    "practices": [
        {
            "intent": "N1",
            "why": "Think.",
            "items": [
                {
                    "at": "decide",
                    "text": "Choose.",
                    "trace": {"action": "run", "takes": ["make", "make all"]},
                },
                {"at": "make", "text": "Where it fails, mend it."},
            ],
        },
        {"intent": "N2", "why": "Then.", "items": [{"at": "make", "text": "Do."}]},
    ],
}


# A best practice of the kind `kind`, beside no other kind's.
PATH = os.path.join("kind", "best-practice.json")


def changed(change):
    data = copy.deepcopy(DATA)
    change(data)
    return practices.faults(data)


class Factors(unittest.TestCase):
    """The critical success factors, which a best practice may hold, each with a necessary
    condition under it."""

    def factored(self, change=lambda d: None):
        data = copy.deepcopy(DATA)
        data["critical_success_factors"] = [{"id": "C1", "what": "A."}, {"id": "C2", "what": "B."}]
        data["necessary_conditions"][0]["csf"] = "C1"
        data["necessary_conditions"][1]["csf"] = "C2"
        change(data)
        return data

    def test_a_sound_best_practice_of_factors_has_none(self):
        self.assertEqual(practices.faults(self.factored()), [])

    def test_factors_out_of_number_order(self):
        def swap(d):
            d["critical_success_factors"].reverse()

        self.assertEqual(
            practices.faults(self.factored(swap)),
            ["factors are C2, C1, not numbered in order from C1"],
        )

    def test_a_condition_under_no_factor(self):
        def stray(d):
            d["necessary_conditions"][1]["csf"] = "C3"

        self.assertEqual(
            practices.faults(self.factored(stray)),
            [
                "N2 is under C3, which is no critical success factor",
                "C2 has no necessary condition under it",
            ],
        )

    def test_a_condition_that_names_no_factor(self):
        def bare(d):
            del d["necessary_conditions"][0]["csf"]
            d["necessary_conditions"][1]["csf"] = "C1"

        self.assertEqual(
            practices.faults(self.factored(bare)),
            [
                "N1 is under None, which is no critical success factor",
                "C2 has no necessary condition under it",
            ],
        )

    def test_the_markdown_lists_the_factors_and_each_condition_under_its_factor(self):
        text = practices.markdown_of(PATH, self.factored())
        self.assertIn(
            "## Critical success factors\n\n| ID | Factor |\n| --- | --- |\n| C1 | A. |\n"
            "| C2 | B. |\n\n## Necessary conditions\n\n| ID | Factor | Condition | Parts |\n"
            "| --- | --- | --- | --- |\n"
            "| N1 | C1 | Does it? | a |\n| N2 | C2 | After N1, does all? | b, the whole |\n\n"
            "## Practices\n",
            text,
        )
        self.assertNotIn("Critical success factors", practices.markdown_of(PATH, DATA))

    def test_the_markdown_names_the_sections_where_a_template_holds_the_form(self):
        data = {k: v for k, v in DATA.items() if k != "parts"}
        text = practices.markdown_of(PATH, dict(data, template="template.md"))
        self.assertIn("| ID | Condition | Sections |\n", text)


class Faults(unittest.TestCase):
    def test_a_sound_best_practice_has_none(self):
        self.assertEqual(practices.faults(DATA), [])

    def test_questions_out_of_number_order(self):
        def swap(d):
            d["necessary_conditions"].reverse()
            d["practices"].reverse()

        self.assertIn("conditions are N2, N1, not numbered in order from N1", changed(swap))

    def test_practices_not_in_the_questions_order(self):
        def swap(d):
            d["practices"].reverse()

        expected = "practices meet N2, N1, not each condition once in its order"
        self.assertEqual(changed(swap), [expected])

    def test_a_question_with_no_method(self):
        def drop(d):
            d["practices"].pop()

        self.assertEqual(changed(drop), ["practices meet N1, not each condition once in its order"])

    def test_about_a_part_that_is_not_there(self):
        def wrong(d):
            d["necessary_conditions"][0]["about"] = "c"

        self.assertEqual(changed(wrong), ["N1 is about c, which is no part"])

    def test_a_part_named_twice(self):
        def twice(d):
            d["parts"].append({"id": "a", "what": "Again."})

        self.assertEqual(changed(twice), ["part a is named more than once"])

    def test_a_question_named_in_the_text_that_is_not_there(self):
        def name(d):
            d["practices"][1]["why"] = "As N3 says."

        self.assertEqual(changed(name), ["N3 is named, but there is no such condition"])

    def test_a_part_no_question_is_about(self):
        def add(d):
            d["parts"].append({"id": "c", "what": "C."})

        self.assertEqual(changed(add), ["part c has no condition about it"])

    def test_no_question_about_the_whole_is_no_fault(self):
        def narrow(d):
            d["necessary_conditions"][1]["about"] = "b"

        self.assertEqual(changed(narrow), [])

    def test_a_best_practice_of_one_question_about_the_whole(self):
        data = {
            "goal": "G.",
            "necessary_conditions": [{"id": "N1", "about": "the whole", "what": "Does it?"}],
            "practices": [{"intent": "N1", "why": "T.", "items": [{"at": "make", "text": "Do."}]}],
        }
        self.assertEqual(practices.faults(data), [])

    def test_two_questions_of_one_number(self):
        def same(d):
            d["necessary_conditions"][1]["id"] = "N1"
            d["practices"][1]["intent"] = "N1"

        self.assertIn("conditions are N1, N1, not numbered in order from N1", changed(same))

    def test_a_question_numbered_otherwise_is_not_named_as_missing(self):
        def letter(d):
            d["necessary_conditions"][0]["id"] = "A"
            d["practices"][0]["intent"] = "A"

        self.assertEqual(
            changed(letter),
            [
                "conditions are A, N2, not numbered in order from N1",
                "N1 is named, but there is no such condition",
            ],
        )

    def test_about_a_part_named_after_the_whole_that_is_not_there(self):
        def wrong(d):
            d["necessary_conditions"][0]["about"] = "z"

        self.assertEqual(changed(wrong), ["N1 is about z, which is no part"])

    def test_a_question_named_in_a_intent_that_is_not_there(self):
        def name(d):
            d["necessary_conditions"][0]["what"] = "Before N3, does it?"

        self.assertEqual(changed(name), ["N3 is named, but there is no such condition"])

    def test_a_value_that_is_no_text_names_no_question(self):
        def number(d):
            d["parts"][0]["level"] = 3

        self.assertEqual(changed(number), [])

    def test_a_step_of_a_case_that_carries_a_trace(self):
        # Given: a step that holds only where its case does, opening with Where or If, with a trace
        expected = (
            "N1.2 holds only in its case, so it carries no trace, as a run outside the case never"
            " makes it"
        )
        for opening in ("Where it fails", "If it fails"):

            def traced(d, opening=opening):
                d["practices"][0]["items"][1] = {
                    "at": "make",
                    "text": f"{opening}, mend it.",
                    "trace": {"action": "write", "takes": ["a.md"]},
                }

            # Then: the trace is a fault, as not every run makes it
            with self.subTest(opening=opening):
                self.assertEqual(changed(traced), [expected])

    def test_a_step_with_a_fault_after_one_with_no_trace(self):
        # Given: a step with no trace, then one of a case with a trace
        def traced(d):
            d["practices"][1]["items"] = [
                {"at": "make", "text": "Do."},
                {
                    "at": "make",
                    "text": "If it fails, mend it.",
                    "trace": {"action": "run", "takes": ["make"]},
                },
            ]

        # Then: the later step's trace is still named
        expected = (
            "N2.2 holds only in its case, so it carries no trace, as a run outside the case never"
            " makes it"
        )
        self.assertEqual(changed(traced), [expected])

    def test_a_step_that_opens_with_a_word_holding_where_or_if_is_no_case(self):
        def traced(d):
            d["practices"][0]["items"][0]["text"] = "Wherever it runs, Iffy, do it."

        self.assertEqual(changed(traced), [])

    def test_a_trace_that_takes_an_empty_text(self):
        for empty in ("", " "):

            def traced(d, empty=empty):
                d["practices"][1]["items"] = [
                    {
                        "at": "make",
                        "text": "Do.",
                        "trace": {"action": "read", "takes": ["a.md", empty]},
                    }
                ]

            with self.subTest(empty=empty):
                self.assertEqual(
                    changed(traced),
                    ["N2.1 takes an empty text in its trace, which no call matches"],
                )

    def test_a_decide_item_after_a_make_item(self):
        # Given: a practice whose item taken while deciding comes after one taken while making
        def late(d):
            d["practices"][0]["items"].append({"at": "decide", "text": "Choose again."})

        # Then: the check names the late item, as the maker settles the decisions before it makes
        expected = "N1.3 is taken while deciding, after N1.2, which is taken while making"
        self.assertEqual(changed(late), [expected])

    def test_decide_items_after_make_items_of_another_practice_are_no_fault(self):
        # Given: a practice of decide items only, after one that ends with a make item
        def other(d):
            d["practices"][1]["items"] = [{"at": "decide", "text": "Choose."}]

        self.assertEqual(changed(other), [])

    def test_an_item_named_in_the_text_that_is_not_there(self):
        # Given: a text naming the third item of N1, which has two, and the first of N2
        def name(d):
            d["practices"][1]["why"] = "As N1.3 says, and N2.1."

        # Then: the check names only the item that isn't there
        self.assertEqual(changed(name), ["N1.3 is named, but there is no such item"])

    def test_an_item_of_a_condition_that_is_not_there(self):
        def name(d):
            d["practices"][1]["why"] = "As N3.1 says."

        self.assertEqual(
            changed(name),
            [
                "N3 is named, but there is no such condition",
                "N3.1 is named, but there is no such item",
            ],
        )

    def test_an_item_numbered_zero_is_not_there(self):
        def name(d):
            d["practices"][1]["why"] = "As N1.0 says."

        self.assertEqual(changed(name), ["N1.0 is named, but there is no such item"])


TEMPLATE = """# <Product>

> [!NOTE]
> DELETE_TEMPLATE_COMMENT: <Product>: the product's name.

<Product> is <kind>.

## Roles

### <role>

## OKRs
"""
SECTIONS = ["the opening", "Roles", "OKRs"]
BY_TEMPLATE = {
    "goal": "The reader gets it.",
    "inputs": [],
    "preconditions": [],
    "necessary_conditions": [
        {"id": "N1", "about": "the opening, Roles", "what": "Does it?"},
        {"id": "N2", "about": "OKRs, the whole", "what": "Does all?"},
    ],
    "practices": DATA["practices"],
}


class Sections(unittest.TestCase):
    def test_the_opening_and_each_second_level_heading(self):
        self.assertEqual(practices.sections(TEMPLATE), SECTIONS)

    def test_an_opening_on_the_line_right_under_the_title(self):
        self.assertEqual(practices.sections("# <P>\n<P> is.\n## Roles\n"), ["the opening", "Roles"])

    def test_no_opening_where_only_the_title_and_notes_stand_before_the_first_section(self):
        bare = "# <P> UX\n\n> [!NOTE]\n> DELETE_TEMPLATE_COMMENT:\n> - <slot>: what.\n\n## Roles\n"
        self.assertEqual(practices.sections(bare), ["Roles"])

    def test_an_opening_right_under_a_note(self):
        text = "# <P>\n\n> [!NOTE]\n> DELETE_TEMPLATE_COMMENT: Delete.\n<P> is.\n## Roles\n"
        self.assertEqual(practices.sections(text), ["the opening", "Roles"])

    def test_a_quote_of_the_work_s_own_is_an_opening(self):
        text = "# <P>\n\n> [!NOTE]\n> <P> is not yet released.\n\n## Roles\n"
        self.assertEqual(practices.sections(text), ["the opening", "Roles"])


class NotesLeft(unittest.TestCase):
    def test_a_note_of_a_markdown_template_by_its_line(self):
        text = "# t\n\n> [!NOTE]\n> DELETE_TEMPLATE_COMMENT:\n> - <slot>: what.\n"
        self.assertEqual(practices.notes_left(text), [4])

    def test_a_note_of_a_json_template_by_its_key(self):
        text = '{\n "goal": "g",\n "x": {\n  "DELETE_TEMPLATE_COMMENT": "y"\n }\n}'
        self.assertEqual(practices.notes_left(text), [4])

    def test_lines_counted_from_a_first_line_that_is_blank(self):
        text = "\n> [!NOTE]\n> DELETE_TEMPLATE_COMMENT: what.\n"
        self.assertEqual(practices.notes_left(text), [3])

    def test_the_marker_named_in_a_sentence_is_no_note(self):
        steps = '{"steps": ["Open each note with `DELETE_TEMPLATE_COMMENT:`."]}'
        text = steps + "\nSay > DELETE_TEMPLATE_COMMENT:"
        self.assertEqual(practices.notes_left(text), [])


class Keys(unittest.TestCase):
    def test_each_key_in_order_but_the_comments(self):
        text = (
            '{"DELETE_TEMPLATE_COMMENT": "x", "goal": "<g>", "necessary_conditions": [],'
            ' "practices": []}'
        )
        self.assertEqual(practices.keys(text), ["goal", "necessary_conditions", "practices"])

    def test_keeps_a_key_that_sorts_before_the_comments(self):
        self.assertEqual(
            practices.keys('{"$anchor": "a", "DELETE_TEMPLATE_COMMENT": "x"}'), ["$anchor"]
        )

    def test_the_fields_at_the_top_of_a_template_that_is_a_json_schema(self):
        text = json.dumps(
            {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "description": "d",
                "type": "object",
                "properties": {"goal": {"type": "string"}, "steps": {"type": "array"}},
            }
        )
        self.assertEqual(practices.keys(text), ["goal", "steps"])


SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "A plan.",
    "type": "object",
    "required": ["goal"],
    "properties": {"goal": {"type": "string", "description": "The end."}},
}


class Unheld(helpers.FolderTest):
    """unheld, the point an example in JSON is out of the template beside it by, where the template
    is a JSON Schema."""

    def setUp(self) -> None:
        super().setUp()
        self.path = os.path.join("kind", "best-practice.json")
        self.data = dict(DATA, template="plan.schema.json", example="example.json")
        self.write_json(os.path.join("kind", "plan.schema.json"), SCHEMA)

    def example(self, value: Any) -> list[str]:
        self.write_json(os.path.join("kind", "example.json"), value)
        return practices.unheld(self.path, self.data)

    def test_none_where_the_example_holds_to_the_schema(self):
        self.assertEqual(self.example({"goal": "g"}), [])

    def test_the_point_the_example_is_out_by(self):
        self.assertEqual(
            self.example({"goal": 1}),
            ["its example example.json is out of its template: $.goal: expected a string, found 1"],
        )

    def test_none_where_the_template_is_no_schema(self):
        self.write_json(os.path.join("kind", "plan.schema.json"), {"goal": "<goal>"})
        self.assertEqual(self.example({"goal": 1}), [])

    def test_none_where_the_template_or_the_example_is_no_json(self):
        self.write(os.path.join("kind", "example.md"), "# Plan\n")
        self.write(os.path.join("kind", "template.md"), "# <Plan>\n")
        for named in (
            dict(self.data, example="example.md"),
            dict(self.data, template="template.md"),
            DATA,
        ):
            with self.subTest(named=named.get("template"), example=named.get("example")):
                self.assertEqual(practices.unheld(self.path, named), [])

    def test_a_schema_it_does_not_read_whole_is_named(self):
        self.write_json(os.path.join("kind", "plan.schema.json"), dict(SCHEMA, oneOf=[]))
        found = self.example({"goal": "g"})
        self.assertEqual(len(found), 1)
        self.assertTrue(
            found[0].startswith("its template plan.schema.json is no schema it reads whole: $"),
            found,
        )

    def test_an_example_that_is_no_json_is_named(self):
        self.write(os.path.join("kind", "example.json"), "{")
        found = practices.unheld(self.path, self.data)
        self.assertEqual(len(found), 1)
        self.assertIn("example.json is not JSON", found[0])


class Beside(helpers.FolderTest):
    """template and missing, on the files a best practice names beside it."""

    def setUp(self) -> None:
        super().setUp()
        self.folder = os.path.join(self.base, "kind")
        self.path = os.path.join(self.folder, "best-practice.json")

    def test_none_where_it_names_no_template(self):
        self.assertIsNone(practices.template(self.path, DATA))
        self.assertEqual(practices.missing(self.path, DATA), [])

    def test_the_sections_of_a_template_in_markdown(self):
        self.write(os.path.join(self.folder, "template.md"), TEMPLATE)
        named = dict(BY_TEMPLATE, template="template.md")
        self.assertEqual(practices.template(self.path, named), SECTIONS)

    def test_the_keys_of_a_template_in_json(self):
        self.write(
            os.path.join(self.folder, "template.json"),
            '{"DELETE_TEMPLATE_COMMENT": "x", "goal": "g"}',
        )
        named = dict(BY_TEMPLATE, template="template.json")
        self.assertEqual(practices.template(self.path, named), ["goal"])

    def test_each_file_named_that_is_not_there(self):
        self.write(os.path.join(self.folder, "template.md"), TEMPLATE)
        named = dict(BY_TEMPLATE, template="template.md", example="example.md")
        self.assertEqual(
            practices.missing(self.path, named), ["its example example.md is not beside it"]
        )

    def test_an_example_in_the_folder_of_another_kind(self):
        named = dict(DATA, example="../other/best-practice.json")
        self.write_json(self.path, named)
        self.write(os.path.join(self.base, "other", "best-practice.json"), "{}")
        self.assertEqual(practices.missing(self.path, named), [])

    def test_each_kind_it_takes_with_no_best_practice_beside_or_among_rn_s_own(self):
        named = dict(DATA, inputs=["note", "gone"], preconditions=["late", "note"])
        self.write(os.path.join(self.base, "note", "best-practice.json"), "{}")
        self.write(os.path.join(self.base, "late", "template.md"), "# <P>\n")
        self.assertEqual(
            practices.missing(self.path, named),
            [
                "its input gone has no best practice beside it or among rn's own",
                "its precondition late has no best practice beside it or among rn's own",
            ],
        )

    def test_a_kind_it_takes_among_rn_s_own_where_none_lies_beside(self):
        named = dict(DATA, inputs=["readme"])
        self.assertEqual(practices.missing(self.path, named), [])
        self.assertEqual(
            practices.practice_of(self.path, "readme"),
            os.path.join(practices.OWN, "readme", "best-practice.json"),
        )

    def test_a_kind_beside_it_before_rn_s_own(self):
        self.write(os.path.join(self.base, "readme", "best-practice.json"), "{}")
        self.assertEqual(
            practices.practice_of(self.path, "readme"),
            os.path.join(self.base, "readme", "best-practice.json"),
        )

    def test_a_kind_neither_beside_nor_among_rn_s_own_is_sought_beside(self):
        self.assertEqual(
            practices.practice_of(self.path, "gone"),
            os.path.join(self.base, "gone", "best-practice.json"),
        )

    def test_the_markdown_links_each_kind_it_takes_where_its_best_practice_lies(self):
        self.write(os.path.join(self.base, "late", "best-practice.json"), "{}")
        named = dict(DATA, inputs=["late", "readme", "gone"])
        own = os.path.relpath(os.path.join(practices.OWN, "readme"), self.folder)
        own = own.replace(os.sep, "/")
        self.assertIn(
            "## Inputs\n\n- [late](../late/best-practice.md)\n"
            f"- [readme]({own}/best-practice.md)\n- [gone](../gone/best-practice.md)\n",
            practices.markdown_of(self.path, named),
        )

    def test_the_entries_at_the_top_of_a_template_that_is_a_folder(self):
        for entry in (".claude-plugin/plugin.json", "skills/up/SKILL.md", "README.md", ".DS_Store"):
            self.write(os.path.join(self.folder, "template", entry), "x")
        named = dict(BY_TEMPLATE, template="template")
        self.assertEqual(
            practices.template(self.path, named), [".claude-plugin", "README.md", "skills"]
        )
        self.assertEqual(practices.missing(self.path, named), [])

    def test_a_template_folder_that_is_not_there(self):
        named = dict(BY_TEMPLATE, template="template")
        self.assertEqual(
            practices.missing(self.path, named), ["its template template is not beside it"]
        )

    def test_the_kind_is_the_name_of_its_folder(self):
        self.assertEqual(practices.kind_of(self.path), "kind")


class Shown(unittest.TestCase):
    def test_each_figure_under_its_folder_by_its_path_without_the_place_in_it(self):
        text = "![A](a.svg) and ![B](images/b.svg#part)\n"
        self.assertEqual(practices.shown(text), ["a.svg", "images/b.svg"])

    def test_a_figure_after_a_code_block_and_none_in_it(self):
        text = "![A](a.svg)\n```text\n![Q](q.svg)\n```\n![B](b.svg)\n```\n![R](r.svg)\n```\n"
        self.assertEqual(practices.shown(text), ["a.svg", "b.svg"])

    def test_no_link_figure_on_another_site_or_figure_above_its_folder(self):
        text = "[c](c.md) ![W](https://example.com/w.svg) ![U](../u.svg)\n"
        self.assertEqual(practices.shown(text), [])


class Leftovers(helpers.FolderTest):
    """leftovers, each file in a best practice's folder that neither it, its template nor its
    example holds."""

    def setUp(self) -> None:
        super().setUp()
        self.folder = os.path.join("practices", "kind")
        self.path = os.path.join(self.folder, "best-practice.json")
        self.data = dict(DATA, template="template.md", example="example.md")
        self.write(self.at("best-practice.json"), "{}")
        self.write(self.at("best-practice.md"), "# kind\n")
        self.write(self.at("template.md"), "![The product](images/template-a.svg)\n")
        self.write(self.at("images", "template-a.svg"), "<svg/>")
        self.write(self.at("example.md"), "![P](images/a.svg)\n```text\n![Q](images/q.svg)\n```\n")
        self.write(self.at("images", "a.svg"), "<svg/>")

    def at(self, *path: str) -> str:
        return os.path.join(self.folder, *path)

    def test_none_where_each_file_is_its_own_or_a_figure_its_template_or_example_shows(self):
        self.assertEqual(practices.leftovers(self.path, self.data), [])

    def test_a_file_none_of_them_holds(self):
        self.write(self.at("images", "old.svg"), "<svg/>")
        self.write(self.at("notes.md"), "n")
        self.assertEqual(
            practices.leftovers(self.path, self.data),
            [self.at("images", "old.svg"), self.at("notes.md")],
        )

    def test_a_hidden_file_is_no_leftover(self):
        self.write(self.at("images", ".DS_Store"), "")
        self.assertEqual(practices.leftovers(self.path, self.data), [])

    def test_a_figure_the_old_copy_shows_is_a_leftover_once_its_source_dropped_it(self):
        data = dict(self.data, source="../../doc/source.md")
        self.write(os.path.join("doc", "source.md"), "No figure.\n")
        self.assertEqual(practices.leftovers(self.path, data), [self.at("images", "a.svg")])

    def test_an_example_with_no_template_keeps_the_figures_it_shows(self):
        data = dict(DATA, example="example.md")
        self.assertEqual(
            practices.leftovers(self.path, data),
            [self.at("images", "template-a.svg"), self.at("template.md")],
        )

    def test_each_file_of_a_template_that_is_a_folder_is_held(self):
        data = dict(DATA, template="template")
        self.write(self.at("template", "skills", "up", "SKILL.md"), "s")
        self.write(self.at("template", ".claude-plugin", "plugin.json"), "{}")
        self.assertEqual(
            practices.leftovers(self.path, data),
            [
                self.at("example.md"),
                self.at("images", "a.svg"),
                self.at("images", "template-a.svg"),
                self.at("template.md"),
            ],
        )

    def test_a_source_with_no_example_keeps_only_its_own_files(self):
        data = dict(DATA, source="../../doc/source.md")
        self.assertEqual(
            practices.leftovers(self.path, data),
            [
                self.at("example.md"),
                self.at("images", "a.svg"),
                self.at("images", "template-a.svg"),
                self.at("template.md"),
            ],
        )


class Copies(helpers.FolderTest):
    """copies, the files of an example that's a copy of the document its source names."""

    def setUp(self) -> None:
        super().setUp()
        self.path = os.path.join("practices", "kind", "best-practice.json")
        self.data = dict(DATA, example="example.md", source="../../doc/source.md")
        self.copy = os.path.join("practices", "kind", "example.md")

    def made(self, text: str) -> dict[str, bytes]:
        self.write(os.path.join("doc", "source.md"), text)
        return practices.copies(self.path, self.data)

    def test_none_where_it_names_no_source(self):
        self.assertEqual(practices.copies(self.path, DATA), {})

    def test_the_source_as_it_is_where_it_links_nothing(self):
        self.assertEqual(self.made("# Doc\n\nText.\n"), {self.copy: b"# Doc\n\nText.\n"})

    def test_a_link_reaches_from_the_copy_what_it_reached_from_the_source(self):
        made = self.made("[a](other.md#part) and [b](../LICENSE)\n")
        self.assertEqual(made[self.copy], b"[a](../../doc/other.md#part) and [b](../../LICENSE)\n")

    def test_a_link_to_a_page_a_place_in_it_or_another_site_is_kept(self):
        text = "[a](https://example.com/x) [b](#part) [c](mailto:a@b.c)\n"
        self.assertEqual(self.made(text)[self.copy], text.encode())

    def test_a_figure_under_the_source_is_copied_beside_the_copy(self):
        self.write(os.path.join("doc", "images", "idea.svg"), "<svg/>")
        made = self.made("![Idea](images/idea.svg)\n")
        self.assertEqual(made[self.copy], b"![Idea](images/idea.svg)\n")
        self.assertEqual(made[os.path.join("practices", "kind", "images", "idea.svg")], b"<svg/>")

    def test_a_figure_above_the_source_is_linked_where_it_is(self):
        made = self.made("![Idea](../idea.svg)\n")
        self.assertEqual(made, {self.copy: b"![Idea](../../idea.svg)\n"})

    def test_a_link_in_a_code_block_is_text_and_kept(self):
        text = "```text\n[a](other.md)\n```\n[b](other.md)\n"
        self.assertEqual(
            self.made(text)[self.copy], b"```text\n[a](other.md)\n```\n[b](../../doc/other.md)\n"
        )

    def test_a_source_or_figure_not_there_is_refused(self):
        with self.assertRaises(FileNotFoundError):
            practices.copies(self.path, self.data)
        with self.assertRaises(FileNotFoundError):
            self.made("![Idea](images/idea.svg)\n")


class FaultsByTemplate(unittest.TestCase):
    def by(self, change=lambda d: None):
        data = copy.deepcopy(BY_TEMPLATE)
        change(data)
        return practices.faults(data, SECTIONS)

    def test_questions_about_its_sections_have_none(self):
        self.assertEqual(self.by(), [])

    def test_about_what_is_no_section(self):
        def wrong(d):
            d["necessary_conditions"][0]["about"] = "the opening, Scenarios, Roles"

        self.assertEqual(
            self.by(wrong), ["N1 is about Scenarios, which is no section of the template"]
        )

    def test_a_section_no_question_is_about(self):
        def narrow(d):
            d["necessary_conditions"][0]["about"] = "Roles"

        self.assertEqual(self.by(narrow), ["section the opening has no condition about it"])

    def test_parts_beside_the_template(self):
        def add(d):
            d["parts"] = [{"id": "Roles", "what": "R."}]

        self.assertEqual(self.by(add), ["parts are kept, though the template holds the form"])


class Markdown(unittest.TestCase):
    def test_names_the_source_its_example_is_copied_from(self):
        named = dict(DATA, example="example.md", source="../../README.md")
        text = practices.markdown_of(PATH, named)
        self.assertIn(
            "## Example\n\n[example.md](example.md),"
            " a copy of [../../README.md](../../README.md)\n",
            text,
        )

    def test_links_the_template_and_the_example_it_names(self):
        named = dict(BY_TEMPLATE, template="template.md", example="example.md")
        text = practices.markdown_of(PATH, named)
        self.assertIn("## Template\n\n[template.md](template.md)\n", text)
        self.assertIn("## Example\n\n[example.md](example.md)\n", text)
        self.assertNotIn("## Template", practices.markdown_of(PATH, DATA))
        self.assertNotIn("## Example", practices.markdown_of(PATH, DATA))

    def test_links_each_kind_it_takes_after_the_example(self):
        named = dict(DATA, example="example.md", inputs=["a"], preconditions=["b", "c"])
        text = practices.markdown_of(PATH, named)
        self.assertIn(
            "[example.md](example.md)\n\n## Inputs\n\n- [a](../a/best-practice.md)\n\n"
            "## Preconditions\n\n- [b](../b/best-practice.md)\n- [c](../c/best-practice.md)\n\n"
            "## Parts\n",
            text,
        )

    def test_leaves_out_a_list_of_kinds_that_is_empty(self):
        text = practices.markdown_of(PATH, dict(DATA, preconditions=["b"]))
        self.assertNotIn("## Inputs", text)
        self.assertIn("## Preconditions", text)
        self.assertNotIn("## Preconditions", practices.markdown_of(PATH, DATA))

    def test_holds_each_part_question_and_method_under_its_question(self):
        text = practices.markdown_of(PATH, DATA)
        expected = ["# `kind`\n", "The reader gets it.", "## Parts", "- **a**: A.", "  - **b**: B."]
        expected += [
            (
                "## Necessary conditions\n\n| ID | Condition | Parts |\n| --- | --- | --- |\n"
                "| N1 | Does it? | a |\n| N2 | After N1, does all? | b, the whole |\n\n"
                "## Practices\n"
            ),
            (
                "### N1\n\nDoes it?\n\nThink.\n\n"
                "1. *While deciding.* Choose. The trace: `make` or `make all` run.\n"
                "2. *While making.* Where it fails, mend it.\n\n"
                "### N2\n"
            ),
        ]
        for line in expected:
            self.assertIn(line, text)

    def test_names_each_trace_by_its_call(self):
        # Given: a step of each action, one taking three calls
        items = [
            {"at": "make", "text": "Run.", "trace": {"action": "run", "takes": ["make"]}},
            {
                "at": "make",
                "text": "Read.",
                "trace": {"action": "read", "takes": ["a.md", "b.md", "c.md"]},
            },
            {
                "at": "make",
                "text": "Make.",
                "trace": {"action": "write", "takes": ["{deliverable}"]},
            },
        ]
        data = copy.deepcopy(DATA)
        data["practices"][1]["items"] = items
        # Then: each names its calls, the last after or, and what the call does
        self.assertIn(
            "1. *While making.* Run. The trace: `make` run.\n"
            "2. *While making.* Read. The trace: `a.md`, `b.md` or `c.md` read to its end.\n"
            "3. *While making.* Make. The trace: `{deliverable}` made.\n",
            practices.markdown_of(PATH, data),
        )

    def test_sets_each_part_under_the_one_it_is_in(self):
        c: dict[str, Any] = {"id": "c", "what": "C."}
        b: dict[str, Any] = {"id": "b", "what": "B.", "parts": [c]}
        data = {**DATA, "parts": [{"id": "a", "what": "A.", "parts": [b]}]}
        lines = practices.markdown_of(PATH, data).splitlines()
        start = lines.index("## Parts") + 2
        self.assertEqual(
            lines[start : start + 3], ["- **a**: A.", "  - **b**: B.", "    - **c**: C."]
        )

    def test_leaves_out_what_a_best_practice_has_none_of(self):
        data = copy.deepcopy(DATA)
        del data["parts"]
        text = practices.markdown_of(PATH, data)
        self.assertNotIn("## Parts", text)


class Practices(helpers.FolderTest):
    """form and markdown, on a best practice of the kind `kind`."""

    def setUp(self) -> None:
        super().setUp()
        self.folder = os.path.join(self.base, "kind")
        self.path = os.path.join(self.folder, "best-practice.json")
        self.write_json(self.path, DATA)

    def test_form_fails_until_markdown_writes_it(self):
        self.assertEqual(ran("form", self.path)[0], 1)
        self.assertEqual(ran("markdown", self.path), (0, "", ""))
        self.assertEqual(
            self.read(os.path.join(self.folder, "best-practice.md")),
            practices.markdown_of(self.path, DATA),
        )
        self.assertEqual(ran("form", self.path), (0, "", ""))

    def test_form_fails_on_a_fault_of_the_form(self):
        data = copy.deepcopy(DATA)
        data["practices"].pop()
        self.write_json(self.path, data)
        ran("markdown", self.path)
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"practices.py: {self.path}: {practices.faults(data)[0]}", err)

    def test_form_holds_the_questions_to_the_template_beside_it(self):
        data = copy.deepcopy(DATA)
        del data["parts"]
        for question in data["necessary_conditions"]:
            question["about"] = "the whole"
        data["template"] = "template.md"
        self.write_json(self.path, data)
        self.write(os.path.join(self.folder, "template.md"), "# <P>\n\n## Use\n")
        ran("markdown", self.path)
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"practices.py: {self.path}: section Use has no condition about it", err)
        self.assertIn(
            "[template.md](template.md)", self.read(os.path.join(self.folder, "best-practice.md"))
        )

    def test_form_holds_the_questions_to_a_template_that_is_a_folder_and_keeps_its_files(self):
        data = copy.deepcopy(DATA)
        del data["parts"]
        for question in data["necessary_conditions"]:
            question["about"] = "the whole"
        data["template"] = "template"
        self.write_json(self.path, data)
        self.write(os.path.join(self.folder, "template", "skills", "up", "SKILL.md"), "# up\n")
        ran("markdown", self.path)
        self.assertEqual(
            ran("form", self.path),
            (1, "", f"practices.py: {self.path}: section skills has no condition about it\n"),
        )

    def test_form_fails_on_a_file_it_names_that_is_not_beside_it(self):
        self.write_json(self.path, dict(DATA, example="example.md"))
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"practices.py: {self.path}: its example example.md is not beside it", err)

    def test_form_fails_on_a_json_out_of_its_schema(self):
        self.write_json(self.path, {"goal": "g"})
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn("is out of its form", err)

    def test_form_fails_on_a_best_practice_that_names_no_kinds_it_takes(self):
        for key in ("inputs", "preconditions"):
            with self.subTest(key=key):
                data = copy.deepcopy(DATA)
                del data[key]
                self.write_json(self.path, data)
                code, _, err = ran("form", self.path)
                self.assertEqual(code, 1)
                self.assertIn(f'is out of its form: $: expected the key "{key}"', err)

    def test_form_fails_on_a_kind_it_takes_that_has_no_best_practice(self):
        self.write_json(self.path, dict(DATA, inputs=["gone"]))
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(
            f"practices.py: {self.path}: its input gone has no best practice beside it"
            " or among rn's own",
            err,
        )

    def test_form_fails_on_an_example_out_of_the_schema_that_is_its_template(self):
        data = copy.deepcopy(DATA)
        del data["parts"]
        for question in data["necessary_conditions"]:
            question["about"] = "goal, the whole"
        data.update(template="plan.schema.json", example="example.json")
        self.write_json(self.path, data)
        self.write_json(
            os.path.join(self.folder, "plan.schema.json"),
            {"$schema": "x", "type": "object", "properties": {"goal": {"type": "string"}}},
        )
        self.write_json(os.path.join(self.folder, "example.json"), {"goal": 1})
        ran("markdown", self.path)
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertEqual(
            err,
            f"practices.py: {self.path}: its example example.json is out of its template:"
            " $.goal: expected a string, found 1\n",
        )

    def test_form_fails_on_a_markdown_changed_by_hand(self):
        made = practices.markdown_of(self.path, DATA)
        for changed in (made + "More.\n", made[:-1]):
            with self.subTest(changed=changed[-6:]):
                self.write(os.path.join(self.folder, "best-practice.md"), changed)
                code, _, err = ran("form", self.path)
                self.assertEqual(code, 1)
                self.assertIn(
                    "best-practice.md is not as its JSON makes it; run practices.py markdown", err
                )

    def sourced(self) -> str:
        """Names a source for the example, and writes it with a figure. Gives the example's path."""
        self.write_json(self.path, dict(DATA, example="example.md", source="../doc/source.md"))
        self.write(os.path.join(self.base, "doc", "source.md"), "![A](images/a.svg) [b](b.md)\n")
        self.write(os.path.join(self.base, "doc", "images", "a.svg"), "<svg/>")
        ran("markdown", self.path)
        return os.path.join(self.folder, "example.md")

    def test_form_fails_until_example_copies_the_source_and_its_figures(self):
        example = self.sourced()
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"practices.py: {self.path}: {example} is not a copy of its source", err)
        self.assertIn("; run practices.py example", err)
        self.assertEqual(ran("example", self.path), (0, "", ""))
        self.assertEqual(self.read(example), "![A](images/a.svg) [b](../doc/b.md)\n")
        self.assertEqual(self.read(os.path.join(self.folder, "images", "a.svg")), "<svg/>")
        self.assertEqual(ran("form", self.path), (0, "", ""))

    def test_form_fails_on_a_copy_or_figure_changed_by_hand(self):
        example = self.sourced()
        ran("example", self.path)
        figure = os.path.join(self.folder, "images", "a.svg")
        cuts = [(f, lambda text: "changed") for f in (example, figure)]
        cuts += [(f, lambda text: text[:-1]) for f in (example, figure)]
        for changed, cut in cuts:
            with self.subTest(changed=changed, cut=cut("ab")):
                ran("example", self.path)
                self.write(changed, cut(self.read(changed)))
                code, _, err = ran("form", self.path)
                self.assertEqual(code, 1)
                self.assertIn(
                    f"{changed} is not a copy of its source; run practices.py example", err
                )

    def test_a_source_or_figure_not_there_is_named(self):
        self.sourced()
        os.remove(os.path.join(self.base, "doc", "images", "a.svg"))
        for command in ("form", "example"):
            with self.subTest(command=command):
                code, _, err = ran(command, self.path)
                self.assertEqual(code, 1)
                self.assertIn("a.svg, which its example copies, is not there", err)

    def test_a_source_with_no_example_to_copy_to_is_named(self):
        self.write_json(self.path, dict(DATA, source="../doc/source.md"))
        ran("markdown", self.path)
        for command in ("form", "example"):
            with self.subTest(command=command):
                code, _, err = ran(command, self.path)
                self.assertEqual(code, 1)
                self.assertIn("its source ../doc/source.md has no example to be copied to", err)

    def test_form_fails_on_a_figure_left_from_an_old_source_until_example_removes_it(self):
        self.sourced()
        ran("example", self.path)
        old = os.path.join(self.folder, "images", "old.svg")
        self.write(old, "<svg/>")
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(
            f"practices.py: {self.path}: {old} is neither the template's nor the example's;"
            " run practices.py example",
            err,
        )
        self.assertEqual(ran("example", self.path), (0, "", ""))
        self.assertFalse(os.path.exists(old))
        self.assertEqual(ran("form", self.path), (0, "", ""))

    def test_form_says_to_remove_a_leftover_where_no_source_makes_the_example(self):
        ran("markdown", self.path)
        stray = os.path.join(self.folder, "notes.md")
        self.write(stray, "n")
        code, _, err = ran("form", self.path)
        self.assertEqual(code, 1)
        self.assertIn(f"{stray} is neither the template's nor the example's; remove it", err)

    def test_example_leaves_every_file_where_the_source_cannot_be_copied(self):
        self.sourced()
        stray = os.path.join(self.folder, "notes.md")
        self.write(stray, "n")
        os.remove(os.path.join(self.base, "doc", "source.md"))
        self.assertEqual(ran("example", self.path)[0], 1)
        self.assertTrue(os.path.exists(stray))

    def test_example_names_a_best_practice_with_no_source(self):
        code, _, err = ran("example", self.path)
        self.assertEqual(code, 1)
        self.assertIn(
            f"practices.py: {self.path}: it names no source to copy its example from", err
        )

    def test_each_command_names_a_json_it_cannot_read(self):
        self.write(self.path, "{")
        for command in ("form", "markdown", "example"):
            with self.subTest(command=command):
                code, _, err = ran(command, self.path)
                self.assertEqual(code, 1)
                self.assertIn(f"practices.py: {self.path}: {self.path} is not JSON", err)
        self.assertFalse(os.path.exists(os.path.join(self.folder, "best-practice.md")))


if __name__ == "__main__":
    unittest.main()

"""The unit cases of template/check.py, rn's check of a deliverable against its kind's template,
through `faults` and `of_kind`, and of its command, `template`, through `main`. Whether a
document holds its template turns on each part of the template's form: its sections, items,
paragraphs, figures, and code blocks, what its notes let a document leave out, repeat, or say in
how many sentences, and how many words a sentence takes; and on the document's language, in which
a document other than English keeps the template's form but not its own words, and a sentence is
bounded by characters where its language writes no space between words. So the cases take, for
each part, the document that holds it and each way of leaving it, a sentence on both sides of each
limit, and a document in Japanese that holds the form and one that leaves it."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Any

import pytest
from fault import Wrong
from template.check import Fault, faults, figures, of_kind
from template.command import USAGE, main
from template.language import MOST_CHARACTERS, MOST_WORDS

# rn's folder, at the top of the repository four folders up from this file.
RN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4, "plugins", "rn")
)


def lines(*each: str) -> str:
    """The lines as one Markdown text."""
    return "\n".join(each) + "\n"


def note(*items: str) -> str:
    """A note of a template with the items, as the templates of rn's best practices write it."""
    return "\n".join(
        ["> [!NOTE]", "> DELETE_TEMPLATE_COMMENT:", *[f"> - {item}" for item in items]]
    )


def test_a_document_that_fills_each_slot_and_drops_each_note_has_no_fault():
    """Given a template with a section, an item, and a paragraph of slots, with a note, and a
    document that fills each slot and drops the note
    When the document is checked
    Then it has no fault"""
    template = lines(
        "# `<Product>`",
        "",
        "## Roles",
        "",
        "- `<role>`\\",
        "  `<who they are>`.",
        "",
        "`<Product>` is `<kind>`.",
        "",
        note("`<role>`: each kind of person."),
    )
    document = lines(
        "# rn", "", "## Roles", "", "- user\\", "  One who asks.", "", "rn is a plugin."
    )
    assert faults(template, document) == ()


def test_a_section_left_out_has_no_fault():
    """Given a template of sections A, B, and C, and a document without B
    When the document is checked
    Then it has no fault, as the maker leaves out a section that the deliverable's people don't
    need, such as a License that the person leaves out of a guide"""
    template = lines("# T", "", "## A", "", "## B", "", "## C")
    document = lines("# T", "", "## A", "", "## C")
    assert faults(template, document) == ()


def test_a_section_beside_the_templates_is_named():
    """Given a template of sections A and B, and a document with a section FAQ between them
    When the document is checked
    Then the one fault names FAQ"""
    template = lines("# T", "", "## A", "", "## B")
    document = lines("# T", "", "## A", "", "## FAQ", "", "## B")
    assert faults(template, document) == (Fault(5, '"## FAQ" lies beside the template'),)


def test_sections_out_of_order_are_named():
    """Given a template of sections A, B, and C, and a document of A, C, and B
    When the document is checked
    Then the one fault names the section out of its place"""
    template = lines("# T", "", "## A", "", "## B", "", "## C")
    document = lines("# T", "", "## A", "", "## C", "", "## B")
    assert faults(template, document) == (Fault(7, '"## B" lies beside the template'),)


def test_a_heading_with_a_slot_may_repeat():
    """Given a template whose section of level 3 is `S<n>`: `<path>`, and a document with two
    such sections
    When the document is checked
    Then it has no fault"""
    template = lines("# T", "", "## Sequences", "", "### `S<n>`: `<path>`", "", "`<step>`.")
    document = lines(
        "# T",
        "",
        "## Sequences",
        "",
        "### S1: a request",
        "",
        "Go.",
        "",
        "### S2: a point",
        "",
        "Ask.",
    )
    assert faults(template, document) == ()


def test_a_heading_reworded_leaves_the_form():
    """Given a template whose title is Product vision of `<Product>`, and a document whose title is
    Invoicer product vision
    When the document is checked
    Then the fault names the title by the template's words"""
    template = lines("# Product vision of `<Product>`")
    assert faults(template, lines("# Invoicer product vision")) == (
        Fault(
            1,
            '"# Invoicer product vision" leaves the form of the template\'s'
            ' "# Product vision of `<Product>`" at its line 1',
        ),
    )


def test_a_list_item_whose_first_words_hold_a_slot_may_repeat():
    """Given a template of one item `<requirement>`: `<check>` shows it., and a document of two
    such items
    When the document is checked
    Then it has no fault"""
    template = lines("# T", "", "- `<requirement>`: `<check>` shows it.")
    document = lines("# T", "", "- Git: `git --version` shows it.", "- gh: `gh` shows it.")
    assert faults(template, document) == ()


def test_a_list_item_whose_first_words_are_fixed_stands_once():
    """Given a template of the item Tries: `<tries>`., and a document with two such items
    When the document is checked
    Then the second lies beside the template"""
    template = lines("# T", "", "- Tries: `<tries>`.")
    document = lines("# T", "", "- Tries: parts.", "- Tries: more.")
    assert faults(template, document) == (Fault(4, '"- Tries: more." lies beside the template'),)


def test_items_past_the_most_their_note_gives_are_named():
    """Given a template whose item `<idea>` has a note of at most two, and a document of three
    When the document is checked
    Then the third is named as past the two"""
    template = lines("# T", "", "- `<idea>`.", "", note("`<idea>`: each idea, at most two."))
    document = lines("# T", "", "- One.", "- Two.", "- Three.")
    assert faults(template, document) == (
        Fault(5, '"- Three." goes past the 2 of the template\'s "- `<idea>`." at its line 3'),
    )


def test_a_nested_item_beside_the_template_is_named():
    """Given a template of an item without nested items, and a document whose item holds one
    When the document is checked
    Then the nested item lies beside the template"""
    template = lines("# T", "", "- `KR<n>.1`: `<key result>`.")
    document = lines("# T", "", "- KR1.1: the share.", "  - A role breaks a step.")
    assert faults(template, document) == (
        Fault(4, '"- A role breaks a step." lies beside the template'),
    )


def test_a_paragraph_whose_note_says_to_leave_it_out_may_be_left_out():
    """Given a template whose paragraph `<status>`. has a note that says to leave it out, and a
    document without it
    When the document is checked
    Then it has no fault"""
    template = lines(
        "# T",
        "",
        "`<status>`.",
        "",
        "End.",
        "",
        note("`<status>`: where. Leave it out where none."),
    )
    assert faults(template, lines("# T", "", "End.")) == ()


def test_a_paragraph_that_leads_into_items_that_may_be_left_out_may_go_with_them():
    """Given a template of a paragraph, then the fixed paragraph The choices made, and why:, which
    leads into items whose note says to leave them out, and a document of the first paragraph alone
    When the document is checked
    Then it has no fault"""
    template = lines(
        "# T",
        "",
        "Intro.",
        "",
        "The choices made, and why:",
        "",
        "- `<choice>` over `<other way>`",
        "",
        note("`<choice>`, `<other way>`: each choice. Leave them out where none."),
    )
    assert faults(template, lines("# T", "", "Intro.")) == ()


def test_a_paragraph_beside_the_template_is_named():
    """Given a template of one paragraph, and a document with a second
    When the document is checked
    Then the second lies beside the template"""
    template = lines("# T", "", "At the end, you have `<result>`.")
    document = lines("# T", "", "At the end, you have a pull request.", "", "You then merge it.")
    assert faults(template, document) == (
        Fault(5, '"You then merge it." lies beside the template'),
    )


def test_a_slot_with_more_sentences_than_its_note_gives_is_named():
    """Given a template whose paragraph `<answer>`. has a note of a sentence or two, and a document
    whose paragraph has three
    When the document is checked
    Then the fault names the three sentences and the one to two the template takes"""
    template = lines(
        "# T", "", "`<answer>`.", "", note("`<answer>`: in a sentence or two the part.")
    )
    document = lines("# T", "", "One. Two. Three.")
    assert faults(template, document) == (
        Fault(3, 'has 3 sentences, where the template\'s "`<answer>`." at its line 3 takes 1 to 2'),
    )


def test_a_slot_whose_note_gives_no_number_takes_one_sentence():
    """Given a template of the paragraph `<sign>`. with no number in its note, and a document
    whose paragraph has two sentences
    When the document is checked
    Then the fault names the two sentences and the one the template takes"""
    template = lines("# T", "", "`<sign>`.", "", note("`<sign>`: what shows it worked."))
    document = lines("# T", "", "It shows. Then it works.")
    assert faults(template, document) == (
        Fault(3, 'has 2 sentences, where the template\'s "`<sign>`." at its line 3 takes 1'),
    )


def test_a_note_that_says_to_leave_out_a_word_and_the_link_lets_both_go_or_stay():
    """Given a template of the paragraph `<Product>` tests by [`<shared rules>`](<path>), in unit
    tests., whose note says to leave out `by` and the link, and a document without them and one
    that keeps them
    When each document is checked
    Then neither has a fault"""
    template = lines(
        "# T",
        "",
        "`<Product>` tests by [`<shared rules>`](<path>), in unit tests.",
        "",
        note("`<shared rules>`, `<path>`: the rules. Leave out `by` and the link where none."),
    )
    assert faults(template, lines("# T", "", "rn tests, in unit tests.")) == ()
    document = lines("# T", "", "rn tests by [the guide](guide.md), in unit tests.")
    assert faults(template, document) == ()


def test_a_note_that_says_as_in_a_section_takes_that_sections_items():
    """Given a template whose Components note lets its choices be left out, and whose Deployment
    note says its choices are as in Components, and a document without Deployment's choice
    When the document is checked
    Then it has no fault"""
    template = lines(
        "# T",
        "",
        "## Components",
        "",
        note("`<choice>`: each choice. Leave them out where none."),
        "",
        "## Deployment",
        "",
        "`<start>`.",
        "",
        "- `<choice>` over it",
        "",
        note("`<choice>`: as in Components."),
    )
    document = lines("# T", "", "## Components", "", "## Deployment", "", "It starts.")
    assert faults(template, document) == ()


def test_a_note_of_the_template_kept_is_named():
    """Given a template with a note, and a document that keeps it
    When the document is checked
    Then the one fault names the note at its line"""
    template = lines("# T", "", note("`<x>`: a thing."))
    document = lines("# T", "", note("`<x>`: a thing."))
    assert faults(template, document) == (Fault(3, "keeps a note of the template"),)


def test_a_placeholder_of_the_template_kept_is_named():
    """Given a template of the item `<role>`, and a document that keeps `<role>`
    When the document is checked
    Then the one fault names the placeholder"""
    template = lines("# T", "", "- `<role>`")
    assert faults(template, lines("# T", "", "- `<role>`")) == (
        Fault(3, "keeps the template's placeholder <role>"),
    )


def test_a_placeholder_kept_as_a_line_of_a_code_block_is_named():
    """Given a template whose code block is <command>, and a document that keeps that line
    When the document is checked
    Then the one fault names the placeholder"""
    template = lines("# T", "", "```console", "<command>", "```")
    assert faults(template, lines("# T", "", "```console", "<command>", "```")) == (
        Fault(3, "keeps the template's placeholder <command>"),
    )


def test_a_slot_name_inside_longer_code_is_no_placeholder():
    """Given a template with the slot <result>, and a document whose code span holds
    "<result>" among other words
    When the document is checked
    Then it has no fault"""
    template = lines("# T", "", "At the end, you have `<result>`.")
    document = lines("# T", "", 'At the end, you have `{"result": "<result>"}`.')
    assert faults(template, document) == ()


def test_the_templates_own_figure_kept_is_named():
    """Given a template with the figure images/template-components.svg, and a document that keeps
    that path
    When the document is checked
    Then the one fault names the template's figure"""
    template = lines("# T", "", "![Parts](images/template-components.svg)")
    document = lines("# T", "", "![rn's parts](images/template-components.svg)")
    assert faults(template, document) == (
        Fault(3, "keeps the template's own figure images/template-components.svg"),
    )


def test_a_code_block_in_another_language_than_the_template_fixes_is_named():
    """Given a template whose code block is console, and a document whose code block is text
    When the document is checked
    Then the fault names the code block by the template's info string"""
    template = lines("# T", "", "```console", "<command>", "```")
    document = lines("# T", "", "```text", "claude plugin list", "```")
    assert faults(template, document) == (
        Fault(3, '"```text" leaves the form of the template\'s "```console" at its line 3'),
    )


def test_a_code_block_whose_language_is_a_slot_takes_any_language():
    """Given a template whose code block's info string is <language>, and a document whose code
    block is python
    When the document is checked
    Then it has no fault"""
    template = lines("# T", "", "```<language>", "<input>", "```")
    assert faults(template, lines("# T", "", "```python", "print(1)", "```")) == ()


def test_a_run_of_blocks_whose_note_says_each_may_repeat_as_a_whole():
    """Given a template of a paragraph, and then an input, `<Product>` shows:, and an output, whose
    note gives one pair for each exchange, and a document of the paragraph and two such runs
    When the document is checked
    Then it has no fault"""
    template = lines(
        "# T",
        "",
        "At the end, you have `<result>`.",
        "",
        "```<language>",
        "<input>",
        "```",
        "",
        "`<Product>` shows:",
        "",
        "```<language>",
        "<output>",
        "```",
        "",
        note(
            "`<result>`: what the reader has.",
            "`<input>`, `<output>`: as they were. One pair goes for each exchange.",
        ),
    )
    exchange = ("```text", "yes", "```", "", "rn shows:", "", "```text", "Done.", "```", "")
    document = lines("# T", "", "At the end, you have a pull request.", "", *exchange, *exchange)
    assert faults(template, document) == ()


def test_a_run_of_blocks_repeated_in_part_lacks_the_rest():
    """Given the template of an input, `<Product>` shows:, and an output, which repeats as a whole,
    and a document of one run and a second without its output
    When the document is checked
    Then the one fault names the output of the second run, at the run's last line"""
    template = lines(
        "# T",
        "",
        "```<language>",
        "<input>",
        "```",
        "",
        "`<Product>` shows:",
        "",
        "```<language>",
        "<output>",
        "```",
        "",
        note("`<input>`, `<output>`: as they were. One pair goes for each exchange."),
    )
    exchange = ("```text", "yes", "```", "", "rn shows:", "", "```text", "Done.", "```", "")
    document = lines("# T", "", *exchange, "```text", "no", "```", "", "rn shows:")
    assert faults(template, document) == (
        Fault(17, 'lacks the template\'s "```<language>" at its line 9'),
    )


def test_a_paragraph_whose_note_says_each_may_repeat():
    """Given a template of a fixed paragraph and the paragraph `<places>`., whose note says each top
    folder, and a document of the fixed paragraph and two more
    When the document is checked
    Then it has no fault"""
    template = lines(
        "# T", "", "Intro.", "", "`<places>`.", "", note("`<places>`: for each top folder.")
    )
    assert faults(template, lines("# T", "", "Intro.", "", "One.", "", "Two.")) == ()


def test_a_paragraph_whose_each_note_names_slots_of_two_levels_stands_once():
    """Given a template whose note says each problem, naming a heading's slot and the paragraph's
    under it, and a document with two paragraphs under the heading
    When the document is checked
    Then the second lies beside the template"""
    template = lines(
        "# T",
        "",
        "## How",
        "",
        "### `<problem>`",
        "",
        "`<answer>`.",
        "",
        note("`<problem>`, `<answer>`: each problem, and in a sentence or two the answer."),
    )
    document = lines("# T", "", "## How", "", "### Slow?", "", "No.", "", "Never.")
    assert faults(template, document) == (Fault(9, '"Never." lies beside the template'),)


def test_a_sentence_of_more_than_the_most_words_is_named():
    """Given a template of a free slot, and a document of a sentence of the most words and one of
    one word more
    When the document is checked
    Then the one fault names the longer one's number of words and its first words"""
    template = lines("# T", "", "`<body>`")
    most = " ".join(["word"] * MOST_WORDS) + "."
    sentence = " ".join(["word"] * (MOST_WORDS + 1)) + "."
    assert faults(template, lines("# T", "", f"{most} {sentence}")) == (
        Fault(
            3,
            f"has a sentence of {MOST_WORDS + 1} words, more than {MOST_WORDS}:"
            " word word word word word word ...",
        ),
    )


def test_a_free_slot_takes_any_blocks():
    """Given a template whose section is a slot alone, and a document whose section holds a list,
    a paragraph, and a code block
    When the document is checked
    Then it has no fault"""
    template = lines("# T", "", "## Steps", "", "`<steps>`")
    document = lines(
        "# T", "", "## Steps", "", "1. Read.", "2. Write.", "", "Then.", "", "```", "x", "```"
    )
    assert faults(template, document) == ()


def test_an_empty_document_lacks_the_title_at_its_first_line():
    """Given a template of a title, and an empty document
    When the document is checked
    Then the one fault, at line 1, names the title"""
    assert faults(lines("# T"), "") == (Fault(1, 'lacks the template\'s "# T" at its line 1'),)


def test_the_faults_come_in_the_order_of_the_documents_lines():
    """Given a document with a note kept at line 3, and a long sentence after it, at line 7
    When the document is checked
    Then the note's fault comes first"""
    template = lines("# T", "", "`<body>`")
    long = " ".join(["word"] * (MOST_WORDS + 1)) + "."
    document = lines("# T", "", note("`<x>`: a thing."), "", long)
    assert [each.line for each in faults(template, document)] == [3, 7]


def test_of_kind_gives_the_template_of_a_kind_that_has_one():
    """Given rn's folder
    When the template of readme is asked for
    Then it's the readme best practice's template.md"""
    assert of_kind(RN, "readme") == os.path.join(
        RN, "domain", "best-practices", "readme", "template.md"
    )


def test_of_kind_refuses_a_kind_without_a_template_naming_the_kinds_that_have_one():
    """Given rn's folder
    When the template of design-tree, which has a schema in its place, is asked for
    Then it raises Wrong naming the kind and each kind that has a Markdown template"""
    with pytest.raises(Wrong) as raised:
        of_kind(RN, "design-tree")
    assert str(raised.value) == (
        "no kind 'design-tree' has a Markdown template; the kinds that have one are architecture,"
        " code, product-vision, prompt, readme, software-design, test-design,"
        " test-implementation"
    )


@pytest.fixture
def folder(tmp_path: Any) -> str:
    return str(tmp_path)


def test_template_gives_0_and_prints_nothing_for_a_document_that_holds_its_kinds_template(
    folder: str,
):
    """Given a product vision that fills each slot of rn's template and drops its notes
    When `template product-vision <document>` runs
    Then it gives 0 and prints nothing"""
    document = lines(
        "# Product vision of tally",
        "",
        "## Roles",
        "",
        "- user\\",
        "  One who totals invoices.",
        "",
        "## Objectives and key results",
        "",
        "- O1: the user totals each invoice right.",
        "  - KR1.1: the share of totals that are wrong. Lower is better.",
        "  - KR1.2: the time to a total. Shorter is better.",
        "",
        "The first key result of each objective comes first. Keep a change that improves a key",
        "result only if none before it gets worse.",
        "Key results have no targets, as a measure made a target stops being a good measure, by",
        "Goodhart's law. They show whether a change brought its objective closer.",
        "",
        "## Concept",
        "",
        "tally adds each line as it's typed.",
        "",
        "- Lines added at once, for O1\\",
        "  The user sees each total grow.",
    )
    with open(os.path.join(folder, "vision.md"), "w", encoding="utf-8") as file:
        file.write(document.replace("`KR<n>.1`", "KR1.1"))
    assert main(["product-vision", "vision.md"], folder, RN) == (0, "", "")


def test_template_gives_1_with_each_fault_at_the_documents_path_and_line(folder: str):
    """Given a document of a title and a section FAQ
    When `template product-vision <document>` runs
    Then it gives 1, with each fault of the document on a line of its own, at its path and line,
    after a line on why the template holds and before a line on when to change the template"""
    with open(os.path.join(folder, "vision.md"), "w", encoding="utf-8") as file:
        file.write("# Product vision of tally\n\n## FAQ\n")
    before = (
        "rn's template check: the template holds only the vital few. Cut each place below as"
        " trivia, or put its vital point in the template's form."
    )
    after = (
        "Where the form would lose what the document's people need, keep it, and propose a"
        " change to the template."
    )
    code, printed, said = main(["product-vision", "vision.md"], folder, RN)
    assert (code, printed) == (1, "")
    assert said.splitlines() == [
        before,
        'vision.md:3: "## FAQ" lies beside the template',
        after,
    ]


def test_template_run_as_a_command_ends_with_what_main_gives(folder: str):
    """Given a document of a title and a section FAQ
    When `python3 domain/scripts/template product-vision <document>` runs in the document's
    folder
    Then it exits 1, prints nothing, and says the fault on its standard error, as a maker that
    runs the command reads only its exit code and what it says"""
    with open(os.path.join(folder, "vision.md"), "w", encoding="utf-8") as file:
        file.write("# Product vision of tally\n\n## FAQ\n")
    run = subprocess.run(
        [
            sys.executable,
            os.path.join(RN, "domain", "scripts", "template"),
            "product-vision",
            "vision.md",
        ],
        cwd=folder,
        capture_output=True,
        text=True,
        check=False,
    )
    assert (run.returncode, run.stdout) == (1, "")
    assert 'vision.md:3: "## FAQ" lies beside the template' in run.stderr.splitlines()


def test_template_gives_1_naming_a_document_that_isnt_there(folder: str):
    """Given no file vision.md
    When `template product-vision vision.md` runs
    Then it gives 1, naming the file"""
    assert main(["product-vision", "vision.md"], folder, RN) == (
        1,
        "",
        "template: vision.md: no such file to check against the template of product-vision\n",
    )


def test_template_gives_1_naming_a_document_that_isnt_utf_8(folder: str):
    """Given a file vision.md that isn't UTF-8
    When `template product-vision vision.md` runs
    Then it gives 1, naming the file and the encoding it takes"""
    with open(os.path.join(folder, "vision.md"), "wb") as file:
        file.write(b"# \xff\n")
    assert main(["product-vision", "vision.md"], folder, RN) == (
        1,
        "",
        "template: vision.md: isn't UTF-8 text, which the check of a template reads\n",
    )


def test_template_with_other_than_a_kind_a_document_and_a_language_gives_2_with_the_usage(
    folder: str,
):
    """Given four arguments
    When `template` runs
    Then it gives 2 with the usage"""
    assert main(["a", "b", "c", "d"], folder, RN) == (2, "", USAGE)


def test_a_link_whose_path_is_a_slot_takes_any_path_after_its_words():
    """Given a template of the paragraph See [the guide](<path>)., and a document that names a path
    When the document is checked
    Then it has no fault"""
    template = lines("# T", "", "See [the guide](<path>).")
    assert faults(template, lines("# T", "", "See [the guide](docs/guide.md).")) == ()


def test_a_block_is_named_by_its_first_60_characters():
    """Given a document whose two paragraphs beside the template have 60 and 61 characters
    When the document is checked
    Then the first is named whole, and the second by its first 60 characters, the rest marked left
    out"""
    whole = "a" * 59 + "."
    assert faults(lines("# T"), lines("# T", "", whole, "", "a" * 60 + ".")) == (
        Fault(3, f'"{whole}" lies beside the template'),
        Fault(5, f'"{"a" * 60}..." lies beside the template'),
    )


def test_a_paragraph_that_leads_into_items_that_must_stand_stands():
    """Given a template of the fixed paragraph What each decides alone:, which leads into items
    that must stand, and a document of the items alone
    When the document is checked
    Then the one fault names the paragraph"""
    template = lines("# T", "", "What each decides alone:", "", "- `<component>`")
    assert faults(template, lines("# T", "", "- user")) == (
        Fault(3, 'lacks the template\'s "What each decides alone:" at its line 3'),
    )


def test_a_placeholder_of_mermaid_kept_is_named():
    """Given a template whose Mermaid code block holds #lt;name#gt;, and a document that keeps it
    on a line of its own
    When the document is checked
    Then the one fault names the placeholder"""
    template = lines("# T", "", "```mermaid", "sequenceDiagram", "  A->>B: #lt;name#gt;", "```")
    document = lines("# T", "", "```mermaid", "sequenceDiagram", "#lt;name#gt;", "```")
    assert faults(template, document) == (Fault(3, "keeps the template's placeholder <name>"),)


def test_a_title_with_a_slot_stands_once():
    """Given a template whose title is `<Product>`, and a document with two titles
    When the document is checked
    Then the second lies beside the template"""
    assert faults(lines("# `<Product>`"), lines("# rn", "", "# rn")) == (
        Fault(3, '"# rn" lies beside the template'),
    )


def test_a_heading_a_level_below_the_templates_lies_beside_it():
    """Given a template of the section A at level 2, and a document whose section A is at level 3
    When the document is checked
    Then A at level 3 lies beside the template"""
    assert faults(lines("# T", "", "## A"), lines("# T", "", "### A")) == (
        Fault(3, '"### A" lies beside the template'),
    )


def test_a_slot_whose_note_gives_a_sentence_for_each_thing_takes_at_least_one():
    """Given a template of the paragraph Intro. `<places>`., whose note gives one sentence for each
    top folder, and a document whose paragraph is Intro. alone
    When the document is checked
    Then the faults name the paragraph out of the form, and its one sentence where the template
    takes two or more"""
    template = lines(
        "# T", "", "Intro. `<places>`.", "", note("`<places>`: one sentence for each top folder.")
    )
    assert faults(template, lines("# T", "", "Intro.")) == (
        Fault(3, '"Intro." leaves the form of the template\'s "Intro. `<places>`." at its line 3'),
        Fault(
            3,
            'has 1 sentence, where the template\'s "Intro. `<places>`." at its line 3 takes 2 or'
            " more",
        ),
    )


def test_a_note_holds_only_in_its_own_section():
    """Given a template whose section A has a note that lets `<x>`. be left out, and whose section
    B has `<x>`. too, without a note, and a document without both
    When the document is checked
    Then the one fault names B's `<x>`."""
    template = lines(
        "# T",
        "",
        "## A",
        "",
        "`<x>`.",
        "",
        note("`<x>`: a thing. Leave it out where none."),
        "",
        "## B",
        "",
        "`<x>`.",
    )
    assert faults(template, lines("# T", "", "## A", "", "## B")) == (
        Fault(5, 'lacks the template\'s "`<x>`." at its line 13'),
    )


def test_a_section_below_the_top_whose_note_says_to_leave_it_out_may_be_left_out():
    """Given a template whose section of level 3 is `<part>`, with a note of `<part>` that says to
    leave out each part where none, and a document without it
    When the document is checked
    Then it has no fault"""
    template = lines(
        "# T",
        "",
        "## Steps",
        "",
        "`<steps>`.",
        "",
        "### `<part>`",
        "",
        "`<part_steps>`.",
        "",
        note("`<part>`, `<part_steps>`: each part. Leave out each part where none."),
    )
    assert faults(template, lines("# T", "", "## Steps", "", "Go.")) == ()


def test_a_free_slot_holds_its_prose_to_the_most_words_and_not_its_code():
    """Given a template of the result sentence and the free slot `<run>`, and a document whose run
    holds a code block of a long line and a paragraph of one word more than the most
    When the document is checked
    Then the one fault names the paragraph's sentence"""
    template = lines("# T", "", "At the end, you have `<result>`.", "", "`<run>`")
    long = " ".join(["word"] * (MOST_WORDS + 1))
    document = lines(
        "# T", "", "At the end, you have a total.", "", "```console", long, "```", "", long + "."
    )
    assert faults(template, document) == (
        Fault(
            9,
            f"has a sentence of {MOST_WORDS + 1} words, more than {MOST_WORDS}:"
            " word word word word word word ...",
        ),
    )


def test_a_list_item_out_of_its_form_after_one_in_it_is_named_by_the_form():
    """Given a template of the item `<requirement>`: `<check>` shows it., and a document of one
    such item and then one that says what the check shows in its place
    When the document is checked
    Then the second item is named as leaving the template's form"""
    template = lines("# T", "", "- `<requirement>`: `<check>` shows it.")
    document = lines("# T", "", "- gh: `gh` shows it.", "- Git: `git --version` shows `git`.")
    assert faults(template, document) == (
        Fault(
            4,
            '"- Git: `git --version` shows `git`." leaves the form of the template\'s'
            ' "- `<requirement>`: `<check>` shows it." at its line 3',
        ),
    )


def test_a_table_whose_row_holds_slots_takes_a_row_for_each_thing():
    """Given a template of a table whose one row holds slots, and a document of that table with
    three rows
    When the document is checked
    Then it has no fault"""
    template = lines(
        "# T", "", "| Test type | Exit criteria |", "|---|---|", "| `<type>` | `<exit>` |"
    )
    document = lines(
        "# T",
        "",
        "| Test type | Exit criteria |",
        "|---|---|",
        "| Unit | coverage: 100% |",
        "| Integration | each case passes |",
        "| E2E | k = 3 |",
    )
    assert faults(template, document) == ()


def test_a_table_with_another_header_leaves_the_form():
    """Given a template of a table, and a document whose table names another column
    When the document is checked
    Then the fault names the header by the template's words"""
    template = lines(
        "# T", "", "| Test type | Exit criteria |", "|---|---|", "| `<type>` | `<exit>` |"
    )
    document = lines("# T", "", "| Type | Exit criteria |", "|---|---|", "| Unit | all pass |")
    assert faults(template, document) == (
        Fault(
            3,
            '"| Type | Exit criteria |" leaves the form of the template\'s'
            ' "| Test type | Exit criteria |" at its line 3',
        ),
    )


def test_a_row_without_a_cell_of_the_template_leaves_its_form():
    """Given a template of a table whose row has two cells of slots, and a document whose row has
    one
    When the document is checked
    Then the fault names the row by the template's words"""
    template = lines(
        "# T", "", "| Test type | Exit criteria |", "|---|---|", "| `<type>` | `<exit>` |"
    )
    document = lines(
        "# T", "", "| Test type | Exit criteria |", "|---|---|", "| Unit and all pass |"
    )
    assert faults(template, document) == (
        Fault(
            5,
            '"| Unit and all pass |" leaves the form of the template\'s "| `<type>` | `<exit>` |"'
            " at its line 5",
        ),
    )


def test_a_sentence_of_a_cell_holds_to_the_most_words():
    """Given a template of a table, and a document whose cell holds a sentence of one word more
    than the most, beside a short one
    When the document is checked
    Then the one fault names the cell's long sentence"""
    template = lines(
        "# T", "", "| Test type | Exit criteria |", "|---|---|", "| `<type>` | `<exit>` |"
    )
    long = " ".join(["word"] * (MOST_WORDS + 1))
    document = lines(
        "# T", "", "| Test type | Exit criteria |", "|---|---|", f"| Unit | All pass. {long}. |"
    )
    assert faults(template, document) == (
        Fault(
            5,
            f"has a sentence of {MOST_WORDS + 1} words, more than {MOST_WORDS}:"
            " word word word word word word ...",
        ),
    )


def test_a_note_that_says_to_leave_out_a_lead_paragraph_lets_it_and_its_items_go():
    """Given a template whose lead paragraph Strategies: leads into items, with a note that says to
    leave out Strategies where there's none, and a document without both
    When the document is checked
    Then it has no fault"""
    template = lines(
        "# T",
        "",
        "Strategies:",
        "",
        "- `<strategy>`\\",
        "  `<intent>`.",
        "",
        note("`<strategy>`, `<intent>`: each decision. Leave out Strategies where there's none."),
    )
    assert faults(template, lines("# T")) == ()


# A document in a language other than English.

# A template of a title, a section of roles, and a paragraph, with a note.
ROLES = lines(
    "# `<Product>`",
    "",
    "## Roles",
    "",
    "- `<role>`\\",
    "  `<who they are>`.",
    "",
    "`<Product>` is `<kind>`.",
    "",
    note("`<role>`: each kind of person."),
)


def test_a_japanese_document_of_the_templates_form_in_its_own_words_has_no_fault():
    """Given a template of a title, a section of roles, and a paragraph, and a document in
    Japanese of each part in its order, its heading in Japanese
    When the document is checked in Japanese
    Then it has no fault"""
    document = lines(
        "# rn", "", "## 役割", "", "- 利用者\\", "  頼む人です。", "", "rnはプラグインです。"
    )
    assert faults(ROLES, document, "Japanese") == ()


def test_a_document_in_japanese_words_checked_in_english_leaves_the_templates_words():
    """Given a template of a title, a section of roles, and a paragraph, and a document of each
    part in its order, its heading in Japanese
    When the document is checked with no language given, which is English
    Then the one fault names the section as beside the template, as its heading isn't Roles"""
    document = lines(
        "# rn", "", "## 役割", "", "- 利用者\\", "  頼む人です。", "", "rnはプラグインです。"
    )
    assert faults(ROLES, document) == (Fault(3, '"## 役割" lies beside the template'),)


def test_a_japanese_document_without_a_part_of_the_form_lacks_it():
    """Given a template of a section A that holds a paragraph and a section B, and a document in
    Japanese whose section holds the paragraph alone
    When the document is checked in Japanese
    Then the one fault names B as lacking"""
    template = lines("# T", "", "## A", "", "`<a>`.", "", "### B", "", "`<b>`.")
    document = lines("# 題", "", "## 甲", "", "段落です。")
    assert faults(template, document, "Japanese") == (
        Fault(5, 'lacks the template\'s "### B" at its line 7'),
    )


def test_a_japanese_document_without_a_section_takes_each_other_by_its_form():
    """Given a template of sections A of a paragraph, B of an item, and C of a paragraph, and a
    document in Japanese of a section of an item and then one of a paragraph
    When the document is checked in Japanese
    Then it has no fault, as its sections hold the form of B and C, A being left out"""
    template = lines(
        "# T", "", "## A", "", "`<a>`.", "", "## B", "", "- `<b>`.", "", "## C", "", "`<c>`."
    )
    document = lines("# 題", "", "## 乙", "", "- 項目です。", "", "## 丙", "", "段落です。")
    assert faults(template, document, "Japanese") == ()


def test_a_japanese_section_with_a_fault_inside_is_named_at_the_fault():
    """Given a template of a section A of a paragraph of one sentence and an item, and a document
    in Japanese whose section's paragraph has two sentences
    When the document is checked in Japanese
    Then the one fault names the paragraph's two sentences, not the section"""
    template = lines("# T", "", "## A", "", "`<a>`.", "", "- `<b>`.")
    document = lines("# 題", "", "## 甲", "", "一つ目です。二つ目です。", "", "- 項目です。")
    assert faults(template, document, "Japanese") == (
        Fault(5, 'has 2 sentences, where the template\'s "`<a>`." at its line 5 takes 1'),
    )


def test_a_japanese_row_without_a_cell_of_the_template_leaves_its_form():
    """Given a template of a table whose row has two cells, and a document in Japanese whose header
    has two cells of its own words and whose row has one
    When the document is checked in Japanese
    Then the one fault names the row, as a row keeps its number of cells in any language"""
    template = lines(
        "# T", "", "| Test type | Exit criteria |", "|---|---|", "| `<type>` | `<exit>` |"
    )
    document = lines("# 題", "", "| 種類 | 終了条件 |", "|---|---|", "| 単体のみ |")
    assert faults(template, document, "Japanese") == (
        Fault(
            5,
            '"| 単体のみ |" leaves the form of the template\'s "| `<type>` | `<exit>` |"'
            " at its line 5",
        ),
    )


def test_a_japanese_code_block_in_another_language_than_the_template_fixes_is_named():
    """Given a template whose code block is of the language console, and a document in Japanese
    whose code block is of text
    When the document is checked in Japanese
    Then the one fault names the code block, as a code block's language is no word of the
    document's"""
    template = lines("# T", "", "```console", "<command>", "```")
    document = lines("# 題", "", "```text", "ls", "```")
    assert faults(template, document, "Japanese") == (
        Fault(3, '"```text" leaves the form of the template\'s "```console" at its line 3'),
    )


def test_a_sentence_of_more_than_the_most_characters_is_named_in_a_language_without_spaces():
    """Given a template of a free slot, and a document in Chinese, named Simplified Chinese, of a
    sentence of the most characters, its full stop among them, and one of a character more
    When the document is checked in that language
    Then the one fault names the longer one's number of characters and its first characters"""
    template = lines("# T", "", "`<body>`")
    most = "い" * (MOST_CHARACTERS - 1) + "。"
    sentence = "あ" * MOST_CHARACTERS + "。"
    assert faults(template, lines("# 題", "", most + sentence), "Simplified Chinese") == (
        Fault(
            3,
            f"has a sentence of {MOST_CHARACTERS + 1} characters, more than {MOST_CHARACTERS}:"
            f" {'あ' * 20} ...",
        ),
    )


def test_a_sentence_of_more_than_the_most_words_is_named_in_a_language_with_spaces():
    """Given a template of a free slot, and a document in French, whose words have spaces between
    them, its sentence of 21 words and heading of its own words
    When the document is checked in French
    Then the one fault names its number of words"""
    template = lines("# T", "", "## Roles", "", "`<body>`")
    sentence = " ".join(["mot"] * (MOST_WORDS + 1)) + "."
    assert faults(template, lines("# T", "", "## Rôles", "", sentence), "French") == (
        Fault(
            5,
            f"has a sentence of {MOST_WORDS + 1} words, more than {MOST_WORDS}:"
            " mot mot mot mot mot mot ...",
        ),
    )


def test_faults_refuse_a_blank_language():
    """Given a template and a document
    When the document is checked in a language of spaces alone
    Then the check refuses it, saying what it takes"""
    with pytest.raises(Wrong, match="the language is blank; give the document's language"):
        faults(lines("# T"), lines("# T"), " ")


# The Japanese product vision of tally, on rn's template in its own words.
VISION_JA = lines(
    "# tallyのプロダクトビジョン",
    "",
    "## 役割",
    "",
    "- 利用者\\",
    "  請求書を合計する人です。",
    "",
    "## 目的と主要な結果",
    "",
    "- O1: 利用者が各請求書を正しく合計する。",
    "  - KR1.1: 誤った合計の割合。低いほど良い。",
    "  - KR1.2: 合計までの時間。短いほど良い。",
    "",
    "各目的の最初の主要な結果を先に置く。前の結果を悪くしない変更だけを残す。",
    "主要な結果に目標はなく、目標にした指標は良い指標でなくなる。変更が目的に近づけたかを示す。",
    "",
    "## コンセプト",
    "",
    "tallyは行を打つたびに足す。",
    "",
    "- 一度に足す行、O1のため\\",
    "  利用者は各合計が増えるのを見る。",
)


def test_template_with_a_language_holds_the_document_in_it(folder: str):
    """Given a product vision in Japanese on rn's template in its own words
    When `template product-vision <document> Japanese` runs
    Then it gives 0 and prints nothing"""
    with open(os.path.join(folder, "vision.md"), "w", encoding="utf-8") as file:
        file.write(VISION_JA)
    assert main(["product-vision", "vision.md", "Japanese"], folder, RN) == (0, "", "")


# The figures that a document of a template keeps of its own.


def test_figures_are_each_own_figure_that_a_note_names_but_the_templates_own():
    """Given a template with two figures of its own, images/template-a.svg and
    images/template-b.png, whose notes say the document keeps its own at images/a.svg and at
    images/b.png, naming one of them twice and the template's own once
    When its figures are asked
    Then they are images/a.svg and images/b.png, each once, in the order the notes name them"""
    template = lines(
        "# `<Product>`",
        "",
        "![A](images/template-a.svg)",
        "",
        note("The figure: the deliverable's own at images/a.svg, not images/template-a.svg."),
        "",
        "## More",
        "",
        "![B](images/template-b.png)",
        "",
        note("The figure: the deliverable's own, at images/b.png, beside images/a.svg."),
    )
    assert figures(template) == ["images/a.svg", "images/b.png"]


def test_a_figure_that_its_note_lets_the_document_leave_out_is_neither_kept_nor_asked():
    """Given a template whose figure's note says the document keeps its own at images/a.svg, and
    to leave it out where the answers show the mechanism without it
    When its figures are asked, and a document without the figure is checked
    Then there are none, and the document has no fault"""
    template = lines(
        "# T",
        "",
        "![A](images/template-a.svg)",
        "",
        note(
            "The figure: the deliverable's own at images/a.svg. Leave it out where the answers"
            " show the mechanism without it."
        ),
    )
    assert figures(template) == []
    assert faults(template, lines("# T")) == ()

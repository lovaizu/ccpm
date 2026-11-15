"""The property-based tests of record.py's check of a deliverable against its kind's template, as
rn's Test strategy names them: an AI writes each deliverable, so a document takes forms that no
developer foresees. Each finds no counterexample, by hypothesis, and quality.sh runs them in CI."""

from __future__ import annotations

import os
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from record.markdown import read
from record.template import MOST_WORDS, faults

# rn's folder, at the top of the repository four folders up from this file.
RN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 4, "plugins", "rn")
)

KINDS = ("product-vision", "readme", "architecture")
WORD = st.text("abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=8)
WORDS = st.lists(WORD, min_size=1, max_size=3).map(" ".join)


def template_of(kind: str) -> str:
    """The template of the kind among rn's best practices."""
    path = os.path.join(RN, "domain", "best-practices", kind, "template.md")
    with open(path, encoding="utf-8") as file:
        return file.read()


@st.composite
def parts(draw: Any) -> tuple[str, str]:
    """One part of a template's section, with the part of a document that fills it: a fixed
    paragraph, a paragraph of slots, a list item of slots, or a code block, each as Markdown."""
    fixed = draw(WORDS).capitalize() + "."
    shapes = [
        (fixed, fixed),
        ("`<a>` is `<b>`.", f"{draw(WORDS)} is {draw(WORDS)}."),
        ("- `<x>`: `<y>`.", f"- {draw(WORDS)}: {draw(WORDS)}."),
        ("```console\n<command>\n```", f"```console\n{draw(WORDS)}\n```"),
        ("```<language>\n<input>\n```", f"```text\n{draw(WORDS)}\n```"),
    ]
    return draw(st.sampled_from(shapes))


@st.composite
def filled(draw: Any) -> tuple[str, list[str]]:
    """A template of a title and sections of their own headings, with no note, and the blocks of
    a document that fills each of its slots, one block for each of the template's."""
    headings = draw(st.lists(WORD, min_size=1, max_size=4, unique=True))
    template, document = ["# Title"], ["# Title"]
    for heading in headings:
        template.append(f"## {heading.capitalize()}")
        document.append(f"## {heading.capitalize()}")
        for form, fill in draw(st.lists(parts(), min_size=1, max_size=3)):
            template.append(form)
            document.append(fill)
    return "\n\n".join(template) + "\n", document


@given(filled())
@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_document_that_fills_each_slot_of_a_template_holds_it(made: tuple[str, list[str]]):
    """Given any template of sections, paragraphs, items, and code blocks, and a document that
    fills each of its slots
    When the document is checked
    Then it has no fault"""
    template, document = made
    assert faults(template, "\n\n".join(document) + "\n") == ()


@given(filled(), st.data())
@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_document_without_a_block_of_its_template_has_a_fault(
    made: tuple[str, list[str]], data: Any
):
    """Given any template whose every block must stand, and a document that fills it but leaves
    out one block
    When the document is checked
    Then it has a fault"""
    template, document = made
    gone = data.draw(st.integers(0, len(document) - 1))
    left = "\n\n".join(document[:gone] + document[gone + 1 :]) + "\n"
    assert faults(template, left) != (), f"block {gone} left out is found"


@given(st.integers(1, 2 * MOST_WORDS), WORD)
@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_sentence_has_a_fault_only_past_the_most_words(count: int, word: str):
    """Given a sentence of any number of words, in a document whose template takes any blocks
    When the document is checked
    Then it has a fault only where the words are more than the most"""
    document = "# T\n\n" + " ".join([word] * count) + ".\n"
    found = faults("# T\n\n`<body>`\n", document) != ()
    assert found == (count > MOST_WORDS), f"a sentence of {count} words is found only past the most"


@given(st.sampled_from(KINDS), st.text(max_size=400))
@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_any_text_checked_against_a_template_gives_faults_at_its_lines(kind: str, text: str):
    """Given any text, and the template of a kind
    When the text is checked
    Then each fault lies at a line of the text, in the order of the lines"""
    lines = [each.line for each in faults(template_of(kind), text)]
    assert all(1 <= line <= text.count("\n") + 1 for line in lines), "each fault lies at a line"
    assert lines == sorted(lines), "the faults come in the order of the lines"


@given(st.text(max_size=400))
@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_any_text_reads_as_blocks_at_its_lines_in_order(text: str):
    """Given any text
    When it's read as Markdown
    Then each block lies at a line of the text, each after the one before it"""
    lines = [block.line for block in read(text)]
    assert all(1 <= line <= text.count("\n") + 1 for line in lines), "each block lies at a line"
    assert lines == sorted(set(lines)), "each block comes after the one before it"

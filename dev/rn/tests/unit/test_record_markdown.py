"""The unit cases of record/markdown.py, how record.py reads Markdown for rn's check of a
deliverable against its kind's template, through `read`, `sections`, `flat`, `sentences`, and
`words`. A block's kind, its line, and its words turn on how each Markdown construct starts and
ends, so the cases take one for each construct, and one for each way a list item or a code block
goes on or ends. A sentence and a word turn on the marks that end or join them, so the cases take
one for each."""

from __future__ import annotations

import pytest
from record.markdown import (
    CODE,
    FIGURE,
    HEADING,
    ITEM,
    PARAGRAPH,
    QUOTE,
    ROW,
    TABLE,
    Block,
    Node,
    flat,
    read,
    sections,
    sentences,
    words,
)


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_heading_gives_its_level_and_words():
    """Given a heading of level 2
    When the text is read
    Then it gives a heading block of level 2 with its words, at line 1"""
    assert read("## Non-goals") == (Block(HEADING, 1, "Non-goals", level=2),)


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_the_lines_of_a_paragraph_join_with_a_space():
    """Given a paragraph of two lines, after a blank line
    When the text is read
    Then it gives one paragraph at line 2 whose lines are joined by a space"""
    assert read("\nrn is a plugin\nfor Claude Code.") == (
        Block(PARAGRAPH, 2, "rn is a plugin for Claude Code."),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_line_that_ends_with_a_backslash_joins_the_next_with_a_newline():
    """Given a list item whose first line ends with a backslash
    When the text is read
    Then the item's words hold a newline in place of the backslash"""
    assert read("- user\\\n  One who asks rn.") == (Block(ITEM, 1, "user\nOne who asks rn."),)


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_list_item_holds_its_indented_lines_and_its_nested_items():
    """Given an item whose words go on an indented line, with a nested item under it, and a second
    item
    When the text is read
    Then the first item holds its two lines and the nested item, and the second stands beside it"""
    text = "- O1: the user\n  gets it.\n  - KR1.1: the share.\n- O2: more."
    assert read(text) == (
        Block(ITEM, 1, "O1: the user gets it.", children=(Block(ITEM, 3, "KR1.1: the share."),)),
        Block(ITEM, 4, "O2: more."),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_line_not_indented_right_after_an_items_words_goes_on_the_item():
    """Given an item whose second line isn't indented, and starts no block
    When the text is read
    Then the item's words hold the second line"""
    assert read("- rn doesn't merge.\nYou merge it.") == (
        Block(ITEM, 1, "rn doesn't merge. You merge it."),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_list_item_holds_a_paragraph_indented_after_a_blank_line():
    """Given an item, a blank line, and an indented paragraph, and then a paragraph not indented
    When the text is read
    Then the item holds the indented paragraph, and the last paragraph stands after it"""
    assert read("- Tries: parts.\n\n  More.\n\nAfter.") == (
        Block(ITEM, 1, "Tries: parts.", children=(Block(PARAGRAPH, 3, "More."),)),
        Block(PARAGRAPH, 5, "After."),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_list_item_that_starts_with_a_code_block_has_no_words_of_its_own():
    """Given a heading, a paragraph, and, after a blank line, an item whose first line opens a code
    block indented under it
    When the text is read
    Then the item at line 4 has no words, and holds the code block without the item's indent"""
    assert read("# T\nA.\n\n- ```text\n  a\n  ```") == (
        Block(HEADING, 1, "T", level=1),
        Block(PARAGRAPH, 2, "A."),
        Block(ITEM, 4, "", children=(Block(CODE, 4, "a", info="text"),)),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_list_item_whose_words_start_on_the_next_line_holds_them():
    """Given the marker 10. alone on its line, the item's words after a blank line, indented past
    the marker, and then a paragraph indented less
    When the text is read
    Then the item's words are those after the blank line, and the last paragraph stands after it"""
    assert read("10.\n\n    The words.\n\n   Other.") == (
        Block(ITEM, 1, "The words."),
        Block(PARAGRAPH, 5, "Other."),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_code_block_keeps_its_info_and_its_body_and_a_heading_inside_is_code():
    """Given a paragraph, and a code block of markdown at line 3 that holds a heading
    When the text is read
    Then it gives the paragraph, and one code block with the info string and the heading in its
    body"""
    assert read("Intro.\n\n```markdown\n## Steps\n\n1. Read.\n```\nAfter.") == (
        Block(PARAGRAPH, 1, "Intro."),
        Block(CODE, 3, "## Steps\n\n1. Read.", info="markdown"),
        Block(PARAGRAPH, 8, "After."),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_code_block_closes_only_at_a_fence_as_long_as_its_own():
    """Given a paragraph, and right under it a code block opened by four backticks that holds a
    fence of three
    When the text is read
    Then the fence of three stays in the body, and nothing follows the code block"""
    assert read("Intro.\n````md\n```\n````") == (
        Block(PARAGRAPH, 1, "Intro."),
        Block(CODE, 2, "```", info="md"),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_code_block_left_open_runs_to_the_end():
    """Given a code block with no closing fence
    When the text is read
    Then its body runs to the end of the text"""
    assert read("```console\nclaude plugin list") == (
        Block(CODE, 1, "claude plugin list", info="console"),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_paragraph_that_is_an_image_is_a_figure_with_its_alt_text_and_path():
    """Given a heading, and right under it a paragraph that is an image alone
    When the text is read
    Then it gives the heading, and a figure at line 2 with the alt text and the path"""
    assert read("# T\n![How rn works](images/how-it-works.svg)") == (
        Block(HEADING, 1, "T", level=1),
        Block(FIGURE, 2, "How rn works", info="images/how-it-works.svg"),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_quote_keeps_its_lines_without_their_mark():
    """Given a quote of two lines
    When the text is read
    Then it gives one quote whose lines lack the `>`"""
    assert read("> [!NOTE]\n> DELETE_TEMPLATE_COMMENT:") == (
        Block(QUOTE, 1, "[!NOTE]\nDELETE_TEMPLATE_COMMENT:"),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_blank_text_gives_no_block():
    """Given a text of blank lines
    When the text is read
    Then it gives no block"""
    assert read("\n  \n") == ()


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_heading_ends_the_paragraph_above_it():
    """Given a paragraph line right before a heading
    When the text is read
    Then the paragraph and the heading are two blocks"""
    assert read("Words.\n## Next") == (
        Block(PARAGRAPH, 1, "Words."),
        Block(HEADING, 2, "Next", level=2),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_sections_put_each_block_under_the_heading_above_it_to_the_next_of_its_level():
    """Given a title, a section of level 2 with a paragraph and a section of level 3, and a second
    section of level 2
    When the blocks are put into sections
    Then the title holds both sections of level 2, and the first holds the paragraph and the
    section of level 3"""
    title, roles, said, sub, concept = read("# T\n## Roles\nWords.\n### Sub\n## Concept")
    assert sections((title, roles, said, sub, concept)) == (
        Node(title, (Node(roles, (Node(said), Node(sub))), Node(concept))),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_sections_put_the_blocks_nested_in_an_item_under_it():
    """Given an item with a nested item
    When the blocks are put into sections
    Then the item's node holds the nested item's"""
    (item,) = read("- O1: more.\n  - KR1.1: less.")
    assert sections((item,)) == (Node(item, (Node(item.children[0]),)),)


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_flat_gives_each_block_and_then_each_nested_in_it():
    """Given an item with a nested item, and a paragraph after it
    When the blocks are flattened
    Then they come as the item, the nested item, and the paragraph"""
    item, after = read("- O1: more.\n  - KR1.1: less.\n\nAfter.")
    assert flat((item, after)) == [item, item.children[0], after]


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_sentences_split_after_a_full_stop_a_question_mark_or_an_exclamation_mark():
    """Given words of three sentences, ending with `.`, `?`, and `!`
    When they're split into sentences
    Then they give the three"""
    assert sentences("It runs. Does it stop? No!") == ["It runs.", "Does it stop?", "No!"]


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_sentences_split_after_a_quote_that_closes_a_sentence():
    """Given a sentence that ends inside a quote, and a sentence after it
    When they're split into sentences
    Then they give the two"""
    assert sentences('rn says "Done." You merge.') == ['rn says "Done."', "You merge."]


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_sentences_keep_a_code_span_and_a_link_whole():
    """Given a sentence whose code span and link each hold a full stop before a space
    When it's split into sentences
    Then it gives the one sentence"""
    text = "Run `a. b` as [the guide. Here](a.md) says."
    assert sentences(text) == [text]


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_sentences_split_at_a_newline():
    """Given words with a newline, which a line that ends with a backslash gives
    When they're split into sentences
    Then the line before the newline is a sentence of its own"""
    assert sentences("One generator over several\nIt costs less.") == [
        "One generator over several",
        "It costs less.",
    ]


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_sentences_of_blank_words_are_none():
    """Given words that are blank
    When they're split into sentences
    Then they give none"""
    assert sentences(" ") == []


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_words_count_a_code_span_as_one_word():
    """Given a sentence of two words and a code span of three
    When its words are counted
    Then they're three"""
    assert words("Run `gh auth status` now.") == 3


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_words_count_a_link_as_the_words_it_shows():
    """Given a sentence of one word and a link that shows two
    When its words are counted
    Then they're three"""
    assert words("See [the guide](../dev/plugin-development-guide.md#test).") == 3


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_words_count_no_mark_without_a_letter_or_a_digit():
    """Given a sentence of two words joined by a dash between spaces
    When its words are counted
    Then they're two"""
    assert words("rn - Lane") == 2


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_list_item_holds_an_item_indented_past_its_words():
    """Given an item, and a nested item indented further than the item's words
    When the text is read
    Then the item holds the nested item"""
    assert read("- a\n    - b") == (Block(ITEM, 1, "a", children=(Block(ITEM, 2, "b"),)),)


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_list_item_holds_a_paragraph_indented_past_its_words_after_a_blank_line():
    """Given an item, a blank line, and a paragraph indented further than the item's words
    When the text is read
    Then the item holds the paragraph"""
    assert read("- a\n\n    b") == (Block(ITEM, 1, "a", children=(Block(PARAGRAPH, 3, "b"),)),)


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_quote_ends_at_the_first_line_without_its_mark():
    """Given a heading, a quote of one line right under it, and a paragraph right under the quote
    When the text is read
    Then the quote at line 2 holds its line alone, and the paragraph stands after it"""
    assert read("# T\n> a\nAfter.") == (
        Block(HEADING, 1, "T", level=1),
        Block(QUOTE, 2, "a"),
        Block(PARAGRAPH, 3, "After."),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_fence_with_an_info_string_doesnt_close_a_code_block():
    """Given a heading, and right under it a code block opened by a bare fence, whose body is an
    indented fence with an info string
    When the text is read
    Then the body keeps the indented fence, and the code block has no info string"""
    assert read("# T\n```\n  ```py\n```") == (
        Block(HEADING, 1, "T", level=1),
        Block(CODE, 2, "  ```py"),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_code_block_closed_right_after_its_fence_is_empty():
    """Given a code block whose closing fence is the line after its opening one, and a paragraph
    When the text is read
    Then the code block has no body, and the paragraph stands after it"""
    assert read("```text\n```\nAfter.") == (
        Block(CODE, 1, "", info="text"),
        Block(PARAGRAPH, 3, "After."),
    )


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_sentences_keep_each_of_three_code_spans_whole():
    """Given a sentence with three code spans
    When it's split into sentences
    Then it gives the sentence as it was"""
    assert sentences("Run `a`, `b`, and `c`.") == ["Run `a`, `b`, and `c`."]


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_sections_end_a_section_at_a_heading_above_its_level():
    """Given a heading of level 2, and then one of level 1
    When the blocks are put into sections
    Then each stands alone"""
    lower, upper = read("## A\n# B")
    assert sections((lower, upper)) == (Node(lower), Node(upper))


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_a_table_holds_its_header_and_each_row_but_the_delimiter_row():
    """Given a table of a header, a delimiter row, and two rows, with spaces around its cells
    When the text is read
    Then it gives one table of the header, holding the two rows, each cell trimmed"""
    text = "| Test type | Exit criteria |\n|---|---|\n|  Unit | coverage: 100% |\n| E2E | k = 3 |"
    assert read(text) == (
        Block(
            TABLE,
            1,
            "| Test type | Exit criteria |",
            children=(Block(ROW, 3, "| Unit | coverage: 100% |"), Block(ROW, 4, "| E2E | k = 3 |")),
        ),
    )

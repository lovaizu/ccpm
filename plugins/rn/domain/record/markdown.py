"""Decides how record.py reads Markdown into blocks: each heading, paragraph, list item, fenced code
block, figure, and quote, with the line it starts on, and each list item with the blocks nested in
it, so that rn's check of a template reads a template and a document alike."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Kind(Enum):
    """The kind of a block of Markdown."""

    HEADING = "heading"
    PARAGRAPH = "paragraph"
    ITEM = "item"
    CODE = "code"
    FIGURE = "figure"
    QUOTE = "quote"


HEADING = Kind.HEADING
PARAGRAPH = Kind.PARAGRAPH
ITEM = Kind.ITEM
CODE = Kind.CODE
FIGURE = Kind.FIGURE
QUOTE = Kind.QUOTE

_HEADING = re.compile(r"(#{1,6})\s+(.+?)\s*")
_FENCE = re.compile(r"(\s*)(`{3,}|~{3,})(.*)")
_MARKER = re.compile(r"(\s*)(?:[-*+]|\d+[.)])(?:\s+|$)")
_QUOTE = re.compile(r"\s*>")
_FIGURE = re.compile(r"!\[(.*)\]\((\S+?)\)")
# A code span of Markdown, which the words of a block keep whole.
CODE_SPAN = re.compile(r"`[^`\n]*`")
_LINK = re.compile(r"!?\[([^\]\n]*)\]\([^)\n]*\)")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+|(?<=[.!?][\"')\]])\s+")


@dataclass(frozen=True)
class Block:
    """One block of Markdown: its kind, its line from 1, and its text:
    a heading's words; a paragraph's or a list item's own words, its lines joined by a space, or by
    a newline after a line that ends with a backslash; a code block's body; a figure's alt text; or
    a quote's lines without their `>`. `info` holds a code block's info string and a figure's path,
    `level` a heading's number of `#`, and `children` the blocks nested in a list item."""

    kind: Kind
    line: int
    text: str
    info: str = ""
    level: int = 0
    children: tuple[Block, ...] = ()


@dataclass(frozen=True)
class Node:
    """A block with the blocks under it: a heading with its section, or a list item with the blocks
    nested in it."""

    block: Block
    nodes: tuple[Node, ...] = ()


def read(text: str) -> tuple[Block, ...]:
    """Each block of the Markdown text in its order, with a list item's nested blocks in its
    `children`, and () for a text without one. A line inside a code block is the code's, whatever
    it starts with. Every text reads as blocks, so it refuses none."""
    return _read(text.split("\n"), 1)


def _read(lines: list[str], first: int) -> tuple[Block, ...]:
    """The blocks of the lines, the first of which is line `first` of the text."""
    blocks: list[Block] = []
    at = 0
    while at < len(lines):
        if lines[at].strip():
            block, at = _block(lines, at, first)
            blocks.append(block)
        else:
            at += 1
    return tuple(blocks)


def _block(lines: list[str], at: int, first: int) -> tuple[Block, int]:
    """The block that starts at the line `at`, and the line after it."""
    line = lines[at]
    heading = _HEADING.fullmatch(line)
    if heading:
        words = heading.group(2)
        return Block(HEADING, first + at, words, level=len(heading.group(1))), at + 1
    fence = _FENCE.fullmatch(line)
    if fence:
        return _code(lines, at, first, fence)
    if _QUOTE.match(line):
        return _quote(lines, at, first)
    marker = _MARKER.match(line)
    if marker:
        return _item(lines, at, first, marker)
    return _paragraph(lines, at, first)


def _starts_block(line: str) -> bool:
    """Whether the line starts a block, which ends a paragraph before it."""
    return bool(
        _HEADING.fullmatch(line)
        or _FENCE.fullmatch(line)
        or _QUOTE.match(line)
        or _MARKER.match(line)
    )


def _join(lines: list[str]) -> str:
    """The lines of a paragraph as one text: joined by a newline after a line that ends with a
    backslash, and by a space after any other."""
    text = ""
    for line in lines:
        words = " ".join(line.split())
        if text and not text.endswith("\n"):
            text += " "
        text += words[:-1].rstrip() + "\n" if words.endswith("\\") else words
    return text.rstrip("\n")


def _paragraph(lines: list[str], at: int, first: int) -> tuple[Block, int]:
    """The paragraph, or the figure that is all of it, that starts at the line `at`, which starts
    no other block."""
    end = at
    while end < len(lines) and lines[end].strip() and not _starts_block(lines[end]):
        end += 1
    text = _join(lines[at:end])
    figure = _FIGURE.fullmatch(text)
    if figure:
        return Block(FIGURE, first + at, figure.group(1), info=figure.group(2)), end
    return Block(PARAGRAPH, first + at, text), end


def _code(lines: list[str], at: int, first: int, opening: re.Match[str]) -> tuple[Block, int]:
    """The fenced code block that the fence opens at the line `at`, to its closing fence or to the
    end of the text."""
    indent, fence = len(opening.group(1)), opening.group(2)
    end = at + 1
    while end < len(lines) and not _closes(lines[end], fence):
        end += 1
    body = "\n".join(_dedent(line, indent) for line in lines[at + 1 : end])
    return Block(CODE, first + at, body, info=opening.group(3).strip()), end + 1


def _closes(line: str, fence: str) -> bool:
    """Whether the line closes a code block that the fence opened."""
    stripped = line.strip()
    return stripped.startswith(fence) and set(stripped) == {fence[0]}


def _dedent(line: str, indent: int) -> str:
    """The line without the first `indent` columns, or without the spaces it starts with where
    they're fewer."""
    return line[min(indent, _indent(line)) :]


def _quote(lines: list[str], at: int, first: int) -> tuple[Block, int]:
    """The quote that starts at the line `at`."""
    end = at
    while end < len(lines) and _QUOTE.match(lines[end]):
        end += 1
    text = "\n".join(re.sub(r"^\s*> ?", "", line) for line in lines[at:end])
    return Block(QUOTE, first + at, text), end


def _item(lines: list[str], at: int, first: int, marker: re.Match[str]) -> tuple[Block, int]:
    """The list item that the marker starts at the line `at`, with the blocks nested in it."""
    rest = lines[at][marker.end() :]
    indent = marker.end() if rest else len(marker.group(0).rstrip()) + 1
    body = [rest]
    end = at + 1
    while end < len(lines) and _in_item(lines, end, indent):
        body.append(_dedent(lines[end], indent))
        end += 1
    inside = _read(body, first + at)
    if inside and inside[0].kind == PARAGRAPH:
        return Block(ITEM, first + at, inside[0].text, children=inside[1:]), end
    return Block(ITEM, first + at, "", children=inside), end


def _in_item(lines: list[str], at: int, indent: int) -> bool:
    """Whether the line `at` lies in a list item whose words start at the column `indent`: a line
    indented that far, a blank line before one, or a line that starts no block, which goes on the
    paragraph above it, as a blank line before it would have ended the item."""
    line = lines[at]
    if not line.strip():
        after = [each for each in lines[at:] if each.strip()]
        return bool(after) and _indent(after[0]) >= indent
    if _indent(line) >= indent:
        return True
    return not _starts_block(line)


def _indent(line: str) -> int:
    """How many spaces the line starts with."""
    return len(line) - len(line.lstrip(" "))


def sections(blocks: tuple[Block, ...]) -> tuple[Node, ...]:
    """The blocks as nodes: each heading with the blocks up to the next heading of its level or
    above, and each list item with the blocks nested in it."""
    nodes: list[Node] = []
    at = 0
    while at < len(blocks):
        block = blocks[at]
        end = at + 1
        if block.kind == HEADING:
            while end < len(blocks) and not (
                blocks[end].kind == HEADING and blocks[end].level <= block.level
            ):
                end += 1
            nodes.append(Node(block, sections(blocks[at + 1 : end])))
        else:
            nodes.append(Node(block, sections(block.children)))
        at = end
    return tuple(nodes)


def flat(blocks: tuple[Block, ...]) -> list[Block]:
    """Each block, and each block nested in it."""
    return [each for block in blocks for each in (block, *flat(block.children))]


def sentences(text: str) -> list[str]:
    """The sentences of a block's words, in their order: split after `.`, `?`, or `!` before a
    space, and at each newline, which a line that ends with a backslash gives, with a code span or a
    link kept whole. [] for words that hold none."""
    spans: list[str] = []

    def hide(match: re.Match[str]) -> str:
        spans.append(match.group(0))
        return f"\0{len(spans) - 1}\0"

    hidden = _LINK.sub(hide, CODE_SPAN.sub(hide, text))
    found = []
    for line in hidden.split("\n"):
        found += [each for each in _SENTENCE_END.split(line) if each.strip()]
    return [re.sub(r"\0(\d+)\0", lambda m: spans[int(m.group(1))], each) for each in found]


def words(sentence: str) -> int:
    """How many words the sentence holds: a code span counts as one, a link as the words it shows,
    and a mark that holds no letter or digit, such as `-`, as none."""
    plain = _LINK.sub(r"\1", CODE_SPAN.sub("code", sentence))
    return sum(1 for word in plain.split() if re.search(r"\w", word))

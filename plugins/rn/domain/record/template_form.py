"""Decides how record.py reads a template of a best practice into its form: each part of it, the
words or the code block's language that a document's part must match, with each slot any words, and
what the template's notes let a document leave out, repeat, or say in how many sentences."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from record.markdown import (
    CODE,
    CODE_SPAN,
    FIGURE,
    HEADING,
    ITEM,
    PARAGRAPH,
    QUOTE,
    Block,
    Node,
    flat,
    sections,
    sentences,
)

_NOTE = "DELETE_TEMPLATE_COMMENT"
_SLOT = re.compile(r"<([^<>\s`][^<>`]*)>|#lt;(.+?)#gt;")
_TOKEN = re.compile(r"`[^`\n]*`|\[[^\]\n]*\]\([^)\n]*\)|<[^<>\s`][^<>`]*>")
_LONE_SLOT = re.compile(r"`<([^<>`]+)>`")
_ONLY_SLOTS = re.compile(r"\s*(?:(?:<[^<>\s`][^<>`]*>|#lt;.+?#gt;)\s*)+")
_MERMAID_SLOT = re.compile(r"#lt;(.+?)#gt;")
_NUMBERS = {"one": 1, "a": 1, "two": 2, "three": 3}
_SENTENCES = re.compile(
    r"\b(one|a|two|three)(?: or (two|three))? (?:short )?(?:sentence|clause)s?\b"
    r"(?: or (two|three)\b)?( for each\b)?",
    re.IGNORECASE,
)
_MOST = re.compile(r"\bat most (one|two|three|\d+)\b")
_LEAVE = re.compile(r"\bLeave\b")
_LEAVE_WORD = re.compile(r"Leave out `([^`<>]+)` and the link")
_LEAVE_SECTION = re.compile(r"Leave out ([A-Z][\w-]*(?: [\w-]+)*?) where")
_AS_IN = re.compile(r"\bas in ([A-Z][\w ]*?)\.")
_EACH = re.compile(r"\beach\b", re.IGNORECASE)


# Each dataclass marked frozen is never changed after it's made, so a mutant that unfreezes it
# changes nothing.
@dataclass(frozen=True)  # pragma: no mutate
class _Note:
    """One item of a note of the template: the slots it names, and what it says of them."""

    slots: frozenset[str]
    words: str


@dataclass
class Unit:
    """One part of the template's form: its block; the pattern that a document's block of its kind
    must match, None for a figure; whether it's a slot alone that takes any blocks; how many times
    it may stand: none where it's optional, more than once where it repeats, and at most `most`,
    None for no most; the unit that the document may go back to after it, so that the run of units
    from there to it repeats as a whole, None for none; how many sentences it takes, at least and at
    most, None for no most; and the units inside it."""

    # An annotation stays text, by `from __future__ import annotations`, so a mutant of its `|`
    # changes nothing.
    block: Block
    pattern: re.Pattern[str] | None  # pragma: no mutate
    free: bool
    optional: bool
    repeats: bool
    most: int | None  # pragma: no mutate
    back_to: int | None  # pragma: no mutate
    sentences: tuple[int, int | None]  # pragma: no mutate
    units: list[Unit]


@dataclass(frozen=True)  # pragma: no mutate
class Form:
    """The template's form: its units, and each slot it names, with each figure of its own."""

    units: list[Unit]
    slots: frozenset[str]
    figures: frozenset[str]


@dataclass(frozen=True)  # pragma: no mutate
class _Context:
    """What the units of the template are built with: the note items that hold for each block by
    its line, the headings of the sections that may be left out, and how many blocks of its
    section hold the slots of each note item, by the note items of the section and the item."""

    scoped: dict[int, tuple[_Note, ...]]
    optional: frozenset[str]
    holders: Counter[tuple[int, _Note]]


def form(blocks: tuple[Block, ...]) -> Form:
    """The form of the template whose blocks these are."""
    nodes = sections(blocks)
    scoped: dict[int, tuple[_Note, ...]] = {}
    _scope(nodes, (), _by_heading(nodes), scoped)
    holders = Counter(
        (id(scoped[node.block.line]), note)
        for node in _walk(nodes)
        if not is_note(node.block)
        for note in scoped[node.block.line]
        if note.slots & _slots(node.block)
    )
    optional = frozenset(words for note in _all_notes(nodes) for words in _left_sections(note))
    units = _units(nodes, _Context(scoped, optional, holders))
    slots = frozenset(name for block in flat(blocks) for name in _slots(block))
    figures = frozenset(block.info for block in flat(blocks) if block.kind == FIGURE)
    return Form(units, slots, figures)


def _walk(nodes: tuple[Node, ...]) -> list[Node]:
    """Each node, and each node under it."""
    return [each for node in nodes for each in (node, *_walk(node.nodes))]


def _slots(block: Block) -> set[str]:
    """The name of each slot of the block's words or info string, such as `role` for `<role>`."""
    return _names(f"{block.text}\n{block.info}")


def _names(text: str) -> set[str]:
    """The name of each slot of the text."""
    return {match.group(1) or match.group(2) for match in _SLOT.finditer(text)}


def is_note(block: Block) -> bool:
    """Whether the block is a note of the template."""
    return block.kind == QUOTE and _NOTE in block.text


def _notes_of(block: Block) -> list[_Note]:
    """The items of a note of the template."""
    items = re.findall(r"^- ((?:.|\n(?!- ))*)", block.text.partition(_NOTE)[2], re.MULTILINE)
    found = []
    for item in items:
        words = " ".join(item.split())
        label, _, said = words.partition(": ")
        slots = frozenset(_LONE_SLOT.findall(label)) if said else frozenset()
        found.append(_Note(slots, said or words))
    return found


def _own_notes(nodes: tuple[Node, ...]) -> list[_Note]:
    """Each item of each note among the nodes themselves."""
    return [note for node in nodes if is_note(node.block) for note in _notes_of(node.block)]


def _all_notes(nodes: tuple[Node, ...]) -> list[_Note]:
    """Each item of each note under the nodes, at any depth."""
    return [note for node in _walk(nodes) if is_note(node.block) for note in _notes_of(node.block)]


def _left_sections(note: _Note) -> list[str]:
    """The heading of the section that the note item says to leave out where it has nothing, if
    any."""
    match = _LEAVE_SECTION.search(note.words)
    return [match.group(1)] if match else []


# How the note items of a section of each level are gathered: the top section's from its own
# blocks, and a section of level 2's from each block under it.
_GATHER = {1: _own_notes, 2: _all_notes}


def _by_heading(nodes: tuple[Node, ...]) -> dict[str, tuple[_Note, ...]]:
    """The note items of each section, by its heading."""
    return {
        node.block.text: tuple(_all_notes(node.nodes))
        for node in _walk(nodes)
        if node.block.kind == HEADING
    }


def _scope(
    nodes: tuple[Node, ...],
    notes: tuple[_Note, ...],
    by_heading: dict[str, tuple[_Note, ...]],
    scoped: dict[int, tuple[_Note, ...]],
) -> None:
    """Keeps in `scoped`, by each block's line, the note items that hold for it: those of its
    section of level 2, at any depth, or, above the first such section, the top section's own."""
    for node in nodes:
        gather = _GATHER.get(node.block.level) if node.block.kind == HEADING else None
        own = _resolved(tuple(gather(node.nodes)), by_heading) if gather else notes
        scoped[node.block.line] = own
        _scope(node.nodes, own, by_heading, scoped)


def _resolved(
    notes: tuple[_Note, ...], by_heading: dict[str, tuple[_Note, ...]]
) -> tuple[_Note, ...]:
    """The note items, each that says `as in` a section replaced by that section's items of its
    slots."""
    found: list[_Note] = []
    for note in notes:
        match = _AS_IN.search(note.words)
        if match and match.group(1) in by_heading:
            found += [
                _Note(note.slots & other.slots, other.words)
                for other in by_heading[match.group(1)]
                if note.slots & other.slots
            ]
        else:
            found.append(note)
    return tuple(found)


def _units(nodes: tuple[Node, ...], context: _Context) -> list[Unit]:
    """The units of the sibling nodes of the template, its notes left out."""
    kept = tuple(node for node in nodes if not is_note(node.block))
    units = [_unit(node, context) for node in kept]
    for at in range(len(kept)):
        _repeat(units, kept, at, context)
    for unit, after in zip(units, units[1:]):
        unit.optional = unit.optional or _leads(unit, after)
    return units


def _unit(node: Node, context: _Context) -> Unit:
    """The unit of one node of the template."""
    block = node.block
    notes = [note for note in context.scoped[block.line] if note.slots & _slots(block)]
    free = block.kind == PARAGRAPH and bool(_LONE_SLOT.fullmatch(block.text))
    return Unit(
        block,
        _pattern_of(block, notes),
        free,
        _left_out(block, notes, context.optional),
        free or _repeats(block),
        next((_number(m.group(1)) for n in notes for m in [_MOST.search(n.words)] if m), None),
        None,
        _sentences_of(block.text, notes),
        _units(node.nodes, context),
    )


def _repeats(block: Block) -> bool:
    """Whether the block may stand more than once, by its form alone: a heading below the top
    whose words hold a slot, or a list item whose first words do."""
    if block.kind == HEADING:
        # A heading's level is at least 1, so a mutant of `>` to `!=` changes nothing.
        return block.level > 1 and bool(_slots(block))  # pragma: no mutate
    first = _TOKEN.match(block.text)
    return block.kind == ITEM and bool(first and _SLOT.search(first.group(0)))


def _left_out(block: Block, notes: list[_Note], optional: frozenset[str]) -> bool:
    """Whether the template lets the document leave the block out."""
    if block.kind == HEADING:
        return block.text in optional
    return any(
        _LEAVE.search(note.words)
        and not _LEAVE_WORD.search(note.words)
        and not _LEAVE_SECTION.search(note.words)
        for note in notes
    )


def _leads(unit: Unit, after: Unit) -> bool:
    """Whether the unit is a paragraph of fixed words that leads into a part that may be left out,
    and so may be left out with it."""
    block = unit.block
    return (
        block.kind == PARAGRAPH
        and not _slots(block)
        and block.text.endswith(":")
        and after.optional
    )


def _repeat(units: list[Unit], kept: tuple[Node, ...], at: int, context: _Context) -> None:
    """Lets the paragraph or code block at `at` repeat where a note item that says `each` names
    slots that it alone of its section holds, or lets the run of siblings from it to the last that
    holds them repeat, where several siblings hold them."""
    block = kept[at].block
    notes = context.scoped[block.line]
    for note in notes:
        holding = [i for i, node in enumerate(kept) if note.slots & _slots(node.block)]
        if not (_EACH.search(note.words) and holding and holding[0] == at):
            continue
        if holding[1:]:
            units[holding[-1]].back_to = at
        # A note's slots lie in at least the block itself, so a mutant of `==` to `<=` changes
        # nothing.
        elif (
            block.kind in (PARAGRAPH, CODE) and context.holders[(id(notes), note)] == 1
        ):  # pragma: no mutate
            units[at].repeats = True


def _number(word: str) -> int:
    """The number that the word or digits name."""
    return _NUMBERS[word] if word in _NUMBERS else int(word)


def _pattern_of(block: Block, notes: list[_Note]) -> re.Pattern[str] | None:
    """The pattern that the document's block must match: a heading's, a paragraph's, or an item's
    words, or a code block's info string, None for a figure."""
    if block.kind == FIGURE:
        return None
    if block.kind == CODE:
        return re.compile(".+" if _SLOT.search(block.info) else re.escape(block.info))
    word = next((m.group(1) for n in notes for m in [_LEAVE_WORD.search(n.words)] if m), "")
    return re.compile(_optional_link(block.text, word))


def _optional_link(text: str, word: str) -> str:
    """The pattern of the text, where the word and the link after it may be left out."""
    match = re.search(rf" {re.escape(word)} (\[[^\]]*\]\([^)]*\))", text) if word else None
    if not match:
        return _pattern(text)
    optional = f"(?: {re.escape(word)} {_pattern(match.group(1))})?"
    return _pattern(text[: match.start()]) + optional + _pattern(text[match.end() :])


def _pattern(text: str) -> str:
    """The pattern of the template's words: each slot any words on its line, `<n>` a number, a
    code span with or without its backticks, and each other word as it is."""
    found = ""
    at = 0
    for match in _TOKEN.finditer(text):
        found += re.escape(text[at : match.start()]) + _token(match.group(0))
        at = match.end()
    return found + re.escape(text[at:])


def _token(token: str) -> str:
    """The pattern of one code span, link, or slot of the template. A code span with a number, such
    as `S<n>`, may stand for several joined by commas or `and`, such as `S6, S7`."""
    if token.startswith("`"):
        one = f"`?{_pattern(token[1:-1])}`?"
        return f"{one}(?:(?:, | and ){one})*" if "<n>" in token else one
    if token.startswith("["):
        words, _, target = token[1:-1].partition("](")
        return rf"\[{_pattern(words)}\]\({_pattern(target)}\)"
    return r"\d+" if token == "<n>" else r"[^\n]+?"


def _sentences_of(text: str, notes: list[_Note]) -> tuple[int, int | None]:
    """How many sentences, least and most, None for no most, the template's words take: one for
    each of its sentences, and, for a sentence that is a slot alone, as many as its note says."""
    said = [
        _said(alone.group(1), notes) if alone else (1, 1)
        for alone in (_LONE_SLOT.fullmatch(each.rstrip(".:!?")) for each in sentences(text))
    ]
    highs = [high for _, high in said]
    most = sum(high for high in highs if high is not None)
    return sum(low for low, _ in said), None if None in highs else most


def _said(slot: str, notes: list[_Note]) -> tuple[int, int | None]:
    """How many sentences the notes say the slot takes, (1, 1) where they say none."""
    for note in notes:
        match = _SENTENCES.search(note.words)
        if slot in note.slots and match:
            least = _number(match.group(1).lower())
            most = match.group(2) or match.group(3)
            return least, None if match.group(4) else (_number(most) if most else least)
    return 1, 1


def kept(block: Block) -> set[str]:
    """The name of each slot that the document's block keeps as the template writes it: in its
    words, a code span that is the slot alone, or the slot outside a code span; in a code block, a
    line of slots alone, or a slot of Mermaid such as `#lt;name#gt;`, the info string among them."""
    if block.kind == CODE:
        lines = [*block.text.split("\n"), block.info]
        alone = [line for line in lines if _ONLY_SLOTS.fullmatch(line)]
        return _names("\n".join(alone)) | set(_MERMAID_SLOT.findall(block.text))
    spans = {span[2:-2] for span in CODE_SPAN.findall(block.text) if _LONE_SLOT.fullmatch(span)}
    return spans | _names(CODE_SPAN.sub("", block.text))

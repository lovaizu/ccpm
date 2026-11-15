"""Decides whether a document made by a best practice holds its kind's template and nothing beside
it: each part of the template's form in its order and no other, each in its words and its number of
sentences, no note or placeholder of the template left, and no sentence longer than MOST_WORDS
words; and where the template of each kind lies."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum

from fault import Wrong

from record.markdown import (
    CODE,
    FIGURE,
    HEADING,
    ITEM,
    PARAGRAPH,
    Block,
    Node,
    flat,
    read,
    sections,
    sentences,
    words,
)
from record.template_form import Form, Unit, form, is_note, kept

# The most words a sentence takes: the limit that ASD-STE100 sets for procedures, as the user
# judged the 25 of GOV.UK and the Australian Government Style Manual too long to read.
MOST_WORDS = 20


# A Fault is never changed after it's made, so a mutant that unfreezes it changes nothing.
@dataclass(frozen=True)  # pragma: no mutate
class Fault:
    """One place where the document leaves its template: the document's line from 1, and what's
    wrong there, in words from which its writer mends it."""

    line: int
    what: str


def of_kind(plugin_root: str, kind: str) -> str:
    """The path of the Markdown template of the kind among rn's best practices at `plugin_root`.
    Raises Wrong, naming the kinds that have one, where the kind has none."""
    folder = os.path.join(plugin_root, "domain", "best-practices")
    path = os.path.join(folder, kind, "template.md")
    if os.path.isfile(path):
        return path
    kinds = sorted(
        each
        for each in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, each, "template.md"))
    )
    raise Wrong(
        f"no kind {kind!r} has a Markdown template; the kinds that have one are {', '.join(kinds)}"
    )


def faults(template: str, document: str) -> tuple[Fault, ...]:
    """Each place where the Markdown text `document` leaves the Markdown text `template`, in the
    order of the document's lines, or () where it holds the template and nothing beside it."""
    shape = form(read(template))
    blocks = read(document)
    found = _paired(shape.units, _without_notes(blocks), 1)
    found += _notes_left(blocks) + _placeholders_left(blocks, shape) + _long_sentences(blocks)
    return tuple(sorted(found, key=lambda each: each.line))


def _without_notes(blocks: tuple[Block, ...]) -> tuple[Node, ...]:
    """The document's nodes, each note of the template left out, as _notes_left names them."""
    return _strip(sections(blocks))


def _strip(nodes: tuple[Node, ...]) -> tuple[Node, ...]:
    """The nodes without notes of the template, at any depth."""
    return tuple(Node(node.block, _strip(node.nodes)) for node in nodes if not is_note(node.block))


def _fit(unit: Unit, block: Block) -> int | None:
    """0 where the block holds the unit's form, 1 where it's of the unit's kind but not its form,
    and None where it's of another kind."""
    if unit.free:
        return None if block.kind == HEADING else 0
    if block.kind != unit.block.kind or block.level != unit.block.level:
        return None
    if unit.pattern is None:
        return 0
    said = block.info if block.kind == CODE else block.text
    return 0 if unit.pattern.fullmatch(said) else 1


# The weight of each fault in the pairing. A block paired out of its unit's form weighs more than
# a unit missing or a block beside, and less than both, so the pairing names a block moved from
# its place as missing there and beside where it stands, and a block reworded in its place as out
# of form.
# Among equals the pairing pairs first, so a mutant that moves a weight by one to an equal changes
# no pairing that the faults show.
_MISSING = 2  # pragma: no mutate
_BESIDE = 2  # pragma: no mutate
_OUT_OF_FORM = 3  # pragma: no mutate


class _Move(Enum):
    """What a step of the pairing does."""

    PAIR = "a block paired with the unit"
    AGAIN = "the run of units that repeats taken again"
    NEXT = "the next unit"
    BESIDE = "a block beside the units"


# A place in the pairing: the unit, the node, and whether the unit has stood, 0 or 1.
_Place = tuple[int, int, int]
# A step of the pairing: the weight of the fault it makes, what it does, and where it leads.
_Step = tuple[int, _Move, _Place]


def _weights(units: list[Unit], nodes: tuple[Node, ...]) -> dict[_Place, int]:
    """The least weight of faults from each place of the pairing to its end."""
    weight: dict[_Place, int] = {}
    for j in range(len(nodes), -1, -1):
        for used in (0, 1):
            for i in range(len(units), -1, -1):
                steps = _steps(units, nodes, (i, j, used))
                # Only the end has no step, and a weight there adds alike to every pairing, so a
                # mutant of the 0 changes no pairing.
                weight[(i, j, used)] = min(
                    (own + weight[to] for own, _, to in steps),
                    default=0,  # pragma: no mutate
                )
    return weight


def _steps(units: list[Unit], nodes: tuple[Node, ...], at: _Place) -> list[_Step]:
    """Each step from the place `at`, in the order the pairing takes among equals: a block paired,
    the run of units again, the next unit, a block beside. Each leads to a place whose weight
    _weights knows by then: one with the next node, or one with the same node and a later unit or
    a unit not yet stood."""
    i, j, used = at
    m, n = len(units), len(nodes)
    found: list[_Step] = []
    if i < m and j < n and (not used or units[i].repeats):
        fit = _fit(units[i], nodes[j].block)
        if fit is not None:
            found.append((fit * _OUT_OF_FORM, _Move.PAIR, (i, j + 1, 1)))
    back = units[i].back_to if i < m and used else None
    if back is not None:
        # Going back weighs nothing, and a weight of one either way only moves its pairings among
        # those that the weights of 2 and 3 above already part, so a mutant of it changes none.
        found.append((0, _Move.AGAIN, (back, j, 0)))  # pragma: no mutate
    if i < m:
        missing = _MISSING if not used and not units[i].optional else 0
        found.append((missing, _Move.NEXT, (i + 1, j, 0)))
    if j < n:
        found.append((_BESIDE, _Move.BESIDE, (i, j + 1, used)))
    return found


def _paired(units: list[Unit], nodes: tuple[Node, ...], where: int) -> list[Fault]:
    """Each fault of the nodes against the units, by the pairing with the least weight of faults,
    and of each pair's nodes inside against the unit's units. A unit missing at the end goes at the
    last node's line, or at `where` where there's no node."""
    weight = _weights(units, nodes)
    found: list[Fault] = []
    counts = [0] * len(units)
    at = (0, 0, 0)
    while at[0] < len(units) or at[1] < len(nodes):
        own, move, after = min(_steps(units, nodes, at), key=lambda step: step[0] + weight[step[2]])
        i, j, _ = at
        line = nodes[min(j, len(nodes) - 1)].block.line if nodes else where
        if move == _Move.BESIDE:
            found.append(Fault(line, f"{_shown(nodes[j].block)} lies beside the template"))
        elif move == _Move.NEXT and own:
            found.append(Fault(line, f"lacks {_from(units[i])}"))
        elif move == _Move.PAIR:
            counts[i] += 1
            found += _pair(units[i], nodes[j], counts[i])
        at = after
    return found


def _pair(unit: Unit, node: Node, count: int) -> list[Fault]:
    """The faults of a block paired with a unit, and of the blocks inside it."""
    block = node.block
    found: list[Fault] = []
    if _fit(unit, block):
        found.append(Fault(block.line, f"{_shown(block)} leaves the form of {_from(unit)}"))
    if unit.most is not None and count > unit.most:
        found.append(
            Fault(block.line, f"{_shown(block)} goes past the {unit.most} of {_from(unit)}")
        )
    if unit.free:
        return found
    if block.kind in (PARAGRAPH, ITEM):
        found += _counted(unit, block)
    return found + _paired(unit.units, node.nodes, block.line)


def _counted(unit: Unit, block: Block) -> list[Fault]:
    """The fault of a paragraph or an item whose sentences are fewer or more than its unit takes."""
    least, most = unit.sentences
    count = len(sentences(block.text))
    if least <= count and (most is None or count <= most):
        return []
    takes = f"{least} or more" if most is None else f"{least} to {most}"
    if most == least:
        takes = f"{least}"
    noun = "sentence" if count == 1 else "sentences"
    return [Fault(block.line, f"has {count} {noun}, where {_from(unit)} takes {takes}")]


def _shown(block: Block) -> str:
    """The block as a writer finds it: its first words, after its Markdown mark."""
    mark = {HEADING: "#" * block.level + " ", ITEM: "- ", CODE: "```", FIGURE: "!["}.get(
        block.kind, ""
    )
    said = " ".join((block.info if block.kind == CODE else block.text).split())
    return f'"{mark}{said[:60]}{"..." if len(said) > 60 else ""}"'


def _from(unit: Unit) -> str:
    """The unit, named by its words and its line in the template."""
    return f"the template's {_shown(unit.block)} at its line {unit.block.line}"


def _notes_left(blocks: tuple[Block, ...]) -> list[Fault]:
    """A fault for each note of the template that the document keeps."""
    return [
        Fault(each.line, "keeps a note of the template") for each in flat(blocks) if is_note(each)
    ]


def _placeholders_left(blocks: tuple[Block, ...], form: Form) -> list[Fault]:
    """A fault for each slot or figure of the template that the document keeps."""
    found = []
    for block in (each for each in flat(blocks) if not is_note(each)):
        for name in sorted(kept(block) & form.slots):
            found.append(Fault(block.line, f"keeps the template's placeholder <{name}>"))
        if block.info in form.figures:
            found.append(Fault(block.line, f"keeps the template's own figure {block.info}"))
    return found


def _long_sentences(blocks: tuple[Block, ...]) -> list[Fault]:
    """A fault for each sentence of a paragraph or an item that holds more than MOST_WORDS words."""
    found = []
    for block in flat(blocks):
        if block.kind not in (PARAGRAPH, ITEM):
            continue
        for sentence in sentences(block.text):
            count = words(sentence)
            if count > MOST_WORDS:
                begins = " ".join(sentence.split()[:6])
                found.append(
                    Fault(
                        block.line,
                        f"has a sentence of {count} words, more than {MOST_WORDS}: {begins} ...",
                    )
                )
    return found

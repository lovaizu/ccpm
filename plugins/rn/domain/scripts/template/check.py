"""Decides whether a document made by a best practice holds its kind's template and nothing beside
it: each part of the template's form in its order and no other, each in its words, where the
document's language keeps them, and its number of sentences, no note or placeholder of the template
left, and no sentence longer than its language takes; where the template of each kind lies; and
which figures a document of a template keeps of its own."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from enum import Enum

from fault import Wrong

from template.form import Form, Unit, form, is_note, kept
from template.language import ENGLISH, Language, of
from template.markdown import (
    CODE,
    FIGURE,
    HEADING,
    ITEM,
    PARAGRAPH,
    ROW,
    TABLE,
    Block,
    Node,
    cells,
    flat,
    read,
    sections,
    sentences,
)

# The file of a kind's template, in the folder of its best practice.
TEMPLATE = "template.md"
# The file of a figure, as a template's note names it, such as images/how-it-works.svg.
_FIGURE_FILE = re.compile(r"[\w./-]+\.(?:svg|png|jpe?g|gif|webp)\b")


@dataclass(frozen=True)
class Fault:
    """One place where the document leaves its template: the document's line from 1, and what's
    wrong there, in words from which its writer mends it."""

    line: int
    what: str


def of_kind(plugin_root: str, kind: str) -> str:
    """The path of the Markdown template of the kind among rn's best practices at `plugin_root`.
    Raises Wrong, naming the kinds that have one, where the kind has none."""
    folder = os.path.join(plugin_root, "domain", "best-practices")
    path = os.path.join(folder, kind, TEMPLATE)
    if os.path.isfile(path):
        return path
    kinds = sorted(
        each for each in os.listdir(folder) if os.path.isfile(os.path.join(folder, each, TEMPLATE))
    )
    raise Wrong(
        f"no kind {kind!r} has a Markdown template; the kinds that have one are {', '.join(kinds)}"
    )


def figures(template: str) -> list[str]:
    """The figures that a document of the Markdown text `template` keeps of its own, by their
    paths from the document's folder, in the order the template names them, each once: each file
    of a figure that a note of the template names, as the meta best practice has each note say
    where the deliverable keeps its own figure, but the template's own figures. [] where the notes
    name none."""
    blocks = read(template)
    own = form(blocks).figures
    named = [
        found
        for block in flat(blocks)
        if is_note(block)
        for found in _FIGURE_FILE.findall(block.text)
        if found not in own
    ]
    return list(dict.fromkeys(named))


def faults(template: str, document: str, language: str = ENGLISH) -> tuple[Fault, ...]:
    """Each place where the Markdown text `document` leaves the Markdown text `template`, in the
    order of the document's lines, or () where it holds the template and nothing beside it.

    `language` is the document's, by its name, such as English or Japanese. In English the
    document keeps the template's own words. In any other it keeps each part of the form in its
    order, its kind, its heading's level, its row's number of cells, its code block's language, and
    its number of sentences, in words of its own. A sentence takes as many words or characters as
    `template.language.of` gives the language. Raises Wrong where the language is blank."""
    held = of(language)
    shape = form(read(template))
    blocks = read(document)
    found = _Pairing(held.own_words).paired(shape.units, _without_notes(sections(blocks)), 1)
    found += _notes_left(blocks) + _placeholders_left(blocks, shape)
    found += _long_sentences(blocks, held)
    return tuple(sorted(found, key=lambda each: each.line))


def _without_notes(nodes: tuple[Node, ...]) -> tuple[Node, ...]:
    """The nodes without notes of the template, at any depth, as _notes_left names them."""
    return tuple(
        Node(node.block, _without_notes(node.nodes)) for node in nodes if not is_note(node.block)
    )


# The weight of each fault in the pairing. A block paired out of its unit's form weighs more than
# a unit missing or a block beside, and less than both, so the pairing names a block moved from
# its place as missing there and beside where it stands, and a block reworded in its place as out
# of form.
_MISSING = 2
_BESIDE = 2
_OUT_OF_FORM = 3
# Taking a run of units again weighs nothing.
_AGAIN = 0


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


class _Pairing:
    """The pairing of a document's nodes with the template's units by the least weight of faults.

    Where the document keeps the template's own words, they tell which unit a block stands for,
    so a step weighs the fault of its own block alone. Where it doesn't, only the form tells, so a
    pair weighs too the faults inside it, and a block beside weighs as each block under it beside,
    so that the pairing takes for each part the unit whose form it holds, such as the section after
    one left out, and names a fault inside a part at its place, not the part as beside."""

    def __init__(self, own_words: bool):
        self.own_words = own_words
        # The least weight of the pairing of each run of units with each run of nodes, by their
        # identities, as a pair of a document without the template's words weighs its inside.
        self._known: dict[tuple[int, int], dict[_Place, int]] = {}

    def _fit(self, unit: Unit, block: Block) -> int | None:
        """0 where the block holds the unit's form, 1 where it's of the unit's kind but not its
        form, and None where it's of another kind."""
        if unit.free:
            return None if block.kind == HEADING else 0
        if block.kind != unit.block.kind or block.level != unit.block.level:
            return None
        return 0 if self._holds(unit, block) else 1

    def _holds(self, unit: Unit, block: Block) -> bool:
        """Whether the block, of the unit's kind and level, holds the unit's form: its words, or,
        without the template's own words, a table's header or row its number of cells, and a code
        block its language in either, as a code block's language is no word of the document's."""
        if unit.pattern is None:
            return True
        if block.kind == CODE:
            return bool(unit.pattern.fullmatch(block.info))
        if self.own_words:
            return bool(unit.pattern.fullmatch(block.text))
        if block.kind in (TABLE, ROW):
            return len(cells(block.text)) == len(cells(unit.block.text))
        return True

    def _weights(self, units: list[Unit], nodes: tuple[Node, ...]) -> dict[_Place, int]:
        """The least weight of faults from each place of the pairing to its end."""
        key = (id(units), id(nodes))
        if key in self._known:
            return self._known[key]
        weight: dict[_Place, int] = {}
        for j in range(len(nodes), -1, -1):
            for used in (0, 1):
                for i in range(len(units), -1, -1):
                    steps = self._steps(units, nodes, (i, j, used))
                    # Only the end has no step, and a weight there adds alike to every pairing.
                    weight[(i, j, used)] = min(
                        (own + weight[to] for own, _, to in steps),
                        default=0,
                    )
        self._known[key] = weight
        return weight

    def _steps(self, units: list[Unit], nodes: tuple[Node, ...], at: _Place) -> list[_Step]:
        """Each step from the place `at`, in the order the pairing takes among equals: a block
        paired, the run of units again, the next unit, a block beside. Each leads to a place whose
        weight _weights knows by then: one with the next node, or one with the same node and a
        later unit or a unit not yet stood."""
        i, j, used = at
        m, n = len(units), len(nodes)
        found: list[_Step] = []
        pairing = self._pairing(units[i], nodes[j], used) if i < m and j < n else None
        if pairing is not None:
            found.append((pairing, _Move.PAIR, (i, j + 1, 1)))
        back = units[i].back_to if i < m and used else None
        if back is not None:
            found.append((_AGAIN, _Move.AGAIN, (back, j, 0)))
        if i < m:
            missing = _MISSING if not used and not units[i].optional else 0
            found.append((missing, _Move.NEXT, (i + 1, j, 0)))
        if j < n:
            found.append((self._beside(nodes[j]), _Move.BESIDE, (i, j + 1, used)))
        return found

    def _pairing(self, unit: Unit, node: Node, used: int) -> int | None:
        """The weight of the faults of pairing the node with the unit, which has stood where
        `used` is 1, or None where they can't pair: where the block is of another kind, or the unit
        has stood and doesn't repeat. A unit that has stood takes another block out of its form at
        the weight of a block beside, so that the fault names the form the block leaves. Without
        the template's own words, the pair weighs too the faults inside it."""
        fit = self._fit(unit, node.block) if not used or unit.repeats else None
        if fit is None:
            return None
        own = fit * (_BESIDE if used else _OUT_OF_FORM)
        if self.own_words or unit.free:
            return own
        prose = node.block.kind in (PARAGRAPH, ITEM)
        counted = _OUT_OF_FORM if prose and _counted(unit, node.block) else 0
        return own + counted + self._weights(unit.units, node.nodes)[(0, 0, 0)]

    def _beside(self, node: Node) -> int:
        """The weight of the node beside the units: one block's, or, without the template's own
        words, one for the node and each node under it."""
        if self.own_words:
            return _BESIDE
        return _BESIDE + sum(self._beside(each) for each in node.nodes)

    def paired(self, units: list[Unit], nodes: tuple[Node, ...], where: int) -> list[Fault]:
        """Each fault of the nodes against the units, by the pairing with the least weight of
        faults, and of each pair's nodes inside against the unit's units. A unit missing at the end
        goes at the last node's line, or at `where` where there's no node."""
        weight = self._weights(units, nodes)
        found: list[Fault] = []
        counts = [0] * len(units)
        at = (0, 0, 0)
        while at[0] < len(units) or at[1] < len(nodes):
            own, move, after = min(
                self._steps(units, nodes, at), key=lambda step: step[0] + weight[step[2]]
            )
            i, j, _ = at
            line = nodes[min(j, len(nodes) - 1)].block.line if nodes else where
            if move == _Move.BESIDE:
                found.append(Fault(line, f"{_shown(nodes[j].block)} lies beside the template"))
            elif move == _Move.NEXT and own:
                found.append(Fault(line, f"lacks {_from(units[i])}"))
            elif move == _Move.PAIR:
                counts[i] += 1
                found += self._pair(units[i], nodes[j], counts[i])
            at = after
        return found

    def _pair(self, unit: Unit, node: Node, count: int) -> list[Fault]:
        """The faults of a block paired with a unit, and of the blocks inside it."""
        block = node.block
        found: list[Fault] = []
        if self._fit(unit, block):
            found.append(Fault(block.line, f"{_shown(block)} leaves the form of {_from(unit)}"))
        if unit.most is not None and count > unit.most:
            found.append(
                Fault(block.line, f"{_shown(block)} goes past the {unit.most} of {_from(unit)}")
            )
        if unit.free:
            return found
        if block.kind in (PARAGRAPH, ITEM):
            found += _counted(unit, block)
        return found + self.paired(unit.units, node.nodes, block.line)


def _counted(unit: Unit, block: Block) -> list[Fault]:
    """The fault of a paragraph or an item whose sentences are fewer or more than its unit takes."""
    least, most = unit.sentences
    count = len(sentences(block.text))
    if least <= count and (most is None or count <= most):
        return []
    if most == least:
        takes = f"{least}"
    elif most is None:
        takes = f"{least} or more"
    else:
        takes = f"{least} to {most}"
    noun = "sentence" if count == 1 else "sentences"
    return [Fault(block.line, f"has {count} {noun}, where {_from(unit)} takes {takes}")]


# The most characters of a block's words that a fault shows, enough for its writer to find it.
_SHOWN = 60


def _shown(block: Block) -> str:
    """The block as a writer finds it: its first words, after its Markdown mark."""
    mark = {HEADING: "#" * block.level + " ", ITEM: "- ", CODE: "```", FIGURE: "!["}.get(
        block.kind, ""
    )
    said = " ".join((block.info if block.kind == CODE else block.text).split())
    return f'"{mark}{said[:_SHOWN]}{"..." if len(said) > _SHOWN else ""}"'


def _from(unit: Unit) -> str:
    """The unit, named by its words and its line in the template."""
    return f"the template's {_shown(unit.block)} at its line {unit.block.line}"


def _notes_left(blocks: tuple[Block, ...]) -> list[Fault]:
    """A fault for each note of the template that the document keeps."""
    return [
        Fault(each.line, "keeps a note of the template") for each in flat(blocks) if is_note(each)
    ]


def _placeholders_left(blocks: tuple[Block, ...], shape: Form) -> list[Fault]:
    """A fault for each slot or figure of the template that the document keeps."""
    found = []
    for block in (each for each in flat(blocks) if not is_note(each)):
        for name in sorted(kept(block) & shape.slots):
            found.append(Fault(block.line, f"keeps the template's placeholder <{name}>"))
        if block.info in shape.figures:
            found.append(Fault(block.line, f"keeps the template's own figure {block.info}"))
    return found


def _long_sentences(blocks: tuple[Block, ...], language: Language) -> list[Fault]:
    """A fault for each sentence of a paragraph, an item, or a cell of a row that holds more words
    or characters than its language takes."""
    found = []
    for block in flat(blocks):
        for sentence in (each for text in _prose(block) for each in sentences(text)):
            count = language.length(sentence)
            if count > language.most:
                found.append(
                    Fault(
                        block.line,
                        f"has a sentence of {count} {language.unit}, more than {language.most}:"
                        f" {language.begins(sentence)} ...",
                    )
                )
    return found


def _prose(block: Block) -> list[str]:
    """The words of the block that a reader reads as sentences: a paragraph's or an item's, or each
    cell of a row, and none of another block."""
    if block.kind == ROW:
        return cells(block.text)
    return [block.text] if block.kind in (PARAGRAPH, ITEM) else []

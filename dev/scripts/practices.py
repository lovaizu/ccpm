"""What a person or CI runs on rn's best practices, as `python3 dev/scripts/practices.py form`
with the JSON of one best practice or more: it names each fault of a best practice's form, its
template where it's a JSON Schema that schema.py doesn't read whole, and each file in its folder
that neither it nor its template holds. It gives 0, or 1 where it names any fault, and 2 with its
usage where it gets no command it takes. It's ccpm's own tooling, kept out of rn's folder, as no
run of rn checks the form of rn's own best practices. It holds each best practice to its form, rn's
`plugins/rn/domain/schemas/best-practice.schema.json`."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Callable

# rn's folder of the work's knowledge, where its best practices and their form lie. The code that
# reads a file to its form lies beside this script.
RN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "plugins",
    "rn",
    "domain",
)

import files
import schema

USAGE = "usage: python3 dev/scripts/practices.py form <best practice json>..."

# What the about of a question may name beside the parts or sections: the whole deliverable.
WHOLE = "the whole"
# The section of a template before its first heading under the title.
OPENING = "the opening"
# A section of a Markdown template: a heading of the second level, or of the third, such as a view
# that Solution strategy of the architecture's template nests. A heading whose words hold a slot,
# such as `### <problem>`, stands once for each thing the slot names, and is no section.
SECTION = re.compile(r"^(?:##|###(?=[^<\n]*$)) (.+)$", re.MULTILINE)
# A note of a template. In Markdown, it's a GitHub note whose first line opens with the marker,
# and the quote lines under it. In JSON, it's a key named by the marker. A note of the work's own,
# or the marker named in a sentence, opens otherwise, so neither reads as the other.
MARKER = "DELETE_TEMPLATE_COMMENT"
# The key by which a template in JSON is a JSON Schema of the deliverable.
SCHEMA = "$schema"
NOTE = re.compile(r"^> \[!NOTE\]\n> " + MARKER + r":.*(?:\n>.*)*", re.MULTILINE)
QUESTION = re.compile(r"\bN\d+\b")
# An item named in a text, by its condition's ID and its place, such as N6.2.
ITEM = re.compile(r"\b(N\d+)\.(\d+)\b")
# A link or a figure in Markdown, a fenced code block, whose text links nothing, and a link's target
# that names no file: another site, or a place in the same page.
LINK = re.compile(r"(!?)(\[[^\]]*\]\()([^)\s]+)(\))")
# `FENCE`'s flags stand in the pattern, which reads as one string.
FENCE = re.compile(r"(?ms)(^```.*?^```)")
KEPT = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|#)")
# rn's own best practices, where the check seeks a kind that lies beside no best practice's folder.
OWN = os.path.join(RN, "best-practices")
PRACTICE = "best-practice.json"


def factors(data: dict[str, Any]) -> list[dict[str, Any]]:
    """The critical success factors that the best practice's goal holds, in order."""
    return data["goal"]["critical_success_factors"]


def conditions(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Each necessary condition of the best practice, with its practice, in the order of the tree:
    the conditions of each factor in turn."""
    return [c for factor in factors(data) for c in factor["necessary_conditions"]]


def sections(template: str) -> list[str]:
    """The sections of a template a question may be about: the opening, where text stands between
    the title and the first heading under it, then each heading of the second level, and of the
    third that holds no slot, in order."""
    first = SECTION.search(template)
    before = NOTE.sub("", template[: first.start() if first else len(template)])
    said = [line for line in before.splitlines()[1:] if line.strip()]
    return ([OPENING] if said else []) + SECTION.findall(template)


# A section of a template, by the names of the sections it lies in and its own, from the top: one
# name for a heading of Markdown or an entry of a folder, and a key's path for a template in JSON.
Section = tuple[str, ...]


def held_keys(value: Any, at: Section = ()) -> list[Section]:
    """Each key of the JSON value at any depth, by its path, in order, each path once, as each
    object of a list holds the same keys, but the notes, MARKER."""
    found: list[Section] = []
    if isinstance(value, list):
        for item in value:
            found += [p for p in held_keys(item, at) if p not in found]
    elif isinstance(value, dict):
        for key, inner in value.items():
            if key != MARKER:
                found += [p for p in [(*at, key), *held_keys(inner, (*at, key))] if p not in found]
    return found


def fields(node: Any, root: dict[str, Any], at: Section = (), refs: Section = ()) -> list[Section]:
    """Each field of the JSON Schema node at any depth, by its path, in order, each path once,
    through each list's items and each $ref within the root, a definition walked once on each path
    as one may refer back to itself."""
    if not isinstance(node, dict):
        return []
    found: list[Section] = []
    ref = node.get("$ref", "")
    if ref.startswith("#/") and ref not in refs:
        target: Any = root
        for step in ref[2:].split("/"):
            target = target[step]
        found += fields(target, root, at, (*refs, ref))
    found += fields(node.get("items"), root, at, refs)
    for key, inner in node.get("properties", {}).items():
        found += [(*at, key), *fields(inner, root, (*at, key), refs)]
    return [p for n, p in enumerate(found) if p not in found[:n]]


def keys(template: str) -> list[Section]:
    """The sections of a template in JSON a question may be about: each key at any depth that
    holds content, by its path, the fields where it's a JSON Schema, whose descriptions are its
    notes, else its keys, but the notes, MARKER."""
    read = json.loads(template)
    return fields(read, read) if SCHEMA in read else held_keys(read)


def beside(path: str, name: str) -> str:
    """The path of the file of the name beside the best practice at the path."""
    return os.path.join(os.path.dirname(path), name)


def entries(folder: str) -> list[str]:
    """The sections of a template that's a folder, such as the skeleton of a plugin: each folder
    and file at its top, by name in order, but a hidden file, such as one the system keeps."""
    return sorted(
        name
        for name in os.listdir(folder)
        if not name.startswith(".") or os.path.isdir(os.path.join(folder, name))
    )


def template(path: str, data: dict[str, Any]) -> list[Section] | None:
    """The sections of the template the best practice at the path names, read as its format is,
    each by its path, or None where it names none. Refuses, by FileNotFoundError, one that isn't
    there."""
    if "template" not in data:
        return None
    if os.path.isdir(beside(path, data["template"])):
        return [(name,) for name in entries(beside(path, data["template"]))]
    with open(beside(path, data["template"]), encoding="utf-8") as f:
        text = f.read()
    if data["template"].endswith(".json"):
        return keys(text)
    return [(name,) for name in sections(text)]


def unread(path: str, data: dict[str, Any]) -> list[str]:
    """Why the template of the best practice at the path, where it's a JSON Schema, is no schema
    that schema.py reads whole, in words, as a check that holds a deliverable to it would read
    it wrong."""
    if not data.get("template", "").endswith(".json"):
        return []
    try:
        form = files.read(beside(path, data["template"]))
        if SCHEMA in form:
            schema.checked(form)
    except (schema.Unread, files.Unreadable) as why:
        return [f"its template {data['template']} is no schema it reads whole: {why}"]
    return []


def practice_of(path: str, kind: str) -> str:
    """The path of the best practice of the kind beside the folder of the one at the path, else
    among rn's own, else beside, where neither place holds it."""
    near = os.path.normpath(beside(path, os.path.join("..", kind, PRACTICE)))
    own = os.path.join(OWN, kind, PRACTICE)
    return own if not os.path.isfile(near) and os.path.isfile(own) else near


def lacked(path: str, taken: dict[str, Any]) -> list[str]:
    """Each section that the input takes and its kind's template, by the best practice of the kind
    as practice_of finds it from the path, doesn't hold, in words, or why that template can't be
    read."""
    kind = taken["kind"]
    if not taken["takes"]:
        return []
    found = practice_of(path, kind)
    try:
        held = template(found, files.read(found)) or []
    except (files.Unreadable, FileNotFoundError, ValueError) as why:
        return [f"its input {kind} takes sections of a template it can't read: {why}"]
    names = {" / ".join(section) for section in held}
    return [
        f"its input {kind} takes {name}, which is no section of {kind}'s template"
        for name in taken["takes"]
        if name not in names
    ]


def missing(path: str, data: dict[str, Any]) -> list[str]:
    """The template the best practice at the path names, where it isn't beside it, each kind it
    takes that has no best practice beside its folder, and each section it takes that the kind's
    template doesn't hold, in words."""
    found = []
    if "template" in data and not os.path.exists(beside(path, data["template"])):
        found.append(f"its template {data['template']} is not beside it")
    for taken in data["inputs"]:
        kind = taken["kind"]
        if os.path.isfile(practice_of(path, kind)):
            found += lacked(path, taken)
        else:
            found.append(f"its input {kind} has no best practice beside it or among rn's own")
    return found


def shown(text: str, figures_only: bool = True) -> list[str]:
    """Each figure the Markdown shows from under its own folder, or each file it links there where
    figures_only is false, by its path from there, but none in a code block, whose text shows
    nothing."""
    pieces = FENCE.split(text)
    return [
        link.group(3).split("#")[0]
        for n, piece in enumerate(pieces)
        if not n % 2
        for link in LINK.finditer(piece)
        if (link.group(1) or not figures_only)
        and not KEPT.match(link.group(3))
        and not os.path.normpath(link.group(3)).startswith("..")
    ]


def kept(path: str, data: dict[str, Any]) -> set[str]:
    """The files the folder of the best practice at the path holds by right: the best practice and
    each file that a text of it links, and its template, each file in it where it's a folder, else
    the figures it shows."""
    files = {path}
    for text in texts(data):
        files.update(beside(path, linked) for linked in shown(text, figures_only=False))
    if "template" in data:
        named = os.path.normpath(beside(path, data["template"]))
        files.add(named)
        files.update(os.path.join(r, n) for r, _, names in os.walk(named) for n in names)
        if os.path.isfile(named):
            with open(named, encoding="utf-8") as f:
                files.update(beside(named, figure) for figure in shown(f.read()))
    return {os.path.normpath(f) for f in files}


def leftovers(path: str, data: dict[str, Any]) -> list[str]:
    """Each file in the folder of the best practice at the path, at any depth, that it doesn't hold
    by right, in order. A hidden file, such as one the system keeps, is none."""
    held = kept(path, data)
    return sorted(
        os.path.join(root, name)
        for root, _, names in os.walk(os.path.dirname(path))
        for name in names
        if not name.startswith(".") and os.path.normpath(os.path.join(root, name)) not in held
    )


def texts(value: Any) -> list[str]:
    """Each string in the value at any depth."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [t for item in value for t in texts(item)]
    if isinstance(value, dict):
        return [t for v in value.values() for t in texts(v)]
    return []


def faults(data: dict[str, Any], template: list[Section] | list[str] | None = None) -> list[str]:
    """Each fault of the best practice's form that its schema can't name, in words: factors
    numbered in their order from C1, conditions numbered from N1 each once, each about a section of
    its template, where it names one, or the whole, every section asked of, each practice's items
    taken while deciding before those taken while making, and each condition and item named in the
    text one that's there."""
    sections = [s if isinstance(s, tuple) else (s,) for s in template or []]
    return [
        *section_faults(data, sections),
        *number_faults(data),
        *about_faults(data, sections),
        *order_faults(data),
        *condition_faults(data),
        *item_faults(data),
    ]


def section_faults(data: dict[str, Any], sections: list[Section]) -> list[str]:
    """Each section of the template, by its path of names, that it names more than once, or that
    no condition is about, in words."""
    found = []
    for section in sorted({s for s in sections if sections.count(s) > 1}):
        found.append(f"section {'.'.join(section)} is named more than once")
    named = {a.strip() for c in conditions(data) for a in c["about"].split(",")}
    for section in sections:
        # A condition about a section holds each section inside it, and one about a section inside
        # holds the section around it.
        if not any(named & set(s) for s in sections if s[: len(section)] == section):
            found.append(f"section {'.'.join(section)} has no condition about it")
    return found


def number_faults(data: dict[str, Any]) -> list[str]:
    """The fault of the factors' IDs where they aren't numbered in order from C1, and of the
    conditions' where they aren't N1 to the last, each once, in words."""
    found = []
    ids = [f["id"] for f in factors(data)]
    if ids != [f"C{n}" for n in range(1, len(ids) + 1)]:
        found.append(f"factors are {', '.join(ids)}, not numbered in order from C1")
    questions = [c["id"] for c in conditions(data)]
    expected = [f"N{n}" for n in range(1, len(questions) + 1)]
    # A condition keeps its ID wherever the tree holds it, so the IDs need only each be there once.
    if sorted(questions) != sorted(expected):
        found.append(f"conditions are {', '.join(questions)}, not N1 to {expected[-1]}, each once")
    return found


def about_faults(data: dict[str, Any], sections: list[Section]) -> list[str]:
    """Each condition about a name that is neither the whole nor a section of the template, in
    words."""
    names = {s[-1] for s in sections}
    return [
        f"{c['id']} is about {about}, which is no section of the template"
        for c in conditions(data)
        for about in (a.strip() for a in c["about"].split(","))
        if about != WHOLE and about not in names
    ]


def condition_faults(data: dict[str, Any]) -> list[str]:
    """Each condition named in the text, such as N6, that the best practice doesn't hold, in
    words."""
    questions = {c["id"] for c in conditions(data)}
    named = {n for t in texts(data) for n in QUESTION.findall(t)}
    return [
        f"{name} is named, but there is no such condition" for name in sorted(named - questions)
    ]


def order_faults(data: dict[str, Any]) -> list[str]:
    """Each item taken while deciding that comes after one taken while making in its practice, in
    words, as the maker settles the work's decisions before it makes the deliverable."""
    found = []
    for c in conditions(data):
        made = None
        for n, item in enumerate(c["items"], 1):
            if item["at"] == "make" and made is None:
                made = n
            elif item["at"] == "decide" and made is not None:
                found.append(
                    f"{c['id']}.{n} is taken while deciding, after {c['id']}.{made}, which is taken"
                    " while making"
                )
    return found


def item_faults(data: dict[str, Any]) -> list[str]:
    """Each item named in the text, such as N6.2, that its condition's practice doesn't hold, in
    words."""
    counts = {c["id"]: len(c["items"]) for c in conditions(data)}
    named = {m.group(0): m.groups() for t in texts(data) for m in ITEM.finditer(t)}
    return [
        f"{name} is named, but there is no such item"
        for name, (condition, place) in sorted(named.items())
        if not 1 <= int(place) <= counts.get(condition, 0)
    ]


def strays(path: str, data: dict) -> list[str]:
    """Each file in the best practice's folder that neither it nor its template holds, in words."""
    return [
        f"{file} is neither the best practice's nor its template's; remove it"
        for file in leftovers(path, data)
    ]


def form(path: str) -> list[str]:
    """Each fault of the best practice's form, its template where it's a schema that schema.py
    doesn't read whole, and each file in its folder that neither it nor its template holds."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    late = strays(path, data)
    found = missing(path, data)
    if found:
        return found + late
    return unread(path, data) + faults(data, template(path, data)) + late


PRACTICES: dict[str, Callable[[str], list[str]]] = {
    "form": form,
}


def main(argv: list[str]) -> int:
    """Runs the command on each best practice given, as the module says, giving 0, or 1 where it
    names any fault. Otherwise it prints the usage and gives 2."""
    if not argv[1:] or argv[0] not in PRACTICES:
        print(USAGE, file=sys.stderr)
        return 2
    failed = False
    for path in argv[1:]:
        for fault in PRACTICES[argv[0]](path):
            print(f"practices.py: {path}: {fault}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


# Run as the command, and not when the tests import it under the name practices.
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

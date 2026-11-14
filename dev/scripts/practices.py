"""What a person or CI runs on rn's best practices, as `python3 dev/scripts/practices.py
form|markdown` with the JSON of one best practice or more: `form` names each fault of a best
practice's form, its Markdown, made from its JSON for a person to read, left behind it, its
template where it's a JSON Schema that schema.py doesn't read whole, and each file in its folder
that neither it nor its template holds. `markdown` writes its Markdown beside
it. Each gives 0, or 1 where it names any fault, and 2 with its usage where it gets no command it
takes. It's ccpm's own tooling, kept out of rn's folder, as no run of rn checks a best practice's
Markdown. It holds each best practice to its form, `forms/best-practice.schema.json` beside this
script."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Callable

# rn's folder of the work's knowledge, where its best practices lie. Their form, and the code that
# reads a file to its form, lie beside this script.
RN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "plugins",
    "rn",
    "domain",
)

import files
import schema

USAGE = "usage: python3 dev/scripts/practices.py form|markdown <best practice json>..."

# What the about of a question may name beside the parts or sections: the whole deliverable.
WHOLE = "the whole"
# The section of a template before its first heading under the title.
OPENING = "the opening"
SECTION = re.compile(r"^## (.+)$", re.MULTILINE)
# A note of a template. In Markdown, it's a GitHub note whose first line opens with the marker,
# and the quote lines under it. In JSON, it's a key named by the marker. A note of the work's own,
# or the marker named in a sentence, opens otherwise, so neither reads as the other.
MARKER = "DELETE_TEMPLATE_COMMENT"
# The key by which a template in JSON is a JSON Schema of the deliverable.
SCHEMA = "$schema"
NOTE = re.compile(r"^> \[!NOTE\]\n> " + MARKER + r":.*(?:\n>.*)*", re.MULTILINE)
MARK = re.compile(r"^(?:> " + MARKER + r":|\s*\"" + MARKER + r"\"\s*:)", re.MULTILINE)
QUESTION = re.compile(r"\bN\d+\b")
# An item named in a text, by its condition's ID and its place, such as N6.2.
ITEM = re.compile(r"\b(N\d+)\.(\d+)\b")
# An item that holds only in a case opens with Where or If and its case, as the template writes one.
CASE = re.compile(r"^(?:Where|If) ")
# What each action of a trace has its calls do, as the Markdown names them.
DONE = {"run": "run", "read": "read to its end", "write": "made"}
# When the maker takes each item, as the Markdown names it.
AT = {"decide": "*While deciding.*", "make": "*While making.*"}
# A link or a figure in Markdown, a fenced code block, whose text links nothing, and a link's target
# that names no file: another site, or a place in the same page.
LINK = re.compile(r"(!?)(\[[^\]]*\]\()([^)\s]+)(\))")
# `FENCE`'s flags stand in the pattern, as the two flags joined by `|`, `+`, or `^` make the same
# number, mutants no test can tell apart.
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


def by_id(found: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The conditions in the order of their IDs, N9 before N10, as a reader looks a practice up by
    the ID that a role cites."""
    return sorted(found, key=lambda c: (len(c["id"]), c["id"]))


def sections(template: str) -> list[str]:
    """The sections of a template a question may be about: the opening, where text stands between
    the title and the first heading under it, then each heading under the title, in order."""
    first = SECTION.search(template)
    before = NOTE.sub("", template[: first.start() if first else len(template)])
    said = [line for line in before.splitlines()[1:] if line.strip()]
    return ([OPENING] if said else []) + SECTION.findall(template)


def notes_left(text: str) -> list[int]:
    """The number of each line of the text that opens a note of a template, left unwritten."""
    return [text.count("\n", 0, m.start()) + 1 for m in MARK.finditer(text)]


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


def kind_of(path: str) -> str:
    """The kind of the best practice at the path: the name of the folder it lies in."""
    return os.path.basename(os.path.dirname(os.path.abspath(path)))


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


# The lists of the kinds a best practice takes, each with the word for one of them.
TAKEN = {"inputs": "input", "preconditions": "precondition"}


def practice_of(path: str, kind: str) -> str:
    """The path of the best practice of the kind beside the folder of the one at the path, else
    among rn's own, else beside, where neither place holds it."""
    near = os.path.normpath(beside(path, os.path.join("..", kind, PRACTICE)))
    own = os.path.join(OWN, kind, PRACTICE)
    return own if not os.path.isfile(near) and os.path.isfile(own) else near


def missing(path: str, data: dict[str, Any]) -> list[str]:
    """The template the best practice at the path names, where it isn't beside it, and each kind
    it takes that has no best practice beside its folder, in words."""
    found = []
    if "template" in data and not os.path.exists(beside(path, data["template"])):
        found.append(f"its template {data['template']} is not beside it")
    for key, called in TAKEN.items():
        found += [
            f"its {called} {kind} has no best practice beside it or among rn's own"
            for kind in data[key]
            if not os.path.isfile(practice_of(path, kind))
        ]
    return found


def shown(text: str) -> list[str]:
    """Each figure the Markdown shows from under its own folder, by its path from there, but none
    in a code block, whose text shows nothing."""
    pieces = FENCE.split(text)
    return [
        link.group(3).split("#")[0]
        for n, piece in enumerate(pieces)
        if not n % 2
        for link in LINK.finditer(piece)
        if link.group(1)
        and not KEPT.match(link.group(3))
        and not os.path.normpath(link.group(3)).startswith("..")
    ]


def kept(path: str, data: dict[str, Any]) -> set[str]:
    """The files the folder of the best practice at the path holds by right: the best practice and
    its Markdown, and its template, each file in it where it's a folder, else the figures it
    shows."""
    files = {path, os.path.splitext(path)[0] + ".md"}
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
    its template, where it names one, or the whole, every section asked of, each item's trace one
    that every run makes and a call can match, each practice's items taken while deciding before
    those taken while making, and each condition and item named in the text one that's there."""
    sections = [s if isinstance(s, tuple) else (s,) for s in template or []]
    return [
        *section_faults(data, sections),
        *number_faults(data),
        *about_faults(data, sections),
        *trace_faults(data),
        *order_faults(data),
        *condition_faults(data),
        *item_faults(data),
    ]


def section_faults(data: dict[str, Any], sections: list[Section]) -> list[str]:
    """Each section of the template, by its path of names, that it names more than once, or that
    no condition is about, in words."""
    found = []
    # Each section counts once or more in sections, which it comes from.
    for section in sorted({s for s in sections if sections.count(s) > 1}):  # pragma: no mutate
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


def trace_faults(data: dict[str, Any]) -> list[str]:
    """Each fault of an item's trace, in words: a trace on an item that holds only in its case,
    which a run outside the case never makes, so Lane would stop that run's end, and an empty text
    taken, which no call matches."""
    found = []
    for c in conditions(data):
        for n, item in enumerate(c["items"], 1):
            if "trace" not in item:
                continue
            where = f"{c['id']}.{n}"
            if CASE.match(item["text"]):
                found.append(
                    f"{where} holds only in its case, so it carries no trace, as a run outside the"
                    " case never makes it"
                )
            if any(not take.strip() for take in item["trace"]["takes"]):
                found.append(f"{where} takes an empty text in its trace, which no call matches")
    return found


def listed(takes: list[str]) -> str:
    """The texts in code, joined by commas, and by the word or before the last one."""
    *rest, last = [f"`{t}`" for t in takes]
    return f"{', '.join(rest)} or {last}" if rest else last


def item_line(n: int, item: dict[str, Any]) -> str:
    """The item as a line of a numbered list, with when the maker takes it, and the calls its trace
    takes and what they do."""
    line = f"{n}. {AT[item['at']]} {item['text']}"
    if "trace" in item:
        trace = item["trace"]
        line += f" The trace: {listed(trace['takes'])} {DONE[trace['action']]}."
    return line


def tree(data: dict[str, Any]) -> list[str]:
    """The goal tree as a nested list: the goal, each factor under it, and each condition under its
    factor with the sections that hold it, each ID in bold before its sentence, as the prose check
    reads a capital after a colon as a fault."""
    lines = [f"- {data['goal']['what']}"]
    for factor in factors(data):
        lines.append(f"  - **{factor['id']}** {factor['what']}")
        held = factor["necessary_conditions"]
        lines += [f"    - **{c['id']}** {c['what']} ({c['about']})" for c in held]
    return lines


def link_of(path: str, kind: str) -> str:
    """The link from the Markdown of the best practice at the path to that of the kind it takes."""
    found = os.path.splitext(practice_of(path, kind))[0] + ".md"
    return os.path.relpath(found, os.path.dirname(os.path.abspath(path))).replace(os.sep, "/")


def markdown_of(path: str, data: dict[str, Any]) -> str:
    """The best practice at the path as Markdown: its goal tree, a link to its template, and a link
    to each kind it takes where it takes any, to where its best practice lies, then each
    condition's practice, in the order of the IDs, under the question it meets."""
    out = [f"# `{kind_of(path)}`", "", "## Goal tree", "", *tree(data)]
    if "template" in data:
        out += ["", "## Template", "", f"[{data['template']}]({data['template']})"]
    for key in TAKEN:
        if data[key]:
            out += ["", f"## {key.capitalize()}", ""]
            out += [f"- [{taken}]({link_of(path, taken)})" for taken in data[key]]
    out += ["", "## Practices"]
    for c in by_id(conditions(data)):
        out += ["", f"### {c['id']}", "", c["what"], "", c["why"], ""]
        out += [item_line(n, s) for n, s in enumerate(c["items"], 1)]
    return "\n".join(out) + "\n"


def strays(path: str, data: dict) -> list[str]:
    """Each file in the best practice's folder that neither it nor its template holds, in words."""
    return [
        f"{file} is neither the best practice's nor its template's; remove it"
        for file in leftovers(path, data)
    ]


def form(path: str) -> list[str]:
    """Each fault of the best practice's form, its template where it's a schema that schema.py
    doesn't read whole, its Markdown left behind it, and each file in its folder that neither it
    nor its template holds."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    late = strays(path, data)
    found = missing(path, data)
    if found:
        return found + late
    found = unread(path, data) + faults(data, template(path, data))
    target = os.path.splitext(path)[0] + ".md"
    try:
        with open(target, encoding="utf-8") as f:
            if f.read() != markdown_of(path, data):
                found.append(f"{target} is not as its JSON makes it; run practices.py markdown")
    except FileNotFoundError:
        found.append(f"{target} is missing; run practices.py markdown")
    return found + late


def markdown(path: str) -> list[str]:
    """Writes the best practice's Markdown beside it, where a person can read it."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    with open(os.path.splitext(path)[0] + ".md", "w", encoding="utf-8") as f:
        f.write(markdown_of(path, data))
    return []


PRACTICES: dict[str, Callable[[str], list[str]]] = {
    "form": form,
    "markdown": markdown,
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
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))

"""What a person or CI runs on rn's best practices, as `python3 dev/scripts/practices.py
form|markdown|example <best practice json>...`: `form` names each fault of a best practice's form,
its Markdown, made from its JSON for a person to read, left behind it, the copy of its example left
behind the work it copies, and each file in its folder that none of them holds; `markdown` writes
its Markdown beside it; `example` writes the copy of its example from the work its source names,
and removes each file that none of them holds. Each gives 0, or 1 where it names any fault, and 2
with its usage where it is given no command it takes. It is ccpm's own tooling, kept out of rn's
folder, as no run of rn checks a best practice's Markdown or the copy of its example; it holds
each best practice to rn's form of it, `plugins/rn/domain/forms/best-practice.schema.json`."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Callable

# rn's folder of the work's knowledge, where its best practices, their form and the code that reads
# a file to its form lie.
RN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "plugins",
    "rn",
    "domain",
)
sys.path.insert(0, RN)  # pragma: no mutate

import files
import schema

USAGE = "usage: python3 dev/scripts/practices.py form|markdown|example <best practice json>..."

# What the about of a question may name beside the parts or sections: the whole deliverable.
WHOLE = "the whole"
# The section of a template before its first heading under the title.
OPENING = "the opening"
SECTION = re.compile(r"^## (.+)$", re.MULTILINE)
# A note of a template: in Markdown, a GitHub note whose first line opens with the marker, and
# the quote lines under it; in JSON, a key named by the marker. A note of the work's own, or the
# marker named in a sentence, opens otherwise, so they are told apart.
MARKER = "DELETE_TEMPLATE_COMMENT"
# The key by which a template in JSON is a JSON Schema of the deliverable.
SCHEMA = "$schema"
NOTE = re.compile(r"^> \[!NOTE\]\n> " + MARKER + r":.*(?:\n>.*)*", re.MULTILINE)
MARK = re.compile(r"^(?:> " + MARKER + r":|\s*\"" + MARKER + r"\"\s*:)", re.MULTILINE)
QUESTION = re.compile(r"\bQ\d+\b")
# A step that holds only in a case, as the template writes one: its case first, after Where or If.
CASE = re.compile(r"^(?:Where|If) ")
# What each action of a trace has its calls do, as the Markdown names them.
DONE = {"run": "run", "read": "read to its end", "write": "made"}
# A link or a figure in Markdown, a fenced code block, whose text links nothing, and a link's target
# that a copy elsewhere still reaches as it is: another site, or a place in the same page.
LINK = re.compile(r"(!?)(\[[^\]]*\]\()([^)\s]+)(\))")
# FENCE's flags stand in the pattern, as `re.M | re.S` is the same number as `re.M + re.S` or
# `re.M ^ re.S`, mutants no test can tell apart.
FENCE = re.compile(r"(?ms)(^```.*?^```)")
KEPT = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|#)")
# rn's own best practices, where a kind that lies beside no best practice's folder is sought.
OWN = os.path.join(RN, "best-practices")
PRACTICE = "best-practice.json"


def part_ids(items: list[dict[str, Any]]) -> list[str]:
    """The id of each part at any depth, in order."""
    found = []
    for item in items:
        found.append(item["id"])
        found.extend(part_ids(item.get("parts", [])))
    return found


def leaf_ids(items: list[dict[str, Any]]) -> list[str]:
    """The id of each part that holds no parts of its own, in order: a part made of parts is asked
    of through them."""
    found = []
    for item in items:
        found.extend(leaf_ids(item["parts"]) if item.get("parts") else [item["id"]])
    return found


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


def keys(template: str) -> list[str]:
    """The sections of a template in JSON a question may be about: the fields at its top where it
    is a JSON Schema, whose descriptions are its notes, else its keys, in order, but the notes,
    MARKER."""
    read = json.loads(template)
    if SCHEMA in read:
        return list(read["properties"])
    return [key for key in read if key != MARKER]


def beside(path: str, name: str) -> str:
    """The path of the file of the name beside the best practice at the path."""
    return os.path.join(os.path.dirname(path), name)


def kind_of(path: str) -> str:
    """The kind of the best practice at the path: the name of the folder it lies in."""
    return os.path.basename(os.path.dirname(os.path.abspath(path)))


def entries(folder: str) -> list[str]:
    """The sections of a template that is a folder, such as the skeleton of a plugin: each folder
    and file at its top, by name in order, but a hidden file, such as one the system keeps."""
    return sorted(
        name
        for name in os.listdir(folder)
        if not name.startswith(".") or os.path.isdir(os.path.join(folder, name))
    )


def template(path: str, data: dict[str, Any]) -> list[str] | None:
    """The sections of the template the best practice at the path names, read as its format is,
    or None where it names none; refuses, by FileNotFoundError, one that is not there."""
    if "template" not in data:
        return None
    if os.path.isdir(beside(path, data["template"])):
        return entries(beside(path, data["template"]))
    with open(beside(path, data["template"]), encoding="utf-8") as f:
        text = f.read()
    return keys(text) if data["template"].endswith(".json") else sections(text)


# The lists of the kinds a best practice takes, each with what one of them is called in words.
TAKEN = {"inputs": "input", "preconditions": "precondition"}


def practice_of(path: str, kind: str) -> str:
    """The path of the best practice of the kind beside the folder of the one at the path, else
    among rn's own, else beside, where it is sought and not found."""
    near = os.path.normpath(beside(path, os.path.join("..", kind, PRACTICE)))
    own = os.path.join(OWN, kind, PRACTICE)
    return own if not os.path.isfile(near) and os.path.isfile(own) else near


def missing(path: str, data: dict[str, Any]) -> list[str]:
    """Each file the best practice at the path names, its template and its example, that is not
    beside it, and each kind it takes that has no best practice beside its folder, in words."""
    found = [
        f"its {key} {data[key]} is not beside it"
        for key in ("template", "example")
        if key in data and not os.path.exists(beside(path, data[key]))
    ]
    for key, called in TAKEN.items():
        found += [
            f"its {called} {kind} has no best practice beside it or among rn's own"
            for kind in data[key]
            if not os.path.isfile(practice_of(path, kind))
        ]
    return found


def unheld(path: str, data: dict[str, Any]) -> list[str]:
    """The point the example of the best practice at the path is out of its template by, in words,
    where both are JSON and the template is a JSON Schema; or why it cannot be held to it."""
    if not all(data.get(key, "").endswith(".json") for key in ("template", "example")):
        return []
    try:
        form = files.read(beside(path, data["template"]))
        if SCHEMA not in form:
            return []
        schema.checked(form)
        value = files.read(beside(path, data["example"]))
    except schema.Unread as why:
        return [f"its template {data['template']} is no schema it reads whole: {why}"]
    except files.Unreadable as why:
        return [str(why)]
    out = schema.held(form, value)
    return [f"its example {data['example']} is out of its template: {out.told()}"] if out else []


def copies(path: str, data: dict[str, Any]) -> dict[str, bytes]:
    """The files of the example of the best practice at the path, where it names the work it is a
    copy of in `source`, each path with what it holds: the work, each relative link in it set to
    reach from the example what it reached from the work, and each figure it shows from under the
    work's folder, at the same relative path beside the example; none where it names no source.
    Refuses, by FileNotFoundError, a work or a figure that is not there."""
    if "source" not in data:
        return {}
    source = os.path.normpath(beside(path, data["source"]))
    example = os.path.normpath(beside(path, data["example"]))
    made: dict[str, bytes] = {}

    def moved(link: re.Match[str]) -> str:
        figure, opening, target, closing = link.groups()
        if KEPT.match(target):
            return link.group(0)
        place = target.split("#")[0]
        at = os.path.normpath(os.path.join(os.path.dirname(source), place))
        if figure and not os.path.normpath(place).startswith(".."):
            with open(at, "rb") as f:
                made[os.path.normpath(os.path.join(os.path.dirname(example), place))] = f.read()
            return link.group(0)
        reach = os.path.relpath(at, os.path.dirname(example)).replace(os.sep, "/")
        return figure + opening + reach + target[len(place) :] + closing

    with open(source, encoding="utf-8") as f:
        pieces = FENCE.split(f.read())
    # The pieces between the code blocks, at the even places, are those that link.
    text = "".join(p if n % 2 else LINK.sub(moved, p) for n, p in enumerate(pieces))
    made[example] = text.encode("utf-8")
    return made


def shown(text: str) -> list[str]:
    """Each figure the Markdown shows from under its own folder, by its path from there; none in a
    code block, whose text shows nothing."""
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
    its Markdown, its template and the figures it shows, and its example, as the copy of its source
    would now be where it names one, else with the figures it shows. Refuses, by FileNotFoundError,
    a source or a figure of it that is not there."""
    files = {path, os.path.splitext(path)[0] + ".md"}
    copied = copies(path, data) if "example" in data else {}
    files.update(copied)
    for key in ("template", "example"):
        if key not in data:
            continue
        named = os.path.normpath(beside(path, data[key]))
        files.add(named)
        files.update(os.path.join(r, n) for r, _, names in os.walk(named) for n in names)
        if named not in copied and os.path.isfile(named):
            with open(named, encoding="utf-8") as f:
                files.update(beside(named, figure) for figure in shown(f.read()))
    return {os.path.normpath(f) for f in files}


def leftovers(path: str, data: dict[str, Any]) -> list[str]:
    """Each file in the folder of the best practice at the path, at any depth, that it does not hold
    by right, in order; a hidden file, such as one the system keeps, is none."""
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


def faults(data: dict[str, Any], template: list[str] | None = None) -> list[str]:
    """Each fault of the best practice's form, in words: questions numbered in their order, each
    about a part it has, a section of its template where it has one, or the whole, every part or
    section and the whole asked of, each question with one practice in the same order, each step's
    trace one that every run makes and a call can match, and each question named in the text one
    that is there."""
    found = []
    if template is None:
        ids, leaves, what = part_ids(data.get("parts", [])), leaf_ids(data.get("parts", [])), "part"
    else:
        ids, leaves, what = template, template, "section"
        if "parts" in data:
            found.append("parts are kept, though the template holds the form")
    # Each id counts once or more in ids, which it is taken from.
    for part in sorted({i for i in ids if ids.count(i) > 1}):  # pragma: no mutate
        found.append(f"{what} {part} is named more than once")
    named_parts = {a.strip() for q in data["intents"] for a in q["about"].split(",")}
    for part in leaves:
        if part not in named_parts:
            found.append(f"{what} {part} has no question about it")
    if WHOLE not in named_parts:
        found.append(f"no question is about {WHOLE}")
    questions = [q["id"] for q in data["intents"]]
    expected = [f"Q{n}" for n in range(1, len(questions) + 1)]
    if questions != expected:
        found.append(f"questions are {', '.join(questions)}, not numbered in order from Q1")
    for q in data["intents"]:
        for about in (a.strip() for a in q["about"].split(",")):
            if about != WHOLE and about not in ids:
                where = "part" if template is None else "section of the template"
                found.append(f"{q['id']} is about {about}, which is no {where}")
    answered = [p["intent"] for p in data["practices"]]
    if answered != questions:
        found.append(f"practices meet {', '.join(answered)}, not each question once in its order")
    found += trace_faults(data)
    for named in sorted({n for t in texts(data) for n in QUESTION.findall(t)} - set(questions)):
        found.append(f"{named} is named, but there is no such question")
    return found


def trace_faults(data: dict[str, Any]) -> list[str]:
    """Each fault of a step's trace, in words: a trace on a step that holds only in its case, which
    a run outside the case never makes, so Lane would stop that run's end, and an empty text taken,
    which no call matches."""
    found = []
    for practice in data["practices"]:
        for n, step in enumerate(practice["steps"], 1):
            if "trace" not in step:
                continue
            where = f"step {n} of {practice['intent']}"
            if CASE.match(step["text"]):
                found.append(
                    f"{where} holds only in its case, so it carries no trace, as a run outside the"
                    " case never makes it"
                )
            if any(not take.strip() for take in step["trace"]["takes"]):
                found.append(f"{where} takes an empty text in its trace, which no call matches")
    return found


def listed(takes: list[str]) -> str:
    """The texts in code, joined by commas, with or before the last."""
    *rest, last = [f"`{t}`" for t in takes]
    return f"{', '.join(rest)} or {last}" if rest else last


def step_line(n: int, step: dict[str, Any]) -> str:
    """The step as a line of a numbered list, with the calls its trace takes and what they do."""
    line = f"{n}. {step['text']}"
    if "trace" in step:
        trace = step["trace"]
        line += f" The trace: {listed(trace['takes'])} {DONE[trace['action']]}."
    return line


def parts(items: list[dict[str, Any]], depth: int = 0) -> list[str]:
    """Each part, its id in bold and what it holds, its own parts under it."""
    lines = []
    for item in items:
        lines.append(f"{'  ' * depth}- **{item['id']}**: {item['what']}")
        lines.extend(parts(item.get("parts", []), depth + 1))
    return lines


def link_of(path: str, kind: str) -> str:
    """The link from the Markdown of the best practice at the path to that of the kind it takes."""
    found = os.path.splitext(practice_of(path, kind))[0] + ".md"
    return os.path.relpath(found, os.path.dirname(os.path.abspath(path))).replace(os.sep, "/")


def markdown_of(path: str, data: dict[str, Any]) -> str:
    """The best practice at the path as Markdown: its goal, a link to its template and its example,
    with the work the example is a copy of, a link to each kind it takes where it takes any, to
    where its best practice lies, or else its parts, and its intents, then the practice for each
    intent, under the question it meets."""
    kind = kind_of(path)
    questions = {q["id"]: q for q in data["intents"]}
    out = [f"# `{kind}`", "", "## Goal", "", data["goal"]]
    for key in ("template", "example"):
        if key in data:
            out += ["", f"## {key.capitalize()}", "", f"[{data[key]}]({data[key]})"]
    if "example" in data and "source" in data:
        # The example comes last, so its link is the last line.
        out[-1] += f", a copy of [{data['source']}]({data['source']})"
    for key in TAKEN:
        if data[key]:
            out += ["", f"## {key.capitalize()}", ""]
            out += [f"- [{taken}]({link_of(path, taken)})" for taken in data[key]]
    if data.get("parts"):
        out += ["", "## Parts", "", *parts(data["parts"])]
    # A table and headings of their own, as the prose check reads a capital after a colon as a
    # fault.
    out += ["", "## Intents", "", "| ID | About | Question |", "| --- | --- | --- |"]
    out += [f"| {q['id']} | {q['about']} | {q['what']} |" for q in data["intents"]]
    out += ["", "## Practices"]
    for practice in data["practices"]:
        question = questions[practice["intent"]]
        out += ["", f"### {question['id']}", "", question["what"], ""]
        out += ["**Thinking**", "", practice["thinking"]]
        if practice["steps"]:
            out += ["", "**Steps**", ""]
            out += [step_line(n, s) for n, s in enumerate(practice["steps"], 1)]
    return "\n".join(out) + "\n"


def copied(path: str, data: dict) -> tuple[dict[str, bytes], list[str]]:
    """The files of the best practice's example copied from its source, or else why they cannot be
    made."""
    if "example" not in data:
        return {}, [f"its source {data['source']} has no example to be copied to"]
    try:
        return copies(path, data), []
    except FileNotFoundError as why:
        return {}, [f"{why.filename}, which its example copies, is not there"]


def behind(path: str, data: dict) -> list[str]:
    """Each file of the best practice's example that is not as its source makes it, or why it
    cannot be made; none where it names no source."""
    if "source" not in data:
        return []
    made, found = copied(path, data)
    for copy, content in made.items():
        try:
            with open(copy, "rb") as f:
                same = f.read() == content
        except FileNotFoundError:
            same = False
        if not same:
            found.append(f"{copy} is not a copy of its source; run practices.py example")
    return found


def strays(path: str, data: dict) -> list[str]:
    """Each file in the best practice's folder that neither it, its template nor its example holds,
    in words; none where its source cannot be copied, which behind names."""
    try:
        found = leftovers(path, data)
    except FileNotFoundError:
        return []
    fix = "run practices.py example" if "source" in data else "remove it"
    return [f"{file} is neither the template's nor the example's; {fix}" for file in found]


def form(path: str) -> list[str]:
    """Each fault of the best practice's form, its Markdown and the copy of its example left
    behind it, and each file in its folder that none of them holds."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    late = behind(path, data) + strays(path, data)
    found = missing(path, data)
    if found:
        return found + late
    found = faults(data, template(path, data)) + unheld(path, data)
    target = os.path.splitext(path)[0] + ".md"
    try:
        with open(target, encoding="utf-8") as f:
            if f.read() != markdown_of(path, data):
                found.append(f"{target} is not as its JSON makes it; run practices.py markdown")
    except FileNotFoundError:
        found.append(f"{target} is missing; run practices.py markdown")
    return found + late


def markdown(path: str) -> list[str]:
    """Writes the best practice's Markdown beside it, where it can be read."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    with open(os.path.splitext(path)[0] + ".md", "w", encoding="utf-8") as f:
        f.write(markdown_of(path, data))
    return []


def example(path: str) -> list[str]:
    """Writes the best practice's example, and each figure it shows, as a copy of its source, and
    removes each file in its folder that neither it, its template nor its example holds."""
    try:
        data = files.load(path, "best-practice")
    except files.Unreadable as why:
        return [str(why)]
    if "source" not in data:
        return ["it names no source to copy its example from"]
    made, found = copied(path, data)
    for copy, content in made.items():
        os.makedirs(os.path.dirname(copy), exist_ok=True)
        with open(copy, "wb") as f:
            f.write(content)
    # Only once the copy is made, as which files it holds is known only then.
    for file in leftovers(path, data) if made else []:
        os.remove(file)
    return found


PRACTICES: dict[str, Callable[[str], list[str]]] = {
    "form": form,
    "markdown": markdown,
    "example": example,
}


def main(argv: list[str]) -> int:
    """Runs the command on each best practice given, as the module says, giving 0, or 1 where it
    names any fault; or prints the usage and gives 2."""
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

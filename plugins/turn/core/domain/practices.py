"""A kind's best practice, a JSON that Turn's roles read: the faults its form shows, checked before
anything reads it; the Markdown a person reads of it, written beside it, the JSON staying the one
source so the two cannot say different things; the Standard the evaluator is given, the best
practice without its ways of meeting the questions; and the groups of its questions, each answered
by a run of the evaluator of its own."""

from __future__ import annotations

import json
import os
import re
from typing import Any

# What the about of a question may name beside the parts or sections: the whole deliverable.
WHOLE = "the whole"
# The section of a template before its first heading under the title.
OPENING = "the opening"
SECTION = re.compile(r"^## (.+)$", re.MULTILINE)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
QUESTION = re.compile(r"\bQ\d+\b")


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
    before = COMMENT.sub("", template[: first.start() if first else len(template)])
    said = [line for line in before.splitlines()[1:] if line.strip()]
    return ([OPENING] if said else []) + SECTION.findall(template)


def keys(template: str) -> list[str]:
    """The sections of a template in JSON a question may be about: its keys, in order, but the
    comments, `$comment`."""
    return [key for key in json.loads(template) if key != "$comment"]


def beside(path: str, name: str) -> str:
    """The path of the file of the name beside the best practice at the path."""
    return os.path.join(os.path.dirname(path), name)


def template(path: str, data: dict[str, Any]) -> list[str] | None:
    """The sections of the template the best practice at the path names, read as its format is,
    or None where it names none; refuses, by FileNotFoundError, one that is not there."""
    if "template" not in data:
        return None
    with open(beside(path, data["template"]), encoding="utf-8") as f:
        text = f.read()
    return keys(text) if data["template"].endswith(".json") else sections(text)


def missing(path: str, data: dict[str, Any]) -> list[str]:
    """Each file the best practice at the path names, its template and its example, that is not
    beside it, in words."""
    return [
        f"its {key} {data[key]} is not beside it"
        for key in ("template", "example")
        if key in data and not os.path.isfile(beside(path, data[key]))
    ]


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
    section and the whole asked of, each question with one practice in the same order, and each
    question named in the text one that is there."""
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
    named_parts = {a.strip() for q in data["user_benefits"] for a in q["about"].split(",")}
    for part in leaves:
        if part not in named_parts:
            found.append(f"{what} {part} has no question about it")
    if WHOLE not in named_parts:
        found.append(f"no question is about {WHOLE}")
    questions = [q["id"] for q in data["user_benefits"]]
    expected = [f"Q{n}" for n in range(1, len(questions) + 1)]
    if questions != expected:
        found.append(f"questions are {', '.join(questions)}, not numbered in order from Q1")
    for q in data["user_benefits"]:
        for about in (a.strip() for a in q["about"].split(",")):
            if about != WHOLE and about not in ids:
                where = "part" if template is None else "section of the template"
                found.append(f"{q['id']} is about {about}, which is no {where}")
    answered = [p["user_benefit"] for p in data["practices"]]
    if answered != questions:
        found.append(f"practices meet {', '.join(answered)}, not each question once in its order")
    for named in sorted({n for t in texts(data) for n in QUESTION.findall(t)} - set(questions)):
        found.append(f"{named} is named, but there is no such question")
    return found


def parts(items: list[dict[str, Any]], depth: int = 0) -> list[str]:
    """Each part, its id in bold and what it holds, its own parts under it."""
    lines = []
    for item in items:
        lines.append(f"{'  ' * depth}- **{item['id']}**: {item['what']}")
        lines.extend(parts(item.get("parts", []), depth + 1))
    return lines


def markdown(kind: str, data: dict[str, Any]) -> str:
    """The best practice of the kind as Markdown: its goal, a link to its template and its example
    or else its parts, and its user benefits, then the practice for each user benefit, under the
    question it meets."""
    questions = {q["id"]: q for q in data["user_benefits"]}
    out = [f"# {kind}", "", "## Goal", "", data["goal"]]
    for key in ("template", "example"):
        if key in data:
            out += ["", f"## {key.capitalize()}", "", f"[{data[key]}]({data[key]})"]
    if data.get("parts"):
        out += ["", "## Parts", "", *parts(data["parts"])]
    out += ["", "## User benefits", ""]
    out += [f"- **{q['id']}** ({q['about']}): {q['what']}" for q in data["user_benefits"]]
    out += ["", "## Practices"]
    for practice in data["practices"]:
        question = questions[practice["user_benefit"]]
        out += ["", f"### {question['id']}: {question['what']}", ""]
        out.append(f"**Thinking**: {practice['thinking']}")
        if practice["steps"]:
            out += ["", "**Steps**", "", *(f"{n}. {s}" for n, s in enumerate(practice["steps"], 1))]
    return "\n".join(out) + "\n"


def standard(data: dict[str, Any]) -> dict[str, Any]:
    """The best practice's goal, parts and questions, without its practices: the Standard, what the
    evaluator is given, as the work's user never sees how the work was made."""
    kept = {"goal": data["goal"]}
    if "parts" in data:
        kept["parts"] = data["parts"]
    kept["user_benefits"] = data["user_benefits"]
    return kept


def groups(data: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    """The best practice's questions in groups, each named with the kind, as `<kind>/Q1`: the
    questions about the whole in one group, and the others joined where they ask of a part in
    common; the groups in the order of their first question, numbered G1 on."""
    found: list[tuple[set[str], list[str]]] = []
    for q in data["user_benefits"]:
        abouts = {a.strip() for a in q["about"].split(",")}
        if WHOLE in abouts:
            abouts = {WHOLE}
        joined = [g for g in found if g[0] & abouts]
        if not joined:
            found.append((abouts, [q["id"]]))
            continue
        first = joined[0]
        for g in joined[1:]:
            first[0].update(g[0])
            first[1].extend(g[1])
            found.remove(g)
        first[0].update(abouts)
        first[1].append(q["id"])
    return [
        {"id": f"G{n}", "questions": [f"{kind}/{i}" for i in sorted(g[1], key=number)]}
        for n, g in enumerate(found, 1)
    ]


def number(question: str) -> int:
    """The number of a question of the form `Q<n>`, which faults holds every question to."""
    return int(question[1:])

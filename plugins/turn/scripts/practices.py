"""Turn's best practices, each a JSON that Turn's roles read: the faults its form shows, checked
before anything reads it, and the Markdown a person reads of it, written beside it. The JSON stays
the one source; the Markdown is made from it, never edited by hand, so the two cannot say
different things."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

# What the about of a question may name beside the parts: the whole deliverable.
WHOLE = "the whole"
GROUND = ("title", "url", "by", "quote")
QUESTION = re.compile(r"\bQ\d+\b")


def part_ids(items: list[dict[str, Any]]) -> list[str]:
    """The id of each part at any depth, in order."""
    found = []
    for item in items:
        found.append(item["id"])
        found.extend(part_ids(item.get("parts", [])))
    return found


def texts(value: Any) -> list[str]:
    """Each string in the value at any depth, but a ground's, whose words are its source's."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [t for item in value for t in texts(item)]
    if isinstance(value, dict):
        return [t for k, v in value.items() if k != "grounds" for t in texts(v)]
    return []


def faults(data: dict[str, Any]) -> list[str]:
    """Each fault of the best practice's form, in words: questions numbered in their order, each
    about a part it has or the whole, each with one method in the same order, each ground whole,
    and each question named in the text one that is there."""
    found = []
    standard, methods = data["standard"], data["practice"]["methods"]
    ids = part_ids(standard.get("parts", []))
    for part in sorted({i for i in ids if ids.count(i) > 1}):
        found.append(f"part {part} is named more than once")
    questions = [q["id"] for q in standard["checklist"]]
    expected = [f"Q{n}" for n in range(1, len(questions) + 1)]
    if questions != expected:
        found.append(f"questions are {', '.join(questions)}, not numbered in order from Q1")
    for q in standard["checklist"]:
        for about in (a.strip() for a in q["about"].split(",")):
            if about != WHOLE and about not in ids:
                found.append(f"{q['id']} is about {about}, which is no part")
    answered = [m["question"] for m in methods]
    if answered != questions:
        found.append(f"methods meet {', '.join(answered)}, not each question once in its order")
    for method in methods:
        for n, item in enumerate(method["grounds"], 1):
            missing = [k for k in GROUND if not item.get(k)]
            if missing:
                found.append(f"{method['question']} ground {n} has no {', '.join(missing)}")
            elif not item["url"].startswith("https://"):
                found.append(f"{method['question']} ground {n} links no https page")
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


def ground(item: dict[str, str]) -> str:
    """A ground as a link labelled with its page's title, then who wrote it and the words quoted."""
    return f"- [{item['title']}]({item['url']}), {item['by']}: \"{item['quote']}\""


def markdown(kind: str, data: dict[str, Any]) -> str:
    """The best practice of the kind as Markdown: the Standard's goal, parts and checklist, then
    the Practice's method for each question, under the question it meets."""
    standard, methods = data["standard"], data["practice"]["methods"]
    questions = {q["id"]: q for q in standard["checklist"]}
    out = [f"# {kind}", "", "## Standard", "", "### Goal", "", standard["goal"]]
    if standard.get("parts"):
        out += ["", "### Parts", "", *parts(standard["parts"])]
    out += ["", "### Checklist", ""]
    out += [f"- **{q['id']}** ({q['about']}): {q['what']}" for q in standard["checklist"]]
    out += ["", "## Practice"]
    for method in methods:
        question = questions[method["question"]]
        out += ["", f"### {question['id']}: {question['what']}", ""]
        out.append(f"**Thinking**: {method['thinking']}")
        if method["steps"]:
            out += ["", "**Steps**", "", *(f"{n}. {s}" for n, s in enumerate(method["steps"], 1))]
        if method["grounds"]:
            out += ["", "**Grounds**", "", *(ground(g) for g in method["grounds"])]
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    """`write <json>...` writes each Markdown beside its JSON; `check <json>...` names each fault
    of a JSON's form and each Markdown not as its JSON makes it, and fails if any."""
    if len(argv) < 2 or argv[0] not in ("write", "check"):
        print("usage: practices.py write|check <best practice json>...", file=sys.stderr)
        return 2
    failed = False
    for path in argv[1:]:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        target = os.path.splitext(path)[0] + ".md"
        text = markdown(os.path.splitext(os.path.basename(path))[0], data)
        if argv[0] == "write":
            with open(target, "w", encoding="utf-8") as f:
                f.write(text)
            continue
        found = faults(data)
        try:
            with open(target, encoding="utf-8") as f:
                if f.read() != text:
                    found.append(f"{target} is not as its JSON makes it; run write")
        except FileNotFoundError:
            found.append(f"{target} is missing; run write")
        for fault in found:
            print(f"practices.py: {path}: {fault}", file=sys.stderr)
        failed = failed or bool(found)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

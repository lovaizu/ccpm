"""The Markdown a person reads of a best practice, written beside its JSON: the JSON is what Turn's
roles read, and stays the one source; the Markdown is made from it, never edited by hand, so the two
cannot say different things."""

from __future__ import annotations

import json
import os
import sys
from typing import Any


def parts(items: list[dict[str, Any]], depth: int = 0) -> list[str]:
    """Each part of a format, its id in bold and what it holds, its own parts under it."""
    lines = []
    for item in items:
        lines.append(f"{'  ' * depth}- **{item['id']}**: {item['what']}")
        lines.extend(parts(item.get("parts", []), depth + 1))
    return lines


def markdown(kind: str, data: dict[str, Any]) -> str:
    """The best practice of the kind as Markdown: the Standard's goal, format and checklist, then
    the Practice's method for each question, under the question it meets."""
    standard, methods = data["standard"], data["practice"]["methods"]
    questions = {q["id"]: q for q in standard["checklist"]}
    out = [f"# {kind}", "", "## Standard", "", "### Goal", "", standard["goal"]]
    if "format" in standard:
        out += ["", "### Format", "", *parts(standard["format"]["parts"])]
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
            out += ["", "**Grounds**", "", *(f"- {g}" for g in method["grounds"])]
    return "\n".join(out) + "\n"


def written(path: str) -> tuple[str, str]:
    """The Markdown's path beside the JSON at the path, and the Markdown made from it."""
    kind = os.path.splitext(os.path.basename(path))[0]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return os.path.splitext(path)[0] + ".md", markdown(kind, data)


def main(argv: list[str]) -> int:
    """`write <json>...` writes each Markdown; `check <json>...` names each one not as its JSON
    makes it, and fails if any."""
    if len(argv) < 2 or argv[0] not in ("write", "check"):
        print("usage: markdown.py write|check <best practice json>...", file=sys.stderr)
        return 2
    stale = []
    for path in argv[1:]:
        target, text = written(path)
        if argv[0] == "write":
            with open(target, "w", encoding="utf-8") as f:
                f.write(text)
            continue
        try:
            with open(target, encoding="utf-8") as f:
                kept = f.read()
        except FileNotFoundError:
            kept = None
        if kept != text:
            stale.append(target)
    for target in stale:
        print(f"markdown.py: {target} is not as its JSON makes it; run write", file=sys.stderr)
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

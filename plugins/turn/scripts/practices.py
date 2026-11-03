"""Turn's best practices, each a JSON that Turn's roles read: the faults its form shows, checked
before anything reads it, and the Markdown a person reads of it, written beside it. The JSON stays
the one source; the Markdown is made from it, never edited by hand, so the two cannot say
different things."""

from __future__ import annotations

import functools
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

# What the about of a question may name beside the parts: the whole deliverable.
WHOLE = "the whole"
GROUND = ("title", "url", "by", "quote")
# The marks a page may write for one another: curly and plain quotes, and every dash.
SAME = (("\u2018\u2019\u2032", "'"), ("\u201c\u201d\u2033", '"'), ("\u2013\u2014\u2212", "-"))
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
    about a part it has or the whole, every part and the whole asked of, each question with one
    practice in the same order, each ground whole, and each question named in the text one that is
    there."""
    found = []
    ids = part_ids(data.get("parts", []))
    for part in sorted({i for i in ids if ids.count(i) > 1}):
        found.append(f"part {part} is named more than once")
    named_parts = {a.strip() for q in data["benefits"] for a in q["about"].split(",")}
    for part in leaf_ids(data.get("parts", [])):
        if part not in named_parts:
            found.append(f"part {part} has no question about it")
    if WHOLE not in named_parts:
        found.append(f"no question is about {WHOLE}")
    questions = [q["id"] for q in data["benefits"]]
    expected = [f"Q{n}" for n in range(1, len(questions) + 1)]
    if questions != expected:
        found.append(f"questions are {', '.join(questions)}, not numbered in order from Q1")
    for q in data["benefits"]:
        for about in (a.strip() for a in q["about"].split(",")):
            if about != WHOLE and about not in ids:
                found.append(f"{q['id']} is about {about}, which is no part")
    answered = [p["benefit"] for p in data["practices"]]
    if answered != questions:
        found.append(f"practices meet {', '.join(answered)}, not each question once in its order")
    for practice in data["practices"]:
        for n, item in enumerate(practice["grounds"], 1):
            missing = [k for k in GROUND if not item.get(k)]
            if missing:
                found.append(f"{practice['benefit']} ground {n} has no {', '.join(missing)}")
            elif not item["url"].startswith("https://"):
                found.append(f"{practice['benefit']} ground {n} links no https page")
    for named in sorted({n for t in texts(data) for n in QUESTION.findall(t)} - set(questions)):
        found.append(f"{named} is named, but there is no such question")
    return found


def plain(text: str) -> str:
    """Text as it reads, for finding words in a page: tags and entities gone, quotes, dashes and
    spaces of every kind made one, and case set aside."""
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    for kinds, one in SAME:
        text = re.sub(f"[{kinds}]", one, text)
    return re.sub(r"\s+", " ", text).strip().lower()


# How often a page that asks to be called again later is asked again, and how long is waited first.
TRIES = 4
WAIT = 15


@functools.cache
def fetch(url: str) -> tuple[str, bytes]:
    """The page at the URL, its content type and its body, as a browser would be given it, each
    page opened once however many grounds quote it; a page that answers too many requests is
    asked again after a wait."""
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(TRIES):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.headers.get("Content-Type", ""), response.read()
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == TRIES - 1:
                raise
            time.sleep(WAIT * (attempt + 1))
    raise AssertionError("unreachable")


def sources(data: dict[str, Any], get: Callable[[str], tuple[str, bytes]] = fetch) -> list[str]:
    """Each ground whose page is not the one meant, in words: a page that does not open, or whose
    text does not hold the title and the words quoted; a page that is no HTML or text, such as a
    PDF, is named as not checked."""
    found = []
    for practice in data["practices"]:
        for n, item in enumerate(practice["grounds"], 1):
            where = f"{practice['benefit']} ground {n} ({item['url']})"
            try:
                kind, body = get(item["url"])
            except Exception as error:  # every way a page fails to open is the same fault here
                found.append(f"{where} does not open: {error}")
                continue
            if not kind.startswith(("text/", "application/xhtml")):
                found.append(f"{where} not checked: the page is {kind or 'of no type'}")
                continue
            page = plain(body.decode("utf-8", "replace"))
            for field in ("title", "quote"):
                if plain(item[field]) not in page:
                    found.append(f"{where} does not hold its {field}")
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
    """The best practice of the kind as Markdown: its goal, parts and benefits, then the practice
    for each benefit, under the question it meets."""
    questions = {q["id"]: q for q in data["benefits"]}
    out = [f"# {kind}", "", "## Goal", "", data["goal"]]
    if data.get("parts"):
        out += ["", "## Parts", "", *parts(data["parts"])]
    out += ["", "## Benefits", ""]
    out += [f"- **{q['id']}** ({q['about']}): {q['what']}" for q in data["benefits"]]
    out += ["", "## Practices"]
    for practice in data["practices"]:
        question = questions[practice["benefit"]]
        out += ["", f"### {question['id']}: {question['what']}", ""]
        out.append(f"**Thinking**: {practice['thinking']}")
        if practice["steps"]:
            out += ["", "**Steps**", "", *(f"{n}. {s}" for n, s in enumerate(practice["steps"], 1))]
        if practice["grounds"]:
            out += ["", "**Grounds**", "", *(ground(g) for g in practice["grounds"])]
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    """`write <json>...` writes each Markdown beside its JSON; `check <json>...` names each fault
    of a JSON's form and each Markdown not as its JSON makes it; `sources <json>...` opens each
    ground's page and names each that is not the one meant. Each fails if it names any."""
    if len(argv) < 2 or argv[0] not in ("write", "check", "sources"):
        print("usage: practices.py write|check|sources <best practice json>...", file=sys.stderr)
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
        if argv[0] == "sources":
            for fault in sources(data):
                print(f"practices.py: {path}: {fault}", file=sys.stderr)
                failed = True
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

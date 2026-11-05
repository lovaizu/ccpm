"""A kind's best practice, a JSON that Turn's roles read: the faults its form shows, checked before
anything reads it; the Markdown a person reads of it, written beside it, the JSON staying the one
source so the two cannot say different things; the Standard the evaluator is given, the best
practice without its ways of meeting the questions; and the groups of its questions, each answered
by a run of the evaluator of its own."""

from __future__ import annotations

import functools
import html
import http.client
import re
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

# What the about of a question may name beside the parts or sections: the whole deliverable.
WHOLE = "the whole"
# The section of a template before its first heading under the title.
OPENING = "the opening"
SECTION = re.compile(r"^## (.+)$", re.MULTILINE)
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
GROUND = ("title", "url", "by", "quote")
# The marks a page may write for one another: curly and plain quotes, and every dash.
SAME = (("\u2018\u2019\u2032", "'"), ("\u201c\u201d\u2033", '"'), ("\u2013\u2014\u2212", "-"))
QUESTION = re.compile(r"\bQ\d+\b")
# What a page holds that a browser does not show as text.
# The two flags are bits apart, so joined by `|`, `+` or `^` they are one value.
UNSHOWN_FLAGS = re.DOTALL | re.IGNORECASE  # pragma: no mutate
UNSHOWN = re.compile(r"<(style|script)\b.*?</\1\s*>", UNSHOWN_FLAGS)
# The tags a browser shows inside a line, joining the text on either side: the rest start a block,
# which a browser sets apart from the text beside it.
INLINE = re.compile(
    r"</?(?:a|abbr|b|cite|code|dfn|em|i|kbd|mark|q|s|samp|small|span|strong|sub|sup|u|var)\b[^>]*>",
    re.IGNORECASE,
)


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


def template(path: str) -> list[str] | None:
    """The sections of the template beside the best practice at the path, `<kind>-template.md`, or
    None where the kind has none."""
    try:
        with open(path.removesuffix(".json") + "-template.md", encoding="utf-8") as f:
            return sections(f.read())
    except FileNotFoundError:
        return None


def texts(value: Any) -> list[str]:
    """Each string in the value at any depth, but a ground's, whose words are its source's."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [t for item in value for t in texts(item)]
    if isinstance(value, dict):
        return [t for k, v in value.items() if k != "grounds" for t in texts(v)]
    return []


def faults(data: dict[str, Any], template: list[str] | None = None) -> list[str]:
    """Each fault of the best practice's form, in words: questions numbered in their order, each
    about a part it has, a section of its template where it has one, or the whole, every part or
    section and the whole asked of, each question with one practice in the same order, each ground
    whole, and each question named in the text one that is there."""
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
    named_parts = {a.strip() for q in data["benefits"] for a in q["about"].split(",")}
    for part in leaves:
        if part not in named_parts:
            found.append(f"{what} {part} has no question about it")
    if WHOLE not in named_parts:
        found.append(f"no question is about {WHOLE}")
    questions = [q["id"] for q in data["benefits"]]
    expected = [f"Q{n}" for n in range(1, len(questions) + 1)]
    if questions != expected:
        found.append(f"questions are {', '.join(questions)}, not numbered in order from Q1")
    for q in data["benefits"]:
        for about in (a.strip() for a in q["about"].split(",")):
            if about != WHOLE and about not in ids:
                where = "part" if template is None else "section of the template"
                found.append(f"{q['id']} is about {about}, which is no {where}")
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
    """Text as it reads, for finding words in a page: styles and scripts gone, the text of a tag
    inside a line joined to the text beside it, the text of each block set apart, entities gone,
    quotes, dashes and spaces of every kind made one, a space a tag left before a stop gone, code
    marks dropped, and case set aside."""
    text = INLINE.sub("", UNSHOWN.sub(" ", text))
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    for kinds, one in SAME:
        text = re.sub(f"[{kinds}]", one, text)
    text = re.sub(r"\s+", " ", text.replace("`", ""))
    return re.sub(r" ([.,:;?!])", r"\1", text).strip().lower()


RAW = r"https://raw.githubusercontent.com/\1/\2/"
# Who asks for a page: this script, named as a browser-like client, as some sites refuse a bare
# "Mozilla/5.0".
AGENT = "Mozilla/5.0 (compatible; plan.py; +https://github.com/lovaizu/ccpm)"
# How often a page that asks to be called again later is asked again, and how long is waited first.
TRIES = 4
WAIT = 15


@functools.cache
def fetch(url: str) -> tuple[str, bytes]:
    """The page at the URL, its content type and its body, as a browser would be given it, each
    page opened once however many grounds quote it; a page that answers too many requests is
    asked again after a wait."""
    # A file on GitHub is read as its own text, not the page around it that holds it as data.
    url = re.sub(r"^https://github\.com/([^/]+)/([^/]+)/blob/", RAW, url)
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    tried = 0
    while True:
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.headers.get("Content-Type", ""), response.read()
        except urllib.error.HTTPError as error:
            tried += 1
            if error.code != 429:
                raise
            # tried counts up from 0 by one, so it meets TRIES before it could pass it.
            if tried == TRIES:  # pragma: no mutate
                raise
            time.sleep(WAIT * tried)


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
            # A page fails to open as the network or the server fails, a refusal and a timeout
            # among them, as its answer breaks off, or as its URL is none that can be asked for.
            # Cosmic Ray 8.7.0's ExceptionReplacer fails on a dotted name among the exceptions, so
            # makes no mutant of this line to test.
            except (OSError, http.client.HTTPException, ValueError) as error:  # pragma: no mutate
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
    return f'- [{item["title"]}]({item["url"]}), {item["by"]}: "{item["quote"]}"'


def markdown(kind: str, data: dict[str, Any], template: bool = False) -> str:
    """The best practice of the kind as Markdown: its goal, its template or its parts, and its
    benefits, then the practice for each benefit, under the question it meets."""
    questions = {q["id"]: q for q in data["benefits"]}
    out = [f"# {kind}", "", "## Goal", "", data["goal"]]
    if template:
        out += ["", "## Template", "", f"[{kind}-template.md]({kind}-template.md)"]
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


def standard(data: dict[str, Any]) -> dict[str, Any]:
    """The best practice's goal, parts and questions, without its practices: the Standard, what the
    evaluator is given, as the work's user never sees how the work was made."""
    kept = {"goal": data["goal"]}
    if "parts" in data:
        kept["parts"] = data["parts"]
    kept["benefits"] = data["benefits"]
    return kept


def groups(data: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    """The best practice's questions in groups, each named with the kind, as `<kind>/Q1`: the
    questions about the whole in one group, and the others joined where they ask of a part in
    common; the groups in the order of their first question, numbered G1 on."""
    found: list[tuple[set[str], list[str]]] = []
    for q in data["benefits"]:
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

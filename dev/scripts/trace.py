"""Decides whether the plugins' architectures and the doubles of their tests lead to what they stand
on: each decision of an architecture to a story or a rule, and each result of a double to a line of
a record that names its source. Run it from the top of the repository as
`python3 dev/scripts/trace.py tags <plugin>`, `doubles`, or `sources`.

`tags` reads only the architecture, as its writer tags each decision of Solution strategy's views
with the story or rule it carries out: each strategy and each arrow of a sequence tags a story or a
rule that exists, as does each branch condition, and each story and each rule is tagged at least
once. It exits 0 where it finds none of those faults, 1 where it reports one, and 2 where it could
not read what it checks, such as an architecture without one of those sections.

`doubles` reads each folder `recorded/` under each plugin's tests, as the guide's
Each result of a double from a record says: each line of each record names its event once, and,
where the file's name holds no version of a recorded run, its `source` and `shows`; and each call
`line(...)` or `lines(...)` of each double beside the folder, a Python file but a test, names a
record and events written out that are there. `sources` reads each page that a line's `source`
names, and checks that its words, without markup, hold the line's `shows`; it alone needs the
network. Each exits as `tags` does."""

from __future__ import annotations

import ast
import functools
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request

USAGE = "usage: trace.py tags <plugin> | doubles | sources"
STORY = re.compile(r"- (S\d+):")
RULE = re.compile(r"\s+- (P\d+\.\d+):")
# A tag at the end of a strategy's first sentence or of a sequence's arrow, such as `[P1.1]` or
# `[S1, P2.1]`.
TAG = re.compile(r"\[([^\[\]]+)\]\s*$")
# An arrow of a Mermaid sequence diagram, such as `A->>B: does`, `A-->>B: ends`, or `A-)B: calls`.
ARROW = re.compile(r"\s*[^\s:]+?\s*--?(?:>>|>|x|\))[+-]?\s*[^\s:]+\s*:(.*)")
# A branch condition of a Mermaid sequence diagram, such as `alt a point only the user can settle`.
# A bare `else` or `end` states no condition.
BRANCH = re.compile(r"\s*(?:loop|alt|else|opt|par|and|critical|break)\s+(\S.*)")
# The name of a record of a run of the real thing, `<thing>-<version>[-<what>].jsonl`, which names
# that run as the source of each of its lines.
RUN_RECORD = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*?-\d+(?:\.\d+)+(?:-[a-z0-9-]+)?\.jsonl")
URL = re.compile(r"https?://\S+")
NO_SOURCE = (
    "comes from no recorded run, as the file's name holds no version, so it carries source, the URL"
    " of the page of the documentation it comes from, and shows, the page's words"
)
# What a double calls to take one line of a record, and a run of its lines, with how many names.
TAKES = {"line": 2, "lines": 3}


class Unreadable(Exception):
    """What trace.py could not read, said so that whoever ran it can mend it."""


def section(lines: list[tuple[int, str]], heading: str, path: str) -> list[tuple[int, str]]:
    """Each line under the heading, such as `## User stories`, up to the next heading of its level
    or above, with its line number."""
    try:
        start = [line for _, line in lines].index(heading)
    except ValueError:
        raise Unreadable(f"{path}: has no {heading}, where the template puts it") from None
    level = len(heading.split(" ")[0])
    rest = lines[start + 1 :]
    fenced = False
    for n, (_, line) in enumerate(rest):
        fenced = fenced != line.startswith("```")
        if not fenced and re.match(rf"#{{1,{level}}} ", line):
            return rest[:n]
    return rest


def views(strategy: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Each line of Solution strategy's views, each section under it but Principles, its heading
    among them."""
    found = []
    inside = fenced = False
    for number, line in strategy:
        fenced = fenced != line.startswith("```")
        if not fenced and line.startswith("### "):
            inside = line != "### Principles"
        if inside:
            found.append((number, line))
    return found


def read(path: str) -> str:
    """The text of the file, which must be there."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as error:
        raise Unreadable(f"{path}: can't be read: {error.strerror}") from None


def architecture(plugin: str) -> tuple[str, list[tuple[int, str]]]:
    """The path of the plugin's architecture, and each of its lines with its number."""
    path = f"dev/{plugin}/architecture.md"
    return path, list(enumerate(read(path).split("\n"), 1))


def ids(path: str, lines: list[tuple[int, str]]) -> list[tuple[int, str, str]]:
    """Each story and each rule of the architecture, as its line, its kind, and its ID."""
    found = []
    for number, line in section(lines, "## User stories", path):
        story = STORY.match(line)
        if story:
            found.append((number, "story", story.group(1)))
    strategy = section(lines, "## Solution strategy", path)
    for number, line in section(strategy, "### Principles", path):
        rule = RULE.match(line)
        if rule:
            found.append((number, "rule", rule.group(1)))
    return found


def tagged(lines: list[tuple[int, str]]) -> list[tuple[int, str, list[str] | None]]:
    """Each strategy and each arrow of a sequence among the lines of the views, in the order of
    their lines, as its line, what it is, and each ID it tags, None where it tags none."""
    return sorted(arrows(lines) + strategies(lines))


def arrows(lines: list[tuple[int, str]]) -> list[tuple[int, str, list[str] | None]]:
    """Each arrow and each branch condition of a Mermaid block among the lines, with each ID it
    tags."""
    found: list[tuple[int, str, list[str] | None]] = []
    fenced = False
    for number, line in lines:
        if line.startswith("```"):
            fenced = not fenced and line == "```mermaid"
        elif fenced and (arrow := ARROW.fullmatch(line)):
            found.append((number, "arrow", tags_of(arrow.group(1))))
        elif fenced and (branch := BRANCH.fullmatch(line)):
            found.append((number, "branch condition", tags_of(branch.group(1))))
    return found


def strategies(lines: list[tuple[int, str]]) -> list[tuple[int, str, list[str] | None]]:
    """Each item of a list of Strategies among the lines, with each ID that its first sentence,
    up to the backslash that ends it, tags, or as a strategy that ends with no backslash where a
    line that isn't indented comes first."""
    found: list[tuple[int, str, list[str] | None]] = []
    listed = False
    item: tuple[int, str] | None = None
    # A heading after the last line ends an item still open there.
    for number, line in [*lines, (0, "### ")]:
        if item and not line.startswith("  "):
            found.append((item[0], "strategy that ends with no backslash", None))
            item = None
        elif item:
            item = (item[0], f"{item[1]} {line.strip()}")
        if line.startswith(("### ", "#### ")):
            listed = False
        listed = listed or line == "Strategies:"
        if listed and line.startswith("- "):
            item = (number, line[2:])
        if item and item[1].endswith("\\"):
            found.append((item[0], "strategy", tags_of(item[1][:-1])))
            item = None
    return found


def tags_of(text: str) -> list[str] | None:
    """Each ID that the tag at the end of the text names, None where it ends with no tag."""
    tag = TAG.search(text)
    return [each.strip() for each in tag.group(1).split(",")] if tag else None


def tag_faults(plugin: str) -> list[str]:
    """Each strategy, arrow, and branch condition that tags no story or rule, or one that isn't
    there, and each story and each rule that nothing tags."""
    path, lines = architecture(plugin)
    known = ids(path, lines)
    names = {name for _, _, name in known}
    found = []
    used = set()
    for number, what, tags in tagged(views(section(lines, "## Solution strategy", path))):
        if tags is None:
            found.append(f"{path}:{number}: the {what} tags no story or rule; end it with one")
            continue
        used.update(tags)
        found += [
            f"{path}:{number}: the {what} tags {tag}, which is no story or rule"
            for tag in tags
            if tag not in names
        ]
    found += [
        f"{path}:{number}: {kind} {name} is tagged by no strategy, arrow, or branch condition"
        for number, kind, name in known
        if name not in used
    ]
    return found


def records(plugins: list[str]) -> list[str]:
    """Each folder `recorded/` of the doubles that the plugins' tests run, under each plugin's own
    tests."""
    found = []
    for top in [f"dev/{plugin}/tests" for plugin in plugins]:
        for folder, subfolders, _ in os.walk(top):
            subfolders.sort()
            if os.path.basename(folder) == "recorded":
                found.append(folder)
    return found


def record_faults(path: str) -> tuple[list[str], dict[str, int]]:
    """Each line of the record that names no event of its own or no source, and the line number of
    each event it holds."""
    run = RUN_RECORD.fullmatch(os.path.basename(path))
    found, events = [], {}
    for number, text in enumerate(read(path).splitlines(), 1):
        try:
            each = json.loads(text)
        except ValueError:
            each = None
        if not isinstance(each, dict):
            found.append(f"{path}:{number}: isn't a JSON object")
            continue
        event = each.get("event")
        if not (isinstance(event, str) and event):
            found.append(f"{path}:{number}: names no event")
        elif event in events:
            found.append(
                f"{path}:{number}: names the event {event!r}, as line {events[event]} does"
            )
        else:
            events[event] = number
        found += [f"{path}:{number}: {fault}" for fault in source_faults(each, bool(run))]
    return found, events


def source_faults(each: dict, run: bool) -> list[str]:
    """What the line lacks of its source: where it comes from no recorded run, a URL and the words
    of the page there."""
    if run and "source" not in each:
        return []
    if "source" not in each:
        return [NO_SOURCE]
    found = []
    if not (isinstance(each["source"], str) and URL.fullmatch(each["source"])):
        found.append("its source isn't a URL")
    if not (isinstance(each.get("shows"), str) and each["shows"].strip()):
        found.append("carries no shows, the words of its page that show it")
    return found


def written_out(node: ast.expr, constants: dict[str, str]) -> str | None:
    """The string that the node writes out, as itself or as a name the module sets to one."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return constants.get(getattr(node, "id", ""))


def taken(path: str) -> list[tuple[int, str, list[str | None]]]:
    """Each call of the double that takes a line or a run of lines, as its line number, its
    function, and each name it gives, None for one not written out."""
    tree = ast.parse(read(path), path)
    constants = {
        target.id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    return [
        (node.lineno, node.func.id, [written_out(arg, constants) for arg in node.args])
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in TAKES
    ]


def call_faults(path: str, folder: str, events: dict[str, dict[str, int]]) -> list[str]:
    """Each call of the double that names a record or an event that isn't there."""
    found = []
    for number, function, names in taken(path):
        place = f"{path}:{number}"
        if len(names) != TAKES[function]:
            found.append(
                f"{place}: line takes a record and an event, and lines a record and its first and"
                " last events"
            )
        elif None in names:
            found.append(
                f"{place}: names a record or an event that isn't written out; write each as a"
                " string, or as a name the module sets to one"
            )
        elif str(names[0]) not in events:
            found.append(f"{place}: names {folder}/{names[0]}, which isn't there")
        else:
            held = events[str(names[0])]
            found += [
                f"{place}: names {event!r}, which {folder}/{names[0]} holds no line of"
                for event in names[1:]
                if event not in held
            ]
    return found


def double_faults(folder: str) -> list[str]:
    """Each fault of the records in the folder, and of each call of the doubles beside it that
    names a line of them."""
    found, events = [], {}
    for name in sorted(os.listdir(folder)):
        faults_of, events[name] = record_faults(os.path.join(folder, name))
        found += faults_of
    beside = os.path.dirname(folder)
    for name in sorted(os.listdir(beside)):
        if name.endswith(".py") and not name.startswith("test"):
            found += call_faults(os.path.join(beside, name), folder, events)
    return found


def plugins() -> list[str]:
    """Each plugin whose architecture dev/ holds."""
    return sorted(
        name for name in os.listdir("dev") if os.path.isfile(f"dev/{name}/architecture.md")
    )


def doubles() -> list[str]:
    """Each fault of each double's records and calls, which no network decides."""
    return [fault for folder in records(plugins()) for fault in double_faults(folder)]


def page(url: str, pages: dict[str, str]) -> str:
    """The words of the page at the URL, without its markup or scripts, each run of spaces one."""
    if url not in pages:
        request = urllib.request.Request(url, headers={"User-Agent": "trace.py"})
        try:
            with urllib.request.urlopen(request, timeout=30) as reply:
                text = reply.read().decode("utf-8", "replace")
        except (OSError, urllib.error.URLError) as error:
            raise Unreadable(f"{url}: can't be read: {error}") from None
        text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        pages[url] = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())
    return pages[url]


def sources() -> list[str]:
    """Each line taken from the documentation whose page doesn't show its words."""
    found: list[str] = []
    pages: dict[str, str] = {}
    for folder in records(plugins()):
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            for number, text in enumerate(read(path).splitlines(), 1):
                each = json.loads(text)
                if "source" not in each:
                    continue
                words = " ".join(each["shows"].split())
                if words not in page(each["source"].split("#")[0], pages):
                    found.append(f"{path}:{number}: {each['source']} doesn't show {words!r}")
    return found


def main(argv: list[str]) -> int:
    commands = {"doubles": doubles, "sources": sources}
    by_plugin = {"tags": tag_faults}
    if argv[:1] and argv[0] in by_plugin and len(argv) == 2:
        run = functools.partial(by_plugin[argv[0]], argv[1])
    elif len(argv) == 1 and argv[0] in commands:
        run = commands[argv[0]]
    else:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        found = run()
    except Unreadable as error:
        print(f"trace.py: {error}", file=sys.stderr)
        return 2
    for line in found:
        print(f"trace.py: {line}", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

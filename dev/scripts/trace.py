"""Decides whether each decision of a plugin's architecture leads to what it stands on, a story or
a rule. Run it from the top of the repository as `python3 dev/scripts/trace.py tags <plugin>`.

`tags` reads only the architecture, as its writer tags each decision of Solution strategy's views
with the story or rule it carries out: each strategy and each arrow of a sequence tags a story or a
rule that exists, as does each branch condition, and each story and each rule is tagged at least
once. It exits 0 where it finds none of those faults, 1 where it reports one, and 2 where it could
not read what it checks, such as an architecture without one of those sections."""

from __future__ import annotations

import re
import sys

USAGE = "usage: trace.py tags <plugin>"
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


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] != "tags":
        print(USAGE, file=sys.stderr)
        return 2
    try:
        found = tag_faults(argv[1])
    except Unreadable as error:
        print(f"trace.py: {error}", file=sys.stderr)
        return 2
    for line in found:
        print(f"trace.py: {line}", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

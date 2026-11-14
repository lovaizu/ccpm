"""Decides whether the plugins' tests lead by their names to what they stand on: each test case to
what it supports one level up, each element of the plugin's architecture to an integration case,
each case of a principle to a failure with its part taken out, and each result of a double to a
line of a record that names its source. Run it from the top of the repository as
`python3 dev/scripts/trace.py check <plugin>`, `doubles`, or `sources`.

It reads what dev/plugin-development-guide.md's Test says a plugin keeps, and the elements as the
template of the architecture best practice names them:

- each story by its `S<n>` in User stories of `dev/<plugin>/architecture.md`
- each principle by its heading under Principles
- each role and component by its name in Components' list of what each decides alone
- each kind of data by each `<text class="name">` of `dev/<plugin>/images/data-model.svg`, the one
  place that names every kind, as Data model's text names only the kinds a reader could confuse
- each key result by its `KR<n>.<m>` in `dev/<plugin>/product-vision.md`
- each case, a function `test...` of a file `test*.py` under `dev/<plugin>/tests/`, at the top or in
  a class, with each name that its `@pytest.mark.supports(...)` gives

A case in `e2e/` names a key result, one in `integration/` an element, and one in `unit/`,
`properties/`, or `prompts/`, the unit tests, an integration case by its function's name. Each
integration case that names a principle takes the fixture `broken`, and trace.py runs it alone by
pytest with `TRACE_BROKEN=1`, under which the fixture takes out the part that holds the principle,
as the guide's A principle's test seen to fail says. It exits 0 where every case names only what
exists one level up, every element has an integration case, and every case of a principle fails
with its part taken out, 1 where it reports one that doesn't, and 2 where it could not read or run
what it checks, such as an architecture without one of those sections, as a check that can't read
its input passes nothing. A 0 shows only that every name leads somewhere and that each case of a
principle can fail, not that the cases are enough, as N13 of
plugins/rn/domain/best-practices/architecture/best-practice.md says.

`doubles` reads each folder `recorded/` under dev/tests/ and each plugin's tests, as the guide's
Each result of a double from a record says: each line of each record names its event once, and,
where the file's name holds no version of a recorded run, its `source` and `shows`; and each call
`line(...)` or `lines(...)` of each double beside the folder, a Python file but a test, names a
record and events written out that are there. `sources` reads each page that a line's `source`
names, and checks that its words, without markup, hold the line's `shows`; it alone needs the
network. Each exits as `check` does."""

from __future__ import annotations

import ast
import functools
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from typing import NamedTuple

USAGE = "usage: trace.py check <plugin> | doubles | sources"
# The folder of each level's cases, and the level whose names they support.
LEVELS = {
    "unit": "integration",
    "properties": "integration",
    "prompts": "integration",
    "integration": "element",
    "e2e": "key result",
}
STORY = re.compile(r"- (S\d+):")
COMPONENT = re.compile(r"- (.+)\\$")
KEY_RESULT = re.compile(r"\s*- (KR\d+\.\d+):")
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
# What the summary of a pytest run says of a case that failed.
FAILED = re.compile(r"\b\d+ (failed|errors?)\b")


class Unreadable(Exception):
    """What trace.py could not read, said so that whoever ran it can mend it."""


class Case(NamedTuple):
    """One test case: where it starts, its function's name, each name it supports, None for one
    not written out, its node ID, by which pytest runs it alone, and whether it takes `broken`."""

    place: str
    name: str
    names: list[str | None]
    node: str
    broken: bool


def section(lines: list[str], heading: str, path: str) -> list[tuple[int, str]]:
    """Each line under the `## ` heading up to the next, with its line number."""
    try:
        start = lines.index(heading)
    except ValueError:
        raise Unreadable(f"{path}: has no {heading}, where the template puts it") from None
    rest = lines[start + 1 :]
    end = next((n for n, line in enumerate(rest) if line.startswith("## ")), len(rest))
    return list(enumerate(rest[:end], start + 2))


def components(lines: list[tuple[int, str]], path: str) -> list[tuple[int, str]]:
    """Each name in Components' list of what each decides alone, with its line number."""
    numbered = iter(lines)
    if not any(line == "What each decides alone:" for _, line in numbered):
        raise Unreadable(f"{path}: Components has no line `What each decides alone:`")
    found = []
    for number, line in numbered:
        if line.startswith("The choices made"):
            break
        named = COMPONENT.match(line)
        if named:
            found.append((number, named.group(1)))
    return found


def read(path: str) -> str:
    """The text of the file, which must be there."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as error:
        raise Unreadable(f"{path}: can't be read: {error.strerror}") from None


def elements(plugin: str) -> list[tuple[str, str, str]]:
    """Each element of the plugin's architecture, as its place, its kind, and its name."""
    path = f"dev/{plugin}/architecture.md"
    lines = read(path).split("\n")
    found = []
    for number, line in section(lines, "## User stories", path):
        story = STORY.match(line)
        if story:
            found.append((f"{path}:{number}", "story", story.group(1)))
    for number, line in section(lines, "## Principles", path):
        if line.startswith("### "):
            found.append((f"{path}:{number}", "principle", line[4:].strip()))
    for number, name in components(section(lines, "## Components", path), path):
        found.append((f"{path}:{number}", "component", name))
    figure = f"dev/{plugin}/images/data-model.svg"
    try:
        root = ET.fromstring(read(figure))
    except ET.ParseError as error:
        raise Unreadable(f"{figure}: isn't XML: {error}") from None
    for text in root.iter():
        if text.tag.endswith("text") and "name" in text.get("class", "").split():
            found.append((figure, "kind of data", "".join(text.itertext()).strip()))
    return found


def key_results(plugin: str) -> set[str]:
    """The ID of each key result of the plugin's product vision."""
    text = read(f"dev/{plugin}/product-vision.md")
    return {each.group(1) for each in map(KEY_RESULT.match, text.split("\n")) if each}


def supports_mark(decorator: ast.expr) -> ast.Call | None:
    """The decorator, where it's `pytest.mark.supports(...)`, or `mark.supports(...)` where the
    file takes `mark` from pytest."""
    if not (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)):
        return None
    mark = decorator.func.value
    named = mark.attr if isinstance(mark, ast.Attribute) else getattr(mark, "id", None)
    return decorator if decorator.func.attr == "supports" and named == "mark" else None


def written(arg: ast.expr) -> str | None:
    """The name that a mark's argument writes out, or None where it isn't a string written out."""
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value
    return None


def supported(function: ast.FunctionDef) -> list[str | None]:
    """Each name that the case's marks `supports` give, None for one not written out."""
    marks = [supports_mark(each) for each in function.decorator_list]
    return [written(arg) for mark in marks if mark for arg in mark.args]


def cases_in(path: str) -> list[Case]:
    """Each case of the test file."""
    try:
        tree = ast.parse(read(path), path)
    except SyntaxError as error:
        raise Unreadable(f"{path}:{error.lineno}: isn't Python: {error.msg}") from None
    functions = [(path, node) for node in tree.body if isinstance(node, ast.FunctionDef)]
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            inside = f"{path}::{node.name}"
            functions += [(inside, f) for f in node.body if isinstance(f, ast.FunctionDef)]
    return [
        Case(
            f"{path}:{min([f.lineno] + [d.lineno for d in f.decorator_list])}",
            f.name,
            supported(f),
            f"{owner}::{f.name}",
            "broken" in [arg.arg for arg in f.args.args],
        )
        for owner, f in functions
        if f.name.startswith("test")
    ]


def cases(plugin: str) -> tuple[dict[str, list[Case]], list[str]]:
    """The cases of each level of the plugin, and each test file that lies in no level's folder."""
    top = f"dev/{plugin}/tests"
    found: dict[str, list[Case]] = {level: [] for level in LEVELS}
    stray = []
    for folder, subfolders, files in os.walk(top):
        subfolders.sort()
        for name in sorted(files):
            if not (name.startswith("test") and name.endswith(".py")):
                continue
            path = os.path.join(folder, name)
            level = os.path.relpath(path, top).split(os.sep)[0]
            if level not in LEVELS:
                stray.append(
                    f"{path}: lies in no level's folder; move it to one of {top}/"
                    f"{', '.join(LEVELS)}"
                )
                continue
            found[level] += cases_in(path)
    return found, stray


def fails_broken(case: Case) -> bool:
    """Whether pytest fails the case run alone with TRACE_BROKEN=1, which has its fixture `broken`
    take out the part that holds its principle."""
    env = dict(os.environ, TRACE_BROKEN="1")
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", case.node]
    ran = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
    # pytest exits 0 where every test passed or was skipped, and 1 where one failed, which its
    # summary then counts. Python exits 1 too where pytest isn't there to run.
    failed = ran.returncode == 1 and FAILED.search(ran.stdout)
    if ran.returncode not in (0, 1) or ran.returncode == 1 and not failed:
        said = (ran.stdout + ran.stderr).strip().split("\n")[-1]
        raise Unreadable(f"{case.node}: pytest couldn't run it, exit {ran.returncode}: {said}")
    return bool(failed)


def broken_faults(integration: list[Case], principles: set[str]) -> list[str]:
    """Each integration case of a principle that takes no `broken`, or that doesn't fail where
    `broken` takes out the part that holds the principle."""
    found = []
    for case in integration:
        if not principles.intersection(case.names):
            continue
        if not case.broken:
            found.append(
                f"{case.place}: {case.name} names a principle but takes no fixture broken, which"
                " takes out the part that holds it where TRACE_BROKEN is 1"
            )
        elif not fails_broken(case):
            found.append(
                f"{case.place}: {case.name} doesn't fail with TRACE_BROKEN=1, so it doesn't show"
                " the parts keeping its principle; have its fixture broken take out the part"
                " that holds the principle"
            )
    return found


def leads_to(case: Case, above: set[str], what: str) -> list[str]:
    """Each name of the case that leads to nothing one level up, or the case's lack of one."""
    if not case.names:
        hint = f"mark it with @pytest.mark.supports and the name of the {what} it supports"
        return [f"{case.place}: {case.name} names nothing one level up; {hint}"]
    found = []
    for name in case.names:
        if name is None:
            found.append(
                f"{case.place}: {case.name} names a value that isn't written out; write the name"
                " itself in @pytest.mark.supports"
            )
        elif name not in above:
            found.append(f"{case.place}: {case.name} names {name}, which is no {what}")
    return found


def name_faults(plugin: str, level_cases: dict[str, list[Case]], named: set[str]) -> list[str]:
    """Each case of each level that names nothing one level up, or what isn't there."""
    above = {
        "integration": {case.name for case in level_cases["integration"]},
        "element": named,
        "key result": key_results(plugin),
    }
    what = {
        "integration": f"integration case of dev/{plugin}/tests/integration/",
        "element": f"story, principle, component, or kind of data of dev/{plugin}/architecture.md",
        "key result": f"key result of dev/{plugin}/product-vision.md",
    }
    return [
        fault
        for level, up in LEVELS.items()
        for case in level_cases[level]
        for fault in leads_to(case, above[up], what[up])
    ]


def untested(named: list[tuple[str, str, str]], integration: list[Case]) -> list[str]:
    """Each element of the architecture that no integration case names."""
    tested = {name for case in integration for name in case.names}
    return [
        f"{place}: {kind} {name} has no integration test that names it"
        for place, kind, name in named
        if name not in tested
    ]


def faults(plugin: str) -> list[str]:
    """Each test file in no level's folder, each case that names nothing one level up or what
    isn't there, each element that no integration case names, and each case of a principle not
    seen to fail with its part taken out."""
    named = elements(plugin)
    level_cases, stray = cases(plugin)
    principles = {name for _, kind, name in named if kind == "principle"}
    return (
        stray
        + name_faults(plugin, level_cases, {name for _, _, name in named})
        + untested(named, level_cases["integration"])
        + broken_faults(level_cases["integration"], principles)
    )


def records(plugins: list[str]) -> list[str]:
    """Each folder `recorded/` of the doubles that the plugins' tests run: of dev/tests/, which the
    plugins share, and of each plugin's own tests."""
    found = []
    for top in ["dev/tests"] + [f"dev/{plugin}/tests" for plugin in plugins]:
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
    if argv[:1] == ["check"] and len(argv) == 2:
        run = functools.partial(faults, argv[1])
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

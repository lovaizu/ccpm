"""The forms the orchestrator and each role give their judgments in, each checked against the run's
items and the work, so a slip is named where it is made."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable
from typing import Any, Callable, NamedTuple

import records

LINES = re.compile(r"^(.+):(\d+)(?:-(\d+))?$")
# A document's parts open at its top headings; any other file is one part.
DOCUMENT = ".md"
TOP = "## "
# The shapes of a Good: one, with the lines that give it, or one for each part of the work, for an
# item asked of each part.
ONE = ("good", "lines")
EACH = ("parts",)
# A form given inside a ```json fence, as a model often writes JSON, is the form itself.
FENCE = re.compile(r"^\s*```(?:json)?\s*\n(.*)\n\s*```\s*$", re.DOTALL)


# The roles a lesson on the run may be for.
ROLES = ("orchestrator", "generator", "first-user", "evaluator", "learner")


class Grounds(NamedTuple):
    """What a form's lines and quotes are found in: the work, and the records of the agents the
    learner's quotes come from."""

    work: list[str]
    records: tuple[str, ...]


class Form(NamedTuple):
    """What an item may hold besides its checklist and ID, one shape of keys each; whether every
    item is given; whether questions are asked; and what else the form holds beside its items,
    checked against the grounds. A form of no shapes gives no items."""

    shapes: tuple[tuple[str, ...], ...]
    every: bool = False
    asks: bool = False
    more: Callable[[dict[str, Any], Grounds], list[str]] | None = None


# Before the work is made, the orchestrator says for every item what in the CCS and its files gives
# its Good, or the question it waits on.
CHECK = Form((("can",), ("question",)), every=True, asks=True)
# The orchestrator judges, so its decision gives a Good, a question or what the receiver gets once
# it has its Good with the places of the work where it is not found. The evaluator looks only for
# the Good the work gives, so it names only the items it finds a Good for, and a script names the
# rest.
DECISION = Form((ONE, EACH, ("question",), ("gets", "places")), every=True, asks=True)
GOOD = Form((ONE, EACH))
# The first user gives every item the Good it found, or the places of the work where it looked for
# it, what it did there and what it did not get, so that the work made again is aimed at where it
# stopped and at what was missing there.
FIRST_READING = Form((ONE, EACH, ("places", "did", "lacking")), every=True)


def worded(value: Any) -> bool:
    """Whether the value is words, not empty."""
    return isinstance(value, str) and bool(value.strip())


def spaced(words: str) -> str:
    """The words with every run of space, tab or line end as one space, so a quote across a line
    break is found as written."""
    return " ".join(words.split())


def span(line: str) -> tuple[str, int, int]:
    found = LINES.match(line)
    assert found
    return (
        os.path.realpath(found.group(1)),
        int(found.group(2)),
        int(found.group(3) or found.group(2)),
    )


def lessons(data: dict[str, Any], at: Grounds) -> list[str]:
    """The learner gives how the run went, each lesson for a role of turn and resting on words of
    a record it was shown, and what it checked, so that a reply of no lesson says its scope."""
    said: list[str] = []
    process = data.get("process")
    if not isinstance(process, list):
        said.append(
            'give "process": [{"role", "lesson", "grounds"}, ...], each lesson on how the run'
            " went, or [] when you found none"
        )
        process = []
    if not worded(data.get("checked")):
        said.append('give "checked": what you checked of the run, in words')
    for n, lesson in enumerate(process, 1):
        name = f"lesson {n}"
        if (
            not isinstance(lesson, dict)
            or set(lesson) != {"role", "lesson", "grounds"}
            or lesson["role"] not in ROLES
            or not worded(lesson["lesson"])
        ):
            said.append(
                f'{name} must hold "role", one of {", ".join(ROLES)}, "lesson" in words, and'
                ' "grounds"'
            )
            continue
        said += ground_problems(name, lesson["grounds"], at.records)
    return said


def ground_problems(name: str, grounds: Any, kept: tuple[str, ...]) -> list[str]:
    if not isinstance(grounds, list) or not grounds:
        return [f'{name} gives its grounds as no list; give [{{"record": ..., "quote": ...}}, ...]']
    said: list[str] = []
    for k, ground in enumerate(grounds, 1):
        number = ground.get("record") if isinstance(ground, dict) else None
        if (
            not isinstance(ground, dict)
            or set(ground) != {"record", "quote"}
            or not isinstance(number, int)
            or isinstance(number, bool)
            or not 1 <= number <= len(kept)
            or not worded(ground["quote"])
        ):
            said.append(
                f'{name}: ground {k} must hold "record", its number from 1 to {len(kept)}, and'
                ' "quote", its words'
            )
        elif spaced(ground["quote"]) not in spaced(records.shown(kept[number - 1])):
            said.append(
                f"{name}: ground {k} is not in record {number} as written; quote its words as they"
                " are"
            )
    return said


# The generator claims the Good it set for every item, or the question it waits on.
CLAIM = Form((ONE, EACH, ("question",)), every=True, asks=True)
# The learner says how the run went alone, since a lesson on what the work should say tells the
# generator how to give a Good, which is the generator's to decide.
LEARNT = Form((), more=lessons)


def parse(text: str, form: Form) -> dict[str, Any] | None:
    """The form as JSON, or None when it is not an object of the lists it takes."""
    try:
        data = json.loads(unfenced(text))
    except ValueError:
        return None
    if not isinstance(data, dict) or not all(isinstance(data.get(k), list) for k in listed(form)):
        return None
    return data


def listed(form: Form) -> tuple[str, ...]:
    """The lists the form takes."""
    return (("items",) if form.shapes else ()) + (("questions",) if form.asks else ())


def unfenced(text: str) -> str:
    """The text without the ```json fence around it, if it has one."""
    fenced = FENCE.match(text)
    return fenced.group(1) if fenced else text


def check(
    text: str,
    items: list[dict[str, str]],
    work: list[str],
    form: Form,
    asked: int = 0,
    records: tuple[str, ...] = (),
    each: Iterable[tuple[str, str]] = (),
) -> list[str]:
    """What is wrong with the form, each said with what to give instead; empty when it is filled.
    The items are those the form judges; `asked` counts the questions already asked, which its
    own questions are numbered after; `records` are the records its quotes of a record are found
    in; `each` names the items asked of each part of the work."""
    data = parse(text, form)
    if data is None:
        lists = ", ".join(f'"{k}": [...]' for k in listed(form))
        return ["give it as JSON: {" + (lists or '"process": [...], "checked": "..."') + "}"]
    said = item_problems(data["items"], items, work, form, list(each)) if form.shapes else []
    if form.asks:
        said += question_problems(data, asked)
    if form.more:
        said += form.more(data, Grounds(work, records))
    return said


def taken(text: str, offer: dict[str, Any]) -> list[str]:
    """What is wrong with what the orchestrator takes of the lessons offered, each by its number;
    empty when it is filled."""
    try:
        data = json.loads(unfenced(text))
    except ValueError:
        data = None
    if not isinstance(data, dict) or not isinstance(data.get("process"), list):
        return ['give it as JSON: {"process": [...]}']
    said: list[str] = []
    count = len(offer["process"])
    numbers: list[Any] = []
    for n in data["process"]:
        if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= count:
            said.append(f"lesson {n} is not one of 1 to {count}; take each by its number")
        elif n in numbers:
            said.append(f"lesson {n} is given twice; take each once")
        numbers.append(n)
    return said


def lines_problems(name: str, lines: Any, paths: list[str], what: str) -> list[str]:
    if not isinstance(lines, list) or not lines:
        return [f"{name} names no lines; give the lines, each as <path>:<from>-<to>"]
    return [
        f"{name}: {line} is not {what}; give each as <path>:<from>-<to>"
        for line in lines
        if not in_files(line, paths)
    ]


def item_problems(
    given: list[Any],
    items: list[dict[str, str]],
    work: list[str],
    form: Form,
    each: list[tuple[str, str]],
) -> list[str]:
    keys = [(i["checklist"], i["item"]) for i in items]
    said: list[str] = []
    seen: list[tuple[str, str]] = []
    for item in given:
        key = (item.get("checklist"), item.get("item")) if isinstance(item, dict) else None
        name = f"{key[0]} {key[1]}" if key else json.dumps(item)
        if key not in keys:
            said.append(f"{name} is not an item judged here; give each item by its checklist")
            continue
        if key in seen:
            said.append(f"{name} is given twice; give each item once")
            continue
        seen.append(key)
        # An item asked of each part gives a Good for every part, and any other one Good.
        shapes = [s for s in form.shapes if s not in ((ONE,) if key in each else (EACH,))]
        held = [s for s in shapes if all(k in item for k in s)]
        shaped = [k for s in held for k in s]
        rest = [k for k in item if k not in ("checklist", "item") and k not in shaped]
        if len(held) != 1 or rest:
            asked = ", as it is asked of each part" if key in each else ""
            said.append(f"{name} must hold {allowed(shapes)}{asked}")
            continue
        said += value_problems(name, item, work)
    if form.every:
        said += [
            f"{c} {i} is left out; give every item judged here"
            for c, i in keys
            if (c, i) not in seen
        ]
    return said


def allowed(shapes: list[tuple[str, ...]]) -> str:
    """The shapes an item may take, in words."""
    named = [" with ".join(f'"{k}"' for k in shape) for shape in shapes]
    *others, last = named
    return f"one of {', '.join(others)} or {last}" if others else last


def value_problems(name: str, item: dict[str, Any], work: list[str]) -> list[str]:
    said: list[str] = []
    for key in ("can", "good", "gets", "did", "lacking"):
        if key in item and not worded(item[key]):
            said.append(f'{name} has an empty "{key}"; say it in words')
    if "question" in item and not (
        isinstance(item["question"], int) and not isinstance(item["question"], bool)
    ):
        said.append(f"{name}'s \"question\" is not a number; give the question's, from 1")
    if "lines" in item:
        said += lines_problems(name, item["lines"], work, "lines of the work")
    if "places" in item:
        said += lines_problems(name, item["places"], work, "lines of the work")
    if "parts" in item:
        said += parts_problems(name, item["parts"], work)
    return said


def parts_problems(name: str, given: Any, work: list[str]) -> list[str]:
    """An item asked of each part gives, for every part of the work, the Good the part gives, at
    lines inside it."""
    if not isinstance(given, list):
        return [f'{name} gives its parts as no list; give [{{"part", "good", "lines"}}, ...]']
    whole = parts(work)
    said: list[str] = []
    seen: list[str] = []
    for k, part in enumerate(given, 1):
        if (
            not isinstance(part, dict)
            or set(part) != {"part", "good", "lines"}
            or not worded(part["good"])
        ):
            said.append(f'{name}: part {k} must hold "part", "good" and "lines", the Good in words')
        elif part["part"] not in whole:
            said.append(
                f"{name}: {part['part']} is not a part of the work; give each as one of"
                f" {', '.join(f'`{p}`' for p in whole)}"
            )
        elif part["part"] in seen:
            said.append(f"{name}: {part['part']} is given twice; give each part once")
        else:
            seen.append(part["part"])
            inside = lines_problems(name, part["lines"], work, "lines of the work")
            said += inside or [
                f"{name}: {line} is not inside its part {part['part']}; name lines of the part"
                for line in part["lines"]
                if not within_part(line, part["part"])
            ]
    # A part left out has no Good, said once the parts given are in their form.
    return said or [
        f"{name}: {p} has no Good; give a Good for every part, as the item has its Good only where"
        " every part gives it"
        for p in whole
        if p not in seen
    ]


def within_part(line: str, part: str) -> bool:
    path, start, end = span(line)
    part_path, part_start, part_end = span(part)
    return path == part_path and part_start <= start and end <= part_end


def parts(work: list[str]) -> list[str]:
    """The parts of the work, each as its lines: a document's sections under its top headings,
    with the title and opening as one, and each other file whole; an empty file has none."""
    found: list[str] = []
    for path in work:
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        starts = [1] if lines else []
        fenced = False
        for n, line in enumerate(lines, 1):
            if line.startswith("```"):
                fenced = not fenced
            elif (
                path.endswith(DOCUMENT) and not fenced and line.startswith(TOP) and n not in starts
            ):
                starts.append(n)
        ends = [n - 1 for n in starts[1:]] + [len(lines)]
        found += [f"{path}:{a}-{b}" for a, b in zip(starts, ends)]
    return found


def in_files(line: Any, paths: list[str]) -> bool:
    """Whether the line names lines that are there in one of the files."""
    found = LINES.match(line) if isinstance(line, str) else None
    if not found or not os.path.isfile(found.group(1)) or not within(found.group(1), paths):
        return False
    start, end = int(found.group(2)), int(found.group(3) or found.group(2))
    with open(found.group(1), encoding="utf-8") as f:
        count = len(f.read().splitlines())
    return 1 <= start <= end <= count


def question_problems(data: dict[str, Any], asked: int) -> list[str]:
    said: list[str] = []
    questions = data["questions"]
    waiting = [i.get("question") for i in data["items"] if isinstance(i, dict)]
    for n, question in enumerate(questions, asked + 1):
        if not isinstance(question, dict) or not all(
            isinstance(question.get(k), str) and question[k].strip()
            for k in ("question", "recommended")
        ):
            said.append(
                f'question {n} must hold "question" and "recommended", the answer you'
                " recommend, each in words"
            )
        elif n not in waiting:
            said.append(f"question {n} has no item waiting on it; name it at the item it settles")
    said += [
        f"question {n} is waited on but not given; add it to the questions"
        for n in waiting
        if isinstance(n, int) and not 1 <= n <= asked + len(questions)
    ]
    return said


def within(path: str, paths: list[str]) -> bool:
    """Whether the path is one of the files, however either is written."""
    return os.path.realpath(path) in {os.path.realpath(p) for p in paths}

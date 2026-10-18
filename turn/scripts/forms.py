"""The forms the orchestrator and each role give their judgments in, each checked against the run's
items and the work, so a slip is named where it is made."""

from __future__ import annotations

import json
import os
import re
from typing import Any, NamedTuple

LINES = re.compile(r"^(.+):(\d+)(?:-(\d+))?$")
# A form given inside a ```json fence, as a model often writes JSON, is the form itself.
FENCE = re.compile(r"^\s*```(?:json)?\s*\n(.*)\n\s*```\s*$", re.DOTALL)


class Statements(NamedTuple):
    """A list of the work's statements a form holds beside its items: its key, the keys each
    statement holds, and whether the list must be given."""

    key: str
    holds: tuple[str, ...]
    required: bool


class Form(NamedTuple):
    """What an item may hold besides its checklist and ID, one shape of keys each; whether every
    item is given; whether questions are asked; and the statements it holds, if any."""

    shapes: tuple[tuple[str, ...], ...]
    every: bool
    asks: bool
    statements: Statements | None = None


# Before the work is made, the orchestrator says for every item what in the CCS and its files gives
# its Good, or the question it waits on.
CHECK = Form((("can",), ("question",)), every=True, asks=True)
# The orchestrator judges, so its reading and its decision give a Good, a question or what the
# receiver gets once it has its Good; the generator claims the Good it set for every item, or the
# question it waits on. The first user and the evaluator look only for the Good the work gives, so
# each names only the items it finds a Good for, and a script names the rest.
# The generator names, for each statement the work makes of its subject, the lines of the CCS or
# its files it rests on; the orchestrator's reading names each statement it sends back, as one whose
# source it does not find there, or that says otherwise.
DECISION = Form((("good", "lines"), ("question",), ("gets",)), every=True, asks=True)
READING = DECISION._replace(statements=Statements("unsourced", ("lines", "gets"), required=False))
CLAIM = Form(
    (("good", "lines"), ("question",)),
    every=True,
    asks=True,
    statements=Statements("statements", ("lines", "from"), required=True),
)
GOOD = Form((("good", "lines"),), every=False, asks=False)
# The learner says, for every item but those waiting on a question, what makes its Good: how the
# work would give it, or what gives it now, so the remake keeps it.
LEARNT = Form((("learnt",),), every=True, asks=False)


def parse(text: str, form: Form) -> dict[str, Any] | None:
    """The form as JSON, or None when it is not an object of the lists it takes."""
    try:
        data = json.loads(unfenced(text))
    except ValueError:
        return None
    keys = ("items", "questions") if form.asks else ("items",)
    if not isinstance(data, dict) or not all(isinstance(data.get(k), list) for k in keys):
        return None
    return data


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
    sources: tuple[str, ...] = (),
) -> list[str]:
    """What is wrong with the form, each said with what to give instead; empty when it is filled.
    The items are those the form judges; `asked` counts the questions already asked, which its
    own questions are numbered after; `sources` are the files and folders statements rest on."""
    data = parse(text, form)
    if data is None:
        shape = '{"items": [...], "questions": [...]}' if form.asks else '{"items": [...]}'
        return [f"give it as JSON: {shape}"]
    said = item_problems(data["items"], items, work, form)
    if form.asks:
        said += question_problems(data, asked)
    if form.statements:
        said += statement_problems(data, form.statements, work, sources)
    return said


def statement_problems(
    data: dict[str, Any], form: Statements, work: list[str], sources: tuple[str, ...]
) -> list[str]:
    shape = "{" + ", ".join(f'"{k}"' for k in form.holds) + "}"
    if form.key not in data:
        if not form.required:
            return []
        return [f'give "{form.key}": [{shape}, ...], each statement the work makes of its subject']
    given = data[form.key]
    if not isinstance(given, list):
        return [f'"{form.key}" is not a list; give it as [{shape}, ...]']
    said: list[str] = []
    for n, statement in enumerate(given, 1):
        name = f"statement {n} of {form.key}"
        if not isinstance(statement, dict) or set(statement) != set(form.holds):
            said.append(f"{name} must hold {shape} alone")
            continue
        said += lines_problems(name, statement["lines"], work, "lines of the work")
        if "from" in statement:
            said += lines_problems(
                name, statement["from"], list(sources), "lines of the CCS or a file it names"
            )
        if "gets" in statement and not (
            isinstance(statement["gets"], str) and statement["gets"].strip()
        ):
            said.append(f'{name} has an empty "gets"; say it in words')
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
    given: list[Any], items: list[dict[str, str]], work: list[str], form: Form
) -> list[str]:
    keys = [(i["checklist"], i["item"]) for i in items]
    said: list[str] = []
    seen: list[tuple[str, str]] = []
    named = [" with ".join(f'"{k}"' for k in shape) for shape in form.shapes]
    *others, last = named
    allowed = f"one of {', '.join(others)} or {last}" if others else last
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
        held = [s for s in form.shapes if all(k in item for k in s)]
        # Not mutated: both sets taken away lie inside the item, so `^` gives the same.
        rest = set(item) - {"checklist", "item"} - {k for s in held for k in s}  # pragma: no mutate
        if len(held) != 1 or rest:
            said.append(f"{name} must hold {allowed}")
            continue
        said += value_problems(name, item, work)
    if form.every:
        said += [
            f"{c} {i} is left out; give every item judged here"
            for c, i in keys
            if (c, i) not in seen
        ]
    return said


def value_problems(name: str, item: dict[str, Any], work: list[str]) -> list[str]:
    said: list[str] = []
    for key in ("can", "good", "gets", "learnt"):
        if key in item and not (isinstance(item[key], str) and item[key].strip()):
            said.append(f'{name} has an empty "{key}"; say it in words')
    if "question" in item and not (
        isinstance(item["question"], int) and not isinstance(item["question"], bool)
    ):
        said.append(f"{name}'s \"question\" is not a number; give the question's, from 1")
    if "lines" in item:
        said += lines_problems(name, item["lines"], work, "lines of the work")
    return said


def in_files(line: Any, paths: list[str]) -> bool:
    """Whether the line names lines that are there in one of the files, or in a file inside one
    of the folders."""
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
    real = os.path.realpath(path)
    for named in paths:
        top = os.path.realpath(named)
        if real == top or (os.path.isdir(top) and real.startswith(top + os.sep)):
            return True
    return False

"""The forms the orchestrator's reading and the generator's reply take, each checked against the run's
items and the work, so a slip is named where it is made."""

from __future__ import annotations

import json
import os
import re
from typing import Any

SHAPE = '{"items": [...], "questions": [...]}'
LINES = re.compile(r"^(.+):(\d+)(?:-(\d+))?$")
# What an item may hold, besides its checklist and ID, in each form: the orchestrator judges, so
# its reading gives a Good, a question or what the receiver gets once it has its Good; the
# generator only claims, so its reply gives lines or a question.
READING = (("good", "lines"), ("question",), ("gets",))
CLAIM = (("lines",), ("question",))


def parse(text: str) -> dict[str, Any] | None:
    """The form as JSON, or None when it is not an object of items and questions."""
    try:
        data = json.loads(text)
    except ValueError:
        return None
    if not isinstance(data, dict) or not all(
        isinstance(data.get(k), list) for k in ("items", "questions")
    ):
        return None
    return data


def check(text: str, run: dict[str, Any], shapes: tuple[tuple[str, ...], ...]) -> list[str]:
    """What is wrong with the form, each said with what to give instead; empty when it is filled."""
    data = parse(text)
    if data is None:
        return [f"give it as JSON: {SHAPE}"]
    said = item_problems(data["items"], run, shapes)
    said += question_problems(data, shapes)
    return said


def item_problems(
    given: list[Any], run: dict[str, Any], shapes: tuple[tuple[str, ...], ...]
) -> list[str]:
    keys = [(i["checklist"], i["item"]) for i in run["items"]]
    said: list[str] = []
    seen: list[tuple[str, str]] = []
    named = [" with ".join(f'"{k}"' for k in shape) for shape in shapes]
    allowed = ", ".join(named[:-1]) + " or " + named[-1]
    for item in given:
        key = (item.get("checklist"), item.get("item")) if isinstance(item, dict) else None
        name = f"{key[0]} {key[1]}" if key else json.dumps(item)
        if key not in keys:
            said.append(f"{name} is in no checklist of the run; give each item by its checklist")
            continue
        if key in seen:
            said.append(f"{name} is given twice; give each item once")
            continue
        seen.append(key)
        held = [s for s in shapes if all(k in item for k in s)]
        rest = set(item) - {"checklist", "item"} - {k for s in held for k in s}
        if len(held) != 1 or rest:
            said.append(f"{name} must hold one of {allowed}")
            continue
        said += value_problems(name, item, run["work"])
    said += [
        f"{c} {i} is left out; give every item of every checklist"
        for c, i in keys
        if (c, i) not in seen
    ]
    return said


def value_problems(name: str, item: dict[str, Any], work: list[str]) -> list[str]:
    said: list[str] = []
    for key in ("good", "gets"):
        if key in item and not (isinstance(item[key], str) and item[key].strip()):
            said.append(f'{name} has an empty "{key}"; say it in words')
    if "question" in item and not (
        isinstance(item["question"], int) and not isinstance(item["question"], bool)
    ):
        said.append(f"{name}'s \"question\" is not a number; give the question's, from 1")
    if "lines" in item:
        lines = item["lines"]
        if not isinstance(lines, list) or not lines:
            said.append(f"{name} names no lines; give the lines, each as <path>:<from>-<to>")
        else:
            said += [
                f"{name}: {line} is not lines of the work; give each as <path>:<from>-<to>"
                for line in lines
                if not in_work(line, work)
            ]
    return said


def in_work(line: Any, work: list[str]) -> bool:
    found = LINES.match(line) if isinstance(line, str) else None
    if not found or found.group(1) not in work or not os.path.isfile(found.group(1)):
        return False
    start, end = int(found.group(2)), int(found.group(3) or found.group(2))
    with open(found.group(1), encoding="utf-8") as f:
        count = len(f.read().splitlines())
    return 1 <= start <= end <= count


def question_problems(data: dict[str, Any], shapes: tuple[tuple[str, ...], ...]) -> list[str]:
    said: list[str] = []
    questions = data["questions"]
    waiting = [i.get("question") for i in data["items"] if isinstance(i, dict)]
    for n, question in enumerate(questions, 1):
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
        if isinstance(n, int) and not 1 <= n <= len(questions)
    ]
    return said

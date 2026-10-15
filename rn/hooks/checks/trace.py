"""Every criterion ID the record refers to is one the plan holds, every criterion is served once
tasks are planned, and the verification document keeps the form of checklists/verification.md."""

from __future__ import annotations

import re

from checks import (
    Record,
    criteria,
    front_matter,
    section,
    serves,
    tasks,
    verification_path,
    version,
)

TRACED = (
    "since rn traces each task, scene and question to the criterion it serves by its ID, "
    "as checklists/plan.md gives"
)
WHY = (
    "since rn's checks find each criterion's scene and machine check by the form "
    "of checklists/verification.md"
)
QUESTION = re.compile(r"\d{2}-notes-question\.md")


def check(record: Record) -> list[str]:
    plan = f"{record.session}/steering.md"
    held = criteria(section(record.plan, "# Acceptance criteria"))
    problems = []
    served = set()
    for heading, body in tasks(record.plan):
        named = serves(body)
        served.update(named)
        problems += [
            f"rn: {plan} has `{heading}` serve {given}, a criterion the plan does not hold; "
            f"name only criterion IDs under Acceptance criteria, {TRACED}."
            for given in named
            if given not in held
        ]
    if served:
        problems += [
            f"rn: {plan} has no task that serves {given}; add one, or name it in the Serves "
            f"line of the task that brings it to hold, since a criterion no task serves is "
            f"never built, as checklists/plan.md gives."
            for given in held
            if given not in served
        ]
    for name, text in sorted(record.items.items()):
        named = serves(text.split("\n")[0])
        if QUESTION.fullmatch(name) and (not named or not set(named) <= set(held) | {"goal"}):
            problems.append(
                f"rn: {record.session}/open/{name} does not open with a `Serves:` line naming "
                f"criterion IDs the plan holds, or `goal`; make that its first line, {TRACED}."
            )
    if record.verification is not None:
        problems += verification(record.verification, verification_path(record.plan), record, held)
    return problems


def verification(text: str, path: str, record: Record, held: list[str]) -> list[str]:
    fields = front_matter(text)
    problems = []
    if (
        fields is None
        and version(record.rn) != (0, 9)
        or fields is not None
        and (fields.get("name") != "verification" or "version" not in fields)
    ):
        problems.append(
            f"rn: {path} does not open with front matter giving `name: verification` and "
            f"`version`; add it, {WHY}."
        )
    lines = text.split("\n")
    problems += [
        f"rn: {path} has no `{heading}` heading; add it, {WHY}."
        for heading in ("## Scenes", "## Machine checks")
        if heading not in lines
    ]
    scenes = section(text, "## Scenes")
    headed = re.findall(r"^### ([^:\s]+):", scenes, re.MULTILINE)
    attractive = criteria(section(record.plan, "## Attractive quality"))
    problems += [
        f"rn: {path} has no `### {given}:` heading under `## Scenes`; add the scene for it, {WHY}."
        for given in attractive
        if given not in headed
    ]
    problems += [
        f"rn: {path} has a scene for {given}, a criterion the plan does not hold; head it by a "
        f"criterion ID the plan holds, {TRACED}."
        for given in headed
        if given not in held
    ]
    checked = passes(scenes) + "\n" + section(text, "## Machine checks")
    problems += [
        f"rn: {path} names {given} in no scene's pass and no machine check's criteria; name it "
        f"where it is checked, since a must-be criterion no check covers breaks unseen, as "
        f"checklists/verification.md gives."
        for given in criteria(section(record.plan, "## Must-be quality"))
        if not re.search(rf"\b{given}\b", checked)
    ]
    return problems


def passes(scenes: str) -> str:
    """A pass runs from `Passes when` to the next blank line, so that a criterion named elsewhere in
    a scene, such as in what is put in, is not taken as checked."""
    found, inside = [], False
    for line in scenes.split("\n"):
        inside = line.strip().startswith("Passes when") or inside and line.strip() != ""
        if inside:
            found.append(line)
    return "\n".join(found)

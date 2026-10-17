"""The checks of the record's form.

Each module here holds one check, `check(record)`, which takes the record of a session as values
and returns the sentences of a stop, or an empty list. A check reads no file and runs no command:
`record.py` alone reads the repository, so each check is tested on strings. `FORM` names the checks
of the record's form, which each entry file runs among the checks of its event.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Callable, NamedTuple

TASK = re.compile(r"### \[[ x]\] #(\d+): (\S.*)")


class Record(NamedTuple):
    """A session's record as values, so each check is a function of strings and its tests give it
    strings. The folder is kept so a stop names where, and the `rn` field so the checks tell a
    session an earlier rn started, which `/rn:up` brings to the current form, from one that lost
    its key."""

    folder: str
    plan: str
    open: dict[str, str]
    verification: str | None
    rn: str | None


def run(checks: Iterable[Callable[[Record], list[str]]], record: Record) -> list[str]:
    return [sentence for check in checks for sentence in check(record)]


def older(record: Record) -> bool:
    """Whether an earlier rn started the session, which `/rn:up` brings to the current form."""
    if record.rn is None:
        return True
    version = re.match(r"(\d+)\.(\d+)\.(\d+)", record.rn)
    return version is not None and tuple(int(part) for part in version.groups()) < (0, 9, 0)


def stop(step: str, where: str, broken: str, fix: str, why: str) -> str:
    """One sentence of a stop, naming the part of rn's references/conduct.md it concerns by that
    part's heading, so the conductor goes back to the step itself."""
    return f'rn: in "{step}" of conduct.md, {where} {broken}; {fix}, since {why}.'


def front_matter(text: str) -> dict[str, str] | None:
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if match is None:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def field(plan: str, key: str) -> str | None:
    return (front_matter(plan) or {}).get(key)


def section(text: str, heading: str) -> str:
    """A section holds the headings below its level, as the criteria under `# Acceptance criteria`
    sit beneath `## Attractive quality` and `## Must-be quality`, and the tasks beneath
    `# Tasks`."""
    lines = text.splitlines()
    if heading not in lines:
        return ""
    level = heading.index(" ")
    body = []
    for line in lines[lines.index(heading) + 1 :]:
        found = re.match(r"(#+) ", line)
        if found and len(found.group(1)) <= level:
            break
        body.append(line)
    return "\n".join(body)


def criteria(plan: str, heading: str = "# Acceptance criteria") -> list[str]:
    return re.findall(r"^- ([AM]\d+):", section(plan, heading), re.MULTILINE)


def task_blocks(plan: str) -> list[str]:
    """Each task apart, so a `Serves:` line counts for the task it is written under only."""
    blocks = re.split(r"^(?=### )", section(plan, "# Tasks"), flags=re.MULTILINE)
    return [block for block in blocks if block.startswith("### ")]


# Imported last, since each check takes the parts above from this package.
from . import open_names, steering_form, trace

FORM = (steering_form.check, open_names.check, trace.check)

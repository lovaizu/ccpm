"""The checks of rn's hooks, one to a file.

Each check is a function `check(record)` that takes the session's record as values and returns the
sentences of a stop, or an empty list. It reads no file and runs no command, so that its tests give
it strings; `record.py` alone reads the repository. What more than one check reads the record by is
here, so that each form is read in one place.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from types import MappingProxyType
from typing import NamedTuple


class Record(NamedTuple):
    """The session's record as values; `top` is the repository it was read from, kept so that a
    write can be matched to the record."""

    session: str
    plan: str
    items: Mapping[str, str] = MappingProxyType({})
    verification: str | None = None
    rn: str = ""
    top: str = ""


def front_matter(text: str) -> dict[str, str] | None:
    """None, not an empty dict, for a text without `---` lines at its top, so that a check tells a
    text with no front matter from one missing a key."""
    lines = text.split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        return None
    end = lines.index("---", 1)
    return {
        key.strip(): value.strip()
        for key, _, value in (line.partition(":") for line in lines[1:end])
    }


def version(rn: str) -> tuple[int, int]:
    """A field with no numbers reads as (0, 0), so that a plan without an rn field counts as one
    from before rn 0.9."""
    found = re.match(r"(\d+)\.(\d+)", rn)
    return (int(found[1]), int(found[2])) if found else (0, 0)


def verification_path(plan: str) -> str:
    return (front_matter(plan) or {}).get("verification", "")


def section(text: str, heading: str) -> str:
    """A section ends only at a heading of its level or higher, so that it holds its subsections, as
    `# Acceptance criteria` holds both qualities."""
    lines = text.split("\n")
    if heading not in lines:
        return ""
    start = lines.index(heading) + 1
    level = re.compile(f"#{{1,{heading.index(' ')}}} ")
    end = next((i for i in range(start, len(lines)) if level.match(lines[i])), len(lines))
    return "\n".join(lines[start:end])


def criteria(text: str) -> list[str]:
    """A list, not a set, so that an ID given twice is counted twice."""
    return re.findall(r"^- ([AM]\d+):", text, re.MULTILINE)


def tasks(plan: str) -> list[tuple[str, str]]:
    """Each task keeps the lines under its own heading, so that its `Serves:` line is read from
    those alone."""
    found: list[tuple[str, list[str]]] = []
    for line in section(plan, "# Tasks").split("\n"):
        if line.startswith("### "):
            found.append((line, []))
        elif found:
            found[-1][1].append(line)
    return [(heading, "\n".join(body)) for heading, body in found]


def serves(text: str) -> list[str]:
    found = re.search(r"^Serves:(.*)$", text, re.MULTILINE)
    return re.findall(r"[^,\s]+", found[1]) if found else []

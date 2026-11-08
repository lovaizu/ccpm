"""What a subagent did, as a lane checked at its end holds it: the plugin's folder, the folder it
works in, its calls kept, every one and those of the run it is in, each as it came back, and how the
items of an input are read, by lane's reading or the plugin's adapter, and the run's values its
commands hold; and what its calls kept show,
the lines of a file they read and the files they wrote, each judged by the path the call was given,
named from the folder the subagent works in, each link followed."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any, Callable, NamedTuple

# Each tool that writes a file, with the field of its input that names the file.
WRITERS = {"Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path"}
# The lines a Read gives where its call names no limit, as the Read tool documents it.
READ_LINES = 2000


class Done(NamedTuple):
    """What the subagent did, as an end lane holds it, with the run's values its commands hold as
    parts, by their names."""

    root: str
    cwd: str
    calls: list[dict[str, Any]]
    run: list[dict[str, Any]]
    items: Callable[[str, str], list[str]]
    values: Mapping[str, list[str]] = {}

    def full(self, path: str) -> str:
        """The path named from the folder the subagent works in, each link followed."""
        return os.path.realpath(os.path.join(self.cwd, path))


def under(file: str, place: str) -> bool:
    """Whether the file is the place or lies under it, both full paths."""
    return file == place or file.startswith(place + os.sep)


def written(done: Done, calls: list[dict[str, Any]]) -> list[str]:
    """The file each call of the calls wrote, by Write, Edit or NotebookEdit, in order, a full path
    each."""
    found = []
    for c in calls:
        field = WRITERS.get(c.get("tool", ""))
        path = c.get("input", {}).get(field) if field else None
        if isinstance(path, str):
            found.append(done.full(path))
    return found


def lines_read(done: Done, file: str) -> set[int]:
    """The numbers of the lines of the file, a full path, that the subagent's Read calls covered,
    by their offset and limit, counting from 1."""
    found: set[int] = set()
    for c in done.calls:
        given = c.get("input", {})
        path = given.get("file_path") if c.get("tool") == "Read" else None
        if not isinstance(path, str) or done.full(path) != file:
            continue
        offset, limit = given.get("offset"), given.get("limit")
        first = max(offset, 1) if isinstance(offset, int) else 1
        count = limit if isinstance(limit, int) and limit > 0 else READ_LINES
        found.update(range(first, first + count))
    return found


def text(file: str) -> str | None:
    """The text of the file, a full path; None where it is no file that can be read as text."""
    try:
        with open(file, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None

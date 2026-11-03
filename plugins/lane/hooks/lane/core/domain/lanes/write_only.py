"""write_only: the subagent writes no file but the outputs its step names, such as `CHANGELOG.md`
alone, by the path Write, Edit or NotebookEdit is given; an output may be a folder, under which it
writes anything."""

from __future__ import annotations

import os

ACTION = "write"
CALLS = False
WORDING = "Write only `<output>`."


def allows(path: str, takes: list[str], root: str, cwd: str) -> bool:
    """Whether the file at the path is one of the outputs taken or lies under one, each named from
    the folder the call is made in, as the tools take a path, and each link followed, so a file is
    judged by what it is."""

    def full(named: str) -> str:
        return os.path.realpath(os.path.join(cwd, named))

    file = full(path)
    return any(file == o or file.startswith(o + os.sep) for o in map(full, takes))

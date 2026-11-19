"""Which file of the conversation's folder a call names, as a path from that folder, and whether
the paths of a rule name it: a path that closes with / names a folder, and each file under it."""

from __future__ import annotations

import os
from typing import Any


def of_call(event: dict[str, Any]) -> str:
    """The file that a Write, an Edit, or a Read names.

    Takes: the hook event of the call, whose `tool_input.file_path` names the file.
    Gives: the file's path from the event's `cwd`, each link followed, such as `CHANGELOG.md`, or
    `../CHANGELOG.md` for a file outside it.
    Changes: nothing.
    Refuses: nothing.
    """
    cwd = os.path.realpath(event["cwd"])
    path = os.path.realpath(os.path.join(cwd, event["tool_input"]["file_path"]))
    return os.path.relpath(path, cwd)


def named(paths: list[str], file: str) -> bool:
    """Whether the paths name the file.

    Takes: the paths of a rule, and a file's path from the conversation's folder.
    Gives: True where a path is the file's, or closes with / and the file lies under it, such as
    `docs/changes/` for `docs/changes/1.2.0.md`; False for any other, such as
    `docs/changes-old.md`.
    Changes: nothing.
    Refuses: nothing.
    """
    return any(file == path or (path.endswith("/") and file.startswith(path)) for path in paths)

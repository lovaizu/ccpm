"""Which file or folder of the conversation's folder a call names, as a path from that folder, and
whether the paths of a rule name it or a search in it reaches one: a path that closes with / names a
folder, and each file under it."""

from __future__ import annotations

import os
from typing import Any

# The field of `tool_input` that names the file or the folder of each tool's call, `file_path`
# where the tool isn't named here.
_FIELDS = {"NotebookEdit": "notebook_path", "Grep": "path"}


def of_call(event: dict[str, Any]) -> str:
    """The file that a Write, an Edit, a NotebookEdit, or a Read names, or the folder or file that a
    Grep searches.

    Takes: the hook event of the call, whose `tool_input.file_path` names the file, a
    NotebookEdit's `tool_input.notebook_path`, or a Grep's `tool_input.path`, which a Grep leaves
    out to search the event's `cwd`.
    Gives: the path from the event's `cwd`, each link followed, such as `CHANGELOG.md`, `.` for
    `cwd` itself, or `../CHANGELOG.md` for a file outside it.
    Changes: nothing.
    Refuses: nothing.
    """
    cwd = os.path.realpath(event["cwd"])
    given = event["tool_input"].get(_FIELDS.get(event["tool_name"], "file_path"), ".")
    path = os.path.realpath(os.path.join(cwd, given))
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


def reaches(paths: list[str], searched: str) -> bool:
    """Whether a search in the folder or the file reaches a file that the paths name.

    Takes: the paths of a rule, and the path searched from the conversation's folder, as of_call
    gives it.
    Gives: True where the paths name it, as named says, or where it is a path of the rule or a
    folder that holds one, such as `secrets`, `.`, or `..` for `secrets/`; False for any other,
    such as `secrets-old` or `../secrets`.
    Changes: nothing.
    Refuses: nothing.
    """
    held = (os.path.relpath(path, searched).split(os.sep)[0] != ".." for path in paths)
    return named(paths, searched) or any(held)

"""edit_only: once an output its step names is there, the subagent changes it only with Edit, such
as a design tree whose nesting the subagent must see each time it changes a node: Claude Code lets
an Edit go only after a Read of the file, while a Write puts a whole new text in place of one it
need not have read. A Write makes the output while it is not there, and a NotebookEdit never changes
it. An output may be a folder, under which the lane holds each file alike. A command that writes the
output is stopped already, as a subagent with lanes runs only the commands its lanes name."""

from __future__ import annotations

import os

from lanes import write_only

ACTION = "write"
CALLS = False
WORDING = "Once `<output>` is made, change it only with Edit."


def allows(tool: str, path: str, takes: list[str], root: str, cwd: str) -> bool:
    """Whether the tool's write of the file at the path goes through: the file is none of the
    outputs taken nor under one, as write_only judges a path, or the tool is Edit, or a Write makes
    the file while it is not there."""
    if not write_only.allows(path, takes, root, cwd):
        return True
    if tool == "Edit":
        return True
    return tool == "Write" and not os.path.exists(os.path.join(cwd, path))

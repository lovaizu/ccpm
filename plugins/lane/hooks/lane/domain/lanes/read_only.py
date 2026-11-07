"""read_only: the subagent reads no file but the inputs its step names, by the path Read or Grep is
given; an input may be a folder, under which it reads anything. Laid, the lane lets it read beside
them the form each in_form lane of the subagent names, as its step tells it to write in it."""

from __future__ import annotations

from lanes import write_only

ACTION = "read"
WORDING = "Read only `<input>`."
CALLS = False


def allows(path: str, takes: list[str], root: str, cwd: str) -> bool:
    """Whether the file at the path is one of the inputs taken or lies under one, each named from
    the folder the call is made in, and each link followed."""
    return write_only.allows(path, takes, root, cwd)

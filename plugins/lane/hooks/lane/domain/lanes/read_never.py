"""read_never: the subagent reads none of the files its step names, by the path that Read or Grep
takes; a file named may be a folder, under which it reads nothing. It's read_only's counterpart,
for a file that one role keeps, such as a design tree, which another must not read."""

from __future__ import annotations

from lanes import write_only

ACTION = "read"
WORDING = "Never read `<input>`."
CALLS = False


def allows(path: str, takes: list[str], root: str, cwd: str) -> bool:
    """Whether the file at the path is none of the files taken and lies under none of them, each
    named from the project's folder, the path from the folder the call runs in, and each link
    followed."""
    return not write_only.allows(path, takes, root, cwd)

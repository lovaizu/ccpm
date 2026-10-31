"""A role's wait for a message without ending its turn: a message reaches a subagent only at its
next tool call, and Claude Code refuses a bare `sleep` in the shell, so the role runs this wait in
the foreground, on the files the message follows, which change before it is sent, and calls again
until the message comes."""

from __future__ import annotations

import os
import time

import parts as work_parts

# The longest one wait lasts, in seconds, so the role makes its next tool call, where a message
# reaches it, at least that often; and how often the files are looked at meanwhile.
BOUND = 60
EVERY = 2
# What every wait says beside what it saw, as a change of the files is not the reply: a role that
# took it for one read the work while it was still being mended.
AGAIN = "go on only once the reply has come as a message; until then run this wait again"


def seen(paths: list[str]) -> dict[str, tuple[int, int]]:
    """Each file at the paths, a folder's files at any depth among them, by its path, as when it
    last changed and its size; a path with no file there is left out."""
    found: dict[str, tuple[int, int]] = {}
    for path in work_parts.files(paths):
        try:
            stat = os.stat(path)
        except OSError:
            continue
        found[path] = (stat.st_mtime_ns, stat.st_size)
    return found


def waited(paths: list[str]) -> dict[str, object]:
    """Waits until a file at the paths changes, is made or is removed, looking every EVERY seconds,
    at most BOUND seconds; gives the files changed, in order of their paths, or the seconds waited
    where none did, each with AGAIN."""
    before = seen(paths)
    end = time.monotonic() + BOUND
    while time.monotonic() < end:
        time.sleep(EVERY)
        now = seen(paths)
        changed = sorted(p for p in {*before, *now} if before.get(p) != now.get(p))
        if changed:
            return {"changed": changed, "then": AGAIN}
    return {"waited": BOUND, "then": AGAIN}

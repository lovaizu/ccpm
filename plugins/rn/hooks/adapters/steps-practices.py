"""rn's steps adapter, which Lane's guard runs at its steps port as a role starts: given the start's
values on standard input, as the object `values`, it prints the step lists of the best practice the
start names in `practice`, one list for each practice of the intents `intents` names, every one
where that's null, each step its text and the lane of the trace kind its trace calls for:
run_step for a command run, read_whole for a file read to its end, and write_step for a file made.
A start that names no best practice gets no list. A best practice out of its form ends the adapter
with an error, which Lane names to the role and to its maker."""

from __future__ import annotations

import json
import os
import sys

ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
sys.path.insert(0, os.path.join(ROOT, "domain"))  # pragma: no mutate

import practices


def lists(values: dict[str, list[str] | None]) -> list[dict[str, object]]:
    """The step lists of the best practice the values name, as the module says."""
    named = values.get("practice") or []
    if not named:
        return []
    path = named[0].replace("${CLAUDE_PLUGIN_ROOT}", ROOT)
    return practices.steps(practices.read(path), values.get("intents"))


# Run as the adapter, and not when a test imports it.
if __name__ == "__main__":  # pragma: no mutate
    given = json.load(sys.stdin)
    print(json.dumps({"lists": lists(given["values"])}))

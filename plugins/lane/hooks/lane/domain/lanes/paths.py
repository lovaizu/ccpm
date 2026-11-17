"""How a Lane names paths: `paths`, a list of one string or more, each read from the top of the
worktree that a Call's cwd lies in, with the Start's run values filled in."""

from __future__ import annotations

import os
from collections.abc import Mapping

from form import Lane
from place import Call


def fault(lane: Lane) -> tuple[str, ...]:
    """The fault of a Lane whose `paths` isn't a list of one string or more.

    Takes: a Lane of a type that takes `paths`.
    Gives: the fault, naming the Lane's type; none where `paths` is a list of one string or more.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L->>T: checks each Lane, and makes its sentence`.
    """
    given = lane.args.get("paths")
    if not isinstance(given, list) or not given or not all(isinstance(x, str) for x in given):
        return (f"{lane.type} takes `paths`, a list of one string or more",)
    return ()


def filled(lane: Lane, values: Mapping[str, str]) -> tuple[str, ...]:
    """Each of the Lane's `paths`, with each `{<name>}` that the run values give filled in.

    Takes: a Lane whose `paths` can stand, and the Start's run values, none for the main
    conversation.
    Gives: each path, from the top of the worktree, in the Lane's order.
    Changes: nothing.
    Refuses: nothing.
    Carries: the run values of S5 `G->>T: checks the Call by each Lane of the role, with the
    Start's run values` and of `G->>T: checks the Mark by each Lane on Step n`.
    """
    found = []
    for path in lane.args["paths"]:
        for name, value in values.items():
            path = path.replace(f"{{{name}}}", value)
        found.append(os.path.normpath(path))
    return tuple(found)


def named(call: Call, given: str) -> str:
    """A path that a Call names, from the top of its worktree.

    Takes: the Call, and a path as the Call gives it, absolute or from the Call's cwd.
    Gives: the path from `call.top`, such as `CHANGELOG.md`.
    Changes: nothing.
    Refuses: nothing.
    Carries: S5's reading of each path that a Read, Grep, Glob, or Bash command names.
    """
    return os.path.relpath(os.path.join(call.cwd, given), call.top)

"""Decides what the pruner's result of one unit, `<run>/pruner.json` in the form of
domain/schemas/pruner.schema.json, makes of the design tree's commit: the ground of the commit's
message, from each node the pruner kept, and what the orchestrator tells the user once it's
committed, each point to ask and each step of its own that the pruner changed, a line each."""

from __future__ import annotations

import json
from typing import Any

from fault import Wrong

# The pruner's result, in the form of domain/schemas/pruner.schema.json.
Weighing = dict[str, Any]


def read(path: str) -> Weighing:
    """The pruner's result in the file.

    Takes: the path of a run's `pruner.json`.
    Gives: the result, as the file holds it.
    Changes: nothing.
    Refuses: Wrong where no file lies there, saying that the pruner writes it before the commit, or
    where it isn't JSON.
    """
    try:
        with open(path, encoding="utf-8") as file:
            weighing = json.load(file)
    except FileNotFoundError:
        raise Wrong(
            f"{path}: no pruner's result lies there; the pruner writes it as it ends, and the"
            " tree is committed after it"
        ) from None
    except ValueError as error:
        raise Wrong(f"{path}: isn't JSON: {error}; write it as JSON") from None
    return weighing


def ground(weighing: Weighing, name: str, signed: bool) -> str:
    """The message of the design tree's commit after the pruner's weighing.

    Takes: the pruner's result, the run's name, and whether the commit signs off the plan.
    Gives: `rn: the design tree of <name>, weighed`, then, after a blank line, `- <node>` for each
    node of `kept` in its order, a line each, and last `The plan is signed off.` where `signed`;
    the first line alone where neither holds anything.
    Changes: nothing.
    Refuses: nothing.
    """
    body = [f"- {each}" for each in weighing["kept"]]
    if signed:
        body.append("The plan is signed off.")
    head = f"rn: the design tree of {name}, weighed"
    return "\n\n".join([head, "\n".join(body)]) if body else head


def told(weighing: Weighing) -> list[str]:
    """What the orchestrator tells the user of the pruner's weighing.

    Takes: the pruner's result.
    Gives: `ask\\t<deliverable>\\t<condition>\\t<about>\\t<question>` for each of `ask`, then
    `changed\\t<entry>` for each of `changed`, each in its order; none where both are empty.
    Changes: nothing.
    Refuses: nothing.
    """
    asks = [
        "\t".join(["ask", each["deliverable"], each["condition"], each["about"], each["question"]])
        for each in weighing["ask"]
    ]
    return asks + [f"changed\t{each}" for each in weighing["changed"]]

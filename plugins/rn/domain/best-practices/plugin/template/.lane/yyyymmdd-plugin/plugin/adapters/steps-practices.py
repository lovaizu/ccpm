"""<plugin>'s steps adapter, which Lane's guard runs as a role starts: given the start's values on
standard input, as `{"values": {...}}`, it prints `{"lists": [...]}`, one step list for each
practice that the role carries out, each step what it says and the lane that its trace calls for.

DELETE_TEMPLATE_COMMENT: the adapter that gives Lane the practices of a role's best practice as
its steps, as Q9 says. practice, intents: the run values of the role's in schema that name its best
practice and the intents it carries out, each a list, or null for every intent. Each list holds
the practice's intent as `list`, and each step as `says`, with run_step for a command run,
read_whole for a file read to its end, write_step for a file made, and no lane where the step has
no trace. Beside it, steps-practices.json holds its cases, a list of {"given", "gives"}: one for
each form the values take and one that gives nothing, which lay.py print runs before it prints the
proposal. The guard runs it with CLAUDE_PLUGIN_ROOT set to the plugin's folder. It needs only
Python 3.9 and the standard library."""

from __future__ import annotations

import json
import os
import sys

ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
# The lane of the trace kind that each action of a trace calls for.
LANES = {"run": "run_step", "read": "read_whole", "write": "write_step"}


def lists(values: dict[str, list[str] | None]) -> list[dict[str, object]]:
    """The step lists of the best practice the values name, as the module says."""
    named = values.get("practice") or []
    if not named:
        return []
    with open(named[0].replace("${CLAUDE_PLUGIN_ROOT}", ROOT), encoding="utf-8") as f:
        practices = json.load(f)["practices"]
    wanted = values.get("intents")
    return [
        {
            "list": p["intent"],
            "steps": [
                {
                    "says": s["text"],
                    "lanes": [{"lane": LANES[s["trace"]["action"]], "takes": s["trace"]["takes"]}]
                    if "trace" in s
                    else [],
                }
                for s in p["steps"]
            ],
        }
        for p in practices
        if wanted is None or p["intent"] in wanted
    ]


# Run as the adapter, and not when a test imports it.
if __name__ == "__main__":
    given = json.load(sys.stdin)
    print(json.dumps({"lists": lists(given["values"])}))

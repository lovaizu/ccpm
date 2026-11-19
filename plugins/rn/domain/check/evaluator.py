"""Decides when an evaluator's result holds: its form, and each condition of its group answered
once, good with the lines that meet it or more with what its people get once it's good."""

from __future__ import annotations

import os
from collections import Counter
from collections.abc import Sequence

from fault import Wrong
from schemas import form


def faults(run: str, cut: str, plugin: str) -> Sequence[str]:
    """Each fault of an evaluator's result beside its Cut.

    Takes: the run's folder, the path of the Cut from the top of the worktree, and rn's folder.
    Gives: one line for each fault: the result missing or out of
    `schemas/evaluator.schema.json`, or a condition of the Cut's group answered twice or not at all,
    or one outside the group answered; none where the result holds.
    Refuses: Wrong, naming the file, where the Cut isn't there or isn't in its form."""
    schemas = os.path.join(plugin, "domain", "schemas")
    top = os.path.dirname(os.path.dirname(run))
    held = form.read(os.path.join(top, cut), os.path.join(schemas, "cut.schema.json"), cut)
    result = cut.removesuffix(".cut.json") + ".json"
    try:
        judged = form.read(
            os.path.join(top, result), os.path.join(schemas, "evaluator.schema.json"), result
        )
    except Wrong as wrong:
        return [f"{wrong}; write your answers there in their form before you end"]
    group = held["conditions"]
    count = Counter(a["condition"] for a in [*judged["good"], *judged["more"]])
    return [
        *(
            f"{cut}: {c} of {held['group']} isn't answered good or more"
            for c in group
            if not count[c]
        ),
        *(f"{cut}: {c} is answered {n} times; answer it once" for c, n in count.items() if n > 1),
        *(f"{cut}: {c} isn't of {held['group']}, which you judge" for c in count if c not in group),
    ]

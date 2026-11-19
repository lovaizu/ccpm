"""Decides when a generator's result holds: its form, each decision of its Cut named where it's
carried out, and its document held to its kind's template, so that a Round rests only on a
deliverable made from its Cut."""

from __future__ import annotations

import os
from collections.abc import Sequence

from fault import Wrong
from schemas import form
from template import command


def faults(run: str, cut: str, plugin: str, top: str) -> Sequence[str]:
    """Each fault of the generator's result beside its Cut.

    Takes: the run's folder, the path of the Cut from the top of the worktree, rn's folder, and
    the top of the worktree, where the deliverable lies.
    Gives: one line for each fault: the result missing or out of
    `schemas/generator.schema.json`, a point with no text, no deliverable at its path, a decision
    of the Cut that holds an answer and that the result names nowhere, or, where
    the deliverable is a Markdown document whose kind has a template, what template.py says of it;
    none where the result holds.
    Refuses: Wrong, naming the file, where the Cut isn't there or isn't in its form."""
    schemas = os.path.join(plugin, "domain", "schemas")
    held = form.read(os.path.join(top, cut), os.path.join(schemas, "cut.schema.json"), cut)
    result = cut.removesuffix(".cut.json") + ".json"
    try:
        made = form.read(
            os.path.join(top, result), os.path.join(schemas, "generator.schema.json"), result
        )
    except Wrong as wrong:
        return [f"{wrong}; write your result there in its form before you end"]
    if made["result"] != "made":
        if made.get("point", "").strip():
            return []
        return [f"{result}: the point has no text; write it, your recommendation, and its ground"]
    deliverable = held["deliverable"]
    if not os.path.exists(os.path.join(top, deliverable["path"])):
        return [f"{cut}: nothing is at {deliverable['path']}; make the deliverable there"]
    named = {(d["path"], d["condition"], d["about"]) for d in made.get("carried_out", [])}
    found = [
        f"{cut}: the result names nowhere that it carries out {d['about']}"
        f" ({d['path']} {d['condition']}); add where to carried_out"
        for d in held.get("decisions", [])
        if d["decided"] is not None and (d["path"], d["condition"], d["about"]) not in named
    ]
    template = os.path.join(plugin, "domain", "best-practices", deliverable["kind"], "template.md")
    if deliverable["path"].endswith(".md") and os.path.isfile(template):
        code, _, said = command.main([deliverable["kind"], deliverable["path"]], top, plugin)
        found += [said.rstrip("\n")] if code else []
    return found

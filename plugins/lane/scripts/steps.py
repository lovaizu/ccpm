"""Each step of a subagent as lay.py writes it: the sentence of each lane laid there before that
the proposal no longer lays there taken out, in whichever wording lane laid it, a sentence said in
a wording lane laid before put in the current one where it is, each lane's sentence it does not say
put at the end of the step, the rest of the step as it was; and which steps lay.py writes."""

from __future__ import annotations

from typing import Any

import lanes
import step


def sentences(given: dict[str, Any]) -> list[str]:
    """The sentence of each lane on the step."""
    return [lanes.sentence(lane["lane"], lane["takes"]) for lane in given["lanes"]]


def reworded(lines: list[str], given: dict[str, Any]) -> list[str]:
    """The step's lines with each sentence of its lanes that it says in a wording lane laid before,
    and not in the current one, put in the current one where it is, the rest as it was; a wording
    lane never laid is the developer AI's own, and is left as it is."""
    start, end = given["span"]
    kept = list(lines[start:end])
    for lane in given["lanes"]:
        now = lanes.sentence(lane["lane"], lane["takes"])
        if now in step.says([line.rstrip("\n") for line in kept], (0, len(kept))):
            continue
        # An earlier wording may begin a later one, so the longest is looked for first, and once
        # one is put in the current one, no other is.
        for said in sorted(lanes.earlier(lane["lane"], lane["takes"]), key=len, reverse=True):
            if any(" " + said in line for line in kept):
                kept = [line.replace(" " + said, " " + now) for line in kept]
                break
    return kept


def read_as_laid(lines: list[str], given: dict[str, Any]) -> list[str]:
    """The step's lines as they will read: each sentence gone from it taken out, as lay.py put it
    in, after a blank, each sentence of its lanes said in a wording laid before put in the current
    one, and each it does not yet say put at its end."""
    kept = []
    for line in reworded(lines, given):
        for said in given["gone"]:
            line = line.replace(" " + said, "")
        kept.append(line)
    text = step.says([line.rstrip("\n") for line in kept], (0, len(kept)))
    added = [s for s in sentences(given) if s not in text]
    last = kept[-1].rstrip("\n")
    return [*kept[:-1], " ".join([last, *added]) + "\n"]


def steps_laid(
    before: dict[str, list[dict[str, Any]]], agent: dict[str, Any]
) -> list[dict[str, Any]]:
    """Each step lay.py writes in the subagent as the proposal gives it, with the lanes laid before
    in each subagent, by its name, as hooks/lanes.json holds them: the proposal's steps, then each
    other step that a sentence laid before is gone from, with no lanes, where the subagent's file
    still has it; each with where it is and the sentences gone from it, each in its current wording
    and then in each lane laid before."""
    now = {s["step"]: sentences(s) for s in agent["steps"]}
    gone: dict[int, list[str]] = {}
    for s in before.get(agent["name"], []):
        kept = now.get(s["step"], [])
        out = gone.setdefault(s["step"], [])
        for lane in s["lanes"]:
            said = lanes.sentence(lane["lane"], lane["takes"])
            # The current wording first, as an earlier one may begin it.
            if said not in kept:
                out += [said, *lanes.earlier(lane["lane"], lane["takes"])]
    lines = [line.rstrip("\n") for line in agent["lines"]]
    spans = {n: step.span(lines, n) for n in sorted(gone) if n not in now}
    rest: list[dict[str, Any]] = [
        {"step": n, "lanes": [], "span": at} for n, at in spans.items() if at is not None
    ]
    return [{**s, "gone": gone.get(s["step"], [])} for s in [*agent["steps"], *rest]]

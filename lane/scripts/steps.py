"""Each step of a subagent as the layer writes it: the sentence of each lane its hook held before that
the proposal no longer lays there taken out, each lane's sentence put at the end of the step, the
rest of the step as it was; and the print of each step for the building AI's OK."""

from __future__ import annotations

from typing import Any

import entries
import lanes
import step


def sentences(step_given: dict[str, Any]) -> list[str]:
    """The sentence of each lane on the step."""
    return [lanes.sentence(lane["lane"], lane["takes"]) for lane in step_given["lanes"]]


def read_as_laid(lines: list[str], step_given: dict[str, Any]) -> list[str]:
    """The step's lines as they would read with each sentence gone from it taken out, as the layer
    put it in, after a blank, and each sentence of its lanes it does not yet say put at its end."""
    start, end = step_given["span"]
    kept = []
    for line in lines[start:end]:
        for said in step_given["gone"]:
            line = line.replace(" " + said, "")
        kept.append(line)
    text = step.says([line.rstrip("\n") for line in kept], (0, len(kept)))
    added = [s for s in sentences(step_given) if s not in text]
    last = kept[-1].rstrip("\n")
    return [*kept[:-1], " ".join([last, *added]) + "\n"]


def steps_laid(hooks: dict[str, Any], plugin: str, agent: dict[str, Any]) -> list[dict[str, Any]]:
    """Each step the layer writes in the subagent, with its lanes, where it is and the sentences
    gone from it: the sentence of each lane the subagent's hook held before on the step, as lane:up
    wrote it, that the proposal no longer lays there. They are the proposal's steps, then each other
    step any sentence is gone from, with no lanes, in order, where the Steps still have it."""
    before = entries.laid_before(hooks)[0].get(f"{plugin}:{agent['name']}", [])
    now = {s["step"]: sentences(s) for s in agent["steps"]}
    gone: dict[int, list[str]] = {}
    for s in before:
        kept = now.get(s["step"], [])
        gone.setdefault(s["step"], []).extend(t for t in sentences(s) if t not in kept)
    lines = [line.rstrip("\n") for line in agent["lines"]]
    spans = {n: step.span(lines, n) for n in sorted(gone) if n not in now}
    rest: list[dict[str, Any]] = [
        {"step": n, "lanes": [], "span": at} for n, at in spans.items() if at is not None
    ]
    return [{**s, "gone": gone.get(s["step"], [])} for s in [*agent["steps"], *rest]]


def listed(name: str, step_given: dict[str, Any]) -> list[str]:
    """The lines heading the step in the print: the step, and each of its lanes under its action
    with its hook, lined up; for a step with no lanes, that their sentences are taken out."""
    number, said = step_given["step"], sentences(step_given)
    if not said:
        return [f"No lanes on step {number} of {name} now, their sentences taken out:\n"]
    out = [f"Lanes on step {number} of {name}, each hook acting in {name} alone:\n"]
    actions = [lanes.LANES[lane["lane"]].ACTION + ":" for lane in step_given["lanes"]]
    wide, long = max(map(len, actions)), max(map(len, said))
    for action, sentence, lane in zip(actions, said, step_given["lanes"]):
        hook = f"hook {lane['lane']}{held(lane)}"
        out.append(f"  {action:<{wide}} {sentence:<{long}}  {hook}\n")
    return out


def held(lane: dict[str, Any]) -> str:
    """What the lane's hook holds beyond what its sentence shows, as the building AI reads it after the
    hook, such as the commands wait_for holds back; "" for a lane whose sentence shows all."""
    shown = lanes.shown(lane["lane"])
    rest = [f"`{t}`" for t in lane["takes"][shown:]] if shown is not None else []
    return f", holding back {', '.join(rest)}" if rest else ""

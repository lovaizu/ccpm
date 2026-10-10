"""The record turn returns keeps the form the calling plugin reads it by: every line handed in, each
kind under its part, each difference with how it ended, and one `next` that agrees with them."""
import re

import ccs

PART = {"work": "focal_entities", "receiver": "focal_entities", "acceptance": "goal_orientation",
        "use": "goal_orientation", "difference": "goal_orientation", "language": "constraints",
        "rule": "constraints", "answer": "constraints", "source": "retrieved_artifacts",
        "gap": "uncertainty_signal", "process": "semantic_gist", "next": "predictive_cue"}
NEXT = re.compile(r"^(done|ask the user|to the caller: .+|stopped: .+)$", re.S)
ENDING = re.compile(r"→ (fixed|let go: .+|to the caller: .+)$", re.S)


def check(handed, parts):
    problems = []
    lines = [(p, k, v) for p, items in parts for k, v in items]
    for p, items in handed:
        for k, v in items:
            if p != "episodic_trace" and (p, k, v) not in lines:
                problems.append(f"`{p}` lost `{k}: {v}` from the record handed in; keep every line")
    for p, k, v in lines:
        if PART.get(k, p) != p:
            problems.append(f"`{k}` is under `{p}`; it belongs under `{PART[k]}`")
        if k == "difference" and not ENDING.search(v):
            problems.append(f"difference `{v}` must end with `→ fixed`, `→ let go: <why>` or "
                            "`→ to the caller: <why>`; a use with no difference is not one")
    nexts = ccs.values(parts, "predictive_cue", "next")
    if len(nexts) != 1 or not NEXT.match(nexts[0]):
        return problems + ["`next` must be one line: `done`, `ask the user`, "
                           "`to the caller: <why>` or `stopped: <where>`"]
    nxt = nexts[0]
    if ccs.values(parts, "uncertainty_signal", "gap") and nxt != "ask the user":
        problems.append("a `gap` is returned, so `next` is `ask the user`")
    if nxt == "done" and any("→ to the caller:" in v for v in ccs.values(parts, "goal_orientation",
                                                                        "difference")):
        problems.append("a difference goes to the caller, so `next` is `to the caller: <why>`")
    return problems

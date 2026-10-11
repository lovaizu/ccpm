"""Keep each agent running until it has read whole, with Read, every file it decides from.

Asked in words, reading is met by skimming; the record shows which lines each Read showed.
"""
import os
import re

import steps
from turn_state import files

SHOWN = re.compile(r"^\s*(\d+)\t", re.M)


def required(role, t):
    work, n = t["work"], t["round"]
    in_work = lambda *names: [os.path.join(work, x) for x in names]  # noqa: E731
    should = in_work("should.md") + t["viewpoints"]
    seen = in_work(f"first-user-{n}.md", f"steps-generator-{n}.md", f"steps-first-user-{n}.md")
    if role == "generator":
        paths = should + t["sources"] + in_work(f"remake-{n}.md")
    elif role == "learner":
        paths = should + seen
    elif role == "evaluator":
        paths = (should + files(os.path.join(t["repo"], t["deliverable"])) + seen + in_work(f"learner-{n}.json")
                 + (files(os.path.join(work, f"version-{n - 1}")) if n > 1 else []))
    else:
        paths = []
    return [p for p in paths if os.path.isfile(p)]


def shown(transcript):
    """The line numbers each file's successful Reads showed, by real path."""
    seen = {}
    if not os.path.isfile(transcript):
        return seen
    for c, r in steps.pairs(transcript):
        if c["name"] == "Read" and r and not r.get("is_error"):
            lines = seen.setdefault(os.path.realpath(c.get("input", {}).get("file_path", "")), set())
            lines.update(int(m) for m in SHOWN.findall(steps.text(r.get("content"))))
    return seen


def spans(numbers):
    out, run = [], []
    for k in numbers:
        if run and k == run[-1] + 1:
            run.append(k)
        else:
            run = [k]
            out.append(run)
    return ", ".join(f"{r[0]}-{r[-1]}" if len(r) > 1 else str(r[0]) for r in out)


def check(data, t):
    seen = shown(data["agent_transcript_path"])
    unread = []
    for path in required(data["agent_type"].split(":", 1)[1], t):
        with open(path, encoding="utf-8", errors="replace") as f:
            total = len(f.read().splitlines())
        got = seen.get(os.path.realpath(path))
        missing = [k for k in range(1, total + 1) if k not in (got or ())]
        if got is None:
            unread.append(f"{path} (not read)")
        elif missing:
            unread.append(f"{path} (lines {spans(missing)} not read)")
    if not unread:
        return []
    return ["Read these whole with the Read tool before you do anything else: " + "; ".join(unread)]

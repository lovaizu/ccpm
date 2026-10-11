"""Keep each agent running until it has read whole, with Read, every file it decides from.

Asked in words, reading is met by skimming; the record shows which lines each Read showed.
"""
import json
import os
import re

from turn_state import files

SHOWN = re.compile(r"^\s*(\d+)\t", re.M)


def required(role, t):
    work, n = t["work"], t["round"]
    in_work = lambda *names: [os.path.join(work, x) for x in names]  # noqa: E731
    earlier = in_work(*[f"evaluator-{k}.json" for k in range(1, n)])
    steps = in_work(f"steps-generator-{n}.md", f"steps-first-user-{n}.md")
    if role == "generator":
        paths = in_work("should.md") + t["viewpoints"] + t["sources"] + earlier
    elif role == "learner":
        paths = in_work(f"first-user-{n}.md") + steps + t["viewpoints"]
    elif role == "evaluator":
        paths = (in_work("should.md") + t["viewpoints"] + files(os.path.join(t["repo"], t["deliverable"]))
                 + in_work(f"first-user-{n}.md") + steps + in_work(f"learner-{n}.json") + earlier)
    else:
        paths = []
    return [p for p in paths if os.path.isfile(p)]


def shown(transcript):
    """The line numbers each file's successful Reads showed, by real path."""
    calls, seen = {}, {}
    with open(transcript, encoding="utf-8") as f:
        for line in f:
            content = json.loads(line).get("message", {}).get("content")
            for c in content if isinstance(content, list) else []:
                if c.get("type") == "tool_use" and c.get("name") == "Read":
                    calls[c.get("id")] = os.path.realpath(c.get("input", {}).get("file_path", ""))
                elif c.get("type") == "tool_result" and c.get("tool_use_id") in calls and not c.get("is_error"):
                    body = c.get("content")
                    text = body if isinstance(body, str) else "\n".join(x.get("text", "") for x in body or [])
                    lines = seen.setdefault(calls[c["tool_use_id"]], set())
                    lines.update(int(m) for m in SHOWN.findall(text))
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
    return ["Read these whole with the Read tool before you finish: " + "; ".join(unread)]

"""A run kept where its result goes: while it runs, what the hooks and the next step read; once it
returns, the result in the form the caller reads."""

from __future__ import annotations

import json
import os
from typing import Any

import call
import forms


def start(text: str) -> str:
    """Starts the run the call asks for, and gives the prompt the generator is started with."""
    run = call.check(call.parse(text))
    return keep(run, [])


def keep(run: dict[str, Any], sent_back: list) -> str:
    """Keeps the run with the generator's next prompt, and gives that prompt."""
    result = run["call"]["result"]
    run["prompt"] = json.dumps(
        {"run": result, "ccs": run["call"]["ccs"], "work": run["work"], "sent_back": sent_back}
    )
    write(result, {"running": run})
    return run["prompt"]


def read(result: str, text: str) -> dict[str, str]:
    """Records the orchestrator's reading: the items it sends back go to the generator again;
    with none, the result is written and the run returns."""
    run = running(result)
    if run is None:
        raise call.Stop(
            f"turn: no run is going with its result at {result}; start one with"
            " `turn.py start '<call JSON>'`"
        )
    said = forms.check(text, run, forms.READING)
    if said:
        raise call.Stop("turn: the reading is not filled:\n" + "\n".join(said))
    reading = json.loads(text)
    sent_back = [i for i in reading["items"] if "gets" in i]
    if sent_back:
        return {"prompt": keep(run, sent_back)}
    questions = [
        dict(
            q, items=[{"checklist": i["checklist"], "item": i["item"]} for i in waiting(reading, n)]
        )
        for n, q in enumerate(reading["questions"], 1)
    ]
    write(
        result,
        {
            "work": run["work"],
            "items": [i for i in reading["items"] if "good" in i],
            "questions": questions,
            "not_good": [],
        },
    )
    return {"returned": result}


def waiting(reading: dict[str, Any], n: int) -> list:
    return [i for i in reading["items"] if i.get("question") == n]


def running(result: str) -> dict[str, Any] | None:
    """The run going with its result at the path, or None when none is."""
    try:
        with open(result, encoding="utf-8") as f:
            kept = json.load(f)
    except (OSError, ValueError):
        return None
    return kept.get("running") if isinstance(kept, dict) else None


def write(path: str, data: dict[str, Any]) -> None:
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")

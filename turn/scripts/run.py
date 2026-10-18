"""A run kept where its result goes: while it runs, what the hooks and the next step read; once it
returns, the result in the form the caller reads."""

from __future__ import annotations

import json
import os
from typing import Any

import call
import forms

GENERATOR = "turn:generator"
FIRST_USER = "turn:first-user"
EVALUATOR = "turn:evaluator"
LEARNER = "turn:learner"


def start(text: str) -> dict[str, Any]:
    """Starts the run the call asks for, and gives the items the orchestrator checks can get their
    Good before any work is made."""
    run = call.check(call.parse(text))
    run["check"] = True
    write(run["call"]["result"], {"running": run})
    return {"check": run["items"]}


def generator_given(run: dict[str, Any], sent_back: list) -> dict[str, Any]:
    return {
        "ccs": run["call"]["ccs"],
        "work": run["work"],
        "sent_back": sent_back,
        "learnt": run.get("learnt", []),
    }


def reader_given(run: dict[str, Any]) -> dict[str, Any]:
    """What the first user and the evaluator are given: what the receiver has, and the
    checklists."""
    return {
        "work": run["work"],
        "opens": run["opens"],
        "receiver": run["receiver"],
        "use": run["use"],
        "checklists": run["checklist"],
    }


def ask(run: dict[str, Any], agent: str, given: dict[str, Any]) -> dict[str, str]:
    """Keeps the run with the agent to start next and what it is given, and gives the agent and
    its prompt. The prompt names the run alone, and the agent takes what it is given from the
    script, so no AI copies it."""
    prompt = json.dumps({"run": run["call"]["result"]}, ensure_ascii=False)
    run["next"] = {"agent": agent, "prompt": prompt, "given": given}
    write(run["call"]["result"], {"running": run})
    return {"agent": agent, "prompt": prompt}


def given(result: str) -> dict[str, Any]:
    """What the agent started last in the run is given."""
    run = running(result)
    if run is None:
        raise call.Stop(f"turn: no run is going with its result at {result}")
    if "check" in run:
        raise call.Stop("turn: no role is started before the orchestrator's check is given")
    return run["next"]["given"]


def next_step(result: str, text: str) -> dict[str, Any]:
    """Takes what the run waits on, the orchestrator's reading or decision or a role's kept reply,
    and gives what the orchestrator does next."""
    run = running(result)
    if run is None:
        raise call.Stop(
            f"turn: no run is going with its result at {result}; start one with"
            " `turn.py start '<call JSON>'`"
        )
    if "check" in run:
        # Asked with no check, the items to check are shown again.
        return checked(run, text) if text.strip() else {"check": run["items"]}
    # Each role's record is kept for the learner, which looks for what makes the Good in what the
    # roles did.
    record = run["next"].get("record")
    if record and record not in run.setdefault("records", []):
        run["records"].append(record)
    if "decide" in run:
        # Asked with no decision, the items to decide are shown again, so the orchestrator can
        # always see them whole.
        return decide(run, text) if text.strip() else {"decide": run["decide"]}
    agent = run["next"]["agent"]
    if agent == GENERATOR:
        return reading(run, text)
    reply = run["next"].get("reply")
    if reply is None:
        raise call.Stop(
            f"turn: {agent} has not replied; start {agent} with the prompt turn.py printed last,"
            " and wait for its reply"
        )
    if agent == FIRST_USER:
        run["read"] = reply["items"]
        return ask(run, EVALUATOR, dict(reader_given(run), reading=reply["items"]))
    if agent == LEARNER:
        run["learnt"] = reply["items"]
        return ask(run, GENERATOR, generator_given(run, run.pop("unmet")))
    return compare(run, reply["items"])


def checked(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the orchestrator's check: with an item the CCS cannot give its Good, the run returns
    the questions alone, as no work made without the answer can give it; otherwise the generator
    makes the work."""
    said = forms.check(text, run["items"], run["work"], forms.CHECK)
    if said:
        raise call.Stop("turn: the check is not filled:\n" + "\n".join(said))
    found = json.loads(forms.unfenced(text))
    del run["check"]
    asked = waited(found["items"], found["questions"])
    if asked:
        write(run["call"]["result"], {"questions": asked})
        return {"returned": run["call"]["result"]}
    return ask(run, GENERATOR, generator_given(run, []))


def reading(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the orchestrator's reading: the items it sends back go to the generator again;
    with none, the reading is kept as its findings and the first user reads the work."""
    said = forms.check(text, run["items"], run["work"], forms.READING)
    if said:
        raise call.Stop("turn: the reading is not filled:\n" + "\n".join(said))
    found = json.loads(forms.unfenced(text))
    sent_back = [i for i in found["items"] if "gets" in i]
    if sent_back:
        return ask(run, GENERATOR, generator_given(run, sent_back))
    run["findings"] = found
    return ask(run, FIRST_USER, reader_given(run))


def compare(run: dict[str, Any], goods: list[dict[str, Any]]) -> dict[str, Any]:
    """Sets the orchestrator's findings beside the evaluator's Goods: where they agree, the run
    returns; where they differ, the orchestrator decides those items."""
    evaluated = {key(i): judged(i) for i in goods}
    read = {key(i): judged(i) for i in run["read"]}
    findings = run["findings"]
    apart = [
        dict(
            named(f),
            orchestrator=judged(f),
            evaluator=evaluated.get(key(f)),
            first_user=read.get(key(f)),
        )
        for f in findings["items"]
        if ("good" in f) != (key(f) in evaluated)
    ]
    if not apart:
        return settle(run, findings["items"], findings["questions"])
    run["decide"] = {"items": apart, "questions": findings["questions"]}
    write(run["call"]["result"], {"running": run})
    return {"decide": run["decide"]}


def decide(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the orchestrator's decision on the items judged apart, and returns the run."""
    asked = run["decide"]["questions"]
    said = forms.check(text, run["decide"]["items"], run["work"], forms.READING, len(asked))
    if said:
        raise call.Stop("turn: the decision is not filled:\n" + "\n".join(said))
    decision = json.loads(forms.unfenced(text))
    # The calling AI is to get each Good found by a reader that did not make the work, so an item
    # neither the first user nor the evaluator found Good gets none from the orchestrator alone.
    unread = [
        f"{i['checklist']} {i['item']} has no Good a reader found; give what the receiver gets"
        " once it has it"
        for i in run["decide"]["items"]
        if not (i["evaluator"] or i["first_user"])
        for d in decision["items"]
        if key(d) == key(i) and "good" in d
    ]
    if unread:
        raise call.Stop("turn: the decision is not filled:\n" + "\n".join(unread))
    decided = {key(i): i for i in decision["items"]}
    items = [decided.get(key(f), f) for f in run["findings"]["items"]]
    del run["decide"]
    return settle(run, items, asked + decision["questions"])


def settle(run: dict[str, Any], items: list[dict[str, Any]], questions: list) -> dict[str, str]:
    """After the first reading, an item without Good has the learner find what makes the Good, for
    the work to be made again; otherwise the run returns. The result holds each item's Good, each
    question an item still waits on with the items it settles, and each item without Good with
    what the receiver gets once it has it."""
    unmet = [i for i in items if "gets" in i]
    if unmet and "learnt" not in run:
        run["unmet"] = unmet
        # An item waiting on a question gets its Good from the user's answer, not from the work.
        run["learning"] = [named(i) for i in items if "question" not in i]
        learner = {"findings": items, "records": run["records"]}
        return ask(run, LEARNER, learner)
    result = run["call"]["result"]
    write(
        result,
        {
            "work": run["work"],
            "items": [i for i in items if "good" in i],
            "questions": waited(items, questions),
            "not_good": unmet,
        },
    )
    return {"returned": result}


def waited(items: list[dict[str, Any]], questions: list) -> list[dict[str, Any]]:
    """Each question an item waits on, with the items it settles."""
    return [
        dict(q, items=[named(i) for i in waiting])
        for n, q in enumerate(questions, 1)
        for waiting in [[i for i in items if i.get("question") == n]]
        if waiting
    ]


def named(item: dict[str, Any]) -> dict[str, str]:
    """The checklist and ID that name an item."""
    return {"checklist": item["checklist"], "item": item["item"]}


def key(item: dict[str, Any]) -> tuple[str, str]:
    return (item["checklist"], item["item"])


def judged(item: dict[str, Any]) -> dict[str, Any]:
    """An item's judgment without the checklist and ID that name it."""
    return {k: v for k, v in item.items() if k not in ("checklist", "item")}


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

"""A run kept where its result goes: while it runs, what the hooks and the next step read; once it
returns, the result in the form the caller reads."""

from __future__ import annotations

import json
import os
import time
from typing import IO, Any

import call
import forms
import records

GENERATOR = "turn:generator"
FIRST_USER = "turn:first-user"
EVALUATOR = "turn:evaluator"
LEARNER = "turn:learner"
# The roles kept started until the first user's reading of their round ends, each sent what comes
# next by message, so each works on with what it has already read.
KEPT = (GENERATOR, FIRST_USER)
# A reading that does not settle is bounded: each kind of send-back three times a round.
SENDS = 3
# A messaged role's reply is waited for a second at a time, within the shell's two minutes.
WAIT = 100
USAGE = (
    "usage: turn.py start '<call JSON>'\n"
    "       turn.py next <result> [< <your reading or decision as JSON>]\n"
    "       turn.py given <result>\n"
    "       turn.py parts <result>\n"
    "       turn.py record <result> <record number> <page>"
)


def main(argv: list[str], stdin: IO[str]) -> int:
    """What turn.py runs: the call checked and the run started, each step's outcome taken, giving
    the agent to start next, the items to decide, or the result written; what each role is given,
    the parts of the work, and each record for the learner. Prints what comes next as JSON and gives 0, or prints what
    was wrong and gives 1."""
    try:
        if argv[:1] == ["start"] and len(argv) == 2:
            print(json.dumps(start(argv[1]), ensure_ascii=False))
        elif argv[:1] == ["next"] and len(argv) == 2:
            print(json.dumps(next_step(argv[1], stdin.read()), ensure_ascii=False))
        elif argv[:1] == ["given"] and len(argv) == 2:
            print(json.dumps(given(argv[1]), ensure_ascii=False))
        elif argv[:1] == ["parts"] and len(argv) == 2:
            print(json.dumps(parts(argv[1]), ensure_ascii=False))
        elif argv[:1] == ["record"] and len(argv) == 4:
            print(record(argv[1], argv[2], argv[3]))
        else:
            print(USAGE)
            return 1
    except call.Stop as stop:
        print(stop)
        return 1
    return 0


def start(text: str) -> dict[str, Any]:
    """Starts the run the call asks for, and gives the items the orchestrator checks can get their
    Good before any work is made."""
    run = call.check(call.parse(text))
    # The run waits on the orchestrator's check of these items.
    run["check"] = run["items"]
    write(run["call"]["result"], {"running": run})
    return {"check": run["check"]}


def generator_given(run: dict[str, Any], sent_back: list, unsourced: list) -> dict[str, Any]:
    return {
        "ccs": run["call"]["ccs"],
        "work": run["work"],
        "sent_back": sent_back,
        "unsourced": unsourced,
        "lessons": lessons(run, "generator"),
    }


def lessons(run: dict[str, Any], role: str) -> list[str]:
    """The lessons on how the run went that the orchestrator took for the role."""
    return [t["lesson"] for t in run.get("lessons", []) if t["role"] == role]


def sources(run: dict[str, Any]) -> tuple[str, ...]:
    """What a statement of the work may rest on: the CCS and the files and folders it names."""
    return tuple(p for p in run["given"] if p not in run["work"])


def each(run: dict[str, Any]) -> list[tuple[str, str]]:
    """The items asked of each part of the work, by their checklist and ID."""
    return [key(i) for i in run["each"]]


def usable(run: dict[str, Any]) -> list[tuple[str, str]]:
    """The items the first user and the evaluator answer, by their checklist and ID: those of the
    usability checklists, as the receiver has no sources."""
    return [key(i) for i in run["usable"]]


def reader_given(run: dict[str, Any], role: str) -> dict[str, Any]:
    """What the first user and the evaluator are given: what the receiver has, the usability
    checklists, the parts of the work, and the lessons taken for the role."""
    return {
        "work": run["work"],
        "has": run["has"],
        "receiver": run["receiver"],
        "use": run["use"],
        "checklists": run["usability"],
        "parts": forms.parts(run["work"]),
        "lessons": lessons(run, role),
    }


def ask(run: dict[str, Any], agent: str, given: dict[str, Any]) -> dict[str, str]:
    """Keeps the run with the agent to start next, or to send a message to once it is started,
    and what it is given, and gives the agent and its prompt, or the message and the agent it goes
    to. Either names the run alone, and the agent takes what it is given from the script, so no AI
    copies it."""
    prompt = json.dumps({"run": run["call"]["result"]}, ensure_ascii=False)
    to = run.get("started", {}).get(agent)
    if to:
        asked = {"agent": agent, "message": prompt, "to": to}
    else:
        asked = {"agent": agent, "prompt": prompt}
    run["next"] = dict(asked, given=given)
    write(run["call"]["result"], {"running": run})
    return asked


def sending(run: dict[str, Any], kind: str) -> bool:
    """Whether the round may send back once more of the kind, counting each time it is asked."""
    sent = run.setdefault("sent", {})
    sent[kind] = sent.get(kind, 0) + 1
    return sent[kind] <= SENDS


def awaited(result: str, run: dict[str, Any]) -> dict[str, Any]:
    """The run once the messaged role's reply is kept, or as it is after the wait. A run read as
    the hook writes it is read again at the next pause."""
    for _ in range(WAIT):
        if "reply" in run["next"]:
            return run
        time.sleep(1)
        run = running(result) or run
    return run


def given(result: str) -> dict[str, Any]:
    """What the agent started last in the run is given."""
    run = running(result)
    if run is None:
        raise call.Stop(f"turn: no run is going with its result at {result}")
    if "check" in run:
        raise call.Stop("turn: no role is started before the orchestrator's check is given")
    return run["next"]["given"]


def parts(result: str) -> dict[str, list[str]]:
    """The parts of the run's work as it stands, each as its lines."""
    run = running(result)
    if run is None:
        raise call.Stop(f"turn: no run is going with its result at {result}")
    return {"parts": forms.parts(run["work"])}


def record(result: str, number: str, page: str) -> str:
    """A page of a role's record of the run, headed by its number and page among all, so the
    learner is shown every record whole however long it is."""
    run = running(result)
    if run is None:
        raise call.Stop(f"turn: no run is going with its result at {result}")
    shown = learnt_from(run)
    if not number.isdigit() or not 1 <= int(number) <= len(shown):
        raise call.Stop(f"turn: record {number} is not one of 1 to {len(shown)}")
    path = shown[int(number) - 1]
    split = records.pages(path)
    if not page.isdigit() or not 1 <= int(page) <= len(split):
        raise call.Stop(f"turn: page {page} is not one of 1 to {len(split)} of record {number}")
    head = f"record {number} of {len(shown)}, page {page} of {len(split)}: {path}"
    return head + "\n" + split[int(page) - 1]


def learnt_from(run: dict[str, Any]) -> list[str]:
    """The records the learner started last in the run is shown, none before one is started."""
    return run.get("next", {}).get("given", {}).get("records", [])


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
        return checked(run, text) if text.strip() else {"check": run["check"]}
    agent = run["next"]["agent"]
    # A role sent a message replies later, kept by the hook, so the script waits for it.
    messaged = "to" in run["next"] and "reply" not in run["next"]
    if messaged:
        if text.strip():
            raise call.Stop(
                f"turn: {agent} has not replied; run `turn.py next <the call's result>` with"
                " nothing to wait for its reply"
            )
        run = awaited(result, run)
        if "reply" not in run["next"]:
            return {"waiting": agent}
    # Each role's record is kept for the learner, which looks for what makes the Good in what the
    # roles did.
    record = run["next"].get("record")
    if record and record not in run.setdefault("records", []):
        run["records"].append(record)
    if "decide" in run:
        # Asked with no decision, the items to decide are shown again, so the orchestrator can
        # always see them whole; and so with what the learner found, offered to take.
        return decide(run, text) if text.strip() else {"decide": run["decide"]}
    if "take" in run:
        return taking(run, text) if text.strip() else {"take": run["take"]}
    if agent == GENERATOR:
        if messaged:
            # The orchestrator reads the work made again from the generator's reply.
            return {"agent": GENERATOR, "reply": run["next"]["reply"]}
        return reading(run, text)
    reply = run["next"].get("reply")
    if reply is None:
        raise call.Stop(
            f"turn: {agent} has not replied; start {agent} with the prompt turn.py printed last,"
            " and wait for its reply"
        )
    return REPLIED[agent](run, reply)


def first_read(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Keeps the Goods of the first user's reading; sends the generator each item it stopped at,
    with where it stopped, but those waiting on a question, while the round may send them back;
    otherwise the evaluator holds the reading to the items."""
    run["read"] = [i for i in reply["items"] if good(i)]
    asked = [named(f) for f in run["findings"]["items"] if "question" in f]
    stops = [i for i in reply["items"] if "places" in i and named(i) not in asked]
    if stops and sending(run, FIRST_USER):
        return ask(run, GENERATOR, generator_given(run, stops, []))
    return evaluate(run)


def evaluate(run: dict[str, Any]) -> dict[str, Any]:
    return ask(run, EVALUATOR, dict(reader_given(run, "evaluator"), reading=run["read"]))


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
    return ask(run, GENERATOR, generator_given(run, [], []))


def reading(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the orchestrator's reading: the items and the statements it sends back go to the
    generator again; with none, the reading is kept as its findings and the first user reads the
    work."""
    said = forms.check(text, run["items"], run["work"], forms.READING, each=each(run))
    if said:
        raise call.Stop("turn: the reading is not filled:\n" + "\n".join(said))
    found = json.loads(forms.unfenced(text))
    sent_back = [i for i in found["items"] if "gets" in i]
    claim = run["next"].get("reply") or {}
    unsourced = found.pop("unsourced", [])
    # A statement the reading sends back itself is sent back once.
    unrun = [
        u
        for u in forms.unrun(found.pop("statements"), claim.get("statements", []))
        if not any(forms.overlap(u["lines"], s["lines"]) for s in unsourced)
    ]
    unsourced += unrun
    if (sent_back or unsourced) and sending(run, "reading"):
        return ask(run, GENERATOR, generator_given(run, sent_back, unsourced))
    run["findings"] = found
    return ask(run, FIRST_USER, reader_given(run, "first-user"))


def compare(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Sets the orchestrator's findings beside the evaluator's Goods and the first user's, for
    the orchestrator to decide every item, as readers that agree may still carry a doubt inside a
    Good."""
    evaluated = {key(i): judged(i) for i in reply["items"]}
    read = {key(i): judged(i) for i in run["read"]}
    findings = run["findings"]
    every = [
        dict(
            named(f),
            orchestrator=judged(f),
            evaluator=evaluated.get(key(f)),
            first_user=read.get(key(f)),
        )
        for f in findings["items"]
    ]
    run["decide"] = {"items": every, "questions": findings["questions"]}
    write(run["call"]["result"], {"running": run})
    return {"decide": run["decide"]}


def decide(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the orchestrator's decision on every item, and has the learner learn from the run."""
    asked = run["decide"]["questions"]
    said = forms.check(
        text, run["decide"]["items"], run["work"], forms.DECISION, len(asked), each=each(run)
    )
    if said:
        raise call.Stop("turn: the decision is not filled:\n" + "\n".join(said))
    decision = json.loads(forms.unfenced(text))
    # The calling AI is to get each Good found by a reader that did not make the work, so a
    # usability item neither the first user nor the evaluator found Good gets none from the
    # orchestrator alone; an accuracy item is answered against the sources, which no reader has.
    readers = usable(run)
    unread = [
        f"{i['checklist']} {i['item']} has no Good a reader found; give what the receiver gets"
        " once it has it, and where it is not found"
        for i in run["decide"]["items"]
        if not (i["evaluator"] or i["first_user"]) and key(i) in readers
        for d in decision["items"]
        if key(d) == key(i) and good(d)
    ]
    if unread:
        raise call.Stop("turn: the decision is not filled:\n" + "\n".join(unread))
    decided = {key(i): i for i in decision["items"]}
    items = [decided.get(key(f), f) for f in run["findings"]["items"]]
    del run["decide"]
    return settle(run, items, asked + decision["questions"])


def settle(run: dict[str, Any], items: list[dict[str, Any]], questions: list) -> dict[str, str]:
    """After every reading, the learner learns from every record of the run how the run went."""
    run["settled"] = {"items": items, "questions": questions}
    shown = run["records"] + [run["orchestrator"]] if "orchestrator" in run else run["records"]
    learner = {"findings": items, "records": shown, "lessons": lessons(run, "learner")}
    return ask(run, LEARNER, learner)


def remade(run: dict[str, Any]) -> bool:
    """Whether the work is made again: after the first reading alone, with an item without Good."""
    return not run.get("remade") and any("gets" in i for i in run["settled"]["items"])


def offer(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Offers the orchestrator every lesson the learner found on how the run went; with none to
    offer, the run goes on."""
    take = {"process": reply["process"], "checked": reply["checked"]}
    if not take["process"]:
        return took(run, [])
    run["take"] = take
    write(run["call"]["result"], {"running": run})
    return {"take": take}


def taking(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the lessons the orchestrator takes of those the learner found."""
    said = forms.taken(text, run["take"])
    if said:
        raise call.Stop("turn: what you take is not filled:\n" + "\n".join(said))
    chosen = json.loads(forms.unfenced(text))
    take = run.pop("take")
    return took(run, [take["process"][n - 1] for n in chosen["process"]])


def took(run: dict[str, Any], process: list) -> dict[str, str]:
    """With the lessons taken, the work is made again, or the run returns. The result holds each
    item's Good, each question an item still waits on with the items it settles, each item without
    Good with what the receiver gets once it has it and where it is not found, and every lesson on
    the run taken."""
    again = remade(run)
    run.setdefault("lessons", []).extend(process)
    settled = run.pop("settled")
    unmet = [i for i in settled["items"] if "gets" in i]
    if again:
        run["remade"] = True
        # The next round starts the generator and the first user anew, and counts anew.
        for anew in ("started", "sent"):
            run.pop(anew, None)
        return ask(run, GENERATOR, generator_given(run, unmet, []))
    result = run["call"]["result"]
    write(
        result,
        {
            "work": run["work"],
            "items": [i for i in settled["items"] if good(i)],
            "questions": waited(settled["items"], settled["questions"]),
            "not_good": unmet,
            "lessons": run["lessons"],
        },
    )
    return {"returned": result}


def waited(items: list[dict[str, Any]], questions: list) -> list[dict[str, Any]]:
    """Each question an item waits on, with the items it settles."""
    waiting: dict[Any, list[dict[str, str]]] = {}
    for i in items:
        if "question" in i:
            waiting.setdefault(i["question"], []).append(named(i))
    return [dict(q, items=waiting[n]) for n, q in enumerate(questions, 1) if n in waiting]


def named(item: dict[str, Any]) -> dict[str, str]:
    """The checklist and ID that name an item."""
    return {"checklist": item["checklist"], "item": item["item"]}


def key(item: dict[str, Any]) -> tuple[str, str]:
    return (item["checklist"], item["item"])


def good(item: dict[str, Any]) -> bool:
    """Whether the item is judged Good: with one Good, or with a Good for every part."""
    return "good" in item or "parts" in item


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
        # One key or value to a line, so the calling AI and the user can read the result.
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")


# What the run does after each role's reply but the generator's, which the orchestrator reads first.
REPLIED = {FIRST_USER: first_read, EVALUATOR: compare, LEARNER: offer}

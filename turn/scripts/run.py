"""The flow of a run: where the run stands, kept in its state beside the result, and the next move
the orchestrator makes, printed as the tool call itself; once the run returns, the result in the
form the calling AI reads."""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import time
from typing import IO, Any

import call
import forms
import records

GENERATOR = "turn:generator"
FIRST_USER = "turn:first-user"
EVALUATOR = "turn:evaluator"
LEARNER = "turn:learner"
UP = "turn:up"
# The roles kept started until the first user's reading of their round ends, each sent what comes
# next by message, so each works on with what it has already read.
KEPT = (GENERATOR, FIRST_USER)
# A reading that does not settle is bounded: the first user sends back three times a round.
SENDS = 3
# What the orchestrator judges, shown again whenever it asks.
SHOWN = ("check", "decide", "take")
# A messaged role's reply is waited for a second at a time, within the shell's two minutes.
WAIT = 100
# Where SendMessage reaches the main conversation, which alone talks with the user.
MAIN = "main"
# What each role is told of its run, as the line the calling AI is told.
DOES = {
    GENERATOR: "make the work to give every item its Good, and run what it gives as the receiver"
    " would",
    FIRST_USER: "use the work in the receiver's place and give each item's Good",
    EVALUATOR: "look through the work anew for every item's Good",
    LEARNER: "learn from every agent's record how the round went",
}
# What the orchestrator is told it will judge, as the line the calling AI is told, by what waits on
# its judgment.
JUDGES = {
    "check": "check that the CCS gives every item its Good",
    "ask": "ask what only the user can decide",
    "decide": "decide every item from both readers' Goods",
    "take": "take the learner's lessons that hold",
    "returned": "return the result",
}
# What each role is told when it is sent more work, as it is kept started.
AGAIN = {
    GENERATOR: "make the work again for each item the first user found no Good for",
    FIRST_USER: "read the work made again where it found no Good",
}
FORMS = {
    GENERATOR: forms.CLAIM,
    FIRST_USER: forms.FIRST_READING,
    EVALUATOR: forms.GOOD,
    LEARNER: forms.LEARNT,
}
USAGE = (
    "usage: turn.py start '<call JSON>'\n"
    "       turn.py next <result> [< <your check, decision, take or the agent ID as JSON>]\n"
    "       turn.py next <result> <page>\n"
    "       turn.py questions <result>\n"
    "       turn.py parts <result>"
)


def main(argv: list[str], stdin: IO[str]) -> int:
    """What turn.py runs: the call checked and the run started or gone on with, each step's outcome
    taken, giving the next move, what the orchestrator judges, or the result written; the questions
    the run asks, and the parts of the work. Prints what comes next and gives 0, or prints what was
    wrong and gives 1."""
    try:
        if argv[:1] == ["start"] and len(argv) == 2:
            print(json.dumps(start(argv[1]), ensure_ascii=False))
        elif argv[:1] == ["next"] and len(argv) == 2:
            print(shown(argv[1], next_step(argv[1], stdin.read()), "1"))
        elif argv[:1] == ["next"] and len(argv) == 3:
            print(shown(argv[1], view(argv[1]), argv[2]))
        elif argv[:1] == ["questions"] and len(argv) == 2:
            print(json.dumps(questions(argv[1]), ensure_ascii=False))
        elif argv[:1] == ["parts"] and len(argv) == 2:
            print(json.dumps(parts(argv[1]), ensure_ascii=False))
        else:
            print(USAGE)
            return 1
    except call.Stop as stop:
        print(stop)
        return 1
    return 0


def state_path(result: str) -> str:
    """Where the run is kept: beside its result, so a call again finds it by the result it names."""
    return result + ".run.json"


def reply_path(result: str, agent: str) -> str:
    """Where the role writes its reply, read by the flow alone, as a whole path."""
    return os.path.abspath(f"{result}.{agent.partition(':')[2]}.json")


def records_folder(result: str) -> str:
    """Where the records the learner reads are shown as text, as a whole path."""
    return os.path.abspath(result + ".records")


def whole(paths: list[str]) -> list[str]:
    """The paths as whole paths in the folder the call was made from, where the flow runs: a role's
    commands and hooks run from the session's working folder, which the calling AI may move with
    `cd`."""
    return [os.path.abspath(p) for p in paths]


def start(text: str) -> dict[str, Any]:
    """Starts the run the call asks for, or goes on with the run its result names from the move it
    was last at; gives where the result goes, for the run's lanes."""
    asked = call.parse(text)
    result = asked.get("result")
    kept = running(result) if isinstance(result, str) else None
    if kept is None or not isinstance(result, str):
        run = call.check(asked)
        # The paths of the call mean the folder it is made from, kept for every step after.
        run["root"] = os.getcwd()
        # The run waits on the orchestrator's check of these items.
        run["check"] = run["items"]
        save(run)
        return {"result": os.path.abspath(run["call"]["result"])}
    if kept["call"] != asked:
        raise call.Stop(
            f"turn: a run of another call is kept at {state_path(result)}; call turn with that"
            " call to go on with it, or with another result"
        )
    call.check(asked)
    save(resumed(kept))
    return {"result": os.path.abspath(result)}


def resumed(run: dict[str, Any]) -> dict[str, Any]:
    """The run gone on with by an orchestrator started anew: the agents of the run before are gone
    with it, so the role due is started anew with what it was given and what was sent to it since,
    and is told again."""
    step = run.get("next")
    if step:
        prompt = dict(run.get("prompts", {}).get(step["agent"], step["prompt"]))
        since = run.get("since", {}).get(step["agent"], [])
        if "to" in step:
            # A message moved is among those sent since; one due is not yet.
            prompt["since"] = since + ([] if step.get("moved") else [step["message"]])
        run["next"] = {"agent": step["agent"], "prompt": prompt}
    # A judgment due is told again, as the role due is.
    for gone in ("started", "since", "prompts", "told"):
        run.pop(gone, None)
    return run


def lessons(run: dict[str, Any], role: str) -> list[str]:
    """The lessons on how the run went that the orchestrator took for the role."""
    return [t["lesson"] for t in run.get("lessons", []) if t["role"] == role]


def each(run: dict[str, Any]) -> list[tuple[str, str]]:
    """The items asked of each part of the work, by their checklist and ID."""
    return [key(i) for i in run["each"]]


def generator_given(run: dict[str, Any], sent_back: list) -> dict[str, Any]:
    """What the generator is given: the files it makes the work from, the work, the checklists,
    each item sent back, the lessons taken for it, and where it replies."""
    return {
        "given": whole(run["given"]),
        "work": whole(run["work"]),
        "checklists": whole(run["checklist"]),
        "sent_back": sent_back,
        "lessons": lessons(run, "generator"),
        "reply": reply_path(run["call"]["result"], GENERATOR),
    }


def reader_given(run: dict[str, Any], agent: str) -> dict[str, Any]:
    """What the first user and the evaluator are given: what the receiver has with the work, the
    checklists, the receiver and their use, the parts of the work, the lessons taken for the role,
    and where it replies."""
    return {
        "given": whole(run["shown"]),
        "work": whole(run["work"]),
        "checklists": whole(run["checklist"]),
        "receiver": run["receiver"],
        "use": run["use"],
        "parts": forms.parts(run["work"]),
        "lessons": lessons(run, agent.partition(":")[2]),
        "reply": reply_path(run["call"]["result"], agent),
    }


def ask(run: dict[str, Any], agent: str, prompt: dict[str, Any], sent: Any = None) -> dict:
    """Keeps the run with the role due, to be told, then started with the prompt, or, once it is
    started, sent what is sent; and gives the line the calling AI is told."""
    to = run.get("started", {}).get(agent)
    if to and sent is not None:
        run["next"] = {"agent": agent, "prompt": prompt, "message": sent, "to": to}
    else:
        run["next"] = {"agent": agent, "prompt": prompt}
        run.setdefault("prompts", {})[agent] = prompt
        run.setdefault("since", {})[agent] = []
    return told(run)


def told(run: dict[str, Any]) -> dict[str, Any]:
    """The move telling the calling AI what was done and what the role due will do."""
    step = run["next"]
    agent = step["agent"]
    step["told"] = True
    # No judgment waits once a role is due.
    run.pop("told", None)
    return telling(run, agent, AGAIN[agent] if "to" in step else DOES[agent])


def judge(run: dict[str, Any], judged: str) -> dict[str, Any]:
    """The move telling the calling AI what was done and what the orchestrator will judge now; what
    waits on its judgment is shown after."""
    run["told"] = True
    return telling(run, UP, JUDGES[judged])


def telling(run: dict[str, Any], agent: str, does: str) -> dict[str, Any]:
    """The move telling the calling AI what was done and what the next move will do, how far and
    how; the flow makes the line from the move, so it says what the run does."""
    work = ", ".join(run["work"])
    done = run.pop("done", "")
    line = f"turn: {done + ' ' if done else ''}Next, {agent} will {does}, of {work}"
    line += f", for {len(run['items'])} items, round {2 if run.get('remade') else 1}."
    save(run)
    return {"line": line, "move": {"tool": "SendMessage", "input": {"to": MAIN, "message": line}}}


def moved(run: dict[str, Any]) -> dict[str, Any]:
    """The move starting the role due, or sending it what is sent; its reply is written anew."""
    step = run["next"]
    reply = step["prompt"]["reply"]
    if os.path.exists(reply):
        os.remove(reply)
    step["moved"] = True
    save(run)
    if "to" in step:
        message = json.dumps(step["message"], ensure_ascii=False)
        run.setdefault("since", {}).setdefault(step["agent"], []).append(step["message"])
        save(run)
        return {"move": {"tool": "SendMessage", "input": {"to": step["to"], "message": message}}}
    prompt = json.dumps(step["prompt"], ensure_ascii=False)
    agent = step["agent"]
    started = {"subagent_type": agent, "description": f"turn {agent}", "prompt": prompt}
    return {"move": {"tool": "Agent", "input": started}}


def sending(run: dict[str, Any]) -> bool:
    """Whether the round may send back once more, counting each time it is asked."""
    run["sent"] = run.get("sent", 0) + 1
    return run["sent"] <= SENDS


def awaited(path: str) -> bool:
    """Whether the reply is written, waited for where it comes later, as a role sent a message
    replies after the send."""
    for _ in range(WAIT):
        if os.path.exists(path):
            return True
        time.sleep(1)
    return os.path.exists(path)


def questions(result: str) -> dict[str, Any]:
    """The questions the run asks the calling AI, as the result holds them."""
    try:
        with open(result, encoding="utf-8") as f:
            kept = json.load(f)
    except (OSError, ValueError):
        kept = None
    if not isinstance(kept, dict) or "questions" not in kept:
        raise call.Stop(f"turn: {result} holds no questions; run `turn.py next {result}`")
    return {"questions": kept["questions"]}


def parts(result: str) -> dict[str, list[str]]:
    """The parts of the run's work as it stands, each as its lines."""
    return {"parts": forms.parts(going(result)["work"])}


def view(result: str) -> dict[str, Any]:
    """What the orchestrator is to judge now, the check, the items to decide or what to take."""
    run = going(result)
    for step in SHOWN:
        if step in run:
            return {step: run[step]}
    raise call.Stop(
        f"turn: nothing waits on your judgment to show in pages; run `turn.py next {result}`"
    )


def shown(result: str, out: dict[str, Any], page: str) -> str:
    """What turn.py prints: a move as the line it tells and the tool call itself, last, as one JSON
    line; anything else as JSON, in pages."""
    if "move" in out:
        move = json.dumps(out["move"], ensure_ascii=False)
        return f"{out['line']}\n{move}" if "line" in out else move
    return paged(result, out, page)


def paged(result: str, out: dict[str, Any], page: str) -> str:
    """A page of what turn.py prints, headed by its number among all where there is more than one,
    so the orchestrator sees whole what it judges however long it is, as the shell cuts a long
    print short."""
    split = records.split(json.dumps(out, ensure_ascii=False))
    if not page.isdigit() or not 1 <= int(page) <= len(split):
        raise call.Stop(f"turn: page {page} is not one of 1 to {len(split)}")
    shown = split[int(page) - 1]
    # A print in one page comes as it is.
    if not split[1:]:
        return shown
    head = (
        f"{next(iter(out))}, page {page} of {len(split)}: see every page, each with"
        f" `turn.py next {result} <page>` in a command of its own with no pipe or redirect"
    )
    return head + "\n" + shown


def going(result: str) -> dict[str, Any]:
    """The run going with its result at the path, gone on with from the folder the call was made
    from; stops where none is."""
    run = running(result)
    if run is None:
        raise call.Stop(
            f"turn: no run is going with its result at {result}; start one with"
            " `turn.py start '<call JSON>'`"
        )
    os.chdir(run["root"])
    return run


def next_step(result: str, text: str) -> dict[str, Any]:
    """Takes what the run waits on, the orchestrator's check, decision or take, or a role's reply,
    and gives what the orchestrator does next."""
    run = going(result)
    # What waits on the orchestrator's judgment is told first, before it is shown.
    waits = [j for j in JUDGES if j in run]
    if waits and not run.get("told") and not text.strip():
        return judge(run, waits[0])
    # Asked with nothing, what the orchestrator is to judge is shown again, so it can always see it
    # whole.
    if "check" in run:
        return checked(run, text) if text.strip() else {"check": run["check"]}
    if "ask" in run:
        run["asked"] = run.pop("ask")
        del run["told"]
        save(run)
        return {"asked": run["call"]["result"]}
    if "asked" in run:
        # The calling AI keeps the answer in its CCS, so the check is made again on it.
        anew = dict(call.check(run["call"]), root=run["root"], done="The calling AI answered.")
        anew["check"] = anew["items"]
        return judge(anew, "check")
    if "returned" in run:
        return returned(run)
    if "decide" in run:
        return decide(run, text) if text.strip() else {"decide": run["decide"]}
    if "take" in run:
        return taking(run, text) if text.strip() else {"take": run["take"]}
    step = run["next"]
    if not step.get("told"):
        return told(run)
    if not step.get("moved"):
        return moved(run)
    return replied(run, step, text)


def replied(run: dict[str, Any], step: dict[str, Any], text: str) -> dict[str, Any]:
    """Takes the role's reply once it is written: one out of its form is sent back to the role with
    what is wrong; one filled goes on to what the run does after it."""
    agent = step["agent"]
    if "to" not in step and "id" not in step:
        step["id"] = agent_id(agent, text)
        save(run)
    elif text.strip():
        raise call.Stop(
            f"turn: the run waits on {agent}'s reply, not on yours; run `turn.py next"
            f" {run['call']['result']}` with nothing"
        )
    to = step.get("to") or step["id"]
    path = step["prompt"]["reply"]
    if not awaited(path):
        return {"waiting": agent}
    with open(path, encoding="utf-8") as f:
        reply = f.read()
    said = forms.check(
        reply,
        run["items"],
        run["work"],
        FORMS[agent],
        records=tuple(run.get("learnt", [])),
        each=each(run),
    )
    if said:
        os.remove(path)
        fix = f"Write your reply to {path} again in your form, filled:\n" + "\n".join(said)
        return {"move": {"tool": "SendMessage", "input": {"to": to, "message": fix}}}
    # Each role's record is kept for the learner, which looks for what makes the Good in what the
    # roles did.
    if to not in run.setdefault("records", []):
        run["records"].append(to)
    if agent in KEPT:
        run.setdefault("started", {})[agent] = to
    del run["next"]
    return REPLIED[agent](run, json.loads(forms.unfenced(reply)))


def agent_id(agent: str, text: str) -> str:
    """The agent ID the Agent call starting the role gave back, as the orchestrator hands it on."""
    try:
        given = json.loads(forms.unfenced(text))
    except ValueError:
        given = None
    found = given.get("agent_id") if isinstance(given, dict) else None
    if not isinstance(found, str) or not found.strip():
        raise call.Stop(
            f'turn: give the agent ID the Agent call starting {agent} gave back, as {{"agent_id":'
            ' "<ID>"}'
        )
    return found


def made(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Keeps the generator's claim, for the questions it asks, and has the first user use the work
    made, with no reading between."""
    run["claim"] = reply
    run["done"] = f"{GENERATOR} made {', '.join(run['work'])}."
    # The parts are given anew, as a remake may add or take away a section.
    remade = {
        "remade": whole(run["work"]),
        "parts": forms.parts(run["work"]),
        "reply": reply_path(run["call"]["result"], FIRST_USER),
    }
    return ask(run, FIRST_USER, reader_given(run, FIRST_USER), remade)


def first_read(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Keeps the Goods of the first user's reading; sends the generator each item it stopped at,
    as the first user gave it, but those waiting on a question, while the round may send them
    back; otherwise the evaluator holds the reading to the items."""
    run["read"] = [i for i in reply["items"] if good(i)]
    asked = [named(f) for f in run["claim"]["items"] if "question" in f]
    stops = [i for i in reply["items"] if "places" in i and named(i) not in asked]
    run["done"] = f"{FIRST_USER} found the Good of {len(run['read'])} of {len(run['items'])} items."
    if stops and sending(run):
        back = {"sent_back": stops, "reply": reply_path(run["call"]["result"], GENERATOR)}
        return ask(run, GENERATOR, generator_given(run, stops), back)
    return ask(run, EVALUATOR, dict(reader_given(run, EVALUATOR), reading=run["read"]))


def checked(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the orchestrator's check: with an item the CCS cannot give its Good, the run asks
    the calling AI its questions, as no work made without the answer can give it; otherwise the
    generator makes the work."""
    said = forms.check(text, run["items"], run["work"], forms.CHECK)
    if said:
        raise call.Stop("turn: the check is not filled:\n" + "\n".join(said))
    found = json.loads(forms.unfenced(text))
    del run["check"]
    asked = waited(found["items"], found["questions"])
    if asked:
        write(run["call"]["result"], {"questions": asked})
        run["ask"] = asked
        waiting = len([i for i in found["items"] if "question" in i])
        run["done"] = (
            f"{UP} found {waiting} of {len(run['items'])} items waiting on the user's answer."
        )
        return judge(run, "ask")
    run["done"] = f"{UP} found in the CCS what gives the Good of {len(run['items'])} items."
    return ask(run, GENERATOR, generator_given(run, []))


def compare(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Sets the evaluator's Goods beside the first user's, with the question the generator found an
    item waits on, for the orchestrator to decide every item, as readers that agree may still carry
    a doubt inside a Good."""
    evaluated = {key(i): judged(i) for i in reply["items"]}
    read = {key(i): judged(i) for i in run["read"]}
    waits = {key(i): i["question"] for i in run["claim"]["items"] if "question" in i}
    every = [
        dict(
            named(i),
            evaluator=evaluated.get(key(i)),
            first_user=read.get(key(i)),
            **({"question": waits[key(i)]} if key(i) in waits else {}),
        )
        for i in run["items"]
    ]
    run["decide"] = {"items": every, "questions": run["claim"]["questions"]}
    found = len(reply["items"])
    run["done"] = f"{EVALUATOR} found the Good of {found} of {len(run['items'])} items."
    return judge(run, "decide")


def decide(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the orchestrator's decision on every item, and has the learner learn from the run."""
    asked = run["decide"]["questions"]
    said = forms.check(
        text, run["decide"]["items"], run["work"], forms.DECISION, len(asked), each=each(run)
    )
    if said:
        raise call.Stop("turn: the decision is not filled:\n" + "\n".join(said))
    decision = json.loads(forms.unfenced(text))
    # The calling AI is to get each Good found by a reader that did not make the work, so an item
    # neither the first user nor the evaluator found Good gets none from the orchestrator alone.
    unread = [
        f"{i['checklist']} {i['item']} has no Good a reader found; give what the receiver gets"
        " once it has it, and where it is not found"
        for i in run["decide"]["items"]
        if not (i["evaluator"] or i["first_user"])
        for d in decision["items"]
        if key(d) == key(i) and good(d)
    ]
    if unread:
        raise call.Stop("turn: the decision is not filled:\n" + "\n".join(unread))
    decided = {key(i): i for i in decision["items"]}
    items = [decided[key(i)] for i in run["items"]]
    del run["decide"]
    return settle(run, items, asked + decision["questions"])


def settle(run: dict[str, Any], items: list[dict[str, Any]], questions: list) -> dict[str, Any]:
    """After every round, the learner learns from every record of the run how the run went, each
    record shown as text it reads whole."""
    run["settled"] = {"items": items, "questions": questions}
    result = run["call"]["result"]
    found = [records.find(i) for i in run["records"]]
    kept = [p for p in found if p]
    orchestrator = records.orchestrator(kept, result)
    run["learnt"] = kept + ([orchestrator] if orchestrator else [])
    folder = records_folder(result)
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)
    texts = []
    for n, path in enumerate(run["learnt"], 1):
        texts.append(os.path.join(folder, f"{n}.txt"))
        with open(texts[-1], "w", encoding="utf-8") as f:
            f.write(records.wrapped(records.shown(path)))
    learner = {
        "given": texts,
        "findings": items,
        "lessons": lessons(run, "learner"),
        "reply": reply_path(result, LEARNER),
    }
    good_items = len([i for i in items if good(i)])
    run["done"] = f"{UP} decided {good_items} of {len(items)} items Good."
    return ask(run, LEARNER, learner)


def remade(run: dict[str, Any]) -> bool:
    """Whether the work is made again: after the first round alone, with an item without Good."""
    return not run.get("remade") and any("gets" in i for i in run["settled"]["items"])


def offer(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Offers the orchestrator every lesson the learner found on how the run went; with none to
    offer, the run goes on."""
    take = {"process": reply["process"], "checked": reply["checked"]}
    run["done"] = f"{LEARNER} gave {len(take['process'])} lessons on how the round went."
    if not take["process"]:
        return took(run, [])
    run["take"] = take
    return judge(run, "take")


def taking(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the lessons the orchestrator takes of those the learner found."""
    said = forms.taken(text, run["take"])
    if said:
        raise call.Stop("turn: what you take is not filled:\n" + "\n".join(said))
    chosen = json.loads(forms.unfenced(text))
    take = run.pop("take")
    run["done"] = f"{UP} took {len(chosen['process'])} of {len(take['process'])} lessons."
    return took(run, [take["process"][n - 1] for n in chosen["process"]])


def took(run: dict[str, Any], process: list) -> dict[str, Any]:
    """With the lessons taken, the work is made again, or the result is written and the run is to
    return. The result holds each item's Good, each question an item still waits on with the items
    it settles, each item without Good with what the receiver gets once it has it and where it is
    not found, and every lesson on the run taken."""
    again = remade(run)
    run.setdefault("lessons", []).extend(process)
    settled = run.pop("settled")
    unmet = [i for i in settled["items"] if "gets" in i]
    if again:
        run["remade"] = True
        # The next round starts the generator and the first user anew, and counts anew.
        for anew in ("started", "sent"):
            run.pop(anew, None)
        return ask(run, GENERATOR, generator_given(run, unmet))
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
    run["returned"] = True
    return judge(run, "returned")


def returned(run: dict[str, Any]) -> dict[str, Any]:
    """The run returned, once told: what it kept beside the result is removed."""
    result = run["call"]["result"]
    os.remove(state_path(result))
    for agent in FORMS:
        # A role a round did not reach, such as one called again before, wrote no reply.
        with contextlib.suppress(FileNotFoundError):
            os.remove(reply_path(result, agent))
    shutil.rmtree(records_folder(result))
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
    """The run kept for the result at the path, or None when none is."""
    try:
        with open(state_path(result), encoding="utf-8") as f:
            kept = json.load(f)
    except (OSError, ValueError):
        return None
    return kept if isinstance(kept, dict) else None


def save(run: dict[str, Any]) -> None:
    """Keeps where the run stands, beside its result."""
    write(state_path(run["call"]["result"]), run)


def write(path: str, data: dict[str, Any]) -> None:
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        # One key or value to a line, so the calling AI and the user can read it.
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")


# What the run does after each role's reply.
REPLIED = {GENERATOR: made, FIRST_USER: first_read, EVALUATOR: compare, LEARNER: offer}

"""The flow of a run: the stage the run is at, kept in its state, and the next move the
orchestrator makes, printed as the tool call itself, each told first by a line the flow makes;
the outcome of each move taken, and once the run returns, the result in the form the calling AI
reads."""

from __future__ import annotations

import glob
import json
import os
import shutil
import time
from typing import Any

import call
import forms
import prompts
import record
import state
from prompts import FIRST_USER, GENERATOR

UP = "turn:up"
# A reading that does not settle is bounded: the first user sends back three times a round.
SENDS = 3
# Rounds that do not settle are bounded too: one more round may run after the first, so an item two
# rounds leave without Good becomes a question, and the rounds count anew from its answer; the run
# keeps how many more rounds may run.
MORE = 1
# A messaged role's end is waited for a second at a time, within the shell's two minutes.
WAIT = 100
# Where SendMessage reaches the main conversation, which alone talks with the user.
MAIN = "main"
# What each role is told of its run, as the line the calling AI is told.
DOES = {
    GENERATOR: "make the work to give every item its Good, and run what it gives as the receiver"
    " would",
    FIRST_USER: "use the work in the receiver's place and give each item's Good",
}
# What the orchestrator does itself at each stage it is told of, as the line the calling AI is told.
OWN = {
    "check": "check that the CCS gives every item its Good",
    "ask": "ask what only the user can decide",
    "left": "word a question for each item two rounds left without Good",
    "returned": "return the result",
}
# What a role kept started is told when it is sent more, by what the message holds first.
AGAIN = {
    "sent_back": "make the work again for each item the first user found no Good for",
    "answers": "go on with the calling AI's answer",
    "remade": "read the work made again for every item",
}
# What a word a line counts by takes after it, by the count: none for one, an s for any other.
PLURAL = {1: ""}
# The stage a run gone on with by an orchestrator started anew is at, where the one before made a
# move of its own that is gone with it: a question asked is asked again.
AGAIN_AT = {"asked": "ask"}


def start(text: str) -> dict[str, Any]:
    """Starts the run the call asks for, or goes on with the run its result names from the move it
    was last at, begun again where the CCS now lays the run out anew; gives, for the run's lanes,
    where the result goes and what the orchestrator reads for its check: the CCS and every file it
    names but the work."""
    asked = call.checked(call.parse(text))
    kept = state.running(asked["result"])
    if kept is None:
        # The paths of the call mean the folder it is made from, kept for every step after.
        run = begun(asked, os.getcwd())
    elif kept["call"] != asked:
        raise call.Stop(
            f"turn: a run of another call is kept at {state.state_path(asked['result'])}; call turn"
            " with that call to go on with it, or with another result"
        )
    elif laid_out_anew(kept):
        run = again(kept)
    else:
        run = resumed(kept)
    state.save(run)
    return {"result": os.path.abspath(asked["result"]), "given": prompts.checked(run)}


def begun(asked: dict[str, Any], root: str) -> dict[str, Any]:
    """The run the call asks for, from the folder it is made from, at the orchestrator's check of
    every item, in its first round, not told yet."""
    run = call.laid_out(asked)
    run.update(root=root, round=1, more=MORE, stage="check", told=False)
    return run


def resumed(run: dict[str, Any]) -> dict[str, Any]:
    """The run gone on with by an orchestrator started anew: the agents of the run before are gone
    with it, so the role due is started anew with what it was given and what was sent to it since;
    a question asked is asked again; and the stage is told again."""
    step = run.get("next")
    if step:
        prompt = dict(run.get("prompts", {}).get(step["agent"], step["prompt"]))
        since = run.get("since", {}).get(step["agent"], [])
        if "to" in step:
            # A message moved is among those sent since; one due is not yet.
            prompt["since"] = since + ([] if step.get("moved") else [step["message"]])
        run["next"] = {"agent": step["agent"], "prompt": prompt}
    run["stage"] = AGAIN_AT.get(run["stage"], run["stage"])
    for gone in ("started", "since", "prompts"):
        run.pop(gone, None)
    run["told"] = False
    return run


def laid_out_anew(run: dict[str, Any]) -> bool:
    """Whether the CCS now lays the run out other than it was begun with: other files of the work,
    checklists, items, receiver, use or what the receiver has."""
    anew = call.laid_out(run["call"])
    return any(anew[k] != run[k] for k in anew)


def again(run: dict[str, Any]) -> dict[str, Any]:
    """The run begun again on the CCS as it is now, at the check, with every answer the calling AI
    gave, and what was done last, for the line telling the check."""
    anew = begun(run["call"], run["root"])
    anew.update({k: run[k] for k in ("answers", "done") if k in run})
    return anew


def next_step(result: str, text: str) -> dict[str, Any]:
    """Takes what the run waits on at its stage, the orchestrator's check, its questions, the
    calling AI's answer or a role's reply, and gives what the orchestrator does next."""
    run = state.going(result)
    return STAGES[run["stage"]](run, text)


def view(result: str) -> dict[str, Any]:
    """What the orchestrator is to judge now, the same on every page: the items to check with what
    to read for it, or the items left without Good to word a question for."""
    run = state.going(result)
    if run["stage"] not in VIEWS:
        raise call.Stop(
            f"turn: nothing waits on your judgment to show in pages; run `turn.py next {result}`"
        )
    return VIEWS[run["stage"]](run)


def questions(result: str) -> dict[str, Any]:
    """The questions the run asks the calling AI now, each with the items it settles."""
    run = state.going(result)
    if run["stage"] != "asked":
        raise call.Stop(f"turn: the run asks no question now; run `turn.py next {result}`")
    return {"questions": run["questions"]["questions"]}


def parts(result: str) -> dict[str, list[str]]:
    """The parts of the run's work as it stands, each as its lines."""
    return {"parts": prompts.parts(state.going(result))}


def counted(count: int, word: str) -> str:
    """The count with the word it counts, as a line says it."""
    return f"{count} {word}{PLURAL.get(count, 's')}"


def covered(run: dict[str, Any]) -> list[dict[str, Any]]:
    """The items the next move covers: those the generator is given to make again, those left to
    word a question for, or else every item."""
    step = run.get("next")
    if step:
        return step["prompt"].get("sent_back") or run["items"]
    return run["left"] if run["stage"] == "left" else run["items"]


def tell(run: dict[str, Any]) -> dict[str, Any]:
    """The move telling the calling AI what was done and what the next move will do, how far and
    how: the role due, or the orchestrator's own move at the stage; the flow makes the line from
    the move, so it says what the run does."""
    step = run.get("next")
    if step:
        agent = step["agent"]
        does = AGAIN[next(iter(step["message"]))] if "to" in step else DOES[agent]
    else:
        agent, does = UP, OWN[run["stage"]]
    work = ", ".join(run["work"])
    done = run.pop("done", "")
    line = f"turn: {done + ' ' if done else ''}Next, {agent} will {does}, of {work}"
    line += f", for {counted(len(covered(run)), 'item')}, round {run['round']}."
    run["told"] = True
    state.save(run)
    return {"line": line, "move": {"tool": "SendMessage", "input": {"to": MAIN, "message": line}}}


def judge(run: dict[str, Any], stage: str) -> dict[str, Any]:
    """The run at a stage the orchestrator makes the move of itself, told."""
    run["stage"] = stage
    return tell(run)


def due(
    run: dict[str, Any], agent: str, prompt: dict[str, Any], sent: Any = None
) -> dict[str, Any]:
    """The run with the role due, told, to be started with the prompt, or, once it is kept
    started, sent what is sent."""
    to = run.get("started", {}).get(agent)
    if to and sent:
        run["next"] = {"agent": agent, "prompt": prompt, "message": sent, "to": to}
    else:
        run["next"] = {"agent": agent, "prompt": prompt}
        run.setdefault("prompts", {})[agent] = prompt
        run.setdefault("since", {})[agent] = []
    run["stage"] = "role"
    return tell(run)


def checking(run: dict[str, Any], text: str) -> dict[str, Any]:
    """At the check: the orchestrator's check taken, or what it checks shown, once told."""
    return checked(run, text) if text.strip() else to_judge(run)


def leaving(run: dict[str, Any], text: str) -> dict[str, Any]:
    """At the items left: the orchestrator's questions for them taken, or the items shown, once
    told."""
    return left_asked(run, text) if text.strip() else to_judge(run)


def to_judge(run: dict[str, Any]) -> dict[str, Any]:
    """What the orchestrator is to judge at the stage, told first."""
    return VIEWS[run["stage"]](run) if run["told"] else tell(run)


def asking_now(run: dict[str, Any], text: str) -> dict[str, Any]:
    """At the questions, once told: the run asks the calling AI them."""
    if not run["told"] and not text.strip():
        return tell(run)
    run["stage"] = "asked"
    state.save(run)
    return {"asked": run["call"]["result"]}


def returning(run: dict[str, Any], text: str) -> dict[str, Any]:
    """At the result written, once told: the run's folder is removed, the result alone staying, and
    the run returns."""
    if not run["told"] and not text.strip():
        return tell(run)
    result = run["call"]["result"]
    shutil.rmtree(state.folder(result))
    return {"returned": result}


def role(run: dict[str, Any], text: str) -> dict[str, Any]:
    """At the role due: told, then started or sent what is sent, then its reply taken."""
    step = run["next"]
    if not run["told"]:
        return tell(run)
    if not step.get("moved"):
        return moved(run)
    return replied(run, step, text)


def moved(run: dict[str, Any]) -> dict[str, Any]:
    """The move starting the role due, or sending it what is sent, the message kept among those sent
    to it since it started; its reply is written anew."""
    step = run["next"]
    agent = step["agent"]
    reply = step["prompt"]["reply"]
    if os.path.exists(reply):
        os.remove(reply)
    step["moved"] = True
    if "to" in step:
        run.setdefault("since", {}).setdefault(agent, []).append(step["message"])
        return sent(run, step, step["to"], json.dumps(step["message"], ensure_ascii=False))
    state.save(run)
    prompt = json.dumps(step["prompt"], ensure_ascii=False)
    started = {"subagent_type": agent, "description": f"turn {agent}", "prompt": prompt}
    return {"move": {"tool": "Agent", "input": started}}


def sent(run: dict[str, Any], step: dict[str, Any], to: str, message: str) -> dict[str, Any]:
    """The move sending the role's agent the message, kept with how many messages its record holds
    before it, so the role's end is read after it."""
    step["heard"] = len(messages(entries(to)))
    state.save(run)
    return {"move": {"tool": "SendMessage", "input": {"to": to, "message": message}}}


def replied(run: dict[str, Any], step: dict[str, Any], text: str) -> dict[str, Any]:
    """Takes the role's reply once the role has ended, as a role may change its reply until it ends:
    a role started has ended once its Agent call gave back its agent ID, and one sent a message
    once its record shows it; until then the run waits on it. One ended with no reply is told to
    write it; one out of its form is sent back with what is wrong; one filled goes on to what the
    run does after it."""
    agent = step["agent"]
    path = step["prompt"]["reply"]
    if "to" not in step and "id" not in step:
        step["id"] = agent_id(agent, text)
        state.save(run)
    elif not awaited(run, step, text):
        return {"waiting": agent}
    to = step.get("to") or step["id"]
    if not os.path.exists(path):
        return sent(run, step, to, f"Write your reply to {path} in your form; it is not there")
    with open(path, encoding="utf-8") as f:
        reply = f.read()
    said = PROBLEMS[agent](run, reply)
    if said:
        os.remove(path)
        fix = f"Write your reply to {path} again in your form, filled:\n" + "\n".join(said)
        return sent(run, step, to, fix)
    # Each role is kept started through its round, sent what comes next by message, so it works on
    # with what it has already read.
    run.setdefault("started", {})[agent] = to
    del run["next"]
    return REPLIED[agent](run, json.loads(forms.unfenced(reply)))


def awaited(run: dict[str, Any], step: dict[str, Any], text: str) -> bool:
    """Whether the role sent a message has ended since, waiting on it a second at a time within the
    shell's two minutes. The flow reads the end in the record Claude Code writes of the role's
    agent, as Claude Code tells it by a task notification to the main conversation alone where
    turn:up is a subagent; stops where the orchestrator hands on anything, saying to hand on
    nothing."""
    agent, to = step["agent"], step.get("to") or step["id"]
    if text.strip():
        raise call.Stop(
            f"turn: the run waits on the end of {agent}, agent {to}, which it reads in the agent's"
            f" record; run `turn.py next {run['call']['result']}` with nothing"
        )
    for _ in range(WAIT):
        if role_ended(to, step["heard"]):
            return True
        time.sleep(1)
    return role_ended(to, step["heard"])


def role_ended(to: str, heard: int) -> bool:
    """Whether the agent of the ID has ended since the message sent to it last: its record holds
    more messages than the number it held before that one, and a reply ending its turn after the
    last of them."""
    found = entries(to)
    replies = record.replies(found)
    told = messages(found)
    last = max(told + replies, default=None)
    return bool(told[heard:]) and last in replies


def entries(to: str) -> list[dict[str, Any]]:
    """The entries of the record Claude Code keeps of the agent of the ID, beside the record of the
    conversation it runs under, in whichever project; none where it is not there yet. An agent ID
    names one agent, so one record."""
    session = record.conversation("*", os.path.join(glob.escape(record.projects()), "*"))
    for file in glob.glob(record.subagent(session, glob.escape(to))):
        return record.read(file) or []
    return []


def messages(found: list[dict[str, Any]]) -> list[int]:
    """Where each message that reached an agent, its prompt first, stands among the entries of its
    record."""
    return [n for n, entry in enumerate(found) if record.message(entry)]


def agent_id(agent: str, text: str) -> str:
    """The agent ID the Agent call starting the role gave back, as the orchestrator hands it on."""
    try:
        found = json.loads(forms.unfenced(text))
    except ValueError:
        found = None
    named = found.get("agent_id") if isinstance(found, dict) else None
    if not forms.worded(named):
        raise call.Stop(
            f'turn: give the agent ID the Agent call starting {agent} gave back, as {{"agent_id":'
            ' "<ID>"}'
        )
    return str(named)


def claim_problems(run: dict[str, Any], reply: str) -> list[str]:
    """What is wrong with the generator's claim."""
    return forms.check(reply, run["items"], prompts.absolute(run["work"]), forms.CLAIM, run["each"])


def reading_problems(run: dict[str, Any], reply: str) -> list[str]:
    """What is wrong with the first user's reading."""
    work = prompts.absolute(run["work"])
    return forms.check(reply, run["items"], work, forms.FIRST_READING, run["each"])


def checked(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Takes the orchestrator's check: with an item the CCS cannot give its Good, the run asks the
    calling AI at once, as no work made without the answer can give it; otherwise the generator
    makes the work."""
    work = prompts.absolute(run["work"])
    said = forms.check(text, run["items"], work, forms.CHECK, run["each"])
    if said:
        raise call.Stop(
            "turn: the check is not filled:\n"
            + "\n".join(said)
            + f"\nrun `turn.py next {run['call']['result']}` again with the check filled"
        )
    found = json.loads(forms.unfenced(text))
    if found["questions"]:
        return asking(run, "check", UP, found)
    run["done"] = (
        f"{UP} found in the CCS what gives the Good of {counted(len(run['items']), 'item')}."
    )
    return generate(run, [])


def asking(run: dict[str, Any], source: str, who: str, found: dict[str, Any]) -> dict[str, Any]:
    """Has the run ask the calling AI the questions found, each with the items it settles, as soon
    as they are met; the source, the check, the generator or the items left, says where the run
    goes on once answered."""
    run["questions"] = {"from": source, "questions": waited(found["items"], found["questions"])}
    waiting = len([i for i in found["items"] if "question" in i])
    run["done"] = (
        f"{who} found {waiting} of {counted(len(run['items']), 'item')} waiting on the user's"
        " answer."
    )
    return judge(run, "ask")


def answered(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Keeps the calling AI's answer, as it came, with the questions it answers, and goes on where
    they were asked; where the CCS the calling AI kept the answer in now lays the run out anew,
    such as with a file added to it, the run is to be started again."""
    if not text.strip():
        raise call.Stop(
            "turn: the run waits on the calling AI's answer; run `turn.py next"
            f" {run['call']['result']}` with the answer, as it came, as its input"
        )
    asked = run["questions"]["questions"]
    run.setdefault("answers", []).append({"questions": asked, "answer": text.strip()})
    run["done"] = "The calling AI answered."
    run["stage"] = "anew"
    return anew(run, "")


def anew(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Once answered: where the CCS lays the run out anew, the orchestrator starts it again, so the
    run, and the lanes on what the orchestrator reads, take the files the CCS now names; otherwise
    the run goes on where the questions were asked."""
    if laid_out_anew(run):
        state.save(run)
        return {"anew": run["call"]["result"]}
    return GOES_ON[run.pop("questions")["from"]](run)


def checked_again(run: dict[str, Any]) -> dict[str, Any]:
    """The check made again on the CCS the calling AI kept the answer in."""
    return judge(run, "check")


def sent_answer(run: dict[str, Any]) -> dict[str, Any]:
    """The generator that asked is sent the answer, and goes on making the work."""
    message = {
        "answers": [run["answers"][-1]],
        "reply": prompts.reply_path(run["call"]["result"], GENERATOR),
    }
    return generate(run, run["back"], message)


def left_answered(run: dict[str, Any]) -> dict[str, Any]:
    """The items two rounds left without Good are made again with the answer, the rounds counted
    anew from it."""
    run["more"] = MORE
    return next_round(run, run["back"])


def generate(
    run: dict[str, Any], sent_back: list[dict[str, Any]], sent: Any = None
) -> dict[str, Any]:
    """Has the generator make the work, started with what it is given, or, kept started, sent what
    is sent; the items sent back are kept, so a generator started anew is given them."""
    run["back"] = sent_back
    return due(run, GENERATOR, prompts.generator(run, sent_back), sent)


def made(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Has the run ask the generator's questions at once, before any reading rests on them;
    otherwise keeps the choices the work as made rests on, as the claim names them, and has the
    first user use the work made, with no reading between."""
    if reply["questions"]:
        return asking(run, GENERATOR, GENERATOR, reply)
    run["chosen"] = reply["chosen"]
    run["done"] = f"{GENERATOR} made {', '.join(run['work'])}."
    return due(run, FIRST_USER, prompts.reader(run), prompts.remade(run))


def first_read(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Takes the first user's reading: an item has its Good where the first user gave one; the
    generator is sent each item it stopped at, as the first user gave it, while the round may send
    them back; otherwise the round ends."""
    goods = [i for i in reply["items"] if good(i)]
    stops = [i for i in reply["items"] if not good(i)]
    run["done"] = (
        f"{FIRST_USER} found the Good of {len(goods)} of {counted(len(run['items']), 'item')}."
    )
    if stops and sending(run):
        back = {"sent_back": stops, "reply": prompts.reply_path(run["call"]["result"], GENERATOR)}
        return generate(run, stops, back)
    return ended(run, goods, stops)


def sending(run: dict[str, Any]) -> bool:
    """Whether the round may send back once more, counting each time it is asked."""
    run["sent"] = run.get("sent", 0) + 1
    return run["sent"] <= SENDS


def ended(
    run: dict[str, Any], goods: list[dict[str, Any]], lacking: list[dict[str, Any]]
) -> dict[str, Any]:
    """The round ended: with every item's Good, the result is written; otherwise the items without
    Good are made again in the next round, or, once the rounds are spent, wait on a question the
    orchestrator words."""
    if not lacking:
        return finished(run, goods)
    if run["more"]:
        run["more"] -= 1
        return next_round(run, lacking)
    run["left"] = lacking
    return judge(run, "left")


def next_round(run: dict[str, Any], lacking: list[dict[str, Any]]) -> dict[str, Any]:
    """The next round: the generator and the first user started anew, counting anew, the generator
    given each item without Good with what was found lacking."""
    run["round"] += 1
    for anew_count in ("started", "sent"):
        run.pop(anew_count, None)
    return generate(run, lacking)


def left_asked(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Takes the orchestrator's question for each item two rounds left without Good, and has the
    run ask them at once."""
    left = [forms.named(i) for i in run["left"]]
    said = forms.check(text, left, prompts.absolute(run["work"]), forms.LEFT, run["each"])
    if said:
        raise call.Stop(
            "turn: the questions are not filled:\n"
            + "\n".join(said)
            + f"\nrun `turn.py next {run['call']['result']}` again with the questions filled"
        )
    run["back"] = run.pop("left")
    return asking(run, "left", UP, json.loads(forms.unfenced(text)))


def finished(run: dict[str, Any], goods: list[dict[str, Any]]) -> dict[str, Any]:
    """Once every item has its Good, writes the result and has the run return: where the work is,
    each item's Good as the first user gave it, in the checklists' order, and each choice the work
    rests on, as the generator's last claim named it."""
    found = {forms.key_of(g): g for g in goods}
    items = [found[forms.key_of(i)] for i in run["items"]]
    made = {"work": run["work"], "items": items, "chosen": run["chosen"]}
    state.write(run["call"]["result"], made)
    return judge(run, "returned")


def waited(items: list[dict[str, Any]], asked: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each question an item waits on, with the items it settles."""
    waiting: dict[Any, list[dict[str, Any]]] = {}
    for i in items:
        if "question" in i:
            waiting.setdefault(i["question"], []).append(forms.named(i))
    return [dict(q, items=waiting[n]) for n, q in enumerate(asked, 1) if n in waiting]


def good(item: dict[str, Any]) -> bool:
    """Whether the item is judged Good: with one Good, or with a Good for every part."""
    return "good" in item or "parts" in item


def checked_view(run: dict[str, Any]) -> dict[str, Any]:
    """The items to check, with what to read for it as the CCS now names it."""
    return {"check": run["items"], "given": prompts.checked(run)}


def left_view(run: dict[str, Any]) -> dict[str, Any]:
    """The items two rounds left without Good, as the first user last gave them."""
    return {"left": run["left"]}


# What the run takes at each stage.
STAGES = {
    "check": checking,
    "ask": asking_now,
    "asked": answered,
    "anew": anew,
    "left": leaving,
    "role": role,
    "returned": returning,
}
# What the orchestrator is shown at each stage that waits on its judgment.
VIEWS = {"check": checked_view, "left": left_view}
# What is wrong with each role's reply.
PROBLEMS = {GENERATOR: claim_problems, FIRST_USER: reading_problems}
# What the run does after each role's reply.
REPLIED = {GENERATOR: made, FIRST_USER: first_read}
# Where the run goes on once the calling AI answers, by where the questions were asked.
GOES_ON = {"check": checked_again, GENERATOR: sent_answer, "left": left_answered}

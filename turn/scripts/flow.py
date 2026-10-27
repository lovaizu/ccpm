"""The flow of a run: the stage the run is at, kept in its state, and the next move the
orchestrator makes, printed as the tool call itself, with the line the flow makes for the user
where a role starts or ends, a point is asked or the result is back; the outcome of each move
taken, a role's end waited for here, and once the run returns, the result in the form the calling
AI reads."""

from __future__ import annotations

import contextlib
import fcntl
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
# A messaged role's end is waited for a second at a time, as one move of the orchestrator, within
# the ten minutes its step gives the shell, the most Claude Code lets a command run before it moves
# it to the background.
WAIT = 540
# Where SendMessage reaches the main conversation, which alone talks with the user.
MAIN = "main"
# What a role does as it starts, as the line the user is told, the work's files put in for `{work}`.
DOES = {
    GENERATOR: "make {work} to give every item its Good",
    FIRST_USER: "use {work} in the receiver's place and give each item's Good",
}
# What a role kept started does once it is sent more, by what the message holds first.
AGAIN = {
    "sent_back": "make {work} again for each item the first user found no Good for",
    "answers": "take in the user's answer",
    "remade": "read {work} made again",
}
# What a word a line counts by takes after it, by the count: none for one, an s for any other.
PLURAL = {1: ""}
# The stage a run gone on with by an orchestrator started anew is at, where the one before made a
# move of its own that is gone with it: a question asked is asked again.
AGAIN_AT = {"asked": "ask"}
# The file in the run's folder a `turn.py next` holds while it runs, so no second one, started while
# the first waits on a role and Claude Code has moved it to the background, takes the same move.
LOCK = "next.lock"


def start(text: str) -> dict[str, Any]:
    """Starts the run the call asks for, or goes on with the run its result names from the move it
    was last at, begun again where the CCS now lays the run out anew; gives where the result goes,
    as a whole path, which each later command names."""
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
    return {"result": os.path.abspath(asked["result"])}


def begun(asked: dict[str, Any], root: str, kept: dict[str, Any] | None = None) -> dict[str, Any]:
    """The run the call asks for, from the folder it is made from, in its first round, with what is
    kept of a run before it, its answers and what it did last; its generator due, which asks first
    what only the user can decide."""
    run = call.laid_out(asked)
    run.update(root=root, round=1, more=MORE, back=[])
    run.update({k: v for k, v in (kept or {}).items() if k in ("answers", "done")})
    due(run, GENERATOR, prompts.generator(run, []))
    return run


def resumed(run: dict[str, Any]) -> dict[str, Any]:
    """The run gone on with by an orchestrator started anew: the agents of the run before are gone
    with it, so the role due is started anew, told again, with what it was given and what was sent
    to it since; and a question asked is asked again."""
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
    return run


def laid_out_anew(run: dict[str, Any]) -> bool:
    """Whether the CCS now lays the run out other than it was begun with: other files of the work,
    checklists, items, receiver, use or what the receiver has."""
    anew = call.laid_out(run["call"])
    return any(anew[k] != run[k] for k in anew)


def again(run: dict[str, Any]) -> dict[str, Any]:
    """The run begun again on the CCS as it is now, with every answer the calling AI gave, and what
    was done last, for the line telling the generator's start."""
    return begun(run["call"], run["root"], run)


def next_step(result: str, text: str) -> dict[str, Any]:
    """Takes what the run waits on at its stage, the orchestrator's questions, the calling AI's
    answer or a role's reply, and gives what the orchestrator does next; stops where another
    `turn.py next` of the run still runs."""
    called = state.going(result)["call"]["result"]
    with held(called):
        run = state.going(called)
        return STAGES[run["stage"]](run, text)


@contextlib.contextmanager
def held(result: str) -> Any:
    """Holds the run of the result, in the folder the call was made from, while the block runs;
    stops where another process holds it."""
    with open(os.path.join(state.folder(result), LOCK), "w", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)  # pragma: no mutate
        except OSError:
            raise call.Stop(
                f"turn: another `turn.py next {result}` still runs, waiting on a role's end; wait"
                " for it to end and take the move it prints"
            ) from None
        yield


def view(result: str) -> dict[str, Any]:
    """What the orchestrator is to judge now, the same on every page: the items left without Good
    to word a question for."""
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


def tell(line: str) -> dict[str, Any]:
    """The move sending the line to the main conversation, which alone talks with the user."""
    return {"tool": "SendMessage", "input": {"to": MAIN, "message": line}}


def said(run: dict[str, Any], words: str = "") -> str:
    """The line for the user: what was done last, then the words, as the flow makes it from the
    move, so it says what the run does."""
    return "turn: " + " ".join(w for w in (run.pop("done", ""), words) if w)


def doing(run: dict[str, Any], verb: str, does: str) -> str:
    """The line telling the role due, starting or going on, what it does, of the run's work, in
    which round."""
    work = ", ".join(run["work"])
    return said(
        run, f"{run['next']['agent']} {verb}: {does.format(work=work)}, round {run['round']}."
    )


def due(run: dict[str, Any], agent: str, prompt: dict[str, Any], sent: Any = None) -> None:
    """Has the role due, to be started with the prompt, or, once it is kept started, sent what is
    sent."""
    to = run.get("started", {}).get(agent)
    if to and sent:
        run["next"] = {"agent": agent, "prompt": prompt, "message": sent, "to": to}
    else:
        run["next"] = {"agent": agent, "prompt": prompt}
        run.setdefault("prompts", {})[agent] = prompt
        run.setdefault("since", {})[agent] = []
    run["stage"] = "role"


def leaving(run: dict[str, Any], text: str) -> dict[str, Any]:
    """At the items left: the orchestrator's questions for them taken, or the items shown again."""
    return left_asked(run, text) if text.strip() else left_view(run)


def asking_now(run: dict[str, Any], text: str) -> dict[str, Any]:
    """The run asks the calling AI the questions, told."""
    run["stage"] = "asked"
    asked = run["questions"]
    line = said(
        run, f"{asked['who']} asks the user {counted(len(asked['questions']), 'question')}."
    )
    state.save(run)
    return {"line": line, "asked": run["call"]["result"]}


def returning(run: dict[str, Any], text: str) -> dict[str, Any]:
    """The result written: the run's folder is removed, the result alone staying, and the run
    returns, told."""
    result = run["call"]["result"]
    line = said(run, f"The result is at {result}.")
    shutil.rmtree(state.folder(result))
    return {"line": line, "returned": result}


def role(run: dict[str, Any], text: str) -> dict[str, Any]:
    """At the role due: a role to start told first by a move of its own, as the Agent call starting
    it returns only at its end; then started or sent what is sent, a message told in the same move;
    then its reply taken."""
    step = run["next"]
    if "to" not in step and not step.get("told"):
        line = doing(run, "starts", DOES[step["agent"]])
        step["told"] = True
        state.save(run)
        return {"move": tell(line)}
    if not step.get("moved"):
        return moved(run)
    return replied(run, step, text)


def moved(run: dict[str, Any]) -> dict[str, Any]:
    """The move starting the role due, or sending it what is sent, told, the message kept among
    those sent to it since it started; its reply is written anew."""
    step = run["next"]
    agent = step["agent"]
    reply = step["prompt"]["reply"]
    if os.path.exists(reply):
        os.remove(reply)
    step["moved"] = True
    if "to" in step:
        line = doing(run, "goes on", AGAIN[next(iter(step["message"]))])
        run.setdefault("since", {}).setdefault(agent, []).append(step["message"])
        message = json.dumps(step["message"], ensure_ascii=False)
        return dict(sent(run, step, step["to"], message), line=line)
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
    """Whether the role sent a message has ended since, waiting on it a second at a time up to
    WAIT. The flow reads the end in the record Claude Code writes of the role's
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
    """What is wrong with the generator's claim: of every item, or on a remake of each item sent
    back alone, as an item not sent back stands as it was."""
    back = [forms.named(i) for i in run["back"]]
    form = forms.REMADE if back else forms.CLAIM
    work = prompts.absolute(run["work"])
    return forms.check(reply, back or run["items"], work, form, run["each"])


def reading_problems(run: dict[str, Any], reply: str) -> list[str]:
    """What is wrong with the first user's reading."""
    work = prompts.absolute(run["work"])
    return forms.check(reply, run["items"], work, forms.FIRST_READING, run["each"])


def asking(run: dict[str, Any], source: str, who: str, found: dict[str, Any]) -> dict[str, Any]:
    """Has the run ask the calling AI the questions found, each with the items it settles, as soon
    as they are met, told as asked by who found them; the source, the generator or the items left,
    says where the run goes on once answered."""
    asked = waited(found["items"], found["questions"])
    run["questions"] = {"from": source, "who": who, "questions": asked}
    return asking_now(run, "")


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


def settled(run: dict[str, Any]) -> dict[str, Any]:
    """A gap the generator and the first user differed on, settled by the answer: the generator is
    sent each item the first user stopped at with the answer, in the round where they differed, as
    no making was spent on the gap."""
    message = {
        "sent_back": run["back"],
        "answers": [run["answers"][-1]],
        "reply": prompts.reply_path(run["call"]["result"], GENERATOR),
    }
    return generate(run, run["back"], message)


def generate(
    run: dict[str, Any], sent_back: list[dict[str, Any]], sent: Any = None
) -> dict[str, Any]:
    """Has the generator make the work, started with what it is given, or, kept started, sent what
    is sent; the items sent back are kept, so a generator started anew is given them."""
    run["back"] = sent_back
    due(run, GENERATOR, prompts.generator(run, sent_back), sent)
    return role(run, "")


def made(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Has the run ask the generator's questions at once, before any reading rests on them;
    otherwise keeps the choices the work as made rests on, as the claim names them, and has the
    first user use the work made, with no reading between: one kept started, which found the gaps
    sent back, is sent the generator's answer to each with the work made again; one started anew
    reads it on its own first."""
    if reply["questions"]:
        return asking(run, GENERATOR, GENERATOR, reply)
    run["chosen"] = reply["chosen"]
    if FIRST_USER in run.get("started", {}):
        run["gaps"] = reply["items"]
        run["done"] = f"{GENERATOR} answered {counted(len(run['back']), 'gap')}."
    else:
        run["done"] = f"{GENERATOR} made {', '.join(run['work'])}."
    due(run, FIRST_USER, prompts.reader(run), prompts.remade(run))
    return role(run, "")


def first_read(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Takes the first user's reading: an item has its Good where the first user gave one; a gap
    the generator held outside the purpose and the first user still stops at is a question of the
    purpose at once, the items stopped at made again once it is answered; otherwise the generator
    is sent each item stopped at, as the first user gave it, while the round may send them back;
    otherwise the round ends."""
    goods = [i for i in reply["items"] if good(i)]
    stops = [i for i in reply["items"] if not good(i)]
    run["done"] = (
        f"{FIRST_USER} found the Good of {len(goods)} of {counted(len(run['items']), 'item')}."
    )
    outside = {forms.key_of(g): g["outside"] for g in run.pop("gaps", []) if "outside" in g}
    differ = [
        dict(s, outside=outside[forms.key_of(s)]) for s in stops if forms.key_of(s) in outside
    ]
    if differ:
        return to_word(run, differ, stops, "differ")
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
    return to_word(run, lacking, lacking, "left")


def to_word(
    run: dict[str, Any], asked: list[dict[str, Any]], back: list[dict[str, Any]], source: str
) -> dict[str, Any]:
    """The items to word a question for shown, told with the reading before; the items to make
    again once answered kept, and the source, the rounds spent or the two roles differing, which
    says where the run goes on."""
    run.update(left=asked, back=back, left_from=source, stage="left")
    line = said(run)
    state.save(run)
    return dict(left_view(run), line=line)


def next_round(run: dict[str, Any], lacking: list[dict[str, Any]]) -> dict[str, Any]:
    """The next round: the generator and the first user started anew, counting anew, the generator
    given each item without Good with what was found lacking."""
    run["round"] += 1
    for anew_count in ("started", "sent"):
        run.pop(anew_count, None)
    return generate(run, lacking)


def left_asked(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Takes the orchestrator's question for each item left, two rounds left without Good or a gap
    the two roles differ on, and has the run ask them at once."""
    left = [forms.named(i) for i in run["left"]]
    said = forms.check(text, left, prompts.absolute(run["work"]), forms.LEFT, run["each"])
    if said:
        raise call.Stop(
            "turn: the questions are not filled:\n"
            + "\n".join(said)
            + f"\nrun `turn.py next {run['call']['result']}` again with the questions filled"
        )
    run.pop("left")
    return asking(run, run.pop("left_from"), UP, json.loads(forms.unfenced(text)))


def finished(run: dict[str, Any], goods: list[dict[str, Any]]) -> dict[str, Any]:
    """Once every item has its Good, writes the result and has the run return: where the work is,
    each item's Good as the first user gave it, in the checklists' order, and each choice the work
    rests on, as the generator's last claim named it."""
    found = {forms.key_of(g): g for g in goods}
    items = [found[forms.key_of(i)] for i in run["items"]]
    made = {"work": run["work"], "items": items, "chosen": run["chosen"]}
    state.write(run["call"]["result"], made)
    run["stage"] = "returned"
    state.save(run)
    return returning(run, "")


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


def left_view(run: dict[str, Any]) -> dict[str, Any]:
    """The items left, as the first user last gave them, each the generator held outside the
    purpose with its reason."""
    return {"left": run["left"]}


# What the run takes at each stage.
STAGES = {
    "ask": asking_now,
    "asked": answered,
    "anew": anew,
    "left": leaving,
    "role": role,
    "returned": returning,
}
# What the orchestrator is shown at each stage that waits on its judgment.
VIEWS = {"left": left_view}
# What is wrong with each role's reply.
PROBLEMS = {GENERATOR: claim_problems, FIRST_USER: reading_problems}
# What the run does after each role's reply.
REPLIED = {GENERATOR: made, FIRST_USER: first_read}
# Where the run goes on once the calling AI answers, by where the questions were asked.
GOES_ON = {GENERATOR: sent_answer, "left": left_answered, "differ": settled}

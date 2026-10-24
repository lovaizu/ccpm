"""The flow of a run: where the run stands, kept in its state beside the result, and the next move
the orchestrator makes, printed as the tool call itself; once the run returns, the result in the
form the calling AI reads."""

from __future__ import annotations

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
LEARNER = "turn:learner"
UP = "turn:up"
# The roles kept started through their round, each sent what comes next by message, so each works
# on with what it has already read.
KEPT = (GENERATOR, FIRST_USER)
# A reading that does not settle is bounded: the first user sends back three times a round.
SENDS = 3
# Rounds that do not settle are bounded too: one more round may run after the first, so an item two
# rounds leave without Good becomes a question, and the rounds count anew from its answer; the run
# keeps how many more rounds may run.
MORE = 1
# What the orchestrator judges, shown again whenever it asks.
SHOWN = ("check", "goods", "left")
# A messaged role's reply is waited for a second at a time, within the shell's two minutes.
WAIT = 100
# Where SendMessage reaches the main conversation, which alone talks with the user.
MAIN = "main"
# What each role is told of its run, as the line the calling AI is told.
DOES = {
    GENERATOR: "make the work to give every item its Good, and run what it gives as the receiver"
    " would",
    FIRST_USER: "use the work in the receiver's place and give each item's Good",
    LEARNER: "learn from every agent's record what fell short in the run and why",
}
# What the orchestrator is told it will judge, as the line the calling AI is told, by what waits on
# its judgment.
JUDGES = {
    "check": "check that the CCS gives every item its Good",
    "ask": "ask what only the user can decide",
    "goods": "check that each Good the first user found holds, running what it says",
    "left": "word a question for each item two rounds left without Good",
    "returned": "return the result",
}
# What a role kept started is told when it is sent more, by what the message holds first.
AGAIN = {
    "sent_back": "make the work again for each item the first user found no Good for",
    "answers": "go on with the calling AI's answer",
    "remade": "read the work made again for every item",
}
FORMS = {GENERATOR: forms.CLAIM, FIRST_USER: forms.FIRST_READING, LEARNER: forms.LEARNT}
USAGE = (
    "usage: turn.py start '<call JSON>'\n"
    "       turn.py next <result> [< <your check or questions as JSON, the answer as it came,"
    " or the agent ID as JSON>]\n"
    "       turn.py next <result> <page>\n"
    "       turn.py questions <result>\n"
    "       turn.py parts <result>"
)


def main(argv: list[str], stdin: IO[str]) -> int:
    """What turn.py runs: the call checked and the run started or gone on with, each step's outcome
    taken, giving the next move, what the orchestrator judges, or the result written; the questions
    the run asks now, and the parts of the work. Prints what comes next and gives 0, or prints what
    was wrong and gives 1."""
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


def without_run_files(paths: list[str], result: str, apart: tuple[str, ...] = ()) -> list[str]:
    """The paths, in their order, without the run's own files: the result, and each file beside it
    whose name begins with the result's name and a dot, as every file the run keeps is named; and
    without each file kept `apart`, as the CCS is from the first user. A path that is one of them
    is left out, and a folder holding the result's folder or a file kept apart is given as its
    entries, sorted, the one on the way opened the same way: a role's lane lets it read anything
    under a folder it is given, and the first user is not to read the generator's reply nor the
    CCS. A path inside one of them, such as a record shown to the learner, is left out too; a path
    met again, as a checklist the CCS also names, is given once."""
    folder = os.path.realpath(os.path.dirname(result) or ".")
    name = os.path.basename(result)
    kept_apart = {os.path.realpath(p) for p in apart}
    # The folders a folder given is opened on the way to.
    inside = {folder} | {os.path.dirname(p) for p in kept_apart}

    def ours(path: str) -> bool:
        # The entry of the result's folder the path is at or in; `..` for a path outside it.
        entry = os.path.relpath(os.path.realpath(path), folder).split(os.sep)[0]
        return entry == name or entry.startswith(name + ".") or os.path.realpath(path) in kept_apart

    def opened(path: str) -> list[str]:
        real = os.path.realpath(path)
        if not any(real == f or f.startswith(real + os.sep) for f in inside):
            return [path]
        entries = [os.path.normpath(os.path.join(path, e)) for e in sorted(os.listdir(path))]
        return [p for e in entries if not ours(e) for p in opened(e)]

    return list(dict.fromkeys(p for path in paths if not ours(path) for p in opened(path)))


def whole(paths: list[str]) -> list[str]:
    """The paths as whole paths in the folder the call was made from, where the flow runs: a role's
    commands and hooks run from the session's working folder, which the calling AI may move with
    `cd`."""
    return [os.path.abspath(p) for p in paths]


def start(text: str) -> dict[str, Any]:
    """Starts the run the call asks for, or goes on with the run its result names from the move it
    was last at; gives, for the run's lanes, where the result goes and what the orchestrator reads
    for its check: the CCS and every file it names but the work."""
    asked = call.parse(text)
    result = asked.get("result")
    kept = running(result) if isinstance(result, str) else None
    if kept is None or not isinstance(result, str):
        # The paths of the call mean the folder it is made from, kept for every step after.
        run = begun(asked, os.getcwd())
    elif kept["call"] != asked:
        raise call.Stop(
            f"turn: a run of another call is kept at {state_path(result)}; call turn with that"
            " call to go on with it, or with another result"
        )
    elif laid_out_anew(kept):
        run = again(kept)
    else:
        run = resumed(kept)
    save(run)
    return {"result": os.path.abspath(run["call"]["result"]), "given": checked_given(run)}


def checked_given(run: dict[str, Any]) -> list[str]:
    """What the orchestrator reads for its check: the CCS and every file it names but the work,
    as the CCS now names them."""
    read = [p for p in run["given"] if p not in run["work"]]
    return whole(without_run_files(read, run["call"]["result"]))


def begun(asked: dict[str, Any], root: str) -> dict[str, Any]:
    """The run the call asks for, from the folder it is made from, waiting on the orchestrator's
    check of every item, in its first round."""
    run = call.check(asked)
    run["root"] = root
    run["check"] = run["items"]
    run["round"] = 1
    run["more"] = MORE
    return run


def resumed(run: dict[str, Any]) -> dict[str, Any]:
    """The run gone on with by an orchestrator started anew: the agents of the run before are gone
    with it, so the role due is started anew with what it was given and what was sent to it since,
    and is told again; a question asked is asked again, as the orchestrator that asked it is gone."""
    step = run.get("next")
    if step:
        prompt = dict(run.get("prompts", {}).get(step["agent"], step["prompt"]))
        since = run.get("since", {}).get(step["agent"], [])
        if "to" in step:
            # A message moved is among those sent since; one due is not yet.
            prompt["since"] = since + ([] if step.get("moved") else [step["message"]])
        run["next"] = {"agent": step["agent"], "prompt": prompt}
    if "asked" in run:
        run["ask"] = run.pop("asked")
    # A judgment due is told again, as the role due is.
    for gone in ("started", "since", "prompts", "told"):
        run.pop(gone, None)
    return run


def each(run: dict[str, Any]) -> list[tuple[str, str]]:
    """The items asked of each part of the work, by their checklist and ID."""
    return [forms.key_of(i) for i in run["each"]]


def generate(run: dict[str, Any], sent_back: list, sent: Any = None) -> dict[str, Any]:
    """Has the generator make the work, started with what it is given, or, kept started, sent what
    is sent; the items sent back are kept, so a generator started anew is given them."""
    run["back"] = sent_back
    return ask(run, GENERATOR, generator_given(run, sent_back), sent)


def generator_given(run: dict[str, Any], sent_back: list) -> dict[str, Any]:
    """What the generator is given: the files it makes the work from, the work, the checklists,
    each item sent back with what was found lacking, every answer the calling AI gave, and where it
    replies."""
    return {
        "given": whole(without_run_files(run["given"], run["call"]["result"])),
        "work": whole(run["work"]),
        "checklists": whole(run["checklist"]),
        "sent_back": sent_back,
        "answers": run.get("answers", []),
        "reply": reply_path(run["call"]["result"], GENERATOR),
    }


def reader_given(run: dict[str, Any]) -> dict[str, Any]:
    """What the first user is given: what the receiver has with the work, the checklists, the
    receiver and their use, the parts of the work, and where it replies; not the CCS nor the
    generator's reply, as a reader shown the maker's claim finds the Good it was told to find."""
    return {
        "given": whole(
            without_run_files(run["shown"], run["call"]["result"], apart=(run["call"]["ccs"],))
        ),
        "work": whole(run["work"]),
        "checklists": whole(run["checklist"]),
        "receiver": run["receiver"],
        "use": run["use"],
        "parts": forms.parts(run["work"]),
        "reply": reply_path(run["call"]["result"], FIRST_USER),
    }


def ask(run: dict[str, Any], agent: str, prompt: dict[str, Any], sent: Any = None) -> dict:
    """Keeps the run with the role due, to be told, then started with the prompt, or, once it is
    kept started, sent what is sent; and gives the line the calling AI is told."""
    to = run.get("started", {}).get(agent)
    if to and sent:
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
    return telling(run, agent, AGAIN[next(iter(step["message"]))] if "to" in step else DOES[agent])


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
    line += f", for {len(run['items'])} items, round {run['round']}."
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
    """The questions the run asks the calling AI now, each with the items it settles."""
    asked = going(result).get("asked")
    if asked is None:
        raise call.Stop(f"turn: the run asks no question now; run `turn.py next {result}`")
    return {"questions": asked["questions"]}


def parts(result: str) -> dict[str, list[str]]:
    """The parts of the run's work as it stands, each as its lines."""
    return {"parts": forms.parts(going(result)["work"])}


def view(result: str) -> dict[str, Any]:
    """What the orchestrator is to judge now: the items to check, the Goods to check, or the items
    left without Good to word a question for."""
    run = going(result)
    for step in SHOWN:
        if step in run:
            return judged(run, step)
    raise call.Stop(
        f"turn: nothing waits on your judgment to show in pages; run `turn.py next {result}`"
    )


def judged(run: dict[str, Any], step: str) -> dict[str, Any]:
    """What the orchestrator is to judge at the step, the same on every page: the check with what to
    read for it as the CCS now names it, as an answer may name more."""
    shown = {step: run[step]}
    if step in ("check",):
        shown["given"] = checked_given(run)
    return shown


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
    """Takes what the run waits on, the orchestrator's check, its questions, the calling AI's
    answer or a role's reply, and gives what the orchestrator does next."""
    run = going(result)
    # What waits on the orchestrator's judgment is told first, before it is shown.
    waits = next((j for j in JUDGES if j in run), None)
    if waits and not run.get("told") and not text.strip():
        return judge(run, waits)
    # Asked with nothing, what the orchestrator is to judge is shown again, so it can always see it
    # whole.
    if "check" in run:
        return checked(run, text) if text.strip() else judged(run, "check")
    if "ask" in run:
        run["asked"] = run.pop("ask")
        del run["told"]
        save(run)
        return {"asked": run["call"]["result"]}
    if "asked" in run:
        return answered(run, text)
    if "returned" in run:
        return returned(run)
    if "goods" in run:
        return goods_checked(run, text) if text.strip() else judged(run, "goods")
    if "left" in run:
        return left_asked(run, text) if text.strip() else judged(run, "left")
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
    # Each role's record is kept for the learner, which looks for what fell short in what the roles
    # did.
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


def checked(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the orchestrator's check: with an item the CCS cannot give its Good, the run asks
    the calling AI at once, as no work made without the answer can give it; otherwise the
    generator makes the work."""
    said = forms.check(text, run["items"], run["work"], forms.CHECK)
    if said:
        raise call.Stop("turn: the check is not filled:\n" + "\n".join(said))
    found = json.loads(forms.unfenced(text))
    del run["check"]
    if found["questions"]:
        return asking(run, "check", UP, found)
    run["done"] = f"{UP} found in the CCS what gives the Good of {len(run['items'])} items."
    return generate(run, [])


def asking(run: dict[str, Any], source: str, who: str, found: dict[str, Any]) -> dict[str, Any]:
    """Has the run ask the calling AI the questions found, each with the items it settles, as soon
    as they are met; the source, the check, the generator or the items left, says where the run
    goes on once answered."""
    run["ask"] = {"from": source, "questions": waited(found["items"], found["questions"])}
    waiting = len([i for i in found["items"] if "question" in i])
    run["done"] = (
        f"{who} found {waiting} of {len(run['items'])} items waiting on the user's answer."
    )
    return judge(run, "ask")


def answered(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Keeps the calling AI's answer, as it came, with the questions it answers, and goes on where
    they were asked."""
    if not text.strip():
        raise call.Stop(
            "turn: the run waits on the calling AI's answer; run `turn.py next"
            f" {run['call']['result']}` with the answer, as it came, as its input"
        )
    asked = run.pop("asked")
    answer = {"questions": asked["questions"], "answer": text.strip()}
    run.setdefault("answers", []).append(answer)
    run["done"] = "The calling AI answered."
    # An answer kept in the CCS may lay the whole work out anew, such as a file added to it.
    if laid_out_anew(run):
        return checked_again(run)
    return GOES_ON[asked["from"]](run)


def laid_out_anew(run: dict[str, Any]) -> bool:
    """Whether the CCS now gives the run other than it was begun with: other files of the work,
    checklists, items, receiver, use or what the receiver has."""
    anew = call.check(run["call"])
    return any(anew[k] != run[k] for k in anew)


def again(run: dict[str, Any]) -> dict[str, Any]:
    """The run begun again on the CCS as it is now, waiting on the check, with every answer the
    calling AI gave and the record of every role started so far."""
    anew = begun(run["call"], run["root"])
    anew.update({k: run[k] for k in ("answers", "records") if k in run})
    return anew


def checked_again(run: dict[str, Any]) -> dict[str, Any]:
    """The check made again on the CCS the calling AI kept the answer in, as an answer may also
    change how the whole work is laid out."""
    anew = again(run)
    anew["done"] = run["done"]
    return judge(anew, "check")


def sent_answer(run: dict[str, Any]) -> dict[str, Any]:
    """The generator that asked is sent the answer, and goes on making the work."""
    answer = run["answers"][-1]
    message = {"answers": [answer], "reply": reply_path(run["call"]["result"], GENERATOR)}
    return generate(run, run["back"], message)


def left_answered(run: dict[str, Any]) -> dict[str, Any]:
    """The items two rounds left without Good are made again with the answer, the rounds counted
    anew from it."""
    run["more"] = MORE
    return next_round(run, run["back"])


def made(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Has the run ask the generator's questions at once, before any reading rests on them;
    otherwise has the first user use the work made, with no reading between."""
    if reply["questions"]:
        return asking(run, GENERATOR, GENERATOR, reply)
    run["done"] = f"{GENERATOR} made {', '.join(run['work'])}."
    # The parts are given anew, as a remake may add or take away a section.
    remade = {
        "remade": whole(run["work"]),
        "parts": forms.parts(run["work"]),
        "reply": reply_path(run["call"]["result"], FIRST_USER),
    }
    return ask(run, FIRST_USER, reader_given(run), remade)


def first_read(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Keeps the first user's reading; sends the generator each item it stopped at, as the first
    user gave it, while the round may send them back; otherwise the orchestrator checks each Good
    the first user gave, or, with none given, the round ends."""
    run["read"] = reply["items"]
    goods = [i for i in reply["items"] if good(i)]
    stops = [i for i in reply["items"] if not good(i)]
    run["done"] = f"{FIRST_USER} found the Good of {len(goods)} of {len(run['items'])} items."
    if stops and sending(run):
        back = {"sent_back": stops, "reply": reply_path(run["call"]["result"], GENERATOR)}
        return generate(run, stops, back)
    if goods:
        run["goods"] = goods
        return judge(run, "goods")
    return ended(run, [], run.pop("read"))


def goods_checked(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the orchestrator's check of each Good the first user gave: an item has its Good
    only where the first user gave one and the check says it holds; every other item is without
    Good, with the stop the first user gave or the check found."""
    goods = run["goods"]
    said = forms.check(text, [named(g) for g in goods], run["work"], forms.HELD)
    if said:
        raise call.Stop("turn: the check of the Goods is not filled:\n" + "\n".join(said))
    found = {forms.key_of(i): i for i in json.loads(forms.unfenced(text))["items"]}
    del run["goods"]
    kept = [g for g in goods if "holds" in found[forms.key_of(g)]]
    lacking = [found.get(forms.key_of(i), i) for i in run.pop("read") if i not in kept]
    run["done"] = f"{UP} found {len(kept)} of {len(goods)} Goods hold."
    return ended(run, kept, lacking)


def ended(run: dict[str, Any], goods: list, lacking: list) -> dict[str, Any]:
    """The round ended: with every item's Good, the learner learns from the run; otherwise the
    items without Good are made again in the next round, or, once the rounds are spent, wait on a
    question the orchestrator words."""
    if not lacking:
        return learn(run, goods)
    if run["more"]:
        run["more"] -= 1
        return next_round(run, lacking)
    run["left"] = lacking
    return judge(run, "left")


def next_round(run: dict[str, Any], lacking: list) -> dict[str, Any]:
    """The next round: the generator and the first user started anew, counting anew, the generator
    given each item without Good with what was found lacking."""
    run["round"] += 1
    for anew in ("started", "sent"):
        run.pop(anew, None)
    return generate(run, lacking)


def left_asked(run: dict[str, Any], text: str) -> dict[str, Any]:
    """Records the orchestrator's question for each item two rounds left without Good, and has the
    run ask them at once."""
    left = run["left"]
    said = forms.check(text, [named(i) for i in left], run["work"], forms.LEFT)
    if said:
        raise call.Stop("turn: the questions are not filled:\n" + "\n".join(said))
    run["back"] = run.pop("left")
    return asking(run, "left", UP, json.loads(forms.unfenced(text)))


def learn(run: dict[str, Any], goods: list) -> dict[str, Any]:
    """Once the run is done, the learner learns from every record of the run what fell short and
    why, each record shown as text it reads whole; every item's Good is kept for the result."""
    found = {forms.key_of(g): g for g in goods}
    run["held"] = [found[forms.key_of(i)] for i in run["items"]]
    result = run["call"]["result"]
    kept = [p for p in (records.find(i) for i in run["records"]) if p]
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
    return ask(run, LEARNER, {"given": texts, "reply": reply_path(result, LEARNER)})


def taught(run: dict[str, Any], reply: dict[str, Any]) -> dict[str, Any]:
    """Writes the result and has the run return: where the work is, each item's Good as the first
    user gave it, and the learner's lessons with what it checked, for the calling AI to put to the
    user; each ground names its record by its path, as the texts the learner read by number are
    removed once the run returns."""
    lessons = [
        dict(n, grounds=[dict(g, record=run["learnt"][g["record"] - 1]) for g in n["grounds"]])
        for n in reply["lessons"]
    ]
    write(
        run["call"]["result"],
        {
            "work": run["work"],
            "items": run["held"],
            "lessons": lessons,
            "checked": reply["checked"],
        },
    )
    run["done"] = f"{LEARNER} gave {len(reply['lessons'])} lessons from the run."
    run["returned"] = run["call"]["result"]
    return judge(run, "returned")


def returned(run: dict[str, Any]) -> dict[str, Any]:
    """The run returned, once told: what it kept beside the result is removed."""
    result = run["returned"]
    os.remove(state_path(result))
    for agent in FORMS:
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


def good(item: dict[str, Any]) -> bool:
    """Whether the item is judged Good: with one Good, or with a Good for every part."""
    return "good" in item or "parts" in item


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
REPLIED = {GENERATOR: made, FIRST_USER: first_read, LEARNER: taught}
# Where the run goes on once the calling AI answers, by where the questions were asked.
GOES_ON = {"check": checked_again, GENERATOR: sent_answer, "left": left_answered}

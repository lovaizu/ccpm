"""The ux trials of Pin's UX, as dev/pin/architecture.md's ux says: an AI on Opus stands in for the
person, given an intent written before the run, intent_o1.md or intent_o2.md beside this file,
which no part of Pin is shown. The subject is the notes app in notes/ beside this file, a repository
with several scripts that read `notes list`, and a plan of about ten points. The intent brings out
the frequent cases: a fact found and confirmed, a fact corrected, a decision of the person's, a
decision left to Pin, a point that an answer raises, and a change at the design.

- O1: the person types `/pin:down notes list should give JSON as well` in an interactive session,
  and the main conversation is the go-between.
- O2: the person types `/maker:json notes list should give JSON as well`; the plugin maker beside
  this file stands in for a maker AI's plugin. Its subagent maker:maker hands over the goal, three
  questions and two points it settled, takes pin:down as the go-between, and builds the JSON output
  on the design it gets back.

Each run copies Pin, and maker for O2, and makes the notes app a git repository of its own, outside
any ccpm clone. Every Claude Code it starts runs on Opus with `--permission-mode
bypassPermissions` and a configuration folder of its own, as trials/trying.py starts it. The
session runs in an interactive terminal, as Pin runs where Claude Code starts the one who started
a subagent again once it ends.

The trial measures each key result of the UX from the records of the session, the stand-in's view
of each message and the design tree, and prints them:

- KR1.1: of the intent's points and the points put to the person that are not among them, the share
  that went wrong: a point the confirmed design does not hold, holds open or holds otherwise than
  the intent, a point of the person's settled without them, a point put to them that was not
  theirs or was asked again, and an answer that did not reach the pinner word for word, so it was
  settled apart from Pin.
- KR1.2: the seconds from the request to the stop at which the stand-in confirmed the design.
- KR2.1 (O2): of the designs the maker AI got back, the share that went wrong: a point it settled
  changed or asked again, a question it gave with no decision under it, a Reply of the pinner's
  that did not reach the person as given or an answer that did not reach the pinner word for word,
  and a write of the maker AI to the design tree once it had handed it over.
- KR2.2 (O2): the seconds from the maker AI's start of the pinner to the pinner's `done`.

A run counts only where each frequent case came up. It passes where nothing went wrong in KR1.1,
and, for O2, nothing in KR2.1 and `notes.py list --json` gives one array whose objects hold a
path. A trial passes where every run passes, three of three by default, as
dev/plugin-best-practice.md's Results that vary from run to run says. The UX gives no key result a
target, so each measure is set against the last trial's.

Run as `python3 dev/pin/tests/ux/trial.py [o1|o2|both] [runs]`, both and three by default. It
prints the folder of each run, where the session's records, the stand-in's view of each message,
`turns.json`, and the measures, `measures.json`, are kept. `python3 dev/pin/tests/ux/trial.py
--judge <folder of a run> o1|o2` judges a kept run again from its records, to check the judge on a
kept record before trusting it."""

from __future__ import annotations

import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "dev", "lane", "trials"), os.path.dirname(HERE)]

import helpers
import trying

record = trying.record
MAKER = os.path.join(HERE, "maker")
REQUESTS = {
    "o1": "/pin:down notes list should give JSON as well",
    "o2": "/maker:json notes list should give JSON as well",
}
# The intent's points that are the person's to decide, by number, which the design must hold as
# settled by them; and, for O2, those the maker AI settled, which it must hold as settled by maker.
THEIRS = {"o1": {1, 2, 3, 7, 8}, "o2": {2, 3, 7, 9}}
MAKERS = {"o1": set(), "o2": {1, 8}}
# The maker AI's hand-over: where it lies, and the IDs of the points and questions it gives.
HANDED = os.path.join(".maker", "notes-json", "design-tree.md")
HANDED_POINTS = ("M1", "M2")
HANDED_QUESTIONS = ("Q1", "Q2", "Q3")
# The most messages put to the person before a run is stopped as one that does not end.
TURNS = 30
# What the stand-in gives of each message, beside its answer.
KEYS = (
    """- "answer": your answer to the message, as you would write it;
"""
    + trying.POINTS
    + """
- "about": the number of the point of what you want above that the message is about, or 0 where it
  is about none of them, or puts nothing to you;
- "asks_fact": true where it asks you something about the repository that the AI could read for
  itself, rather than showing you what it found; otherwise false;
- "asks_settled": true where it asks you again something you are said above to have settled
  already, or that you already answered in this conversation; otherwise false;
- "asks_not_theirs": true where it asks you to decide something that follows from what you want,
  the facts and what you said, so the AI could have settled it itself; otherwise false;
- "shows_fact": true where it shows you a fact it found, for you to confirm; otherwise false;
- "corrects_fact": true where your answer corrects a fact it showed you; otherwise false;
- "puts_decision": true where it asks you to make one decision or to approve one proposal, the
  goal included; otherwise false;
- "leaves_to_ai": true where your answer says the AI may decide it; otherwise false;
- "raises_point": true where your answer raises a point the message did not ask; otherwise false;
- "confirms_design": true where it shows you the whole design and asks whether you understand it
  the same way; otherwise false;
- "changes_design": true where it shows you the whole design and your answer asks for something in
  it to change; otherwise false;
- "finished": true where the message asks you nothing and says the work or the planning is done;
  otherwise false."""
)
FINDS = trying.finds(
    "You stand in for the person an AI is planning a change with. Here is who you are and what you"
    " truly want; the AI cannot see it:",
    KEYS,
)
# The frequent cases each run must bring out to count, each by the stand-in's key that shows it.
CASES = {
    "shows_fact": "no fact was shown to confirm",
    "corrects_fact": "no fact was corrected",
    "puts_decision": "no decision was put to the person",
    "leaves_to_ai": "no decision was left to Pin",
    "raises_point": "no answer raised a point",
    "changes_design": "the design was not changed",
}
JUDGES = """An AI has written a design tree for a plan. The person whose plan it is wanted the
points below. For each point, judge whether a decision of the tree, or the goal, holds it as the
person wants it, and give the settled_by of the decision that holds it.

The points:
{wants}

The design tree:
{tree}

Give only one JSON object, with no other text: {{"points": [{{"point": <its number>, "held": true
or false, "settled_by": the settled_by of the decision that holds it, or null}}]}}, one entry for
each point, in order."""


def intent(objective: str) -> str:
    """The intent of the objective, as written before the run."""
    with open(os.path.join(HERE, f"intent_{objective}.md"), encoding="utf-8") as f:
        return f.read()


def wants(objective: str) -> list[str]:
    """The intent's points, in order: each numbered item of its list of what the person wants."""
    found = re.findall(r"^(\d+)\. (.*(?:\n   .*)*)", intent(objective), re.MULTILINE)
    return [" ".join(text.split()) for _, text in found]


def run(objective: str, number: int) -> bool:
    """One run of the trial of the objective; prints what it found and measured, and gives whether
    it counted and passed."""
    place = trying.folder("pin", f"trial-{objective}-{number}")
    repo = os.path.join(place, "notes")
    trying.committed(repo, helpers.NOTES)
    plugins = [os.path.join(place, "plugins", "pin")]
    shutil.copytree(helpers.PIN, plugins[0])
    if objective == "o2":
        plugins.append(os.path.join(place, "plugins", "maker"))
        shutil.copytree(MAKER, plugins[1])
    told = intent(objective)
    alone = os.path.join(place, "person")
    os.makedirs(alone)
    turns: list[dict[str, Any]] = []
    said: list[str] = []
    started = time.monotonic()

    def answer(message: str) -> str | None:
        """The stand-in's answer to the main conversation's last message; None once the work or the
        planning is done, or once the design confirmed has been answered."""
        if len(turns) >= TURNS:
            raise SystemExit(f"the conversation did not end in {TURNS} messages")
        heard = trying.heard(FINDS, told, said, message, alone)
        heard.update(message=message, at=time.monotonic() - started)
        turns.append(heard)
        print(f"  AI: {message[:300]!r}\n  person: {str(heard.get('answer'))[:200]!r}", flush=True)
        # O1 ends at the reply to the design confirmed; O2 goes on until the maker AI is done.
        confirmed = [t for t in turns[:-1] if t.get("confirms_design")]
        settled = bool(confirmed) and not confirmed[-1].get("changes_design")
        if heard.get("finished") or (objective == "o1" and settled):
            return None
        said.extend([f"AI: {message}", f"You: {heard['answer']}"])
        heard["sent"] = True
        return str(heard["answer"])

    session = trying.interactive(
        REQUESTS[objective],
        plugins,
        repo,
        place,
        wait=90,
        answer=answer,
        permit=lambda screen: trying.permitted(told, screen, alone),
    )["session_id"]
    with open(os.path.join(place, "turns.json"), "w", encoding="utf-8") as f:
        json.dump({"session": session, "turns": turns}, f, indent=1)
    return judged(place, objective)


def judged(place: str, objective: str) -> bool:
    """Judges the run kept in its folder from its records, the stand-in's view of each message and
    its design tree; prints and keeps the measures, and gives whether it counted and passed."""
    with open(os.path.join(place, "turns.json"), encoding="utf-8") as f:
        kept = json.load(f)
    turns: list[dict[str, Any]] = kept["turns"]
    repo = os.path.join(place, "notes")
    files = records(kept["session"])
    path = design_tree(repo, objective)
    untried = [why for key, why in CASES.items() if not any(t.get(key) for t in turns)]
    wrong = kr1_1(objective, turns, path, files, place)
    points = len(wants(objective)) + sum(
        1 for t in turns if int(t.get("points") or 0) and not t.get("about")
    )
    confirmed = [t["at"] for t in turns if t.get("confirms_design") and not t.get("changes_design")]
    measures: dict[str, Any] = {
        "KR1.1": f"{len(wrong)} of {points}",
        "KR1.1 wrong": wrong,
        "KR1.2": round(confirmed[-1]) if confirmed else None,
    }
    if objective == "o2":
        designs, wrong_designs, lead = kr2(turns, path, files, repo)
        measures.update(
            {"KR2.1": f"{len(wrong_designs)} of {designs}", "KR2.1 wrong": wrong_designs}
        )
        measures["KR2.2"] = lead
        wrong += wrong_designs + built(repo)
    else:
        wrong += held(path)
    with open(os.path.join(place, "measures.json"), "w", encoding="utf-8") as f:
        json.dump(measures, f, indent=1)
    print("  measures:", json.dumps(measures, ensure_ascii=False))
    return trying.verdict(untried, wrong)


def records(session: str) -> dict[str, list[dict[str, Any]]]:
    """The entries of the session's records, by who kept them: the main conversation, as `main`,
    and each agent it started by its type, such as `pin:pinner`, the runs of one type joined in
    order."""
    found: dict[str, list[dict[str, Any]]] = {"main": []}
    for path in glob.glob(record.conversation(session)):
        found["main"] += record.read(path) or []
    for path in sorted(trying.agents(session)):
        found.setdefault(record.agent_type(path), []).extend(record.read(path) or [])
    return found


def design_tree(repo: str, objective: str) -> str:
    """The path of the design tree the run settled: the maker AI's hand-over for O2, else the one
    file in `.pin/`, or "" where there is not one alone."""
    if objective == "o2":
        return os.path.join(repo, HANDED)
    found = glob.glob(os.path.join(repo, ".pin", "*", "design-tree.md"))
    return found[0] if len(found) == 1 else ""


def tree_of(path: str) -> dict[str, Any]:
    """The design tree at the path, as Pin's tree.py reads it; none where it cannot be read."""
    try:
        return helpers.tree.load(path)
    except helpers.tree.Unreadable:
        return {}


def kr1_1(
    objective: str,
    turns: list[dict[str, Any]],
    path: str,
    files: dict[str, list[dict[str, Any]]],
    place: str,
) -> list[str]:
    """Each point that went wrong in any of the UX's four ways of KR1.1."""
    wrong = []
    tree = tree_of(path)
    asked = trying.stand_in(
        JUDGES.format(
            wants="\n".join(f"{n}. {w}" for n, w in enumerate(wants(objective), 1)),
            tree=json.dumps(tree, ensure_ascii=False),
        ),
        os.path.join(place, "person"),
    )
    for n, point in enumerate(asked.get("points", []), 1):
        by = point.get("settled_by")
        if not point.get("held"):
            wrong.append(f"the design does not hold point {n} as the person means it")
        elif n in THEIRS[objective] and by != "user":
            wrong.append(f"point {n} is the person's, but settled by {by}")
        elif n in MAKERS[objective] and by != "maker":
            wrong.append(f"point {n} was settled by the maker AI, but is held as settled by {by}")
    for n, t in enumerate(turns, 1):
        if t.get("asks_fact") or t.get("asks_not_theirs"):
            wrong.append(f"message {n} put a point to the person that was not theirs")
        if t.get("asks_settled"):
            wrong.append(f"message {n} asked the person again what was settled")
    heard = "\n".join(said for e in files.get("pin:pinner", []) for said in record.message(e))
    for n, t in enumerate(turns, 1):
        if t.get("sent") and str(t.get("answer")) not in heard:
            wrong.append(f"answer {n} did not reach the pinner word for word")
    return wrong


def replies(entries: list[dict[str, Any]]) -> list[str]:
    """Each reply that ended a turn, in the entries of a record, as its text."""
    return [d.given[record.SAID] for d in record.done(entries, "") if d.tool == record.REPLY]


def at(entries: list[dict[str, Any]], tool: str, words: str) -> list[datetime.datetime]:
    """When each use of the tool whose input holds the words was made, in a record's entries."""
    return [
        datetime.datetime.fromisoformat(str(entries[n]["timestamp"]).replace("Z", "+00:00"))
        for n, d in record.done_at(entries, "")
        if d.tool == tool and words in json.dumps(d.given)
    ]


def kr2(
    turns: list[dict[str, Any]], path: str, files: dict[str, list[dict[str, Any]]], repo: str
) -> tuple[int, list[str], int | None]:
    """For O2: the designs the maker AI got back, each way they went wrong of KR2.1, and the seconds
    from its first start of the pinner to the pinner's first `done`, KR2.2."""
    maker, pinner = files.get("maker:maker", []), files.get("pin:pinner", [])
    done = at(pinner, "Bash", "result.py pinner done")
    starts = at(maker, "Agent", "pin:pinner")
    wrong = []
    tree = tree_of(path)
    handed = {d["id"]: d for d in tree.get("decisions", []) if d.get("id") in HANDED_POINTS}
    for point in HANDED_POINTS:
        if handed.get(point, {}).get("settled_by") != "maker":
            wrong.append(f"the maker AI's point {point} was changed")
    served = {q for d in tree.get("decisions", []) for q in d.get("contributes_to", [])}
    for question in HANDED_QUESTIONS:
        if question not in served:
            wrong.append(f"the maker AI's question {question} has no decision under it")
    if any(t.get("asks_settled") for t in turns):
        wrong.append("the person was asked again a point that was settled")
    passed = "\n".join(replies(maker))
    for reply in replies(pinner):
        if reply.strip() and reply.strip() not in passed:
            wrong.append(
                f"a Reply of the pinner's did not reach the person as given: {reply[:80]!r}"
            )
    first = starts[0] if starts else None
    for d_at in at(maker, "Write", HANDED) + at(maker, "Edit", HANDED):
        if first and d_at > first:
            wrong.append("the maker AI wrote the design tree after it handed it over")
    lead = round((done[0] - first).total_seconds()) if done and first else None
    return len(done), wrong, lead


def built(repo: str) -> list[str]:
    """What is wrong with the work the maker AI built: `notes.py list --json` gives one array of
    objects, each holding a path; nothing where it does."""
    done = subprocess.run(
        [sys.executable, "notes.py", "list", "--json"],
        capture_output=True,
        text=True,
        cwd=repo,
        check=False,
    )
    try:
        given = json.loads(done.stdout)
    except ValueError:
        return [f"notes.py list --json gave no JSON: {done.stdout[:200]!r} {done.stderr[:200]!r}"]
    if not isinstance(given, list) or not all(isinstance(o, dict) and "path" in o for o in given):
        return [f"notes.py list --json is not an array of objects with a path: {given!r:.200}"]
    return []


def held(path: str) -> list[str]:
    """That the design tree does not hold with no decision open, by check.py, where it does not."""
    if not path:
        return ["not one design tree in .pin/"]
    check = os.path.join(helpers.PIN, "scripts", "check.py")
    done = subprocess.run(
        [sys.executable, check, path], capture_output=True, text=True, check=False
    )
    if done.returncode != 0 or "No decision is open." not in done.stdout:
        return [f"the design tree does not hold with no decision open: {done.stdout[-200:]!r}"]
    return []


def main(argv: list[str]) -> None:
    """Runs the trials the command line names, or judges a kept run again; exits 0 where every run
    counted and passed."""
    if argv[:1] == ["--judge"]:
        sys.exit(0 if judged(argv[1], argv[2]) else 1)
    chosen = argv[0] if argv else "both"
    runs = int(argv[1]) if len(argv) > 1 else 3
    objectives = ["o1", "o2"] if chosen == "both" else [chosen]
    passed = [run(o, n) for o in objectives for n in range(1, runs + 1)]
    print(f"{sum(passed)} of {len(passed)} runs passed")
    sys.exit(0 if all(passed) else 1)


if __name__ == "__main__":
    main(sys.argv[1:])

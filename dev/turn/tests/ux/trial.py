"""The ux trials of Turn's UX, as dev/turn/architecture.md's ux says: an AI on Opus stands in for
the person, given an intent written before the run, one of the intent_*.md files beside this file,
which no part of Turn is shown. The subject is tidy in tidy/ beside this file, a repository of
several modules with its tests and its packaging and no README, which the architecture tests read
too. The trials bring out the frequent cases: the kind open and the kind named, a fact found and
confirmed, a decision of the person's, a decision left to Turn, a question not met and sent back,
and a reading round.

- readme, O1: the person types `/turn:up something that tells people what tidy does and how to
  use it`, which leaves the kind open; the main conversation is the starter.
- man-page, O1: the person types `/turn:up a man page for tidy`, a kind Turn has no best practice
  of, so the person approves its purpose and its questions first.
- o2, O2: the person types `/caller:readme`; the plugin caller beside this file stands in for a
  calling AI's plugin. Its subagent caller:caller hands Turn the kind, a goal and two settled
  points, and passes the README on.

Each run copies Turn and Pin, and caller for o2, and makes tidy a git repository of its own,
outside any ccpm clone. Every Claude Code it starts runs on Opus with `--permission-mode
bypassPermissions` and a configuration folder of its own, as trials/trying.py starts it; the
request is typed as a person types it, with nothing added. The session runs in an
interactive terminal, as Turn runs where Claude Code starts the one who started a subagent again
once it ends.

The trial measures each key result of the UX from the records of the session, the stand-in's view
of each message, the run's folder and the work, and prints them:

- KR1.1: of the works made, the share that went wrong in any of the UX's five ways: the person
  would change the work or send it back before using it, as the stand-in judges the work from its
  intent; the person was asked a point that was not theirs; the person would settle a point outside
  the run or make the work another way; the run stopped with no work handed back; and, for a kind
  new to Turn, the person changed a question of the kind after approving it.
- KR1.2: the seconds from the request to the work handed back.
- KR2.1 (o2): of the works the calling AI got back, the share that went wrong in any of the UX's
  four ways: a point the calling AI settled asked again, or held in the design otherwise than
  given; a message of Turn's the calling AI did not pass on as given; a write of the calling AI to
  the work; and no work back.
- KR2.2 (o2): the seconds from the calling AI's start of turn:up to the work handed back.

A run counts only where each frequent case of its trial came up. It passes where nothing went
wrong in KR1.1, and, for o2, nothing in KR2.1. A trial passes where every run passes, three of
three by default, as dev/plugin-best-practice.md's Results that vary from run to run says. The UX
gives no key result a target, so each measure is set against the last trial's.

Run as `python3 dev/turn/tests/ux/trial.py [readme|man-page|o2|all] [runs]`, all and three by
default. It prints the folder of each run, where the session's records, the stand-in's view of
each message, `turns.json`, and the measures, `measures.json`, are kept. `python3
dev/turn/tests/ux/trial.py --judge <folder of a run> readme|man-page|o2` judges a kept run again
from its records, to check the judge on a kept record before trusting it."""

from __future__ import annotations

import datetime
import glob
import json
import os
import shutil
import sys
import time
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path[:0] = [os.path.join(ROOT, "dev", "lane", "trials"), os.path.dirname(HERE)]

import helpers
import trying

record = trying.record
TRIALS = {
    "readme": (
        "/turn:up something that tells people what tidy does and how to use it",
        "intent_readme.md",
    ),
    "man-page": ("/turn:up a man page for tidy", "intent_man_page.md"),
    "o2": ("/caller:readme", "intent_o2.md"),
}
# The run's folder the calling AI names, and the points it settled, as caller.md hands them over.
CALLERS_RUN = os.path.join(".caller", "readme")
SETTLED = ("M1", "M2")
# The most messages put to the person before a run is stopped as one that does not end.
TURNS = 40
KEYS = (
    """- "answer": your answer to the message, as you would write it, or "" where it asks you
  nothing;
"""
    + trying.POINTS
    + """
- "asks_kind": true where it asks you what kind of thing to make; otherwise false;
- "asks_fact": true where the message asks you a thing about the repository that the AI could
  have read there itself; otherwise false;
- "asks_settled": true where the message asks you a thing the text above says you settled
  already, or one you answered before in this conversation; otherwise false;
- "asks_not_theirs": true where the message asks you to decide a thing that follows from your
  wants, the facts and your answers, which the AI could have settled; otherwise false;
- "shows_fact": true where the message shows you a thing it found, asking whether it is right;
  otherwise false;
- "puts_decision": true where it asks you to make one decision or to approve one proposal;
  otherwise false;
- "leaves_to_ai": true where your answer says the AI may decide it; otherwise false;
- "approves_questions": true where it shows you the purpose or the questions of a kind of work in
  general and your answer approves them; otherwise false;
- "changes_question": true where your answer changes the purpose or a question of a kind of work
  that you approved before in this conversation; otherwise false;
- "elsewhere": true where, from what the message asks, you would rather settle the point yourself
  outside this conversation, or make the work another way; otherwise false;
- "confirms_design": true where it shows you the whole design and asks whether you understand it
  the same way; otherwise false;
- "finished": true where the message says the work is done and asks you nothing; otherwise
  false."""
)
FINDS = trying.finds(
    "You stand in for the person an AI is making a work for. Here is who you are and what you truly"
    " want; the AI cannot see it:",
    KEYS,
)
# The frequent cases each trial's run must bring out to count: by the stand-in's key, or by the
# run's folder.
CASES = {
    "readme": ("asks_kind", "shows_fact", "puts_decision", "leaves_to_ai"),
    "man-page": ("approves_questions", "shows_fact", "puts_decision", "leaves_to_ai"),
    "o2": ("shows_fact", "puts_decision", "leaves_to_ai"),
}
JUDGES = """You stand in for the person an AI made a work for. Here is who you are and what you
truly want:

{intent}

The work, each file as it is:

{work}

Judge the work as that person, about to put it to use. Give only one JSON object, with no other
text: {{"changes": [each change you would make or ask for before you put it to use, in a short
sentence each; none where you would use it as it is]}}."""


def intent(trial: str) -> str:
    """The trial's intent, as written before the run."""
    with open(os.path.join(HERE, TRIALS[trial][1]), encoding="utf-8") as f:
        return f.read()


def copies(place: str, trial: str) -> list[str]:
    """Copies of the plugins the trial runs, in the run's folder, Lane's code taken whole through
    each plugin's link."""
    names = ["turn", "pin"] + (["caller"] if trial == "o2" else [])
    made = []
    for name in names:
        source = (
            os.path.join(HERE, "caller")
            if name == "caller"
            else os.path.join(ROOT, "plugins", name)
        )
        made.append(os.path.join(place, "plugins", name))
        shutil.copytree(source, made[-1], symlinks=False)
    return made


class Person:
    """The stand-in for the person: given each last message of the main conversation, it judges
    the message from the intent and gives the answer to type, keeping the conversation and its view
    of each message in `turns`."""

    def __init__(self, intent_text: str, cwd: str) -> None:
        self.intent = intent_text
        self.cwd = cwd
        self.turns: list[dict[str, Any]] = []
        self.said: list[str] = []
        self.began = time.monotonic()

    def __call__(self, message: str) -> str | None:
        """The answer to the message: None once the work is handed back, "" where the message asks
        nothing, so the session waits."""
        if len(self.turns) == TURNS:
            raise SystemExit(f"no work came back in {TURNS} messages to the person")
        view = trying.heard(FINDS, self.intent, self.said, message, self.cwd)
        view["message"], view["at"] = message, time.monotonic() - self.began
        self.turns.append(view)
        words = str(view.get("answer") or "")
        print(f"  Turn: {message[:300]!r}\n  the person: {words[:200]!r}", flush=True)
        if view.get("finished"):
            return None
        if words:
            self.said += [f"AI: {message}", f"You: {words}"]
            view["sent"] = True
        return words

    def permits(self, screen: str) -> str:
        """The choice it takes where Claude Code asks it to allow a call."""
        return trying.permitted(self.intent, screen, self.cwd)


def run(trial: str, number: int) -> bool:
    """One run of the trial; prints what it found and measured, and gives whether it counted and
    passed."""
    place = trying.folder("turn", f"trial-{trial}-{number}")
    repo = os.path.join(place, "tidy")
    trying.committed(repo, helpers.TIDY)
    person = Person(intent(trial), os.path.join(place, "person"))
    os.makedirs(person.cwd)
    plugins = copies(place, trial)
    ended = trying.interactive(
        TRIALS[trial][0], plugins, repo, place, wait=180, answer=person, permit=person.permits
    )
    keep(os.path.join(place, "turns.json"), ended["session_id"], person.turns)
    return judged(place, trial)


def keep(path: str, session: str, turns: list[dict[str, Any]]) -> None:
    """Keeps the session's ID and the stand-in's view of each message, for the judge to read."""
    text = json.dumps({"session": session, "turns": turns}, ensure_ascii=False, indent=1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")


def by_type(session: str) -> dict[str, list[dict[str, Any]]]:
    """The entries of the session's records, `main` for the main conversation and each agent's
    type for its runs, joined in order."""
    found: dict[str, list[dict[str, Any]]] = {}
    paths = [("main", p) for p in glob.glob(record.conversation(session))]
    paths += [(record.agent_type(p), p) for p in sorted(trying.agents(session))]
    for kind, path in paths:
        found.setdefault(kind, []).extend(record.read(path) or [])
    return found


def run_folder(repo: str, trial: str) -> str:
    """The folder of the run Turn made: the calling AI's for o2, else the one in .turn/ that holds
    a Run, or "" where there is not one alone."""
    if trial == "o2":
        return os.path.join(repo, CALLERS_RUN)
    found = [os.path.dirname(p) for p in glob.glob(os.path.join(repo, ".turn", "*", "run.json"))]
    return found[0] if len(found) == 1 else ""


def loaded(path: str) -> Any:
    """The JSON at the path; None where there is none, or it is no JSON."""
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        return json.loads(text)
    except ValueError:
        return None


def rounds_seen(folder: str) -> tuple[bool, bool]:
    """Whether the run's rounds held a question not met, and a reading round, from each Round and
    each Answers file kept in its folders."""
    short = reading = False
    for path in glob.glob(
        os.path.join(folder, "**", "verification", "**", "*.json"), recursive=True
    ):
        data = loaded(path) or {}
        reading = reading or data.get("phase") == "reading"
        short = short or bool(data.get("not_met")) and os.path.basename(path).startswith("G")
    return short, reading


def judged(place: str, trial: str) -> bool:
    """Judges the run kept in its folder from its records, the stand-in's view of each message, the
    run's folder and the work; prints and keeps the measures, and gives whether it counted and
    passed."""
    kept = loaded(os.path.join(place, "turns.json")) or {"session": "", "turns": []}
    turns: list[dict[str, Any]] = kept["turns"]
    repo = os.path.join(place, "tidy")
    folder = run_folder(repo, trial)
    short, reading = rounds_seen(folder) if folder else (False, False)
    untried = [
        f"no message showed {key}" for key in CASES[trial] if not any(t.get(key) for t in turns)
    ]
    untried += [] if short else ["no question was found not met and sent back"]
    untried += [] if reading else ["no reading round was made"]
    done = [t["at"] for t in turns if t.get("finished")]
    wrong = kr1_1(trial, turns, folder, repo, place, bool(done))
    measures: dict[str, Any] = {"KR1.1": f"{len(wrong)} wrong of 1 work", "KR1.1 wrong": wrong}
    measures["KR1.2"] = round(done[-1]) if done else None
    if trial == "o2":
        wrong_back, lead = kr2(turns, folder, by_type(kept["session"]), bool(done))
        measures.update({"KR2.1": f"{len(wrong_back)} wrong of 1 work", "KR2.1 wrong": wrong_back})
        measures["KR2.2"] = lead
        wrong += wrong_back
    with open(os.path.join(place, "measures.json"), "w", encoding="utf-8") as f:
        json.dump(measures, f, indent=1)
    print("  measures:", json.dumps(measures, ensure_ascii=False))
    return trying.verdict(untried, wrong)


def work_of(folder: str, repo: str) -> dict[str, str]:
    """Each file of the work the run handed back, by its path, as it lies in the repository."""
    data = loaded(os.path.join(folder, "run.json")) or {"works": [{"paths": []}]}
    found = {}
    for path in data["works"][-1]["paths"]:
        try:
            with open(os.path.join(repo, path), encoding="utf-8") as f:
                found[path] = f.read()
        except OSError:
            found[path] = "(missing)"
    return found


def kr1_1(
    trial: str, turns: list[dict[str, Any]], folder: str, repo: str, place: str, handed: bool
) -> list[str]:
    """Each way the work went wrong of the UX's five of KR1.1; the work counts once, but each way
    is kept to read."""
    if not handed or not folder:
        return ["the run stopped with no work handed back"]
    wrong = []
    work = work_of(folder, repo)
    shown = "\n\n".join(f"--- {path}\n{text}" for path, text in work.items())
    judged_work = trying.stand_in(
        JUDGES.format(intent=intent(trial), work=shown), os.path.join(place, "person")
    )
    wrong += [f"the person would change: {c}" for c in judged_work.get("changes", [])]
    for n, t in enumerate(turns, 1):
        if t.get("asks_fact") or t.get("asks_not_theirs"):
            wrong.append(f"message {n} put a point to the person that was not theirs")
        if t.get("elsewhere"):
            wrong.append(f"message {n} would have the person settle it outside the run")
    approved = False
    for n, t in enumerate(turns, 1):
        if approved and t.get("changes_question"):
            wrong.append(
                f"message {n}: the person changed a question of the kind after approving it"
            )
        approved = approved or bool(t.get("approves_questions"))
    return wrong


def times(entries: list[dict[str, Any]], tool: str, words: str) -> list[datetime.datetime]:
    """When each use of the tool whose input holds the words was made, in a record's entries."""
    found = []
    for n, done in record.done_at(entries, ""):
        if done.tool == tool and words in json.dumps(done.given):
            stamp = str(entries[n]["timestamp"]).replace("Z", "+00:00")
            found.append(datetime.datetime.fromisoformat(stamp))
    return found


def last_messages(entries: list[dict[str, Any]]) -> list[str]:
    """The text of each message that ended a turn, in a record's entries."""
    return [d.given[record.SAID] for d in record.done(entries, "") if d.tool == record.REPLY]


def kr2(
    turns: list[dict[str, Any]], folder: str, files: dict[str, list[dict[str, Any]]], handed: bool
) -> tuple[list[str], int | None]:
    """For o2: each way the work the calling AI got back went wrong of the UX's four of KR2.1, and
    the seconds from its start of turn:up to the work handed back, KR2.2."""
    caller, up = files.get("caller:caller", []), files.get("turn:up", [])
    wrong = [] if handed else ["the calling AI got no work back"]
    if any(t.get("asks_settled") for t in turns):
        wrong.append("Turn asked the person a point the calling AI settled")
    tree = loaded(os.path.join(folder, "design-tree.json")) or {}
    by_id = {d.get("id"): d for d in tree.get("decisions", [])}
    for point in SETTLED:
        if by_id.get(point, {}).get("settled_by") != "maker":
            wrong.append(f"the design holds the calling AI's point {point} otherwise than given")
    passed = "\n".join(last_messages(caller))
    for message in last_messages(up):
        if message.startswith(("For the person:", "Done:")) and message.strip() not in passed:
            wrong.append(f"the calling AI did not pass on as given: {message[:80]!r}")
    if times(caller, "Write", "README.md") + times(caller, "Edit", "README.md"):
        wrong.append("the calling AI wrote the work")
    started = times(caller, "Agent", "turn:up")
    ended = [t for t in times(files.get("turn:planner", []), "Bash", "result.py planner done")]
    lead = round((ended[-1] - started[0]).total_seconds()) if started and ended else None
    return wrong, lead


def main(argv: list[str]) -> None:
    """Runs the trials the command line names, or judges a kept run again; exits 0 where every run
    counted and passed."""
    if argv[:1] == ["--judge"]:
        sys.exit(0 if judged(argv[1], argv[2]) else 1)
    chosen = argv[0] if argv else "all"
    count = int(argv[1]) if len(argv) > 1 else 3
    trials = list(TRIALS) if chosen == "all" else [chosen]
    passed = [run(t, n) for t in trials for n in range(1, count + 1)]
    print(f"{sum(passed)} of {len(passed)} runs passed")
    sys.exit(0 if all(passed) else 1)


if __name__ == "__main__":
    main(sys.argv[1:])

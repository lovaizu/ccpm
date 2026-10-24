"""The cases of rn's move trials, one per move the steps of rn's skills take: the state each starts
from, made by rn's commands and the stand-in turn as the moves before it would leave it, what that
state must be for the step, the messages sent, what the stand-in turn gives back for each work it is
called on, and what each message's move must leave, checked by script.

The session is the smallest piece of work that reaches every move: a line greeting new contributors
added to the README of a small project, with one criterion settled in a task, one document, one task
building the finished work, and two learnings, one general and one of the project's own."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Callable, NamedTuple

from place import ROOT, SEED, Place, Seen

sys.path.insert(0, os.path.join(ROOT, "rn", "scripts"))
import rn

# The user's words, in the conversation language their instructions set.
REQUEST = "/rn:up README に新しいコントリビューター向けの挨拶を一行足して"
FEEDBACK = "挨拶には、質問があるときは issue を開けばよいことも書いてほしい"
# Each answer in the user's own words, so the decision kept is the one the stand-in turn's reply
# was made from, whichever order rn puts its options in.
LANGUAGES_ANSWER = "会話は日本語、リポジトリは英語でお願いします"
DONE_ANSWER = "README に、新しいコントリビューターを迎えて `sh demo.sh` を実行するよう伝える一行があることです"
WHY_ANSWER = "歓迎されていると感じて、早く最初の変更を出してもらうためです"
USE_ANSWER = "いいえ、Use の節は指さなくていいです"
PLACE_ANSWER = "タイトルのすぐ下に置いてください"
ASK_ANSWER = "挨拶の行に、質問があれば issue を開くよう書いてください。リンクはいりません"
SLUG = "greet-contributors"
TITLE = "Greet new contributors"
PR = "https://github.com/trial/demo/pull/1"

# What rn.py ccs is given for each work, as the steps of /rn:up give it.
PLAN_CCS = [
    "ccs",
    "plan",
    "--kind",
    "plan",
    "--receiver",
    (
        "the user at the plan sign-off, approving what the finished work will do and why, and rn's"
        " orchestrator in any later conversation, carrying the work on without asking them again"
    ),
    "--use",
    "approving the goal and the acceptance criteria, then carrying each later work to them",
    "--has",
    ".",
]


def note_ccs(work: str, path: str) -> list:
    """What rn.py ccs is given for a task's work of the kind note, its reader as the note
    checklist's opening names them."""
    return [
        "ccs",
        work,
        path,
        "--kind",
        "note",
        "--receiver",
        f"a contributor who opens {path}",
        "--use",
        "taking in the greeting line and doing what it says",
        "--has",
        ".",
    ]


DELIVERABLE_CCS = [
    "ccs",
    "deliverable",
    "--kind",
    "deliverable",
    "--receiver",
    "the user at the deliverable sign-off",
    "--use",
    "checking that the finished work does each acceptance criterion",
    "--has",
    ".",
]


def learnings_ccs(records: list) -> list:
    """What rn.py ccs is given for the learnings, as /rn:ty's step 3 gives it."""
    has = [arg for path in records for arg in ("--has", path)]
    return [
        "ccs",
        "learnings",
        "--kind",
        "learnings",
        "--receiver",
        "the user deciding each learning once the finished work is approved",
        "--use",
        (
            "deciding where each learning goes: their checklists, an issue to rn's makers, both, or"
            " neither"
        ),
        *has,
    ]


# Each Next the moves before a case keep, as the steps of /rn:up word it.
NEXT_PURPOSE = "Step 6 of /rn:up on plan: hear the purpose and what shows it done"
NEXT_CALL = "Step 6 of /rn:up on plan: have the plan made, step 4, as no point is left to hear"
NEXT_T1 = (
    "Step 5 of /rn:up on T1: step 1, read README.md and confirm the greeting's place with the user"
)
NEXT_T1_2 = "Step 5 of /rn:up on T1: step 2, have turn make the criteria from what step 1 settled"
NEXT_PLAN_SIGNOFF = "Step 9 of /rn:up on plan: stop at the plan sign-off"
NEXT_FEEDBACK = "Step 10 of /rn:up on plan: find the point behind the feedback"
NEXT_DOCUMENTS = "Step 7 of /rn:up on plan: hear which documents the purpose needs"
NEXT_T2 = "Step 5 of /rn:up on T2: step 1, read README.md and confirm the greeting's words"
NEXT_T2_2 = "Step 5 of /rn:up on T2: step 2, have turn design docs/greeting.md"
NEXT_T2_4 = "Step 5 of /rn:up on T2: step 4, have turn make docs/greeting.md"
NEXT_DESIGN_SIGNOFF = "Step 9 of /rn:up on design: stop at the design sign-off"
NEXT_BUILD = "Step 8 of /rn:up on plan: make the tasks that build the finished work"
NEXT_T3 = "Step 5 of /rn:up on T3: step 1, read docs/greeting.md and README.md"
NEXT_T3_2 = "Step 5 of /rn:up on T3: step 2, have turn design the change to README.md"
NEXT_T3_4 = "Step 5 of /rn:up on T3: step 4, have turn make the change to README.md"
NEXT_REPLAN = "Step 8 of /rn:up on plan: have the plan made again from what T3 brought"
NEXT_FINISHED = "Step 8 of /rn:up on deliverable: have the finished work used"
NEXT_DELIVERABLE_SIGNOFF = "Step 9 of /rn:up on deliverable: stop at the deliverable sign-off"
NEXT_LEARNINGS = "Step 11 of /rn:up: put each learning to the user"
NEXT_L2 = "Step 11 of /rn:up on L2: put it to the user"

# The plan, as turn makes it at each stage: the goal, the criteria and the tasks.
G1 = (
    "G1: New contributors are greeted in the README and told where to start, so they feel welcome"
    " and open their first change sooner."
)
G1_BARE = "G1: The README greets new contributors."
G1_ASK = (
    "G1: New contributors are greeted in the README and told where to start and where to ask, so"
    " they feel welcome and open their first change sooner."
)
AC1_FIRST = "- AC1: The README holds a line greeting new contributors."
AC1 = "- AC1: The README holds a line greeting new contributors, right under its title."
AC2 = "- AC2: The greeting line tells new contributors to start by running `sh demo.sh`."
AC3 = "- AC3: The greeting line tells new contributors to open an issue to ask a question."
T1 = """- [ ] T1: Settle the acceptance criteria with the user. Serves G1.

  Completion criterion: the criteria together give the whole of G1, each answered yes or no by reading the README; checked by reading each against G1.

  - [ ] 1. Read README.md, finding out where a greeting fits and what a new contributor runs first; confirm the greeting's place with the user. The orchestrator, with the user.
  - [ ] 2. Make the criteria again from what step 1 settled. turn."""
T2 = """- [ ] T2: Write the greeting's words and place in docs/greeting.md. Serves AC1 and AC2.

  Completion criterion: docs/greeting.md gives the greeting line and where in the README it goes; checked by a contributor finding both on its first screen.

  - [ ] 1. Read README.md, finding out the tone it is written in; confirm the greeting's words with the user. The orchestrator, with the user.
  - [ ] 2. Design the note, `docs/greeting.md` as a note work, and how a contributor finds the line and its place. turn, first run.
  - [ ] 3. Trace the note on paper against the note checklist. That run's first reader.
  - [ ] 4. Make docs/greeting.md. turn, second run."""
T3 = """- [ ] T3: Add the greeting line to README.md. Serves AC1 and AC2.

  Completion criterion: README.md holds the line docs/greeting.md gives, right under its title; checked by reading README.md and running `sh demo.sh` as the line says.

  - [ ] 1. Read docs/greeting.md and README.md, finding out the line and its place; confirm what is lacking with the user. The orchestrator, with the user.
  - [ ] 2. Design the change, `README.md` as a note work, and how a contributor finds the line. turn, first run.
  - [ ] 3. Trace the change on paper against the note checklist. That run's first reader.
  - [ ] 4. Make the change to README.md. turn, second run."""
TASKS = "## Tasks.."


def plan(goal: str, criteria: list, tasks: list, said: dict) -> dict:
    """The made of a call on the plan: its part, and every item of rn's plan checklist with its
    Good, said giving those of the goal, the criteria, the tasks and the stage."""
    part = "\n\n".join(
        [f"# {TITLE}", goal, "## Acceptance criteria", "\n".join(criteria), "## Tasks", *tasks]
    )
    whole = "whole"
    ids = [c.split(":")[0][2:] for c in criteria]
    goods = {
        "F-1": (
            (
                "From the title to the tasks the part follows F-1's template: the title, G1 under it,"
                " each criterion as `- AC<n>:`, and each task's line ending with what it serves, its"
                " completion criterion and its numbered steps, each saying who does it"
            ),
            whole,
        ),
        "B-1": (said["goal"], ["G1:"]),
        "B-2": (said["criteria"], [f"- {i}:" for i in ids]),
        "B-3": (said["tasks"], [TASKS]),
        "B-4": (
            "Each step says what it does toward its task's completion criterion and who does it"
            + said.get("design", ""),
            [TASKS],
        ),
        "B-8": (
            "Each task's step 1 reads what the task rests on and confirms with the user what is"
            " lacking" + said.get("traced", ""),
            [TASKS],
        ),
        "B-5": (said["stage"], [TASKS]),
        "B-6": (
            (
                "Each line is the goal, a criterion or a task, used by the user at the sign-off or by"
                " the orchestrator later; how each point was reached is left to the commit messages"
            ),
            whole,
        ),
        "B-7": (
            (
                "The goal is G1, each criterion and task keeps one ID, and each task serves only IDs"
                " the plan holds"
            ),
            whole,
        ),
    }
    return {
        "part": part + "\n",
        "goods": {"plan.md": {i: {"good": g, "at": at} for i, (g, at) in goods.items()}},
    }


WHY = (
    "G1 says what the user wants, new contributors greeted in the README and told where to start,"
    " and why: so they feel welcome and open their first change sooner"
)
CRITERIA = (
    "Each criterion is answered yes or no by reading the README: AC1 the greeting line there, AC2"
    " its telling to run `sh demo.sh`; together they give G1's greeting and where to start, and"
    " with them its reason"
)
PLAN_STAGE = {
    "goal": WHY,
    "criteria": CRITERIA,
    "tasks": "T1's result, the criteria, is accepted by its completion criterion, each read against"
    " G1, with nothing left to a later task",
    "stage": "In the plan stage, T1 settles the criteria for the whole goal",
}
DESIGN_STAGE = dict(
    PLAN_STAGE,
    tasks=PLAN_STAGE["tasks"] + "; T2's, docs/greeting.md, by a contributor finding the line and"
    " its place on its first screen",
    design="; T2's design step names `docs/greeting.md` as a note work",
    traced="; T2's design is traced on paper by that run's first reader before it is made",
    stage="In the design stage, T2 makes the one document the purpose needs, docs/greeting.md",
)
BUILD_STAGE = dict(
    DESIGN_STAGE,
    tasks=DESIGN_STAGE["tasks"] + "; T3's change to README.md, by reading it and running"
    " `sh demo.sh` as the line says",
    design=DESIGN_STAGE["design"] + ", and T3's `README.md` as a note work",
    traced="; T2's and T3's designs are traced on paper by that run's first reader before they"
    " are made",
    stage="In the build stage, T3 builds AC1 and AC2 in README.md",
)
PLAN_FIRST = plan(G1, [AC1_FIRST, AC2], [T1], PLAN_STAGE)
# A plan whose goal holds no reason, as its purpose was kept with none, while its Good claims one:
# a Good its lines fall short of, with a point behind it that is the user's.
PLAN_BARE = plan(G1_BARE, [AC1_FIRST, AC2], [T1], PLAN_STAGE)
PLAN_PLACED = plan(G1, [AC1, AC2], [T1], PLAN_STAGE)
PLAN_ASKED = plan(
    G1_ASK,
    [AC1, AC2, AC3],
    [T1],
    dict(
        PLAN_STAGE,
        goal=WHY.replace("where to start,", "where to start and where to ask,"),
        criteria="Each criterion is answered yes or no by reading the README: AC1 the greeting"
        " line there, AC2 its telling to run `sh demo.sh`, AC3 its telling to open an issue to"
        " ask; together they give G1's greeting, where to start and where to ask, and with them"
        " its reason",
    ),
)
PLAN_DESIGN = plan(G1, [AC1, AC2], [T1, T2], DESIGN_STAGE)
PLAN_BUILD = plan(G1, [AC1, AC2], [T1, T2, T3], BUILD_STAGE)
QUESTIONS = {
    "questions": [
        {
            "question": "Should the greeting also point to the README's Use section?",
            "recommended": "No: AC2 already tells new contributors to run `sh demo.sh`, which is"
            " what the Use section says",
            "items": [{"checklist": "plan.md", "item": "B-2"}],
        }
    ]
}

# The learnings, as turn makes them from each stretch's records, each quoting a commit message the
# state-making below keeps, or the feedback the orchestrator keeps.
PLACE_QUOTE = "the greeting goes right under the title"
LINE_QUOTE = "the greeting line as docs/greeting.md gives it"
L_PLACE = (
    "- L1: The first plan named no place for the greeting, so T1's first step had to ask it, kept"
    f" as \"{PLACE_QUOTE}\" in the commit of T1.1; for everyone's work, rn's plan checklist could"
    " ask, of a task that changes a file, where in the file the change goes."
)
L_FEEDBACK = (
    f'- L2: At the plan sign-off the user sent the plan back with "{FEEDBACK}" (the commit keeping'
    " the feedback), as no point asked where a new contributor asks a question; for everyone's"
    " work, rn could ask, of a work that greets or guides someone, what they do when they are"
    " stuck."
)
L_TWICE = (
    "- L1: The greeting's words were settled for docs/greeting.md and then again for README.md,"
    f' kept as "{LINE_QUOTE}" in the commit of T3.1; in this repository, the note checklist could'
    " ask that a note names the file its lines go into."
)


def learnt(lines: list, whole: str) -> dict:
    """The made of a call on the learnings: its part, and every item of rn's learnings checklist
    with its Good, whole saying what the stretch fell short in."""
    marks = [line.split(":")[0] + ":" for line in lines]
    goods = {
        "F-1": (
            (
                "The part is `## Learnings`, each learning `- L<n>:` saying what happened with the"
                " words it rests on, then where it would make later work better"
            ),
            "whole",
        ),
        "B-1": ("Each learning quotes the commit message it rests on and names that move", marks),
        "B-2": ("Each says what would change, and whether for everyone's work or this one", marks),
        "B-3": ("Each learning is one thing, apart from the others", "whole"),
        "B-4": (whole, "whole"),
    }
    if not lines:
        goods = {
            i: ("Nothing in the stretch fell short, so no learning is given", "whole")
            for i in goods
        }
    part = "\n\n".join(["## Learnings", "\n".join(lines)]).strip() + "\n"
    return {
        "part": part,
        "goods": {"learnings.md": {i: {"good": g, "at": at} for i, (g, at) in goods.items()}},
    }


LEARNT_PLACE = learnt([L_PLACE], "The stretch's one shortfall, the place asked late, is L1")
LEARNT_FEEDBACK = learnt(
    [L_PLACE, L_FEEDBACK],
    "The stretch's shortfalls are the place asked late, L1, and the plan sent back, L2",
)
LEARNT_NONE = learnt([], "")
LEARNT_TWICE = learnt([L_TWICE], "The stretch's one shortfall, the words settled twice, is L1")

# The works the tasks make, and the finished work used.
LINE = "Welcome, new contributor! Start by running `sh demo.sh`, then open a pull request."
GREETING = f"# Greeting\n\nThe README greets new contributors on the line right under its title:\n\n> {LINE}\n"
README = SEED["README.md"].replace("\n\n", f"\n\n{LINE}\n\n", 1)


def noted(path: str, text: str, mark: str) -> dict:
    """The made of a call on a note: the file, and both items of the note checklist with their
    Goods at the line holding the mark."""
    goods = {
        "B-1": "The decided line stands on the note's first screen, the first a contributor reads",
        "B-2": "It tells the contributor to run `sh demo.sh`, which the repository holds and which"
        " prints hello, then to open a pull request",
    }
    return {
        "files": {path: text},
        "goods": {"note.md": {i: {"good": g, "at": [mark]} for i, g in goods.items()}},
    }


NOTE_GREETING = noted("docs/greeting.md", GREETING, "> Welcome")
NOTE_README = noted("README.md", README, "Welcome")
FINISHED = {
    "goods": {
        "deliverable.md": {
            "B-1": {
                "good": "Used as the user would: README.md greets new contributors right under its"
                " title (AC1) and tells them to start by running `sh demo.sh`, which runs and prints"
                " hello (AC2)",
                "at": ["Welcome"],
                "in": "README.md",
            }
        }
    }
}
NOTE_ADDED = (
    SEED[".rn/checklists/note.md"]
    .replace(
        "do what they say.",
        "do what they say, and by whoever copies them into another file.",
    )
    .rstrip("\n")
    + """

### B-3: Where the lines go, named

Scope: its part

Can whoever copies the decided lines tell from the note which file they go into?

Look for: lines with no file named.

Why: lines copied into the wrong file are read by no one they were for.
"""
)
CHECKLIST_GOODS = {
    "F-1": "note.md follows the template: the front matter, the title, the purpose, the idea, and"
    " `## Benefit` with B-1 to B-3, each with its Scope, its question and its Why; a note adds no"
    " part to a document's shape, so it has no Format section",
    "F-2": "Its version is 1, as no release has numbered it",
    "F-3": "made_from names checklist 1 and usability 1, the versions that stand now",
    "F-4": "Its items are B-1, B-2 and B-3, counted up in Benefit",
    "B-1": "The opening says who uses a note, a contributor and whoever copies its lines, what"
    " they then do, and the idea: the decided lines where the reader looks first",
    "B-2": "Each thing the opening names has an item: finding the lines B-1, doing what they say"
    " B-2, copying them into the file they go into B-3",
    "B-3": "Each item asks one thing of the purpose that no other asks",
    "B-4": "Each item is answered by pointing at the note's lines: the lines, the command they give,"
    " the file they name",
    "B-5": "Each item asks one thing, with a sign of what is looked at",
}
NOTE_CHECKLIST = {
    "files": {".rn/checklists/note.md": NOTE_ADDED},
    "goods": {"checklist.md": {i: {"good": g, "at": "whole"} for i, g in CHECKLIST_GOODS.items()}},
}


# The moves before a case, each kept by rn's commands as the steps of rn's skills keep them, each
# building on the one before; the stand-in turn returning each call.
def number(called: str) -> str:
    """The number of the call rn.py ccs printed."""
    return os.path.basename(json.loads(called)["ccs"])[:4]


def made(p: Place, args: list, given: dict) -> str:
    """The work's CCS written and the call returned by the stand-in turn with what is given; gives
    the call's number."""
    called = p.rn(*args)
    p.turned(called, given)
    return number(called)


def state(p: Place, next_step: str, message: str, *more: str) -> None:
    """rn.py state, keeping the move with Next and the options given."""
    p.rn("state", "--next", next_step, *more, "--message", message)


def decide(p: Place, work: str, title: str, says: str, message: str) -> None:
    """rn.py decide, keeping one decision of the work."""
    p.rn("decide", work, "--title", title, "--says", says, "--message", message)


def nothing(p: Place) -> None:
    """No session: the repository as it is on its default branch."""


def started(p: Place) -> None:
    """The session started on its branch with its draft pull request, Next to hear the plan's
    purpose."""
    p.rn(
        "start",
        SLUG,
        "--title",
        TITLE,
        "--artifact-language",
        "English",
        "--conversation-language",
        "Japanese",
        "--next",
        NEXT_PURPOSE,
        "--message",
        "Start the session: the user asked to add a line greeting new contributors to the README;"
        " English for the repository, Japanese for the conversation, as their instructions set",
    )


def purposed(p: Place) -> None:
    """The purpose of the plan heard and kept, what shows it done still to hear."""
    started(p)
    decide(
        p,
        "plan",
        "Purpose",
        "new contributors are greeted in the README and told where to start, so they feel welcome"
        " and open their first change sooner",
        "Purpose: the user chose a welcome that tells where to start, over a greeting alone",
    )


def heard(p: Place, purpose: Callable[[Place], None] = purposed) -> None:
    """Both points of the plan heard and kept, after the purpose as given, the plan not yet
    called."""
    purpose(p)
    decide(
        p,
        "plan",
        "What shows it done",
        "the README holds a line greeting new contributors that tells them to run `sh demo.sh`",
        "What shows it done: the user chose the line in the README, over a separate file",
    )


def unreasoned(p: Place) -> None:
    """The purpose of the plan kept with no reason why the user wants it, a point rn did not ask,
    what shows it done still to hear."""
    started(p)
    decide(
        p,
        "plan",
        "Purpose",
        "new contributors are greeted in the README",
        "Purpose: the user asked for a greeting of new contributors in the README",
    )


def unreasoned_at_call(p: Place) -> None:
    """As at_call, the purpose kept with no reason."""
    heard(p, unreasoned)
    state(p, NEXT_CALL, "Every point of the plan is heard; the plan is made next")


def at_call(p: Place) -> None:
    """As heard, Next naming the call on the plan, as no point is left."""
    heard(p)
    state(p, NEXT_CALL, "Every point of the plan is heard; the plan is made next")


def planned(p: Place) -> None:
    """The plan made, every Good holding, and put back: G1, AC1, AC2 and T1, Next T1's step 1."""
    heard(p)
    put = made(p, PLAN_CCS, PLAN_FIRST)
    state(p, NEXT_T1, "The plan made: G1, AC1, AC2 and T1", "--put", put)


def t1_read(p: Place) -> None:
    """T1's step 1 done, the greeting's place kept as a decision, Next T1's step 2."""
    planned(p)
    decide(
        p,
        "plan",
        "Place",
        "the greeting goes right under the README's title, the first line a contributor reads",
        f'T1.1: the user chose where the greeting goes: "{PLACE_QUOTE}", over the end of the README',
    )
    state(p, NEXT_T1_2, "T1.1 done: the greeting's place settled", "--done", "T1.1")


def plan_signoff(p: Place) -> None:
    """T1 done, the plan made again with the place, and the plan sign-off waiting."""
    t1_read(p)
    put = made(p, PLAN_CCS, PLAN_PLACED)
    state(p, NEXT_PLAN_SIGNOFF, "T1.2 done: AC1 names the place", "--put", put, "--done", "T1.2")
    p.rn("proposal", "plan")


def answered(p: Place, answer: str, next_step: str, opened: list, given: dict) -> None:
    """The user's answer at the sign-off kept, and the stretch's learnings made and put back."""
    more = [arg for point in opened for arg in ("--open", point)]
    if answer == "approved":
        message = "The user approved the sign-off with /rn:ty"
    else:
        message = f"The user sent the sign-off back with /rn:gm: {opened[0]}"
    p.rn("answer", answer, "--next", next_step, *more, "--message", message)
    put = made(p, learnings_ccs(json.loads(p.rn("records"))), given)
    state(p, next_step, "The stretch's learnings kept", "--put", put, *more)


def fed_back(p: Place) -> None:
    """The plan sign-off answered with the feedback, kept in Open, and the stretch's learnings
    put back, Next step 10."""
    plan_signoff(p)
    answered(p, "feedback", NEXT_FEEDBACK, [FEEDBACK], LEARNT_FEEDBACK)


def plan_approved(p: Place) -> None:
    """The plan approved, the design stage begun, and the stretch's learning put back, Next
    step 7."""
    plan_signoff(p)
    answered(p, "approved", NEXT_DOCUMENTS, [], LEARNT_PLACE)


def t2_made(p: Place) -> None:
    """The documents heard, the plan made again with T2, and T2's steps 1 to 3 done, Next T2's
    step 4."""
    plan_approved(p)
    decide(
        p,
        "plan",
        "Documents",
        "docs/greeting.md, a note work, holding the greeting's words and its place in the README",
        "Documents: the user chose one note for the greeting, over none",
    )
    put = made(p, PLAN_CCS, PLAN_DESIGN)
    state(p, NEXT_T2, "The plan made again: T2 writes docs/greeting.md", "--put", put)
    decide(p, "t2", "Words", LINE, "T2.1: the user chose the greeting's words")
    state(p, NEXT_T2_2, "T2.1 done: the words settled", "--done", "T2.1")
    made(p, note_ccs("t2", "docs/greeting.md"), NOTE_GREETING)
    state(p, NEXT_T2_4, "T2.2 and T2.3 done", "--done", "T2.2", "--done", "T2.3")


def design_approved(p: Place) -> None:
    """T2 done, the design approved with no learning, the plan made again with T3, and
    T3's steps 1 to 3 done, Next T3's step 4."""
    t2_made(p)
    made(p, note_ccs("t2", "docs/greeting.md"), NOTE_GREETING)
    state(p, NEXT_DESIGN_SIGNOFF, "T2.4 done: docs/greeting.md made", "--done", "T2.4")
    p.rn("proposal", "design")
    answered(p, "approved", NEXT_BUILD, [], LEARNT_NONE)
    put = made(p, PLAN_CCS, PLAN_BUILD)
    state(p, NEXT_T3, "The plan made again: T3 adds the line to README.md", "--put", put)
    decide(
        p,
        "t3",
        "Line",
        "the greeting line as docs/greeting.md gives it, right under the README's title",
        f'T3.1: the user confirmed "{LINE_QUOTE}"',
    )
    state(p, NEXT_T3_2, "T3.1 done", "--done", "T3.1")
    made(p, note_ccs("t3", "README.md"), NOTE_README)
    state(p, NEXT_T3_4, "T3.2 and T3.3 done", "--done", "T3.2", "--done", "T3.3")


def deliverable_signoff(p: Place) -> None:
    """T3 done, the plan made again, the finished work used, and the deliverable
    sign-off waiting."""
    design_approved(p)
    made(p, note_ccs("t3", "README.md"), NOTE_README)
    state(p, NEXT_REPLAN, "T3.4 done: README.md greets new contributors", "--done", "T3.4")
    put = made(p, PLAN_CCS, PLAN_BUILD)
    message = "The plan made again: every task ticked"
    state(p, NEXT_FINISHED, message, "--put", put, "--stage", "deliverable")
    made(p, DELIVERABLE_CCS, FINISHED)
    state(p, NEXT_DELIVERABLE_SIGNOFF, "The finished work used: AC1 and AC2 done")
    p.rn("proposal", "deliverable")


def learnings_due(p: Place) -> None:
    """The finished work approved and the stretch's learning put back, the two learnings
    to put to the user, Next step 11."""
    deliverable_signoff(p)
    answered(p, "approved", NEXT_LEARNINGS, [], LEARNT_TWICE)


def l1_answered(p: Place) -> None:
    """L1 answered, taken for an issue, the answer in the commit message alone, Next L2."""
    learnings_due(p)
    state(p, NEXT_L2, "L1: the user chose an issue to lovaizu/ccpm alone")


# What a move must leave, each check with what it checks in words.
class Check(NamedTuple):
    """What a check checks, in words, and whether what a move left holds it."""

    what: str
    holds: Callable[[Seen], bool]


def steered(seen: Seen) -> rn.Steering | None:
    """The steering as the last commit holds it, where it holds its form."""
    if not seen.text or rn.out_of_form(seen.text):
        return None
    return rn.parsed(seen.text)


def front(stage: str, signoff: str) -> Check:
    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and (s.keys["stage"], s.keys["signoff"]) == (stage, signoff)

    return Check(f"the steering at the {stage} stage, sign-off {signoff}", holds)


def next_has(words: str) -> Check:
    return Check(f"Next holds `{words}`", lambda s: words in getattr(steered(s), "next", ""))


def open_has(words: str, held: bool = True) -> Check:
    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and (words in "\n".join(s.open)) == held

    return Check(f"Open {'holds' if held else 'no longer holds'} `{words}`", holds)


def open_none(nothing: bool = True) -> Check:
    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and (s.open == [rn.NOTHING_OPEN]) == nothing

    return Check("Open is `None.`" if nothing else "Open holds a point", holds)


def plan_has(words: str, held: bool = True) -> Check:
    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and (words in "\n".join(s.plan)) == held

    return Check(f"the plan {'holds' if held else 'does not hold'} `{words}`", holds)


def ticked(task: str) -> Check:
    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and any(t.id == task and t.ticked for t in rn.tasks_of(s.plan))

    return Check(f"{task} ticked", holds)


def learnings(n: int) -> Check:
    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and len([x for x in s.learnings if rn.LEARNING.fullmatch(x)]) == n

    return Check(f"the steering holds {n} learnings", holds)


def returned(work: str, n: int) -> Check:
    def holds(seen: Seen) -> bool:
        return len([c for c in seen.calls if c[1] == work and c[2]]) == n

    return Check(f"{n} calls on {work} returned and kept", holds)


def decisions(work: str, n: int) -> Check:
    def holds(seen: Seen) -> bool:
        last = [c for c in seen.calls if c[1] == work][-1:]
        return bool(last) and last[0][3] >= n

    return Check(f"the latest call on {work} holds {n} decisions or more", holds)


def pr(draft: bool) -> Check:
    def holds(seen: Seen) -> bool:
        prs = seen.gh["prs"]
        return len(prs) == 1 and prs[0]["isDraft"] == draft and prs[0]["baseRefName"] == "main"

    return Check(f"one pull request into main, {'draft' if draft else 'marked ready'}", holds)


def issues(n: int) -> Check:
    def holds(seen: Seen) -> bool:
        return len(seen.gh["issues"]) == n and all(
            i["repo"] == "lovaizu/ccpm" for i in seen.gh["issues"]
        )

    return Check(f"{n} issues opened on lovaizu/ccpm", holds)


def file_has(path: str, words: str) -> Check:
    return Check(f"{path} holds `{words}`", lambda s: words in s.texts.get(path, ""))


def says(words: str) -> Check:
    return Check(f"the reply holds `{words}`", lambda s: words in s.reply)


NO_SESSION = Check("no session on the branch", lambda s: not s.steering)
NO_PR = Check("no pull request opened", lambda s: not s.gh["prs"])
STAYS = Check("no commit made", lambda s: s.commits == 0)
MOVED = Check("a commit made", lambda s: s.commits > 0)
KEPT = Check("every change committed and the branch pushed", lambda s: s.clean and s.pushed)
JAPANESE = Check("the reply in Japanese", lambda s: bool(re.search(r"[぀-ヿ一-鿿]", s.reply)))
ONE_POINT = Check(
    "the reply asks one point, `▶` once, with options `a.` and `b.`",
    lambda s: s.reply.count("▶") == 1 and all(re.search(rf"(?m)^\W*{x}\. ", s.reply) for x in "ab"),
)
TURN_LINE = Check(
    "a line of turn's passed on to the user",
    lambda s: any(t.strip().startswith("turn:") for t in s.said),
)


def languages(seen: Seen) -> bool:
    """Whether the steering keeps English for the repository and Japanese for the conversation."""
    s = steered(seen)
    if s is None:
        return False
    spoken = s.keys["conversation-language"].lower()
    return "english" in s.keys["artifact-language"].lower() and (
        "japanese" in spoken or "日本語" in spoken
    )


LANGUAGES = Check(
    "the steering's languages English for the repository, Japanese for the conversation", languages
)


def proposal(signoff: str) -> list:
    """The checks of a move that stops at the sign-off: kept waiting, the proposal shown whole."""
    return [
        front({"plan": "plan", "design": "design"}.get(signoff, "deliverable"), signoff),
        next_has(f"Wait at the {signoff} sign-off"),
        says(PR),
        says("/rn:ty"),
        says("/rn:gm"),
        JAPANESE,
    ]


class Case(NamedTuple):
    """A case: the move it tries, the steps it covers, the state it starts from with what that
    state must be, each message with what its move must leave, and the stand-in turn's replies by
    work, each call on a work given the next."""

    move: str
    covers: str
    start: Callable[[Place], None]
    expects: list
    messages: list
    replies: dict


CASES = {
    "none-up": Case(
        "/rn:up alone with no session",
        "up 1 (no session, no words)",
        nothing,
        [NO_SESSION],
        [("/rn:up", [NO_SESSION, STAYS, NO_PR, JAPANESE, says("/rn:up")])],
        {},
    ),
    "none-ty": Case(
        "/rn:ty with no session",
        "ty 1 (no session)",
        nothing,
        [NO_SESSION],
        [("/rn:ty", [NO_SESSION, STAYS, NO_PR, JAPANESE, says("/rn:up")])],
        {},
    ),
    "none-gm": Case(
        "/rn:gm <feedback> with no session",
        "gm 1 (no session)",
        nothing,
        [NO_SESSION],
        [(f"/rn:gm {FEEDBACK}", [NO_SESSION, STAYS, NO_PR, JAPANESE, says("/rn:up")])],
        {},
    ),
    "request": Case(
        "/rn:up <request> with no session: the languages asked first",
        "up 1 (no session, words), 2 (the first point), 3 (the point's form)",
        nothing,
        [NO_SESSION],
        [(REQUEST, [NO_SESSION, STAYS, NO_PR, ONE_POINT, JAPANESE])],
        {},
    ),
    "languages": Case(
        "the languages answered: the session started, the first point of the plan asked",
        "up 2 (start), 6 (hear the purpose), 3 (ask)",
        nothing,
        [NO_SESSION],
        [
            (REQUEST, [NO_SESSION, ONE_POINT]),
            (
                LANGUAGES_ANSWER,
                [
                    MOVED,
                    KEPT,
                    front("plan", "none"),
                    LANGUAGES,
                    next_has("Step 6"),
                    pr(draft=True),
                    ONE_POINT,
                    JAPANESE,
                ],
            ),
        ],
        {},
    ),
    "point": Case(
        "/rn:up in a fresh conversation while a point is asked, then the point answered",
        "up 1 (Next), 6, 3 (the next point, nothing settled asked again; the answer kept)",
        purposed,
        [front("plan", "none"), next_has("Step 6"), decisions("plan", 1)],
        [
            ("/rn:up", [STAYS, ONE_POINT, JAPANESE]),
            (DONE_ANSWER, [MOVED, KEPT, decisions("plan", 2), ONE_POINT]),
        ],
        {"plan": [PLAN_FIRST]},
    ),
    "good": Case(
        "turn's result with every Good holding: checked at its lines and put back",
        "up 1, 6, 4 (the call, turn's line, every Good holding, --put), 5 (the line before T1.1)",
        at_call,
        [next_has("Step 6"), decisions("plan", 2), returned("plan", 0)],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    returned("plan", 1),
                    plan_has("- AC2:"),
                    next_has("T1"),
                    open_none(),
                    TURN_LINE,
                    ONE_POINT,
                ],
            )
        ],
        {"plan": [PLAN_FIRST]},
    ),
    "short": Case(
        "a result with a Good its lines fall short of: the point behind it, the plan made again",
        "up 4 (a Good falling short, Open, Next step 3), 3, 4 again (--put)",
        unreasoned_at_call,
        [next_has("Step 6"), returned("plan", 0)],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    returned("plan", 1),
                    plan_has("G1:", held=False),
                    next_has("Step 3"),
                    open_none(nothing=False),
                    ONE_POINT,
                ],
            ),
            (
                WHY_ANSWER,
                [KEPT, returned("plan", 2), plan_has("so they feel welcome"), open_none()],
            ),
        ],
        {"plan": [PLAN_BARE, PLAN_FIRST]},
    ),
    "asks": Case(
        "turn asks a question: asked as a point, the answer kept and sent to turn",
        "up 4 (turn's questions, SendMessage), 3",
        at_call,
        [next_has("Step 6"), returned("plan", 0)],
        [
            ("/rn:up", [returned("plan", 0), ONE_POINT, JAPANESE]),
            (USE_ANSWER, [KEPT, decisions("plan", 3), returned("plan", 1), next_has("T1")]),
        ],
        {"plan": [QUESTIONS, PLAN_FIRST]},
    ),
    "task": Case(
        "a task's step of the orchestrator's, then one of turn's, each with a line before and"
        " after, up to the plan sign-off",
        "up 1, 5 (both kinds of step), 3, 4, 6, 9",
        planned,
        [next_has("Step 5 of /rn:up on T1: step 1"), returned("plan", 1)],
        [
            ("/rn:up", [STAYS, ONE_POINT, JAPANESE]),
            (PLACE_ANSWER, [MOVED, KEPT, decisions("plan", 3), ticked("T1"), *proposal("plan")]),
        ],
        {"plan": [PLAN_PLACED]},
    ),
    "plan-signoff": Case(
        "a task's step of turn's, then the plan sign-off",
        "up 1, 5 (turn's step), 4, 6, 9",
        t1_read,
        [next_has("Step 5 of /rn:up on T1: step 2"), returned("plan", 1)],
        [("/rn:up", [MOVED, KEPT, returned("plan", 2), ticked("T1"), *proposal("plan")])],
        {"plan": [PLAN_PLACED]},
    ),
    "resume-signoff": Case(
        "/rn:up in a fresh conversation while the plan sign-off waits",
        "up 1 (a sign-off waiting), 9 (the same proposal, nothing kept)",
        plan_signoff,
        [front("plan", "plan")],
        [("/rn:up", [STAYS, *proposal("plan")])],
        {},
    ),
    "nosignoff-ty": Case(
        "/rn:ty with no sign-off waiting",
        "ty 1 (no sign-off)",
        planned,
        [front("plan", "none")],
        [("/rn:ty", [STAYS, front("plan", "none"), JAPANESE, says("/rn:up")])],
        {},
    ),
    "nosignoff-gm": Case(
        "/rn:gm <feedback> with no sign-off waiting",
        "gm 1 (no sign-off)",
        planned,
        [front("plan", "none")],
        [(f"/rn:gm {FEEDBACK}", [STAYS, front("plan", "none"), JAPANESE, says("/rn:up")])],
        {},
    ),
    "empty-gm": Case(
        "/rn:gm with no feedback at the plan sign-off",
        "gm 1 (no feedback)",
        plan_signoff,
        [front("plan", "plan")],
        [("/rn:gm", [STAYS, front("plan", "plan"), JAPANESE, says("/rn:gm")])],
        {},
    ),
    "ty-plan": Case(
        "/rn:ty at the plan sign-off: approved, the learnings made, going on",
        "ty 1, 2, 3 (up 4 on learnings), 4 (up 7, 3)",
        plan_signoff,
        [front("plan", "plan"), learnings(0)],
        [
            (
                "/rn:ty",
                [
                    MOVED,
                    KEPT,
                    front("design", "none"),
                    returned("learnings", 1),
                    learnings(1),
                    next_has("Step 7"),
                    ONE_POINT,
                ],
            )
        ],
        {"learnings": [LEARNT_PLACE]},
    ),
    "gm-plan": Case(
        "/rn:gm <feedback> at the plan sign-off: kept whole in Open, the learnings made, stop",
        "gm 1, 2, 3 (ty 3, up 4 on learnings), 4",
        plan_signoff,
        [front("plan", "plan"), learnings(0)],
        [
            (
                f"/rn:gm {FEEDBACK}",
                [
                    MOVED,
                    KEPT,
                    front("plan", "none"),
                    next_has("Step 10"),
                    open_has(FEEDBACK),
                    returned("learnings", 1),
                    returned("plan", 2),
                    learnings(2),
                    JAPANESE,
                    says("/rn:up"),
                ],
            )
        ],
        {"learnings": [LEARNT_FEEDBACK]},
    ),
    "after-feedback": Case(
        "/rn:up in a fresh conversation after feedback: the point behind it, the plan made again,"
        " the same sign-off",
        "up 1, 10, 3, 4, 9 (what changed)",
        fed_back,
        [front("plan", "none"), next_has("Step 10"), open_has(FEEDBACK)],
        [
            ("/rn:up", [STAYS, ONE_POINT, open_has(FEEDBACK)]),
            (
                ASK_ANSWER,
                [
                    MOVED,
                    KEPT,
                    returned("plan", 3),
                    plan_has("- AC3:"),
                    open_has(FEEDBACK, held=False),
                    *proposal("plan"),
                ],
            ),
        ],
        {"plan": [PLAN_ASKED]},
    ),
    "design-signoff": Case(
        "a document's last step, made by turn, then the design sign-off",
        "up 1, 5, 4 (a task's work), 7, 9",
        t2_made,
        [front("design", "none"), next_has("Step 5 of /rn:up on T2: step 4"), returned("t2", 1)],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    returned("t2", 2),
                    ticked("T2"),
                    *proposal("design"),
                    says("docs/greeting.md"),
                ],
            )
        ],
        {"t2": [NOTE_GREETING]},
    ),
    "deliverable-signoff": Case(
        "the build's last step, the plan made again, the finished work used, the deliverable"
        " sign-off",
        "up 1, 5, 4, 8, 9",
        design_approved,
        [front("build", "none"), next_has("Step 5 of /rn:up on T3: step 4")],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    ticked("T3"),
                    returned("deliverable", 1),
                    file_has("README.md", "Welcome, new contributor!"),
                    *proposal("deliverable"),
                ],
            )
        ],
        {"t3": [NOTE_README], "plan": [PLAN_BUILD], "deliverable": [FINISHED]},
    ),
    "ty-deliverable": Case(
        "/rn:ty at the deliverable sign-off: approved, the learnings made, the first learning put",
        "ty 1, 2, 3, 4 (up 11)",
        deliverable_signoff,
        [front("deliverable", "deliverable"), learnings(1)],
        [
            (
                "/rn:ty",
                [
                    MOVED,
                    KEPT,
                    front("learnings", "none"),
                    learnings(2),
                    next_has("Step 11"),
                    ONE_POINT,
                ],
            )
        ],
        {"learnings": [LEARNT_TWICE]},
    ),
    "learning": Case(
        "the learnings put one per message, the first taken for an issue",
        "up 1, 11 (one learning per message, each answer kept)",
        learnings_due,
        [front("learnings", "none"), learnings(2), next_has("Step 11")],
        [
            ("/rn:up", [STAYS, ONE_POINT, JAPANESE]),
            (
                "issue だけに送ってください",
                [MOVED, KEPT, next_has("L2"), issues(0), ONE_POINT],
            ),
        ],
        {},
    ),
    "last": Case(
        "the last learning taken for the checklist, the issue shown and sent, the pull request"
        " marked ready",
        "up 1, 11 (the checklist made, up 4; the issue; gh pr ready; finished)",
        l1_answered,
        [front("learnings", "none"), next_has("L2")],
        [
            ("/rn:up", [STAYS, ONE_POINT]),
            ("チェックリストだけに足してください", [MOVED, KEPT, decisions("checklist-note", 1)]),
            (
                "はい",
                [
                    KEPT,
                    issues(1),
                    returned("checklist-note", 1),
                    file_has(".rn/checklists/note.md", "### B-3:"),
                    pr(draft=False),
                    front("finished", "none"),
                    says(PR),
                ],
            ),
        ],
        {"checklist-note": [NOTE_CHECKLIST]},
    ),
}

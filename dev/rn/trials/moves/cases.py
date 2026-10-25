"""The cases of rn's move trials, one per move the steps of rn's skills take: the state each starts
from, made by rn's commands and the stand-in turn as the moves before it would leave it, what that
state must be for the step, the messages sent, what the stand-in turn gives back for each work it is
called on, and what each message's move must leave, checked by script.

The session is the smallest piece of work that reaches every move: a line greeting new contributors
added to the README of a small project, with one task in the plan stage, whose research settles a
criterion with the user, one document, one task building the finished work, and two learnings, one
general and one of the project's own."""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
import uuid
from typing import Callable, NamedTuple

from place import ROOT, SEED, Place, Seen

sys.path.insert(0, os.path.join(ROOT, "rn", "scripts"))
import record
import session
import steering

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
L1_OPEN = "L1: an issue to lovaizu/ccpm alone, not yet sent"
SLUG = "greet-contributors"
TITLE = "Greet new contributors"
PR = "https://github.com/trial/demo/pull/1"
# The session's folder, named by the day rn.py start runs, as the state is made on the day the trial
# runs; and the research T1 makes there.
SESSION = f"{session.RECORD}/{datetime.date.today():%Y%m%d}-{SLUG}"
RESEARCH = f"{SESSION}/place.md"

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


RESEARCH_CCS = [
    "ccs",
    "t1",
    RESEARCH,
    "--kind",
    "research",
    "--receiver",
    "the user deciding where the greeting goes, and the maker of each later work it is handed to",
    "--use",
    "deciding the greeting's place on checked facts instead of a guess",
    "--has",
    "README.md",
]


def note_ccs(work: str, path: str, has: str) -> list:
    """What rn.py ccs is given for a task's work of the kind note, its reader as the note
    checklist's opening names them, with the earlier output it is made from."""
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
        has,
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
NEXT_T1 = "Step 5 of /rn:up on t1: action 1, have turn research where the greeting goes"
NEXT_T1_2 = "Step 5 of /rn:up on t1: action 2, confirm the greeting's place with the user"
NEXT_T1_WEIGH = "Step 5 of /rn:up on t1: weigh what it brought"
NEXT_PLAN_SIGNOFF = "Step 9 of /rn:up on plan: stop at the plan sign-off"
NEXT_FEEDBACK = "Step 10 of /rn:up on plan: find the point behind the feedback"
NEXT_DOCUMENTS = "Step 7 of /rn:up on plan: hear which documents the purpose needs"
NEXT_T2 = "Step 5 of /rn:up on t2: action 1, confirm the greeting's words with the user"
NEXT_T2_2 = "Step 5 of /rn:up on t2: action 2, have turn make docs/greeting.md"
NEXT_DESIGN_SIGNOFF = "Step 9 of /rn:up on design: stop at the design sign-off"
NEXT_BUILD = "Step 8 of /rn:up on plan: make the tasks that build the finished work"
NEXT_T3 = "Step 5 of /rn:up on t3: action 1, confirm the line docs/greeting.md gives"
NEXT_T3_2 = "Step 5 of /rn:up on t3: action 2, have turn make the change to README.md"
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
AC3 = (
    "- AC3: The greeting line tells new contributors to open an issue to ask a question, with no"
    " link."
)
T1 = f"""- T1: The greeting's place, chosen by the user from checked facts. Serves AC1.

  Completion criterion: the user has chosen where in README.md the greeting goes, from what the README holds and what GitHub shows of it first; checked by the choice kept as a decision of the plan resting on the research.

  - [ ] 1. Research what README.md holds above its first section and what GitHub shows of a README first, `{RESEARCH}` as a research work. turn.
  - [ ] 2. Confirm the greeting's place with the user, from that research. The orchestrator, with the user."""
T2 = """- T2: docs/greeting.md, giving the greeting's words and its place. Serves AC1 and AC2.

  Completion criterion: docs/greeting.md gives the greeting line and where in the README it goes; checked by a contributor finding both on its first screen.

  - [ ] 1. Confirm the greeting's words with the user, in the tone README.md is written in. The orchestrator, with the user.
  - [ ] 2. Make the note from the words settled, `docs/greeting.md` as a note work. turn."""
T3 = """- T3: README.md greeting new contributors. Serves AC1 and AC2.

  Completion criterion: README.md holds the line docs/greeting.md gives, right under its title; checked by reading README.md and running `sh demo.sh` as the line says.

  - [ ] 1. Confirm with the user the line docs/greeting.md gives and its place. The orchestrator, with the user.
  - [ ] 2. Make the change from docs/greeting.md, `README.md` as a note work. turn."""
TASKS = "## Tasks.."
# What the items of the tasks say of a plan with none, as the stage needs none.
NO_TASK = "No task is left: the criteria rest on nothing the session has yet to find out"


def plan(goal: str, criteria: list, tasks: list, said: dict) -> dict:
    """The made of a call on the plan: its part, and every item of rn's plan checklist with its
    Good, said giving those of the goal, the criteria, the tasks and the stage; with no task, the
    tasks' heading left out and the items of the tasks read on the whole."""
    listed = ["## Tasks", *tasks] if tasks else []
    part = "\n\n".join([f"# {TITLE}", goal, "## Acceptance criteria", "\n".join(criteria), *listed])
    whole = "whole"
    at = [TASKS] if tasks else whole
    ids = [c.split(":")[0][2:] for c in criteria]
    goods = {
        "F-1": (
            (
                "From the title to the tasks the part follows F-1's template: the title, G1 under it,"
                " each criterion as `- AC<n>:`, and "
                + (
                    "each task's line ending with what it serves, its completion criterion and its"
                    " numbered actions, each saying who does it"
                    if tasks
                    else "no `## Tasks`, as no task is left"
                )
            ),
            whole,
        ),
        "B-1": (said["goal"], ["G1:"]),
        "B-2": (said["criteria"], [f"- {i}:" for i in ids]),
        "B-3": (said["tasks"] if tasks else NO_TASK, at),
        "B-4": (
            "Each action says who does it and what it does toward its task's completion"
            " criterion, each of turn's one work at its path" + said.get("actions", "")
            if tasks
            else NO_TASK,
            at,
        ),
        "B-8": (said["ground"] if tasks else NO_TASK, at),
        "B-5": (said["stage"], at),
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
    "tasks": "T1's result, the place the user chose, is accepted by its completion criterion, the"
    " choice kept as a decision of the plan, resting on the research",
    "actions": "; T1's research names its path in the session's folder as a research work",
    "ground": "T1 researches what the place rests on before the user chooses it, and hands the"
    " research by name to that choice",
    "stage": "In the plan stage, T1 alone is needed, as AC1's place rests on what the session has"
    " yet to find out",
}
# A plan made in the plan stage once no task is left, or that needs none.
PLAN_DONE = dict(PLAN_STAGE, stage="In the plan stage no task is left, the criteria giving G1")
DESIGN_STAGE = dict(
    PLAN_STAGE,
    tasks="T2's result, docs/greeting.md, is accepted by a contributor finding the line and its"
    " place on its first screen",
    actions="; T2's making names `docs/greeting.md` as a note work",
    ground="T2 confirms the greeting's words with the user before turn makes the note from them",
    stage="In the design stage, T2 makes the one document the purpose needs, docs/greeting.md",
)
BUILD_STAGE = dict(
    DESIGN_STAGE,
    tasks="T3's result, the change to README.md, is accepted by reading it and running"
    " `sh demo.sh` as the line says",
    actions="; T3's making names `README.md` as a note work, made from docs/greeting.md",
    ground="T3's change is made from docs/greeting.md, the document approved at the design"
    " sign-off",
    stage="In the build stage, T3 builds AC1 and AC2 in README.md",
)
PLAN_FIRST = plan(G1, [AC1_FIRST, AC2], [T1], PLAN_STAGE)
# The same plan with no task, as one the plan stage's first call makes where no gap needs a task.
PLAN_UNTASKED = plan(G1, [AC1_FIRST, AC2], [], PLAN_DONE)
# A plan whose goal holds no reason, as its purpose was kept with none, while its Good claims one:
# a Good its lines fall short of, with a point behind it that is the user's.
PLAN_BARE = plan(G1_BARE, [AC1_FIRST, AC2], [], PLAN_DONE)
# The plan made again once T1 is done, AC1 naming the place the user chose.
PLAN_PLACED = plan(G1, [AC1, AC2], [], PLAN_DONE)
PLAN_ASKED = plan(
    G1_ASK,
    [AC1, AC2, AC3],
    [],
    dict(
        PLAN_DONE,
        goal=WHY.replace("where to start,", "where to start and where to ask,"),
        criteria="Each criterion is answered yes or no by reading the README: AC1 the greeting"
        " line there, AC2 its telling to run `sh demo.sh`, AC3 its telling to open an issue to"
        " ask, with no link; together they give G1's greeting, where to start and where to ask, and with them"
        " its reason",
    ),
)
PLAN_DESIGN = plan(G1, [AC1, AC2], [T2], DESIGN_STAGE)
PLAN_BUILD = plan(G1, [AC1, AC2], [T3], BUILD_STAGE)
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
    "- L1: The hearing named no place for the greeting, so the plan took a task of research and a"
    f' question to find it, kept as "{PLACE_QUOTE}" in the commit of T1.2; for everyone\'s work,'
    " rn's hearing could ask, of a work that changes a file, where in the file the change goes."
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
                "Under the heading rn cut, each learning is `- L<n>:` saying what happened with"
                " the words it rests on, then where it would make later work better"
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
GREETING = (
    f"# Greeting\n\nThe line new contributors read first, right under README.md's title"
    f" `# demo`:\n\n> {LINE}\n"
)
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
ABOUT_READMES = (
    "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features"
    "/customizing-your-repository/about-readmes"
)
PLACE = f"""# Where the greeting goes

Asked for T1: where in README.md a line greeting new contributors goes.

Answer: right under the title `# demo`, above the README's one line and its `## Use`, puts the
greeting first in the README GitHub shows a visitor; where it goes is the user's to choose.

- README.md holds `# demo`, then `demo prints a greeting.`, then `## Use` (README.md, lines 1-5).
- GitHub's page on READMEs says: "If you put your README file in your repository's hidden .github,
  root, or docs directory, GitHub will recognize and automatically surface your README to
  repository visitors." ({ABOUT_READMES}, read {datetime.date.today():%Y-%m-%d}).

Not known: whether this project's visitors reach the README from GitHub's page or from a clone;
the user knows.
"""
RESEARCH_PLACE = {
    "files": {RESEARCH: PLACE},
    "goods": {
        "research.md": {
            "B-1": {
                "good": "The opening says what was asked, for T1, and its answer: right under the"
                " title `# demo`, first in what GitHub shows, the choice left to the user",
                "at": ["Asked for T1", "Answer:"],
            },
            "B-2": {
                "good": "Each fact names a source the reader can open: the README's own lines, and"
                " GitHub's page on READMEs, quoted, with the date it was read",
                "at": ["- README.md holds..repository visitors"],
            },
            "B-3": {
                "good": "What the research did not settle, where visitors read the README, is said"
                " as unknown, for the user",
                "at": ["Not known:"],
            },
            "B-4": {
                "good": "Each line gives the user choosing the place something they use",
                "at": "whole",
            },
        }
    },
}
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
    """The plan made, every Good holding, and put back: G1, AC1, AC2 and T1, Next T1's action
    1."""
    heard(p)
    put = made(p, PLAN_CCS, PLAN_FIRST)
    state(p, NEXT_T1, "The plan made: G1, AC1, AC2 and T1", "--put", put)


def t1_researched(p: Place) -> None:
    """T1's action 1 done, the research on the greeting's place made by turn, Next T1's action
    2."""
    planned(p)
    made(p, RESEARCH_CCS, RESEARCH_PLACE)
    state(p, NEXT_T1_2, "T1.1 done: where the greeting goes researched", "--done", "T1.1")


def plan_signoff(p: Place) -> None:
    """T1's action 2 done, the greeting's place kept as a decision of the plan, as it settles a
    criterion, T1 done and out of the steering, the plan made again with the place, and the plan
    sign-off waiting."""
    t1_researched(p)
    decide(
        p,
        "plan",
        "Place",
        "the greeting goes right under the README's title, the first line a contributor reads",
        f'T1.2: the user chose where the greeting goes: "{PLACE_QUOTE}", over the end of the README',
    )
    state(p, NEXT_T1_WEIGH, "T1.2 done: the greeting's place settled", "--done", "T1.2")
    put = made(p, PLAN_CCS, PLAN_PLACED)
    state(p, NEXT_PLAN_SIGNOFF, "The plan made again from T1: AC1 names the place", "--put", put)
    p.rn("proposal", "plan")


def typed(p: Place, words: str) -> None:
    """The user's command typed, written as Claude Code keeps it in a conversation's record, a
    record of its own among those of the repository, where rn's scripts read it."""
    top = p.git("rev-parse", "--show-toplevel")
    command, _, args = words.partition(" ")
    entry = {
        "type": "user",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cwd": top,
        "gitBranch": p.git("branch", "--show-current"),
        "message": {
            "role": "user",
            "content": f"<command-message>{command[1:]}</command-message>\n<command-name>"
            f"{command}</command-name>\n<command-args>{args}</command-args>",
        },
    }
    folder = record.folders(top)[0]
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, f"{uuid.uuid4()}.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def answered(p: Place, answer: str, next_step: str, opened: list, given: dict) -> None:
    """The user's answer at the sign-off typed and kept, and the stretch's learnings made and put
    back."""
    more = [arg for point in opened for arg in ("--open", point)]
    if answer == "approved":
        message = "The user approved the sign-off with /rn:ty"
        typed(p, "/rn:ty")
    else:
        message = f"The user sent the sign-off back with /rn:gm: {opened[0]}"
        typed(p, f"/rn:gm {opened[0]}")
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


def t2_worded(p: Place) -> None:
    """The documents heard, the plan made again with T2, and T2's action 1 done, the greeting's
    words kept as a decision of T2, Next T2's action 2."""
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


def design_approved(p: Place) -> None:
    """T2 done and out of the steering, changing nothing of the plan, the design approved with no
    learning, the plan made again with T3, and T3's action 1 done, Next T3's action 2."""
    t2_worded(p)
    made(p, note_ccs("t2", "docs/greeting.md", "README.md"), NOTE_GREETING)
    message = "T2.2 done: docs/greeting.md made, changing nothing of the plan"
    state(p, NEXT_DESIGN_SIGNOFF, message, "--done", "T2.2")
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


def deliverable_signoff(p: Place) -> None:
    """T3 done and out of the steering, changing nothing of the plan, no task left, the finished
    work used, and the deliverable sign-off waiting."""
    design_approved(p)
    made(p, note_ccs("t3", "README.md", "docs/greeting.md"), NOTE_README)
    message = "T3.2 done: README.md greets new contributors; no task is left"
    state(p, NEXT_FINISHED, message, "--done", "T3.2", "--stage", "deliverable")
    made(p, DELIVERABLE_CCS, FINISHED)
    state(p, NEXT_DELIVERABLE_SIGNOFF, "The finished work used: AC1 and AC2 done")
    p.rn("proposal", "deliverable")


def learnings_due(p: Place) -> None:
    """The finished work approved and the stretch's learning put back, the two learnings
    to put to the user, Next step 11."""
    deliverable_signoff(p)
    answered(p, "approved", NEXT_LEARNINGS, [], LEARNT_TWICE)


def l1_answered(p: Place) -> None:
    """L1 answered, taken for an issue not yet sent, kept in Open, Next L2."""
    learnings_due(p)
    state(p, NEXT_L2, "L1: the user chose an issue to lovaizu/ccpm alone", "--open", L1_OPEN)


# What a move must leave, each check with what it checks in words.
class Check(NamedTuple):
    """What a check checks, in words, and whether what a move left holds it."""

    what: str
    holds: Callable[[Seen], bool]


def steered(seen: Seen) -> steering.Steering | None:
    """The steering as the last commit holds it, where it holds its form."""
    if not seen.text or steering.out_of_form(seen.text):
        return None
    return steering.parsed(seen.text)


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
        return s is not None and (s.open == [steering.NOTHING_OPEN]) == nothing

    return Check("Open is `None.`" if nothing else "Open holds a point", holds)


def plan_has(words: str, held: bool = True) -> Check:
    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and (words in "\n".join(s.plan)) == held

    return Check(f"the plan {'holds' if held else 'does not hold'} `{words}`", holds)


def ticked(action: str) -> Check:
    def holds(seen: Seen) -> bool:
        s = steered(seen)
        task, _, number = action.partition(".")
        return s is not None and any(
            t.id == task and a is not None and (a.number, a.ticked) == (number, True)
            for t in steering.tasks_of(s.plan)
            for _, _, a in t.actions
        )

    return Check(f"{action} ticked", holds)


def done(task: str) -> Check:
    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and all(t.id != task for t in steering.tasks_of(s.plan))

    return Check(f"{task} done, out of the steering", holds)


def kept_learnings(seen: Seen) -> list:
    """Each learning of the session's learnings as the last commit holds them, none before any is
    made."""
    path = session.learnings_path(os.path.dirname(seen.steering))
    return [x for x in seen.texts.get(path, "").splitlines() if session.LEARNING.fullmatch(x)]


def learnings(n: int) -> Check:
    return Check(
        f"the session's learnings hold {n}",
        lambda s: bool(s.steering) and len(kept_learnings(s)) == n,
    )


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
    "none-answer": Case(
        "/rn:up <an answer> with no session, as after the conversation asking the languages was"
        " cleared",
        "up 1 (no session, words asking for no work)",
        nothing,
        [NO_SESSION],
        [(f"/rn:up {LANGUAGES_ANSWER}", [NO_SESSION, STAYS, NO_PR, JAPANESE, says("/rn:up")])],
        {},
    ),
    "fresh-answer": Case(
        "/rn:up <a letter> in a fresh conversation while a point is asked: the point asked again",
        "up 1 (Next, words answering a point this conversation has not shown), 3",
        purposed,
        [front("plan", "none"), next_has("Step 6"), decisions("plan", 1)],
        [("/rn:up a", [STAYS, decisions("plan", 1), ONE_POINT, JAPANESE])],
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
        {"plan": [PLAN_FIRST], "t1": [RESEARCH_PLACE]},
    ),
    "good": Case(
        "turn's result with every Good holding: checked at its lines and put back; with no task"
        " in it, the plan sign-off",
        "up 1, 6, 4 (the call, turn's line, every Good holding, --put), 9 (no task left)",
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
                    plan_has("## Tasks", held=False),
                    open_none(),
                    TURN_LINE,
                    *proposal("plan"),
                ],
            )
        ],
        {"plan": [PLAN_UNTASKED]},
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
        {"plan": [PLAN_BARE, PLAN_UNTASKED]},
    ),
    "asks": Case(
        "turn asks a question: asked as a point, the answer kept and sent to turn",
        "up 4 (turn's questions, SendMessage), 3",
        at_call,
        [next_has("Step 6"), returned("plan", 0)],
        [
            ("/rn:up", [returned("plan", 0), ONE_POINT, JAPANESE]),
            (
                USE_ANSWER,
                [KEPT, decisions("plan", 3), returned("plan", 1), front("plan", "plan")],
            ),
        ],
        {"plan": [QUESTIONS, PLAN_UNTASKED]},
    ),
    "task": Case(
        "a task's action of turn's, a research made in the session's folder, then one of the"
        " orchestrator's, each with a line before and after",
        "up 1, 5 (both kinds of action), 4 (a research work), 3",
        planned,
        [next_has("Step 5 of /rn:up on t1: action 1"), returned("t1", 0)],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    returned("t1", 1),
                    file_has(RESEARCH, "Answer:"),
                    ticked("T1.1"),
                    next_has("on t1"),
                    TURN_LINE,
                    ONE_POINT,
                    JAPANESE,
                ],
            )
        ],
        {"t1": [RESEARCH_PLACE]},
    ),
    "plan-signoff": Case(
        "a task's last action, the orchestrator's, the task done and what it brought weighed, the"
        " plan made again from it, then the plan sign-off",
        "up 1, 5 (the last action, what the task brought weighed), 3, 4 (the plan made again), 6, 9",
        t1_researched,
        [next_has("Step 5 of /rn:up on t1: action 2"), ticked("T1.1"), returned("plan", 1)],
        [
            ("/rn:up", [STAYS, ONE_POINT, JAPANESE]),
            (
                PLACE_ANSWER,
                [
                    MOVED,
                    KEPT,
                    decisions("plan", 3),
                    done("T1"),
                    returned("plan", 2),
                    plan_has("right under its title"),
                    *proposal("plan"),
                ],
            ),
        ],
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
        "a document's last action, made by turn in one call, then the design sign-off",
        "up 1, 5, 4 (a task's work), 7, 9",
        t2_worded,
        [front("design", "none"), next_has("Step 5 of /rn:up on t2: action 2"), returned("t2", 0)],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    returned("t2", 1),
                    done("T2"),
                    *proposal("design"),
                    says("docs/greeting.md"),
                ],
            )
        ],
        {"t2": [NOTE_GREETING]},
    ),
    "deliverable-signoff": Case(
        "the build's last action, the task weighed and the plan not made again as it changed"
        " nothing, the finished work used, the deliverable sign-off",
        "up 1, 5, 4, 8, 9",
        design_approved,
        [
            front("build", "none"),
            next_has("Step 5 of /rn:up on t3: action 2"),
            returned("plan", 4),
        ],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    done("T3"),
                    returned("plan", 4),
                    returned("deliverable", 1),
                    file_has("README.md", "Welcome, new contributor!"),
                    *proposal("deliverable"),
                ],
            )
        ],
        {"t3": [NOTE_README], "deliverable": [FINISHED]},
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
                [MOVED, KEPT, next_has("L2"), open_has("L1"), issues(0), ONE_POINT],
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

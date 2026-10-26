"""The cases of rn's move trials, one per move the steps of rn's skills take: the state each starts
from, made by rn's commands, the stand-in turn and the parts the orchestrator writes as the moves
before it would leave it, what that state must be for the step, the messages sent, what the
stand-in turn gives back for each work it is called on, and what each message's move must leave,
checked by script.

The session is the smallest piece of work that reaches every move: a line greeting new contributors
added to the README of a small project, with one task in the plan stage, whose research settles a
criterion with the user, one document, whose words the user answers again, one task building the
finished work, and two learnings, one general and one of the project's own."""

from __future__ import annotations

import datetime
import json
import os
import re
import shlex
import sys
import uuid
from typing import Callable, NamedTuple

from place import ALL_KEPT, ROOT, RULES, SEED, Place, Seen, kept_learnings, steered

sys.path.insert(0, os.path.join(ROOT, "rn", "scripts"))
import record
import session
import steering

import rn

# The user's words, in the conversation language their instructions set.
REQUEST = "/rn:up README に新しいコントリビューター向けの挨拶を一行足して"
# The feedback at the plan sign-off, a sign of the point behind it, where a new contributor asks,
# which it leaves open; and one that settles it with the goal's change, as the plan written again
# says where to ask in G1 too, which is also the answer to that point where FEEDBACK leaves it open.
FEEDBACK = (
    "挨拶を読んだ新しいコントリビューターは、質問したいときにどうすればいいか分からないと思います"
)
SETTLED = (
    "挨拶の行に、質問があれば issue を開くよう書いてください。リンクはいりません。目的にも、質問の"
    "窓口を伝えることを入れてください"
)
# Each answer in the user's own words, so the decision kept is the one the stand-in turn's reply
# was made from, whichever order rn puts its options in.
LANGUAGES_ANSWER = "会話は日本語、リポジトリは英語でお願いします"
DONE_ANSWER = (
    "README に、新しいコントリビューターを迎えて `sh demo.sh` を"
    "実行するよう伝える一行があることです"
)
WHY_ANSWER = "歓迎されていると感じて、早く最初の変更を出してもらうためです"
MOBILE_ANSWER = "いいえ、モバイルは調べなくていいです"
PLACE_ANSWER = "タイトルのすぐ下に置いてください"
L1_OPEN = "L1: an issue to lovaizu/ccpm alone, not yet sent"
SLUG = "greet-contributors"
TITLE = "Greet new contributors"
PR = "https://github.com/trial/demo/pull/1"
# The session's folder, named by the day rn.py start runs, as the state is made on the day the trial
# runs; and the research T1 makes there.
SESSION = f"{session.RECORD}/{datetime.date.today():%Y%m%d}-{SLUG}"
RESEARCH = f"{SESSION}/place.md"

# What rn.py ccs is given for each work, as the steps of /rn:up give it: nothing more for the works
# rn makes the same way every time, the plan, the learnings and the finished work; for a task's
# work, the receiver, their use and what they have, as rn.py takes the path and the kind from the
# action.
PLAN_CCS = ["ccs", "plan"]
LEARNINGS_CCS = ["ccs", "learnings"]
DELIVERABLE_CCS = ["ccs", "deliverable"]
RESEARCH_CCS = [
    "ccs",
    "t1.1",
    "--receiver",
    "the user deciding where the greeting goes, and the maker of each later work it is handed to",
    "--use",
    "deciding the greeting's place on checked facts instead of a guess",
    "--has",
    "README.md",
]


def note_ccs(work: str, path: str, has: str) -> list:
    """What rn.py ccs is given for a task's work of the kind note at the path, its reader as the
    note checklist's opening names them, with the earlier output it is made from."""
    return [
        "ccs",
        work,
        "--receiver",
        f"a contributor who opens {path}",
        "--use",
        "taking in the greeting line and doing what it says",
        "--has",
        has,
    ]


# Each Next the moves before a case keep, as the steps of /rn:up word it, those rn sets itself
# taken from rn.py.
NEXT_CALL = "Step 8 of /rn:up on plan: write the plan, step 3, as no point is left to hear"
NEXT_T1 = "Step 4 of /rn:up on T1: action 1, have turn research where the greeting goes"
NEXT_T1_2 = "Step 4 of /rn:up on T1: action 2, confirm the greeting's place with the user"
NEXT_T1_WEIGH = "Step 4 of /rn:up on T1: weigh what it brought"
NEXT_PLAN_SIGNOFF = "Step 5 of /rn:up on plan: stop at the plan sign-off"
NEXT_T2 = "Step 4 of /rn:up on T2: action 1, confirm the greeting's words with the user"
NEXT_T2_2 = "Step 4 of /rn:up on T2: action 2, have turn make docs/greeting.md"
NEXT_DESIGN_SIGNOFF = "Step 5 of /rn:up on design: stop at the design sign-off"
NEXT_T3 = "Step 4 of /rn:up on T3: action 1, confirm the line docs/greeting.md gives"
NEXT_T3_2 = "Step 4 of /rn:up on T3: action 2, have turn make the change to README.md"
NEXT_DELIVERABLE_SIGNOFF = "Step 5 of /rn:up on deliverable: stop at the deliverable sign-off"
NEXT_L1 = "Step 11 of /rn:up on L1: put it to the user"
NEXT_L2 = "Step 11 of /rn:up on L2: put it to the user"

# The plan, as the orchestrator writes it at each stage: the goal, the criteria and the tasks.
G1 = (
    "G1: New contributors are greeted in the README and told where to start, so they feel welcome"
    " and open their first change sooner."
)
AC1_FIRST = "- AC1: The README holds a line greeting new contributors."
AC1 = "- AC1: The README holds a line greeting new contributors, right under its title."
AC2 = "- AC2: The greeting line tells new contributors to start by running `sh demo.sh`."
T1 = f"""- T1: The greeting's place, chosen by the user from checked facts. Serves AC1.

  Completion criterion: the user has chosen where in README.md the greeting goes, from what the
  README holds and what GitHub shows of it first; checked by the choice kept as a decision of the
  plan resting on the research.

  - [ ] 1. Research what README.md holds above its first section and what GitHub shows of a README
    first, `{RESEARCH}` as a research work. turn.
  - [ ] 2. Confirm the greeting's place with the user, from that research. The orchestrator, with
    the user."""
T2 = """- T2: docs/greeting.md, giving the greeting's words and its place. Serves AC1 and AC2.

  Completion criterion: docs/greeting.md gives the greeting line and where in the README it goes;
  checked by a contributor finding both on its first screen.

  - [ ] 1. Confirm the greeting's words with the user, in the tone README.md is written in. The
    orchestrator, with the user.
  - [ ] 2. Make the note from the words settled, `docs/greeting.md` as a note work. turn."""
T3 = """- T3: README.md greeting new contributors. Serves AC1 and AC2.

  Completion criterion: README.md holds the line docs/greeting.md gives, right under its title;
  checked by reading README.md and running `sh demo.sh` as the line says.

  - [ ] 1. Confirm with the user the line docs/greeting.md gives and its place. The orchestrator,
    with the user.
  - [ ] 2. Make the change from docs/greeting.md, `README.md` as a note work. turn."""


def plan(goal: str, criteria: list, tasks: list) -> str:
    """The part of a call on the plan, as the orchestrator writes it: the title, the goal, the
    criteria and the tasks, the tasks' heading left out where none is."""
    listed = ["## Tasks", *tasks] if tasks else []
    part = "\n\n".join([f"# {TITLE}", goal, "## Acceptance criteria", "\n".join(criteria), *listed])
    return part + "\n"


PLAN_FIRST = plan(G1, [AC1_FIRST, AC2], [T1])
# The plan written again once T1 is done, AC1 naming the place the user chose.
PLAN_PLACED = plan(G1, [AC1, AC2], [])
PLAN_DESIGN = plan(G1, [AC1, AC2], [T2])
PLAN_BUILD = plan(G1, [AC1, AC2], [T3])
# What the stand-in turn asks while it researches the greeting's place, which the points put to
# the user did not settle.
QUESTIONS = {
    "questions": [
        {
            "question": "Should the research also find what GitHub's mobile app shows of a README"
            " first?",
            "recommended": "No: the user chooses the place from what README.md holds and what"
            " GitHub's page shows, which the research gives",
            "items": [{"checklist": "research.md", "item": "B-3"}],
        }
    ]
}

# The learnings, as the orchestrator writes them once the finished work is approved, each quoting a
# commit message the state-making below keeps.
PLACE_QUOTE = "the greeting goes right under the title"
LINE_QUOTE = "the greeting line as docs/greeting.md gives it"
L_PLACE = (
    "- L1: rn's first questions named no place for the greeting, so the plan took a task of"
    f' research and a question to find it, kept as "{PLACE_QUOTE}" in the commit keeping the'
    " user's choice of place; for everyone's work, rn could ask first, of a work that changes a"
    " file, where in the file the change goes."
)
L_TWICE = (
    "- L2: The plan written again after the design sign-off asked the user once more for the"
    " greeting line docs/greeting.md gave, which that sign-off had approved, kept as"
    f' "{LINE_QUOTE}" in the commit of the line\'s confirmation; for this repository, its plan'
    " checklist could ask that no action asks the user again what a sign-off approved."
)
LEARNT = f"{L_PLACE}\n{L_TWICE}\n"

# The works the tasks make, and the finished work used.
LINE = "Welcome, new contributor! Start by running `sh demo.sh`, then open a pull request."
# The words the user first chose for the line, which they then changed, the change quoted in the
# commit that kept it.
FIRST_LINE = "Welcome, new contributor! Open a pull request when you are ready."
CHANGED_QUOTE = "start by running `sh demo.sh`"
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

Answer: right under the title `# demo`, above the README's one line and its `## Use`, makes the
greeting the README's first line after its title, the README being what GitHub shows a
repository's visitors; where it goes is the user's to choose.

- README.md holds `# demo`, then `demo prints a greeting.`, then `## Use` (README.md, lines 1-5).
- GitHub's page on READMEs says: "If you put your README file in your repository's hidden .github,
  root, or docs directory, GitHub will recognize and automatically surface your README to
  repository visitors." ({ABOUT_READMES}, read {datetime.date.today():%Y-%m-%d}).

Not known: what part of the README a visitor's screen shows first, which GitHub's page does not
say and opening the repository's page on GitHub would show; and whether this project's visitors
reach the README from GitHub's page or from a clone, which the user knows.
"""
# The research, at the path the plan's action names, RESEARCH in the plans the state-making writes.
RESEARCH_PLACE = {
    "files": {"": PLACE},
    "goods": {
        "research.md": {
            "B-1": {
                "good": "The opening says what was asked, for T1, and its answer: right under the"
                " title `# demo`, the README's first line after it, the choice left to the user",
                "at": ["Asked for T1", "Answer:..the user's to choose"],
            },
            "B-2": {
                "good": "Each fact names a source the reader can open: the README's own lines, and"
                " GitHub's page on READMEs, quoted, with the date it was read",
                "at": ["- README.md holds..repository visitors"],
            },
            "B-3": {
                "good": "What the research did not settle, what GitHub shows of a README first and"
                " where visitors read it, is said as unknown, with what would settle each",
                "at": ["Not known:..which the user knows"],
            },
            "B-4": {
                "good": "Each line gives the user choosing the place something they use",
                "at": "whole",
            },
            "B-5": {
                "good": "Each term is plain or quoted as the README holds it, `# demo` and"
                " `## Use`",
                "at": "whole",
            },
        }
    },
}
# The issue turn makes of L1 once the user takes it for rn's makers, in the form of rn's issue
# checklist.
ISSUE = f"{SESSION}/issue-1.md"
ISSUE_TEXT = f"""# rn: the first questions leave where in a file a change goes

## What happened

rn's first questions named no place for the greeting in the file it changes, so the plan took a
task of research and a question to find it, kept as "{PLACE_QUOTE}".

## Why it matters

A user waits for a research task, and answers a later question, for a point rn could ask first.

## What it should be

/rn:up's first questions, in step 8 where it hears the purpose, ask, of a work that changes a
file, where in the file the change goes.

## Seen in

rn 0.9.0
"""
ISSUE_MADE = {
    "files": {ISSUE: ISSUE_TEXT},
    "goods": {
        "issue.md": {
            "F-1": {"good": "The issue follows the template, its title first", "at": "whole"},
            "B-1": {
                "good": "The title and What it should be name the change to /rn:up's first"
                " questions, and Why it matters what a user loses",
                "at": ["# rn:", "## Why it matters..## Seen in"],
            },
            "B-2": {
                "good": "What happened quotes the learning's words and holds nothing more of the"
                " user's work",
                "at": ["## What happened..## Why it matters"],
            },
            "B-3": {"good": "It holds one need, met by one change of rn's", "at": "whole"},
        }
    },
}
FINISHED = {
    "goods": {
        "deliverable.md": {
            "B-1": {
                "good": "Used as the user would: README.md greets new contributors right under"
                " its title (AC1) and tells them to start by running `sh demo.sh`, which runs and"
                " prints hello (AC2)",
                "at": ["Welcome"],
                "in": "README.md",
            }
        }
    }
}
# The user's addition to rn's plan checklist, made once they take the learning of the line asked
# again for their own checklist.
PLAN_ADDITION = ".rn/checklists/plan.md"
PLAN_ADDED = """---
name: plan
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Plan, this repository's addition

What this repository adds to rn's checklist for a plan, read by rn's orchestrator writing a plan
and by the user approving it.

A plan serves the user by taking what a sign-off approved as settled, asking only what no one has
decided yet.

## Benefit

### B-1: Nothing approved asked again

Scope: whole

Can the user tell that no action of the plan asks them again what a sign-off approved, such as the
lines of a document?

Look for: an action confirming with the user what an approved document gives.

Why: a point asked again spends the user's time on what they already decided.
"""
CHECKLIST_GOODS = {
    "F-1": "plan.md follows the template: the front matter, the title, the purpose, the idea, and"
    " `## Benefit` with B-1, with its Scope, its question and its Why; an addition holds only what"
    " it adds, so it has no Format section",
    "F-2": "Its version is 1, as no release has numbered it",
    "F-3": "made_from names checklist 1 and usability 1, the versions that stand now",
    "F-4": "Its item is B-1, counted up in Benefit",
    "B-1": "The opening says who reads it, rn's orchestrator writing a plan and the user approving"
    " it, and what it adds to rn's plan checklist",
    "B-2": "What the opening names, a plan that asks nothing approved again, has its item, B-1",
    "B-3": "Its one item asks one thing of the purpose, which rn's plan checklist does not ask",
    "B-4": "B-1 is answered by pointing at a plan's actions",
    "B-5": "B-1 asks one thing, with a sign of what is looked at",
}
PLAN_CHECKLIST = {
    "files": {PLAN_ADDITION: PLAN_ADDED},
    "goods": {"checklist.md": {i: {"good": g, "at": "whole"} for i, g in CHECKLIST_GOODS.items()}},
}
# The user's note checklist with an item added while the session runs, whose choice, where a
# contributor asks when stuck, no answer of the user's made.
NOTE_CHECKLIST = ".rn/checklists/note.md"
NOTE_ASKING = (
    SEED[NOTE_CHECKLIST]
    + """
### B-3: Where to ask, told

Scope: whole

Can the contributor who opens the note tell where to ask when they are stuck?

Why: a contributor who does not know where to ask gives up at the first question.
"""
)


def number(ccs: str) -> str:
    """The number of the call whose CCS is at the path."""
    return os.path.basename(ccs)[:4]


def written(p: Place, args: list, part: str) -> str:
    """The CCS of the plan or the learnings written and their part cut, as rn.py ccs does, then the
    part written as given and checked by the command rn.py printed, as the orchestrator writes it;
    gives the call's number."""
    cut = json.loads(p.rn(*args))
    p.write(cut["part"], part)
    p.run(*shlex.split(cut["check"]))
    return number(cut["ccs"])


def made(p: Place, args: list, given: dict) -> str:
    """The work's CCS written and the call, the first line rn.py ccs printed, returned by the
    stand-in turn with what is given; gives the call's number."""
    called = p.rn(*args).splitlines()[0]
    p.turned(called, given)
    return number(json.loads(called)["ccs"])


def state(p: Place, next_step: str | None, message: str, *more: str) -> None:
    """rn.py state, keeping the move with the options given, and with Next where one is given, as
    rn keeps Next, or sets it at a stage's end, where none is."""
    given = [] if next_step is None else ["--next", next_step]
    p.rn("state", *given, *more, "--message", message)


def decide(p: Place, work: str, title: str, says: str, message: str) -> None:
    """rn.py decide, keeping one decision of the work."""
    p.rn("decide", work, "--title", title, "--says", says, "--message", message)


# The moves before a case, each kept by rn's commands as the steps of rn's skills keep them, each
# building on the one before; the stand-in turn returning each call.
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
    """The plan written and put back: G1, AC1, AC2 and T1, Next T1's action 1."""
    heard(p)
    put = written(p, PLAN_CCS, PLAN_FIRST)
    state(p, NEXT_T1, "The plan made: G1, AC1, AC2 and T1", "--put", put)


def t1_researched(p: Place) -> None:
    """T1's action 1 done, the research on the greeting's place made by turn, Next T1's action
    2."""
    planned(p)
    made(p, RESEARCH_CCS, RESEARCH_PLACE)
    state(p, NEXT_T1_2, "T1.1 done: where the greeting goes researched", "--done", "T1.1")


def plan_signoff(p: Place) -> None:
    """T1's action 2 done, the greeting's place kept as a decision of the plan, as it settles a
    criterion, T1 done and out of the steering, the plan written again with the place, and the plan
    sign-off waiting."""
    t1_researched(p)
    decide(
        p,
        "plan",
        "Place",
        "the greeting goes right under the README's title, the first line a contributor reads",
        f'T1.2: the user chose where the greeting goes: "{PLACE_QUOTE}", over the end of the'
        " README",
    )
    state(p, NEXT_T1_WEIGH, "T1.2 done: the greeting's place settled", "--done", "T1.2")
    put = written(p, PLAN_CCS, PLAN_PLACED)
    state(p, NEXT_PLAN_SIGNOFF, "The plan written again from T1: AC1 names the place", "--put", put)
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


def answered(p: Place, answer: str, opened: list) -> None:
    """The user's answer at the sign-off typed and kept, Next as rn sets it."""
    more = [arg for point in opened for arg in ("--open", point)]
    if answer == "approved":
        message = "The user approved the sign-off with /rn:ty"
        typed(p, "/rn:ty")
    else:
        message = f"The user sent the sign-off back with /rn:gm: {opened[0]}"
        typed(p, f"/rn:gm {opened[0]}")
    p.rn("answer", answer, *more, "--message", message)


def fed_back(p: Place) -> None:
    """The plan sign-off answered with the feedback, kept in Open, Next step 6."""
    plan_signoff(p)
    answered(p, "feedback", [FEEDBACK])


def settled_back(p: Place) -> None:
    """The plan sign-off answered with the feedback that settles its point, kept in Open, Next
    step 6."""
    plan_signoff(p)
    answered(p, "feedback", [SETTLED])


def plan_approved(p: Place) -> None:
    """The plan approved, the design stage begun, Next step 9."""
    plan_signoff(p)
    answered(p, "approved", [])


def t2_planned(p: Place) -> None:
    """The documents heard and the plan written again with T2, Next T2's action 1."""
    plan_approved(p)
    decide(
        p,
        "plan",
        "Documents",
        "docs/greeting.md, a note work, holding the greeting's words and its place in the README",
        "Documents: the user chose one note for the greeting, over none",
    )
    put = written(p, PLAN_CCS, PLAN_DESIGN)
    state(p, NEXT_T2, "The plan written again: T2 writes docs/greeting.md", "--put", put)


def t2_unasked(p: Place) -> None:
    """As t2_planned, with an item added to the user's note checklist that no decision answers,
    and the greeting's words kept as a decision of T2 while its action 1 is still taken, Next T2's
    action 1."""
    t2_planned(p)
    p.write(NOTE_CHECKLIST, NOTE_ASKING)
    state(p, NEXT_T2, "The user's note checklist asks where a contributor asks when stuck")
    decide(p, "t2.2", "Words", LINE, "T2.1: the user chose the greeting's words")


def t2_worded(p: Place) -> None:
    """As t2_planned, and T2's action 1 done, the greeting's words kept as a decision of T2 and
    then replaced, as the user answered them again, Next T2's action 2."""
    t2_planned(p)
    decide(p, "t2.2", "Words", FIRST_LINE, "T2.1: the user chose the greeting's words")
    decide(
        p,
        "t2.2",
        "Words",
        LINE,
        f'T2.1 asked again: the user changed the words to "{CHANGED_QUOTE}", as the first words'
        " named no first step",
    )
    state(p, NEXT_T2_2, "T2.1 done: the words settled", "--done", "T2.1")


def design_approved(p: Place) -> None:
    """T2 done and out of the steering, changing nothing of the plan, the design approved, the plan
    written again with T3, and T3's action 1 done, Next T3's action 2."""
    t2_worded(p)
    made(p, note_ccs("t2.2", "docs/greeting.md", "README.md"), NOTE_GREETING)
    message = "T2.2 done: docs/greeting.md made, changing nothing of the plan"
    state(p, NEXT_DESIGN_SIGNOFF, message, "--done", "T2.2")
    p.rn("proposal", "design")
    answered(p, "approved", [])
    put = written(p, PLAN_CCS, PLAN_BUILD)
    state(p, NEXT_T3, "The plan written again: T3 adds the line to README.md", "--put", put)
    decide(
        p,
        "t3.2",
        "Line",
        "the greeting line as docs/greeting.md gives it, right under the README's title",
        f'T3.1: the user confirmed "{LINE_QUOTE}"',
    )
    state(p, NEXT_T3_2, "T3.1 done", "--done", "T3.1")


def deliverable_signoff(p: Place) -> None:
    """T3 done and out of the steering, changing nothing of the plan, no task left, the finished
    work used, and the deliverable sign-off waiting."""
    design_approved(p)
    made(p, note_ccs("t3.2", "README.md", "docs/greeting.md"), NOTE_README)
    message = "T3.2 done: README.md greets new contributors; no task is left"
    state(p, None, message, "--done", "T3.2", "--stage", "deliverable")
    made(p, DELIVERABLE_CCS, FINISHED)
    state(p, NEXT_DELIVERABLE_SIGNOFF, "The finished work used: AC1 and AC2 done")
    p.rn("proposal", "deliverable")


def learnings_due(p: Place) -> None:
    """The finished work approved, and the learnings written from the history and put back, the
    two to put to the user, Next step 11 on L1."""
    deliverable_signoff(p)
    answered(p, "approved", [])
    put = written(p, LEARNINGS_CCS, LEARNT)
    state(p, NEXT_L1, "The learnings written: L1 and L2", "--put", put)


def l1_answered(p: Place) -> None:
    """L1 answered, taken for an issue not yet sent, kept as the decision of the issue's work and in
    Open, Next L2."""
    learnings_due(p)
    decide(p, "issue-1", "Learning", L_PLACE[len("- L1: ") :], "L1: for an issue to rn's makers")
    state(p, NEXT_L2, "L1: the user chose an issue to lovaizu/ccpm alone", "--open", L1_OPEN)


# What a move must leave, each check with what it checks in words.
class Check(NamedTuple):
    """What a check checks, in words, and whether what a move left holds it."""

    what: str
    holds: Callable[[Seen], bool]


def front(stage: str, signoff: str) -> Check:
    """The check that the steering is at the stage, waiting at the sign-off."""

    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and (s.keys["stage"], s.keys["signoff"]) == (stage, signoff)

    return Check(f"the steering at the {stage} stage, sign-off {signoff}", holds)


def next_has(words: str) -> Check:
    """The check that the steering's Next holds the words."""

    return Check(f"Next holds `{words}`", lambda s: words in getattr(steered(s), "next", ""))


def open_has(words: str, held: bool = True) -> Check:
    """The check that the steering's Open holds the words, or no longer does."""

    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and (words in "\n".join(s.open)) == held

    return Check(f"Open {'holds' if held else 'no longer holds'} `{words}`", holds)


def open_none(nothing: bool = True) -> Check:
    """The check that the steering's Open is `None.`, or holds a point."""

    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and (s.open == [steering.NOTHING_OPEN]) == nothing

    return Check("Open is `None.`" if nothing else "Open holds a point", holds)


def plan_has(words: str, held: bool = True) -> Check:
    """The check that the steering's plan holds the words, or does not."""

    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and (words in "\n".join(s.plan)) == held

    return Check(f"the plan {'holds' if held else 'does not hold'} `{words}`", holds)


def ticked(action: str) -> Check:
    """The check that the action, `T<n>.<k>`, is ticked."""

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
    """The check that the task is done, out of the steering."""

    def holds(seen: Seen) -> bool:
        s = steered(seen)
        return s is not None and all(t.id != task for t in steering.tasks_of(s.plan))

    return Check(f"{task} done, out of the steering", holds)


def learnings(n: int) -> Check:
    """The check that the session's learnings hold n."""

    return Check(
        f"the session's learnings hold {n}",
        lambda s: bool(s.steering_path) and len(kept_learnings(s)) == n,
    )


def returned(work: str, n: int) -> Check:
    """The check that n calls on the work were returned and kept."""

    def holds(seen: Seen) -> bool:
        return len([c for c in seen.calls if c.work == work and c.returned]) == n

    return Check(f"{n} calls on {work} returned and kept", holds)


def called(work: str, n: int, least: bool = False) -> Check:
    """The check that n calls on the work were kept, or n or more."""

    def holds(seen: Seen) -> bool:
        count = len([c for c in seen.calls if c.work == work])
        return count >= n if least else count == n

    return Check(f"{n}{' or more' if least else ''} calls on {work} kept", holds)


def no_result(work: str) -> Check:
    """The check that no call on the work has a result of turn's, as the orchestrator writes it."""

    def holds(seen: Seen) -> bool:
        return not any(c.returned for c in seen.calls if c.work == work)

    return Check(f"no call on {work} returned by turn", holds)


def learnt_some() -> Check:
    """The check that the session's learnings hold one or more."""

    return Check(
        "the session's learnings hold one or more",
        lambda s: bool(s.steering_path) and len(kept_learnings(s)) > 0,
    )


def decisions(work: str, n: int) -> Check:
    """The check that the work's latest call holds n decisions or more."""

    def holds(seen: Seen) -> bool:
        last = [c for c in seen.calls if c.work == work][-1:]
        return bool(last) and last[0].decisions >= n

    return Check(f"the latest call on {work} holds {n} decisions or more", holds)


def pr(draft: bool) -> Check:
    """The check that one pull request into main is there, a draft or marked ready."""

    def holds(seen: Seen) -> bool:
        prs = seen.gh["prs"]
        return len(prs) == 1 and prs[0]["isDraft"] == draft and prs[0]["baseRefName"] == "main"

    return Check(f"one pull request into main, {'draft' if draft else 'marked ready'}", holds)


def issues(n: int) -> Check:
    """The check that n issues were opened, each on lovaizu/ccpm."""

    def holds(seen: Seen) -> bool:
        return len(seen.gh["issues"]) == n and all(
            i["repo"] == "lovaizu/ccpm" for i in seen.gh["issues"]
        )

    return Check(f"{n} issues opened on lovaizu/ccpm", holds)


def file_has(path: str, words: str) -> Check:
    """The check that the file at the path, as the last commit holds it, holds the words."""

    return Check(f"{path} holds `{words}`", lambda s: words in s.texts.get(path, ""))


def says(words: str) -> Check:
    """The check that the reply holds the words."""

    return Check(f"the reply holds `{words}`", lambda s: words in s.reply)


NO_SESSION = Check("no session on the branch", lambda s: not s.steering_path)
NO_PR = Check("no pull request opened", lambda s: not s.gh["prs"])
STAYS = Check("no commit made", lambda s: s.commits == 0)
MOVED = Check("a commit made", lambda s: s.commits > 0)
KEPT = Check(ALL_KEPT, RULES[ALL_KEPT])
JAPANESE = Check("the reply in Japanese", lambda s: bool(re.search(r"[぀-ヿ一-鿿]", s.reply)))
ONE_POINT = Check(
    "the reply asks one point, `▶` once, with options `a.` and `b.`",
    lambda s: s.reply.count("▶") == 1 and all(re.search(rf"(?m)^\W*{x}\. ", s.reply) for x in "ab"),
)
# A line of turn's, put into the conversation language, may take that language's colon.
TURN_LINE = Check(
    "a line of turn's passed on to the user",
    lambda s: any(t.strip().startswith(("turn:", "turn：")) for t in s.said),
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
        front(signoff, signoff),
        next_has(rn.WAITING.format(signoff)),
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
        "up 1 (no session, words), 7 (the first point), 2 (the point's form)",
        nothing,
        [NO_SESSION],
        [(REQUEST, [NO_SESSION, STAYS, NO_PR, ONE_POINT, JAPANESE])],
        {},
    ),
    "languages": Case(
        "the languages answered: the session started, the first point of the plan asked",
        "up 7 (start), 8 (hear the purpose), 2 (ask)",
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
                    next_has("Step 8"),
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
        "up 1 (Next, words answering a point this conversation has not shown), 2",
        purposed,
        [front("plan", "none"), next_has("Step 8"), decisions("plan", 1)],
        [("/rn:up a", [STAYS, decisions("plan", 1), ONE_POINT, JAPANESE])],
        {},
    ),
    "point": Case(
        "/rn:up in a fresh conversation while a point is asked, then the point answered",
        "up 1 (Next), 8, 2 (the next point, nothing settled asked again; the answer kept)",
        purposed,
        [front("plan", "none"), next_has("Step 8"), decisions("plan", 1)],
        [
            ("/rn:up", [STAYS, ONE_POINT, JAPANESE]),
            (DONE_ANSWER, [MOVED, KEPT, decisions("plan", 2)]),
        ],
        {"t1.1": [RESEARCH_PLACE]},
    ),
    "good": Case(
        "the plan written by the orchestrator from the points heard, checked against rn's plan"
        " checklist and put back, with no call to turn",
        "up 1, 8, 3 (the plan's part written, checked, --put)",
        at_call,
        [next_has("Step 8"), decisions("plan", 2), called("plan", 1)],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    called("plan", 1, least=True),
                    no_result("plan"),
                    plan_has("G1:"),
                    plan_has("- AC2:"),
                    plan_has("sh demo.sh"),
                    JAPANESE,
                ],
            )
        ],
        {"t1.1": [RESEARCH_PLACE]},
    ),
    "short": Case(
        "the plan's checklist asking what no decision gives, the reason behind the goal: asked as"
        " a point before the plan is put back, then the plan written with it",
        "up 3 (an item no line can give without the user's point), 2, 3 again (--put)",
        unreasoned_at_call,
        [next_has("Step 8"), called("plan", 1)],
        [
            ("/rn:up", [plan_has("G1:", held=False), ONE_POINT, JAPANESE]),
            (
                WHY_ANSWER,
                [
                    KEPT,
                    decisions("plan", 3),
                    called("plan", 2, least=True),
                    no_result("plan"),
                    plan_has("G1:"),
                    open_none(),
                ],
            ),
        ],
        {"t1.1": [RESEARCH_PLACE]},
    ),
    "asks": Case(
        "turn asks a question while it makes a task's work: asked as a point, the answer kept and"
        " sent to turn",
        "up 4, 3 (turn's questions, SendMessage), 2",
        planned,
        [next_has("Step 4 of /rn:up on T1: action 1"), returned("t1.1", 0)],
        [
            ("/rn:up", [returned("t1.1", 0), ONE_POINT, JAPANESE]),
            (
                MOBILE_ANSWER,
                [
                    KEPT,
                    decisions("t1.1", 1),
                    returned("t1.1", 1),
                    file_has(RESEARCH, "Answer:"),
                    ticked("T1.1"),
                ],
            ),
        ],
        {"t1.1": [QUESTIONS, RESEARCH_PLACE]},
    ),
    "task": Case(
        "a task's action of turn's, a research made in the session's folder, then one of the"
        " orchestrator's, each with a line before and after",
        "up 1, 4 (both kinds of action), 3 (a research work), 2",
        planned,
        [next_has("Step 4 of /rn:up on T1: action 1"), returned("t1.1", 0)],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    returned("t1.1", 1),
                    file_has(RESEARCH, "Answer:"),
                    ticked("T1.1"),
                    next_has("Step 4"),
                    TURN_LINE,
                    ONE_POINT,
                    JAPANESE,
                ],
            )
        ],
        {"t1.1": [RESEARCH_PLACE]},
    ),
    "plan-signoff": Case(
        "a task's last action, the orchestrator's, the task done and what it brought weighed, the"
        " plan written again from it, the place the user answered written into a criterion in the"
        " plan's words with nothing asked, then the plan sign-off",
        "up 1, 4 (the last action, what the task brought weighed), 2, 3 (the plan written again),"
        " 8, 5",
        t1_researched,
        [next_has("Step 4 of /rn:up on T1: action 2"), ticked("T1.1"), called("plan", 1)],
        [
            ("/rn:up", [STAYS, ONE_POINT, JAPANESE]),
            (
                PLACE_ANSWER,
                [
                    MOVED,
                    KEPT,
                    decisions("plan", 3),
                    done("T1"),
                    called("plan", 2, least=True),
                    no_result("plan"),
                    plan_has("title"),
                    *proposal("plan"),
                ],
            ),
        ],
        {},
    ),
    "resume-signoff": Case(
        "/rn:up in a fresh conversation while the plan sign-off waits",
        "up 1 (a sign-off waiting), 5 (the same proposal, nothing kept)",
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
        "/rn:ty at the plan sign-off: approved, going on with no learning made",
        "ty 1, 2, 3 (up 9, 2)",
        plan_signoff,
        [front("plan", "plan"), learnings(0)],
        [
            (
                "/rn:ty",
                [
                    MOVED,
                    KEPT,
                    front("design", "none"),
                    called("learnings", 0),
                    learnings(0),
                    next_has("Step 9"),
                    ONE_POINT,
                ],
            )
        ],
        {},
    ),
    "gm-plan": Case(
        "/rn:gm <feedback> at the plan sign-off: kept whole in Open, no learning made, stop",
        "gm 1, 2, 3",
        plan_signoff,
        [front("plan", "plan"), learnings(0)],
        [
            (
                f"/rn:gm {FEEDBACK}",
                [
                    MOVED,
                    KEPT,
                    front("plan", "none"),
                    next_has("Step 6"),
                    open_has(FEEDBACK),
                    called("learnings", 0),
                    learnings(0),
                    JAPANESE,
                    says("/rn:up"),
                ],
            )
        ],
        {},
    ),
    "after-feedback": Case(
        "/rn:up in a fresh conversation after feedback that leaves the point behind it open: that"
        " point asked, the plan written again, the same sign-off",
        "up 1, 6, 2, 3, 5 (what changed)",
        fed_back,
        [front("plan", "none"), next_has("Step 6"), open_has(FEEDBACK)],
        [
            ("/rn:up", [STAYS, ONE_POINT, open_has(FEEDBACK)]),
            (
                SETTLED,
                [
                    MOVED,
                    KEPT,
                    called("plan", 3, least=True),
                    no_result("plan"),
                    plan_has("issue"),
                    open_has(FEEDBACK, held=False),
                    *proposal("plan"),
                ],
            ),
        ],
        {},
    ),
    "settled-feedback": Case(
        "/rn:up in a fresh conversation after feedback that settles the point behind it: the"
        " feedback kept as its answer, nothing asked again, the plan written again, the same"
        " sign-off",
        "up 1, 6, 2 (the feedback the answer), 3, 5 (what changed)",
        settled_back,
        [front("plan", "none"), next_has("Step 6"), open_has(SETTLED)],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    called("plan", 3, least=True),
                    no_result("plan"),
                    plan_has("issue"),
                    open_has(SETTLED, held=False),
                    *proposal("plan"),
                ],
            ),
        ],
        {},
    ),
    "checklist-point": Case(
        "a work's hearing finding a point its checklist raises that no answer made, where a"
        " contributor asks when stuck: asked before turn is called",
        "up 1, 4 (an action of the orchestrator's), 2 (the checklists read, an item's choice"
        " asked)",
        t2_unasked,
        [
            front("design", "none"),
            next_has("Step 4 of /rn:up on T2: action 1"),
            decisions("t2.2", 1),
            file_has(NOTE_CHECKLIST, "### B-3:"),
        ],
        [("/rn:up", [STAYS, returned("t2.2", 0), ONE_POINT, JAPANESE])],
        {"t2.2": [NOTE_GREETING]},
    ),
    "design-signoff": Case(
        "a document's last action, made by turn in one call, then the design sign-off",
        "up 1, 4, 3 (a task's work), 9, 5",
        t2_worded,
        [
            front("design", "none"),
            next_has("Step 4 of /rn:up on T2: action 2"),
            returned("t2.2", 0),
        ],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    returned("t2.2", 1),
                    done("T2"),
                    *proposal("design"),
                    says("docs/greeting.md"),
                ],
            )
        ],
        {"t2.2": [NOTE_GREETING]},
    ),
    "deliverable-signoff": Case(
        "the build's last action, the task weighed and the plan not written again as it changed"
        " nothing, the finished work used, the deliverable sign-off",
        "up 1, 4, 3, 10, 5",
        design_approved,
        [
            front("build", "none"),
            next_has("Step 4 of /rn:up on T3: action 2"),
            called("plan", 4),
        ],
        [
            (
                "/rn:up",
                [
                    MOVED,
                    KEPT,
                    done("T3"),
                    called("plan", 4),
                    returned("deliverable", 1),
                    file_has("README.md", "Welcome, new contributor!"),
                    *proposal("deliverable"),
                ],
            )
        ],
        {"t3.2": [NOTE_README], "deliverable": [FINISHED]},
    ),
    "ty-deliverable": Case(
        "/rn:ty at the deliverable sign-off: approved, the learnings looked for once in the"
        " history, written and put back, the first learning put",
        "ty 1, 2, 3 (up 11: the history, the search, up 3 on learnings, the first learning put)",
        deliverable_signoff,
        [front("deliverable", "deliverable"), learnings(0)],
        [
            (
                "/rn:ty",
                [
                    MOVED,
                    KEPT,
                    front("learnings", "none"),
                    called("learnings", 1, least=True),
                    no_result("learnings"),
                    learnt_some(),
                    next_has("Step 11"),
                    ONE_POINT,
                ],
            )
        ],
        {},
    ),
    "learning": Case(
        "the learnings put one per message, the first taken for an issue",
        "up 1, 11 (one learning per message, each answer kept, an issue's as its decision)",
        learnings_due,
        [front("learnings", "none"), learnings(2), next_has("Step 11")],
        [
            ("/rn:up", [STAYS, ONE_POINT, JAPANESE]),
            (
                "issue だけに送ってください",
                [
                    MOVED,
                    KEPT,
                    next_has("L2"),
                    decisions("issue-1", 1),
                    open_none(nothing=False),
                    issues(0),
                    ONE_POINT,
                ],
            ),
        ],
        {},
    ),
    "last": Case(
        "the last learning taken for the checklist, the issue shown and sent, the pull request"
        " marked ready",
        "up 1, 11 (the issue made, up 3, shown and sent; the checklist made, up 3; finished)",
        l1_answered,
        [front("learnings", "none"), next_has("L2")],
        [
            ("/rn:up", [STAYS, ONE_POINT]),
            (
                "このリポジトリの plan のチェックリストだけに足してください",
                [
                    MOVED,
                    KEPT,
                    decisions("checklist-plan", 1),
                    returned("issue-1", 1),
                    file_has(ISSUE, "## What it should be"),
                    issues(0),
                ],
            ),
            (
                "はい",
                [
                    KEPT,
                    issues(1),
                    returned("checklist-plan", 1),
                    file_has(PLAN_ADDITION, "### B-1:"),
                    pr(draft=False),
                    front("finished", "none"),
                    says(PR),
                ],
            ),
        ],
        {"issue-1": [ISSUE_MADE], "checklist-plan": [PLAN_CHECKLIST]},
    ),
}

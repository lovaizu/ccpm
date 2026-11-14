"""What the unit cases of Lane's parts build their inputs from: the walkthrough's laid set, Runs at
the moments the walkthrough meets, and moments of a conversation in the guard's form, each in the
words of Lane's README walkthrough, which is the parts' specification."""

from __future__ import annotations

from typing import Any

from domain.event import CALL, COMMAND, Call, Event
from domain.laid_set import NO_MORE, START, LaidSet, Lane, Move, Route
from domain.run_record import PERSON, Result, Run, Start

ROOT = "/repo"
PLUGIN_ROOT = "/repo/changelog"
SESSION = "4344a6c5-dc82-48d7-9cfd-249b08288cea"
RESULT_PY = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py"
CARRY_OUT = "Carry out your steps"

RUN_ONLY = "Run only `git log --oneline`."
WRITE_ONLY = "Write only `CHANGELOG.md`."
WRITER_END = f"End by running `{RESULT_PY} writer written`."
REVIEWER_END = f"End by running `{RESULT_PY} reviewer more` or `{RESULT_PY} reviewer good`."
SKILL_STEP = (
    "Start each subagent you are told to start, until you are told to start no more. End by"
    f" running `{RESULT_PY} write good`."
)

LANES = (
    Lane("write", 1, "skills/write/SKILL.md", "gives_result", ("good",), SKILL_STEP),
    Lane("writer", 2, "agents/writer.md", "run_only", ("git log --oneline",), RUN_ONLY),
    Lane("writer", 3, "agents/writer.md", "write_only", ("CHANGELOG.md",), WRITE_ONLY),
    Lane("writer", 4, "agents/writer.md", "gives_result", ("written",), WRITER_END),
    Lane("reviewer", 2, "agents/reviewer.md", "gives_result", ("more", "good"), REVIEWER_END),
)
ROUTES = (
    Route("first", (Move(START, "writer"),)),
    Route("writer written", (Move(START, "reviewer"),)),
    Route("reviewer more", (Move(START, "writer"),)),
    Route("reviewer good", (Move(NO_MORE),)),
)


def laid_set(**fields: Any) -> LaidSet:
    """The laid set of the walkthrough's `changelog`, with the fields given in place of its own."""
    given: dict[str, Any] = {
        "plugin": "changelog",
        "skill": "write",
        "roles": ("write", "writer", "reviewer"),
        "lanes": LANES,
        "routes": ROUTES,
    }
    given.update(fields)
    return LaidSet(**given)


def run(**fields: Any) -> Run:
    """A Run of `changelog` that a person's `/changelog:write` started, with the fields given."""
    given: dict[str, Any] = {
        "plugin": "changelog",
        "skill": "write",
        "session": SESSION,
        "by": PERSON,
    }
    given.update(fields)
    return Run(**given)


def writer_running(**fields: Any) -> Run:
    """The Run once the main conversation started writer, subagent `a1`, which runs."""
    started = Start(1, "writer", CARRY_OUT, agent="a1", running=True)
    return run(starts=[started], **fields)


def writer_gave_written() -> Run:
    """The Run once writer, subagent `a1`, gave `written` and ended, so reviewer's start is due."""
    started = Start(1, "writer", CARRY_OUT, agent="a1", running=False)
    return run(
        starts=[started],
        results=[Result("writer", "written", "a1", 1)],
        moves=[Move(START, "reviewer")],
        texts={"reviewer": (CARRY_OUT, {})},
    )


def event(moment: str, **fields: Any) -> Event:
    """A moment of the conversation in the guard's form, at the root of the repository."""
    return Event(moment, SESSION, ROOT, ROOT, **fields)


def command(text: str, agent: str = "", role: str = "") -> Event:
    """A call of a shell command, by the subagent where one is given, else the main conversation."""
    return event(CALL, agent=agent, role=role, call=Call(COMMAND, command=text))

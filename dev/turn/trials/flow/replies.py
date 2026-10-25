"""The replies the stand-in roles of the flow trial give, by the way the run takes, each built from
the pieces the ways share: the README the generator writes, with or without its license, its claim
and the first user's reading of it, and the learner's lessons."""

from __future__ import annotations

from typing import Any

from shared import UNLICENSED

CHECKLIST = "checklist.md"
USE = "## Use\n\nRun `sh demo.sh`."
LICENSE = "\n\n## License\n\nMIT.\n"
# The README with a license, and with one and what demo prints, beside the one with none.
LICENSED = f"# demo\n\ndemo prints a greeting.\n\n{USE}{LICENSE}"
SAID = f"# demo\n\ndemo prints a greeting.\n\n{USE} It prints `Hello`.{LICENSE}"
# What running demo as its Use says gives the reader, as the README says it or not.
RAN = "Running `sh demo.sh` as this part says, the reader sees demo print Hello"
RUN = f"{RAN}, so learns what demo does."
RUN_SAID = f"{RAN}, as the part says it does."
MIT = {
    "checklist": CHECKLIST,
    "item": "B-1",
    "good": "The reader learns demo is under MIT.",
    "lines": ["README.md:11-11"],
}
STOP = {
    "checklist": CHECKLIST,
    "item": "B-1",
    "places": ["README.md:1-7"],
    "did": "read the whole README for the terms on which I may use demo",
    "lacking": "under which license I may use it",
}
CHECKED = "every page of every record"


def parts(run: str, licensed: bool) -> dict[str, Any]:
    """B-2, a Good in each part of the README, with the part of its license where it has one."""
    found = [
        {
            "part": "README.md:1-4",
            "good": "The reader learns what demo does.",
            "lines": ["README.md:3-3"],
        },
        {"part": f"README.md:5-{8 if licensed else 7}", "good": run, "lines": ["README.md:7-7"]},
    ]
    if licensed:
        terms = "The reader learns on what terms they may use demo."
        found.append({"part": "README.md:9-11", "good": terms, "lines": ["README.md:11-11"]})
    return {"checklist": CHECKLIST, "item": "B-2", "parts": found}


def made(write: str, *items: dict[str, Any], questions: tuple = ()) -> dict[str, Any]:
    """The generator writing the README and running demo, then claiming the items."""
    reply = {"items": list(items), "questions": list(questions)}
    return {"write": write, "run": ["sh demo.sh"], "reply": reply}


def read(*items: dict[str, Any]) -> dict[str, Any]:
    """The first user's reading of the items."""
    return {"reply": {"items": list(items)}}


def learnt(*lessons: dict[str, Any]) -> dict[str, Any]:
    """The learner's lessons."""
    return {"reply": {"lessons": list(lessons), "checked": CHECKED}}


def lesson(said: str, whose: str) -> dict[str, Any]:
    """A lesson resting on the first user's stop, in the record of the second agent of the run."""
    return {"lesson": said, "whose": whose, "grounds": [{"record": 2, "quote": STOP["lacking"]}]}


# The generator's claims and the first user's readings, of the README with no license and with one.
SHORT = made(
    UNLICENSED,
    dict(MIT, good="The reader learns the terms of use.", lines=["README.md:1-7"]),
    parts(RUN, False),
)
WHOLE = made(LICENSED, MIT, parts(RUN, True))
STOPPED = read(STOP, parts(RUN, False))
GOOD = read(MIT, parts(RUN, True))
# The questions the generator asks in the `generator` way, before making anything and while making.
ASKED_FIRST = {
    "question": "The decisions name MIT, and the repository has no LICENSE file: should the README"
    " name MIT in its own text, or link a LICENSE file to be added?",
    "recommended": "Name MIT in the README's own text, as no LICENSE file is there for the reader"
    " to open.",
}
ASKED_WHILE = {
    "question": "demo.sh takes no arguments and prints `Hello`: should the Use section say what it"
    " prints?",
    "recommended": "Yes, say it prints `Hello`, so the reader knows what to expect before running"
    " it.",
}
# Each way's replies, by role, in the order the docstring of flow.py lists them; a role asked more
# often than its replies are set gives its last again.
WAYS = {
    "plain": {"generator": [WHOLE], "first-user": [GOOD], "learner": [learnt()]},
    "given": {
        "generator": [SHORT, WHOLE],
        "first-user": [STOPPED, GOOD],
        "learner": [learnt()],
    },
    "sent": {
        "generator": [SHORT] * 4 + [WHOLE],
        "first-user": [STOPPED] * 4 + [GOOD],
        "learner": [
            learnt(
                lesson(
                    "The generator, sent B-1 back three times with the license lacking, made the"
                    " README again without it each time, so the round ended with B-1 without Good.",
                    "general",
                )
            )
        ],
    },
    "left": {
        "generator": [SHORT] * 8 + [WHOLE],
        "first-user": [STOPPED] * 8 + [GOOD],
        "learner": [
            learnt(
                lesson(
                    "The checklist's B-1 does not say where the README names the license, and two"
                    " rounds left it out though the decisions name MIT.",
                    "own",
                )
            )
        ],
    },
    "generator": {
        "generator": [
            {
                "reply": {
                    "items": [{"checklist": CHECKLIST, "item": "B-1", "question": 1}],
                    "questions": [ASKED_FIRST],
                }
            },
            made(
                LICENSED,
                MIT,
                {"checklist": CHECKLIST, "item": "B-2", "question": 1},
                questions=(ASKED_WHILE,),
            ),
            made(SAID, MIT, parts(RUN_SAID, True)),
        ],
        "first-user": [read(MIT, parts(RUN_SAID, True))],
        "learner": [learnt()],
    },
}

"""The replies the stand-in roles of the orchestrator trial give, by the way the run takes, each
built from the pieces the ways share: the README the generator writes, with or without its license,
its claim and the first user's reading of it."""

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
    "hinders": "I cannot tell whether I may use demo in my own work",
}


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


def passed(item: str, evidence: str) -> dict[str, Any]:
    """The generator's claim that the item passes, with its evidence."""
    return {"checklist": CHECKLIST, "item": item, "evidence": evidence}


def made(write: str, *items: dict[str, Any], questions: tuple = ()) -> dict[str, Any]:
    """The generator writing the README and running demo, then claiming the items."""
    reply = {"items": list(items), "questions": list(questions), "chosen": []}
    return {"write": write, "run": ["sh demo.sh"], "reply": reply}


def read(*items: dict[str, Any]) -> dict[str, Any]:
    """The first user's reading of the items."""
    return {"reply": {"items": list(items)}}


# The evidence of each item, as the generator gives it, the README with no license or with one.
TERMS = passed("B-1", "cat -n README.md: the README tells what demo does")
LICENSED_TERMS = passed("B-1", "cat -n README.md: line 11 names MIT")
RAN_DEMO = passed("B-2", "sh demo.sh printed Hello, as the Use part says")
# The generator's claims and the first user's readings, of the README with no license and with one:
# every item, then on a remake B-1 alone.
SHORT = made(UNLICENSED, TERMS, RAN_DEMO)
SHORT_AGAIN = made(UNLICENSED, TERMS)
WHOLE = made(LICENSED, LICENSED_TERMS)
STOPPED = read(STOP, parts(RUN, False))
GOOD = read(MIT, parts(RUN, True))
# The questions the generator asks in the `generator` way, before making anything and while making,
# each a point only the user decides.
ASKED_FIRST = {
    "question": "Is demo to be used by people outside the team, who need to know the terms it is"
    " under?",
    "recommended": "Yes, as the decisions name MIT, a license for others to use it under.",
}
ASKED_WHILE = {
    "question": "demo.sh prints `Hello` alone: is that what demo is to greet its users with?",
    "recommended": "Yes, as no decision names another greeting.",
}
# Each way's replies, by role, in the order the docstring of orchestrator.py lists them; a role
# asked more often than its replies are set gives its last again.
WAYS = {
    "plain": {"generator": [made(LICENSED, LICENSED_TERMS, RAN_DEMO)], "first-user": [GOOD]},
    "given": {"generator": [SHORT, WHOLE], "first-user": [STOPPED, GOOD]},
    "sent": {
        "generator": [SHORT] + [SHORT_AGAIN] * 3 + [WHOLE],
        "first-user": [STOPPED] * 4 + [GOOD],
    },
    "left": {
        "generator": [SHORT] + [SHORT_AGAIN] * 7 + [WHOLE],
        "first-user": [STOPPED] * 8 + [GOOD],
    },
    "generator": {
        "generator": [
            {
                "reply": {
                    "items": [{"checklist": CHECKLIST, "item": "B-1", "question": 1}],
                    "questions": [ASKED_FIRST],
                    "chosen": [],
                }
            },
            made(
                LICENSED,
                LICENSED_TERMS,
                {"checklist": CHECKLIST, "item": "B-2", "question": 1},
                questions=(ASKED_WHILE,),
            ),
            made(SAID, LICENSED_TERMS, RAN_DEMO),
        ],
        "first-user": [read(MIT, parts(RUN_SAID, True))],
    },
}

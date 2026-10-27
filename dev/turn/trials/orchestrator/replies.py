"""The replies the stand-in roles of the orchestrator trial give, by the way the run takes, each
built from the pieces the ways share: the README the generator writes, with or without its license,
its claim and the first user's reading of it, each item at its lines or, where the first user
finds no Good, with what the reader would need."""

from __future__ import annotations

from typing import Any

from shared import UNLICENSED

CHECKLIST = "checklist.md"
USE = "## Use\n\nRun `sh demo.sh`."
LICENSE = "\n\n## License\n\nMIT.\n"
# The README with a license, and with one and what demo prints, beside the one with none.
LICENSED = f"# demo\n\ndemo prints a greeting.\n\n{USE}{LICENSE}"
SAID = f"# demo\n\ndemo prints a greeting.\n\n{USE} It prints `Hello`.{LICENSE}"
MIT = {"checklist": CHECKLIST, "item": "B-1", "lines": ["README.md:11-11"]}
NEED = {
    "checklist": CHECKLIST,
    "item": "B-1",
    "need": "Before using demo in their own work, the reader can tell on what terms they may.",
}


def each_part(licensed: bool) -> dict[str, Any]:
    """B-2, at lines in each part of the README, the part of its license among them where it has
    one."""
    lines = ["README.md:3-3", "README.md:7-7"] + ["README.md:11-11"] * licensed
    return {"checklist": CHECKLIST, "item": "B-2", "lines": lines}


def at(item: str, *lines: str) -> dict[str, Any]:
    """The generator's claim of the item, at the lines that give its Good."""
    return {"checklist": CHECKLIST, "item": item, "lines": list(lines)}


def made(write: str, *items: dict[str, Any], questions: tuple = ()) -> dict[str, Any]:
    """The generator writing the README and running demo, then claiming the items."""
    reply = {"items": list(items), "questions": list(questions), "chosen": []}
    return {"write": write, "run": ["sh demo.sh"], "reply": reply}


def read(*items: dict[str, Any]) -> dict[str, Any]:
    """The first user's reading of the items."""
    return {"reply": {"items": list(items)}}


# The lines of each item, as the generator claims them, the README with no license or with one.
TERMS = at("B-1", "README.md:1-7")
LICENSED_TERMS = at("B-1", "README.md:11-11")
RAN_DEMO = each_part(False)
RAN_LICENSED = each_part(True)
# The generator's claims and the first user's readings, of the README with no license and with one:
# every item, then on a remake B-1 alone.
SHORT = made(UNLICENSED, TERMS, RAN_DEMO)
SHORT_AGAIN = made(UNLICENSED, TERMS)
WHOLE = made(LICENSED, LICENSED_TERMS)
NEEDED = read(NEED, each_part(False))
GOOD = read(MIT, each_part(True))
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
    "plain": {"generator": [made(LICENSED, LICENSED_TERMS, RAN_LICENSED)], "first-user": [GOOD]},
    "given": {"generator": [SHORT, WHOLE], "first-user": [NEEDED, GOOD]},
    "sent": {
        "generator": [SHORT] + [SHORT_AGAIN] * 3 + [WHOLE],
        "first-user": [NEEDED] * 4 + [GOOD],
    },
    "left": {
        "generator": [SHORT] + [SHORT_AGAIN] * 7 + [WHOLE],
        "first-user": [NEEDED] * 8 + [GOOD],
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
            made(SAID, LICENSED_TERMS, RAN_LICENSED),
        ],
        "first-user": [GOOD],
    },
}

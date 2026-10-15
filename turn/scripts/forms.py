"""The forms each role fills, one place per item, and what makes a place filled."""

import os
import re

from questions import asked, asked_numbers, question_faults
from state import Stop, read_json, the_work, write_json

ROLES = ("generator", "hand-on", "first-user", "evaluator", "orchestrator", "learner")
PLACES = ("the work", "what the work should be")
DECIDING = ("hand-on", "orchestrator")
LEFT_OUT = (
    "; name the lines that meet it, or, where the work leaves the item out until a question is "
    "answered, give that question's number as `question`"
)
NAMES_LINES = re.compile(r"\blines?\s*\d|\b\d+\s*-\s*\d+\b")
LINES = re.compile(r"\s*\d+(\s*-\s*\d+)?(\s*,\s*\d+(\s*-\s*\d+)?)*\s*$")


def forms(ids):
    return {
        "generator": {i: {"lines": ""} for i in ids},
        "first-user": {},
        "evaluator": {},
        "hand-on": {i: {"met": None, "lines": "", "note": ""} for i in ids},
        "orchestrator": {i: {"met": None, "lines": "", "note": ""} for i in ids},
        "learner": {},
    }


def lay(work, laid):
    for role in ROLES:
        write_json(os.path.join(work, f"{role}.json"), laid[role])


def bad_lines(given, count):
    if not LINES.match(given):
        return True
    return any(
        not 1 <= int(a) <= int(b or a) <= count
        for a, b in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", given)
    )


def check(work, role):
    """Says each place of the role's form that is left or wrong; nothing when every place is filled."""
    _, _, _, path = the_work(work)
    with open(path) as f:
        count = len(f.read().splitlines())
    ids = [i["id"] for i in read_json(os.path.join(work, "list.json"), "the list")["items"]]
    form = read_json(os.path.join(work, f"{role}.json"), "the form")
    found = [f"{i}: not an item of the list" for i in form if i not in ids]
    grounds = (
        read_json(os.path.join(work, "evaluator.json"), "the form")
        if role == "orchestrator"
        else {}
    )
    if role == "learner":
        return (
            found
            + learner_faults(form, without_good(work), count)
            + question_faults(work, decided=False)
        )
    if role in ("generator", "hand-on"):
        found += question_faults(work, decided=role == "hand-on")
    for i in ids if role not in ("first-user", "evaluator") else [i for i in ids if i in form]:
        place = form.get(i)
        if place is None:
            found.append(f"{i}: not filled")
            continue
        lines = place.get("lines", "")
        # An item the generator leaves out until a question is answered has no lines yet.
        needed = (
            role in ("first-user", "evaluator")
            or (role == "generator" and "question" not in place)
            or (role in DECIDING and place.get("met"))
        )
        if role == "first-user" and not place.get("took"):
            found.append(f"{i}: what was taken is not given")
        if role == "evaluator" and not place.get("grounds"):
            found.append(f"{i}: grounds are not given")
        if role in DECIDING and not isinstance(place.get("met"), bool):
            found.append(f"{i}: not decided")
        if role in DECIDING and place.get("met") and not place.get("note"):
            found.append(f"{i}: the note is not given")
        elif place.get("met") and place.get("note") == grounds.get(i, {}).get("grounds"):
            found.append(
                f"{i}: the note is the evaluator's grounds; read the work for the item, and say "
                "what the receiver gets from the lines"
            )
        if role == "hand-on" and place.get("met") is False:
            found += aim_faults(i, place, count)
        if needed and not lines:
            found.append(f"{i}: lines are not given" + (LEFT_OUT if role == "generator" else ""))
        elif lines and bad_lines(lines, count):
            found.append(f"{i}: lines {lines} are not in the work")
        if (
            role == "hand-on"
            and "question" in place
            and place["question"] not in asked_numbers(work)
        ):
            found.append(f"{i}: question {place['question']} is not asked")
        if (
            role == "generator"
            and "question" in place
            and place["question"] not in range(1, len(asked(work)) + 1)
        ):
            found.append(f"{i}: question {place['question']} is not in the questions{LEFT_OUT}")
    return found


def without_good(work):
    return [
        i
        for i, p in read_json(os.path.join(work, "orchestrator.json"), "the form").items()
        if p.get("met") is not True
    ]


def aim_faults(i, place, count):
    """Says where a way to a Good is not made from the aim: the aim and the way said of the whole work,
    and the reach, every line the same shape reaches."""
    found = []
    for key, said in (("aim", "say it of the whole work"), ("way", "say it from the aim")):
        if not place.get(key):
            found.append(f"{i}: the {key} is not given")
        elif NAMES_LINES.search(place[key]):
            found.append(f"{i}: the {key} names lines; {said}")
    reach = place.get("reach", "")
    if not reach:
        found.append(f"{i}: reach is not given")
    elif bad_lines(reach, count):
        found.append(f"{i}: reach {reach} is not in the work")
    return found


def learner_faults(form, left, count):
    found = [f"{i}: has a Good, so needs no way" for i in form if i not in left]
    for i in left:
        place = form.get(i)
        if place is None:
            found.append(f"{i}: not filled")
            continue
        found += aim_faults(i, place, count)
        if place.get("in") not in PLACES:
            found.append(f"{i}: in must be one of: {', '.join(PLACES)}")
        if not isinstance(place.get("making"), str):
            found.append(f'{i}: making is not given; write "" where nothing is learned of making')
    return found


def learned(work):
    """The ways the learner gave in the run, each once with the items it serves, and what it learned
    of making such work."""
    found = check(work, "orchestrator") or check(work, "learner")
    if found:
        raise Stop("\n".join(found))
    return ways_in(os.path.join(work, "learner.json"))


def ways_in(form):
    """The ways a learner's form gives, each once with the items it serves, and what it learned of
    making such work."""
    grouped, rules = {}, []
    for i, p in read_json(form, "the form").items():
        grouped.setdefault((p["way"], p["in"]), []).append(p)
        p["item"] = i
        if p["making"] and p["making"] not in rules:
            rules.append(p["making"])
    return [
        dict(serves(places, w), **{"in": where}) for (w, where), places in grouped.items()
    ], rules


def serves(places, way):
    """One way with the items it serves, their aims and every line it reaches, each said once."""
    aims, reach = (list(dict.fromkeys(p[key] for p in places)) for key in ("aim", "reach"))
    return {"way": way, "items": sorted(p["item"] for p in places), "aims": aims, "reach": reach}


def coverage(work, role):
    _, _, _, path = the_work(work)
    with open(path) as f:
        text = [k for k, line in enumerate(f.read().splitlines(), 1) if line.strip()]
    named = set()
    for place in read_json(os.path.join(work, f"{role}.json"), "the form").values():
        for a, b in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", place.get("lines", "")):
            named.update(range(int(a), int(b or a) + 1))
    left = [k for k in text if k not in named]
    print(f"lines no item names: {', '.join(map(str, left))}" if left else "every line is named")

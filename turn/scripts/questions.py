"""The questions only the user can decide, and what makes each left open or shown answered."""

import os
import re

from state import read_json


def asked(work):
    return read_json(os.path.join(work, "questions.json"), "the questions")


def asked_numbers(work):
    return [k for k, q in enumerate(asked(work), 1) if q.get("ask")]


def left_open(work):
    """The questions the run asks the user at its end."""
    return [q["question"] for q in asked(work) if q.get("ask")]


def question_faults(work, decided):
    """Says each question left without its words or naming an item, or, once decided, neither left
    open nor shown answered."""
    questions = asked(work)
    if not isinstance(questions, list):
        return ["the questions are not a list"]
    found = []
    ids = [i["id"] for i in read_json(os.path.join(work, "list.json"), "the list")["items"]]
    for k, q in enumerate(questions, 1):
        if not (isinstance(q, dict) and q.get("question")):
            found.append(f"question {k}: the question is not given")
            continue
        named = [i for i in ids if re.search(rf"\b{i.split()[-1]}\b", q["question"])]
        if named:
            found.append(
                f"question {k}: names {named[0]}; say in plain words what the work leaves out"
            )
        elif decided and not isinstance(q.get("ask"), bool):
            found.append(f"question {k}: not decided")
        elif decided and not q["ask"] and not q.get("answered"):
            found.append(f"question {k}: where it is answered is not given")
    return found

"""The properties of reading a run from its files, the design tree and the Rounds, as rn's Test
strategy measures them by 0 counterexamples: tree/design.read keeps any edit in form, tree/rounds
gives back each start that rounds.fresh placed, tree/course ends each run within its limit of
Rounds, and check/evaluator holds a result exactly where it answers each condition of its group
once. Each names the kind of John Hughes's How to Specify It that it takes."""

from __future__ import annotations

import json
import os
import re
import tempfile
from typing import Any

import pytest
from check import evaluator
from hypothesis import event, given
from hypothesis import strategies as st
from rn_bench import COMMAND, RN, RUN, conditions, evaluator_cut, plan, run_worktree
from schemas import form
from tree import course, cut, design, rounds
from tree.rounds import Start

SCHEMA = os.path.join(RN, "domain", "best-practices", "design-tree", "design-tree.schema.json")
# What the design tree's schema keeps out of a decision's words: its ground and its date.
DECIDED = re.compile(form.load(SCHEMA)["$defs"]["settled"]["properties"]["decided"]["pattern"])
BY = ("user", "maker", "reasoning", "research")
GROUPS = ("C1", "C2", "C3", "C4", "C5", "C6")
IDS = tuple(f"N{n}" for n in range(1, 13))


def read_json(path: str) -> Any:
    """The JSON file at the path."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, value: Any) -> None:
    """Writes the value as JSON at the path, making its folder."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f)


def beside(cut_path: str) -> str:
    """The path of the result beside the Cut, as Data model's Round places it."""
    return cut_path.removesuffix(".cut.json") + ".json"


@st.composite
def decisions(draw: Any) -> dict[str, Any]:
    """A decision as an orchestrator or a person writes it in the design tree: settled in any
    words but its ground and its date, by anyone, or a point still open."""
    about = draw(st.text(max_size=40))
    if draw(st.booleans()):
        return {"about": about, "decided": None}
    decided = draw(st.text(max_size=80).filter(lambda t: DECIDED.search(t) is not None))
    return {"about": about, "decided": decided, "by": draw(st.sampled_from(BY))}


@st.composite
def plans_edited(draw: Any) -> dict[str, Any]:
    """The plan with any edit in form that a review makes: the goal, a deliverable's name, its
    status open or doing, and any decisions under any of its conditions."""
    tree = plan()
    tree["goal"]["decided"] = draw(st.text(max_size=120))
    for node in tree["deliverables"]:
        node["name"] = draw(st.text(max_size=60))
        node["status"] = draw(st.sampled_from(["open", "doing"]))
        for held in node["necessary_conditions"]:
            held["decisions"] = draw(st.lists(decisions(), max_size=2))
    return tree


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
@given(tree=plans_edited())
def test_read_gives_back_any_edit_of_the_tree_in_its_form(tree: dict[str, Any]):
    """Given any edit of the plan that keeps the design tree's schema and its checks: any goal and
    names, a status open or doing, and any decisions, settled by anyone or still open, in any
    words but a ground or a date
    When design.read reads the run's folder
    Then it gives the tree as written, never refusing it, as the strategy of each design tree edit
    checked before its commit (P1.1) and Data model's Design tree need. A postcondition."""
    with tempfile.TemporaryDirectory() as tmp:
        _, top = run_worktree(tmp, {f"{RUN}/design-tree.json": tree})
        assert design.read(os.path.join(top, RUN), RN) == tree


@st.composite
def starts_placed(draw: Any) -> list[tuple[int, str, str, Any]]:
    """Starts in the order a run cuts them: each of any Round, the generator or an evaluator of
    any group, with a result or none, as one stopped or still running leaves none."""
    each = []
    for n in range(draw(st.integers(0, 8))):
        role = draw(st.sampled_from(["generator", "evaluator"]))
        group = "" if role == "generator" else draw(st.sampled_from(GROUPS))
        result = draw(st.sampled_from([None, {"result": "made"}, {"good": [], "more": []}]))
        each.append((draw(st.integers(1, 12)), role, group, {"n": n, "result": result}))
    return each


@pytest.mark.supports("test_each_rounds_results_lie_beside_their_cuts")
@given(placed=starts_placed())
def test_each_start_placed_by_fresh_is_read_back_in_its_order(
    placed: list[tuple[int, str, str, Any]],
):
    """Given any starts of a run's Rounds, of any Round number and role and group, each Cut
    written where rounds.fresh names it, with its result beside it or none
    When rounds.each reads the run's folder, and rounds.path names each start's Cut
    Then each gives what a model of the Rounds gives: each start once, its slot one past those of
    its Round, role, and group before it, its result None where none lies beside its Cut, ordered
    by the Round's number, the generator before the evaluators, the group, and the slot; and each
    Cut where fresh placed it, as Data model's Round and the run's state in files (P6.1) need. A
    model-based property."""
    with tempfile.TemporaryDirectory() as tmp:
        run = os.path.join(tmp, RUN)
        os.makedirs(run)
        model: list[Start] = []
        places: dict[int, str] = {}
        for number, role, group, held in placed:
            path = rounds.fresh(run, Start(number, role, group, held, None))
            write_json(path, held)
            if held["result"] is not None:
                write_json(beside(path), held["result"])
            slot = 1 + sum((s.round, s.role, s.group) == (number, role, group) for s in model)
            model.append(Start(number, role, group, held, held["result"], slot))
            places[held["n"]] = path
        model.sort(key=lambda s: (s.round, s.role != "generator", s.group, s.slot))
        assert list(rounds.each(run)) == model
        assert {s.cut["n"]: rounds.path(run, s) for s in model} == places


# Where a deliverable of each kind lies, as a run's plan places it.
PATHS = {
    "code": COMMAND,
    "readme": "docs/print-invoice.md",
    "architecture": "docs/invoicer-architecture.md",
    "light": "docs/notes.md",
}


def one_deliverable(kind: str) -> dict[str, Any]:
    """A design tree of one deliverable of the kind, resting on none, first in the work."""
    tree = plan()
    node = {**tree["deliverables"][0], "kind": kind, "path": PATHS[kind], "inputs": []}
    node["necessary_conditions"] = conditions(kind)
    return {**tree, "deliverables": [node], "work": [{"do": "make", "path": PATHS[kind]}]}


def review(tree: dict[str, Any], short: list[str], data: Any) -> None:
    """The orchestrator's review after a Round's evaluators: for each condition judged short, a
    decision taken from the finding, the condition held good as one its people never meet, or
    nothing, each by anyone but the user."""
    by_id = {c["id"]: c for c in tree["deliverables"][0]["necessary_conditions"]}
    for n, condition in enumerate(short):
        held = by_id.get(condition)
        does = data.draw(st.sampled_from(["decide", "good", "leave"]))
        if held is not None and does == "decide":
            by = data.draw(st.sampled_from(BY[1:]))
            held["decisions"].append({"about": f"finding {n}", "decided": "mended", "by": by})
        elif held is not None and does == "good":
            held["good"] = True


def play(run: str, tree: dict[str, Any], data: Any) -> bool:
    """Plays the run's Rounds: each start that course.due gives cut by cut.write and ended with
    any result its role can give, and the orchestrator's review after each Round's evaluators;
    whether course.due gave none within 30 moves."""
    for _ in range(30):
        due = course.due(tree, rounds.each(run), [])
        if not due:
            return True
        short: list[str] = []
        for each in due:
            path = cut.write(run, tree, each)
            if each.role == "generator":
                result = data.draw(st.sampled_from(["made", "made", "made", "point"]))
                answer: Any = {"result": result, "carried_out": []}
                if result == "point":
                    answer["point"] = "Which currency?"
            else:
                judged = {c: data.draw(st.booleans()) for c in read_json(path)["conditions"]}
                answer = {
                    "good": [{"condition": c, "lines": ["x:1"]} for c, g in judged.items() if g],
                    "more": [
                        {"condition": c, "good_when": "w"} for c, g in judged.items() if not g
                    ],
                }
                short += [c for c, g in judged.items() if not g]
            write_json(beside(path), answer)
        if due[0].role == "evaluator":
            review(tree, short, data)
    return False


@pytest.mark.supports("test_findings_past_the_limit_start_no_further_round")
@given(kind=st.sampled_from(["code", "readme", "architecture", "light"]), data=st.data())
def test_each_run_ends_within_two_rounds_of_content_and_two_of_refactoring(kind: str, data: Any):
    """Given any deliverable of a kind, and any course of its run: each generator made or stopped
    on a point, each condition judged good or short, and after each Round the orchestrator taking a
    finding into a decision, holding its condition good, or neither, never by the user's decision
    When course.due gives the starts due after each move, each cut by cut.write
    Then it gives none within 30 moves, with at most two Rounds made of content and two of
    refactoring, none of refactoring for the kind light, as remaking has a limit (P3.3). An
    inductive property over the run's moves."""
    with tempfile.TemporaryDirectory() as tmp:
        tree = one_deliverable(kind)
        _, top = run_worktree(tmp, {f"{RUN}/design-tree.json": tree})
        run = os.path.join(top, RUN)
        assert play(run, tree, data), "course.due gave starts past 30 moves"
        made = [
            s.cut["best_practice"]
            for s in rounds.each(run)
            if s.role == "generator" and (s.result or {}).get("result") == "made"
        ]
        event(f"Rounds made: {made}")
        content = sum(p == kind for p in made)
        refactoring = sum(p != kind for p in made)
        assert content <= 2 and refactoring <= (0 if kind == "light" else 2)


NEAR = ("N1", "N10", "n1", "N1 ", "N01", "C1")


@st.composite
def answers(draw: Any) -> tuple[list[str], dict[str, Any]]:
    """An evaluator's Cut's conditions, and a result in its form that answers any of them any
    number of times, or a near match of one, each good or more, in any order."""
    held = draw(st.lists(st.sampled_from(IDS), min_size=1, max_size=6, unique=True))
    answered = [c for c in held for _ in range(draw(st.sampled_from([1, 1, 1, 0, 2])))]
    answered += draw(st.lists(st.sampled_from(NEAR + IDS), max_size=2))
    result: dict[str, Any] = {"good": [], "more": []}
    for c in draw(st.permutations(answered)):
        if draw(st.booleans()):
            result["good"].append({"condition": c, "lines": [draw(st.sampled_from(["x:1", "a"]))]})
        else:
            result["more"].append({"condition": c, "good_when": draw(st.text(max_size=20))})
    return held, result


@pytest.mark.supports(
    "test_an_evaluators_result_that_leaves_a_condition_unanswered_is_held_naming_it"
)
@given(cut_and_result=answers())
def test_an_evaluators_result_holds_exactly_where_it_answers_each_condition_once(
    cut_and_result: tuple[list[str], dict[str, Any]],
):
    """Given any evaluator's Cut of a group's conditions, and any result in its form beside it that
    answers each condition none, one, or two times, and any near match of one, good or more
    When evaluator.faults checks the result
    Then it gives no fault exactly where a model gives the result whole: each condition of the
    Cut answered once and none other, so that a result that answers its group ends the evaluator
    and one that drops a finding never does, as a trial names only what's good and what would
    make it good (P2.2) and roles hand each other short results (P4.2). A model-based property."""
    held, result = cut_and_result
    group = f"{RUN}/rounds/1/evaluator-C1.cut.json"
    answered = [a["condition"] for a in result["good"] + result["more"]]
    whole = sorted(answered) == sorted(held)
    with tempfile.TemporaryDirectory() as tmp:
        _, top = run_worktree(tmp, {group: evaluator_cut("C1", held), beside(group): result})
        assert (list(evaluator.faults(os.path.join(top, RUN), group, RN)) == []) == whole

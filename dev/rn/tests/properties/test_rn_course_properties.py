"""The property-based tests of which Round a deliverable takes next, as rn's Test strategy names
them: each invariant that the architecture's principles state of a deliverable's Rounds, for any
node of the design tree and any course of Rounds that a run brings, each Round before the last
made and judged, and the last at any point of its course.

- Remaking has a limit (P3.3), twice at most as the README says: since the deliverable's last
  Round put up for its sign-off, as a send-back there starts its course again, as the user's answer
  does too where a Round's Cut shows it came after, no new Round of
  content once it holds two, and none of refactoring once it holds one, as a new
  generator refactors once each condition is good (P3.2), else the deliverable grows with each
  round and the user waits on it.
- No evaluator judges the refactoring (P3.2): the evaluator is never due in a refactor Round, as
  the refactoring keeps the intent that the content's Rounds judged.
- The user is asked only what only they can decide, one point at a time (P1.2): while a decision
  waits on the user, as a point to answer or, once its Rounds are over, as a proposal to sign off
  (P3.3), neither the generator nor the evaluator is due, else a role makes on a guess the user
  hasn't answered.
- A pause loses neither time nor work (S2, P6.1): a Round that a pause stopped before its
  generator's result goes on in itself, spending none of the stage's Rounds.
- Work rests on a deliverable once the user signs it off (P1.3): the sign-off waits only on a
  deliverable whose conditions are each good, whose Rounds are over with its findings left as
  proposals, or whose last Round was put up with the conditions not good and the open decisions
  it holds now, else the user signs off what the run knows short without seeing why, or what
  changed since they saw it."""

from __future__ import annotations

from typing import Any

import pytest
import rn_files
from hypothesis import given
from hypothesis import strategies as st
from rounds.course import Done, Next, next_of
from rounds.files import Round

# The most Rounds of each stage: of content, as the README's How it works says, "twice at most";
# of refactoring, one, as the architecture's strategy of a new generator for it says.
MOST = {"content": 2, "refactor": 1}
ROLES = {"generator", "evaluator", "answer", "pruner", "sign-off"}
LAST = st.sampled_from(["none", "point", "made", "judged"])


@st.composite
def nodes(draw: Any) -> dict[str, Any]:
    """A deliverable's open node, of the kind light or readme, with any conditions good and any
    decisions open."""
    node = rn_files.open_node(
        "The guide", "docs/guide.md", draw(st.sampled_from(["light", "readme"]))
    )
    for each in node["necessary_conditions"]:
        each["good"] = draw(st.booleans())
        if draw(st.integers(0, 4)) == 0:
            each["decisions"] = [rn_files.decision("a point", draw(st.sampled_from([None, "yes"])))]
    return node


@st.composite
def stages(draw: Any) -> list[tuple[str, bool]]:
    """The stage of each Round so far, in the order they were made, and whether it's put up for the
    sign-off: none, one, or two courses sent back after their last Round was put up, each one or
    two of content then a refactor Round or none, then none, or up to two of content then up to
    one of refactor, the last put up or not."""
    found: list[tuple[str, bool]] = []
    for _ in range(draw(st.integers(0, 2))):
        course = ["content"] * draw(st.integers(1, MOST["content"]))
        course += ["refactor"] * draw(st.integers(0, MOST["refactor"]))
        found += [(each, n == len(course)) for n, each in enumerate(course, 1)]
    content = draw(st.integers(0, MOST["content"]))
    refactor = draw(st.integers(0, MOST["refactor"])) if content else 0
    found += [(each, False) for each in ["content"] * content + ["refactor"] * refactor]
    if found and not found[-1][1]:
        found[-1] = (found[-1][0], draw(st.booleans()))
    return found


def state_of(node: dict[str, Any]) -> dict[str, Any]:
    """The node's state as a Round put up holds it in put-up.json, as rounds/files.py's module
    opening gives its form: each condition not good, and each open decision by its condition and
    its about, in the node's order."""
    conditions = node["necessary_conditions"]
    return {
        "short": [c["id"] for c in conditions if not c["good"]],
        "open": [
            {"condition": c["id"], "about": d["about"]}
            for c in conditions
            for d in c["decisions"]
            if d["decided"] is None
        ],
    }


@st.composite
def states(draw: Any) -> dict[str, Any]:
    """A state put up for the sign-off: any conditions not good, and no open decision."""
    short = draw(st.lists(st.sampled_from(["N1", "N2", "N3"]), unique=True))
    return {"short": sorted(short), "open": []}


def done(stage: str, number: int, held: str, put_up: dict[str, Any] | None) -> Done:
    """The Round of the stage and number, holding the results `held` names, `none`, `point`,
    `made`, or `judged`, a refactor Round never judged, and one put up, with its state, made and,
    of content, judged."""
    if put_up is not None:
        held = "judged" if stage == "content" else "made"
    elif stage == "refactor" and held == "judged":
        held = "made"
    made = {"none": None, "point": rn_files.point()}.get(held, rn_files.made())
    judged = rn_files.judged() if held == "judged" else None
    folder = rn_files.round_of("/r/.rn/r", "docs/guide.md", stage, number)
    return Done(Round(folder, "docs/guide.md", stage, number), made, judged, put_up)


@st.composite
def courses(draw: Any) -> tuple[dict[str, Any], list[Any], bool]:
    """A node of nodes(); its Rounds so far, of the stages that stages() gives, each before the last
    made, and of content judged, and the last at any point of its course, each put up with any
    state, the last with the node's own or another; and whether its kind is refactored."""
    node = draw(nodes())
    staged = draw(stages())
    rounds = []
    for number, (stage, put_up) in enumerate(staged, 1):
        last = number == len(staged)
        mark = None
        if put_up:
            mark = state_of(node) if last and draw(st.booleans()) else draw(states())
        rounds.append(done(stage, number, draw(LAST) if last else "judged", mark))
    return node, rounds, draw(st.booleans())


def is_open(node: dict[str, Any]) -> bool:
    return any(d["decided"] is None for c in node["necessary_conditions"] for d in c["decisions"])


def since_signoff(rounds: list[Any]) -> list[Any]:
    """The Rounds since the last put up for the sign-off, or since the first."""
    marked = [n for n, each in enumerate(rounds) if each.put_up is not None]
    return list(rounds[marked[-1] + 1 :] if marked else rounds)


def waiting(node: dict[str, Any], rounds: list[Any]) -> bool:
    """Whether the last Round was put up with the node's state as it stands."""
    return bool(rounds) and rounds[-1].put_up == state_of(node)


def past_its_rounds(rounds: list[Any]) -> bool:
    """Whether the Rounds are over: the last is of content, and the content since the last
    sign-off holds two Rounds, each made and judged."""
    held = since_signoff(rounds)
    if not held or held[-1].round.stage != "content":
        return False
    return len(held) == MOST["content"] and all(each.generator and each.evaluator for each in held)


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
@given(courses())
def test_no_new_round_of_a_stage_that_holds_its_most(
    course: tuple[dict[str, Any], list[Any], bool],
):
    """Given any deliverable's node, any course of its Rounds, and whether its kind is refactored
    When what it waits on next is found
    Then it's one of the generator, the evaluator, the answer, the pruner, or the sign-off,
    and a generator in a new Round is of a stage that holds fewer than its most since the last
    sign-off, two of content and one of refactoring
    (Invariant, resting on P3.3 and P3.2.)"""
    node, rounds, refactors = course
    found = next_of(node, rounds, refactors)
    assert found.waits_on in ROLES
    if found.waits_on == "generator" and not found.resumes:
        assert found.stage is not None, "a new Round has a stage"
        held = since_signoff(rounds)
        assert sum(1 for each in held if each.round.stage == found.stage) < MOST[found.stage]


@pytest.mark.supports("test_no_evaluator_is_due_after_a_refactor_round")
@given(courses())
def test_no_evaluator_in_a_refactor_round(course: tuple[dict[str, Any], list[Any], bool]):
    """Given any deliverable's node, any course of its Rounds, and whether its kind is refactored
    When what it waits on next is found
    Then the evaluator is due only in a Round of content
    (Invariant, resting on P3.2, a new generator refactoring with no evaluator.)"""
    node, rounds, refactors = course
    found = next_of(node, rounds, refactors)
    if found.waits_on == "evaluator":
        assert found.stage == "content" and rounds[-1][0].stage == "content"


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
@given(courses())
def test_no_maker_or_judge_while_a_decision_waits_on_the_user(
    course: tuple[dict[str, Any], list[Any], bool],
):
    """Given any deliverable's node with any decision open, and any course of its Rounds
    When what it waits on next is found
    Then, while a decision is open, neither the generator nor the evaluator is due, as each open
    decision waits on the user, as a point to answer or as a proposal to sign off; and it waits on
    the answer only while a decision is open
    (Invariant, resting on P1.2 and P3.3.)"""
    node, rounds, refactors = course
    found = next_of(node, rounds, refactors)
    if is_open(node):
        assert found.waits_on not in ("generator", "evaluator")
    else:
        assert found.waits_on != "answer"


@st.composite
def paused_courses(draw: Any) -> tuple[dict[str, Any], list[Any], bool]:
    """A course of courses() with no decision open and at least one Round, its last Round holding
    no result of either role, as a pause that stopped its generator leaves it."""
    node, rounds, refactors = draw(courses())
    for each in node["necessary_conditions"]:
        each["decisions"] = [rn_files.decision("a point", "yes")] if each["decisions"] else []
    if not rounds:
        folder = rn_files.round_of("/r/.rn/r", "docs/guide.md", "content", 1)
        rounds = [Done(Round(folder, "docs/guide.md", "content", 1), None, None)]
    rounds[-1] = Done(rounds[-1].round, None, None)
    return node, rounds, refactors


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
@given(paused_courses())
def test_a_pause_spends_no_round(course: tuple[dict[str, Any], list[Any], bool]):
    """Given any deliverable's node with no decision open, and any course of its Rounds whose last
    Round holds no generator's result, as a pause stopped it
    When what it waits on next is found
    Then the generator resumes that Round, of its stage, so that the stop spends none of the
    stage's Rounds
    (Invariant, resting on S2 and P6.1, a run that goes on from its files losing no work.)"""
    node, rounds, refactors = course
    found = next_of(node, rounds, refactors)
    assert found == Next("generator", rounds[-1][0].stage, True)


@pytest.mark.supports(
    "test_a_finding_the_people_would_never_meet_is_dropped_by_holding_its_condition_good"
)
@given(courses())
def test_the_signoff_waits_on_a_deliverable_good_or_past_its_rounds(
    course: tuple[dict[str, Any], list[Any], bool],
):
    """Given any deliverable's node and any course of its Rounds
    When what it waits on next is found
    Then it waits on the sign-off only where each of its conditions is good, where its Rounds
    are over with the findings left kept as open decisions, the proposals the user signs off, or
    where its last Round was put up with the state it holds now
    (Invariant, resting on P1.3 and P3.3.)"""
    node, rounds, refactors = course
    if next_of(node, rounds, refactors).waits_on == "sign-off":
        good = all(each["good"] for each in node["necessary_conditions"])
        over = past_its_rounds(rounds) and is_open(node)
        assert good or over or waiting(node, rounds)

"""The property-based tests of which Round a deliverable takes next, as rn's Test strategy names
them: each invariant that the architecture's principles state of a deliverable's Rounds, for any
node of the design tree and any course of Rounds that a run brings, each Round before the last
made and judged, and the last at any point of its course.

- Remaking has a limit (P3.3), twice at most of each stage as the README says: no new Round of a
  stage that holds two, else the deliverable grows with each round and the user waits on it.
- The user is asked only what only they can decide, one point at a time (P1.2): while a decision
  is open, no role starts, else a role makes on a guess the user hasn't answered.
  Once its Rounds are over, its findings left kept as open decisions wait for the sign-off as
  proposals (P3.3), not on an answer that no role would take back.
- A pause loses neither time nor work (S2, P6.1): a Round that a pause stopped before its
  generator's result goes on in itself, spending none of the stage's two Rounds.
- Work rests on a deliverable once the user signs it off (P1.3): the sign-off waits only on a
  deliverable whose conditions are each good, or whose Rounds are over with its findings left as
  proposals, else the user signs off what the run knows short without seeing why."""

from __future__ import annotations

from typing import Any

import pytest
import rn_files
from hypothesis import assume, given
from hypothesis import strategies as st
from rounds.course import Next, next_of
from rounds.files import Round

pytestmark = pytest.mark.xfail(
    strict=True, reason="rounds.course's bodies raise NotImplementedError"
)

# The most Rounds of a stage, as the README's How it works says: "twice at most".
MOST = 2
ROLES = {"generator", "evaluator", "answer", "orchestrator", "sign-off"}
LAST = st.sampled_from(["none", "point", "made", "judged"])


@st.composite
def courses(draw: Any) -> tuple[dict[str, Any], list[Any], bool]:
    """A deliverable's open node, of the kind light or readme, with any conditions good and any
    decisions open; its Rounds so far, none, or up to two of content then up to two of refactor,
    each before the last made and judged; and whether its kind is refactored."""
    kind = draw(st.sampled_from(["light", "readme"]))
    node = rn_files.open_node("The guide", "docs/guide.md", kind)
    for each in node["necessary_conditions"]:
        each["good"] = draw(st.booleans())
        if draw(st.integers(0, 4)) == 0:
            each["decisions"] = [rn_files.decision("a point", draw(st.sampled_from([None, "yes"])))]
    content = draw(st.integers(0, MOST))
    refactor = draw(st.integers(0, MOST)) if content else 0
    stages = [("content", n) for n in range(1, content + 1)]
    stages += [("refactor", n) for n in range(1, refactor + 1)]
    rounds = []
    for place, (stage, number) in enumerate(stages, 1):
        folder = rn_files.round_of("/r/.rn/r", "docs/guide.md", stage, number)
        held = "judged" if place < len(stages) else draw(LAST)
        made = {"none": None, "point": rn_files.point()}.get(held, rn_files.made())
        judged = rn_files.judged() if held == "judged" else None
        rounds.append((Round(folder, "docs/guide.md", stage, number), made, judged))
    return node, rounds, draw(st.booleans())


def is_open(node: dict[str, Any]) -> bool:
    return any(d["decided"] is None for c in node["necessary_conditions"] for d in c["decisions"])


def past_its_rounds(rounds: list[Any]) -> bool:
    """Whether the last Round's stage holds two Rounds, each made and judged."""
    if not rounds:
        return False
    stage = rounds[-1][0].stage
    held = [each for each in rounds if each[0].stage == stage]
    return len(held) == MOST and all(made and judged for _, made, judged in held)


@pytest.mark.supports("test_a_deliverable_short_after_two_content_rounds_gets_no_third")
@given(courses())
def test_no_new_round_of_a_stage_that_holds_two(course: tuple[dict[str, Any], list[Any], bool]):
    """Given any deliverable's node, any course of its Rounds, and whether its kind is refactored
    When what it waits on next is found
    Then it's one of the generator, the evaluator, the answer, the orchestrator, or the sign-off,
    and a generator in a new Round is of a stage that holds fewer than two Rounds
    (Invariant, resting on P3.3.)"""
    node, rounds, refactors = course
    found = next_of(node, rounds, refactors)
    assert found.waits_on in ROLES
    if found.waits_on == "generator" and not found.resumes:
        assert sum(1 for each, _, _ in rounds if each.stage == found.stage) < MOST


@pytest.mark.supports("test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut")
@given(courses())
def test_no_role_while_a_decision_is_open(course: tuple[dict[str, Any], list[Any], bool]):
    """Given any deliverable's node with any decision open, and any course of its Rounds
    When what it waits on next is found
    Then, while a decision is open, it waits on no role: on the sign-off where its Rounds are over,
    each of the last stage's two made and judged, the open decisions being the proposals left, and
    else on the answer; and on the answer only while a decision is open
    (Invariant, resting on P1.2 and P3.3.)"""
    node, rounds, refactors = course
    found = next_of(node, rounds, refactors)
    if is_open(node):
        assert found.waits_on == ("sign-off" if past_its_rounds(rounds) else "answer")
    else:
        assert found.waits_on != "answer"


@pytest.mark.supports(
    "test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut"
)
@given(courses())
def test_a_pause_spends_no_round(course: tuple[dict[str, Any], list[Any], bool]):
    """Given any deliverable's node with no decision open, and any course of its Rounds whose last
    Round holds no generator's result, as a pause stopped it
    When what it waits on next is found
    Then the generator resumes that Round, of its stage, so that the stop spends none of the two
    Rounds of the stage
    (Invariant, resting on S2 and P6.1, a run that goes on from its files losing no work.)"""
    node, rounds, refactors = course
    assume(rounds and rounds[-1][1] is None and not is_open(node))
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
    Then it waits on the sign-off only where each of its conditions is good, or where its Rounds
    are over with the findings left kept as open decisions, the proposals the user signs off
    (Invariant, resting on P1.3 and P3.3.)"""
    node, rounds, refactors = course
    if next_of(node, rounds, refactors).waits_on == "sign-off":
        good = all(each["good"] for each in node["necessary_conditions"])
        assert good or (past_its_rounds(rounds) and is_open(node))

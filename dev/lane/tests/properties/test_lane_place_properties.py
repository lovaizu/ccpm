"""The property-based tests of the guard's placing of moves, as Lane's Test strategy names it: two
starts of one role and the main conversation mark their steps in any order, and each call must be
placed on its own start at the first step that the start hasn't marked done, as the Strategy of
each move placed on its run and start says, since a call placed on another start's step is held to
rules that aren't its own, leaving its step unnoticed or stopping a right move; and a main
conversation that takes its steps at each turn must have each turn's end placed as if no turn came
before, as the Strategy of the main conversation's steps given at each turn says, since a mark of
an earlier turn counted in a later one lets a step of that later event go undone."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator

import lane_bench
import lane_entries
import pytest
from hypothesis import given
from hypothesis import strategies as st
from lane_events import Events, Subagent
from place import place
from record import Entry, Run
from rules import Step

WRITER = Subagent("a1", "log:writer")
OTHER = Subagent("a2", "log:writer")
# Each role's steps in log's rules, by the role that a call of the agent, or of the main
# conversation for None, is held to.
STEPS = {
    None: ("log:up", ["lead"]),
    WRITER.id: ("log:writer", ["write", "report"]),
    OTHER.id: ("log:writer", ["write", "report"]),
}
WHO = st.sampled_from([WRITER.id, OTHER.id, None])
MARK = st.builds(
    lambda who, step, item: {
        "kind": "mark",
        "run": "r1",
        "agent_id": who,
        "step": step,
        **({"item": item} if item else {}),
    },
    WHO,
    st.sampled_from(["lead", "write", "report"]),
    st.sampled_from([None, None, "dated", "linked"]),
)


@pytest.fixture(scope="module")
def folders() -> Iterator[tuple[str, str]]:
    """The folder of `log`, with its rules, and the folder that its conversation works in."""
    with tempfile.TemporaryDirectory() as tmp:
        log = lane_bench.plugin(
            os.path.join(tmp, "log"),
            "log",
            lane_bench.SKILLS,
            lane_bench.RULES,
            lane_bench.ADAPTERS,
        )
        cwd = os.path.join(tmp, "repo")
        os.makedirs(cwd)
        yield log, cwd


@pytest.mark.supports("test_two_starts_of_one_role_are_each_held_to_their_own_start")
@given(st.lists(MARK, max_size=8), WHO)
def test_each_call_is_placed_on_its_own_start_at_its_first_step_not_marked(
    folders: tuple[str, str], marks: list[Entry], who: str | None
):
    """Given a run of log:up whose two starts of log:writer are tied to a1 and a2, and any marks of
    steps and items in any order, by either start and by the main conversation
    When either start or the main conversation writes a file
    Then place gives a `call` of the caller, held to its role's steps, at the first step that the
    caller hasn't marked done
    (Model-based, resting on the Strategy of each move placed on its run and start, P2.5, and
    place.place's Gives.)"""
    log, cwd = folders
    entries: list[Entry] = [
        {"kind": "run", "run": "r1", "skill": "log:up", "words": lane_bench.WORDS},
        lane_entries.start("u1"),
        lane_entries.tie("u1", WRITER.id),
        lane_entries.start("u2"),
        lane_entries.tie("u2", OTHER.id),
        *marks,
    ]
    run = Run("r1", "session-1", "log:up", lane_bench.WORDS, log, entries)
    e = Events(cwd, os.path.join(os.path.dirname(cwd), "transcripts", "session-1.jsonl"))
    agent = {WRITER.id: WRITER, OTHER.id: OTHER}.get(who or "")
    moved = place(
        e.write(os.path.join(cwd, "CHANGELOG.md"), agent), [run], lambda _: {"starts": []}
    )
    role, steps = STEPS[who]
    done = {m["step"] for m in marks if m["agent_id"] == who and "item" not in m}
    assert moved is not None
    assert (moved.kind, moved.agent_id, moved.role) == ("call", who, role)
    assert [step["name"] for step in moved.steps] == steps
    first = next((step for step in steps if step not in done), None)
    if first is not None:
        assert moved.step == first


# The steps of a turn of the main conversation that takes its steps at each turn, as the plugin's
# adapter of the rules may give them: two steps held in order.
TURN_STEPS: list[Step] = [
    {"name": "up", "rules": [{"type": "order"}]},
    {"name": "file", "rules": [{"type": "order"}]},
]
MAIN_MARK = st.builds(
    lambda who, step, item: {
        "kind": "mark",
        "run": "r1",
        "agent_id": who,
        "step": step,
        **({"item": item} if item else {}),
    },
    st.sampled_from([None, None, WRITER.id]),
    st.sampled_from(["up", "file"]),
    st.sampled_from([None, None, "noted"]),
)


def a_turn(prompt: str) -> Entry:
    return {"kind": "turn", "run": "r1", "role": "log:up", "prompt": prompt, "steps": TURN_STEPS}


def turns_ended(earlier: list[list[Entry]]) -> list[Entry]:
    """The entries of each earlier turn, with its marks, each ended and the next begun."""
    entries: list[Entry] = []
    for each, marks in enumerate(earlier):
        entries += [a_turn("" if each == 0 else "Go on."), *marks]
        entries += [{"kind": "turn_ended", "run": "r1"}]
        entries += [{"kind": "turn_begun", "run": "r1", "prompt": "Go on."}]
    return entries


@pytest.fixture(scope="module")
def per_turn() -> Iterator[tuple[str, str]]:
    """The folder of `log`, whose rules name log:up with no steps, and its conversation's folder."""
    with tempfile.TemporaryDirectory() as tmp:
        log = lane_bench.plugin(
            os.path.join(tmp, "log"), "log", lane_bench.SKILLS, lane_bench.PER_TURN, {}
        )
        cwd = os.path.join(tmp, "repo")
        os.makedirs(cwd)
        yield log, cwd


@pytest.mark.xfail(strict=True, reason="place.own_entries and place._turn_steps are empty")
@pytest.mark.supports("test_a_turn_whose_first_move_is_its_end_is_held_to_its_own_steps_afresh")
@given(st.lists(st.lists(MAIN_MARK, max_size=4), min_size=1, max_size=3), st.lists(MAIN_MARK))
def test_the_turns_before_leave_the_end_of_the_turn_at_hand_as_it_stands_alone(
    per_turn: tuple[str, str], earlier: list[list[Entry]], marks: list[Entry]
):
    """Given any turns before the one at hand of a main conversation that takes its steps at each
    turn, with any marks of steps and items in each, by it or by the writer, and any such marks in
    the turn at hand
    When the main conversation ends its turn
    Then place gives the end held to the same steps, at the same step, as for a run that holds the
    turn at hand alone
    (Metamorphic, resting on the Strategy of the main conversation's steps given at each turn, S11,
    whose turn starts each turn's steps afresh.)"""
    log, cwd = per_turn
    head: list[Entry] = [
        {"kind": "run", "run": "r1", "skill": "log:up", "words": lane_bench.WORDS},
        lane_entries.start("u1"),
        lane_entries.tie("u1", WRITER.id),
    ]
    at_hand = [a_turn("Go on."), *marks]
    e = Events(cwd, os.path.join(os.path.dirname(cwd), "transcripts", "session-1.jsonl"))

    def ended(entries: list[Entry]) -> tuple[object, ...]:
        run = Run("r1", "session-1", "log:up", lane_bench.WORDS, log, entries)
        moved = place(e.stop(), [run], lambda _: {"starts": []})
        assert moved is not None
        return (moved.kind, moved.role, moved.agent_id, moved.steps, moved.step)

    assert ended([*head, *turns_ended(earlier), *at_hand]) == ended([*head, *at_hand])

"""The property-based test of the guard's placing of moves, as Lane's Test strategy names it: two
starts of one role and the main conversation mark their steps in any order, and each call must be
placed on its own start at the first step that the start hasn't marked done, as the Strategy of
each move placed on its run and start says, since a call placed on another start's step is held to
rules that aren't its own, leaving its step unnoticed or stopping a right move."""

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

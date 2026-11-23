"""The property-based tests of the record, as overnight's Test strategy names them: where each task
stands lies in files beside the queue file for any later session, as P5.2 says, so any runs read
back as they were written (model-based, of Run), and each reply lies in its own file there
(invariant, of Reply); a task left unended when overnight stops ends given up, as P3.3 says, and a
queue stacked again carries on each unfinished task in its session, as P3.4 says (postconditions);
and a resumed task's reply follows its earlier one with the line of its wait, as P5.1 says
(model-based)."""

from __future__ import annotations

import os
import tempfile
from datetime import timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st
from overnight_generators import LOCAL_MOMENTS, MOMENTS, NAMES, WORDS
from record.place import of
from record.replies import Reply, part
from record.runs import Kept, Run, State, Wait, dump, load
from record.stopped import carried_on, left
from stacker.queue_file import Task

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

STATES: list[State] = [
    "waiting for the start",
    "running",
    "waiting for the limit",
    "finished",
    "given up",
]
SESSIONS = st.uuids().map(str)
# A reply's text, as a session answers it: any letters and lines, with no space at either end.
TEXTS = st.text(min_size=1, max_size=60).filter(lambda text: text.strip() == text)


@st.composite
def runs(draw: st.DrawFn) -> Run:
    """Any run that a task's use brings: a state, a session from its first start or none before it,
    each wait of up to seven stops, when it goes on while it waits, and its end and why once it
    ended, given up only with why."""
    state = draw(st.sampled_from(STATES))
    started = state != "waiting for the start" or draw(st.booleans())
    stops = draw(st.integers(0, 7))
    stopped = [draw(MOMENTS) for _ in range(stops)]
    open_wait = state == "waiting for the limit"
    waits = tuple(
        Wait(each, None if open_wait and n == stops - 1 else each + timedelta(minutes=61))
        for n, each in enumerate(stopped)
    )
    ended = draw(MOMENTS) if state in ("finished", "given up") else None
    return Run(
        state,
        draw(SESSIONS) if started else None,
        stops,
        waits,
        draw(MOMENTS) if open_wait else None,
        ended,
        draw(TEXTS) if state == "given up" else None,
    )


TASKS = st.builds(
    lambda name, words, writes: Task(
        name, os.path.join(os.sep, *words) + ".md", os.sep + words[0], writes
    ),
    NAMES,
    st.lists(WORDS, min_size=1, max_size=3),
    st.booleans(),
)


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
@given(st.lists(st.tuples(TASKS, runs()), max_size=5, unique_by=lambda t: t[0].name))
def test_any_runs_read_back_as_they_were_written(kept: list[tuple[Task, Run]]):
    """Given any tasks of distinct names, each with any run its use brings
    When their runs' file is dumped, written, and loaded by a later session
    Then each task and run reads back as it was, in the order written"""
    given_kept = tuple(Kept(task, run) for task, run in kept)
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "runs.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(dump(given_kept))

        assert load(path) == given_kept


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
@given(
    st.lists(WORDS, min_size=1, max_size=3),
    WORDS,
    st.lists(NAMES, min_size=2, max_size=6, unique=True),
)
def test_each_reply_lies_in_its_own_file_beside_the_queue_file(
    folders: list[str], queue: str, names: list[str]
):
    """Given any queue file, of any folder and name, and any tasks of distinct names
    When where overnight writes for it is found
    Then its folder lies beside the queue file under its name, and each task's reply is a file of
    its own there, apart from the runs and the lock"""
    queue_file = os.path.join(os.sep, *folders, queue + ".json")
    place = of(queue_file)

    assert place.folder == os.path.join(os.sep, *folders, queue)
    replies = [place.reply(name) for name in names]
    assert len(set(replies)) == len(names)
    assert all(os.path.dirname(each) == place.folder for each in replies)
    assert not {place.runs, place.lock} & set(replies)


@pytest.mark.supports("test_a_task_left_unended_by_a_stop_ends_given_up_with_that_reason")
@given(runs(), MOMENTS)
def test_a_stop_ends_each_run_with_its_session_kept(run: Run, seen):
    """Given any run, and any moment at which its runner's stop is seen
    When what the run becomes is found
    Then a run that ended is as it was, and any other is given up then with why, its session,
    stops, and waits kept"""
    given_run = left(run, seen)

    if run.state in ("finished", "given up"):
        assert given_run == run
    else:
        assert (given_run.state, given_run.ended, bool(given_run.why)) == ("given up", seen, True)
        assert (given_run.session, given_run.stops, given_run.waits) == (
            run.session,
            run.stops,
            run.waits,
        )


@pytest.mark.supports("test_stacking_again_carries_on_each_unfinished_task_in_its_session")
@given(runs())
def test_stacking_again_carries_on_each_unfinished_run_in_its_session(run: Run):
    """Given any run of a runner that stopped
    When its queue is stacked again
    Then a finished run is as it was, and any other waits for the start in its session, with no
    stops, none of its earlier waits, no end, and no why"""
    given_run = carried_on(run)

    if run.state == "finished":
        assert given_run == run
    else:
        assert given_run == Run("waiting for the start", run.session, 0, (), None, None, None)


@pytest.mark.supports("test_a_resumed_tasks_reply_follows_its_earlier_one_with_the_wait")
@given(st.lists(TEXTS, min_size=1, max_size=5), st.lists(LOCAL_MOMENTS, min_size=4, max_size=4))
def test_each_part_of_a_reply_follows_the_one_before_with_the_line_of_its_wait(
    texts: list[str], stops: list
):
    """Given any replies of a task, each after the one before, and a wait before each but the
    first
    When each part is added at the end of the task's reply file
    Then the file holds each reply in order, each after the first following the line that says
    when the limit stopped the task and when it went on"""
    waits = [Wait(stop, stop + timedelta(minutes=61)) for stop in sorted(stops)]
    text = part(Reply(texts[0]), None)
    model = texts[0]
    for reply, wait in zip(texts[1:], waits):
        text += part(Reply(reply), wait)
        line = (
            f"(The usage limit stopped this task at {wait.stopped:%H:%M}."
            f" It went on at {wait.went_on:%H:%M}.)"
        )
        model += f"\n\n{line}\n\n{reply}"

    assert text.rstrip("\n") == model.rstrip("\n")

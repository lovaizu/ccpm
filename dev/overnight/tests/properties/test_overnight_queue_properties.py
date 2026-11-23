"""The property-based tests of a queue as the user writes it, as overnight's Test strategy names
them: each prompt is a path from the queue file's folder, as the README says, so a prompt named
from there and the same named whole read as one task (metamorphic, of Task); and a queue is taken
in only where each of its tasks can start, as P1.4 says, so its faults are none exactly where every
prompt and dir is there, no writing task meets a computer where the sandbox can't hold, and no
runner still carries it (model-based)."""

from __future__ import annotations

import json
import os
import tempfile

import pytest
from hypothesis import given
from hypothesis import strategies as st
from overnight_generators import NAMES, WORDS
from record.runs import Run
from record.store import Standing, Stood
from stacker.admission import faults
from stacker.queue_file import Queue, Task, read

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

PATHS = st.lists(WORDS, min_size=1, max_size=3)


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
@given(
    st.lists(
        st.tuples(NAMES, PATHS, st.booleans()), min_size=1, max_size=4, unique_by=lambda t: t[0]
    )
)
def test_a_prompt_named_from_the_queues_folder_and_named_whole_read_as_one_task(
    tasks: list[tuple[str, list[str], bool]],
):
    """Given any queue of tasks, each named as the form takes it, with a prompt's path of any
    folders and file names, and writing or not
    When the queue file naming each prompt from its folder, and the one naming each whole, are read
    Then both give the same tasks, each prompt whole under the queue's folder"""
    with tempfile.TemporaryDirectory() as top:
        folder = os.path.join(top, "my queues")
        os.makedirs(folder)
        relative = [
            {"name": n, "prompt": os.path.join(*p), "dir": top, "writes": w} for n, p, w in tasks
        ]
        whole = [dict(each, prompt=os.path.join(folder, each["prompt"])) for each in relative]
        paths = []
        for name, entries in (("from.json", relative), ("whole.json", whole)):
            paths.append(os.path.join(folder, name))
            with open(paths[-1], "w", encoding="utf-8") as f:
                json.dump({"tasks": entries}, f)

        first, second = read(paths[0]), read(paths[1])

        assert first.tasks == second.tasks
        assert [each.prompt for each in first.tasks] == [each["prompt"] for each in whole]


@pytest.mark.supports("test_a_queue_with_one_task_that_cant_start_runs_no_task")
@given(
    st.lists(st.tuples(st.booleans(), st.booleans(), st.booleans()), min_size=1, max_size=5),
    st.booleans(),
    st.sampled_from([None, False, True]),
)
def test_a_queue_has_no_fault_exactly_where_each_task_can_start(
    tasks: list[tuple[bool, bool, bool]], sandbox_holds: bool, carried: bool | None
):
    """Given any queue of tasks, each whose prompt is there or not, whose dir is there or not, and
    that writes or not; a computer where the sandbox holds or not; and a queue never stacked, or
    stacked with its runner stopped or still carrying it
    When its faults are found
    Then it has none exactly where every prompt and dir is there, no task writes where the sandbox
    can't hold, and no runner carries it"""
    with tempfile.TemporaryDirectory() as top:
        made = []
        for n, (prompt_there, dir_there, writes) in enumerate(tasks):
            prompt = os.path.join(top, f"task-{n}.md")
            folder = os.path.join(top, f"work-{n}")
            if prompt_there:
                open(prompt, "w", encoding="utf-8").close()
            if dir_there:
                os.makedirs(folder)
            made.append(Task(f"task-{n}", prompt, folder, writes))
        queue = Queue(os.path.join(top, "tonight.json"), None, tuple(made))
        run = Run("waiting for the start", None, 0, (), None, None, None)
        standing = (
            None
            if carried is None
            else Standing(carried, tuple(Stood(t, run, t.name + ".md") for t in made))
        )

        found = faults(queue, standing, sandbox_holds)

    can_start = all(p and d and (not w or sandbox_holds) for p, d, w in tasks) and not carried
    assert (found == ()) is can_start

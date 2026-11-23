"""The unit cases of stacker/queue_file.py, how a queue file reads as a queue: `read`, of the
walkthrough's queue file, of one with no start, of one task and of several, of prompts named from
the queue's folder, from a folder in it, and whole, of each end of the hour and of a task's name,
of two names that nearly match, and each refusal: a file not there, not JSON, of no tasks, of a task
without its dir, of an hour past 23:59, of a name the form refuses, of a field of no name, of
`writes` that isn't true or false, and of a name given twice."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from overnight_bench import Bench, bench, walkthrough
from stacker.queue_file import Queue, Refused, Task, read

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


@pytest.fixture
def b(tmp_path: Any, monkeypatch: Any) -> Bench:
    """The bench alone, in place of the one with the walkthrough written, as each case writes the
    prompts and the queue file it reads."""
    return bench(str(tmp_path), monkeypatch)


def review(b: Bench, **given: Any) -> dict[str, Any]:
    """The walkthrough's review of the payments, as the queue file holds it, with each field
    given."""
    return {
        "name": "review-payments",
        "prompt": "review-payments.md",
        "dir": b.path("work", "shop"),
        **given,
    }


def refused_naming(b: Bench, queue: Any, *words: str) -> None:
    """Asserts that the queue file of the queue is refused with each fault and its mend, the faults
    naming each word."""
    path = b.write(b.queue_file, queue if isinstance(queue, str) else json.dumps(queue))
    with pytest.raises(Refused) as refused:
        read(path)
    faults = refused.value.faults
    assert faults and all(each.what and each.mend for each in faults)
    for word in words:
        assert any(word in each.what + each.mend for each in faults), word


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_the_walkthroughs_queue_file_reads_as_its_queue(b: Bench):
    """Given the walkthrough's queue file from 23:00 of three tasks, only the fix writing
    When it is read
    Then it is the queue of the file's path, 23:00, and the three tasks in its order, each prompt
    whole from the queue's folder, the reviews that give no `writes` reading only"""
    path = walkthrough(b)

    assert read(path) == Queue(
        path,
        "23:00",
        (
            Task(
                "review-payments",
                b.path("overnight", "review-payments.md"),
                b.path("work", "shop"),
                False,
            ),
            Task(
                "review-refunds",
                b.path("overnight", "review-refunds.md"),
                b.path("work", "shop"),
                False,
            ),
            Task(
                "fix-flaky-checkout",
                b.path("overnight", "fix-flaky-checkout.md"),
                b.path("work", "shop-fix-flaky-checkout"),
                True,
            ),
        ),
    )


@pytest.mark.supports(
    "test_a_queue_without_start_starts_its_tasks_at_once",
    "test_a_queue_of_one_waits_and_ends_as_any_queue",
)
def test_a_queue_of_one_with_no_start_reads_as_starting_at_once(b: Bench):
    """Given a queue file of one task with no start
    When it is read
    Then it is the queue with no start and its one task"""
    path = b.queue({"tasks": [review(b)]})

    queue = read(path)

    assert (queue.start, [each.name for each in queue.tasks]) == (None, ["review-payments"])


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_prompts_named_from_a_folder_of_the_queues_and_whole_read_whole(b: Bench):
    """Given a queue file whose first prompt lies in its folder's `prompts/`, and whose second is
    named whole
    When it is read
    Then the first prompt is whole from the queue's folder, and the second as named"""
    whole = b.path("elsewhere", "review-refunds.md")
    path = b.queue(
        {
            "tasks": [
                review(b, prompt=os.path.join("prompts", "review-payments.md")),
                review(b, name="review-refunds", prompt=whole),
            ]
        }
    )

    queue = read(path)

    assert [each.prompt for each in queue.tasks] == [
        b.path("overnight", "prompts", "review-payments.md"),
        whole,
    ]


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
@pytest.mark.parametrize("start", ["00:00", "23:59", "09:05"])
def test_each_hour_of_the_day_reads_as_the_start(b: Bench, start: str):
    """Given a queue file from 00:00, 23:59, or 09:05
    When it is read
    Then its start is that hour"""
    assert read(b.queue({"start": start, "tasks": [review(b)]})).start == start


@pytest.mark.supports("test_a_queue_naming_a_task_twice_is_refused_with_its_mend")
@pytest.mark.parametrize("name", ["a", "Review.v2_final-1", "9"])
def test_a_name_the_form_takes_reads_as_the_tasks(b: Bench, name: str):
    """Given a queue file whose task is named by one letter, by letters, digits, dots, an
    underscore, and a hyphen, or by one digit
    When it is read
    Then the task has that name"""
    assert read(b.queue({"tasks": [review(b, name=name)]})).tasks[0].name == name


@pytest.mark.supports("test_a_queue_naming_a_task_twice_is_refused_with_its_mend")
def test_two_names_that_nearly_match_read_as_two_tasks(b: Bench):
    """Given a queue file of the tasks `review` and `review-2`
    When it is read
    Then it is the two tasks"""
    path = b.queue({"tasks": [review(b, name="review"), review(b, name="review-2")]})

    assert [each.name for each in read(path).tasks] == ["review", "review-2"]


@pytest.mark.supports("test_a_queue_naming_a_task_twice_is_refused_with_its_mend")
def test_a_queue_file_not_there_is_refused(b: Bench):
    """Given no queue file at the path
    When it is read
    Then it refuses with Refused, naming the path"""
    with pytest.raises(Refused) as refused:
        read(b.queue_file)

    assert any(b.queue_file in each.what + each.mend for each in refused.value.faults)


@pytest.mark.supports("test_a_queue_naming_a_task_twice_is_refused_with_its_mend")
@pytest.mark.parametrize(
    ("queue", "named"),
    [
        ('{"tasks": [', "tonight.json"),
        ({"start": "23:00"}, "tasks"),
        ({"tasks": []}, "tasks"),
        ({"tasks": [{"name": "review", "prompt": "review.md"}]}, "dir"),
        ({"start": "24:00", "tasks": [{"name": "r", "prompt": "r.md", "dir": "/w"}]}, "start"),
        ({"start": "7:00", "tasks": [{"name": "r", "prompt": "r.md", "dir": "/w"}]}, "start"),
        ({"tasks": [{"name": "-review", "prompt": "r.md", "dir": "/w"}]}, "-review"),
        ({"tasks": [{"name": "my review", "prompt": "r.md", "dir": "/w"}]}, "my review"),
        ({"tasks": [{"name": "r", "prompt": "r.md", "dir": "/w", "model": "x"}]}, "model"),
        ({"tasks": [{"name": "r", "prompt": "r.md", "dir": "/w", "writes": "yes"}]}, "writes"),
        ({"tasks": [{"name": "r", "prompt": "", "dir": "/w"}]}, "prompt"),
    ],
    ids=[
        "not JSON",
        "no tasks",
        "none",
        "no dir",
        "24:00",
        "7:00",
        "name's start",
        "space",
        "field",
        "writes",
        "empty prompt",
    ],
)
def test_a_queue_file_out_of_its_form_is_refused_with_its_mend(b: Bench, queue: Any, named: str):
    """Given a queue file that isn't JSON, that lacks its tasks, holds none, holds a task without
    its dir, starts at 24:00 or at 7:00, names a task with a leading hyphen or a space, holds a
    field of no name, a `writes` that isn't true or false, or an empty prompt
    When it is read
    Then it refuses with each fault and its mend, a fault naming what's wrong"""
    refused_naming(b, queue, named)


@pytest.mark.supports("test_a_queue_naming_a_task_twice_is_refused_with_its_mend")
def test_a_queue_naming_a_task_twice_is_refused_naming_it(b: Bench):
    """Given a queue file of three tasks, the first and third both named `review`
    When it is read
    Then it refuses with a fault naming `review`"""
    tasks = [review(b, name="review"), review(b, name="review-2"), review(b, name="review")]

    refused_naming(b, {"tasks": tasks}, "review")

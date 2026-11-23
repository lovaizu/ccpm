"""The unit cases of record/place.py, where overnight keeps what it writes for a queue: `of`, for
the walkthrough's queue file, one whose name holds dots, one in a folder whose name holds a space,
and two queue files of one folder; and `Place.reply`, of the walkthrough's task and of a task whose
name holds dots."""

from __future__ import annotations

import os

import pytest
from record.place import of

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

QUEUE_FILE = os.path.join(os.sep, "home", "dev", "overnight", "tonight.json")
FOLDER = os.path.join(os.sep, "home", "dev", "overnight", "tonight")


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_the_walkthroughs_queue_is_kept_in_the_folder_beside_it_named_after_it():
    """Given the walkthrough's queue file, `/home/dev/overnight/tonight.json`
    When where overnight writes for it is found
    Then its folder is `/home/dev/overnight/tonight`, its runs' file `runs.json` there, and its
    runner's lock a file there of another name"""
    place = of(QUEUE_FILE)

    assert (place.folder, place.runs) == (FOLDER, os.path.join(FOLDER, "runs.json"))
    assert os.path.dirname(place.lock) == FOLDER
    assert place.lock != place.runs


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_a_queue_file_whose_name_holds_dots_is_kept_under_its_name_without_json():
    """Given the queue file `/home/dev/overnight/night.v2.json`
    When where overnight writes for it is found
    Then its folder is `/home/dev/overnight/night.v2`"""
    place = of(os.path.join(os.sep, "home", "dev", "overnight", "night.v2.json"))

    assert place.folder == os.path.join(os.sep, "home", "dev", "overnight", "night.v2")
    assert place.runs == os.path.join(place.folder, "runs.json")


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_a_queue_file_in_a_folder_whose_name_holds_a_space_is_kept_beside_it():
    """Given the queue file `/home/dev/my queues/tonight.json`
    When where overnight writes for it is found
    Then its folder is `/home/dev/my queues/tonight`"""
    place = of(os.path.join(os.sep, "home", "dev", "my queues", "tonight.json"))

    assert place.folder == os.path.join(os.sep, "home", "dev", "my queues", "tonight")


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_two_queue_files_of_one_folder_are_kept_apart():
    """Given the queue files `tonight.json` and `tonight-2.json` of one folder
    When where overnight writes for each is found
    Then their folders, runs' files, and locks all differ"""
    first = of(QUEUE_FILE)
    second = of(os.path.join(os.sep, "home", "dev", "overnight", "tonight-2.json"))

    assert len({first.folder, second.folder, first.runs, second.runs, first.lock, second.lock}) == 6


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_a_tasks_reply_lies_in_the_queues_folder_by_its_name():
    """Given the walkthrough's queue's place
    When the reply file of `review-payments` is found
    Then it is `/home/dev/overnight/tonight/review-payments.md`, apart from the runs and the lock"""
    place = of(QUEUE_FILE)

    reply = place.reply("review-payments")

    assert reply == os.path.join(FOLDER, "review-payments.md")
    assert reply not in (place.runs, place.lock)


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_a_tasks_reply_whose_name_holds_dots_keeps_them():
    """Given the walkthrough's queue's place
    When the reply file of `review.v2` is found
    Then it is `/home/dev/overnight/tonight/review.v2.md`"""
    assert of(QUEUE_FILE).reply("review.v2") == os.path.join(FOLDER, "review.v2.md")

"""The unit cases of record/replies.py, how a task's reply lies on disk: `part`, of a task's first
part, of a part after one wait, as the README shows the reply of the review that waited, and of a
third part after a second wait, each added at the end of the reply file."""

from __future__ import annotations

import pytest
from overnight_bench import (
    AFTER_THE_LIMIT,
    BEFORE_THE_LIMIT,
    PAYMENTS_ENDED,
    STOPPED,
    WENT_ON,
    at,
    payments_reply,
)
from record.replies import Reply, part
from record.runs import Wait

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


@pytest.mark.supports("test_a_resumed_tasks_reply_follows_its_earlier_one_with_the_wait")
def test_a_tasks_first_part_is_its_text():
    """Given the first reply of the review of the payments, with no wait before it
    When its part is made
    Then it is the reply's text, before any line break at its end"""
    assert part(Reply(BEFORE_THE_LIMIT), None).rstrip("\n") == BEFORE_THE_LIMIT


@pytest.mark.supports("test_a_resumed_tasks_reply_follows_its_earlier_one_with_the_wait")
def test_a_part_after_a_wait_follows_the_line_of_the_wait():
    """Given the review's first part, and its second reply after the wait from 00:41 to 01:42
    When the second part is made and added after the first
    Then the reply file is the README's: the first part, the line saying the limit stopped the task
    at 00:41 and it went on at 01:42, and the second part"""
    text = part(Reply(BEFORE_THE_LIMIT), None) + part(
        Reply(AFTER_THE_LIMIT), Wait(STOPPED, WENT_ON)
    )

    assert text.rstrip("\n") == payments_reply()


@pytest.mark.supports("test_a_resumed_tasks_reply_follows_its_earlier_one_with_the_wait")
def test_each_part_after_a_wait_follows_the_line_of_its_own_wait():
    """Given three replies of a task, after a wait from 00:41 to 01:42 and one from 02:16 to 03:05
    When each part is made and added after the one before
    Then each line names its own wait, the second's 02:16 and 03:05, in the parts' order"""
    text = (
        part(Reply("one"), None)
        + part(Reply("two"), Wait(STOPPED, WENT_ON))
        + part(Reply("three"), Wait(PAYMENTS_ENDED, at(3, 5, 1)))
    )

    assert text.rstrip("\n") == (
        "one\n\n(The usage limit stopped this task at 00:41. It went on at 01:42.)\n\ntwo\n\n"
        "(The usage limit stopped this task at 02:16. It went on at 03:05.)\n\nthree"
    )

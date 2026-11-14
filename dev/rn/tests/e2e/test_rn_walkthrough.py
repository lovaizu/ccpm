"""rn's E2E cases: the walkthrough of rn's README at its real size, run 3 times on the real Claude
Code on Opus by dev/scripts/e2e.py, with rn and Lane installed, in a fresh clone of
lovaizu/playground that holds invoicer, and an AI in the user's place that holds an intent rn
never receives: type hints for invoicer, with the plan of its two deliverables, the points
answered, each sign-off, and a pause and a pick-up in a new conversation. The developer runs them
once every unit and integration test passes, with their login as CLAUDE_CODE_OAUTH_TOKEN."""

from __future__ import annotations

import pytest
from rn_walkthroughs import (
    RUNS,
    handed_over,
    judge,
    kept_value,
    known_answers,
    kr1_1,
    kr1_2,
    walkthroughs,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


@pytest.fixture(scope="module")
def records() -> list[str]:
    """The records of 3 runs of the walkthrough."""
    return walkthroughs()


@pytest.mark.supports("KR1.1")
def test_kr1_1_the_share_of_deliverables_their_people_cant_use_is_no_larger_than_in_the_last_runs(
    records: list[str],
):
    """Given rn as it now stands, and the KR1.1 of the last runs kept
    When an AI in the user's place runs the walkthrough 3 times
    Then each run hands deliverables over, and the share of them that the judge finds their people
    can't use is no larger than the last runs'"""
    assert len(records) == RUNS and all(handed_over(each) for each in records)
    before, now = kept_value("KR1.1"), kr1_1(records)
    assert before is None or now <= before, f"KR1.1 rose from {before} to {now}"


@pytest.mark.supports("KR1.2")
def test_kr1_2_the_time_from_the_request_to_the_deliverable_is_no_longer_where_kr1_1_holds(
    records: list[str],
):
    """Given rn as it now stands, and the KR1.1 and KR1.2 of the last runs kept
    When an AI in the user's place runs the walkthrough 3 times
    Then, where KR1.1 is the last runs', the time from the request to the deliverable, the
    stand-in's own time answering included, is no longer than the last runs'"""
    before, held = kept_value("KR1.2"), kept_value("KR1.1")
    now = kr1_2(records)
    assert before is None or kr1_1(records) != held or now <= before, (
        f"KR1.2 rose from {before} to {now}"
    )


@pytest.mark.supports("KR1.1")
def test_the_judge_is_right_on_each_kept_deliverable_whose_answer_is_known():
    """Given each kept record of a deliverable handed over whose answer is known
    When the judge gives its verdict on it
    Then its verdict is the known answer on every one"""
    known = known_answers()
    wrong = [(r, d) for r, d, usable in known if judge(r, d).usable != usable]
    assert known and not wrong, wrong

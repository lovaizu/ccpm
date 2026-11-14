"""The unit cases of tree/sign_offs.py, what waits for the user's /rn:ty or /rn:gm and what they
signed off, through `parse`, `load`, `save`, `put_up`, `waiting`, `decide`, and `signed`."""

from __future__ import annotations

from typing import Any

import pytest
from fault import Wrong
from rn_example import CAN_DO, DECIMAL, HINTS, LESSON
from tree.sign_offs import (
    LESSON as OF_LESSON,
)
from tree.sign_offs import (
    PLAN,
    PULL_REQUEST,
    SENT_BACK,
    SIGNED,
    WAITING,
    SignOff,
    decide,
    load,
    parse,
    put_up,
    save,
    signed,
    waiting,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

HINTS_UP = SignOff(HINTS, CAN_DO, (DECIMAL,))


@pytest.mark.supports("test_once_the_hints_are_signed_off_the_typed_marker_is_marked_doing")
def test_parse_reads_a_deliverables_sign_off_waiting():
    """Given the hints' sign-off as the orchestrator writes it
    When it's read
    Then it's the hints, with what its people can do and the Decimal decision, waiting"""
    given = {"of": HINTS, "can_do": CAN_DO, "decisions": [DECIMAL], "words": ""}
    assert parse(given, "sign-off.json") == SignOff(HINTS, CAN_DO, (DECIMAL,), "", WAITING)


@pytest.mark.supports("test_a_lesson_without_its_words_cant_be_put_up")
def test_parse_reads_a_lesson_with_its_words():
    """Given a lesson with its words
    When it's read
    Then it's a lesson holding those words"""
    given = {"of": "lesson", "can_do": "", "decisions": [], "words": LESSON}
    assert parse(given, "s").words == LESSON


@pytest.mark.parametrize(
    "given",
    [
        {"of": "lesson", "can_do": "", "decisions": [], "words": ""},
        {"of": HINTS, "can_do": CAN_DO, "decisions": [], "words": LESSON},
        {"of": HINTS, "can_do": CAN_DO, "decisions": []},
        {"of": HINTS, "can_do": CAN_DO, "decisions": "Decimal", "words": ""},
        [],
    ],
)
@pytest.mark.supports("test_a_lesson_without_its_words_cant_be_put_up")
def test_parse_refuses_a_sign_off_out_of_its_form_naming_the_field(given: Any):
    """Given a lesson without words, a deliverable with words, one with no `words`, one whose
    decisions are a string, or a list
    When it's read
    Then it's refused, naming the file"""
    with pytest.raises(Wrong, match="sign-off.json"):
        parse(given, "sign-off.json")


@pytest.mark.supports("test_gm_after_done_sends_the_pull_request_handed_over_back_to_a_draft")
def test_parse_refuses_the_pull_request_handed_over_from_the_orchestrator():
    """Given a sign-off of the pull request handed over, as the orchestrator might write one
    When it's read
    Then it's refused, as only `tree.py ready` puts the pull request up"""
    given = {"of": PULL_REQUEST, "can_do": "", "decisions": [], "words": ""}
    with pytest.raises(Wrong, match="sign-off.json"):
        parse(given, "sign-off.json")


@pytest.mark.supports(
    "test_ty_after_done_signs_off_the_pull_request_handed_over_and_leaves_it_ready"
)
def test_decide_approved_signs_off_the_pull_request_handed_over():
    """Given the plan and both deliverables signed off, and the pull request handed over waiting
    When the user's /rn:ty decides
    Then the pull request handed over is signed, and nothing waits"""
    handed = (SignOff(PLAN, "", state=SIGNED), SignOff(PULL_REQUEST, ""))
    kept, decided = decide(handed, approved=True)
    assert (decided.of, decided.state) == (PULL_REQUEST, SIGNED) and waiting(kept) is None


@pytest.mark.supports("test_gm_after_done_sends_the_pull_request_handed_over_back_to_a_draft")
def test_decide_not_approved_sends_the_pull_request_handed_over_back():
    """Given the plan and both deliverables signed off, and the pull request handed over waiting
    When the user's /rn:gm decides
    Then the pull request handed over is sent back"""
    handed = (SignOff(PLAN, "", state=SIGNED), SignOff(PULL_REQUEST, ""))
    _, decided = decide(handed, approved=False)
    assert (decided.of, decided.state) == (PULL_REQUEST, SENT_BACK)


@pytest.mark.supports("test_the_users_ty_signs_off_the_plan_waiting")
def test_load_of_a_run_with_no_sign_offs_gives_none(tmp_path: Any):
    """Given a run's folder with no sign-offs.json
    When its Sign-offs are loaded
    Then there are none"""
    assert load(str(tmp_path)) == ()


@pytest.mark.supports("test_the_users_ty_signs_off_the_plan_waiting")
def test_save_writes_what_load_reads(tmp_path: Any):
    """Given the plan signed and the hints waiting
    When they're saved in a run's folder and loaded
    Then they're the same, in their order"""
    kept = (SignOff(PLAN, "", state=SIGNED), HINTS_UP)
    save(str(tmp_path), kept)
    assert load(str(tmp_path)) == kept


@pytest.mark.supports("test_the_users_ty_signs_off_the_plan_waiting")
def test_put_up_adds_the_sign_off_waiting_after_the_others():
    """Given the plan signed
    When the hints are put up
    Then they come after the plan, waiting"""
    assert put_up((SignOff(PLAN, "", state=SIGNED),), HINTS_UP)[-1] == HINTS_UP


@pytest.mark.supports("test_the_users_ty_signs_off_the_plan_waiting")
def test_put_up_refuses_one_of_the_same_thing_still_waiting():
    """Given the hints waiting
    When the hints are put up again
    Then it's refused, naming the hints"""
    with pytest.raises(Wrong, match=HINTS):
        put_up((HINTS_UP,), HINTS_UP)


@pytest.mark.supports("test_the_users_ty_signs_off_the_plan_waiting")
def test_put_up_takes_again_one_sent_back():
    """Given the hints sent back
    When the hints are put up again
    Then the new one waits"""
    assert waiting(put_up((SignOff(HINTS, CAN_DO, state=SENT_BACK),), HINTS_UP)) == HINTS_UP


@pytest.mark.supports("test_the_users_ty_signs_off_the_plan_waiting")
def test_waiting_is_the_first_that_waits():
    """Given the plan signed, the hints waiting, and a lesson waiting after them
    When the one waiting is asked for
    Then it's the hints"""
    lesson = SignOff(OF_LESSON, "", words=LESSON)
    assert waiting((SignOff(PLAN, "", state=SIGNED), HINTS_UP, lesson)) == HINTS_UP


@pytest.mark.supports("test_ty_with_nothing_waiting_doesnt_load")
def test_waiting_of_none_waiting_is_none():
    """Given only the plan signed
    When the one waiting is asked for
    Then there's none"""
    assert waiting((SignOff(PLAN, "", state=SIGNED),)) is None


@pytest.mark.supports("test_the_users_ty_signs_off_the_plan_waiting")
def test_decide_approved_signs_off_the_first_waiting():
    """Given the hints waiting
    When the user's /rn:ty decides
    Then the hints are signed"""
    kept, decided = decide((HINTS_UP,), approved=True)
    assert decided.state == SIGNED and kept == (decided,)


@pytest.mark.supports("test_gm_with_what_to_change_sends_the_sign_off_back_and_carries_their_words")
def test_decide_not_approved_sends_the_first_waiting_back():
    """Given the hints waiting
    When the user's /rn:gm decides
    Then the hints are sent back"""
    _, decided = decide((HINTS_UP,), approved=False)
    assert decided.state == SENT_BACK


@pytest.mark.supports("test_ty_with_nothing_waiting_doesnt_load")
def test_decide_with_none_waiting_is_refused_saying_nothing_waits():
    """Given only the plan signed
    When the user's /rn:ty decides
    Then it's refused, saying nothing waits"""
    with pytest.raises(Wrong, match="nothing waits"):
        decide((SignOff(PLAN, "", state=SIGNED),), approved=True)


@pytest.mark.parametrize(
    ("kept", "expected"),
    [
        ((SignOff(PLAN, "", state=SIGNED),), True),
        ((SignOff(PLAN, ""),), False),
        ((SignOff(PLAN, "", state=SENT_BACK),), False),
        ((SignOff(PLAN, "", state=SIGNED), SignOff(PLAN, "")), False),
        ((), False),
    ],
)
@pytest.mark.supports("test_no_deliverable_is_marked_doing_before_the_plan_is_signed_off")
def test_signed_holds_only_where_the_last_of_it_is_signed(
    kept: tuple[SignOff, ...], expected: bool
):
    """Given the plan signed, waiting, sent back, signed and then put up again, or never put up
    When whether the plan is signed off is asked
    Then it's signed off only where it's signed and nothing of it waits since"""
    assert signed(kept, PLAN) is expected

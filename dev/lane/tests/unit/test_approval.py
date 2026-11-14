"""The unit cases of domain/approval.py: up's Proposal given word for word, a run of `lay.py write`
as the caller's own act, and a Run of up that ends without one, through `shown_whole`,
`own_act`, and `ends_unapproved`."""

from __future__ import annotations

import pytest
from domain.approval import ends_unapproved, own_act, shown_whole
from domain.event import COMMAND, Call
from domain.run_record import AI, PERSON, Run
from lane_parts import run

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

SHOWN = "Routes of write, laid on its step 1:\n  first  start writer\n\nID: b9fd8fd8\n"
WRITE = Call(COMMAND, command="python3 /lane/scripts/lay.py write changelog b9fd8fd8")


def up_run(by: str, prompted: bool, shown: str = SHOWN) -> Run:
    return run(plugin="lane", skill="up", by=by, shown=shown, prompted=prompted)


@pytest.mark.supports(
    "test_up_ending_its_turn_without_the_proposal_word_for_word_is_stopped_with_it"
)
def test_a_message_that_holds_what_print_showed_word_for_word_shows_it_whole():
    """Given a Run of up whose `lay.py print` showed a Proposal
    When up's message holds it word for word, with the question after it
    Then it shows the Proposal whole"""
    message = SHOWN + "Reply yes to lay these, or say what to change."
    assert shown_whole(up_run(PERSON, False), message)


@pytest.mark.supports(
    "test_up_ending_its_turn_without_the_proposal_word_for_word_is_stopped_with_it"
)
def test_a_message_that_tells_the_proposal_in_other_words_shows_it_not():
    """Given a Run of up whose `lay.py print` showed a Proposal
    When up's message says `Lane proposes one route. Reply yes.`
    Then it doesn't show the Proposal whole"""
    assert not shown_whole(up_run(PERSON, False), "Lane proposes one route. Reply yes.")


@pytest.mark.supports("test_a_reply_that_is_neither_yes_nor_a_change_ends_the_run_of_up")
def test_a_message_where_no_print_showed_anything_needs_nothing():
    """Given a Run of up in which no `lay.py print` showed anything
    When up's message says anything
    Then it passes as whole"""
    assert shown_whole(up_run(PERSON, False, shown=""), "Which plugin?")


@pytest.mark.supports("test_a_persons_yes_lays_the_proposal_and_validation_passes")
def test_lay_write_after_the_persons_prompt_since_print_is_their_act():
    """Given a Run of up that a person started, who typed a prompt since the last `lay.py print`
    When up runs `lay.py write`
    Then it's the caller's own act"""
    assert own_act(up_run(PERSON, True), WRITE)


@pytest.mark.supports("test_lay_write_before_the_persons_reply_is_stopped")
def test_lay_write_with_no_prompt_since_print_in_a_persons_run_is_no_act_of_theirs():
    """Given a Run of up that a person started, who typed nothing since the last `lay.py print`
    When up runs `lay.py write`
    Then it isn't the caller's own act"""
    assert not own_act(up_run(PERSON, False), WRITE)


@pytest.mark.supports(
    "test_an_ai_that_called_up_by_the_skill_tool_lays_by_its_own_run_of_lay_write"
)
def test_lay_write_in_a_run_an_ai_started_is_its_own_act():
    """Given a Run of up that an AI started by the Skill tool
    When it runs `lay.py write`
    Then it's the caller's own act"""
    assert own_act(up_run(AI, False), WRITE)


@pytest.mark.supports("test_lay_write_before_the_persons_reply_is_stopped")
def test_a_command_that_isnt_lay_write_is_no_act():
    """Given a Run of up that a person started, who typed a prompt since
    When up runs `python3 /lane/scripts/lay.py print changelog p.json`
    Then it isn't an act of approval"""
    other = Call(COMMAND, command="python3 /lane/scripts/lay.py print changelog p.json")
    assert not own_act(up_run(PERSON, True), other)


@pytest.mark.supports("test_a_reply_that_is_neither_yes_nor_a_change_ends_the_run_of_up")
def test_a_turn_after_the_persons_prompt_with_no_write_or_print_ends_the_run():
    """Given a Run of up in which the person typed a prompt after the Proposal shown, and the turn
    ran no `lay.py write` or `lay.py print` since
    When it's asked whether the Run ends with the turn
    Then it does"""
    assert ends_unapproved(up_run(PERSON, True))


@pytest.mark.supports("test_a_change_the_person_asks_goes_into_the_step_and_up_proposes_again")
def test_a_turn_with_a_new_print_after_the_persons_prompt_keeps_the_run():
    """Given a Run of up in which the person asked a change, and up ran `lay.py print` again, so
    that no prompt came since the new Proposal
    When it's asked whether the Run ends with the turn
    Then it doesn't"""
    assert not ends_unapproved(up_run(PERSON, False))

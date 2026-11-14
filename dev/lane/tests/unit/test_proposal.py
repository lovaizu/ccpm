"""The unit cases of scripts/proposal.py: a Proposal read from up's JSON, whether it can stand
against the lane types, the Steps, and the plugin's files, and each Proposal kept by its ID, through
`parse`, `check`, `moves_of`, `keep`, and `kept`."""

from __future__ import annotations

import copy
import os
from typing import Any

import pytest
from domain.fault import Fault
from domain.laid_set import Laid, Move
from domain.run_record import PERSON, Run
from lane_example import PROPOSAL, REVIEWER, lane, put, put_plugin, route, start
from proposal import Proposal, check, keep, kept, moves_of, parse, waits
from steps import roles

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.fixture
def plugin(tmp_path: Any) -> str:
    """The walkthrough's `changelog` in a folder of the test's own."""
    return put_plugin(os.path.join(os.path.realpath(str(tmp_path)), "changelog"))


def refusal(plugin: str, given: dict[str, Any]) -> Any:
    """What `check` gives for the Proposal of the JSON on the plugin."""
    return check(parse(given, "p.json"), roles(plugin, Laid()), plugin)


def changed(**fields: Any) -> dict[str, Any]:
    given = copy.deepcopy(PROPOSAL)
    given.update(fields)
    return given


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_the_walkthroughs_json_reads_as_its_proposal():
    """Given the walkthrough's Proposal as up writes it
    When it's parsed
    Then it holds `changelog`, the skill `write`, five Lanes, and four Routes, with no ID yet"""
    found = parse(PROPOSAL, "p.json")
    assert (found.plugin, found.skills, len(found.lanes), len(found.routes), found.id) == (
        "changelog",
        ("write",),
        5,
        4,
        "",
    )


@pytest.mark.supports("test_lay_print_refuses_a_proposal_not_in_the_form_of_the_schema")
def test_json_whose_lane_has_no_type_raises_a_fault_naming_type_with_up_to_mend_it():
    """Given the walkthrough's Proposal with no `type` in its first Lane
    When it's parsed
    Then a Fault names `type`, with up to mend it"""
    given = copy.deepcopy(PROPOSAL)
    del given["lanes"][0]["type"]
    with pytest.raises(Fault, match="type") as raised:
        parse(given, "p.json")
    assert raised.value.who == "up"


@pytest.mark.supports("test_lay_print_refuses_a_proposal_not_in_the_form_of_the_schema")
def test_json_with_a_move_of_a_kind_there_isnt_raises_a_fault_naming_the_kind():
    """Given the walkthrough's Proposal whose first move is of the kind `jump`
    When it's parsed
    Then a Fault names `jump`"""
    given = changed(routes=[route("first", {"kind": "jump", "role": "writer"})])
    with pytest.raises(Fault, match="jump"):
        parse(given, "p.json")


@pytest.mark.supports("test_lay_print_refuses_a_proposal_not_in_the_form_of_the_schema")
def test_json_with_a_step_of_0_raises_a_fault():
    """Given the walkthrough's Proposal whose first Lane is on step 0
    When it's parsed
    Then a Fault names `step`"""
    given = copy.deepcopy(PROPOSAL)
    given["lanes"][0]["step"] = 0
    with pytest.raises(Fault, match="step"):
        parse(given, "p.json")


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_the_walkthroughs_proposal_stands(plugin: str):
    """Given the walkthrough's `changelog` and Proposal
    When it's checked
    Then it stands"""
    assert refusal(plugin, PROPOSAL) is None


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_a_lane_of_a_type_there_isnt_is_refused_for_up_to_mend(plugin: str):
    """Given the walkthrough's Proposal with a Lane of the type `run_never`
    When it's checked
    Then it's refused, naming `run_never`, for up to mend"""
    found = refusal(
        plugin, changed(lanes=[*PROPOSAL["lanes"], lane("writer", 1, "run_never", "ls")])
    )
    assert found and not found.in_files and "run_never" in " ".join(found.faults)


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_a_lane_on_a_step_there_isnt_is_refused(plugin: str):
    """Given the walkthrough's Proposal with a Lane on writer's step 5, which writer lacks
    When it's checked
    Then it's refused, naming writer's step 5"""
    found = refusal(
        plugin, changed(lanes=[*PROPOSAL["lanes"], lane("writer", 5, "run_only", "ls")])
    )
    assert found and "5" in " ".join(found.faults)


@pytest.mark.supports(
    "test_lay_print_refuses_an_ends_checked_lane_of_the_skill_naming_a_value_no_start_fills"
)
def test_a_lane_that_its_type_says_cant_stand_is_refused(plugin: str):
    """Given the walkthrough's Proposal with an ends_checked Lane of the skill on
    `python3 check.py {deliverable}`
    When it's checked
    Then it's refused, naming `{deliverable}`"""
    more = lane("write", 1, "ends_checked", "python3 check.py {deliverable}")
    found = refusal(plugin, changed(lanes=[*PROPOSAL["lanes"], more]))
    assert found and "{deliverable}" in " ".join(found.faults)


@pytest.mark.supports("test_lay_print_refuses_routes_that_reach_neither_each_role_nor_each_result")
def test_a_result_that_no_route_goes_after_is_refused(plugin: str):
    """Given the walkthrough's Proposal with no Route after `reviewer more`
    When it's checked
    Then it's refused, naming reviewer's `more`"""
    routes = [r for r in PROPOSAL["routes"] if r["after"] != "reviewer more"]
    found = refusal(plugin, changed(routes=routes))
    assert found and "more" in " ".join(found.faults)


@pytest.mark.supports("test_lay_print_refuses_routes_that_reach_neither_each_role_nor_each_result")
def test_a_role_that_no_route_starts_is_refused(plugin: str):
    """Given the walkthrough's Proposal whose Route after `writer written` starts no more, so no
    Route starts reviewer
    When it's checked
    Then it's refused, naming reviewer"""
    routes = [route("first", start("writer")), route("writer written", {"kind": "no_more"})]
    found = refusal(plugin, changed(routes=routes))
    assert found and "reviewer" in " ".join(found.faults)


@pytest.mark.supports("test_lay_print_refuses_a_subagent_whose_file_doesnt_set_background_true")
def test_a_subagent_without_background_true_is_refused_for_the_user_to_mend(plugin: str):
    """Given `changelog` whose reviewer doesn't set `background: true`
    When the walkthrough's Proposal is checked
    Then it's refused in the plugin's files, naming agents/reviewer.md"""
    put(plugin, "agents/reviewer.md", REVIEWER.replace("background: true\n", ""))
    found = refusal(plugin, PROPOSAL)
    assert found and found.in_files and "agents/reviewer.md" in " ".join(found.faults)


@pytest.mark.supports(
    "test_lay_print_refuses_a_command_that_a_route_waits_for_and_the_model_may_call"
)
def test_a_waited_command_the_model_may_call_is_refused_for_the_user_to_mend(plugin: str):
    """Given `changelog` with a command `approve` that doesn't set `disable-model-invocation: true`
    When a Proposal whose Route waits for `/changelog:approve` is checked
    Then it's refused in the plugin's files, naming skills/approve/SKILL.md"""
    put(plugin, "skills/approve/SKILL.md", "---\nname: approve\n---\n\n## Steps\n\n1. Go on.\n")
    routes = [
        *PROPOSAL["routes"][:3],
        route("reviewer good", start("writer", "/changelog:approve")),
    ]
    given = parse(changed(routes=routes), "p.json")
    found = check(given, roles(plugin, Laid(), {"approve": "write"}), plugin)
    assert found and found.in_files and "skills/approve/SKILL.md" in " ".join(found.faults)


@pytest.mark.supports(
    "test_lay_print_refuses_a_proposal_that_leaves_out_an_adapter_and_shows_the_mended_one"
)
def test_a_program_in_hooks_adapters_that_the_proposal_doesnt_name_is_refused_for_up(plugin: str):
    """Given `changelog` with a program `text` in hooks/adapters/
    When the walkthrough's Proposal, which names none, is checked
    Then it's refused for up to mend, naming hooks/adapters/text"""
    put(plugin, "hooks/adapters/text", "#!/bin/sh\n")
    found = refusal(plugin, PROPOSAL)
    assert found and not found.in_files and "hooks/adapters/text" in " ".join(found.faults)


@pytest.mark.supports(
    "test_lay_print_refuses_a_proposal_that_leaves_out_an_adapter_and_shows_the_mended_one"
)
def test_an_adapter_named_that_isnt_in_hooks_adapters_is_refused(plugin: str):
    """Given `changelog` with no hooks/adapters/
    When the walkthrough's Proposal naming the adapter `text` is checked
    Then it's refused, naming `text`"""
    found = refusal(plugin, changed(text_adapter="text"))
    assert found and "text" in " ".join(found.faults)


@pytest.mark.supports("test_lay_print_refuses_two_roles_that_take_their_steps_from_one_file")
def test_two_roles_that_take_their_steps_from_one_file_are_refused_for_the_user(plugin: str):
    """Given writer and reviewer that both name `${CLAUDE_PLUGIN_ROOT}/domain/part.md`
    When the walkthrough's Proposal is checked
    Then it's refused in the plugin's files, naming domain/part.md"""
    put(plugin, "domain/part.md", "## Steps\n\n1. Read.\n2. Give `good`.\n3. More.\n4. End.\n")
    for role in ("writer", "reviewer"):
        put(
            plugin,
            f"agents/{role}.md",
            f"---\nname: {role}\nbackground: true\n---\n\n"
            "Read ${CLAUDE_PLUGIN_ROOT}/domain/part.md.\n",
        )
    found = refusal(plugin, PROPOSAL)
    assert found and found.in_files and "domain/part.md" in " ".join(found.faults)


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_the_moves_after_a_moment_are_those_of_its_route_or_none():
    """Given the walkthrough's Proposal
    When the moves of `write` after `writer written`, after `writer skipped`, and those of a skill
    `review` that it doesn't name, are asked
    Then the first start reviewer, and the others are none"""
    given = parse(PROPOSAL, "p.json")
    assert moves_of(given, "write", "writer written") == (Move("start", "reviewer"),)
    assert moves_of(given, "write", "writer skipped") == ()
    assert moves_of(given, "review", "writer written") == ()


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_a_proposal_kept_gets_an_id_each_lanes_sentence_from_its_type_and_the_steps_fingerprint(
    plugin: str, tmp_path: Any
):
    """Given the walkthrough's Proposal, checked on `changelog`
    When it's kept
    Then it has an ID of 8 hex digits, writer's step 2 Lane reads `Run only `git log --oneline`.`,
    and it carries the fingerprint of the Steps"""
    found = keep(parse(PROPOSAL, "p.json"), roles(plugin, Laid()), str(tmp_path))
    assert len(found.id) == 8 and int(found.id, 16) >= 0
    assert found.lanes[1].sentence == "Run only `git log --oneline`."
    assert found.steps


@pytest.mark.supports("test_lay_write_of_an_id_that_no_proposal_has_is_refused")
def test_a_proposal_kept_is_found_by_its_id_and_another_id_finds_none(plugin: str, tmp_path: Any):
    """Given the walkthrough's Proposal kept
    When it's looked for by its ID, and by `00000000`
    Then the first finds it, and the second none"""
    found: Proposal = keep(parse(PROPOSAL, "p.json"), roles(plugin, Laid()), str(tmp_path))
    assert kept(str(tmp_path), "changelog", found.id) == found
    assert kept(str(tmp_path), "changelog", "00000000") is None


@pytest.mark.supports("test_a_change_the_person_asks_goes_into_the_step_and_up_proposes_again")
def test_two_proposals_kept_get_two_ids(plugin: str, tmp_path: Any):
    """Given the walkthrough's Proposal
    When it's kept twice
    Then the two have different IDs"""
    first = keep(parse(PROPOSAL, "p.json"), roles(plugin, Laid()), str(tmp_path))
    second = keep(parse(PROPOSAL, "p.json"), roles(plugin, Laid()), str(tmp_path))
    assert first.id != second.id


def shown_in(id: str, **fields: Any) -> Run:
    """A Run of up of the conversation c1 that a person started, which showed the Proposal of the
    ID last, with the fields given."""
    given: dict[str, Any] = {"plugin": "lane", "skill": "up", "session": "c1", "by": PERSON}
    given.update(shown=f"Routes of write, laid on its step 1:\n\nID: {id}\n", **fields)
    return Run(**given)


KEPT = Proposal("changelog", ("write",), (), (), id="b9fd8fd8", conversation="c1")


@pytest.mark.supports("test_lay_write_after_the_run_of_up_ended_without_approval_is_refused")
def test_a_proposal_kept_holds_the_conversation_that_showed_it(plugin: str, tmp_path: Any):
    """Given the walkthrough's Proposal, shown in the conversation c1
    When it's kept, and looked for by its ID
    Then the Proposal found holds c1"""
    found = keep(parse(PROPOSAL, "p.json"), roles(plugin, Laid()), str(tmp_path), "c1")
    again = kept(str(tmp_path), "changelog", found.id)
    assert found.conversation == "c1" and again is not None and again.conversation == "c1"


@pytest.mark.supports("test_a_persons_yes_lays_the_proposal_and_validation_passes")
def test_a_proposal_whose_run_of_up_goes_on_and_showed_it_last_waits():
    """Given a Proposal shown in c1, whose Run of up goes on and showed it last
    When it's asked whether the Proposal still waits
    Then it does"""
    assert waits(KEPT, shown_in("b9fd8fd8"))


@pytest.mark.supports("test_lay_write_after_the_run_of_up_ended_without_approval_is_refused")
def test_a_proposal_whose_run_of_up_ended_waits_not():
    """Given a Proposal shown in c1, whose Run of up showed it last and then ended
    When it's asked whether the Proposal still waits
    Then it doesn't"""
    assert not waits(KEPT, shown_in("b9fd8fd8", ended=True))


@pytest.mark.supports("test_lay_write_after_the_run_of_up_ended_without_approval_is_refused")
def test_a_proposal_that_its_conversations_run_of_up_doesnt_show_last_waits_not():
    """Given a Proposal shown in c1, whose Run of up a later `/lane:up` replaced with one that
    showed the Proposal 0c0c0c0c
    When it's asked whether the Proposal still waits
    Then it doesn't"""
    assert not waits(KEPT, shown_in("0c0c0c0c"))


@pytest.mark.supports(
    "test_an_ai_that_called_up_by_the_skill_tool_lays_by_its_own_run_of_lay_write"
)
def test_a_proposal_whose_conversation_has_no_run_of_up_waits():
    """Given a Proposal whose conversation holds no Run of up, as no Run of up showed it
    When it's asked whether the Proposal still waits
    Then it does"""
    assert waits(KEPT, None)


@pytest.mark.supports(
    "test_a_call_of_another_plugins_skill_that_a_move_names_sets_the_run_aside_until_a_move_after_it"
)
def test_json_with_a_move_that_calls_another_plugins_skill_reads_as_a_call():
    """Given the walkthrough's Proposal whose move after writer's `written` calls `tally:check`,
    and whose Route after that call starts reviewer
    When it's parsed
    Then that move is a call of `tally:check`, and a Route goes after `tally:check`"""
    given = changed(
        routes=[
            PROPOSAL["routes"][0],
            route("writer written", {"kind": "call", "role": "tally:check"}),
            route("tally:check", start("reviewer")),
            *PROPOSAL["routes"][2:],
        ]
    )
    found = parse(given, "p.json")
    assert found.routes[1].moves == (Move("call", "tally:check"),)
    assert found.routes[2].after == "tally:check"

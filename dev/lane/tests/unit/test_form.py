"""The unit cases of form.py, the form of Lanes, Routes, adapters, and the Laid, through
`proposal_form`, `read_proposal`, `read_lanes`, and `write_lanes`: each kind of What a Route goes
after and each kind of Move read as its own, each place a Proposal falls out of form, the edges of a
Step's number and of a Route's moves, and lanes.json kept as written."""

from __future__ import annotations

import copy
import json
import os
from typing import Any

import lane_data as d
import pytest
from form import (
    After,
    Move,
    OutOfForm,
    proposal_form,
    read_lanes,
    read_proposal,
    write_lanes,
)

LANE = os.path.join(os.path.dirname(d.__file__), *[".."] * 3, "plugins", "lane")
SCHEMA = os.path.join(LANE, "hooks", "lane", "domain", "lanes.schema.json")


def proposal_with(**changes: Any) -> str:
    """The walkthrough's Proposal as JSON text, with each top-level key changed."""
    given = copy.deepcopy(d.proposal_json())
    given.update(changes)
    return json.dumps(given)


@pytest.mark.supports("test_types_give_each_lane_type_and_the_form_of_a_proposal")
def test_the_form_of_a_proposal_is_the_schemas() -> None:
    """Given: Lane's lanes.schema.json.
    When: proposal_form gives the form of a Proposal.
    Then: it is the schema's definition of a Proposal, with the definitions it refers to."""
    with open(SCHEMA, encoding="utf-8") as f:
        schema = json.load(f)
    form = proposal_form()
    assert form["properties"] == schema["definitions"]["proposal"]["properties"]
    assert form["required"] == ["lanes", "routes", "adapters"]


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
def test_a_proposal_is_read_with_its_lanes_routes_and_adapters() -> None:
    """Given: the walkthrough's Proposal as up writes it.
    When: read_proposal reads it.
    Then: it gives its Lane of write's Routes, a Route after write's start that starts writer, and a
    Route after reviewer's `good` that starts no more by `good`."""
    proposal = read_proposal(json.dumps(d.proposal_json()))
    assert proposal.lanes == (d.ROUTES, d.WRITE_END)
    assert proposal.routes[0].after == After("first")
    assert proposal.routes[0].moves == (Move("start", role="writer"),)
    assert proposal.routes[1].after == After("result", role="reviewer", result="good")
    assert proposal.routes[1].moves == (Move("no_more", result="good"),)
    assert (proposal.adapters.text, proposal.adapters.records) == (None, None)


@pytest.mark.supports("test_a_move_that_waits_for_the_person_lets_the_turn_end")
@pytest.mark.parametrize(
    "after, read",
    [
        ({"command": "approve"}, After("command", command="approve")),
    ],
    ids=["command"],
)
def test_each_kind_of_after_is_read_as_its_own(after: dict[str, str], read: After) -> None:
    """Given: a Proposal with a Route after a typed command.
    When: read_proposal reads it.
    Then: the Route goes after what its kind names."""
    routes = [{"skill": "write", "after": after, "moves": [{"no_more": "good"}]}]
    assert read_proposal(proposal_with(routes=routes)).routes[0].after == read


@pytest.mark.supports("test_a_move_that_waits_for_the_person_lets_the_turn_end")
@pytest.mark.parametrize(
    "move, read",
    [
        ({"resume": "writer"}, Move("resume", role="writer")),
        ({"wait": "approve"}, Move("wait", command="approve")),
        ({"wait": ""}, Move("wait", command="")),
    ],
    ids=["resume", "wait for a command", "wait for a reply"],
)
def test_each_kind_of_move_is_read_as_its_own(move: dict[str, str], read: Move) -> None:
    """Given: a Proposal with a Route whose move resumes or waits.
    When: read_proposal reads it.
    Then: the move is of its kind, with what it names."""
    routes = [{"skill": "write", "after": {"first": True}, "moves": [move]}]
    assert read_proposal(proposal_with(routes=routes)).routes[0].moves == (read,)


@pytest.mark.supports("test_a_proposal_that_cant_stand_goes_back_to_up")
@pytest.mark.parametrize(
    "text",
    [
        "not json",
        proposal_with(lanes=None),
        json.dumps({"lanes": [], "routes": []}),
        proposal_with(extra=1),
        proposal_with(routes=[{"skill": "write", "after": {"first": True}, "moves": []}]),
        proposal_with(
            routes=[{"skill": "write", "after": {"first": False}, "moves": [{"start": "w"}]}]
        ),
        proposal_with(adapters={"other": "x"}),
    ],
    ids=[
        "not JSON",
        "lanes null",
        "no adapters",
        "an extra key",
        "no moves",
        "first false",
        "unknown adapter",
    ],
)
def test_a_proposal_out_of_form_is_refused(text: str) -> None:
    """Given: a Proposal that lanes.schema.json doesn't take.
    When: read_proposal reads it.
    Then: it raises OutOfForm, with at least one place and what the form takes there."""
    with pytest.raises(OutOfForm) as refused:
        read_proposal(text)
    assert refused.value.problems


@pytest.mark.supports("test_a_lane_on_a_step_that_isnt_there_goes_back_to_up")
@pytest.mark.parametrize("step, stands", [(0, False), (1, True)], ids=["step 0", "step 1"])
def test_a_steps_number_starts_at_1(step: int, stands: bool) -> None:
    """Given: a Proposal whose Lane lies on step 0, or on step 1.
    When: read_proposal reads it.
    Then: it refuses step 0 as out of form, and takes step 1."""
    lanes = [dict(d.proposal_json()["lanes"][0], step=step)]
    if stands:
        assert read_proposal(proposal_with(lanes=lanes)).lanes[0].step == 1
    else:
        with pytest.raises(OutOfForm):
            read_proposal(proposal_with(lanes=lanes))


@pytest.mark.supports("test_yes_lays_the_proposal_into_the_plugin")
def test_lanes_json_is_read_as_written(tmp_path: Any) -> None:
    """Given: no lanes.json.
    When: write_lanes writes the walkthrough's lanes.json, and read_lanes reads it.
    Then: it gives what was written."""
    path = str(tmp_path / "lanes.json")
    write_lanes(path, d.lanes_file())
    assert read_lanes(path) == d.lanes_file()


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_lanes_json_that_isnt_there_is_refused(tmp_path: Any) -> None:
    """Given: a plugin with no hooks/lanes.json.
    When: read_lanes reads it.
    Then: it raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_lanes(str(tmp_path / "lanes.json"))


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_lanes_json_out_of_form_is_refused(tmp_path: Any) -> None:
    """Given: a lanes.json with no Laid.
    When: read_lanes reads it.
    Then: it raises OutOfForm."""
    path = tmp_path / "lanes.json"
    path.write_text(json.dumps({"lanes": [], "routes": [], "adapters": {}}))
    with pytest.raises(OutOfForm):
        read_lanes(str(path))


@pytest.mark.supports("test_a_failed_validate_puts_back_each_file")
def test_lanes_json_that_cant_be_written_is_refused(tmp_path: Any) -> None:
    """Given: a folder where lanes.json must go.
    When: write_lanes writes it.
    Then: it raises OSError."""
    os.makedirs(tmp_path / "lanes.json")
    with pytest.raises(OSError):
        write_lanes(str(tmp_path / "lanes.json"), d.lanes_file())

"""The unit cases of scripts/lay.py, the command up runs, through `main` and `types_text`, on the
walkthrough's plugin in a folder of each test's own."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import pytest
from lane_example import PROPOSAL, REVIEWER, TYPES, WRITE, WRITER, put, read
from lay import USAGE, main, types_text

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.fixture
def cwd(tmp_path: Any) -> str:
    """A folder holding the walkthrough's `changelog`, and the Proposal in proposal.json."""
    root = os.path.realpath(str(tmp_path))
    plugin = os.path.join(root, "changelog")
    put(plugin, ".claude-plugin/plugin.json", '{"name": "changelog", "version": "0.1.0"}')
    put(plugin, "skills/write/SKILL.md", WRITE)
    put(plugin, "agents/writer.md", WRITER)
    put(plugin, "agents/reviewer.md", REVIEWER)
    put(root, "proposal.json", json.dumps(PROPOSAL))
    os.makedirs(os.path.join(root, "tmp"))
    return root


def env(cwd: str) -> dict[str, str]:
    return dict(os.environ, TMPDIR=os.path.join(cwd, "tmp"))


@pytest.mark.supports(
    "test_lay_types_gives_each_type_with_what_it_takes_the_steps_it_suits_and_its_sentence"
)
def test_types_names_each_lane_type():
    """Given Lane's lane types
    When `lay.py types` is asked for its text
    Then it names each of the six"""
    found = types_text()
    assert [name for name in TYPES if name not in found] == []


@pytest.mark.supports(
    "test_lay_types_gives_each_type_with_what_it_takes_the_steps_it_suits_and_its_sentence"
)
def test_types_exits_0_with_its_text(cwd: str):
    """Given Lane
    When `lay.py types` runs
    Then it exits 0 with the text of the types"""
    assert main(["types"], env(cwd), cwd) == (0, types_text(), "")


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_print_of_a_proposal_that_stands_exits_0_with_an_id(cwd: str):
    """Given the walkthrough's `changelog` and Proposal
    When `lay.py print changelog proposal.json` runs
    Then it exits 0, its text ending with an ID and the question"""
    code, out, _ = main(["print", "changelog", "proposal.json"], env(cwd), cwd)
    assert code == 0 and re.search(r"^ID: [0-9a-f]{8}$", out, re.MULTILINE)
    assert out.endswith("Reply yes to lay these into changelog, or say what to change.\n")


@pytest.mark.supports("test_lay_print_refuses_a_lane_of_a_type_there_isnt")
def test_print_of_a_proposal_that_cant_stand_exits_1_with_whats_wrong(cwd: str):
    """Given a Proposal with a Lane of the type `run_never`
    When `lay.py print` runs on it
    Then it exits 1 naming `run_never`, with no ID"""
    odd = dict(
        PROPOSAL,
        lanes=[
            *PROPOSAL["lanes"],
            {"role": "writer", "step": 1, "type": "run_never", "takes": ["ls"]},
        ],
    )
    put(cwd, "proposal.json", json.dumps(odd))
    code, out, err = main(["print", "changelog", "proposal.json"], env(cwd), cwd)
    assert code == 1 and "run_never" in out + err and "ID:" not in out


@pytest.mark.supports("test_lay_print_refuses_a_proposal_not_in_the_form_of_the_schema")
def test_print_of_a_file_that_isnt_json_exits_1_naming_it(cwd: str):
    """Given proposal.json holding `{`
    When `lay.py print` runs on it
    Then it exits 1 naming proposal.json"""
    put(cwd, "proposal.json", "{")
    code, out, err = main(["print", "changelog", "proposal.json"], env(cwd), cwd)
    assert code == 1 and "proposal.json" in out + err


@pytest.mark.supports("test_a_persons_yes_lays_the_proposal_and_validation_passes")
def test_write_of_the_id_print_showed_exits_0_and_lays_it(cwd: str):
    """Given `lay.py print` showed the walkthrough's Proposal
    When `lay.py write changelog <ID>` runs
    Then it exits 0, and changelog holds hooks/lanes.json"""
    _, out, _ = main(["print", "changelog", "proposal.json"], env(cwd), cwd)
    found = re.search(r"^ID: (\S+)$", out, re.MULTILINE)
    assert found
    code, _, _ = main(["write", "changelog", found[1]], env(cwd), cwd)
    assert code == 0 and os.path.isfile(os.path.join(cwd, "changelog", "hooks", "lanes.json"))


@pytest.mark.supports("test_lay_write_of_an_id_that_no_proposal_has_is_refused")
def test_write_of_an_id_no_proposal_has_exits_1_naming_it(cwd: str):
    """Given no Proposal kept
    When `lay.py write changelog 00000000` runs
    Then it exits 1 naming `00000000`"""
    code, out, err = main(["write", "changelog", "00000000"], env(cwd), cwd)
    assert code == 1 and "00000000" in out + err


@pytest.mark.supports(
    "test_lay_write_after_the_steps_changed_since_the_proposal_was_shown_is_refused"
)
def test_write_after_the_steps_changed_exits_1_saying_so(cwd: str):
    """Given `lay.py print` showed the walkthrough's Proposal, and writer's step 3 changed since
    When `lay.py write` runs on its ID
    Then it exits 1 saying the steps changed, and nothing is laid"""
    _, out, _ = main(["print", "changelog", "proposal.json"], env(cwd), cwd)
    found = re.search(r"^ID: (\S+)$", out, re.MULTILINE)
    assert found
    writer = os.path.join(cwd, "changelog", "agents", "writer.md")
    put(cwd, "changelog/agents/writer.md", read(writer).replace("new entries", "entries"))
    code, out, err = main(["write", "changelog", found[1]], env(cwd), cwd)
    assert code == 1 and "changed" in out + err
    assert not os.path.exists(os.path.join(cwd, "changelog", "hooks"))


@pytest.mark.supports("test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id")
def test_other_arguments_exit_2_with_the_usage(cwd: str):
    """Given Lane
    When `lay.py print changelog` runs, with no Proposal named
    Then it exits 2 with the usage"""
    assert main(["print", "changelog"], env(cwd), cwd) == (2, "", USAGE + "\n")

"""The integration cases of S1, a proposal: the person types `/lane:up changelog`, up asks lay.py
for the types, reads the Steps, writes a Proposal, and shows what `lay.py print` showed, or mends
the Proposal, or tells the person what to fix in their plugin. The test plays the person and up."""

from __future__ import annotations

import json

import pytest
from claude_code import Conversation
from lane_example import (
    LAY,
    PROPOSAL,
    TYPES,
    Repo,
    id_of,
    lane,
    propose,
    put,
    read,
    route,
    shown,
    start,
)

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.mark.supports("S1", "up", "lay.py", "Proposal", "Role", "Step", "Lane", "Route")
def test_lay_print_shows_each_step_as_it_will_read_with_the_routes_and_an_id(
    up: Conversation, repo: Repo
):
    """Given `changelog` as the walkthrough builds it, and the person typed `/lane:up changelog`
    When up runs `lay.py print` on the walkthrough's Proposal
    Then it prints the routes, each step as it'll read, the lanes, the commands, and an ID, as the
    walkthrough shows, and exits 0"""
    up.type("/lane:up changelog")
    printed = propose(up, repo, PROPOSAL)
    assert (printed.exit_code, printed.output) == (0, shown(id_of(printed.output)))


@pytest.mark.supports("S1", "Lane type", "lane types")
def test_lay_types_gives_each_type_with_what_it_takes_the_steps_it_suits_and_its_sentence(
    up: Conversation,
):
    """Given the person typed `/lane:up changelog`
    When up runs `lay.py types`
    Then it prints each lane type, run_only, write_only, read_never, names_printed, ends_checked,
    and gives_result, each with what it takes, the steps it suits, and its sentence"""
    up.type("/lane:up changelog")
    printed = up.bash(f"python3 {LAY} types")
    assert printed.exit_code == 0
    assert [name for name in TYPES if name not in printed.output] == []
    assert "Run only `git log --oneline`." in printed.output


@pytest.mark.supports("S1", "up", "lay.py")
def test_lay_print_refuses_a_proposal_that_leaves_out_an_adapter_and_shows_the_mended_one(
    up: Conversation, repo: Repo
):
    """Given `changelog` with a program `text` in hooks/adapters/
    When up runs `lay.py print` on a Proposal that names no adapter, and then on one that names it
    Then the first exits 1 naming hooks/adapters/text, and the second exits 0 with an ID"""
    put(repo.plugin, "hooks/adapters/text", '#!/bin/sh\necho \'{"text": "t"}\'\n')
    up.type("/lane:up changelog")
    refused = propose(up, repo, PROPOSAL)
    mended = propose(up, repo, {**PROPOSAL, "text_adapter": "text"})
    assert refused.exit_code == 1 and "hooks/adapters/text" in refused.output
    assert mended.exit_code == 0 and id_of(mended.output)


@pytest.mark.supports("S1", "lay.py", "Role")
def test_lay_print_refuses_a_subagent_whose_file_doesnt_set_background_true(
    up: Conversation, repo: Repo
):
    """Given `changelog` whose agents/reviewer.md doesn't set `background: true`
    When up runs `lay.py print` on the walkthrough's Proposal
    Then it exits 1 naming agents/reviewer.md and `background: true`, with no ID"""
    path = f"{repo.plugin}/agents/reviewer.md"
    text = read(path).replace("background: true\n", "")
    put(repo.plugin, "agents/reviewer.md", text)
    up.type("/lane:up changelog")
    refused = propose(up, repo, PROPOSAL)
    assert refused.exit_code == 1
    assert "agents/reviewer.md" in refused.output and "background: true" in refused.output
    assert not id_of(refused.output)


@pytest.mark.supports("S1", "lay.py", "Route")
def test_lay_print_refuses_a_command_that_a_route_waits_for_and_the_model_may_call(
    up: Conversation, repo: Repo
):
    """Given `changelog` with a command `approve` whose SKILL.md doesn't set
    `disable-model-invocation: true`
    When up runs `lay.py print` on a Proposal whose Route waits for `/changelog:approve`
    Then it exits 1 naming skills/approve/SKILL.md and `disable-model-invocation: true`"""
    put(repo.plugin, "skills/approve/SKILL.md", "---\nname: approve\n---\n\n## Steps\n\n1. Go.\n")
    waits = {**PROPOSAL, "routes": [*PROPOSAL["routes"][:3]]}
    waits["routes"].append(route("reviewer good", start("writer", "/changelog:approve")))
    up.type("/lane:up changelog")
    refused = propose(up, repo, waits)
    assert refused.exit_code == 1
    assert "skills/approve/SKILL.md" in refused.output
    assert "disable-model-invocation: true" in refused.output


@pytest.mark.supports("S1", "lay.py", "Step")
def test_lay_print_refuses_two_roles_that_take_their_steps_from_one_file(
    up: Conversation, repo: Repo
):
    """Given `changelog` whose writer and reviewer each name `${CLAUDE_PLUGIN_ROOT}/domain/part.md`
    for their Steps
    When up runs `lay.py print` on a Proposal of both
    Then it exits 1 naming domain/part.md and both roles"""
    put(repo.plugin, "domain/part.md", "## Steps\n\n1. Read `CHANGELOG.md`.\n2. Give `good`.\n")
    for role in ("writer", "reviewer"):
        body = (
            "---\nname: {0}\nbackground: true\n---\n\n"
            "Read ${{CLAUDE_PLUGIN_ROOT}}/domain/part.md.\n"
        )
        put(repo.plugin, f"agents/{role}.md", body.format(role))
    up.type("/lane:up changelog")
    refused = propose(up, repo, PROPOSAL)
    assert refused.exit_code == 1
    assert "domain/part.md" in refused.output
    assert "writer" in refused.output and "reviewer" in refused.output


@pytest.mark.supports("S1", "lay.py", "Route", "Result")
def test_lay_print_refuses_routes_that_reach_neither_each_role_nor_each_result(
    up: Conversation, repo: Repo
):
    """Given `changelog` as the walkthrough builds it
    When up runs `lay.py print` on a Proposal with no Route after `reviewer more`
    Then it exits 1 naming the result `more` of reviewer that no Route goes after"""
    short = {**PROPOSAL, "routes": [r for r in PROPOSAL["routes"] if r["after"] != "reviewer more"]}
    up.type("/lane:up changelog")
    refused = propose(up, repo, short)
    assert refused.exit_code == 1 and "reviewer" in refused.output and "more" in refused.output


@pytest.mark.supports("S1", "lay.py", "Lane type")
def test_lay_print_refuses_a_lane_of_a_type_there_isnt(up: Conversation, repo: Repo):
    """Given `changelog` as the walkthrough builds it
    When up runs `lay.py print` on a Proposal whose Lane names the type `run_never`
    Then it exits 1 naming `run_never` and each type there is"""
    odd = {**PROPOSAL, "lanes": [*PROPOSAL["lanes"], lane("writer", 1, "run_never", "ls")]}
    up.type("/lane:up changelog")
    refused = propose(up, repo, odd)
    assert refused.exit_code == 1
    assert "run_never" in refused.output and "run_only" in refused.output


@pytest.mark.supports("S1", "lay.py", "Proposal")
def test_lay_print_refuses_a_proposal_not_in_the_form_of_the_schema(up: Conversation, repo: Repo):
    """Given `changelog` as the walkthrough builds it
    When up runs `lay.py print` on a Proposal whose Lane has no `type`
    Then it exits 1 naming the field `type` of the first Lane"""
    odd = json.loads(json.dumps(PROPOSAL))
    del odd["lanes"][0]["type"]
    up.type("/lane:up changelog")
    refused = propose(up, repo, odd)
    assert refused.exit_code == 1 and "type" in refused.output


@pytest.mark.supports("S1", "lay.py", "Step")
def test_lay_print_notes_a_step_that_names_a_command_its_subagent_may_not_run(
    up: Conversation, repo: Repo
):
    """Given `changelog` whose writer's step 1 names `cat CHANGELOG.md` in backticks
    When up runs `lay.py print` on the walkthrough's Proposal, whose run_only Lane takes only
    `git log --oneline`
    Then it prints a note beside step 1 of writer naming `cat CHANGELOG.md`"""
    path = f"{repo.plugin}/agents/writer.md"
    text = read(path)
    put(
        repo.plugin,
        "agents/writer.md",
        text.replace("Read `CHANGELOG.md`", "Run `cat CHANGELOG.md`"),
    )
    up.type("/lane:up changelog")
    printed = propose(up, repo, PROPOSAL)
    assert printed.exit_code == 0
    noted = [each for each in printed.output.splitlines() if "cat CHANGELOG.md" in each]
    assert any("step 1" in each for each in noted), printed.output


@pytest.mark.supports("S1", "lay.py", "Lane")
def test_lay_print_refuses_an_ends_checked_lane_of_the_skill_naming_a_value_no_start_fills(
    up: Conversation, repo: Repo
):
    """Given `changelog` as the walkthrough builds it
    When up runs `lay.py print` on a Proposal whose skill's ends_checked Lane runs
    `python3 check.py {deliverable}`
    Then it exits 1 naming `{deliverable}`, as no Start gives the skill a run value"""
    lanes = [*PROPOSAL["lanes"], lane("write", 1, "ends_checked", "python3 check.py {deliverable}")]
    up.type("/lane:up changelog")
    refused = propose(up, repo, {**PROPOSAL, "lanes": lanes})
    assert refused.exit_code == 1 and "{deliverable}" in refused.output

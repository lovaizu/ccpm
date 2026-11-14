"""The unit cases of scripts/laying.py: which files laying a Proposal writes or replaces, as one
change, through `hook_entries` and `lay`, on the walkthrough's plugin in a folder of each test's
own, with a validation the test gives."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import pytest
from domain.laid_set import Laid
from lane_example import (
    LANE,
    PROPOSAL,
    PROPOSAL_AGAIN,
    WROTE,
    put,
    put_plugin,
    read,
)
from laying import hook_entries, lay
from plugin_validate import fails, passes
from proposal import keep, parse
from steps import roles

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)

CODE = os.path.join(LANE, "hooks", "lane")
FILES = ("skills/write/SKILL.md", "agents/writer.md", "agents/reviewer.md")


@pytest.fixture
def plugin(tmp_path: Any) -> str:
    return put_plugin(os.path.join(os.path.realpath(str(tmp_path)), "changelog"))


def laid(plugin: str, proposal: dict[str, Any], validate: Any = passes) -> Any:
    """Lays the Proposal, kept on the plugin's Steps as they now read."""
    from domain.laid_set import load

    before = load(plugin)
    found = roles(plugin, before.laid if before else Laid())
    given = keep(parse(proposal, "p.json"), found, os.path.dirname(plugin))
    return lay(given, found, plugin, CODE, validate)


@pytest.mark.supports("test_the_laid_plugin_runs_on_its_own_copy_of_lanes_code")
def test_each_hook_entry_runs_the_plugins_own_copy_of_the_guard(plugin: str):
    """Given the plugin `changelog`
    When Lane's hook entries for it are asked
    Then they are of the six events of Lane's README, each running
    `${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py`"""
    entries = hook_entries(plugin)
    assert set(entries) == {
        "UserPromptExpansion",
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
        "Stop",
        "SubagentStop",
    }
    text = json.dumps(entries)
    assert text.count('"python3"') == 6
    assert set(re.findall(r'"args": \[([^]]*)\]', text)) == {
        '"${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py"'
    }


@pytest.mark.supports("test_a_persons_yes_lays_the_proposal_and_validation_passes")
def test_laying_the_walkthroughs_proposal_writes_what_the_walkthrough_says(plugin: str):
    """Given the walkthrough's `changelog` and Proposal
    When it's laid, and validation passes
    Then the lines are those the walkthrough shows, and writer's step 2 holds its sentence"""
    found = laid(plugin, PROPOSAL)
    assert found.validated and "\n".join(found.lines) + "\n" == WROTE
    assert "`git log --oneline`. Run only `git log --oneline`." in read(
        os.path.join(plugin, "agents", "writer.md")
    )


@pytest.mark.supports("test_a_persons_yes_lays_the_proposal_and_validation_passes")
def test_laying_copies_lanes_code_whole_into_hooks_lane(plugin: str):
    """Given the walkthrough's `changelog` and Proposal
    When it's laid
    Then hooks/lane/ holds each file of Lane's code, as it is"""
    laid(plugin, PROPOSAL)
    copied = os.path.join(plugin, "hooks", "lane")
    assert sorted(os.listdir(copied)) == sorted(os.listdir(CODE))
    assert read(os.path.join(copied, "hook.py")) == read(os.path.join(CODE, "hook.py"))


@pytest.mark.supports("test_a_failed_validation_puts_back_each_file_that_laying_changed")
def test_a_failed_validation_puts_back_every_file(plugin: str):
    """Given the walkthrough's `changelog` and Proposal
    When it's laid, and validation fails
    Then laying says what the validation said, each Step file reads as before, and no hooks/ is
    left"""
    before = {path: read(os.path.join(plugin, path)) for path in FILES}
    found = laid(plugin, PROPOSAL, fails)
    assert not found.validated and "version" in " ".join(found.lines)
    assert {path: read(os.path.join(plugin, path)) for path in FILES} == before
    assert not os.path.exists(os.path.join(plugin, "hooks"))


@pytest.mark.supports(
    "test_laying_again_replaces_lanes_part_laid_before_and_keeps_the_users_hook_entries"
)
def test_laying_again_keeps_the_users_own_hook_entries(plugin: str):
    """Given `changelog` laid, with a hook entry of the user's own added on SessionStart
    When the walkthrough's Proposal is laid again
    Then hooks/hooks.json holds the user's entry once, and each of Lane's once"""
    laid(plugin, PROPOSAL)
    path = os.path.join(plugin, "hooks", "hooks.json")
    hooks = json.loads(read(path))
    own = {"type": "command", "command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/own.py"]}
    hooks["hooks"]["SessionStart"] = [{"hooks": [own]}]
    put(plugin, "hooks/hooks.json", json.dumps(hooks))
    laid(plugin, PROPOSAL)
    after = json.loads(read(path))["hooks"]
    assert after["SessionStart"] == [{"hooks": [own]}]
    assert all(len(groups) == 1 for event, groups in after.items() if event != "SessionStart")


@pytest.mark.supports("test_laying_again_leaves_no_rule_of_a_step_that_no_longer_holds_it")
def test_laying_again_takes_out_each_sentence_laid_before(plugin: str):
    """Given `changelog` laid with the walkthrough's Proposal
    When its second Proposal is laid on the steps the walkthrough mends
    Then writer's step 2 holds the new sentence, and not the one laid before"""
    laid(plugin, PROPOSAL)
    writer = os.path.join(plugin, "agents", "writer.md")
    text = read(writer).replace(
        "2. Read the commits since then with `git log --oneline`. Run only `git log --oneline`.",
        "2. Read the commits since then with `git log --oneline`, and then read each one with"
        " `git show {commit}`.",
    )
    put(plugin, "agents/writer.md", text)
    reviewer = os.path.join(plugin, "agents", "reviewer.md")
    put(
        plugin,
        "agents/reviewer.md",
        read(reviewer).replace(
            "against the commits they name",
            "against the commits since its last version: list them with `git log --oneline`, and"
            " read each one with `git show {commit}`",
        ),
    )
    laid(plugin, PROPOSAL_AGAIN)
    after = read(writer)
    assert "Run only `git log --oneline` or `git show {commit}`." in after
    assert "Run only `git log --oneline`.\n" not in after


@pytest.mark.supports("test_up_after_an_update_of_lane_lays_the_newest_code_of_lane")
def test_laying_again_removes_a_module_that_lanes_code_has_no_more(plugin: str):
    """Given `changelog` laid, with a module `stale.py` in its hooks/lane/
    When the walkthrough's Proposal is laid again
    Then hooks/lane/ holds no stale.py"""
    laid(plugin, PROPOSAL)
    put(plugin, "hooks/lane/stale.py", "# gone\n")
    laid(plugin, PROPOSAL)
    assert not os.path.exists(os.path.join(plugin, "hooks", "lane", "stale.py"))


@pytest.mark.supports("test_a_persons_yes_lays_the_proposal_and_validation_passes")
def test_laying_leaves_every_other_file_of_the_plugin_as_it_stands(plugin: str):
    """Given `changelog` with a file README.md of its own
    When the walkthrough's Proposal is laid
    Then README.md reads as before"""
    put(plugin, "README.md", "# changelog\n")
    laid(plugin, PROPOSAL)
    assert read(os.path.join(plugin, "README.md")) == "# changelog\n"

"""The unit cases of hooks/lane/plugin.py's plugin_root: one for each class of a conversation's
transcript, as Claude Code writes the skill's base directory into it once the skill's call ends."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from lane_events import base_directory
from plugin import plugin_root
from repo_files import write_files


def transcript_in(tmp: Any) -> str:
    """The path of a transcript in the folder, holding a line of the person's prompt."""
    path = os.path.join(str(tmp), "transcripts", "session-1.jsonl")
    os.makedirs(os.path.dirname(path))
    prompt = {"type": "user", "message": {"role": "user", "content": "/log:up 1.2.0"}}
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(prompt) + "\n")
    return path


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_the_skills_base_directory_gives_its_plugins_folder(tmp_path: Any):
    """Given a transcript holding the base directory of log:up in /plugins/log
    When Lane looks for the folder of the plugin of log:up
    Then it's /plugins/log"""
    transcript = transcript_in(tmp_path)
    base_directory(transcript, "/plugins/log", "up")
    assert plugin_root(transcript, "log:up") == "/plugins/log"


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_an_installed_plugins_folder_is_found_by_the_name_its_manifest_gives(tmp_path: Any):
    """Given a transcript holding the base directory of log:up in an installed plugin's folder,
    cache/ccpm/log/0.1.0/, whose .claude-plugin/plugin.json names log
    When Lane looks for the folder of the plugin of log:up
    Then it's that version's folder"""
    installed = os.path.join(str(tmp_path), "cache", "ccpm", "log", "0.1.0")
    write_files(installed, {".claude-plugin/plugin.json": json.dumps({"name": "log"})})
    transcript = transcript_in(tmp_path)
    base_directory(transcript, installed, "up")
    assert plugin_root(transcript, "log:up") == installed


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_transcript_with_no_base_directory_yet_gives_no_folder(tmp_path: Any):
    """Given a transcript holding only the person's prompt, as at the skill's call
    When Lane looks for the folder of the plugin of log:up
    Then there's none yet"""
    assert plugin_root(transcript_in(tmp_path), "log:up") is None


@pytest.mark.supports("test_each_plugins_run_is_held_to_the_rules_in_its_own_folder")
@pytest.mark.parametrize("skill", ["memo:up", "log:upgrade", "log:u"])
def test_a_base_directory_of_another_skill_gives_no_folder(tmp_path: Any, skill: str):
    """Given a transcript holding the base directory of log:up alone
    When Lane looks for the folder of the plugin of another skill, one whose name begins the same
    among them
    Then there's none"""
    transcript = transcript_in(tmp_path)
    base_directory(transcript, "/plugins/log", "up")
    assert plugin_root(transcript, skill) is None


@pytest.mark.supports("test_the_plugins_command_typed_again_once_its_run_ended_adds_a_new_run")
def test_the_latest_base_directory_of_the_skill_gives_the_folder(tmp_path: Any):
    """Given a transcript holding the base directory of log:up in /old/log, then in /plugins/log
    When Lane looks for the folder of the plugin of log:up
    Then it's /plugins/log, the latest"""
    transcript = transcript_in(tmp_path)
    base_directory(transcript, "/old/log", "up")
    base_directory(transcript, "/plugins/log", "up")
    assert plugin_root(transcript, "log:up") == "/plugins/log"


@pytest.mark.supports(
    "test_the_starts_due_come_at_the_main_conversations_next_event_after_the_skills_call"
)
def test_a_transcript_that_cant_be_read_is_refused(tmp_path: Any):
    """Given no transcript at the path
    When Lane looks for the folder of the plugin of log:up
    Then it refuses with OSError"""
    with pytest.raises(OSError):
        plugin_root(os.path.join(str(tmp_path), "none.jsonl"), "log:up")

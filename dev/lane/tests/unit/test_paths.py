"""The unit cases of domain/lanes/paths.py: which file of a repository a path names, read from the
root and from the top of the git worktree that holds a call's path, through `names_file` and
`under`, on a git repository that each test sets up."""

from __future__ import annotations

import os
import subprocess
from typing import Any

import pytest
from domain.lanes import Where
from domain.lanes.paths import names_file, under

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.fixture
def root(tmp_path: Any) -> str:
    """A git repository with a worktree at .claude/worktrees/w, each with CHANGELOG.md."""
    top = os.path.realpath(str(tmp_path))
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "gc.auto=0"]
    subprocess.run([*git, "init", "-q", "-b", "main"], cwd=top, check=True)
    with open(os.path.join(top, "CHANGELOG.md"), "w", encoding="utf-8") as f:
        f.write("# Changelog\n")
    subprocess.run([*git, "add", "-A"], cwd=top, check=True)
    subprocess.run([*git, "commit", "-q", "-m", "c"], cwd=top, check=True)
    where = os.path.join(top, ".claude", "worktrees", "w")
    subprocess.run([*git, "worktree", "add", "-q", "-b", "w", where], cwd=top, check=True)
    return top


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
def test_a_path_from_the_folder_the_conversation_works_in_names_the_file(root: str):
    """Given the Lane's path `CHANGELOG.md`
    When a call names `CHANGELOG.md` from the root
    Then it names the Lane's file"""
    assert names_file("CHANGELOG.md", "CHANGELOG.md", {}, Where(root, root))


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
def test_an_absolute_path_in_the_repository_names_the_file(root: str):
    """Given the Lane's path `CHANGELOG.md`
    When a call names `<root>/CHANGELOG.md`
    Then it names the Lane's file"""
    assert names_file("CHANGELOG.md", os.path.join(root, "CHANGELOG.md"), {}, Where(root, root))


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
def test_a_path_in_a_worktree_names_the_file_read_from_the_worktrees_top(root: str):
    """Given the Lane's path `CHANGELOG.md`, and a conversation at the root
    When a call names `.claude/worktrees/w/CHANGELOG.md`
    Then it names the Lane's file, read from the top of the worktree"""
    path = os.path.join(".claude", "worktrees", "w", "CHANGELOG.md")
    assert names_file("CHANGELOG.md", path, {}, Where(root, root))


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
def test_another_file_names_not_the_lanes_file(root: str):
    """Given the Lane's path `CHANGELOG.md`
    When a call names `NOTES.md`
    Then it doesn't name the Lane's file"""
    assert not names_file("CHANGELOG.md", "NOTES.md", {}, Where(root, root))


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
def test_a_path_that_leaves_the_repository_by_dot_dot_names_no_file_of_the_lane(root: str):
    """Given the Lane's path `CHANGELOG.md`
    When a call names `../CHANGELOG.md`
    Then it doesn't name the Lane's file"""
    assert not names_file("CHANGELOG.md", "../CHANGELOG.md", {}, Where(root, root))


@pytest.mark.supports("test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped")
def test_a_link_that_leads_out_of_the_repository_names_no_file_of_the_lane(
    root: str, tmp_path: Any
):
    """Given the Lane's path `CHANGELOG.md`, and `out` a link to a folder outside the repository
    When a call names `out/CHANGELOG.md`
    Then it doesn't name the Lane's file"""
    outside = os.path.join(os.path.dirname(root), "outside")
    os.makedirs(outside, exist_ok=True)
    os.symlink(outside, os.path.join(root, "out"))
    assert not names_file("CHANGELOG.md", "out/CHANGELOG.md", {}, Where(root, root))


@pytest.mark.supports("test_a_run_value_holds_each_subagent_to_the_value_of_its_own_start")
def test_a_path_with_a_name_in_braces_names_the_file_of_its_value(root: str):
    """Given the Lane's path `notes/{part}.md`, and the run value `part` `a`
    When a call names `notes/a.md`, and `notes/b.md`
    Then the first names the Lane's file and the second doesn't"""
    assert names_file("notes/{part}.md", "notes/a.md", {"part": "a"}, Where(root, root))
    assert not names_file("notes/{part}.md", "notes/b.md", {"part": "a"}, Where(root, root))


@pytest.mark.supports(
    "test_a_read_of_a_path_that_read_never_keeps_unread_is_stopped_and_its_bang_part_passes"
)
def test_a_file_inside_a_folder_lies_under_it(root: str):
    """Given the Lane's path `notes/`
    When a call names `notes/secret.md`
    Then it lies under the Lane's path"""
    assert under("notes/", "notes/secret.md", {}, Where(root, root))


@pytest.mark.supports(
    "test_a_read_of_a_path_that_read_never_keeps_unread_is_stopped_and_its_bang_part_passes"
)
def test_the_folder_itself_lies_under_it(root: str):
    """Given the Lane's path `notes/`
    When a call names `notes`
    Then it lies under the Lane's path"""
    assert under("notes/", "notes", {}, Where(root, root))


@pytest.mark.supports(
    "test_a_read_of_a_path_that_read_never_keeps_unread_is_stopped_and_its_bang_part_passes"
)
def test_a_sibling_whose_name_starts_alike_lies_not_under_it(root: str):
    """Given the Lane's path `notes/`
    When a call names `notes2/secret.md`
    Then it doesn't lie under the Lane's path"""
    assert not under("notes/", "notes2/secret.md", {}, Where(root, root))

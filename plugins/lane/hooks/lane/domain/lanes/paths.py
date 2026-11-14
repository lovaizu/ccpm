"""Decides which file of a repository a path names: a Lane's path reads from the root of the
repository and from the top of the git worktree that holds the path that a call names, so that a
role that works in a worktree of its own is held there, as Lane's architecture places each path
under Deployment."""

from __future__ import annotations

from collections.abc import Mapping

from domain.lanes import Where


def names_file(lane_path: str, call_path: str, values: Mapping[str, str], where: Where) -> bool:
    """Whether the path that a call names, absolute or from the folder the conversation works in,
    is the file that the Lane's path names, read from the root of the repository or from the top
    of the git worktree that holds the call's path, each name in braces as pattern.matches reads
    it. A path that leaves the repository through `..` or a link names no file of the Lane."""
    raise NotImplementedError("paths.names_file")


def under(lane_path: str, call_path: str, values: Mapping[str, str], where: Where) -> bool:
    """Whether the call's path is the Lane's path or lies inside it, as a folder that the Lane
    names, read as names_file reads it."""
    raise NotImplementedError("paths.under")

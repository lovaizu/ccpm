"""How the unit cases of repository/ make a run as rn leaves it in the user's repository, by git
alone and in the form that the architecture's Directory structure names: the repository with its
remote, the run's worktree on its branch from the default branch, and its design tree committed
there, so that each case starts from a run that no body of rn made."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

import rn_files
from repo_files import git, write_files
from repository.place import RunPlace

NAME = "20261120-invoices"


def made_run(
    tmp: str,
    name: str = NAME,
    design_tree: Mapping[str, Any] | None = None,
    origin: bool = True,
) -> RunPlace:
    """A repository of invoicer's files in the folder, with a bare remote `origin` where `origin`
    says so, and the run of the name: its worktree on its branch rn-<name> from main, and its
    design tree, the walkthrough's unless given, committed there; gives the run."""
    repo = rn_files.repository(os.path.join(tmp, "invoicer"))
    if origin:
        rn_files.with_origin(repo, os.path.join(tmp, "origin.git"))
    worktree = rn_files.worktree_of(repo, name)
    git(repo, "worktree", "add", "-q", "-b", f"rn-{name}", worktree, "main")
    rn_files.run_folder(repo, name, design_tree or rn_files.walkthrough_tree(name))
    git(worktree, "add", "-A")
    git(worktree, "commit", "-q", "-m", "The run's design tree.")
    return RunPlace(repo, name)


def changed(run: RunPlace, files: Mapping[str, str]) -> None:
    """Writes each file in the run's worktree, by its path from the worktree's top."""
    write_files(rn_files.worktree_of(run.repository, run.name), files)


def head(folder: str, ref: str = "HEAD") -> str:
    """The commit that the ref names in the repository of the folder."""
    return git(folder, "rev-parse", ref).strip()


def subject(folder: str, ref: str = "HEAD") -> str:
    """The message of the ref's commit, whole."""
    return git(folder, "log", "-1", "--format=%B", ref).strip()


def committed_files(folder: str, ref: str = "HEAD") -> list[str]:
    """Each file that the ref's commit changed."""
    return git(folder, "show", "--name-only", "--format=", ref).split()


def hook(repo: str, script: str) -> None:
    """Sets the repository's pre-commit hook, which git runs before each commit of each of its
    worktrees, to the shell script."""
    path = os.path.join(repo, ".git", "hooks", "pre-commit")
    with open(path, "w", encoding="utf-8") as f:
        f.write("#!/bin/sh\n" + script)
    os.chmod(path, 0o755)

"""How the unit cases of rn's prompts run each role: each case runs its role alone on Opus by
`claude -p`, in a throwaway copy of invoicer that the case sets up with its inputs given as files,
three times, each run a test of its own, as rn's Test strategy sets the benchmark of a part that
holds a prompt. A case's Then decides by code each point of the result that the run's files show.

The orchestrator runs as the main conversation with rn and Lane loaded, from the command the user
types. The generator and the evaluator each run as the session's agent, `--agent`, with rn alone
loaded, given the path of its Cut as the prompt, as the orchestrator starts it."""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import opus
import rn_files
from repo_files import environment, git

LANE = os.path.join(rn_files.TOP, "plugins", "lane")
# The runs of each case, as rn's Test strategy sets them: each case's results over 3 runs.
RUNS = [1, 2, 3]
# How long one run of a role may take, in seconds.
TIMEOUT = 1800
# Why each case fails now: the prompts' Goal and Steps are empty, and the scripts they run raise
# NotImplementedError.
NOT_BUILT = "rn's prompts hold no Goal or Steps yet, and the scripts they run have empty bodies"


@dataclass(frozen=True)
class Room:
    """A throwaway copy of invoicer with copies of rn and Lane, and the environment of the run."""

    repo: str
    rn: str
    lane: str
    env: dict[str, str]

    def at(self, path: str) -> str:
        """The path in the repository."""
        return os.path.join(self.repo, path)

    def worktree(self, name: str) -> str:
        """The run's worktree."""
        return rn_files.worktree_of(self.repo, name)

    def folder(self, name: str) -> str:
        """The run's folder."""
        return rn_files.folder_of(self.repo, name)


def room_in(tmp: str) -> Room:
    """A copy of invoicer committed on main in the folder, with copies of rn and Lane beside it,
    and a configuration folder of its own."""
    rn = os.path.join(tmp, "plugins", "rn")
    lane = os.path.join(tmp, "plugins", "lane")
    shutil.copytree(rn_files.RN, rn, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(LANE, lane, ignore=shutil.ignore_patterns("__pycache__"))
    repo = rn_files.repository(os.path.join(tmp, "invoicer"))
    env = environment(tmp)
    env["CLAUDE_CONFIG_DIR"] = os.path.join(tmp, "config")
    return Room(repo, rn, lane, env)


def typed(room: Room, prompt: str, more: bool = False) -> str:
    """What Claude Code printed once the user typed the prompt in the repository, with rn and Lane
    loaded, in the conversation before where `more` says so."""
    flags = ["--plugin-dir", room.rn, "--plugin-dir", room.lane]
    if more:
        flags.append("--continue")
    return opus.prompted(prompt, room.repo, room.env, flags, TIMEOUT)


def as_role(room: Room, role: str, cut_path: str) -> str:
    """What Claude Code printed once the role ran alone as the session's agent, given the path of
    its Cut from the repository's top as its prompt, with rn loaded."""
    flags = ["--plugin-dir", room.rn, "--agent", f"rn:{role}"]
    return opus.prompted(cut_path, room.repo, room.env, flags, TIMEOUT)


def run_of(room: Room, name: str, node: Mapping[str, Any]) -> str:
    """Makes the run's worktree on its branch from main, with its design tree committed, holding
    the plan done and the node, and gives the run's folder."""
    design_tree = rn_files.tree(
        [rn_files.done_node(rn_files.GOAL, rn_files.plan_path(name), "design-tree"), node]
    )
    worktree = room.worktree(name)
    git(room.repo, "worktree", "add", "-q", "-b", f"rn-{name}", worktree, "main")
    folder = rn_files.run_folder(room.repo, name, design_tree)
    git(worktree, "add", "-A")
    git(worktree, "commit", "-q", "-m", "The plan.")
    return folder


def generator_cut(
    room: Room, name: str, node: Mapping[str, Any], findings: Any = None, last_good: Any = None
) -> str:
    """Writes the generator's Cut of Round content-1 of the deliverable, in the form of
    generator-cut.schema.json, and gives its path from the repository's top."""
    folder = rn_files.round_of(room.folder(name), node["path"], "content", 1)
    kind = node["kind"]
    given = {
        "goal": rn_files.GOAL,
        "deliverable": dict(node),
        "worktree": os.path.relpath(room.worktree(name), room.repo),
        "inputs": [
            os.path.relpath(os.path.join(room.worktree(name), each), room.repo)
            for each in node["inputs"]
        ],
        "best_practice": os.path.relpath(
            os.path.join(room.rn, "domain", "best-practices", kind), room.repo
        ),
        "stage": "content",
        "number": 1,
        "round": os.path.relpath(folder, room.repo),
        "findings": findings,
        "last_good": last_good,
    }
    path = os.path.join(folder, "generator-cut.json")
    rn_files.write_json(path, given)
    return os.path.relpath(path, room.repo)


def evaluator_cut(room: Room, name: str, node: Mapping[str, Any], trial: str) -> str:
    """Writes the evaluator's Cut of Round content-1 of the deliverable, in the form of
    evaluator-cut.schema.json, with the people's folder given, and gives its path from the
    repository's top."""
    folder = rn_files.round_of(room.folder(name), node["path"], "content", 1)
    given = {
        "goal": rn_files.GOAL,
        "deliverable": {"name": node["name"], "path": node["path"]},
        "judges_by": rn_files.judged_by(node["kind"]),
        "worktree": os.path.relpath(room.worktree(name), room.repo),
        "round": os.path.relpath(folder, room.repo),
        "trial": trial,
    }
    path = os.path.join(folder, "evaluator-cut.json")
    rn_files.write_json(path, given)
    return os.path.relpath(path, room.repo)


def result_of(room: Room, cut_path: str, role: str) -> Any:
    """The role's result beside its Cut, read from its JSON, or None where it wrote none."""
    path = os.path.join(room.repo, os.path.dirname(cut_path), f"{role}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

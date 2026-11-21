"""How the unit cases of rn's prompts run each role: each case runs its role alone on Opus by
`claude -p`, in a throwaway copy of invoicer that the case sets up with its inputs given as files,
three times, each run a test of its own, as rn's Test strategy sets the benchmark of a part that
holds a prompt. A case's Then decides by code each point of the result that the run's files show.

The orchestrator runs as the main conversation with rn and Lane loaded, from the command the user
types. The generator and the evaluator each run as the session's agent, `--agent`, with rn and
Lane loaded, as rn's manifest depends on Lane, given the path of its Cut as the prompt, as the
orchestrator starts it."""

from __future__ import annotations

import glob
import json
import os
import shutil
from collections.abc import Iterator, Mapping
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
    """A copy of invoicer committed on main in the folder, with a remote `origin` holding `main`,
    as `repository.py new` starts a run from origin's default branch, copies of rn and Lane beside
    it, and a configuration folder of its own."""
    rn = os.path.join(tmp, "plugins", "rn")
    lane = os.path.join(tmp, "plugins", "lane")
    shutil.copytree(rn_files.RN, rn, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(LANE, lane, ignore=shutil.ignore_patterns("__pycache__"))
    repo = rn_files.repository(os.path.join(tmp, "invoicer"))
    rn_files.with_origin(repo, os.path.join(tmp, "origin.git"))
    env = environment(tmp)
    # The case's time zone, so that rn takes the day that the case takes.
    env.update({name: os.environ[name] for name in ("TZ",) if name in os.environ})
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
    its Cut from the repository's top as its prompt, with rn and Lane loaded."""
    flags = ["--plugin-dir", room.rn, "--plugin-dir", room.lane, "--agent", f"rn:{role}"]
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
        "language": rn_files.DELIVERABLES_LANGUAGE,
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


def trial_of(room: Room, name: str, round_folder: str) -> str:
    """The folder of the people's starting state that `repository.py trial` makes for the Round of
    the run, as repository.trial.folder names it, in the room's own system temporary folder, which
    the run's commands take."""
    within = os.path.relpath(round_folder, os.path.join(room.folder(name), "rounds"))
    return os.path.join(room.env["TMPDIR"], f"rn-trial-{name}-{within.replace(os.sep, '-')}") + "/"


def evaluator_cut(room: Room, name: str, node: Mapping[str, Any]) -> str:
    """Writes the evaluator's Cut of Round content-1 of the deliverable, in the form of
    evaluator-cut.schema.json, with the people's folder that `repository.py trial` makes, and
    gives its path from the repository's top."""
    folder = rn_files.round_of(room.folder(name), node["path"], "content", 1)
    trial = trial_of(room, name, folder)
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


def _entries(room: Room, agents: bool) -> Iterator[Any]:
    """Each content block of each assistant message that the room's runs recorded, in the order of
    each record, from Claude Code's records in the room's configuration folder: the main
    conversation's alone, or each subagent's too where `agents` says so."""
    pattern = os.path.join(room.env["CLAUDE_CONFIG_DIR"], "projects", "**", "*.jsonl")
    for path in sorted(glob.glob(pattern, recursive=True)):
        if not agents and f"{os.sep}subagents{os.sep}" in path:
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if entry.get("type") != "assistant":
                    continue
                content = entry.get("message", {}).get("content")
                yield from content if isinstance(content, list) else ()


def commands_of(room: Room, agents: bool = False) -> list[str]:
    """Each command that the room's runs gave Bash, as their records hold it."""
    return [
        each["input"].get("command", "")
        for each in _entries(room, agents)
        if each.get("type") == "tool_use" and each.get("name") == "Bash"
    ]


def first_turn(room: Room) -> list[Any]:
    """Each content block of the main conversation's first turn, up to the first prompt after it,
    such as Lane's word at the turn's end or a subagent's end, as `claude -p` goes on to the turns
    that these start, and prints only the last message of its last turn."""
    pattern = os.path.join(room.env["CLAUDE_CONFIG_DIR"], "projects", "*", "*.jsonl")
    taken: list[Any] = []
    answered = False
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                content = entry.get("message", {}).get("content")
                blocks = content if isinstance(content, list) else [{"type": "text"}]
                prompted = any(each.get("type") != "tool_result" for each in blocks)
                if entry.get("type") == "user" and answered and prompted:
                    return taken
                if entry.get("type") == "assistant":
                    answered = True
                    taken += blocks
    return taken


def first_turn_said(room: Room) -> str:
    """What the main conversation said in its first turn, each text joined."""
    return "\n".join(
        each.get("text", "") for each in first_turn(room) if each.get("type") == "text"
    )


def first_turn_commands(room: Room) -> list[str]:
    """Each command that the main conversation gave Bash in its first turn."""
    return [
        each["input"].get("command", "")
        for each in first_turn(room)
        if each.get("type") == "tool_use" and each.get("name") == "Bash"
    ]

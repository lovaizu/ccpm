"""What lane's trials share: lane's code and the plugins they lay lanes on copied as installing
copies them, the lanes laid on a plugin by `lay.py write`, a project made a git repository, and
Claude Code run on them, what it printed kept."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from typing import Any

import trying

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def copied(source: str, folder: str, name: str) -> str:
    """Copies the plugin at source into the folder as name, each link as the file it points to, as
    installing does; gives the copy's path."""
    place = os.path.join(folder, name)
    shutil.copytree(source, place, ignore=shutil.ignore_patterns("__pycache__"))
    return place


def laid(folder: str, source: str, name: str, lanes: dict[str, dict[int, list[Any]]]) -> str:
    """Copies lane and the plugin at source into the folder, the plugin as name, and lays the lanes
    on it, each subagent's steps by number, each lane with what it takes, by the copied lane's
    `lay.py write` from a proposal written in the folder, as the building AI lays them; gives the
    plugin's path."""
    copy = copied(os.path.join(ROOT, "lane"), folder, "lane")
    plugin = copied(source, folder, name)
    proposal = {
        "plugin": plugin,
        "subagents": [
            {
                "name": agent,
                "steps": [
                    {"step": n, "lanes": [{"lane": lane, "takes": takes} for lane, takes in on]}
                    for n, on in steps.items()
                ],
            }
            for agent, steps in lanes.items()
        ],
    }
    path = os.path.join(folder, "proposal.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(proposal, f)
    subprocess.run(["python3", os.path.join(copy, "scripts", "lay.py"), "write", path], check=True)
    return plugin


def made(place: str, history: list[tuple[str, dict[str, str]]]) -> None:
    """Makes a project at place, a git repository with the history's commits, each a message and
    the files it writes."""
    os.makedirs(place)
    subprocess.run(["git", "-C", place, "init", "-q"], check=True)
    # The machine may name no one to commit as; the project names its own.
    for key, value in (("user.name", "lane trial"), ("user.email", "trial@example.com")):
        subprocess.run(["git", "-C", place, "config", key, value], check=True)
    for message, files in history:
        for name, text in files.items():
            with open(os.path.join(place, name), "w", encoding="utf-8") as f:
                f.write(text)
        subprocess.run(["git", "-C", place, "add", "-A"], check=True)
        subprocess.run(["git", "-C", place, "commit", "-q", "-m", message], check=True)


def run(
    name: str,
    prompt: str,
    plugins: list[str],
    folder: str,
    cwd: str,
    env: dict[str, str] | None = None,
) -> None:
    """Runs Claude Code on prompt in cwd, keeping what it printed in the folder as <name>.jsonl,
    and prints its session, its minutes and the records of each agent it started."""
    start = time.time()
    end = trying.claude(
        prompt, plugins, cwd=cwd, wait=60, record=os.path.join(folder, f"{name}.jsonl"), env=env
    )
    print(end.get("result"))
    print("session:", end.get("session_id"), "cost:", end.get("total_cost_usd"))
    print("minutes:", round((time.time() - start) / 60, 1))
    for record in sorted(trying.agents(end["session_id"])):
        trying.show(record)


def shown(place: str, names: tuple[str, ...]) -> None:
    """Prints the project's state and history, and each file of the names it holds."""
    for args in (["status", "--short"], ["log", "--oneline"]):
        subprocess.run(["git", "-C", place, *args], check=False)
    for name in names:
        path = os.path.join(place, name)
        if not os.path.exists(path):
            print(f"{name}: none")
            continue
        with open(path, encoding="utf-8") as f:
            print(f"{name}:\n{f.read()}")

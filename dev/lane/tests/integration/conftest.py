"""What Lane's integration cases share: a bench for each case, Lane's code imported afresh by each
hook and script that the double runs, as a new process of Python would import the copy it runs,
and the fixture `broken`, which takes out the part that holds a rule where TRACE_BROKEN is 1, as
the plugin guide's A principle's test seen to fail says."""

from __future__ import annotations

import dataclasses
import json
import os
import sys
from collections.abc import Callable, Iterator
from typing import Any

import fresh_imports
import pytest
import walkthrough

# Lane's own modules, by name, which a case's process holds no copy of while the case runs, so that
# each hook imports the code of the plugin it runs from.
LANE_MODULES = (*fresh_imports.GUARD, "lay")


@pytest.fixture(autouse=True)
def fresh_modules() -> Iterator[None]:
    """Takes each of Lane's modules out of the process for the case, and puts back those it held
    before."""
    with fresh_imports.without(LANE_MODULES):
        yield


@pytest.fixture
def b(tmp_path: Any) -> walkthrough.Bench:
    """The bench of the walkthrough: a copy of Lane, and tally with changelog in it."""
    return walkthrough.bench(str(tmp_path))


def take_out(monkeypatch: pytest.MonkeyPatch, module: str, name: str, stand_in: Any) -> None:
    """Puts the stand-in in place of the module's function, and wherever a module of the process
    holds that function by another import."""
    __import__(module)
    original = getattr(sys.modules[module], name)
    for each in list(sys.modules.values()):
        for attr, value in list(vars(each).items()) if each else []:
            if value is original:
                monkeypatch.setattr(each, attr, stand_in)


def hooks_on_lanes_own_folder(lane: str) -> Callable[[], dict[str, Any]]:
    """Lane's hook entries made to run the hook of Lane's own folder, not the plugin's copy."""

    def hook_entries() -> dict[str, Any]:
        entry = {
            "type": "command",
            "command": "python3",
            "args": [os.path.join(lane, "hooks", "lane", "hook.py")],
            "onFailure": "block",
        }
        events = ("UserPromptSubmit", "UserPromptExpansion", "PreToolUse", "PostToolUse")
        events += ("Stop", "SubagentStop")
        return {event: [{"hooks": [entry]}] for event in events}

    return hook_entries


def only_lanes_entries(plugin: str, entries: Any) -> None:
    """hooks.json written with Lane's entries alone, the user's own lost."""
    os.makedirs(os.path.join(plugin, "hooks"), exist_ok=True)
    with open(os.path.join(plugin, "hooks", "hooks.json"), "w", encoding="utf-8") as f:
        json.dump({"hooks": dict(entries)}, f)


def lays_unshown(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """lay.py write, made to find each Proposal with the Steps as they read now, so that it lays
    what print never showed."""
    __import__("lay.write")
    proposals, steps, laid = (sys.modules[f"lay.{m}"] for m in ("proposals", "steps", "laid"))
    original = proposals.find

    def find(plugin: str, proposal_id: str) -> Any:
        kept = original(plugin, proposal_id)
        if kept is None:
            return None
        now = steps.as_held(laid.unlaid(plugin)[0], kept.proposal.routes)
        return dataclasses.replace(kept, steps=now)

    take_out(monkeypatch, "lay.proposals", "find", find)


def hooks_off_the_copy(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    lane = request.getfixturevalue("b").lane
    take_out(monkeypatch, "events", "hook_entries", hooks_on_lanes_own_folder(lane))


def stand_in(module: str, name: str, made: Callable[[], Any]) -> Callable[..., None]:
    """What takes out the module's function, in place of the stand-in that `made` makes."""

    def taken(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
        take_out(monkeypatch, module, name, made())

    return taken


# What takes out the part that holds each rule of Solution strategy, by the rule's heading.
RULES: dict[str, Callable[[pytest.MonkeyPatch, pytest.FixtureRequest], None]] = {
    "The steps are the one source": stand_in(
        "lay.laid", "strip", lambda: lambda steps, laid: (tuple(steps), ())
    ),
    "One type gives the sentence, the check, and the steps it suits": stand_in(
        "lanes", "sentence", lambda: lambda lane, last_step, routes: f"Keep to step {lane.step}."
    ),
    "Laid only as shown": lays_unshown,
    "Lane's part replaced whole": stand_in(
        "lay.hooks_file", "replace_entries", lambda: only_lanes_entries
    ),
    "A result only from the result script": stand_in(
        "place", "place", lambda: result_from_reply(sys.modules)
    ),
    "What no hook shows only from Lane's scripts": stand_in(
        "place", "place", lambda: marks_from_reply(sys.modules)
    ),
    "Only the main conversation starts the roles": stand_in(
        "place", "place", lambda: starts_as_main(sys.modules)
    ),
    "A stop gives the step back": stand_in("answers", "stopped", lambda: lambda plugin, broken: ""),
    "The run kept in a file": stand_in("run_record", "lines", lambda: lambda path: ()),
    "The guard checks only the run": stand_in("runs", "stand", lambda: runs_never_end(sys.modules)),
    "The laid plugin runs alone": hooks_off_the_copy,
}


def result_from_reply(modules: dict[str, Any]) -> Callable[..., Any]:
    """place, made to read a subagent's last message as the Result it names."""
    __import__("place")
    place = modules["place"]
    original = place.place

    def stand_in(event: Any, conversation: Any, lanes: Any, root: str) -> Any:
        placed = original(event, conversation, lanes, root)
        if isinstance(placed.what, place.EndAsked) and placed.start is not None:
            word = placed.what.last_message.strip().strip(".").split()[-1]
            return dataclasses.replace(placed, what=place.ResultPosted(placed.start.role, word))
        return placed

    return stand_in


def marks_from_reply(modules: dict[str, Any]) -> Callable[..., Any]:
    """place, made to read a subagent's end whose last message says a Step is done as the Mark of
    the Step it names, in place of the end."""
    __import__("place")
    place = modules["place"]
    original = place.place

    def stand_in(event: Any, conversation: Any, lanes: Any, root: str) -> Any:
        placed = original(event, conversation, lanes, root)
        if isinstance(placed.what, place.EndAsked) and placed.start is not None:
            said = placed.what.last_message
            if "done" in said:
                step = int(next(w for w in said.split() if w.isdigit()))
                posted = place.StepPosted(placed.start.role, step)
                return dataclasses.replace(placed, what=posted)
        return placed

    return stand_in


def starts_as_main(modules: dict[str, Any]) -> Callable[..., Any]:
    """place, made to place a subagent's start as the main conversation's."""
    __import__("place")
    place = modules["place"]
    original = place.place

    def stand_in(event: Any, conversation: Any, lanes: Any, root: str) -> Any:
        placed = original(event, conversation, lanes, root)
        if isinstance(placed.what, place.StartCall):
            return dataclasses.replace(placed, start=None, agent_id=None)
        return placed

    return stand_in


def runs_never_end(modules: dict[str, Any]) -> Callable[..., Any]:
    """runs.stand, made to keep every Run going after its Routes end."""
    __import__("runs")
    original = modules["runs"].stand

    def stand_in(session_id: str, lines: Any, routes: Any, plugin: str = "") -> Any:
        conversation = original(session_id, lines, routes, plugin)
        kept = tuple(dataclasses.replace(run, ended=False) for run in conversation.runs)
        return dataclasses.replace(conversation, runs=kept)

    return stand_in


@pytest.fixture
def broken(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Where TRACE_BROKEN is 1, takes out the part that holds each rule the case names."""
    if os.environ.get("TRACE_BROKEN") != "1":
        return
    names = [name for mark in request.node.iter_markers("supports") for name in mark.args]
    rules = [name for name in names if name in RULES]
    assert rules, "the case names no rule"
    for rule in rules:
        RULES[rule](monkeypatch, request)

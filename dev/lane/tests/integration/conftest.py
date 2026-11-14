"""The fixtures of Lane's integration cases: the test's repository with the example plugin, a
conversation of the double of Claude Code with Lane and the plugin loaded, the plugin laid, and the
fixture `broken`, which takes out the part that holds each principle where TRACE_BROKEN is 1, as
the plugin guide's A principle's test seen to fail says.

The double runs each hook script and each `python3` command in the test's own process, and keeps
each module that the test imported before, so a part taken out here is taken out of the guard,
lay.py, and result.py that the double runs."""

from __future__ import annotations

import dataclasses
import importlib
import os
from typing import Any, Callable

import pytest
from claude_code import Conversation
from lane_example import LANE, PROPOSAL, Repo, conversation, lay, make_repo


def _without_laid() -> Callable[..., Any]:
    """steps.roles reading the Steps with the text that the Laid names left in them."""
    import steps
    from domain.laid_set import Laid

    original = steps.roles
    return lambda plugin_root, laid, commands=None: original(plugin_root, Laid(), commands)


def _sentence_from_elsewhere() -> Callable[..., Any]:
    """proposal.keep giving each Lane a sentence of its own words, not its type's."""
    import proposal

    original = proposal.keep

    def keep(given: Any, found: Any, temp: str, conversation: str = "") -> Any:
        kept = original(given, found, temp, conversation)
        lanes = tuple(
            dataclasses.replace(each, sentence="Run only what the step names.")
            for each in kept.lanes
        )
        return dataclasses.replace(kept, lanes=lanes)

    return keep


def _result_from_reply() -> Callable[..., Any]:
    """guard.result_since taking a result as a reply would read, with no run of result.py."""
    from domain.run_record import Result

    return lambda run, agent: Result("reviewer", "more", agent)


def _entries_of_installed_lane() -> Callable[..., Any]:
    """laying.hook_entries running the guard of the installed Lane, not the plugin's copy."""
    hook = os.path.join(LANE, "hooks", "lane", "hook.py")
    entry = {"type": "command", "command": "python3", "args": [hook], "onFailure": "block"}
    events = ["UserPromptExpansion", "UserPromptSubmit", "PreToolUse", "PostToolUse"]
    return lambda plugin_root: {e: [{"hooks": [dict(entry)]}] for e in events}


# For each principle of Lane's architecture, the module and the name of the part that holds it, and
# what takes it out.
PARTS: dict[str, tuple[str, str, Callable[[], Callable[..., Any]]]] = {
    "The steps are the one source": ("steps", "roles", _without_laid),
    "One type gives the sentence, the check, and the steps it suits": (
        "proposal",
        "keep",
        _sentence_from_elsewhere,
    ),
    "Laid only on the caller's own act": (
        "domain.approval",
        "own_act",
        lambda: lambda run, call: True,
    ),
    "Lane's part replaced whole": ("domain.laid_set", "load", lambda: lambda plugin_root: None),
    "A result only from the result script": ("domain.guard", "result_since", _result_from_reply),
    "Only the main conversation starts the roles": (
        "domain.guard",
        "starts_from_main",
        lambda: lambda event: True,
    ),
    "A stop gives the step back": (
        "domain.said",
        "stop",
        lambda: lambda plugin, sentence, may_run, printed: f"{plugin}: stopped.",
    ),
    "The run kept in a file": (
        "domain.run_record",
        "load",
        lambda: lambda temp, plugin, session: (),
    ),
    "The guard checks only the run": (
        "domain.guard",
        "in_run",
        lambda: lambda event, laid_set, run: True,
    ),
    "The laid plugin runs alone": ("laying", "hook_entries", _entries_of_installed_lane),
}


@pytest.fixture
def broken(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> bool:
    """Where TRACE_BROKEN is 1, takes out the part that holds each principle that the case names,
    and gives True; else does nothing and gives False."""
    if os.environ.get("TRACE_BROKEN") != "1":
        return False
    for mark in request.node.iter_markers("supports"):
        for name in mark.args:
            if name in PARTS:
                module, attribute, taken_out = PARTS[name]
                monkeypatch.setattr(importlib.import_module(module), attribute, taken_out())
    return True


@pytest.fixture
def repo(tmp_path: Any) -> Repo:
    """The test's repository of `tally`, with the plugin `changelog` as the walkthrough starts."""
    return make_repo(os.path.realpath(str(tmp_path)))


@pytest.fixture
def up(repo: Repo) -> Conversation:
    """A conversation with Lane installed and `changelog` loaded, as the walkthrough starts it."""
    return conversation(repo, LANE, repo.plugin)


@pytest.fixture
def laid(repo: Repo) -> Repo:
    """The repository once its caller approved PROPOSAL and Lane laid it into `changelog`."""
    lay(repo, PROPOSAL)
    return repo


@pytest.fixture
def run(laid: Repo) -> Conversation:
    """A conversation with `changelog` laid and loaded, which loads its hooks as it starts."""
    return conversation(laid, laid.plugin)

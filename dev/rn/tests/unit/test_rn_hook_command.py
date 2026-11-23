"""The unit cases of hook/command.py, the hook that Claude Code runs before each Bash command: a
command of rn's maker that deletes, by rm, rmdir, unlink, or find's -delete, at the start or
further on in a chain or a pipeline, denied with how to use remove.py; and each call that passes,
printing nothing: a maker's command that doesn't delete, a delete by the main conversation or by
another plugin's subagent, another tool, stdin that isn't the hook's JSON, a command that can't be
read, and a fault of the hook's own."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from hook import command
from hook.command import main

ROOT = os.path.join(os.sep, "plugins", "rn")
REMOVE = os.path.join(ROOT, "scripts", "remove.py")


def given(cmd: Any, agent: Any = "rn:generator", tool: str = "Bash") -> bytes:
    """The hook's stdin for the Bash command, as Claude Code gives it in the agent's call."""
    called: dict[str, Any] = {
        "session_id": "abc123",
        "cwd": "/work/invoicer",
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {"command": cmd, "description": "Clean up"},
        "tool_use_id": "toolu_01",
    }
    if agent is not None:
        called.update({"agent_id": "a1", "agent_type": agent})
    return json.dumps(called).encode("utf-8")


def denied(answer: tuple[int, str, str]) -> str:
    """The reason of a denial: 0, the JSON that denies the call on stdout, and nothing on stderr."""
    code, printed, err = answer
    assert (code, err) == (0, "")
    output = json.loads(printed)["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse"
    assert output["permissionDecision"] == "deny"
    return output["permissionDecisionReason"]


@pytest.mark.supports("test_a_makers_delete_by_rm_is_denied_pointing_to_remove_py")
@pytest.mark.parametrize(
    "cmd",
    [
        'rm -r "$W/$p/__pycache__"',
        "rmdir build",
        "unlink notes.txt",
        "find . -name '*.pyc' -delete",
        "find . -name __pycache__ -exec rm -r {} +",
        "/bin/rm -f out.log",
        "cd invoicer && rm -rf __pycache__",
        "pytest; rm -r .pytest_cache",
        "find . -name '*.pyc' | xargs rm",
        "(cd /tmp/rn-trial && rm -r build)",
        "LC_ALL=C sudo rm -f out.log",
        "echo done\nrm -r build",
        'for p in a b; do rm -r "$p"; done',
    ],
)
def test_a_makers_delete_is_denied_with_how_to_use_remove_py(cmd: str):
    """Given rn's generator calling Bash with a command that deletes, by rm, rmdir, unlink, or
    find's -delete, at any place in it
    When the hook runs
    Then it denies the call, its reason giving remove.py's command by its absolute path, with an
    exact path for each argument"""
    reason = denied(main(given(cmd), ROOT))
    assert f"python3 {REMOVE} <exact path> [<exact path> ...]" in reason
    assert "one argument each" in reason


@pytest.mark.supports("test_a_makers_delete_by_rm_is_denied_pointing_to_remove_py")
def test_the_evaluators_delete_is_denied():
    """Given rn's evaluator calling Bash with rm
    When the hook runs
    Then it denies the call"""
    denied(main(given("rm -r /tmp/rn-trial/build", agent="rn:evaluator"), ROOT))


@pytest.mark.supports("test_a_delete_by_the_main_conversation_passes_the_hook")
@pytest.mark.parametrize(
    "cmd",
    [
        "pytest -q",
        "git rm --cached notes.txt",
        "echo rm -r build",
        "grep -n unlink invoicer/lines.py",
        "find . -name '*.pyc'",
        "python3 /plugins/rn/scripts/remove.py invoicer/__pycache__",
        "ls > rm",
    ],
)
def test_a_makers_command_that_doesnt_delete_passes(cmd: str):
    """Given rn's generator calling Bash with a command that deletes nothing, though it may name
    rm as a word
    When the hook runs
    Then it gives 0 and prints nothing, so that the call goes on"""
    assert main(given(cmd), ROOT) == (0, "", "")


@pytest.mark.supports("test_a_delete_by_the_main_conversation_passes_the_hook")
@pytest.mark.parametrize("agent", [None, "Explore", "general-purpose", "turn:worker", "rn"])
def test_a_delete_outside_rns_makers_passes(agent: Any):
    """Given a Bash call with rm by the main conversation, which names no agent, or by an agent
    that isn't one of rn's
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(given("rm -r build", agent=agent), ROOT) == (0, "", "")


@pytest.mark.supports("test_a_delete_by_the_main_conversation_passes_the_hook")
def test_another_tool_passes():
    """Given rn's generator calling a tool other than Bash, whose input holds rm
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(given("rm -r build", tool="Write"), ROOT) == (0, "", "")


@pytest.mark.supports("test_a_delete_by_the_main_conversation_passes_the_hook")
@pytest.mark.parametrize(
    "stdin",
    [
        b"",
        b"not json",
        b"\xff\xfe",
        b"[]",
        json.dumps({"agent_type": "rn:generator", "tool_name": "Bash"}).encode(),
        json.dumps(
            {"agent_type": "rn:generator", "tool_name": "Bash", "tool_input": "rm -r x"}
        ).encode(),
        json.dumps(
            {"agent_type": 7, "tool_name": "Bash", "tool_input": {"command": "rm x"}}
        ).encode(),
    ],
)
def test_stdin_that_isnt_the_hooks_json_passes(stdin: bytes):
    """Given stdin that isn't the hook's JSON, or lacks a field of it, or holds one of another type
    When the hook runs
    Then it gives 0 and prints nothing, as the hook never stops a call on its own fault"""
    assert main(stdin, ROOT) == (0, "", "")


@pytest.mark.supports("test_a_delete_by_the_main_conversation_passes_the_hook")
@pytest.mark.parametrize("cmd", ["rm -r 'build", 42])
def test_a_command_that_cant_be_read_passes(cmd: Any):
    """Given rn's generator calling Bash with a command whose quote never closes, or that isn't
    text
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(given(cmd), ROOT) == (0, "", "")


@pytest.mark.supports("test_a_delete_by_the_main_conversation_passes_the_hook")
def test_a_fault_of_the_hooks_own_passes(monkeypatch: pytest.MonkeyPatch):
    """Given a hook whose reading of the call fails on an error it doesn't expect
    When the hook runs on rn's generator's rm
    Then it gives 0 and prints nothing, as the hook never stops a call on its own fault"""

    def broken(*_: Any) -> Any:
        raise RuntimeError("broken")

    monkeypatch.setattr(command, "decided", broken)
    assert main(given("rm -r build"), ROOT) == (0, "", "")

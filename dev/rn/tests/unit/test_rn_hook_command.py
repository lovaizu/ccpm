"""The unit cases of hook/command.py, the hook that Claude Code runs before each Bash command and
each Write or Edit: a command of rn's maker that deletes, by rm, rmdir, unlink, or find's -delete,
at the start or further on in a chain or a pipeline, denied with how to use remove.py; a Write or
Edit of a run's design tree by the main conversation or by any agent but rn's pruner, its path
written with / or \\, denied pointing to a new pruner; and each call that passes, printing nothing:
a maker's command that doesn't delete, a delete by the main conversation or by another plugin's
subagent, another tool, the pruner's write of the tree, a write of a file near a run's tree, a
write whose path can't be read, stdin that isn't the hook's JSON, a command that can't be read,
and a fault of the hook's own."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from hook import command
from hook.command import main

ROOT = os.path.join(os.sep, "plugins", "rn")
REMOVE = os.path.join(ROOT, "scripts", "remove.py")


def given(cmd: Any, agent: Any = "rn:generator", tool: str = "Bash") -> bytes:
    """The hook's stdin for the Bash command, as Claude Code gives it in the agent's call."""
    tool_input = {"command": cmd, "description": "Clean up"}
    return rn_files.hook_input("/work/invoicer", tool, tool_input, agent).encode("utf-8")


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


# A write to a run's design tree.

TREE = (
    "/work/invoicer/.claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices/design-tree.json"
)
WINDOWS_TREE = (
    "C:\\work\\invoicer\\.claude\\worktrees\\rn-20261120-invoices\\.rn\\20261120-invoices"
    "\\design-tree.json"
)


def written(path: Any, agent: Any = None, tool: str = "Write") -> bytes:
    """The hook's stdin for a Write or Edit of the file, as Claude Code gives it in the agent's
    call, or in the main conversation's where the agent is None."""
    if tool == "Edit":
        tool_input = {"file_path": path, "old_string": "a", "new_string": "b", "replace_all": False}
    else:
        tool_input = {"file_path": path, "content": "{}\n"}
    return rn_files.hook_input("/work/invoicer", tool, tool_input, agent).encode("utf-8")


@pytest.mark.supports(
    "test_the_orchestrators_write_to_the_design_tree_is_denied_pointing_to_a_new_pruner"
)
@pytest.mark.parametrize("tool", ["Write", "Edit"])
def test_the_main_conversations_write_to_a_runs_tree_is_denied_pointing_to_a_new_pruner(
    tool: str,
):
    """Given the main conversation, the orchestrator, which names no agent, calling Write or Edit
    on a run's design-tree.json
    When the hook runs
    Then it denies the call, its reason naming the file and telling the writer to hand the fact
    to a new pruner"""
    reason = denied(main(written(TREE, tool=tool), ROOT))
    assert f"Leave {TREE} as it is" in reason
    assert "hand the fact you'd write to a new pruner" in reason


@pytest.mark.supports("test_a_makers_write_to_the_design_tree_is_denied_while_the_scripts_write_it")
@pytest.mark.parametrize(
    "agent",
    ["rn:generator", "rn:evaluator", "Explore", "general-purpose", "pruner", "rn:pruner2", 7],
)
def test_a_write_to_a_runs_tree_by_any_agent_but_the_pruner_is_denied(agent: Any):
    """Given rn's generator or evaluator, another plugin's or Claude Code's own agent, an agent
    named nearly as the pruner, or an agent_type that isn't text, calling Write on a run's
    design-tree.json
    When the hook runs
    Then it denies the call"""
    denied(main(written(TREE, agent=agent), ROOT))


@pytest.mark.supports("test_a_makers_write_to_the_design_tree_is_denied_while_the_scripts_write_it")
def test_a_write_to_a_runs_tree_given_with_backslashes_is_denied():
    """Given the main conversation calling Write on a run's design-tree.json, its path written
    with backslashes, as Claude Code gives it on Windows
    When the hook runs
    Then it denies the call"""
    denied(main(written(WINDOWS_TREE), ROOT))


@pytest.mark.supports("test_the_pruners_write_passes_the_hook_and_tree_py_check_takes_it")
@pytest.mark.parametrize("tool", ["Write", "Edit"])
def test_the_pruners_write_to_a_runs_tree_passes(tool: str):
    """Given rn's pruner calling Write or Edit on a run's design-tree.json
    When the hook runs
    Then it gives 0 and prints nothing, so that the write goes on"""
    assert main(written(TREE, agent="rn:pruner", tool=tool), ROOT) == (0, "", "")


@pytest.mark.supports(
    "test_the_orchestrators_write_to_the_design_tree_is_denied_pointing_to_a_new_pruner"
)
@pytest.mark.parametrize(
    "path",
    [
        "/work/invoicer/docs/guide.md",
        "/work/invoicer/docs/design-tree.json",
        "/work/invoicer/rn/20261120-invoices/design-tree.json",
        "/work/invoicer/.rn/20261120-invoices/design-tree.json.bak",
        "/work/invoicer/.rn/20261120-invoices/rounds/design-tree.json",
        "/work/invoicer/.rn/design-tree.json",
    ],
)
def test_the_main_conversations_write_to_another_file_passes(path: str):
    """Given the main conversation calling Write on a file that isn't a run's design tree, its
    name, its folder, or its depth under .rn near one's
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(written(path), ROOT) == (0, "", "")


@pytest.mark.supports(
    "test_the_orchestrators_write_to_the_design_tree_is_denied_pointing_to_a_new_pruner"
)
@pytest.mark.parametrize("tool", ["Read", "NotebookEdit"])
def test_another_tool_on_a_runs_tree_passes(tool: str):
    """Given the main conversation calling Read, or a tool that writes no JSON file, on a run's
    design-tree.json
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(written(TREE, tool=tool), ROOT) == (0, "", "")


@pytest.mark.supports(
    "test_the_orchestrators_write_to_the_design_tree_is_denied_pointing_to_a_new_pruner"
)
@pytest.mark.parametrize("given_input", [{"content": "{}"}, {"file_path": 7}, TREE])
def test_a_write_whose_path_cant_be_read_passes(given_input: Any):
    """Given the main conversation calling Write with no file_path, one that isn't text, or an
    input that isn't an object
    When the hook runs
    Then it gives 0 and prints nothing, as the hook never stops a call on its own fault"""
    called = {"tool_name": "Write", "tool_input": given_input}
    assert main(json.dumps(called).encode(), ROOT) == (0, "", "")

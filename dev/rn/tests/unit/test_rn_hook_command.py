"""The unit cases of hook/command.py, the hook that Claude Code runs before each Bash command and
each Write or Edit: a command of rn's maker that deletes, by rm or by find's -delete or -exec rm,
alone, in a subshell's chain, after a variable set and sudo, or on a new line, denied with how to
use remove; a Write or Edit of a run's design tree by the main conversation or by any agent but
rn's pruner, its path written with / or \\, denied pointing to a new pruner; a Bash command of any
but the pruner that surely writes a run's design tree, by each form that hook/written.py tells
apart, denied the same way; and each call that passes, printing nothing: a maker's command that
doesn't delete, a delete by the main conversation or by an agent named nearly as rn's, another
tool, the pruner's write of the tree by Write or Bash, a run of rn's own scripts, a Bash command
that only reads the tree, one that the hook isn't sure writes it, a write of a file near a run's
tree, a write whose path can't be read, stdin that isn't the hook's JSON, a command that can't be
read, and a fault of the hook's own."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from hook import command
from hook.command import main

ROOT = os.path.join(os.sep, "plugins", "rn")
REMOVE = os.path.join(ROOT, "domain", "scripts", "remove")


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


@pytest.mark.parametrize(
    "cmd",
    [
        'rm -r "$W/$p/__pycache__"',
        "find . -name '*.pyc' -delete",
        "find . -name __pycache__ -exec rm -r {} +",
        "(cd /tmp/rn-trial && rm -r build)",
        "LC_ALL=C sudo rm -f out.log",
        "echo done\nrm -r build",
    ],
)
def test_a_makers_delete_is_denied_with_how_to_use_remove_py(cmd: str):
    """Given rn's generator calling Bash with a command that deletes, by rm or by find's -delete or
    -exec rm, at any place in it
    When the hook runs
    Then it denies the call, its reason giving remove's command by its absolute path, with an
    exact path for each argument"""
    reason = denied(main(given(cmd), ROOT))
    assert f"python3 {REMOVE} <exact path> [<exact path> ...]" in reason
    assert "one argument each" in reason


@pytest.mark.parametrize(
    "cmd",
    [
        "pytest -q",
        "echo rm -r build",
        "find . -name '*.pyc'",
        "ls > rm",
    ],
)
def test_a_makers_command_that_doesnt_delete_passes(cmd: str):
    """Given rn's generator calling Bash with a command that deletes nothing, though it may name
    rm as a word
    When the hook runs
    Then it gives 0 and prints nothing, so that the call goes on"""
    assert main(given(cmd), ROOT) == (0, "", "")


@pytest.mark.parametrize("agent", [None, "rn"])
def test_a_delete_outside_rns_makers_passes(agent: Any):
    """Given a Bash call with rm by the main conversation, which names no agent, or by an agent
    that isn't one of rn's, named nearly as rn
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(given("rm -r build", agent=agent), ROOT) == (0, "", "")


def test_another_tool_passes():
    """Given rn's generator calling a tool other than Bash, whose input holds rm
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(given("rm -r build", tool="Write"), ROOT) == (0, "", "")


@pytest.mark.parametrize(
    "stdin",
    [
        b"not json",
        b"[]",
        json.dumps(
            {"agent_type": "rn:generator", "tool_name": "Bash", "tool_input": "rm -r x"}
        ).encode(),
    ],
)
def test_stdin_that_isnt_the_hooks_json_passes(stdin: bytes):
    """Given stdin that isn't JSON, JSON that isn't an object, or a tool_input that isn't one
    When the hook runs
    Then it gives 0 and prints nothing, as the hook never stops a call on its own fault"""
    assert main(stdin, ROOT) == (0, "", "")


@pytest.mark.parametrize("cmd", ["rm -r 'build", 42])
def test_a_command_that_cant_be_read_passes(cmd: Any):
    """Given rn's generator calling Bash with a command whose quote never closes, or that isn't
    text
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(given(cmd), ROOT) == (0, "", "")


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


@pytest.mark.parametrize(("tool", "agent"), [("Write", None), ("Edit", "rn:generator")])
def test_a_write_to_a_runs_tree_by_any_but_the_pruner_is_denied_pointing_to_a_new_pruner(
    tool: str, agent: Any
):
    """Given the main conversation, the orchestrator, which names no agent, calling Write, or rn's
    generator calling Edit, on a run's design-tree.json
    When the hook runs
    Then it denies the call, its reason naming the file and telling the writer to hand the fact
    to a new pruner"""
    reason = denied(main(written(TREE, agent=agent, tool=tool), ROOT))
    assert f"Leave {TREE} as it is" in reason
    assert "hand the fact you'd write to a new pruner" in reason


def test_a_write_to_a_runs_tree_given_with_backslashes_is_denied():
    """Given the main conversation calling Write on a run's design-tree.json, its path written
    with backslashes, as Claude Code gives it on Windows
    When the hook runs
    Then it denies the call"""
    denied(main(written(WINDOWS_TREE), ROOT))


def test_the_pruners_write_to_a_runs_tree_passes():
    """Given rn's pruner calling Edit on a run's design-tree.json
    When the hook runs
    Then it gives 0 and prints nothing, so that the write goes on"""
    assert main(written(TREE, agent="rn:pruner", tool="Edit"), ROOT) == (0, "", "")


@pytest.mark.parametrize(
    "path",
    [
        "/work/invoicer/docs/guide.md",
        "/work/invoicer/rn/20261120-invoices/design-tree.json",
    ],
)
def test_the_main_conversations_write_to_another_file_passes(path: str):
    """Given the main conversation calling Write on a file that isn't a run's design tree, by its
    name, or by its folder, which isn't .rn
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(written(path), ROOT) == (0, "", "")


def test_another_tool_on_a_runs_tree_passes():
    """Given the main conversation calling Read on a run's design-tree.json
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(written(TREE, tool="Read"), ROOT) == (0, "", "")


@pytest.mark.parametrize("given_input", [{"file_path": 7}, TREE])
def test_a_write_whose_path_cant_be_read_passes(given_input: Any):
    """Given the main conversation calling Write with a file_path that isn't text, or an
    input that isn't an object
    When the hook runs
    Then it gives 0 and prints nothing, as the hook never stops a call on its own fault"""
    called = {"tool_name": "Write", "tool_input": given_input}
    assert main(json.dumps(called).encode(), ROOT) == (0, "", "")


# A write to a run's design tree by Bash.

RUN = "/work/invoicer/.claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices"
RELATIVE_TREE = ".claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices/design-tree.json"


def bash_of(cmd: Any, agent: Any = None, cwd: str = "/work/invoicer") -> bytes:
    """The hook's stdin for a Bash call of the command, as Claude Code gives it in the agent's
    call, or in the main conversation's where the agent is None, made in the folder."""
    tool_input = {"command": cmd, "description": "Change the plan"}
    return rn_files.hook_input(cwd, "Bash", tool_input, agent).encode("utf-8")


def tree_denied(answer: tuple[int, str, str], named: str) -> str:
    """The reason of a denial of a write to the design tree: the reason of the Write and Edit
    refusal, naming what the command writes, and telling the writer to hand the fact on."""
    reason = denied(answer)
    assert f"Leave {named} as it is" in reason, "the tree written is named"
    assert "hand the fact you'd write to a new pruner" in reason
    return reason


@pytest.mark.parametrize(
    "cmd",
    [
        f"echo '{{}}' > {TREE}",
        f"echo '{{}}' | tee {TREE}",
        f"sed -i 's/reasoning/user/' {TREE}",
        f"awk -i inplace '{{print}}' {TREE}",
        f"sort -o {TREE} {TREE}",
        f"cp /tmp/plan.json {TREE}",
        f"dd if=/tmp/plan.json of={TREE}",
        f"git -C /work/invoicer checkout -- {TREE}",
        f"cd /tmp && cp plan.json {TREE}",
        f"echo '{{}}' > '{WINDOWS_TREE}'",
    ],
)
def test_a_bash_command_that_writes_a_runs_tree_is_denied_pointing_to_a_new_pruner(cmd: str):
    """Given the main conversation, the orchestrator, calling Bash with a command that writes a
    run's design-tree.json by its path, absolute as written with / or with \\: a redirection or
    tee onto it, an in-place edit, an output option, a copy onto it, or git setting it back, after
    a change of folder among them
    When the hook runs
    Then it denies the call, its reason the Write and Edit refusal's, naming the tree"""
    tree_denied(main(bash_of(cmd), ROOT), WINDOWS_TREE if WINDOWS_TREE in cmd else TREE)


def test_a_bash_write_by_a_path_from_the_current_folder_is_denied():
    """Given the main conversation calling Bash, in the repository's top, with a redirection onto
    the run's design-tree.json by its path from there
    When the hook runs
    Then it denies the call, naming the tree by the path the command gives"""
    tree_denied(main(bash_of(f"echo '{{}}' > {RELATIVE_TREE}"), ROOT), RELATIVE_TREE)


@pytest.mark.parametrize(
    "cmd",
    [
        f"bash -c \"echo '{{}}' > {TREE}\"",
        f"sh <<'EOF'\nsed -i 's/a/b/' {TREE}\nEOF",
    ],
)
def test_a_shells_command_that_writes_a_runs_tree_is_denied(cmd: str):
    """Given the main conversation calling Bash with a shell, by -c or a heredoc, whose command
    writes a run's design-tree.json
    When the hook runs
    Then it denies the call, its reason the Write and Edit refusal's, naming the tree"""
    tree_denied(main(bash_of(cmd), ROOT), TREE)


def test_a_run_of_rns_own_scripts_on_a_runs_tree_passes():
    """Given the main conversation calling Bash with a run of one of rn's own scripts, given a
    run's design-tree.json
    When the hook runs
    Then it gives 0 and prints nothing, as the scripts write the tree by design"""
    assert main(bash_of(f"python3 {ROOT}/domain/scripts/tree signoff {TREE}"), ROOT) == (0, "", "")


@pytest.mark.parametrize(
    "cmd",
    [
        f"python3 -c \"import json; json.dump({{}}, open('{TREE}', 'w'))\"",
        f"git commit -m 'Plan' -- {TREE}",
        f"T={TREE}; echo '{{}}' > \"$T\"",
        f"cd {RUN} && echo '{{}}' > design-tree.json",
        f"ls {TREE} | xargs sed -i 's/a/b/'",
        f"cat {TREE} 'unclosed",
        f"bash /tmp/fix.sh {TREE}",
    ],
)
def test_a_command_naming_a_runs_tree_that_the_hook_isnt_sure_writes_it_passes(cmd: str):
    """Given the main conversation calling Bash with a command that names a run's
    design-tree.json, by its path or its name, where the hook isn't sure that it writes it: an
    interpreter's code, git that only records it, a path held in a variable, a folder changed
    first, the tree fed through xargs, a shell's script, or a command the shell can't read
    When the hook runs
    Then it gives 0 and prints nothing, as a refused read stops the run, and tree checks the
    tree's form before each commit"""
    assert main(bash_of(cmd), ROOT) == (0, "", "")


@pytest.mark.parametrize(
    "cmd",
    [
        f"jq '.work' < {TREE}",
        f"sed -n '1,20p' {TREE}",
        f"awk '/decided/' {TREE}",
        f"sort {TREE}",
        f"cp {TREE} /tmp/plan.json",
        f"git diff -- {TREE}",
        f"wc -l {TREE} > /tmp/count.txt",
        f'bash -c "jq .goal {TREE}"',
    ],
)
def test_a_bash_command_that_only_reads_a_runs_tree_passes(cmd: str):
    """Given the main conversation calling Bash with a command that only reads a run's
    design-tree.json: a reader by an input redirection, a stream editor or a sort with no in-place
    or output option, a copy from it, git's reading, a redirection elsewhere, or a shell whose
    command only reads
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(bash_of(cmd), ROOT) == (0, "", "")


@pytest.mark.parametrize(
    "cmd",
    [
        "echo '{}' > /work/invoicer/.rn/design-tree.json",
        "echo '{}' > design-tree.json",
    ],
)
def test_a_bash_write_near_a_runs_tree_passes(cmd: str):
    """Given the main conversation calling Bash, in the repository's top, with a write to a file
    that isn't a run's design tree: one right under .rn, or design-tree.json in the top
    When the hook runs
    Then it gives 0 and prints nothing"""
    assert main(bash_of(cmd), ROOT) == (0, "", "")


def test_the_pruners_bash_write_to_a_runs_tree_passes():
    """Given rn's pruner calling Bash with a redirection onto a run's design-tree.json
    When the hook runs
    Then it gives 0 and prints nothing, as the tree takes the pruner's writes"""
    assert main(bash_of(f"echo '{{}}' > {TREE}", "rn:pruner"), ROOT) == (0, "", "")

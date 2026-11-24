"""Decides hook.py's input and output, as Claude Code runs it before each Bash command and each
write by Write or Edit: it denies a command of rn's makers that deletes, with how to use remove.py,
as only remove.py removes without a permission prompt that stops the run; it denies each write to a
run's design tree but the pruner's, by Write, Edit, or Bash, telling its writer to hand the fact to
a new pruner, as the plan holds only what the pruner weighed, where it's sure of a write by Bash;
and it lets every other call pass, rn's scripts among them, which write the tree by design."""

from __future__ import annotations

import json
import os
from typing import Any

from fault import Answer

from hook.bash import deletes
from hook.write import is_tree
from hook.written import written

# What the hook gives to let a call pass: 0, with nothing printed.
PASS: Answer = (0, "", "")

# The start of each `agent_type` of rn's subagents, as Claude Code names a plugin's agent
# `<plugin>:<agent>`, such as `rn:generator`.
RN_AGENT = "rn:"
# The `agent_type` of rn's pruner, the one role whose writes the design tree takes.
PRUNER = "rn:pruner"
# The tools that write a file, each giving its path as `tool_input.file_path`.
WRITERS = ("Write", "Edit")

_REASON = (
    "rn's makers remove files only through remove.py, which asks no permission:"
    " python3 {remove} <exact path> [<exact path> ...]. Give each file or folder you made by its"
    " exact path, absolute or from the current folder, one argument each, with no wildcard. It"
    " removes only inside the git work tree that holds the current folder and inside the system's"
    " temporary folder."
)

_TREE_REASON = (
    "A run's design tree takes only the pruner's writes, as the plan holds only what the pruner"
    " weighed. Leave {tree} as it is, and hand the fact you'd write to a new pruner: the"
    " orchestrator starts rn:pruner with the run's folder and the fact, and each other role ends"
    " with the fact in its result, for the orchestrator to hand on."
)


def main(stdin: bytes, plugin_root: str) -> Answer:
    """The exit code, stdout, and stderr of `hook.py` on the hook's input, with rn's folder at
    `plugin_root`.

    0 with the JSON that denies the call, its reason giving remove.py's command by its absolute
    path, where the input is a Bash call of one of rn's agents whose command deletes, as
    `hook.bash.deletes` holds it. 0 with the JSON that denies the call, its reason naming the file
    and telling the writer to hand the fact to a new pruner, where the input is a Write or Edit
    call whose `file_path` is a run's design tree, as `hook.write.is_tree` holds it, and whose
    `agent_type` isn't `rn:pruner`, the main conversation's, which names none, among them. The
    same where the input is a Bash call of any but the pruner whose command writes a run's design
    tree, as `hook.written.written` holds it from the call's `cwd`, naming the tree as the command
    names it. 0 with nothing printed for every other
    input, a run of rn's own scripts among them, one that isn't the hook's JSON and a fault of the
    hook's own among them, as the hook never stops a call on a fault of its own."""
    try:
        return decided(stdin, plugin_root)
    except Exception:  # noqa: BLE001 - the hook's own fault lets the call pass.
        return PASS


def decided(stdin: bytes, plugin_root: str) -> Answer:
    """What the hook gives on its input."""
    try:
        called = json.loads(stdin.decode("utf-8"))
    except ValueError:
        return PASS
    if not isinstance(called, dict):
        return PASS
    if _rn_deletes(called):
        return _denied(_REASON.format(remove=os.path.join(plugin_root, "scripts", "remove.py")))
    tree = _tree_written(called)
    if tree is not None:
        return _denied(_TREE_REASON.format(tree=tree))
    tree = _bash_written(called)
    return PASS if tree is None else _denied(_TREE_REASON.format(tree=tree))


def _denied(reason: str) -> Answer:
    """What the hook gives to deny the call, with the reason."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    return 0, json.dumps(output) + "\n", ""


def _tree_written(called: dict[str, Any]) -> str | None:
    """The design tree that the call writes, where it's a Write or Edit call of a run's design
    tree by any but the pruner; else None."""
    given = called.get("tool_input")
    path = given.get("file_path") if isinstance(given, dict) else None
    if (
        called.get("tool_name") in WRITERS
        and isinstance(path, str)
        and is_tree(path)
        and called.get("agent_type") != PRUNER
    ):
        return path
    return None


def _bash_written(called: dict[str, Any]) -> str | None:
    """The run's design tree that the call surely writes, where it's a Bash call by any but the
    pruner; else None."""
    given = called.get("tool_input")
    command = given.get("command") if isinstance(given, dict) else None
    cwd = called.get("cwd")
    if (
        called.get("tool_name") != "Bash"
        or not isinstance(command, str)
        or called.get("agent_type") == PRUNER
    ):
        return None
    return written(command, cwd if isinstance(cwd, str) else "")


def _rn_deletes(called: dict[str, Any]) -> bool:
    """Whether the call is a Bash command of one of rn's agents that deletes."""
    agent = called.get("agent_type")
    given = called.get("tool_input")
    command = given.get("command") if isinstance(given, dict) else None
    return (
        isinstance(agent, str)
        and agent.startswith(RN_AGENT)
        and called.get("tool_name") == "Bash"
        and isinstance(command, str)
        and deletes(command)
    )

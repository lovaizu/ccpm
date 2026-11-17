"""The words of a run of Lane's own scripts, as a role types it and the guard reads it in a Bash
command: result.py with its role and Result, step.py with its role and Step, and item.py with its
role and Item, so that whoever writes them and whoever reads them hold one form."""

from __future__ import annotations

import os
import re
import shlex

# What the role types for the plugin's folder in a command, as Claude Code fills it in a hook's
# command but not in a Bash command.
ROOT = "${CLAUDE_PLUGIN_ROOT}"
# What in a command makes the shell run more than one program, or read another file than the words
# name, so that the command is no single run of a script.
MORE = re.compile(r"[|&;<>()$`\\\n]")
# A Step's number as a run of step.py gives it: a whole number of 1 or more.
STEP = re.compile(r"[1-9][0-9]*")


def result_command(role: str, result: str) -> str:
    """The command by which a role gives a Result, as a Lane's sentence names it.

    Takes: the role or skill, and the Result.
    Gives: `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py <role> <result>`.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L->>T: checks each Lane, and makes its sentence`, for the Lane on a role's last
    Step.
    """
    return f"python3 {ROOT}/hooks/lane/result.py {role} {result}"


def result_args(command: str, root: str) -> tuple[str, str] | None:
    """The role and the Result that a Bash command gives by the plugin's result.py.

    Takes: the Bash command, and the plugin's folder, which `${CLAUDE_PLUGIN_ROOT}` names.
    Gives: the role and the Result, or None where the command isn't one run of the plugin's
    result.py with two arguments.
    Changes: nothing.
    Refuses: nothing.
    Carries: S5 `SA->>R: result.py <role> <result>` as the guard lets it through, its `CC->>G: the
    PostToolUse, with its agent_id`, and S4's `CC->>G: the PostToolUse, with no agent_id`.
    """
    given = _script_args(command, root, "result.py")
    return (given[0], given[1]) if given else None


def step_command(role: str) -> str:
    """The command by which a role marks a Step done, as the sentence of keeps_steps names it.

    Takes: the role or skill.
    Gives: `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/step.py <role> <n>`, `<n>` standing for the
    Step's number, which the role fills in.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L->>T: checks each Lane, and makes its sentence`, for a Lane of keeps_steps.
    """
    return f"python3 {ROOT}/hooks/lane/step.py {role} <n>"


def step_args(command: str, root: str) -> tuple[str, int] | None:
    """The role and the Step that a Bash command marks by the plugin's step.py.

    Takes: the Bash command, and the plugin's folder, which `${CLAUDE_PLUGIN_ROOT}` names.
    Gives: the role and the Step's number, or None where the command isn't one run of the
    plugin's step.py with a role and a whole number of 1 or more.
    Changes: nothing.
    Refuses: nothing.
    Carries: S5 `alt a run of step.py <role> <n>`, and its `CC->>G: the PostToolUse, with its
    agent_id`; S4's Note that the skill's runs of step.py go as S5 draws.
    """
    given = _script_args(command, root, "step.py")
    if given and STEP.fullmatch(given[1]):
        return given[0], int(given[1])
    return None


def item_command(role: str) -> str:
    """The command by which a role marks an Item of a Step done, as the sentence of keeps_items
    names it.

    Takes: the role or skill.
    Gives: `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/item.py <role> <id>`, `<id>` standing for the
    Item's ID, which the role fills in.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `L->>T: checks each Lane, and makes its sentence`, for a Lane of keeps_items.
    """
    return f"python3 {ROOT}/hooks/lane/item.py {role} <id>"


def item_args(command: str, root: str) -> tuple[str, str] | None:
    """The role and the Item that a Bash command marks by the plugin's item.py.

    Takes: the Bash command, and the plugin's folder, which `${CLAUDE_PLUGIN_ROOT}` names.
    Gives: the role and the Item's ID, or None where the command isn't one run of the plugin's
    item.py with two arguments.
    Changes: nothing.
    Refuses: nothing.
    Carries: S5 `else a run of item.py <role> <id>`, and its `CC->>G: the PostToolUse, with its
    agent_id`; S4's Note that the skill's runs of item.py go as S5 draws.
    """
    given = _script_args(command, root, "item.py")
    return (given[0], given[1]) if given else None


def _script_args(command: str, root: str, script: str) -> list[str] | None:
    """The two arguments of one run of the plugin's script of Lane's, by `python3` and the script's
    path, which `${CLAUDE_PLUGIN_ROOT}` may name; None where the command runs anything else beside
    it, or gives the script other than two arguments."""
    if MORE.search(command.replace(ROOT, "")):
        return None
    words = _words(command.replace(ROOT, root))
    path = os.path.join(root, "hooks", "lane", script)
    if len(words) == 4 and words[0] == "python3" and os.path.normpath(words[1]) == path:
        return words[2:]
    return None


def _words(command: str) -> list[str]:
    """The command's words as shlex splits them, each run of the shell's operators, such as `;`
    or `&&`, a word of its own, so that a word beside one reads apart from it; none where shlex
    can't split it, such as a here-document that holds an apostrophe, which then runs none of
    Lane's scripts as the guard reads them."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        return []

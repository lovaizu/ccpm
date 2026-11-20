"""Decides the steps of each turn of rn's orchestrator and of each start of its generator and
evaluator, and the rules of each step, as Lane asks them: the steps of the turn's event and those
that every event shares, and for a role the files each step reads, writes, and never reads, the
commands it runs, the practices of its kind's best practice as its checklist, and its check at the
end."""

from __future__ import annotations

import os
import sys
from typing import Any

# rn's code lies in domain/, which comes on the import path before it's imported.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import end

# A start as Lane gives it, in the form of Lane's rules.in.schema.json, and its steps that rn
# gives back, in the form of its rules.out.schema.json.
Given = dict[str, Any]
Steps = dict[str, Any]


def steps(given: Given, cwd: str, plugin_root: str) -> Steps:
    """The steps of the turn or the start, each with its rules, each path as Lane compares it,
    `os.path.relpath(os.path.realpath(path), os.path.realpath(cwd))`, so that a folder outside the
    repository, such as the people's starting state or rn's best practices, comes as `../...`, and
    each command as `python3 <plugin_root>/scripts/<script> <subcommand>`.

    Takes: the turn or the start as Lane gives it; the folder that the conversation works in, the
    top of the user's repository; and rn's folder.
    Gives, for a turn of the orchestrator, whose role is the skill of rn that the run stands on,
    `rn:up`, `rn:dn`, `rn:ty`, or `rn:gm`, the steps of the event that its prompt starts, each held
    in order and run on the run's folder: a new request, a prompt `/rn:up` with words, and a
    pick-up, `/rn:up` alone, the run being the one that `place.named` names from the day and the
    words for a new request, else the first that `repository.worktree.paused` gives:
    - the event's own steps: for a new request `start`, running only `repository.py new`; for a
      pick-up `find`, running only `repository.py find`; for a sign-off, `/rn:ty`, `record`,
      running only `tree.py signoff`; for a pause, `/rn:dn`, `stop`, writing nothing, and
      `pause`, running only `repository.py pause`, and no step that every event shares; for a
      send-back, `/rn:gm`, an answer, any other prompt of the person, and a role's end, a
      subagent's end as Claude Code gives it, none;
    - the steps that every other event shares: `review`, writing only the run's design tree;
      `touched`, writing only the run's design tree, with the checklist whose command is
      `tree.py touched <run>`; `commit`, running only `tree.py commit`; and `move`, running only
      `repository.py put-up` and `tree.py cut`, writing nothing.
    For `rn:generator`, whose prompt is the path of its Cut from `cwd`, the steps `read`, `decide`,
    `make`, `try`, and `check`, each held in order: `read` reading whole the Cut, the best
    practice's `best-practice.md`, and each input that is a file, writing nothing; `decide` with the
    best practice's `decide` items as its checklist, writing only the Round's folder, where its
    `generator.json` gives a point, and ending on `point`; `make`
    with its `make` items as its checklist, writing only the deliverable's paths; `try` writing only
    the Round's folder; and `check` running only `repository.py checks`, with the check `check.py
    generator <cut>`, and the results `made` or, ending, `point`.
    For `rn:evaluator`, whose prompt is the path of its Cut from `cwd`, the steps `read`, `start`,
    `try`, and `judge`, each held in order and never reading the design tree, the generator's Cut
    and result, or another Round: `read` reading whole the Cut, writing nothing; `start` running
    only `repository.py trial`, writing nothing; `try` writing only the folder of the people's
    starting state, as `repository.trial.folder` names it; and `judge` with each condition's ID as
    its checklist, writing only the Round's folder, with the check `check.py evaluator <cut>` and
    the result `judged`.
    Changes: nothing.
    Refuses: Wrong where the role is none of rn's, a role's prompt names no Cut in its form, or a
    turn other than a new request finds no run, naming what's wrong.
    """
    raise NotImplementedError("rules.steps")


def main(stdin: str, cwd: str, plugin_root: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of the adapter, as Lane runs it.

    Takes: what Lane writes on its standard input, the folder it runs in, and rn's folder.
    Gives: 0 with `steps`'s output as one line of JSON; 1 with `rules.py: <what's wrong>` where the
    input isn't JSON or `steps` refuses it as Wrong; 2 with what stopped it where it CantRun.
    Lane stops the turn or the start on any but 0.
    Changes: nothing.
    Refuses: nothing; each fault is its exit code.
    """
    raise NotImplementedError("rules.main")


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd(), os.path.dirname(os.path.dirname(HERE))))

#!/usr/bin/env python3
"""Decides the steps and rules that hold a start of the generator or an evaluator, from the Cut
that its prompt names: what it writes and never reads, the items of each step's checklist, its
check, and the results that end it."""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "domain"))

from fault import end


def main(given: str, cwd: str, plugin: str) -> tuple[int, str, str]:
    """Gives Lane the steps of a start, as Lane runs this adapter for each start of a role that
    lane/rules.json names with no steps.

    Takes: the run, the start's role, and its prompt, on standard input in the form of Lane's
    rules.in.schema.json; the folder of the run's worktree; and rn's folder.
    Gives: 0 with `{"steps": [...]}`, in the form of Lane's rules.out.schema.json, the steps of
    `domain/generator.md` or `domain/evaluator.md` by their numbers, each with `order`, and, from
    the Cut that the prompt names, its result beside it at `<role>[-<group>].json`:
    - for `rn:generator`: at step 2, a `checklist` of each `N<n>.<m>` of the Cut's best practice
      that its maker takes while deciding, the m-th practice of the condition N<n>, and a `result`
      that `ends` on `point`; at step 3, a `checklist` of each that its maker takes while making,
      and `writes` of the deliverable's path and the result; at step 4, `writes` of the result, the
      `check` `python3 <rn>/scripts/check.py generator <Cut>`, and a `result` of `made`;
    - for `rn:evaluator`: at step 2, `reads_none` of the run's design-tree.json and the
      generator's Cut and result of the Round; at step 3, a `checklist` of the ID of each condition
      of its Cut; at step 4, `writes` of the result, the `check`
      `python3 <rn>/scripts/check.py evaluator <Cut>`, and a `result` of `judged`.
    1 with what Wrong says, such as Lane's input out of its form, a prompt that names no Cut of a
    run's Round, a Cut out of its form, or one that names no best practice of rn's.
    Changes: nothing.
    Refuses: nothing beyond the exit codes above."""
    raise NotImplementedError("rules.main")


if __name__ == "__main__":
    end(main(sys.stdin.read(), os.getcwd(), os.path.join(HERE, "..", "..")))

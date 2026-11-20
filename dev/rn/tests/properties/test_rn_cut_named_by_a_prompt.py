"""The properties of what rn gives Lane from a start's prompt, which the orchestrator, an AI,
writes: lane/adapters/rules.py's steps and lane/adapters/starts_due.py's starts due take the Cut
that the prompt names the same in each form in which the prompt can name it, from the top of rn's
worktree of the run or whole, in any words around it. Each is metamorphic: the start named from the
top in the bench's words is the input it's compared with."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from rn_bench import RN, RUN, command, evaluator_cut, generator_cut, run_worktree, typed

RULES = command("lane/adapters/rules.py")
STARTS_DUE = command("lane/adapters/starts_due.py")
GROUPS = ("C1", "C2", "C3")
MADE = {"result": "made", "carried_out": []}

# The words around a path that an AI writes: any words, on the path's line or the next.
words = st.text(alphabet="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ,;:-", max_size=30)
# What an AI may put around a path: nothing, a code span, quotes, or brackets, and a mark after it.
wrappers = st.sampled_from([("", ""), ("`", "`"), ('"', '"'), ("'", "'"), ("(", ")")])
marks = st.sampled_from(["", ".", ",", ":"])


def cut_name(role: str, group: str, slot: int) -> str:
    """The name of a Cut of the role and group in the slot, as Data model's Round places it."""
    named = "generator" if role == "generator" else f"evaluator-{group}"
    return f"{named}{'' if slot == 1 else f'.{slot}'}.cut.json"


@st.composite
def prompts(draw: Any, top: str, cut: str) -> str:
    """A prompt that names the Cut, at `cut` from the top, from the top or whole, in any words."""
    path = draw(st.sampled_from([cut, os.path.join(top, cut)]))
    before, after = draw(wrappers)
    line = draw(st.sampled_from([" ", "\n"]))
    return f"{draw(words)} {before}{path}{after}{draw(marks)}{line}{draw(words)}"


def rules(top: str, role: str, prompt: str) -> tuple[int, str, str]:
    """rules.py's main for a start of the role with the prompt, in rn's worktree of the run."""
    given = {"run": {"skill": "rn:up", "words": ""}, "role": f"rn:{role}", "prompt": prompt}
    return RULES.main(json.dumps(given), top, RN)


@pytest.mark.supports("test_a_role_that_writes_beside_its_deliverable_is_told_its_step")
@given(
    role=st.sampled_from(["generator", "evaluator"]),
    number=st.integers(1, 12),
    group=st.sampled_from(GROUPS),
    slot=st.integers(1, 3),
    data=st.data(),
)
def test_rules_take_the_cut_alike_in_any_form_a_prompt_names_it(
    role: str, number: int, group: str, slot: int, data: Any
):
    """Given any start of the generator or an evaluator, of any Round and slot, its Cut beside the
    generator's made where it's an evaluator's, and any prompt that names the Cut from the top of
    rn's worktree of the run or whole, in any words, quotes, or marks around it
    When rules.py runs for the start, and for one whose prompt names the Cut from the top in the
    bench's words
    Then both give 0 with the same steps, every path in them from the top, as the Cut of Data
    model and Lane applied to every activity of every role's steps (P5.1) need"""
    rounds = f"{RUN}/rounds/{number}"
    cut = f"{rounds}/{cut_name(role, group, slot)}"
    files: dict[str, Any] = {f"{rounds}/generator.cut.json": generator_cut()}
    if role == "evaluator":
        files[f"{rounds}/generator.json"] = MADE
    files[cut] = generator_cut() if role == "generator" else evaluator_cut(group, ["N1"])
    with tempfile.TemporaryDirectory() as tmp:
        _, top = run_worktree(tmp, files)
        named = rules(top, role, f"Carry out your steps, from your Cut at {cut}")
        assert named[0] == 0, named
        assert rules(top, role, data.draw(prompts(top, cut))) == named


@pytest.mark.supports("test_a_generator_running_gets_no_second_start_of_its_deliverable")
@given(
    role=st.sampled_from(["generator", "evaluator"]),
    group=st.sampled_from(GROUPS),
    slot=st.integers(1, 3),
    at_root=st.booleans(),
    data=st.data(),
)
def test_starts_due_count_a_start_alike_in_any_form_its_prompt_names_its_cut(
    role: str, group: str, slot: int, at_root: bool, data: Any
):
    """Given any start of round 1 that runs, the generator or an evaluator of the command made, in
    any slot after Cuts that a stop left with no result, a conversation at the repository's root
    or in rn's worktree of the run, and any prompt that names the start's Cut from the worktree's
    top or whole, in any words, quotes, or marks around it
    When starts_due.py runs with the start among the moves, and with one whose prompt names the
    Cut from the top in the bench's words
    Then both give 0 with the same starts due, the start counted as one that runs, so that no
    second start of its work is due, as rn's order given to Lane as the starts due (P5.2) and the
    run's state in files (P6.1) need"""
    rounds = f"{RUN}/rounds/1"
    files: dict[str, Any] = {}
    if role == "evaluator":
        files = {f"{rounds}/generator.cut.json": generator_cut(), f"{rounds}/generator.json": MADE}
    for earlier in range(1, slot + 1):
        held = generator_cut() if role == "generator" else evaluator_cut(group, ["N1"])
        files[f"{rounds}/{cut_name(role, group, earlier)}"] = held
    cut = f"{rounds}/{cut_name(role, group, slot)}"
    with tempfile.TemporaryDirectory() as tmp:
        root, top = run_worktree(tmp, files)
        cwd = root if at_root else top

        def due(prompt: str) -> tuple[int, str, str]:
            start = {"kind": "start", "role": f"rn:{role}", "prompt": prompt}
            run = {"skill": "rn:up", "words": "", "moves": [typed("rn:up"), start]}
            return STARTS_DUE.main(json.dumps({"run": run}), cwd)

        named = due(f"Carry out your steps, from your Cut at {cut}")
        assert named[0] == 0, named
        assert due(data.draw(prompts(top, cut))) == named

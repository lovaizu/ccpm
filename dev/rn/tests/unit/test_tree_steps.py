"""The unit cases of tree/steps.py, how tree.py reads the steps of one of rn's prompts, through
`read` and `of_role`, on parts that each test writes."""

from __future__ import annotations

import os
from typing import Any

import pytest
from rn_example import RN, write
from tree.fault import Wrong
from tree.practices import DECIDE, MAKE
from tree.steps import Step, of_role, read

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

PART = """# rn's generator

## Steps

1. Read what you're given to its end.
2. Decide. For each condition, carry out its practices marked *While deciding*.
3. Make. Carry out the practices marked *While making*.
4. End by giving `done`.

## What you give

Done.
"""


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_read_gives_each_step_with_the_phase_it_takes(tmp_path: Any):
    """Given a part of four steps, step 2 naming *While deciding* and step 3 *While making*
    When its steps are read
    Then they're steps 1 to 4, step 2 taking deciding and step 3 making"""
    path = write(str(tmp_path), "generator.md", PART)
    found = read(path, "generator")
    assert [(each.number, each.takes) for each in found] == [
        (1, ""),
        (2, DECIDE),
        (3, MAKE),
        (4, ""),
    ]
    assert found[0] == Step("generator", 1, "Read what you're given to its end.")


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_read_reads_a_step_over_several_lines_as_one(tmp_path: Any):
    """Given a part whose step 1 runs over two lines
    When its steps are read
    Then step 1 holds both lines' words"""
    path = write(str(tmp_path), "p.md", "## Steps\n\n1. Read what you're\n   given to its end.\n")
    assert read(path, "p")[0].words == "Read what you're given to its end."


@pytest.mark.parametrize(
    "text",
    [
        "# rn's generator\n\nNo steps.\n",
        "## Steps\n\n1. One.\n3. Three.\n",
        "## Steps\n\n2. Two.\n",
    ],
)
@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_read_refuses_a_part_without_steps_numbered_from_1_in_order(tmp_path: Any, text: str):
    """Given a part with no `## Steps`, one whose steps skip 2, or one that starts at 2
    When its steps are read
    Then it's refused, naming the file"""
    path = write(str(tmp_path), "odd.md", text)
    with pytest.raises(Wrong, match="odd.md"):
        read(path, "odd")


@pytest.mark.supports("test_the_orchestrators_turn_is_held_until_its_record_holds_each_step")
def test_of_role_of_the_orchestrator_holds_the_steps_of_its_part_and_of_each_command(tmp_path: Any):
    """Given a plugin whose orchestrator's part and each command's SKILL.md hold steps
    When the steps of `up` are asked for
    Then they hold those of the orchestrator and those of up, dn, ty, and gm, each by its own"""
    write(str(tmp_path), "domain/orchestrator.md", "## Steps\n\n1. Settle each point.\n")
    for command in ("up", "dn", "ty", "gm"):
        write(
            str(tmp_path),
            f"skills/{command}/SKILL.md",
            f"---\nname: {command}\n---\n\n## Steps\n\n1. Go.\n",
        )
    assert {each.of for each in of_role(str(tmp_path), "up")} == {
        "orchestrator",
        "up",
        "dn",
        "ty",
        "gm",
    }


@pytest.mark.supports("test_the_guard_holds_a_generators_end_whose_record_lacks_a_step")
def test_of_role_of_the_generator_is_its_parts_steps():
    """Given rn's plugin
    When the steps of the generator are asked for
    Then each is of the generator, read from domain/generator.md"""
    found = of_role(RN, "generator")
    assert found and found == read(os.path.join(RN, "domain", "generator.md"), "generator")

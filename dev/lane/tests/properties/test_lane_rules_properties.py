"""The property-based tests of reading a plugin's rules, as Lane's Test strategy names them: a
plugin's author writes lane/rules.json in any form that rules.schema.json takes, and any slip of
the hand out of it, so Lane must take each rule in form as written and refuse each one out of form,
since a rule taken wrongly leaves a step unchecked or stops a right move. Each generator draws from
rules.schema.json and the rule types of plugins/lane/docs/rules-and-adapters.md."""

from __future__ import annotations

import copy
import json
import os
import tempfile
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from rules import OutOfForm, read_rules

# Text as a person writes it in a JSON file: any letter, digit, mark, or space, no control
# character.
TEXT = st.text(st.characters(blacklist_categories=("Cc", "Cs")), min_size=1, max_size=12)
TEXTS = st.lists(TEXT, max_size=3)
SOME = st.lists(TEXT, min_size=1, max_size=3)
# A path of a rule, of one to three parts, a folder's closing with /.
PATH = st.builds(
    lambda parts, folder: "/".join(parts) + ("/" if folder else ""),
    st.lists(TEXT.filter(lambda part: "/" not in part), min_size=1, max_size=3),
    st.booleans(),
)
FILE = PATH.filter(lambda path: not path.endswith("/"))

# One rule of each type, with that type's values, as the form takes them.
RULE = st.one_of(
    st.fixed_dictionaries({"type": st.just("writes"), "paths": st.lists(PATH, max_size=3)}),
    st.fixed_dictionaries(
        {"type": st.just("reads_none"), "paths": st.lists(PATH, min_size=1, max_size=3)}
    ),
    st.fixed_dictionaries(
        {"type": st.just("reads_whole"), "paths": st.lists(FILE, min_size=1, max_size=3)}
    ),
    st.fixed_dictionaries({"type": st.just("commands"), "commands": TEXTS}),
    st.just({"type": "order"}),
    st.fixed_dictionaries({"type": st.just("checklist"), "items": TEXTS}),
    st.fixed_dictionaries(
        {"type": st.just("result")}, optional={"results": SOME, "ends": SOME}
    ).filter(lambda rule: "results" in rule or "ends" in rule),
    st.fixed_dictionaries({"type": st.just("check"), "check": TEXT}),
)
STEP = st.fixed_dictionaries({"name": TEXT, "rules": st.lists(RULE, max_size=4)})
ROLE = st.one_of(st.just({}), st.fixed_dictionaries({"steps": st.lists(STEP, max_size=3)}))
ROUTE = st.fixed_dictionaries(
    {
        "after": st.one_of(
            st.fixed_dictionaries({"command": TEXT}),
            st.fixed_dictionaries({"role": TEXT, "result": TEXT}),
        ),
        "start": TEXTS,
    }
)
RULES = st.fixed_dictionaries(
    {"roles": st.dictionaries(TEXT, ROLE, max_size=3)},
    optional={"routes": st.lists(ROUTE, max_size=3)},
)
# Rules with a rule at least, which a slip of the hand can break.
WITH_A_RULE = st.fixed_dictionaries(
    {
        "roles": st.dictionaries(
            TEXT,
            st.fixed_dictionaries(
                {
                    "steps": st.lists(
                        st.fixed_dictionaries(
                            {"name": TEXT, "rules": st.lists(RULE, min_size=1, max_size=3)}
                        ),
                        min_size=1,
                        max_size=2,
                    )
                }
            ),
            min_size=1,
            max_size=2,
        )
    }
)
# The rule types of rules-and-adapters.md, each with the field of its values.
VALUES = {
    "writes": "paths",
    "reads_none": "paths",
    "reads_whole": "paths",
    "commands": "commands",
    "checklist": "items",
    "check": "check",
}
# The name that a slip of the hand gives each field of values.
SLIPPED = {"paths": "path", "commands": "command", "items": "item", "check": "checks"}
TYPES = ("writes", "reads_none", "reads_whole", "commands", "order", "checklist", "result", "check")


def read_written(rules_json: str) -> Any:
    """What read_rules gives of a plugin whose lane/rules.json holds the text."""
    with tempfile.TemporaryDirectory() as plugin:
        os.makedirs(os.path.join(plugin, "lane"))
        with open(os.path.join(plugin, "lane", "rules.json"), "w", encoding="utf-8") as f:
            f.write(rules_json)
        return read_rules(plugin)


@pytest.mark.supports("test_a_step_is_held_only_to_the_types_its_rules_pick")
@given(RULES)
def test_rules_in_form_are_read_as_written(rules: dict[str, Any]):
    """Given any rules in the form of rules.schema.json: any roles, a subagent's with no steps
    among them, any steps of any rules of each type with any values, and any routes
    When read_rules reads them from the plugin's lane/rules.json
    Then it gives them as written, each rule with its type and values
    (Postcondition, resting on Concept model's Rules and read_rules's Gives.)"""
    assert read_written(json.dumps(rules)) == rules


def slip(rules: dict[str, Any], data: st.DataObject) -> dict[str, Any]:
    """The rules with one slip of the hand that leaves the form: a rule of a type that Lane
    lacks, a rule without its values or with them under another name, a file to read whole named
    as a folder, a result rule with neither results nor ends, or a step with no name or an empty
    one."""
    slipped = copy.deepcopy(rules)
    steps = [step for role in slipped["roles"].values() for step in role["steps"]]
    step = data.draw(st.sampled_from(steps))
    rule = data.draw(st.sampled_from(step["rules"]))
    kinds = ["type", "name", "empty name"]
    if rule["type"] in VALUES:
        kinds += ["no values", "values renamed"]
    if rule["type"] == "reads_whole":
        kinds.append("folder")
    if rule["type"] == "result":
        kinds.append("no results")
    kind = data.draw(st.sampled_from(kinds))
    if kind == "type":
        rule["type"] = data.draw(TEXT.filter(lambda name: name not in TYPES))
    elif kind == "name":
        del step["name"]
    elif kind == "empty name":
        step["name"] = ""
    elif kind == "no values":
        del rule[VALUES[rule["type"]]]
    elif kind == "values renamed":
        field = VALUES[rule["type"]]
        rule[SLIPPED[field]] = rule.pop(field)
    elif kind == "folder":
        rule["paths"].append(data.draw(FILE) + "/")
    else:
        rule.pop("results", None)
        rule.pop("ends", None)
    return slipped


@pytest.mark.supports("test_rules_out_of_form_let_the_call_through_saying_what_lane_couldnt_check")
@given(WITH_A_RULE, st.data())
def test_rules_out_of_form_at_any_place_are_refused_naming_the_file(
    rules: dict[str, Any], data: st.DataObject
):
    """Given any rules in form with one slip of the hand at any place, or their text cut short of
    its end, which isn't JSON
    When read_rules reads them from the plugin's lane/rules.json
    Then it refuses them by OutOfForm, naming lane/rules.json
    (Postcondition, resting on P1.1 and read_rules's Refuses.)"""
    text = json.dumps(slip(rules, data))
    if data.draw(st.booleans()):
        text = text[: data.draw(st.integers(0, len(text) - 1))]
    with pytest.raises(OutOfForm) as refused:
        read_written(text)
    assert "rules.json" in str(refused.value)

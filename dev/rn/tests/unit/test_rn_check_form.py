"""The unit cases of check/form.py, which holds a JSON value to one of rn's JSON Schemas: one value
that holds and one that leaves it for each keyword of draft-07 that rn's schemas and the design
tree's use, `type` of each JSON type, `required`, `properties`, `additionalProperties`, the last
three on a value that isn't an object too, `items`, `minItems`, `minLength`, `minimum`, `pattern`,
`enum`, `const`, `oneOf`, `anyOf`, and `$ref` into `$defs`, each limit on both sides; a key that
JSON Pointer escapes; no, one, and several faults; rn's own schemas on the values its parts write;
and CantRun for a schema it can't read or a keyword it doesn't check."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from check.form import faults
from fault import CantRun

DRAFT_07 = "http://json-schema.org/draft-07/schema#"


@pytest.fixture
def schema(tmp_path: Any):
    """Writes the schema, with draft-07's `$schema`, a title, and a description, as rn's schemas
    carry them, in the case's folder, and gives its path."""

    def written(body: dict[str, Any]) -> str:
        path = os.path.join(str(tmp_path), "form.schema.json")
        given = {"$schema": DRAFT_07, "title": "form", "description": "A form.", **body}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(given, f)
        return path

    return written


def value(text: str) -> Any:
    """The value as JSON reads it."""
    return json.loads(text)


def pointers(found: list[str]) -> list[str]:
    """The JSON Pointer that begins each fault, before its `: `."""
    return sorted(each.split(": ", 1)[0] for each in found)


@pytest.mark.parametrize(
    ("kind", "good", "bad"),
    [
        ("object", '{"a": {}}', '{"a": []}'),
        ("array", '{"a": []}', '{"a": {}}'),
        ("string", '{"a": "x"}', '{"a": 1}'),
        ("integer", '{"a": 1}', '{"a": true}'),
        ("integer", '{"a": -3}', '{"a": 1.5}'),
        ("boolean", '{"a": false}', '{"a": 0}'),
        ("null", '{"a": null}', '{"a": false}'),
    ],
)
def test_a_type_holds_its_own_kind_and_refuses_another(schema, kind: str, good: str, bad: str):
    """Given a schema whose property `a` takes the type, and a value of it and one of another type
    that Python's types confuse with it, such as true for an integer or 0 for a boolean
    When each value is held to it
    Then the first has no fault, and the second one fault at /a"""
    path = schema({"type": "object", "properties": {"a": {"type": kind}}})
    assert faults(value(good), path) == []
    assert pointers(faults(value(bad), path)) == ["/a"]


def test_a_required_property_missing_is_a_fault_naming_it(schema):
    """Given a schema whose object requires `goal` and `work`
    When a value with `work` alone is held to it
    Then it has one fault, naming `goal`"""
    path = schema({"type": "object", "required": ["goal", "work"]})
    assert faults(value('{"goal": 1, "work": 2}'), path) == []
    found = faults(value('{"work": []}'), path)
    assert len(found) == 1
    assert "goal" in found[0]


def test_a_property_no_schema_names_is_a_fault_where_additional_ones_are_refused(schema):
    """Given a schema of an object with the property `a` alone and no additional property
    When a value with `a` and `b` is held to it
    Then it has one fault, naming `b`; and a value with `a` alone has none"""
    path = schema({"type": "object", "additionalProperties": False, "properties": {"a": {}}})
    assert faults(value('{"a": 1}'), path) == []
    found = faults(value('{"a": 1, "b": 2}'), path)
    assert len(found) == 1
    assert "b" in found[0]


@pytest.mark.parametrize("given", ['"The goal."', "[]", "null"])
def test_a_value_not_an_object_where_one_is_taken_has_the_types_fault_alone(schema, given: str):
    """Given a schema whose property `goal` takes an object that requires `decided`, holds it as a
    string, and takes no other property, as the design tree's goal does
    When a value whose `goal` is a string, an array, or null is held to it
    Then it has one fault, at /goal, of its type, as `required`, `properties`, and
    `additionalProperties` hold only of an object"""
    goal = {
        "type": "object",
        "required": ["decided"],
        "additionalProperties": False,
        "properties": {"decided": {"type": "string"}},
    }
    path = schema({"type": "object", "properties": {"goal": goal}})
    assert faults(value(f'{{"goal": {given}}}'), path) == [
        "/goal: takes a value of the type object"
    ]


def test_each_item_of_an_array_is_held_to_items_by_its_index(schema):
    """Given a schema of an array of strings
    When ["x", 2, "y", 3] is held to it
    Then it has a fault at /1 and one at /3"""
    path = schema({"type": "array", "items": {"type": "string"}})
    assert faults(value('["x", "y"]'), path) == []
    assert pointers(faults(value('["x", 2, "y", 3]'), path)) == ["/1", "/3"]


def test_min_items_holds_at_its_limit_and_refuses_one_less(schema):
    """Given a schema whose property `lines` takes at least 1 item
    When [] and ["x"] are held to it
    Then [] has a fault at /lines, and ["x"] none"""
    path = schema({"type": "object", "properties": {"lines": {"type": "array", "minItems": 1}}})
    assert pointers(faults(value('{"lines": []}'), path)) == ["/lines"]
    assert faults(value('{"lines": ["x"]}'), path) == []


def test_min_length_holds_at_its_limit_and_refuses_one_less(schema):
    """Given a schema whose property `good_when` takes at least 1 character
    When "" and "x" are held to it
    Then "" has a fault at /good_when, and "x" none"""
    path = schema(
        {"type": "object", "properties": {"good_when": {"type": "string", "minLength": 1}}}
    )
    assert pointers(faults(value('{"good_when": ""}'), path)) == ["/good_when"]
    assert faults(value('{"good_when": "x"}'), path) == []


def test_minimum_holds_at_its_limit_and_refuses_one_less(schema):
    """Given a schema whose property `number` takes an integer of 1 at least
    When 0, 1, and 2 are held to it
    Then 0 has a fault at /number, and 1 and 2 none"""
    path = schema({"type": "object", "properties": {"number": {"type": "integer", "minimum": 1}}})
    assert pointers(faults(value('{"number": 0}'), path)) == ["/number"]
    assert faults(value('{"number": 1}'), path) == []
    assert faults(value('{"number": 2}'), path) == []


def test_a_pattern_is_searched_anywhere_in_the_string(schema):
    """Given a schema whose property `a` takes a string with the pattern `b`
    When "abc" and "acd" are held to it
    Then "abc" has no fault, as draft-07 doesn't anchor a pattern, and "acd" one at /a"""
    path = schema({"type": "object", "properties": {"a": {"type": "string", "pattern": "b"}}})
    assert faults(value('{"a": "abc"}'), path) == []
    assert pointers(faults(value('{"a": "acd"}'), path)) == ["/a"]


def test_an_enum_out_of_its_values_says_each_value_it_takes(schema):
    """Given a schema whose goal's `by` takes one of user, reasoning, and research
    When a value whose /goal/by is `nobody` is held to it
    Then it has the one fault `/goal/by: takes one of user, reasoning, research`, as check/form.py's
    contract words it"""
    by = {"enum": ["user", "reasoning", "research"]}
    path = schema({"type": "object", "properties": {"goal": {"properties": {"by": by}}}})
    assert faults(value('{"goal": {"by": "user"}}'), path) == []
    assert faults(value('{"goal": {"by": "nobody"}}'), path) == [
        "/goal/by: takes one of user, reasoning, research"
    ]


def test_a_const_takes_its_one_value(schema):
    """Given a schema whose property `status` takes the const `done`
    When "done" and "Done" are held to it
    Then "done" has no fault, and "Done" one at /status"""
    path = schema({"type": "object", "properties": {"status": {"const": "done"}}})
    assert faults(value('{"status": "done"}'), path) == []
    assert pointers(faults(value('{"status": "Done"}'), path)) == ["/status"]


def test_one_of_takes_a_value_that_holds_exactly_one_branch(schema):
    """Given a schema whose property `a` takes one of an integer or a value of 0 at least
    When -1, 1, and "x" are held to it
    Then -1 has no fault, holding the first alone, 1 a fault, holding both, and "x" no fault,
    holding the second alone, as a string meets `minimum` vacuously"""
    path = schema(
        {"type": "object", "properties": {"a": {"oneOf": [{"type": "integer"}, {"minimum": 0}]}}}
    )
    assert faults(value('{"a": -1}'), path) == []
    assert pointers(faults(value('{"a": 1}'), path)) == ["/a"]
    assert faults(value('{"a": "x"}'), path) == []


def test_any_of_takes_a_value_that_holds_one_branch_or_more(schema):
    """Given a schema whose property `a` takes any of a string or an integer
    When "x", 1, and null are held to it
    Then "x" and 1 have no fault, and null one at /a"""
    path = schema(
        {
            "type": "object",
            "properties": {"a": {"anyOf": [{"type": "string"}, {"type": "integer"}]}},
        }
    )
    assert faults(value('{"a": "x"}'), path) == []
    assert faults(value('{"a": 1}'), path) == []
    assert pointers(faults(value('{"a": null}'), path)) == ["/a"]


def test_a_ref_into_defs_holds_the_value_to_the_definition(schema):
    """Given a schema whose property `by` refers to #/$defs/by, an enum of user and maker
    When "user" and "someone" are held to it
    Then "user" has no fault, and "someone" one at /by"""
    path = schema(
        {
            "type": "object",
            "properties": {"by": {"$ref": "#/$defs/by"}},
            "$defs": {"by": {"enum": ["user", "maker"]}},
        }
    )
    assert faults(value('{"by": "user"}'), path) == []
    assert pointers(faults(value('{"by": "someone"}'), path)) == ["/by"]


@pytest.mark.parametrize(("key", "pointer"), [("a/b", "/a~1b"), ("a~b", "/a~0b")])
def test_a_fault_under_a_key_with_a_slash_or_a_tilde_is_escaped_in_its_pointer(
    schema, key: str, pointer: str
):
    """Given a schema whose object's every property takes a string, by additionalProperties
    When a value whose key holds `/` or `~` maps to 1
    Then its one fault's pointer escapes the key as JSON Pointer does"""
    path = schema({"type": "object", "additionalProperties": {"type": "string"}})
    assert pointers(faults({key: 1}, path)) == [pointer]


def test_several_faults_are_each_given(schema):
    """Given a schema of an object requiring `result`, with `good` an array of strings and no
    additional property
    When a value lacking `result`, with good [1, 2] and an extra key, is held to it
    Then it has four faults: one naming result, one at /good/0, one at /good/1, and one naming
    the extra key"""
    path = schema(
        {
            "type": "object",
            "required": ["result"],
            "additionalProperties": False,
            "properties": {"result": {}, "good": {"type": "array", "items": {"type": "string"}}},
        }
    )
    found = faults(value('{"good": [1, 2], "extra": 0}'), path)
    assert len(found) == 4
    assert "/good/0" in pointers(found) and "/good/1" in pointers(found)
    assert any("result" in each for each in found) and any("extra" in each for each in found)


def test_the_walkthroughs_design_tree_holds_the_design_tree_schema():
    """Given the walkthrough's design tree, read from JSON
    When it is held to design-tree.schema.json
    Then it has no fault"""
    tree = json.loads(json.dumps(rn_files.walkthrough_tree("20261120-a-command-with-which-the")))
    assert faults(tree, rn_files.TREE_SCHEMA) == []


def test_a_decision_stating_its_date_leaves_the_design_tree_schema():
    """Given the walkthrough's design tree whose command's N1 holds a decision that names its date
    When it is held to design-tree.schema.json
    Then each fault lies under /deliverables/1, the command, where anyOf joins the forms that the
    decision and the deliverable may take"""
    tree = rn_files.walkthrough_tree(
        "20261120-a-command-with-which-the",
        command_decisions={"N1": [rn_files.decision("the tax rate", "Each invoice, 2026-11-20.")]},
    )
    found = pointers(faults(json.loads(json.dumps(tree)), rn_files.TREE_SCHEMA))
    assert found
    assert all(each.startswith("/deliverables/1/") for each in found)


@pytest.mark.parametrize(
    ("name", "written"),
    [
        ("generator-round", rn_files.made([("N1", ["print"])], ["invoicer/__main__.py"])),
        ("generator-round", rn_files.point()),
        ("evaluator-round", rn_files.judged([("N1", ["print"])], [("N2", "They print it.")])),
    ],
)
def test_each_roles_result_holds_its_schema(name: str, written: Any):
    """Given a role's result of each class, read from JSON
    When it is held to its schema in domain/schemas/
    Then it has no fault"""
    path = os.path.join(rn_files.SCHEMAS, f"{name}.schema.json")
    assert faults(json.loads(json.dumps(written)), path) == []


def test_a_generators_result_of_another_word_leaves_its_schema():
    """Given a generator's result `done`, read from JSON
    When it is held to generator-round.schema.json
    Then it has the one fault `/result: takes one of made, point`"""
    path = os.path.join(rn_files.SCHEMAS, "generator-round.schema.json")
    assert faults({"result": "done"}, path) == ["/result: takes one of made, point"]


def test_a_keyword_it_doesnt_check_is_refused_naming_it(schema):
    """Given a schema whose property `a` uses maxLength, a keyword that none of rn's schemas uses
    When a value is held to it
    Then it raises CantRun naming maxLength"""
    path = schema({"type": "object", "properties": {"a": {"type": "string", "maxLength": 3}}})
    with pytest.raises(CantRun, match="maxLength"):
        faults({"a": "x"}, path)


def test_a_schema_that_cant_be_read_is_refused_naming_it(tmp_path: Any):
    """Given a path where no schema lies, and a schema that isn't JSON
    When a value is held to each
    Then each raises CantRun naming its file"""
    missing = os.path.join(str(tmp_path), "missing.schema.json")
    with pytest.raises(CantRun, match="missing.schema.json"):
        faults({}, missing)
    broken = os.path.join(str(tmp_path), "broken.schema.json")
    with open(broken, "w", encoding="utf-8") as f:
        f.write("{not json")
    with pytest.raises(CantRun, match="broken.schema.json"):
        faults({}, broken)

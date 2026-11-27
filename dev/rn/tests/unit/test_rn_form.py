"""The unit cases of form.py, the check of a JSON value against one of rn's schemas: a value that
holds to it, each keyword's fault, a reference within the schema and to another beside it, and a
schema with a keyword that the check doesn't know, which it refuses."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from form import faults

STEERING = os.path.join(rn_files.RN, "domain", "schemas", "steering.schema.json")


def schema(tmp_path: Any, value: dict[str, Any], name: str = "s.schema.json") -> str:
    path = os.path.join(str(tmp_path), name)
    rn_files.write_json(path, value)
    return path


def test_a_steering_that_holds_to_its_schema_has_no_fault() -> None:
    """Given a steering in the schema's form, with an opportunity under another and a solution.
    When it's checked against steering.schema.json.
    Then no fault is named."""
    assert faults(rn_files.steering(), STEERING) == []


def test_each_keyword_names_its_fault_by_where_it_lies() -> None:
    """Given a steering with a field missing, one too many, a wrong type, a value outside its
    enum, an empty string, an id out of its pattern, and a solution of neither form.
    When it's checked against steering.schema.json.
    Then each fault is named by its JSON Pointer and what it takes."""
    value = rn_files.steering()
    del value["ost"]["questions"]
    value["ost"]["extra"] = 1
    value["ost"]["target"] = 3
    value["state"]["steps"][0]["status"] = "waiting"
    value["ost"]["outcome"] = ""
    value["ost"]["opportunities"][0]["id"] = "X1"
    value["ost"]["opportunities"][0]["solution"] = {"solution": "s"}
    assert faults(value, STEERING) == [
        "/ost/questions: is required",
        "/ost/outcome: takes at least 1 character",
        "/ost/opportunities/0/id: takes the form ^O\\d+(\\.\\d+)*$",
        "/ost/opportunities/0/solution: takes exactly one of its 2 forms, and holds 0",
        "/ost/target: takes string or null",
        "/ost/extra: isn't a field of this form",
        "/state/steps/0/status: takes one of open, trying, done",
    ]


def test_a_value_of_the_wrong_type_at_the_top_is_named_by_a_slash() -> None:
    """Given a list where the schema takes an object.
    When it's checked.
    Then the fault names `/`."""
    assert faults([], STEERING) == ["/: takes object"]


def test_a_bool_is_no_integer() -> None:
    """Given true where the steering's schema takes an issue's number.
    When it's checked.
    Then it's named, as JSON holds a bool apart from a number."""
    issues = rn_files.steering()
    issues["state"]["issues"]["closes"] = [True]
    assert faults(issues, STEERING) == ["/state/issues/closes/0: takes integer"]


def test_a_boolean_takes_a_bool(tmp_path: Any) -> None:
    """Given a schema that takes a boolean.
    When true and 1 are checked.
    Then true holds and 1 is named."""
    path = schema(tmp_path, {"type": "boolean"})
    assert (faults(True, path), faults(1, path)) == ([], ["/: takes boolean"])


def test_a_reference_to_another_schema_beside_it_is_followed(tmp_path: Any) -> None:
    """Given a schema whose field refers to the outcome of the steering's schema beside it.
    When a value with an empty outcome is checked.
    Then the fault is the other schema's."""
    rn_files.write_json(os.path.join(str(tmp_path), "steering.schema.json"), rn_files.schema())
    path = schema(
        tmp_path,
        {
            "type": "object",
            "properties": {
                "o": {"$ref": "steering.schema.json#/properties/ost/properties/outcome"}
            },
        },
    )
    assert faults({"o": ""}, path) == ["/o: takes at least 1 character"]


def test_a_schema_with_a_keyword_it_does_not_check_is_refused(tmp_path: Any) -> None:
    """Given a schema that uses `maximum`.
    When a value is checked against it.
    Then the check refuses the schema, naming the keyword, rather than pass it unchecked."""
    path = schema(tmp_path, {"type": "integer", "maximum": 3})
    with pytest.raises(ValueError, match="maximum"):
        faults(5, path)


def test_a_field_beyond_the_form_passes_where_the_schema_allows_others(tmp_path: Any) -> None:
    """Given a schema of an object that names one field and doesn't forbid others.
    When an object with that field and another is checked.
    Then no fault is named, as JSON Schema allows other fields unless it says otherwise."""
    path = schema(tmp_path, {"type": "object", "properties": {"a": {"type": "string"}}})
    assert faults({"a": "x", "b": 1}, path) == []


def test_a_constant_and_a_count_of_items_name_their_faults(tmp_path: Any) -> None:
    """Given a schema of an object whose word is the constant fixed and whose lines hold one at
    least.
    When an object with another word and no line is checked.
    Then each is named."""
    path = schema(
        tmp_path,
        {
            "type": "object",
            "properties": {"result": {"const": "fixed"}, "lines": {"type": "array", "minItems": 1}},
        },
    )
    assert faults({"result": "made", "lines": []}, path) == [
        "/result: takes fixed",
        "/lines: takes at least 1 item",
    ]

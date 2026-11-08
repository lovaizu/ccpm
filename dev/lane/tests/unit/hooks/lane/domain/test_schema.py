"""The cases of schema.py's contract: `checked` reads a schema of the keywords that structured
outputs accept and refuses any other, and `held` gives the one point at which a value is out of a
schema."""

import unittest

from helpers import schema


def told(given, value):
    """What `held` says of the value, or None where the value holds."""
    found = schema.held(given, value)
    return found.told() if found else None


def refusal(given):
    """What `checked` says of the schema, or None where it reads the schema whole."""
    try:
        schema.checked(given)
    except schema.Unread as why:
        return str(why)
    return None


class TestChecked(unittest.TestCase):
    def test_a_schema_of_every_keyword_structured_outputs_accept_is_read(self):
        given = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "entry",
            "description": "an entry",
            "type": "object",
            "required": ["version"],
            "additionalProperties": False,
            "properties": {
                "version": {"type": "string", "pattern": "^[0-9.]+$", "default": "1"},
                "kind": {"enum": ["Added", 1, True, None]},
                "lines": {"type": "array", "items": {"$ref": "#/$defs/line"}, "minItems": 1},
                "old": {"type": "array", "minItems": 0, "items": {"$ref": "#/definitions/old"}},
                "draft": {"const": False},
                "note": {"anyOf": [{"type": "string"}, {"type": ["integer", "null"]}]},
                "both": {"allOf": [{"type": "number"}, {"type": "integer"}]},
            },
            "$defs": {"line": {"type": "string"}},
            "definitions": {"old": {"type": "boolean"}},
        }
        self.assertIsNone(refusal(given))

    def test_a_schema_that_is_no_object_is_refused(self):
        self.assertEqual(refusal([]), "$: expected a schema object, found []")

    def test_a_keyword_outside_structured_outputs_is_refused(self):
        self.assertEqual(
            refusal({"properties": {"n": {"type": "integer", "minimum": 1}}}),
            "$.properties.n: `minimum` is no keyword that Lane reads in a form",
        )

    def test_format_is_refused_as_lane_checks_no_format(self):
        self.assertEqual(
            refusal({"type": "string", "format": "date"}),
            "$: `format` is no keyword that Lane reads in a form",
        )

    def test_a_type_of_no_basic_name_is_refused(self):
        self.assertEqual(
            refusal({"type": "text"}),
            '$.type: expected a basic type or a list of them, found "text"',
        )

    def test_additional_properties_other_than_false_is_refused(self):
        self.assertEqual(
            refusal({"type": "object", "additionalProperties": True}),
            "$.additionalProperties: expected false, found true",
        )

    def test_min_items_above_one_is_refused(self):
        self.assertEqual(
            refusal({"type": "array", "minItems": 2}),
            "$.minItems: expected 0 or 1, found 2",
        )

    def test_an_enum_holding_an_object_is_refused(self):
        self.assertEqual(
            refusal({"enum": ["a", {"b": 1}]}),
            '$.enum: expected a list of strings, numbers, booleans or nulls, found ["a", {"b": 1}]',
        )

    def test_a_ref_within_all_of_is_refused(self):
        self.assertEqual(
            refusal({"allOf": [{"$ref": "#"}]}),
            "$.allOf[0]: expected a schema without $ref, as structured outputs take none in allOf",
        )

    def test_a_ref_outside_the_schema_is_refused(self):
        self.assertEqual(
            refusal({"$ref": "http://example.com/s.json"}),
            "$.$ref: expected #, #/$defs/<name> or #/definitions/<name>, found"
            ' "http://example.com/s.json"',
        )

    def test_a_ref_to_a_definition_not_there_is_refused(self):
        self.assertEqual(
            refusal({"$ref": "#/$defs/line"}),
            "$.$ref: #/$defs/line points to nothing in the schema",
        )

    def test_a_ref_that_comes_back_to_itself_is_refused(self):
        self.assertEqual(
            refusal({"$defs": {"a": {"items": {"$ref": "#/$defs/a"}}}, "$ref": "#/$defs/a"}),
            "$.$defs.a.items.$ref: #/$defs/a comes back to itself, and structured outputs take no"
            " recursive schema",
        )

    def test_required_that_is_no_list_of_names_is_refused(self):
        self.assertEqual(
            refusal({"required": "a"}),
            '$.required: expected a list of key names, found "a"',
        )

    def test_a_pattern_python_cannot_read_is_refused(self):
        self.assertEqual(
            refusal({"pattern": "("}),
            '$.pattern: expected a regular expression, found "("',
        )

    def test_properties_that_are_no_object_are_refused(self):
        self.assertEqual(
            refusal({"properties": []}),
            "$.properties: expected an object of schemas, found []",
        )

    def test_items_that_are_no_schema_are_refused(self):
        self.assertEqual(refusal({"items": 1}), "$.items: expected a schema object, found 1")

    def test_any_of_that_is_no_list_is_refused(self):
        self.assertEqual(
            refusal({"anyOf": {}}),
            "$.anyOf: expected a list of schemas, found {}",
        )

    def test_all_of_that_is_no_list_is_refused(self):
        self.assertEqual(
            refusal({"allOf": {}}),
            "$.allOf: expected a list of schemas, found {}",
        )

    def test_definitions_that_are_no_object_are_refused(self):
        self.assertEqual(
            refusal({"$defs": []}),
            "$.$defs: expected an object of schemas, found []",
        )


class TestHeld(unittest.TestCase):
    def test_a_value_that_holds_gives_none(self):
        self.assertIsNone(told({"type": "object", "properties": {"a": {"type": "string"}}}, {}))

    def test_a_value_holding_its_required_keys_and_items_gives_none(self):
        given = {"required": ["a"], "properties": {"a": {"items": {"type": "string"}}}}
        self.assertIsNone(told(given, {"a": ["x", "y"]}))

    def test_a_const_list_tells_true_apart_from_one_in_each_item(self):
        self.assertEqual(told({"const": [1]}, [True]), "$: expected [1], found [true]")

    def test_a_const_object_holds_an_equal_object(self):
        self.assertIsNone(told({"const": {"a": [1, "b"]}}, {"a": [1.0, "b"]}))

    def test_a_const_object_is_out_by_a_value_of_another_key(self):
        self.assertEqual(
            told({"const": {"a": 1}}, {"a": 2}), '$: expected {"a": 1}, found {"a": 2}'
        )

    def test_a_value_of_another_type_is_out_at_its_place(self):
        self.assertEqual(told({"type": "string"}, 3), "$: expected a string, found 3")

    def test_a_value_of_none_of_several_types_names_each(self):
        self.assertEqual(
            told({"type": ["string", "null"]}, 3),
            "$: expected a string or null, found 3",
        )

    def test_a_number_with_no_fraction_is_an_integer(self):
        self.assertIsNone(told({"type": "integer"}, 1.0))

    def test_a_boolean_is_no_integer(self):
        self.assertEqual(told({"type": "integer"}, True), "$: expected an integer, found true")

    def test_a_boolean_is_no_number(self):
        self.assertEqual(told({"type": "number"}, False), "$: expected a number, found false")

    def test_a_value_outside_the_enum_is_out(self):
        self.assertEqual(
            told({"enum": ["a", "b"]}, "c"),
            '$: expected one of "a", "b", found "c"',
        )

    def test_true_is_not_the_number_one_in_an_enum(self):
        self.assertEqual(told({"enum": [1]}, True), "$: expected one of 1, found true")

    def test_a_value_other_than_the_const_is_out(self):
        self.assertEqual(told({"const": 0}, False), "$: expected 0, found false")

    def test_a_required_key_missing_is_out_at_its_object(self):
        self.assertEqual(
            told({"required": ["name"]}, {}),
            '$: expected the key "name", found an object without it',
        )

    def test_a_key_beside_the_properties_is_out_where_additional_properties_is_false(self):
        self.assertEqual(
            told({"properties": {}, "additionalProperties": False}, {"extra": 1}),
            "$.extra: expected no such key, found 1",
        )

    def test_a_key_beside_the_properties_is_held_to_the_additional_schema(self):
        self.assertEqual(
            told({"additionalProperties": {"type": "string"}}, {"a b": 1}),
            '$["a b"]: expected a string, found 1',
        )

    def test_a_property_is_held_to_its_schema_at_its_place(self):
        self.assertEqual(
            told({"properties": {"a": {"items": {"type": "string"}}}}, {"a": ["x", 2]}),
            "$.a[1]: expected a string, found 2",
        )

    def test_too_few_items_are_out(self):
        self.assertEqual(
            told({"minItems": 2}, ["a"]),
            '$: expected at least 2 items, found ["a"]',
        )

    def test_the_least_count_of_items_holds(self):
        self.assertIsNone(told({"minItems": 2}, ["a", "b"]))

    def test_a_number_below_the_minimum_is_out(self):
        self.assertEqual(told({"minimum": 1}, 0), "$: expected at least 1, found 0")

    def test_the_minimum_itself_holds(self):
        self.assertIsNone(told({"minimum": 1}, 1))

    def test_text_shorter_than_its_least_length_is_out(self):
        self.assertEqual(
            told({"minLength": 1}, ""),
            '$: expected at least 1 character, found ""',
        )

    def test_text_of_its_least_length_holds(self):
        self.assertIsNone(told({"minLength": 1}, "a"))

    def test_text_the_pattern_does_not_match_is_out(self):
        self.assertEqual(
            told({"pattern": "^[a-z]+$"}, "A"),
            '$: expected text matching ^[a-z]+$, found "A"',
        )

    def test_a_pattern_matches_anywhere_in_the_text(self):
        self.assertIsNone(told({"pattern": "b"}, "abc"))

    def test_a_value_out_of_every_branch_of_any_of_is_out_by_the_branch_reaching_deepest(self):
        given = {"anyOf": [{"type": "string"}, {"properties": {"a": {"type": "string"}}}]}
        self.assertEqual(told(given, {"a": 1}), "$.a: expected a string, found 1")

    def test_a_value_out_of_every_branch_at_one_depth_is_out_by_the_first(self):
        self.assertEqual(
            told({"anyOf": [{"type": "string"}, {"type": "null"}]}, 1),
            "$: expected a string, found 1",
        )

    def test_a_value_out_of_one_schema_of_all_of_is_out(self):
        self.assertEqual(
            told({"allOf": [{"type": "number"}, {"type": "integer"}]}, 1.5),
            "$: expected an integer, found 1.5",
        )

    def test_a_ref_is_followed_within_the_schema(self):
        given = {"$defs": {"n": {"type": "integer"}}, "items": {"$ref": "#/$defs/n"}}
        self.assertEqual(told(given, ["x"]), '$[0]: expected an integer, found "x"')

    def test_a_ref_to_the_whole_schema_is_followed(self):
        given = {"type": "array", "items": {"anyOf": [{"type": "string"}, {"$ref": "#"}]}}
        self.assertEqual(told(given, [["a", 1]]), "$[0][1]: expected a string, found 1")

    def test_a_long_value_found_is_cut_short(self):
        self.assertEqual(
            told({"type": "string"}, list(range(30))),
            "$: expected a string, found [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1...",
        )

    def test_the_out_point_keeps_its_place_as_keys_and_indexes(self):
        found = schema.held({"items": {"properties": {"k": {"type": "string"}}}}, [{"k": 1}])
        self.assertEqual(found.path if found else None, (0, "k"))

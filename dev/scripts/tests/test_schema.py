"""The unit tests of schema.py: `checked` reads only the keywords, in the forms, that the schemas of
dev/scripts use, and refuses any other, naming the place; `held` gives the one point a value is out
of a schema by, the highest in the value first, its place, what was expected, and what was found,
cut at 40 characters, or None where it holds."""

from __future__ import annotations

import unittest

import schema
from schema import Out


def out(form: dict, value) -> Out | None:
    """The point the value is out of the form by, once `checked` read the form whole."""
    schema.checked(form)
    return schema.held(form, value)


class TypeTest(unittest.TestCase):
    def test_a_value_other_than_an_object_is_out_of_the_type_object(self):
        self.assertIsNone(out({"type": "object"}, {}))
        self.assertEqual(out({"type": "object"}, []), Out((), "an object", "[]"))

    def test_a_value_other_than_an_array_is_out_of_the_type_array(self):
        self.assertIsNone(out({"type": "array"}, []))
        self.assertEqual(out({"type": "array"}, {}), Out((), "an array", "{}"))

    def test_a_value_other_than_a_string_is_out_of_the_type_string(self):
        self.assertIsNone(out({"type": "string"}, "a"))
        self.assertEqual(out({"type": "string"}, 1), Out((), "a string", "1"))

    def test_a_value_other_than_a_whole_number_is_out_of_the_type_integer(self):
        self.assertIsNone(out({"type": "integer"}, 3))
        self.assertEqual(out({"type": "integer"}, 1.5), Out((), "an integer", "1.5"))

    def test_a_boolean_is_no_integer(self):
        self.assertEqual(out({"type": "integer"}, True), Out((), "an integer", "true"))

    def test_a_value_other_than_a_boolean_is_out_of_the_type_boolean(self):
        self.assertIsNone(out({"type": "boolean"}, False))
        self.assertEqual(out({"type": "boolean"}, 0), Out((), "a boolean", "0"))

    def test_a_value_other_than_null_is_out_of_the_type_null(self):
        self.assertIsNone(out({"type": "null"}, None))
        self.assertEqual(out({"type": "null"}, 0), Out((), "null", "0"))


class HeldTest(unittest.TestCase):
    def test_a_string_out_of_the_enum_is_out_by_its_values(self):
        self.assertIsNone(out({"enum": ["a", "b"]}, "b"))
        self.assertEqual(out({"enum": ["a", "b"]}, "c"), Out((), 'one of "a", "b"', '"c"'))

    def test_a_value_other_than_the_const_is_out_by_it(self):
        self.assertIsNone(out({"const": "a"}, "a"))
        self.assertEqual(out({"const": "a"}, "b"), Out((), '"a"', '"b"'))

    def test_a_missing_key_named_is_the_first_one_required(self):
        self.assertEqual(
            out({"required": ["a", "b"]}, {}), Out((), 'the key "a"', "an object without it")
        )

    def test_an_extra_key_named_is_the_first_one_beyond_the_properties(self):
        form = {"properties": {"a": {}}, "additionalProperties": False}

        self.assertIsNone(out(form, {"a": 1}))
        self.assertEqual(
            out(form, {"a": 1, "x": 1, "y": 2}), Out((), 'only the keys "a"', 'the key "x"')
        )

    def test_an_extra_key_beside_no_properties_is_out_as_no_key_is_known(self):
        self.assertEqual(
            out({"additionalProperties": False}, {"x": 1}),
            Out((), "only the keys none", 'the key "x"'),
        )

    def test_a_value_out_under_a_property_is_out_at_its_key(self):
        form = {"properties": {"a": {"type": "string"}}}

        self.assertEqual(out(form, {"a": 1}), Out(("a",), "a string", "1"))

    def test_an_item_out_is_out_at_its_index(self):
        form = {"items": {"type": "string"}}

        self.assertEqual(out(form, ["a", 1]), Out((1,), "a string", "1"))

    def test_a_list_shorter_than_min_items_is_out(self):
        self.assertIsNone(out({"minItems": 1}, ["a"]))
        self.assertEqual(out({"minItems": 1}, []), Out((), "1 or more items", "0"))

    def test_a_string_shorter_than_min_length_is_out(self):
        self.assertIsNone(out({"minLength": 2}, "ab"))
        self.assertEqual(out({"minLength": 2}, "a"), Out((), "a string of length 2 or more", '"a"'))

    def test_a_number_below_the_minimum_is_out(self):
        self.assertIsNone(out({"minimum": 1}, 1))
        self.assertEqual(out({"minimum": 1}, 0), Out((), "a number of at least 1", "0"))

    def test_a_boolean_is_no_number_that_the_minimum_holds(self):
        self.assertIsNone(out({"minimum": 2}, True))

    def test_a_string_with_the_pattern_nowhere_in_it_is_out(self):
        self.assertIsNone(out({"pattern": "b"}, "abc"))
        self.assertEqual(out({"pattern": "^b"}, "abc"), Out((), "a string matching ^b", '"abc"'))

    def test_each_keyword_of_one_type_holds_a_value_of_another(self):
        form = {
            "required": ["a"],
            "properties": {"a": {"type": "string"}},
            "additionalProperties": False,
            "items": {"type": "string"},
            "minItems": 1,
            "minLength": 1,
            "minimum": 1,
            "pattern": "^a",
        }

        self.assertIsNone(out(form, None))

    def test_a_ref_holds_the_value_to_the_entry_of_defs_it_names(self):
        form = {"items": {"$ref": "#/$defs/name"}, "$defs": {"name": {"type": "string"}}}

        self.assertEqual(out(form, [1]), Out((0,), "a string", "1"))

    def test_a_value_that_goes_into_no_choice_of_any_of_holds_to_none(self):
        form = {"anyOf": [{"type": "string"}, {"type": "integer"}]}

        self.assertIsNone(out(form, 1))
        self.assertEqual(out(form, []), Out((), "a value of one of its anyOf choices", "[]"))

    def test_a_value_that_goes_into_a_choice_of_any_of_is_out_by_its_point_there(self):
        form = {
            "anyOf": [
                {"type": "object", "properties": {"a": {"type": "string"}}},
                {"type": "integer"},
            ]
        }

        self.assertEqual(out(form, {"a": 1}), Out(("a",), "a string", "1"))

    def test_the_point_highest_in_the_value_comes_first(self):
        form = {"required": ["a"], "properties": {"b": {"type": "string"}}}

        self.assertEqual(out(form, {"b": 1}), Out((), 'the key "a"', "an object without it"))

    def test_the_point_is_told_with_its_place_what_was_expected_and_what_was_found(self):
        told = Out(("deliverables", 0, "path"), "a string", "1").told()

        self.assertEqual(told, "$.deliverables[0].path: expected a string, found 1")


class ShownTest(unittest.TestCase):
    def test_a_value_of_forty_characters_is_shown_whole(self):
        self.assertEqual(schema.shown("x" * 38), '"' + "x" * 38 + '"')

    def test_a_longer_value_is_cut_to_forty_characters_with_dots(self):
        self.assertEqual(schema.shown("x" * 39), '"' + "x" * 36 + "...")

    def test_words_beyond_ascii_are_shown_as_written(self):
        self.assertEqual(schema.shown("請求"), '"請求"')


class CheckedTest(unittest.TestCase):
    """What `checked` refuses in a schema, each by the place and what it reads there."""

    def assert_refused(self, form, words: str) -> None:
        with self.assertRaises(schema.Unread) as caught:
            schema.checked(form)
        self.assertIn(words, str(caught.exception))

    def test_the_schemas_of_rn_are_read_with_their_notes(self):
        schema.checked({"$schema": "x", "title": "x", "description": "x", "type": "object"})

    def test_a_keyword_it_does_not_read_is_refused_with_the_ones_it_reads(self):
        self.assert_refused({"allOf": []}, "$: `allOf` is no keyword it reads; it reads $ref, type")

    def test_a_schema_that_is_no_object_is_refused(self):
        self.assert_refused({"items": True}, "$.items: expected a schema object, found true")

    def test_a_type_of_no_basic_type_is_refused(self):
        self.assert_refused({"type": ["string"]}, "$.type: expected one of object, array")

    def test_properties_that_are_no_object_of_schemas_are_refused(self):
        self.assert_refused({"properties": []}, "$.properties: expected an object of schemas")

    def test_a_schema_it_does_not_read_under_properties_is_refused_at_its_place(self):
        self.assert_refused({"properties": {"a": {"type": "number"}}}, "$.properties.a.type")

    def test_an_any_of_that_is_no_list_of_schemas_is_refused(self):
        self.assert_refused({"anyOf": []}, "$.anyOf: expected a list of schemas")

    def test_a_schema_it_does_not_read_in_any_of_is_refused_at_its_place(self):
        self.assert_refused({"anyOf": [{"type": "number"}]}, "$.anyOf[0].type")

    def test_required_or_an_enum_that_is_no_list_of_strings_is_refused(self):
        self.assert_refused({"enum": [1]}, "$.enum: expected a list of strings")

    def test_additional_properties_other_than_false_is_refused(self):
        self.assert_refused(
            {"additionalProperties": True}, "$.additionalProperties: expected false"
        )

    def test_a_const_other_than_a_string_is_refused(self):
        self.assert_refused({"const": None}, "$.const: expected a string")

    def test_min_items_or_min_length_other_than_a_whole_number_is_refused(self):
        self.assert_refused({"minLength": 1.5}, "$.minLength: expected a whole number")

    def test_a_minimum_other_than_a_number_is_refused(self):
        self.assert_refused({"minimum": "1"}, "$.minimum: expected a number")

    def test_a_boolean_is_no_minimum(self):
        self.assert_refused({"minimum": True}, "$.minimum: expected a number")

    def test_a_pattern_that_is_no_regular_expression_is_refused(self):
        self.assert_refused({"pattern": "("}, "$.pattern: expected a regular expression")

    def test_a_note_beside_a_ref_is_read(self):
        schema.checked({"items": {"$ref": "#/$defs/a", "description": "x"}, "$defs": {"a": {}}})

    def test_a_keyword_beside_a_ref_is_refused(self):
        self.assert_refused(
            {"items": {"$ref": "#/$defs/a", "type": "string"}, "$defs": {"a": {}}},
            "$.items: expected $ref alone",
        )

    def test_a_ref_that_names_no_entry_of_defs_is_refused(self):
        self.assert_refused(
            {"items": {"$ref": "#/$defs/b"}, "$defs": {"a": {}}},
            "$.items.$ref: expected `#/$defs/<name>`",
        )

    def test_a_ref_to_an_entry_with_a_ref_or_any_of_at_its_top_is_refused(self):
        form = {"items": {"$ref": "#/$defs/a"}, "$defs": {"a": {"anyOf": [{"$ref": "#/$defs/a"}]}}}

        self.assert_refused(
            form, "$.items.$ref: expected an entry of $defs with neither $ref nor anyOf"
        )


if __name__ == "__main__":
    unittest.main()

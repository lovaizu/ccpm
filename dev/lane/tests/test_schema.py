"""A JSON Schema of the keywords structured outputs accept: read whole, any other keyword refused, and
a value held to it giving the one point it is out by, its place, what was expected and what was
found."""

import unittest

from helpers import schema

# A schema of each keyword lane reads, as a step's output might be given.
ENTRY = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "entry",
    "type": "object",
    "properties": {
        "version": {"type": "string", "description": "the release"},
        "kind": {"enum": ["Added", "Fixed"]},
        "lines": {"type": "array", "items": {"$ref": "#/$defs/line"}, "minItems": 1},
        "draft": {"const": False, "default": False},
        "note": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    },
    "required": ["version", "kind"],
    "additionalProperties": False,
    "$defs": {"line": {"allOf": [{"type": "string"}, {"enum": ["a", "b"]}]}},
}


def held(value, given=ENTRY):
    """The point the value is out of the schema by, as the subagent is told it; None where it
    holds."""
    schema.checked(given)
    found = schema.held(given, value)
    return found.told() if found else None


class TestRead(unittest.TestCase):
    def test_each_keyword_structured_outputs_accept_is_read(self):
        for given in (
            ENTRY,
            {"type": ["string", "null"]},
            {"definitions": {"a": {"type": "integer"}}, "$ref": "#/definitions/a"},
            {"anyOf": [{"$ref": "#/$defs/a"}], "allOf": [{"items": {}}], "$defs": {"a": {}}},
            {"items": {"type": "number"}, "minItems": 0},
            {"type": "boolean"},
            {"$ref": "#/$defs/a/items", "$defs": {"a": {"items": {}}}},
            {"properties": {"a/b": {"$ref": "#/properties/a~0"}, "a~": {}}},
            {"properties": {"a": {"$ref": "#/properties/b~1c"}, "b/c": {}}},
        ):
            with self.subTest(schema=given):
                # Given: a schema of the keywords structured outputs accept, a list of types and
                # escaped references among them
                # When: it is read
                # Then: it is read whole, nothing refused
                self.assertIsNone(schema.checked(given))

    def test_a_keyword_lane_does_not_read_is_told_with_those_it_reads(self):
        # Given: a schema of a keyword lane does not read
        # When: it is read
        # Then: it is refused, naming each keyword lane reads, so the building AI can write the form
        # in them; a keyword's own refusal names the values it takes
        with self.assertRaises(schema.Unread) as refused:
            schema.checked({"format": "date"})
        self.assertEqual(
            str(refused.exception),
            "$: `format` is no keyword lane reads; it reads $ref, type, enum, const, required,"
            " additionalProperties, minItems, properties, items, allOf, anyOf, $defs and"
            " definitions, as Anthropic's structured outputs accept",
        )

    def test_a_schema_lane_cannot_read_whole_is_refused_naming_the_place(self):
        for given, named in (
            ([], "$: expected a schema object, found []"),
            ({"format": "date"}, "$: `format` is no keyword lane reads"),
            ({"properties": {"a": {"minLength": 1}}}, "$.properties.a: `minLength`"),
            ({"type": "text"}, "$.type: expected one of object"),
            ({"type": []}, "$.type: expected one of"),
            ({"type": ["string", 1]}, "$.type: expected one of"),
            ({"properties": []}, "$.properties: expected an object of schemas"),
            ({"properties": {"a": 1}}, "$.properties.a: expected a schema object, found 1"),
            ({"anyOf": []}, "$.anyOf: expected a list of schemas"),
            ({"allOf": {}}, "$.allOf: expected a list of schemas"),
            ({"anyOf": [{}, 2]}, "$.anyOf[1]: expected a schema object"),
            (
                {"allOf": [{}, {"$ref": "#/$defs/a"}], "$defs": {"a": {}}},
                "$.allOf[1]: expected a schema without $ref, as structured outputs take none in allOf",
            ),
            ({"items": [{}]}, "$.items: expected a schema object"),
            ({"required": "a"}, "$.required: expected a list of keys"),
            ({"required": [1]}, "$.required: expected a list of keys"),
            ({"additionalProperties": True}, "$.additionalProperties: expected false"),
            ({"additionalProperties": {}}, "$.additionalProperties: expected false"),
            ({"additionalProperties": 0}, "$.additionalProperties: expected false"),
            ({"enum": []}, "$.enum: expected a list of strings"),
            ({"enum": "a"}, "$.enum: expected a list of strings"),
            ({"enum": ["a", ["b"]]}, "$.enum: expected a list of strings"),
            ({"const": {"a": 1}}, "$.const: expected a string"),
            ({"minItems": 2}, "$.minItems: expected 0 or 1"),
            ({"minItems": True}, "$.minItems: expected 0 or 1"),
            ({"minItems": -1}, "$.minItems: expected 0 or 1"),
            ({"$ref": "other.json#/a"}, "$.$ref: expected a reference within the schema"),
            ({"$ref": 1}, "$.$ref: expected a reference within the schema"),
            ({"$ref": "#a"}, "$.$ref: expected a reference within the schema"),
            ({"$ref": ""}, "$.$ref: expected a reference within the schema"),
            ({"$ref": "#/$defs/a"}, "$.$ref: #/$defs/a points to nothing"),
            ({"$ref": "#/$defs/a/b", "$defs": {"a": {}}}, "points to nothing"),
            ({"$ref": "#/$defs/a/b", "$defs": {"a": []}}, "points to nothing"),
            ({"$ref": "#/$defs/a", "type": "string", "$defs": {"a": {}}}, "$: expected $ref alone"),
            ({"$defs": {"a": {"$ref": "#"}}}, "# comes back to itself"),
            (
                {"$defs": {"a": {"$ref": "#/$defs/b"}, "b": {"items": {"$ref": "#/$defs/a"}}}},
                "comes back to itself",
            ),
        ):
            with self.subTest(schema=given):
                # Given: a schema using a keyword lane does not read, or one in another shape
                # When: it is read
                # Then: it is refused, naming the place and what is wrong there
                with self.assertRaises(ValueError) as refused:
                    schema.checked(given)
                self.assertIn(named, str(refused.exception))

    def test_a_ref_reached_twice_without_coming_back_is_read(self):
        # Given: two properties referring to one definition, which refers to another
        given = {
            "properties": {"a": {"$ref": "#/$defs/x"}, "b": {"$ref": "#/$defs/x"}},
            "$defs": {"x": {"items": {"$ref": "#/$defs/y"}}, "y": {"type": "string"}},
        }
        # When: it is read
        # Then: it is read whole, as no reference comes back to itself
        self.assertIsNone(schema.checked(given))


class TestHeld(unittest.TestCase):
    def test_a_value_of_the_form_holds(self):
        for value in (
            {"version": "1.0", "kind": "Added"},
            {"version": "1.0", "kind": "Fixed", "lines": ["a", "b"], "draft": False},
            {"version": "1.0", "kind": "Added", "note": None},
            {"version": "1.0", "kind": "Added", "note": "n"},
        ):
            with self.subTest(value=value):
                # Given: the entry's schema
                # When: a value of its form is held to it
                # Then: it holds
                self.assertIsNone(held(value))

    def test_a_value_out_of_the_form_gives_its_place_what_was_expected_and_found(self):
        base = {"version": "1.0", "kind": "Added"}
        for value, told in (
            ([], "$: expected an object, found []"),
            ({"kind": "Added"}, '$: expected the key "version", found an object without it'),
            ({"version": "1"}, '$: expected the key "kind", found an object without it'),
            (
                {**base, "extra": 1},
                (
                    '$: expected only the keys "version", "kind", "lines", "draft", "note",'
                    ' found the key "extra"'
                ),
            ),
            ({**base, "version": 1}, "$.version: expected a string, found 1"),
            (
                {**base, "kind": "Removed"},
                '$.kind: expected one of "Added", "Fixed", found "Removed"',
            ),
            ({**base, "lines": []}, "$.lines: expected at least 1 item, found none"),
            ({**base, "lines": ["a", 3]}, "$.lines[1]: expected a string, found 3"),
            ({**base, "lines": ["a", "c"]}, '$.lines[1]: expected one of "a", "b", found "c"'),
            ({**base, "draft": True}, "$.draft: expected false, found true"),
            ({**base, "draft": 0}, "$.draft: expected false, found 0"),
        ):
            with self.subTest(value=value):
                # Given: the entry's schema
                # When: a value out of its form is held to it
                # Then: the one point it is out by is given, its place first
                self.assertEqual(held(value), told)

    def test_the_point_highest_in_the_value_is_given_first(self):
        # Given: a value missing a key and holding a wrong one below
        value = {"kind": "Added", "lines": [3]}
        # When: it is held to the entry's schema
        # Then: the missing key, higher in the value, is given
        self.assertEqual(held(value), '$: expected the key "version", found an object without it')

    def test_of_several_keys_missing_or_extra_the_first_is_given(self):
        given = {"properties": {"a": {}, "b": {}}, "required": ["a", "b"]}
        for value, told in (
            ({}, '$: expected the key "a", found an object without it'),
            ({"a": 1, "b": 1, "x": 1, "y": 1}, None),
        ):
            with self.subTest(value=value):
                # Given: a schema requiring two keys
                # When: an object without both, or with both and two keys more, is held to it
                # Then: the first key missing is given, and keys more pass where none are barred
                self.assertEqual(held(value, given), told)

    def test_of_several_keys_barred_the_first_is_given(self):
        # Given: a schema requiring two keys and barring every other
        properties: dict = {"a": {}, "b": {}}
        barred = {"properties": properties, "required": ["a", "b"], "additionalProperties": False}
        # When: an object with two keys more is held to it
        # Then: the first of them is given
        self.assertEqual(
            held({"a": 1, "b": 1, "x": 1, "y": 1}, barred),
            '$: expected only the keys "a", "b", found the key "x"',
        )

    def test_min_items_holds_an_array_of_that_many(self):
        for given, value in (({"minItems": 0}, []), ({"minItems": 1}, ["a"])):
            with self.subTest(schema=given, value=value):
                # Given: minItems of 0 or 1
                # When: an array of exactly that many items is held to it
                # Then: it holds
                self.assertIsNone(held(value, given))

    def test_text_found_is_shown_as_written(self):
        # Given: a schema of a number
        # When: a string of letters beyond ASCII is held to it
        # Then: they are shown as written
        self.assertEqual(held("é", {"type": "number"}), '$: expected a number, found "é"')

    def test_each_basic_type_tells_its_values(self):
        for name, good, bad in (
            ("object", {}, []),
            ("array", [], {}),
            ("string", "", 1),
            ("integer", 1, 1.5),
            ("integer", 2.0, True),
            ("number", 1.5, "1"),
            ("number", 1, False),
            ("boolean", False, 0),
            ("null", None, 0),
        ):
            with self.subTest(type=name, good=good, bad=bad):
                # Given: a schema of one basic type
                # When: a value of the type, and one of another, are held to it
                # Then: the first holds, the second is out, as JSON tells them
                self.assertIsNone(held(good, {"type": name}))
                self.assertIsNotNone(held(bad, {"type": name}))

    def test_types_listed_are_named_as_choices(self):
        # Given: a schema of a string or null
        # When: a number is held to it
        # Then: both types are named as expected
        self.assertEqual(
            held(1, {"type": ["string", "null"]}), "$: expected a string or null, found 1"
        )

    def test_enum_and_const_tell_a_boolean_from_a_number(self):
        for given, value, holds in (
            ({"enum": [1]}, True, False),
            ({"enum": [True]}, 1, False),
            ({"const": 1}, 1.0, True),
            ({"const": None}, None, True),
            ({"const": "a"}, "A", False),
        ):
            with self.subTest(schema=given, value=value):
                # Given: an enum or a const
                # When: a value is held to it
                # Then: it holds where JSON has them equal, a boolean being no number
                self.assertEqual(held(value, given) is None, holds)

    def test_a_key_lane_cannot_name_plainly_is_named_in_brackets(self):
        # Given: a schema whose key holds a space
        given = {"properties": {"a b": {"type": "string"}, "_c1": {"type": "string"}}}
        # When: a wrong value is held under each
        # Then: the key with a space is named in brackets, a plain key after a dot
        self.assertEqual(held({"a b": 1}, given), '$["a b"]: expected a string, found 1')
        self.assertEqual(held({"_c1": 1}, given), "$._c1: expected a string, found 1")

    def test_a_long_value_found_is_cut(self):
        # Given: a schema of a number
        # When: a string of 50 letters is held to it
        found = held("x" * 50, {"type": "number"})
        # Then: what was found is shown to its fortieth character, ending in dots
        self.assertEqual(found, '$: expected a number, found "' + "x" * 36 + "...")

    def test_a_value_at_the_length_shown_is_shown_whole(self):
        # Given: a schema of a number
        # When: a string shown in exactly forty characters is held to it
        # Then: it is shown whole
        self.assertEqual(
            held("x" * 38, {"type": "number"}), '$: expected a number, found "' + "x" * 38 + '"'
        )

    def test_extra_keys_where_no_properties_are_named(self):
        # Given: an object schema taking no keys at all
        # When: an object with a key is held to it
        # Then: no key is expected
        self.assertEqual(
            held({"a": 1}, {"additionalProperties": False}),
            '$: expected only the keys none, found the key "a"',
        )

    def test_keywords_of_objects_and_arrays_pass_values_of_other_types(self):
        for given in (
            {"required": ["a"]},
            {"additionalProperties": False},
            {"properties": {"a": {"type": "string"}}},
            {"items": {"type": "string"}},
            {"minItems": 1},
        ):
            with self.subTest(schema=given):
                # Given: a keyword of objects or arrays alone, with no type
                # When: a string is held to it
                # Then: it holds, as draft-07 has such keywords pass other types
                self.assertIsNone(held("s", given))

    def test_a_ref_holds_the_value_to_what_it_points_to(self):
        # Given: a schema whose root refers to a definition
        given = {"$ref": "#/definitions/a", "definitions": {"a": {"type": "integer"}}}
        # When: a string is held to it
        # Then: it is out by the definition's type
        self.assertEqual(held("s", given), '$: expected an integer, found "s"')

    def test_all_of_gives_the_point_of_the_first_choice_out(self):
        # Given: allOf of a string and of an enum
        given = {"allOf": [{"type": "string"}, {"enum": ["a"]}]}
        # When: a string out of the enum, and a number, are held to it
        # Then: each is out by the first choice it fails
        self.assertEqual(held("b", given), '$: expected one of "a", found "b"')
        self.assertEqual(held(1, given), "$: expected a string, found 1")


# anyOf of null and of two objects, one holding a string at `a`, the other a string at `b.c`.
CHOICES = {
    "anyOf": [
        {"type": "null"},
        {"type": "object", "properties": {"a": {"type": "string"}}},
        {"type": "object", "properties": {"b": {"properties": {"c": {"type": "string"}}}}},
    ]
}


class TestAnyOf(unittest.TestCase):
    def test_a_value_of_any_choice_holds(self):
        for value in (None, {"a": "s"}, {"b": {"c": "s"}}):
            with self.subTest(value=value):
                # Given: anyOf of null and two objects
                # When: a value of one choice is held to it
                # Then: it holds
                self.assertIsNone(held(value, CHOICES))

    def test_the_point_of_the_choice_gone_deepest_in_is_given(self):
        # Given: anyOf of null and two objects
        # When: an object wrong one level down for one choice and two levels down for another
        # Then: the point of the choice it went deepest in is given
        self.assertEqual(
            held({"a": 1, "b": {"c": 1}}, CHOICES), "$.b.c: expected a string, found 1"
        )

    def test_of_choices_gone_as_deep_the_first_is_given(self):
        # Given: anyOf of two objects, each wrong one level down
        given = {
            "anyOf": [
                {"properties": {"a": {"type": "string"}}},
                {"properties": {"b": {"type": "string"}}},
            ]
        }
        # When: an object wrong under both is held to it
        # Then: the first choice's point is given
        self.assertEqual(held({"a": 1, "b": 1}, given), "$.a: expected a string, found 1")

    def test_a_value_going_into_no_choice_is_out_of_them_all(self):
        # Given: anyOf of null and two objects
        # When: a number is held to it
        # Then: it is out of every choice, at its own place
        self.assertEqual(
            held(1, CHOICES), "$: expected a value of one of its anyOf choices, found 1"
        )


if __name__ == "__main__":
    unittest.main()

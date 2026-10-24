"""Property-based tests of the forms: any value of a schema's shape holds to it and any value put out
of it is named at its place; frontmatter written as `key: value` lines reads back as written; and a
file of a template's headings holds to it whatever text lies between them; on many inputs Hypothesis
makes, new on every run, CI included."""

import string
import unittest

# Hypothesis is installed on the newest Python alone, so the type check on 3.9 finds it missing.
try:
    from hypothesis import given  # pyrefly: ignore[missing-import]
    from hypothesis import strategies as st  # pyrefly: ignore[missing-import]
except ImportError:
    raise unittest.SkipTest("Hypothesis runs on the newest Python alone") from None

from helpers import schema, template, testing

testing.load_hypothesis_profile()

# A changelog entry: a version, and lines each a kind and a text.
ENTRY = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "lines": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"kind": {"enum": ["Added", "Fixed"]}, "text": {"type": "string"}},
                "required": ["kind", "text"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["version", "lines"],
    "additionalProperties": False,
}
LINES = st.lists(
    st.fixed_dictionaries({"kind": st.sampled_from(["Added", "Fixed"]), "text": st.text()})
)
ENTRIES = st.fixed_dictionaries({"version": st.text(), "lines": LINES})
# A key as the reader takes it plain: a letter, digit or underscore, then those and `.-`.
KEYS = st.from_regex(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,8}", fullmatch=True)
# A plain value: words of letters, digits and `._-`, one blank between them.
PLAIN = st.lists(st.text(string.ascii_letters + string.digits + "._-", min_size=1), max_size=4).map(
    " ".join
)
# Any text on one line.
ONE_LINE = st.text().filter(lambda t: "\n" not in t and "\r" not in t)
# Body text: lines beginning with a letter, so none is a heading, a fence or frontmatter.
BODY = st.lists(st.text(string.ascii_letters + " #`~", min_size=1).map(lambda t: "a" + t))


class TestSchema(unittest.TestCase):
    @given(ENTRIES)
    def test_any_value_of_the_schemas_shape_holds(self, entry):
        # Given: the entry's schema
        # When: any value of its shape is held to it
        # Then: it holds
        self.assertIsNone(schema.held(ENTRY, entry))

    @given(ENTRIES.filter(lambda e: e["lines"]), st.data())
    def test_a_line_text_put_out_of_the_shape_is_named_at_its_place(self, entry, data):
        # Given: any value of the entry's shape with a line
        index = data.draw(st.integers(0, len(entry["lines"]) - 1))
        # When: one line's text is made a number
        entry["lines"][index]["text"] = 1
        # Then: the point is that line's text, a string expected
        self.assertEqual(
            schema.held(ENTRY, entry), schema.Out(("lines", index, "text"), "a string", "1")
        )


class TestFrontmatter(unittest.TestCase):
    @given(st.dictionaries(KEYS, PLAIN))
    def test_plain_values_read_back_as_written(self, values):
        # Given: any keys with plain values
        lines = ["---", *(f"{k}: {v}" for k, v in values.items()), "---"]
        # When: they are written as frontmatter and read
        # Then: each value reads back as written, at its line
        self.assertEqual(
            template.keys(lines),
            {k: (number, v) for number, (k, v) in enumerate(values.items(), start=2)},
        )

    @given(ONE_LINE)
    def test_any_text_in_single_quotes_reads_back_as_written(self, text):
        # Given: any text on one line
        quoted = "'" + text.replace("'", "''") + "'"
        # When: it is written in single quotes, its quotes doubled, and read
        # Then: it reads back as written
        self.assertEqual(template.keys(["---", f"a: {quoted}", "---"]), {"a": (2, text)})


class TestHeadings(unittest.TestCase):
    @given(st.lists(st.tuples(st.integers(1, 6), PLAIN.filter(bool)), min_size=1), BODY)
    def test_a_file_of_the_templates_headings_holds_whatever_lies_between(self, headings, body):
        # Given: a template of any headings
        asked = template.read("".join(f"{'#' * level} {text}\n" for level, text in headings))
        # When: a file of those headings, with the body text before each, is held to it
        written = "".join(
            "".join(f"{line}\n" for line in body) + f"{'#' * level} {text}\n"
            for level, text in headings
        )
        # Then: it holds
        self.assertEqual(template.held(asked, written), "")


if __name__ == "__main__":
    unittest.main()

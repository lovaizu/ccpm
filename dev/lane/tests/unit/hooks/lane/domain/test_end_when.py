"""end_when: a result is given only once an output the lane names is there, named from the folder
the subagent works in."""

import unittest

import helpers
from helpers import end_when


class TestMissing(helpers.PluginTest):
    def missing(self, outputs: list) -> str:
        """What end_when taking the outputs finds missing in base."""
        return end_when.missing({"output": outputs}, helpers.did(self.base, self.plugin))

    def test_an_output_there_is_made(self):
        for made in ("report.md", "out/"):
            with self.subTest(made=made):
                # Given: the output there, a file or a folder
                self.write(made + ("x" if made.endswith("/") else ""), "x")
                # When: the subagent gives its result
                # Then: nothing is missing
                self.assertEqual(self.missing([made]), "")

    def test_none_of_the_outputs_there_is_missing_naming_each(self):
        # Given: neither output there
        # When: the subagent gives its result
        # Then: both are named as not there
        self.assertEqual(self.missing(["a.md", "b.md"]), "`a.md` and `b.md` not there")
        # And: one of them there is enough, as the sentence lists them with or
        self.write("b.md", "x")
        self.assertEqual(self.missing(["a.md", "b.md"]), "")


if __name__ == "__main__":
    unittest.main()

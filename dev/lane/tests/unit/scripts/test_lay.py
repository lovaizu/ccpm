"""lay.py, the command line the user runs: the action and its path read, the layer's
answer printed, or what stopped it, with the exit code a script reads."""

import contextlib
import io
import unittest
from unittest import mock

import helpers
from helpers import lay


class TestMain(helpers.LayTest):
    def ran(self, *argv: str) -> tuple:
        """What lay.py prints, given the words, and the code it gives."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = lay.main(list(argv))
        return code, out.getvalue()

    def test_print_prints_the_proposal_and_gives_0(self):
        # Given: the README's proposal
        # When: lay.py print is run on it
        # Then: it prints what the README shows, and gives 0
        self.assertEqual(self.ran("print", helpers.PROPOSED), (0, helpers.PRINTED))

    def test_write_and_up_run_their_actions(self):
        for action, path, call in (
            ("write", "p.json", "written"),
            ("up", "changelog", "brought_up"),
        ):
            with self.subTest(action=action):
                # Given: the action and its path
                # When: lay.py is run with them
                found = mock.Mock(return_value=f"{call} {path}\n")
                with mock.patch.dict(lay.ACTIONS, {action: found}):
                    said = self.ran(action, path)
                # Then: it runs the action on the path, and prints what it gives
                found.assert_called_once_with(path)
                self.assertEqual(said, (0, f"{call} {path}\n"))

    def test_a_stop_is_printed_and_gives_1(self):
        # Given: no proposal at the path
        # When: lay.py print is run on it
        code, said = self.ran("print", "gone.json")
        # Then: it prints why, and gives 1
        self.assertEqual(code, 1)
        self.assertTrue(said.startswith("lay.py: there is no file gone.json;"))

    def test_words_of_no_action_print_the_usage(self):
        for argv in ((), ("print",), ("show", "p.json"), ("print", "a", "b")):
            with self.subTest(argv=argv):
                # Given: no words, an action without its path, no action, or more words
                # When: lay.py is run with them
                # Then: it prints its usage, as the README shows it, and gives 1
                usage = (
                    "usage: lay.py print <proposal>\n       lay.py write <proposal>\n"
                    "       lay.py up <plugin>\n"
                )
                self.assertEqual(self.ran(*argv), (1, usage))


if __name__ == "__main__":
    unittest.main()

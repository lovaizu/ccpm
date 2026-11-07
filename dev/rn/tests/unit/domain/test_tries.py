"""domain/tries.py, a deliverable's commands run in a throwaway copy with a throwaway home, what
each gave kept in the round's try record."""

from __future__ import annotations

import os
from unittest import mock

import helpers
from helpers import RUN, runs, starts, tries

from unit.domain.test_starts import made

CONTENT = os.path.join(RUN, "turns", "01-readme-md", "01")


class Tried(helpers.RunTest):
    def setUp(self) -> None:
        super().setUp()
        self.lays(helpers.walkthrough())
        os.makedirs(CONTENT)

    def record(self, commands, home=()):
        self.write_json(
            os.path.join(CONTENT, runs.MADE), {**made(commands=commands), "home": list(home)}
        )

    def test_each_command_runs_in_the_copy_with_the_home_and_reaches_no_own_file(self):
        self.record(
            ["cat README.md", "echo moved > README.md; ls ~/Downloads; exit 3"],
            home=["Downloads/a.jpg"],
        )
        path = tries.tried(RUN)
        said = self.read(path)
        self.assertEqual(path, os.path.join(CONTENT, runs.TRY))
        self.assertEqual(
            said,
            f"$ cat README.md\n{helpers.TIDY['README.md']}(exit 0)\n"
            "$ echo moved > README.md; ls ~/Downloads; exit 3\na.jpg\n(exit 3)\n",
        )
        self.assertEqual(self.read("README.md"), helpers.TIDY["README.md"])
        self.assertFalse(os.path.exists(os.path.join(runs.temporary(RUN), "try")))

    def test_a_command_that_runs_too_long_is_stopped(self):
        self.record(["echo begun; sleep 5"])
        with mock.patch.object(tries, "SECONDS", 0.5):
            said = self.read(tries.tried(RUN))
        self.assertEqual(said, "$ echo begun; sleep 5\nbegun\n(stopped after 0.5 seconds)\n")

    def test_no_command_is_said_so(self):
        self.record([])
        self.assertEqual(self.read(tries.tried(RUN)), "No command tries the deliverable.\n")

    def test_a_file_out_of_the_home_or_no_record_runs_nothing(self):
        for home in (["/etc/x"], ["../x"], ["."]):
            with self.subTest(home=home):
                self.record(["touch ran"], home=home)
                with self.assertRaises(starts.Stop):
                    tries.tried(RUN)
        self.assertFalse(os.path.exists(os.path.join(CONTENT, runs.TRY)))
        os.remove(os.path.join(CONTENT, runs.MADE))
        with self.assertRaises(starts.Stop) as stop:
            tries.tried(RUN)
        self.assertIn("has no round with a Making record to try", str(stop.exception))
        self.lays({"goal": helpers.walkthrough()["goal"], "deliverables": []})
        with self.assertRaises(starts.Stop):
            tries.tried(RUN)


class Edges(helpers.RunTest):
    def setUp(self) -> None:
        super().setUp()
        self.lays(helpers.walkthrough())
        os.makedirs(CONTENT)

    def test_two_files_out_of_the_home_name_the_first(self):
        self.write_json(
            os.path.join(CONTENT, runs.MADE), {**made(commands=["true"]), "home": ["/a", "/b"]}
        )
        with self.assertRaises(starts.Stop) as stop:
            tries.tried(RUN)
        self.assertEqual(str(stop.exception), "the file /a lies out of the home")

    def test_two_files_in_one_folder_and_a_link_to_nothing(self):
        os.symlink("gone", "dangling")
        self.write_json(
            os.path.join(CONTENT, runs.MADE),
            {**made(commands=["ls ~/Downloads"]), "home": ["Downloads/a", "Downloads/b"]},
        )
        self.assertIn("a\nb\n(exit 0)", self.read(tries.tried(RUN)))

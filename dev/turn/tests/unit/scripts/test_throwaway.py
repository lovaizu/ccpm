"""scripts/throwaway.py, what the generator and the evaluator run the work's commands by: each
command of the work the run is at, in order, in one throwaway copy of the folder it is run in, a
throwaway home as HOME holding each file the work names, both removed after, each command and what
it printed shown, giving 0; or why it could not, giving 2."""

import contextlib
import io
import os
import queue
import runpy
import shutil
import subprocess
import sys
import threading
import unittest
from unittest import mock

import helpers
from helpers import throwaway

USAGE = "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py <run>\n"


def put_each(stream, lines):
    """Puts each line read from the stream into the queue, as it comes."""
    for line in stream:
        lines.put(line)


class TestMain(helpers.RepositoryTest):
    def setUp(self) -> None:
        super().setUp()
        self.write("tidy.py", "print('tidy')\n")
        self.seen = os.path.join(os.path.dirname(self.base), os.path.basename(self.base) + "-seen")
        os.makedirs(self.seen)
        self.addCleanup(shutil.rmtree, self.seen)

    def lays(self, commands, made=()):
        """The Run of one work whose user runs the commands, on the files made under the home."""
        self.lay_run([helpers.work(commands=list(commands), files=list(made))])

    def ran(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = throwaway.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def said(self, name):
        return self.read(os.path.join(self.seen, name)).strip()

    def test_each_command_runs_in_order_in_one_copy_with_a_home_holding_each_file(self):
        # Given: a work whose user lists their Downloads, then makes a file, then reads it
        self.lays(
            [
                f"ls ~/Downloads > {self.seen}/ls; echo $HOME > {self.seen}/home",
                f"pwd > {self.seen}/pwd; cat tidy.py > {self.seen}/tidy; touch made",
                f"ls made > {self.seen}/made; echo sorted",
            ],
            ["Downloads/a.jpg", "Downloads/b"],
        )
        before = sorted(os.listdir(self.base))
        # When: the commands are run
        code, out, err = self.ran(helpers.RUN)
        # Then: it gives 0; they saw the files under their own home, ran in one copy of the
        # repository, and each is shown with what it printed and its exit code
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.said("ls").split(), ["a.jpg", "b"])
        self.assertNotEqual(self.said("home"), os.environ.get("HOME"))
        self.assertEqual((self.said("tidy"), self.said("made")), ("print('tidy')", "made"))
        self.assertNotEqual(self.said("pwd"), self.base)
        self.assertIn(f"$ ls made > {self.seen}/made; echo sorted\nsorted\n(exit 0)\n", out)
        self.assertEqual(out.count("(exit 0)"), 3)
        # And: the repository is as it was, and the home and the copy are gone
        self.assertEqual(sorted(os.listdir(self.base)), before)
        self.assertFalse(os.path.exists(self.said("home")))
        self.assertFalse(os.path.exists(self.said("pwd")))

    def test_a_command_that_fails_is_shown_with_its_code_and_the_next_runs_still(self):
        self.lays(["echo no >&2; exit 3", f"pwd > {self.seen}/pwd"])
        code, out, _ = self.ran(helpers.RUN)
        self.assertEqual(code, 0)
        self.assertIn("$ echo no >&2; exit 3\nno\n(exit 3)\n", out)
        self.assertFalse(os.path.exists(self.said("pwd")))

    def test_a_work_with_no_commands_runs_nothing(self):
        self.lays([])
        self.assertEqual(
            self.ran(helpers.RUN), (0, "throwaway.py: the work has no commands.\n", "")
        )

    def test_a_link_in_the_folder_is_copied_as_the_file_it_reaches(self):
        # Given: a link to a file outside the repository, and a link to nothing
        outside = os.path.join(self.seen, "outside.md")
        self.write(outside, "kept\n")
        os.symlink(outside, "notes.md")
        os.symlink(os.path.join(self.seen, "gone"), "gone")
        self.lays([f"echo more >> notes.md; cat notes.md > {self.seen}/notes"])
        # When: a command writes through the first
        code, _, _ = self.ran(helpers.RUN)
        # Then: it wrote the copy alone, and the file outside is as it was
        self.assertEqual((code, self.said("notes")), (0, "kept\nmore"))
        self.assertEqual(self.read(outside), "kept\n")

    def test_a_file_out_of_the_home_runs_nothing_and_gives_2(self):
        for made in ("/etc/x", "../x", "a/../..", "."):
            with self.subTest(made=made):
                self.lays([f"touch {self.seen}/ran"], [made])
                code, _, err = self.ran(helpers.RUN)
                self.assertEqual(code, 2)
                self.assertIn(f"the file {made} lies out of the home", err)
                self.assertFalse(os.path.exists(os.path.join(self.seen, "ran")))

    def test_of_files_out_of_the_home_the_first_is_named(self):
        self.lays([], ["/etc/x", "../y"])
        self.assertIn("the file /etc/x lies out of the home", self.ran(helpers.RUN)[2])

    def test_each_command_is_shown_while_the_next_runs(self):
        # Given: a work whose second command waits until the test lets it end
        go = os.path.join(self.seen, "go")
        self.lays(["echo first", f"for _ in $(seq 100); do [ -e {go} ] && break; sleep 0.05; done"])
        lines: queue.Queue[str] = queue.Queue()
        # When: the commands are run as the generator runs them, its output read as it comes
        with subprocess.Popen(
            [sys.executable, throwaway.__file__, helpers.RUN], stdout=subprocess.PIPE, text=True
        ) as running:
            reader = threading.Thread(target=put_each, args=(running.stdout, lines), daemon=True)
            reader.start()
            try:
                # Then: the first is shown with its exit code before the second ends
                seen = [lines.get(timeout=4) for _ in range(3)]
            except queue.Empty:
                seen = []
            finally:
                with open(go, "w", encoding="utf-8"):
                    pass
                # The reader reads to the end before the output closes, as it fails on one closed.
                reader.join(timeout=10)
        self.assertEqual(seen, ["$ echo first\n", "first\n", "(exit 0)\n"])

    def test_a_file_whose_name_begins_with_dots_lies_under_the_home(self):
        self.lays([f"ls -A ~ > {self.seen}/ls"], ["..notes"])
        self.assertEqual((self.ran(helpers.RUN)[0], self.said("ls")), (0, "..notes"))

    def test_a_run_it_cannot_read_gives_2(self):
        code, out, err = self.ran(helpers.RUN)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("throwaway.py: could not run the work's commands:", err)

    def test_a_call_it_does_not_take_gives_2_and_its_usage(self):
        for argv in ((), ("a", "b")):
            with self.subTest(argv=argv):
                self.assertEqual(self.ran(*argv), (2, "", USAGE))

    def test_the_script_takes_the_arguments_after_its_own_path(self):
        self.lays([])
        argv = ["throwaway.py", helpers.RUN]
        with (
            mock.patch.object(throwaway.sys, "argv", argv),
            contextlib.redirect_stdout(io.StringIO()),
            self.assertRaises(SystemExit) as end,
        ):
            runpy.run_path(throwaway.__file__, run_name="__main__")
        self.assertEqual(end.exception.code, 0)


if __name__ == "__main__":
    unittest.main()

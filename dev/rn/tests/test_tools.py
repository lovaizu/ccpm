import os
import shutil
import subprocess
import tempfile
import unittest

from helpers import SCRIPTS

TOOLS = os.path.join(SCRIPTS, "tools.sh")
NEEDED = ("python3", "jq", "gh")


def run_with(tools):
    """Runs the check with a PATH holding only the named tools; a tool this machine lacks is stood
    in for by a script that does nothing, since only its presence is checked."""
    with tempfile.TemporaryDirectory() as folder:
        for tool in tools:
            real = shutil.which(tool)
            path = os.path.join(folder, tool)
            if real:
                os.symlink(real, path)
            else:
                with open(path, "w") as f:
                    f.write("#!/bin/sh\n")
                os.chmod(path, 0o755)
        return subprocess.run(
            [shutil.which("sh") or "sh", TOOLS],
            env={"PATH": folder},
            capture_output=True,
            text=True,
            check=False,
        )


class Tools(unittest.TestCase):
    def test_with_every_tool_in_place_the_check_passes_quietly(self):
        # Given: python3, jq and gh on the PATH
        # When: the check runs
        done = run_with(NEEDED)
        # Then: it passes, saying nothing
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_a_missing_tool_stops_the_check_saying_what_to_install(self):
        cases = [
            ("python3", "python3 is not found; install Python 3.9 or later"),
            ("jq", "jq is not found; install it (https://jqlang.org/download/)"),
            (
                "gh",
                (
                    "gh is not found; install the GitHub CLI (https://cli.github.com) and log in "
                    "with push access"
                ),
            ),
        ]
        for missing, said in cases:
            with self.subTest(missing):
                # Given: one of the three missing from the PATH
                # When: the check runs
                done = run_with([t for t in NEEDED if t != missing])
                # Then: it stops before anything else, saying what to install
                self.assertEqual(done.returncode, 1)
                self.assertIn(said, done.stdout)


if __name__ == "__main__":
    unittest.main()

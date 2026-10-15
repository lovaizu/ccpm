import os
import shutil
import subprocess
import tempfile
import unittest

from helpers import SCRIPTS

TOOLS = os.path.join(SCRIPTS, "tools.sh")


def run_with(tools):
    """Runs the check with a PATH holding only the named tools."""
    with tempfile.TemporaryDirectory() as folder:
        for tool in tools:
            os.symlink(shutil.which(tool), os.path.join(folder, tool))
        return subprocess.run(
            [shutil.which("sh") or "sh", TOOLS],
            env={"PATH": folder},
            capture_output=True,
            text=True,
            check=False,
        )


class Tools(unittest.TestCase):
    def test_with_python3_and_jq_in_place_the_check_passes_quietly(self):
        # Given: python3 and jq on the PATH
        # When: the check runs
        done = run_with(["python3", "jq"])
        # Then: it passes, saying nothing
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_a_missing_tool_stops_the_check_saying_what_to_install(self):
        cases = [
            (["jq"], "python3 is not found; install Python 3.9 or later"),
            (["python3"], "jq is not found; install it (https://jqlang.org/download/)"),
        ]
        for tools, said in cases:
            with self.subTest(said):
                # Given: one of the two missing from the PATH
                # When: the check runs
                done = run_with(tools)
                # Then: it stops before anything else, saying what to install
                self.assertEqual(done.returncode, 1)
                self.assertIn(said, done.stdout)


if __name__ == "__main__":
    unittest.main()

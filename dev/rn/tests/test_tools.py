import os
import subprocess

from helpers import SCRIPTS, RepoTest


class TestTools(RepoTest):
    def check_tools(self, *found):
        # The check only looks whether each tool is found, so a stand-in that does nothing is
        # enough, and the tools on the machine running the tests are kept out of the PATH.
        for tool in found:
            path = os.path.join(self.repo, tool)
            self.write(path, "#!/bin/sh\n")
            os.chmod(path, 0o755)
        return subprocess.run(
            ["/bin/sh", os.path.join(SCRIPTS, "tools.sh")],
            check=False,
            capture_output=True,
            text=True,
            env={"PATH": self.repo},
        )

    def test_the_first_tool_not_found_stops_rn_with_how_to_install_it(self):
        # Given: python3, jq and gh looked for in that order, the ones before a missing tool
        #   found
        # When: the tool check runs
        # Then: it names the missing tool and how to install it, and stops
        for found, missing in [
            (
                (),
                (
                    "python3 is not found; install Python 3.9 or later "
                    "(https://www.python.org/downloads/) and run rn again\n"
                ),
            ),
            (
                ("python3",),
                "jq is not found; install it (https://jqlang.org/download/) and run rn again\n",
            ),
            (
                ("python3", "jq"),
                (
                    "gh is not found; install the GitHub CLI (https://cli.github.com) "
                    "and log in with push access, then run rn again\n"
                ),
            ),
        ]:
            with self.subTest(found=found):
                run = self.check_tools(*found)
                self.assertEqual((run.returncode, run.stdout), (1, missing))

    def test_with_every_tool_found_the_check_prints_nothing_and_ends_well(self):
        # Given: python3, jq and gh all found
        # When: the tool check runs
        # Then: it prints nothing and ends well
        run = self.check_tools("python3", "jq", "gh")
        self.assertEqual((run.returncode, run.stdout), (0, ""))

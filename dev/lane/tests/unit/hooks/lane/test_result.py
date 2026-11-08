"""The cases of result.py's contract: a role gives its result by running it, and it refuses a
result that the role may not give, as the architecture's sequence "S3: a result given" draws it."""

import io
import json
import os
import subprocess
import sys

import helpers
from helpers import result, testing

ROUTES = helpers.ROUTES


class ResultTest(testing.FolderTest):
    def setUp(self):
        super().setUp()
        helpers.write(
            os.path.join(self.base, "hooks", "lanes.json"), json.dumps({"routes": ROUTES})
        )

    def give(self, *argv):
        err = io.StringIO()
        code = result.main(["result.py", *argv], err, self.base)
        return code, err.getvalue()


class TestGiven(ResultTest):
    def test_a_result_a_route_from_the_role_is_on_is_given(self):
        self.assertEqual(self.give("reviewer", "good"), (0, ""))

    def test_a_result_no_route_from_the_role_is_on_is_refused_with_those_it_may_give(self):
        self.assertEqual(
            self.give("reviewer", "written"),
            (1, "result.py: reviewer may give `more` or `good`, and `written` is none of them\n"),
        )

    def test_lanes_laid_that_cannot_be_read_refuse_the_result(self):
        helpers.write(os.path.join(self.base, "hooks", "lanes.json"), "{")
        code, err = self.give("reviewer", "good")
        self.assertEqual(code, 1)
        self.assertIn("result.py: can't tell which results reviewer may give:", err)

    def test_a_command_without_a_role_and_a_result_shows_how_to_run_it(self):
        self.assertEqual(
            self.give("reviewer"),
            (2, "result.py: run it as `result.py <role> <result>`\n"),
        )


class TestRun(ResultTest):
    def test_run_as_a_script_it_reads_the_lanes_laid_beside_it(self):
        code = os.path.join(self.base, "hooks", "lane")
        os.symlink(helpers.CODE, code)
        script = os.path.join(code, "result.py")
        done = subprocess.run(
            [sys.executable, "-B", script, "reviewer", "more"], capture_output=True, check=False
        )
        self.assertEqual(done.returncode, 0)

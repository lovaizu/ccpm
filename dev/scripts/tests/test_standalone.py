"""The tests of dev/scripts/standalone.py: each plugin of plugins/ works from its own folder, as
Claude Code installs only that folder, and uses another plugin only where its plugin.json names that
plugin in its dependencies, never both ways."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from helpers import GIT_ENV, TOP, ran_in

SCRIPT = os.path.join(TOP, "dev", "scripts", "standalone.py")
URL = "https://github.com/lovaizu/ccpm/blob/main/"


class StandaloneTest(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="standalone-")
        self.addCleanup(shutil.rmtree, self.repo)
        self.env = dict(os.environ, **GIT_ENV)
        subprocess.run(["git", "init", "-q", self.repo], env=self.env, check=True)
        self.put("LICENSE", "MIT\n")
        for name, uses in (("rn", ["lane"]), ("lane", [])):
            manifest = {"name": name, "dependencies": uses} if uses else {"name": name}
            self.put(f"plugins/{name}/.claude-plugin/plugin.json", json.dumps(manifest))
            self.put(f"plugins/{name}/LICENSE", "MIT\n")
            self.put(f"plugins/{name}/README.md", "# Plugin\n\n[MIT](LICENSE)\n")

    def put(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as file:
            file.write(text)
        subprocess.run(["git", "add", path], cwd=self.repo, env=self.env, check=True)

    def check(self):
        return ran_in(self.repo, self.env, sys.executable, SCRIPT, "check")

    def fails_with(self, *words):
        result = self.check()
        self.assertEqual(result.returncode, 1, result.stderr)
        for word in words:
            self.assertIn(word, result.stderr)

    def test_plugins_whole_in_their_folders_pass(self):
        self.put(
            "plugins/rn/docs/a.md", f"[Lane]({URL}plugins/lane/README.md)\n[up](../README.md)\n"
        )
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_link_out_of_the_plugin_fails(self):
        self.put("plugins/rn/docs/a.md", "# A\n\nSee [the architecture](../../../dev/rn/a.md).\n")
        self.fails_with("plugins/rn/docs/a.md:3", "dev/rn/a.md")

    def test_a_link_in_a_code_block_is_no_link(self):
        self.put("plugins/rn/a.md", "```\n[x](../../dev/a.md)\n```\n")
        self.assertEqual(self.check().returncode, 0)

    def test_a_path_in_json_out_of_the_plugin_fails(self):
        self.put("plugins/rn/a.json", json.dumps({"source": "../../dev/rn/a.md"}))
        self.fails_with("plugins/rn/a.json", "dev/rn/a.md")

    def test_a_link_that_leads_out_of_the_plugin_fails(self):
        os.symlink("../../LICENSE", os.path.join(self.repo, "plugins/rn/COPYING"))
        subprocess.run(
            ["git", "add", "plugins/rn/COPYING"], cwd=self.repo, env=self.env, check=True
        )
        self.fails_with("plugins/rn/COPYING", "LICENSE")

    def test_a_link_into_a_plugin_it_depends_on_passes(self):
        os.symlink("../lane/README.md", os.path.join(self.repo, "plugins/rn/LANE.md"))
        subprocess.run(
            ["git", "add", "plugins/rn/LANE.md"], cwd=self.repo, env=self.env, check=True
        )
        self.assertEqual(self.check().returncode, 0, self.check().stderr)

    def test_a_link_into_a_plugin_it_does_not_depend_on_fails(self):
        os.symlink("../rn/README.md", os.path.join(self.repo, "plugins/lane/RN.md"))
        subprocess.run(
            ["git", "add", "plugins/lane/RN.md"], cwd=self.repo, env=self.env, check=True
        )
        self.fails_with("plugins/lane/RN.md", "plugins/rn/README.md")

    def test_a_plugin_that_uses_one_it_does_not_depend_on_fails(self):
        self.put("plugins/lane/a.md", f"Built for [rn]({URL}plugins/rn/README.md).\n")
        self.fails_with("plugins/lane/a.md:1", "rn")

    def test_two_plugins_that_depend_on_each_other_fail(self):
        self.put("plugins/lane/.claude-plugin/plugin.json", json.dumps({"dependencies": ["rn"]}))
        self.fails_with("rn", "lane", "each other")

    def test_a_plugin_without_the_license_fails(self):
        os.remove(os.path.join(self.repo, "plugins/lane/LICENSE"))
        subprocess.run(["git", "add", "-A"], cwd=self.repo, env=self.env, check=True)
        self.fails_with("plugins/lane/LICENSE")

    def test_a_license_unlike_the_repository_s_fails(self):
        self.put("plugins/lane/LICENSE", "Apache\n")
        self.fails_with("plugins/lane/LICENSE")

    def test_a_command_it_does_not_take_gives_2_with_its_usage(self):
        result = ran_in(self.repo, self.env, sys.executable, SCRIPT, "fix")
        self.assertEqual((result.returncode, result.stderr), (2, "usage: standalone.py check\n"))


if __name__ == "__main__":
    unittest.main()

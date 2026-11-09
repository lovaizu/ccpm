"""hooks/adapters/, rn's steps adapter and items adapter: each gives each case beside it, as Lane's
lay.py runs them, and the items adapter gives the nodes a change since the run's last commit
touches, none where the run's tree is out of its form or the start names no run."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import helpers
from helpers import RUN, runs


def adapted(name: str, given: dict) -> dict:
    """What the adapter of the name prints given the JSON, run as Lane's guard runs it."""
    done = subprocess.run(
        [sys.executable, os.path.join(helpers.ADAPTERS, f"{name}.py")],
        input=json.dumps(given),
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PLUGIN_ROOT": helpers.RN},
        check=True,
    )
    return json.loads(done.stdout)


def imported(name: str):
    """The adapter of the name as a module, rn's folder its plugin's."""
    with helpers.mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": helpers.RN}):
        return helpers.testing.runpy.run_path(os.path.join(helpers.ADAPTERS, f"{name}.py"))


class Cases(helpers.testing.FolderTest):
    def test_each_adapter_gives_each_of_its_cases(self):
        for name in ("steps-practices", "items-tree"):
            with open(os.path.join(helpers.ADAPTERS, f"{name}.json"), encoding="utf-8") as f:
                cases = json.load(f)
            for n, case in enumerate(cases, 1):
                with self.subTest(name=name, case=n):
                    self.assertEqual(adapted(name, case["given"]), case["gives"])


class Steps(helpers.testing.FolderTest):
    def test_the_lists_of_a_best_practice_by_its_path_and_none_with_no_path(self):
        lists = imported("steps-practices")["lists"]
        path = os.path.join(helpers.practices.OWN, "refactor-code", "best-practice.json")
        found = lists({"practice": [path], "necessary_conditions": None})
        self.assertEqual(
            found[0]["steps"][0]["lanes"], [{"lane": "run_step", "takes": ["{tests}"]}]
        )
        self.assertEqual(lists({"practice": None}), [])


class Items(helpers.RunTest):
    def test_the_nodes_the_change_since_the_commit_touches(self):
        items = imported("items-tree")["items"]
        tree = helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", None)
        self.commits(tree)
        now = helpers.decided(helpers.walkthrough(), 1, "Q6", "the list", "each file")
        given = {"input": runs.tree_path(RUN), "text": json.dumps(now), "values": {"run": [RUN]}}
        self.assertEqual(items(given), ["goal", "D1", "D1Q6", "D2"])
        self.assertEqual(items({**given, "text": "[]"}), [])
        self.assertEqual(items({**given, "text": "{"}), [])
        self.assertEqual(items({**given, "values": {"run": None}}), [])
        self.assertEqual(items({**given, "values": []}), [])

"""The rules laid in hooks/lanes.json: the guard takes only rules in the form lay.py write writes,
and says why it can't take any other."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from typing import Any

from domain import laid

STEP: dict[str, Any] = {"step": 2, "lanes": [{"lane": "run_only", "takes": ["git log --oneline"]}]}
OUT_OF_FORM = "hooks/lanes.json isn't in the form lay.py write writes"


def rules(**role: Any) -> dict[str, Any]:
    """Rules of changelog's writer, with the role's fields as given."""
    return {"plugin": "changelog", "subagents": {"writer": role}}


class Read(unittest.TestCase):
    def setUp(self) -> None:
        self.hooks = os.path.realpath(tempfile.mkdtemp(prefix="lane-laid-"))
        self.addCleanup(shutil.rmtree, self.hooks)

    def lay(self, data: Any) -> dict[str, Any] | str:
        with open(os.path.join(self.hooks, "lanes.json"), "w", encoding="utf-8") as f:
            json.dump(data, f)
        return laid.read(self.hooks)

    def test_rules_in_form_are_taken_as_written(self) -> None:
        written = laid.laid("changelog", {"writer": [STEP]})
        self.assertEqual(self.lay(written), written)

    def test_a_role_with_no_steps_is_in_form(self) -> None:
        self.assertEqual(self.lay(rules(steps=[])), rules(steps=[]))

    def test_rules_that_cant_be_opened(self) -> None:
        os.mkdir(os.path.join(self.hooks, "lanes.json"))
        said = laid.read(self.hooks)
        assert isinstance(said, str)
        self.assertRegex(said, r"^hooks/lanes\.json can't be opened \(.+\)$")


class OutOfForm(unittest.TestCase):
    """Each way the rules can break the form, refused with the same reason."""

    def setUp(self) -> None:
        self.hooks = os.path.realpath(tempfile.mkdtemp(prefix="lane-laid-"))
        self.addCleanup(shutil.rmtree, self.hooks)

    def assertRefused(self, data: Any) -> None:
        with open(os.path.join(self.hooks, "lanes.json"), "w", encoding="utf-8") as f:
            json.dump(data, f)
        self.assertEqual(laid.read(self.hooks), OUT_OF_FORM)

    def test_rules_that_arent_an_object(self) -> None:
        self.assertRefused([])

    def test_a_plugin_that_isnt_text(self) -> None:
        self.assertRefused({"plugin": 1, "subagents": {}})

    def test_subagents_that_arent_an_object(self) -> None:
        self.assertRefused({"plugin": "changelog", "subagents": []})

    def test_a_role_that_isnt_an_object(self) -> None:
        self.assertRefused({"plugin": "changelog", "subagents": {"writer": []}})

    def test_steps_that_arent_a_list(self) -> None:
        self.assertRefused(rules(steps={}))

    def test_a_step_that_isnt_an_object(self) -> None:
        self.assertRefused(rules(steps=[2]))

    def test_a_step_with_no_number(self) -> None:
        self.assertRefused(rules(steps=[{"lanes": STEP["lanes"]}]))

    def test_lanes_that_arent_a_list(self) -> None:
        self.assertRefused(rules(steps=[{"step": 2, "lanes": {}}]))

    def test_a_lane_that_isnt_an_object(self) -> None:
        self.assertRefused(rules(steps=[{"step": 2, "lanes": ["run_only"]}]))

    def test_a_lane_of_a_type_lane_doesnt_know(self) -> None:
        lane = {"lane": "write_only", "takes": ["notes.md"]}
        self.assertRefused(rules(steps=[{"step": 2, "lanes": [lane]}]))

    def test_takes_that_arent_a_list(self) -> None:
        lane = {"lane": "run_only", "takes": "git log --oneline"}
        self.assertRefused(rules(steps=[{"step": 2, "lanes": [lane]}]))

    def test_a_take_that_isnt_text(self) -> None:
        lane = {"lane": "run_only", "takes": ["git log --oneline", 3]}
        self.assertRefused(rules(steps=[{"step": 2, "lanes": [lane]}]))

    def test_a_later_step_out_of_form(self) -> None:
        self.assertRefused(rules(steps=[STEP, {"step": 3}]))

    def test_a_later_role_out_of_form(self) -> None:
        self.assertRefused(
            {"plugin": "changelog", "subagents": {"writer": {"steps": [STEP]}, "reviewer": {}}}
        )


if __name__ == "__main__":
    unittest.main()

"""Turn's entries and parts as Claude Code and Lane take them: each agent in the background naming
its part in core/roles/, each script a part names there, and Turn's routes laid in hooks/lanes.json
as the architecture's Routes table gives them."""

import json
import os
import re
import unittest

import helpers

ROLES = ["up", "planner", "designer", "builder", "evaluator", "refactorer", "proofreader"]
# Turn's routes, as dev/turn/architecture.md's Routes table gives them.
ROUTES = [
    {"from": "up", "to": "planner"},
    {"from": "planner", "on": "planned", "to": "designer"},
    {"from": "planner", "on": "asks"},
    {"from": "designer", "on": "designed", "to": "builder"},
    {"from": "designer", "on": "asks"},
    {"from": "builder", "on": "built", "to": "evaluator"},
    {"from": "builder", "on": "open", "to": "designer"},
    {"from": "evaluator", "on": "more", "to": "designer"},
    {"from": "evaluator", "on": "good", "to": "refactorer"},
    {"from": "refactorer", "on": "refactored", "to": "proofreader"},
    {"from": "proofreader", "on": "more", "to": "refactorer"},
    {"from": "proofreader", "on": "content", "to": "designer"},
    {"from": "proofreader", "on": "good"},
]


def read(*path):
    with open(os.path.join(helpers.TURN, *path), encoding="utf-8") as f:
        return f.read()


class TestEntries(unittest.TestCase):
    def test_each_agent_runs_in_the_background_and_names_its_part(self):
        for role in ROLES:
            with self.subTest(role=role):
                text = read("agents", f"{role}.md")
                self.assertIn("\nbackground: true\n", text)
                self.assertIn(f"`${{CLAUDE_PLUGIN_ROOT}}/core/roles/{role}.md`", text)
                self.assertTrue(
                    os.path.isfile(os.path.join(helpers.TURN, "core", "roles", f"{role}.md"))
                )

    def test_each_script_and_file_a_part_names_is_there(self):
        named = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+\.(?:py|json|md))")
        parts = [os.path.join("core", "roles", f"{r}.md") for r in ROLES]
        parts += [
            os.path.join("core", "domain", "use-and-answer.md"),
            os.path.join("skills", "up", "SKILL.md"),
        ]
        for part in parts:
            for path in named.findall(read(part)):
                if "<" in path or path.startswith("hooks/lane/"):
                    continue
                with self.subTest(part=part, path=path):
                    self.assertTrue(os.path.exists(os.path.join(helpers.TURN, path)))


class TestRoutes(unittest.TestCase):
    def test_turn_s_routes_are_laid_as_the_architecture_gives_them(self):
        laid = json.loads(read("hooks", "lanes.json"))
        self.assertEqual(laid["routes"]["orchestrator"], "up")
        self.assertEqual(laid["routes"]["routes"], ROUTES)


if __name__ == "__main__":
    unittest.main()

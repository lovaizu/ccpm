"""pin:down's entry, skills/down/SKILL.md, read as Claude Code takes it, as pin's architecture's
"The check command keeps one form" promises: its frontmatter lets the AI call it, and its text, with
pin's folder put in place of ${CLAUDE_PLUGIN_ROOT}, links the pinner's part and names each command
in the one form `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py <args>`, the check among them."""

import os
import re
import unittest

import helpers

# Each command the entry names, in backticks, as a caller's checks match it: whatever runs a script.
COMMAND = re.compile(r"`([^`]*\.py\b[^`]*)`")
FORM = re.compile(r"python3 \$\{CLAUDE_PLUGIN_ROOT\}/scripts/(\w+)\.py \S.*")


def frontmatter(text: str) -> dict[str, str]:
    """The keys of the text's frontmatter, each with its value, as `key: value` lines between the
    first two lines of `---`."""
    lines = text.split("\n")
    end = lines.index("---", 1)
    return dict(line.split(": ", 1) for line in lines[1:end] if ": " in line)


class TestDownEntry(unittest.TestCase):
    def test_the_ai_may_call_it(self):
        # Given: the entry's frontmatter
        keys = frontmatter(helpers.SKILL)
        # Then: it names the skill and says when to use it, and does not keep it from the AI
        self.assertEqual(keys.get("name"), "down")
        self.assertTrue(keys.get("description"))
        self.assertNotEqual(keys.get("disable-model-invocation"), "true")

    def test_it_links_the_pinners_part_a_file_in_pin(self):
        # Given: the entry's text
        # Then: it names the pinner's part in pin's folder, and that file is there
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/core/roles/pinner.md", helpers.SKILL)
        self.assertTrue(os.path.isfile(os.path.join(helpers.PIN, "core", "roles", "pinner.md")))

    def test_it_names_each_command_in_the_one_form_the_check_a_script_in_pin(self):
        # Given: each command the entry names
        commands = COMMAND.findall(helpers.SKILL)
        # Then: each is in the one form, the check among them, and each script is in pin
        names = [m.group(1) for m in (FORM.fullmatch(c) for c in commands) if m]
        self.assertEqual(len(names), len(commands), commands)
        self.assertIn("check", names)
        for name in names:
            self.assertTrue(os.path.isfile(os.path.join(helpers.SCRIPTS, f"{name}.py")), name)
        self.assertEqual(
            helpers.CHECK_COMMAND, f"python3 {helpers.PIN}/scripts/check.py <design tree>"
        )


if __name__ == "__main__":
    unittest.main()

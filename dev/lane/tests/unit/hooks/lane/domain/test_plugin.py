"""The cases of plugin.py's contract: the user's plugin's manifest, and the entry of each role."""

import os

from helpers import plugin, testing


class PluginTest(testing.FolderTest):
    def manifest(self, data):
        self.write_json(".claude-plugin/plugin.json", data)


class TestManifest(PluginTest):
    def test_the_name_and_each_dependency_by_its_name_are_read(self):
        self.manifest(
            {"name": "changelog", "dependencies": ["checker", "lint@shared", {"name": "vault"}]}
        )
        found = plugin.manifest(self.base)
        self.assertEqual(found, plugin.Manifest("changelog", ("checker", "lint", "vault")))

    def test_a_manifest_with_no_dependencies_has_none(self):
        self.manifest({"name": "changelog"})
        self.assertEqual(plugin.manifest(self.base).dependencies, ())

    def test_a_folder_with_no_manifest_is_refused(self):
        with self.assertRaisesRegex(plugin.Fault, r"holds no \.claude-plugin/plugin\.json"):
            plugin.manifest(self.base)

    def test_a_manifest_that_is_no_json_is_refused(self):
        self.write(".claude-plugin/plugin.json", "{")
        with self.assertRaisesRegex(plugin.Fault, r"plugin\.json is no JSON: "):
            plugin.manifest(self.base)

    def test_a_manifest_with_no_name_is_refused(self):
        self.manifest({"version": "1"})
        with self.assertRaisesRegex(plugin.Fault, r"plugin\.json gives no name"):
            plugin.manifest(self.base)

    def test_a_dependency_of_another_shape_is_refused(self):
        self.manifest({"name": "a", "dependencies": [1]})
        with self.assertRaisesRegex(plugin.Fault, r"plugin\.json gives a dependency as 1"):
            plugin.manifest(self.base)


class TestEntry(PluginTest):
    def test_a_subagent_is_found_by_the_name_in_its_frontmatter(self):
        self.write("agents/w.md", "---\nname: writer\nbackground: true\n---\n\nBody.\n")
        found = plugin.subagent(self.base, "writer")
        self.assertEqual(found.path, os.path.join(self.base, "agents", "w.md"))

    def test_the_frontmatter_values_are_read_without_their_quotes(self):
        self.write("agents/w.md", "---\nname: \"writer\"\ndescription: 'Writes.'\n---\nBody.\n")
        self.assertEqual(
            plugin.subagent(self.base, "writer").frontmatter,
            {"name": "writer", "description": "Writes."},
        )

    def test_a_frontmatter_line_that_sets_no_key_is_passed_over(self):
        self.write("agents/w.md", "---\nname: writer\n  - a list item\n---\n")
        self.assertEqual(plugin.subagent(self.base, "writer").frontmatter, {"name": "writer"})

    def test_the_body_is_the_text_after_the_frontmatter(self):
        self.write("agents/w.md", "---\nname: writer\n---\nBody.\n")
        self.assertEqual(plugin.subagent(self.base, "writer").body, "Body.\n")

    def test_a_file_with_no_frontmatter_has_its_whole_text_as_its_body(self):
        self.write("skills/write/SKILL.md", "Body.\n")
        found = plugin.skill(self.base, "write")
        self.assertEqual((found.frontmatter, found.body), ({}, "Body.\n"))

    def test_a_skill_is_found_by_its_folder(self):
        self.write("skills/write/SKILL.md", "---\nname: write\n---\nSteps.\n")
        found = plugin.skill(self.base, "write")
        self.assertEqual(found.path, os.path.join(self.base, "skills", "write", "SKILL.md"))

    def test_a_skill_with_no_file_is_refused(self):
        with self.assertRaisesRegex(plugin.Fault, r"holds no skills/write/SKILL\.md"):
            plugin.skill(self.base, "write")

    def test_a_subagent_with_no_entry_is_refused(self):
        with self.assertRaisesRegex(plugin.Fault, r"no agents/\*\.md names `writer`"):
            plugin.subagent(self.base, "writer")

    def test_a_subagent_with_two_entries_is_refused(self):
        self.write("agents/a.md", "---\nname: writer\n---\n")
        self.write("agents/b.md", "---\nname: writer\n---\n")
        with self.assertRaisesRegex(plugin.Fault, r"agents/a\.md and agents/b\.md both name"):
            plugin.subagent(self.base, "writer")

    def test_a_background_subagent_sets_background_true(self):
        self.write("agents/w.md", "---\nname: writer\nbackground: true\n---\n")
        self.assertTrue(plugin.subagent(self.base, "writer").background)

    def test_a_subagent_with_background_false_is_no_background_subagent(self):
        self.write("agents/w.md", "---\nname: writer\nbackground: false\n---\n")
        self.assertFalse(plugin.subagent(self.base, "writer").background)

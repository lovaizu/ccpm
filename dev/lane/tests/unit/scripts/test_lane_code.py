"""The cases of lane_code.py's contract. It lays Lane's code into a plugin as a link within Lane's
marketplace, and as a copy that carries Lane's version elsewhere."""

import json
import os

import helpers
from helpers import lane_code, testing


class CodeTest(testing.FolderTest):
    def setUp(self):
        super().setUp()
        self.market = os.path.join(self.base, "market")
        self.lane = os.path.join(self.market, "plugins", "lane")
        helpers.write(os.path.join(self.lane, "hooks", "lane", "hook.py"), "# hook\n")
        helpers.write(os.path.join(self.lane, "hooks", "lane", "domain", "guard.py"), "# g\n")
        helpers.write(
            os.path.join(self.lane, "hooks", "lane", "__pycache__", "hook.pyc"), "compiled"
        )
        helpers.write(
            os.path.join(self.lane, ".claude-plugin", "plugin.json"),
            json.dumps({"name": "lane", "version": "0.2.0"}),
        )
        helpers.write(os.path.join(self.market, ".claude-plugin", "marketplace.json"), "{}")


class TestLay(CodeTest):
    def test_a_plugin_in_lanes_marketplace_gets_a_relative_link(self):
        root = os.path.join(self.market, "plugins", "changelog")
        os.makedirs(root)
        self.assertEqual(lane_code.lay(self.lane, root), lane_code.Laid("link", None))
        self.assertEqual(os.readlink(os.path.join(root, "hooks", "lane")), "../../lane/hooks/lane")

    def test_a_plugin_elsewhere_gets_a_copy_at_lanes_version(self):
        root = os.path.join(self.base, "changelog")
        os.makedirs(root)
        self.assertEqual(lane_code.lay(self.lane, root), lane_code.Laid("copy", "0.2.0"))
        self.assertEqual(self.read("changelog/hooks/lane/domain/guard.py"), "# g\n")

    def test_a_copy_carries_lanes_version(self):
        root = os.path.join(self.base, "changelog")
        lane_code.lay(self.lane, root)
        self.assertEqual(self.read("changelog/hooks/lane/VERSION"), "0.2.0\n")

    def test_a_copy_leaves_out_compiled_files(self):
        root = os.path.join(self.base, "changelog")
        lane_code.lay(self.lane, root)
        self.assertFalse(os.path.exists(os.path.join(root, "hooks", "lane", "__pycache__")))

    def test_a_copy_laid_before_is_replaced_whole(self):
        root = os.path.join(self.base, "changelog")
        helpers.write(os.path.join(root, "hooks", "lane", "old.py"), "")
        lane_code.lay(self.lane, root)
        self.assertFalse(os.path.exists(os.path.join(root, "hooks", "lane", "old.py")))

    def test_a_link_laid_before_is_replaced(self):
        root = os.path.join(self.base, "changelog")
        os.makedirs(os.path.join(root, "hooks"))
        os.symlink(self.base, os.path.join(root, "hooks", "lane"))
        lane_code.lay(self.lane, root)
        self.assertFalse(os.path.islink(os.path.join(root, "hooks", "lane")))

    def test_lane_outside_any_marketplace_gives_a_copy(self):
        os.remove(os.path.join(self.market, ".claude-plugin", "marketplace.json"))
        root = os.path.join(self.market, "plugins", "changelog")
        self.assertEqual(lane_code.lay(self.lane, root).kind, "copy")


class TestState(CodeTest):
    def test_a_link_is_read_as_a_link(self):
        root = os.path.join(self.market, "plugins", "changelog")
        lane_code.lay(self.lane, root)
        self.assertEqual(lane_code.state(root), lane_code.Laid("link", None))

    def test_a_copy_is_read_with_its_version(self):
        root = os.path.join(self.base, "changelog")
        lane_code.lay(self.lane, root)
        self.assertEqual(lane_code.state(root), lane_code.Laid("copy", "0.2.0"))

    def test_a_copy_with_no_version_is_read_with_none(self):
        root = os.path.join(self.base, "changelog")
        helpers.write(os.path.join(root, "hooks", "lane", "hook.py"), "")
        self.assertEqual(lane_code.state(root), lane_code.Laid("copy", None))

    def test_a_plugin_with_no_code_laid_is_read_as_none(self):
        self.assertIsNone(lane_code.state(os.path.join(self.base, "changelog")))


class TestOlder(testing.FolderTest):
    def test_a_lower_version_is_older(self):
        self.assertTrue(lane_code.older("0.9.0", "0.10.0"))

    def test_the_same_version_is_not_older(self):
        self.assertFalse(lane_code.older("0.2.0", "0.2.0"))

    def test_a_higher_version_is_not_older(self):
        self.assertFalse(lane_code.older("1.0.0", "0.9.9"))

    def test_no_version_is_older(self):
        self.assertTrue(lane_code.older(None, "0.1.0"))

    def test_lanes_own_version_is_read_from_its_manifest(self):
        helpers.write("lane/.claude-plugin/plugin.json", json.dumps({"version": "0.3.1"}))
        self.assertEqual(lane_code.version(os.path.join(self.base, "lane")), "0.3.1")

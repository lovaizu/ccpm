"""lane's code put in a plugin's hooks/lane/: a relative link to lane's in a plugin of the ccpm
marketplace, a copy with lane's version in VERSION anywhere else, lane's own left as it is."""

import json
import os
import unittest

import helpers
from helpers import placed


class PlacedTest(helpers.PluginTest):
    def code(self) -> str:
        """The plugin's hooks/lane/."""
        return os.path.join(self.plugin, "hooks", "lane")

    def version(self) -> str:
        """lane's version."""
        with open(
            os.path.join(helpers.LANE, ".claude-plugin", "plugin.json"), encoding="utf-8"
        ) as f:
            return json.load(f)["version"]


class TestCodePut(PlacedTest):
    def test_outside_the_marketplace_a_copy_with_lanes_version_is_put(self):
        # Given: a plugin outside any marketplace, with an old copy in hooks/lane/
        self.write(os.path.join(self.code(), "old.py"), "")
        # When: lane's code is put in it
        placed.code_put(self.plugin)
        # Then: hooks/lane/ is a copy of lane's code, the old gone, with lane's version
        self.assertTrue(os.path.isfile(os.path.join(self.code(), "core", "domain", "guard.py")))
        self.assertFalse(os.path.exists(os.path.join(self.code(), "old.py")))
        self.assertFalse(os.path.islink(self.code()))
        self.assertEqual(self.read(os.path.join(self.code(), "VERSION")), self.version() + "\n")
        self.assertEqual(
            [d for _, ds, _ in os.walk(self.code()) for d in ds if d == "__pycache__"], []
        )

    def in_marketplace(self, name: str, lane_beside: bool) -> str:
        """The plugin in the plugins/ of a marketplace of the name, with lane beside it where
        asked; gives the plugin's folder there."""
        plugin = os.path.join(self.base, "m", "plugins", "changelog")
        os.makedirs(os.path.dirname(plugin))
        os.rename(self.plugin, plugin)
        self.write_json(
            os.path.join(self.base, "m", ".claude-plugin", "marketplace.json"), {"name": name}
        )
        if lane_beside:
            os.makedirs(os.path.join(self.base, "m", "plugins", "lane", "hooks", "lane"))
        return plugin

    def test_in_the_ccpm_marketplace_a_link_to_lane_beside_is_put(self):
        # Given: the plugin in ccpm's plugins/, with lane beside it, and a link there before
        plugin = self.in_marketplace("ccpm", True)
        os.makedirs(os.path.join(plugin, "hooks"))
        os.symlink("elsewhere", os.path.join(plugin, "hooks", "lane"))
        # When: lane's code is put in it
        placed.code_put(plugin)
        # Then: hooks/lane/ is a relative link to lane's
        self.assertEqual(
            os.readlink(os.path.join(plugin, "hooks", "lane")), "../../lane/hooks/lane"
        )

    def test_in_another_marketplace_or_without_lane_beside_a_copy_is_put(self):
        for name, beside in (("other", True), ("ccpm", False)):
            with self.subTest(name=name, beside=beside):
                # Given: the plugin in another marketplace, or in ccpm with no lane beside it
                self.setUp()
                plugin = self.in_marketplace(name, beside)
                # When: lane's code is put in it
                placed.code_put(plugin)
                # Then: a copy is put
                self.assertTrue(os.path.isfile(os.path.join(plugin, "hooks", "lane", "VERSION")))

    def test_a_marketplace_whose_manifest_cannot_be_read_is_none(self):
        for text in ("{", "[]"):
            with self.subTest(text=text):
                # Given: a marketplace.json of no JSON, or no object
                self.write(os.path.join(self.base, ".claude-plugin", "marketplace.json"), text)
                # When: the marketplace is named
                # Then: it is none
                self.assertIsNone(placed.marketplace(self.base))

    def test_lanes_own_code_is_left_as_it_is(self):
        # Given: lane itself
        # When: lane's code is put in it
        placed.code_put(helpers.LANE)
        # Then: its hooks/lane/ is its code still, with no VERSION
        self.assertFalse(os.path.exists(os.path.join(helpers.CODE, "VERSION")))


class TestOlder(PlacedTest):
    def test_a_copy_older_than_lane_gives_its_version(self):
        for given, older in (
            ("0.0.1\n", "0.0.1"),
            ("x", "x"),
            (None, "a copy with no VERSION"),
            ("99.0.0", None),
        ):
            with self.subTest(given=given):
                # Given: a copy of an older version, of no version, with no VERSION, or a newer
                os.makedirs(self.code(), exist_ok=True)
                version = os.path.join(self.code(), "VERSION")
                if given is None:
                    if os.path.exists(version):
                        os.remove(version)
                else:
                    self.write(version, given)
                # When: it is asked whether it is older
                # Then: it gives its version where it is, None for a newer
                self.assertEqual(placed.older(self.plugin), older)

    def test_a_copy_of_lanes_version_link_or_none_is_not_older(self):
        for kind in ("same", "link", "none"):
            with self.subTest(kind=kind):
                # Given: a copy of lane's version, a link, or no hooks/lane/
                self.setUp()
                if kind == "same":
                    self.write(os.path.join(self.code(), "VERSION"), self.version())
                elif kind == "link":
                    os.makedirs(os.path.join(self.plugin, "hooks"))
                    os.symlink(helpers.CODE, self.code())
                # When: it is asked whether it is older
                # Then: it is not
                self.assertIsNone(placed.older(self.plugin))

    def test_lanes_own_is_not_older(self):
        # Given: lane itself
        # When: it is asked whether its code is older
        # Then: it is not
        self.assertIsNone(placed.older(helpers.LANE))


if __name__ == "__main__":
    unittest.main()

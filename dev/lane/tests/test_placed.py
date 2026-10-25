"""lane's code the layer puts in the plugin's hooks/lane/: a link to lane's in a plugin of the ccpm
marketplace, a copy with lane's version anywhere else, lane's own left as it is."""

import os
import unittest
from unittest import mock

import helpers
from helpers import placed
from laying import LayTest


class TestWriteCode(LayTest):
    def code(self):
        return os.path.join(self.plugin, "hooks", "lane")

    def test_lanes_code_is_copied_with_its_version(self):
        # Given: a plugin outside the ccpm marketplace
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: lane's code is copied into hooks/lane/, each file as lane's, with VERSION holding
        # the version of lane's plugin.json
        for name in (
            "pretooluse.py",
            "hook.py",
            "call.py",
            "shell.py",
            "step.py",
            "lanes/hands_off.py",
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    self.read(os.path.join(self.code(), name)),
                    self.read(os.path.join(helpers.CODE, name)),
                )
        version = self.read_json(os.path.join(helpers.LANE, ".claude-plugin", "plugin.json"))
        self.assertEqual(self.read(os.path.join(self.code(), "VERSION")), version["version"] + "\n")
        self.assertFalse(os.path.islink(self.code()))

    def test_a_copy_there_before_is_replaced(self):
        # Given: a copy of lane's code there before, holding a file lane no longer has
        self.write(os.path.join(self.code(), "old.py"), "")
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: the copy is lane's code as it is now
        self.assertFalse(os.path.exists(os.path.join(self.code(), "old.py")))
        self.assertTrue(os.path.exists(os.path.join(self.code(), "pretooluse.py")))

    def test_a_plugin_of_the_ccpm_marketplace_links_to_lanes_code(self):
        # Given: the plugin in a clone of the ccpm marketplace, lane beside it
        self.write_json(
            os.path.join(self.base, ".claude-plugin", "marketplace.json"), {"name": "ccpm"}
        )
        os.makedirs(os.path.join(self.base, "lane", "hooks", "lane"))
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: hooks/lane is a relative link to lane's code beside it, with no VERSION
        self.assertEqual(
            os.readlink(self.code()), os.path.join("..", "..", "lane", "hooks", "lane")
        )

    def test_a_link_there_before_is_made_again(self):
        # Given: the plugin in a clone of the ccpm marketplace, its lanes written once
        self.write_json(
            os.path.join(self.base, ".claude-plugin", "marketplace.json"), {"name": "ccpm"}
        )
        os.makedirs(os.path.join(self.base, "lane", "hooks", "lane"))
        self.lay("write", self.proposal_file)
        self.propose(self.proposal())
        # When: the proposal is written again
        # Then: it is written, hooks/lane the same link
        self.assertEqual(self.lay("write", self.proposal_file)[0], 0)
        self.assertEqual(
            os.readlink(self.code()), os.path.join("..", "..", "lane", "hooks", "lane")
        )

    def test_a_plugin_of_another_marketplace_or_without_lane_beside_it_gets_a_copy(self):
        for name, beside in (
            ('{"name": "ccpm"}', False),
            ('{"name": "acme"}', True),
            ('{"name": "zeta"}', True),
            ("[]", True),
            ("{", True),
        ):
            with self.subTest(marketplace=name, lane_beside=beside):
                # Given: the plugin in ccpm without lane beside it, or in another marketplace, or
                # in one whose manifest names none, with lane beside it
                self.write(os.path.join(self.base, ".claude-plugin", "marketplace.json"), name)
                if beside:
                    os.makedirs(os.path.join(self.base, "lane", "hooks", "lane"), exist_ok=True)
                self.propose(self.proposal())
                # When: the proposal is written
                self.lay("write", self.proposal_file)
                # Then: lane's code is copied
                self.assertFalse(os.path.islink(self.code()))
                self.assertTrue(os.path.exists(os.path.join(self.code(), "VERSION")))

    def test_only_lanes_code_itself_is_lanes_own(self):
        for place, own in ((helpers.CODE, True), (os.path.dirname(helpers.CODE), False)):
            with self.subTest(place=place):
                # Given: lane's code, or the folder it is in
                # When: whether it is lane's own code is read
                # Then: it is for lane's code alone
                self.assertEqual(placed.lanes_own(place), own)

    def test_lanes_own_code_is_left_as_it_is_on_lane_itself(self):
        # Given: the plugin is lane itself, its hooks/lane/ the code the layer runs on
        own = os.path.join(self.code(), "pretooluse.py")
        self.write(own, "lane's own")
        with mock.patch.object(placed, "CODE", self.code()):
            # When: the proposal is written
            self.lay("write", self.proposal_file)
        # Then: lane's code is left where it is, unremoved, with no VERSION put in it
        self.assertEqual(self.read(own), "lane's own")
        self.assertFalse(os.path.exists(os.path.join(self.code(), "VERSION")))


if __name__ == "__main__":
    unittest.main()

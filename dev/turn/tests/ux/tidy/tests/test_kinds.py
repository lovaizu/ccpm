import unittest

from tidy.kinds import OTHER, kind_of  # pyrefly: ignore[missing-import]


class KindOf(unittest.TestCase):
    def test_a_known_extension_in_any_case(self):
        self.assertEqual(kind_of("Photo.JPG"), "images")

    def test_an_unknown_extension_goes_to_other(self):
        self.assertEqual(kind_of("notes.xyz"), OTHER)

    def test_no_extension_stays(self):
        self.assertIsNone(kind_of("Makefile"))


if __name__ == "__main__":
    unittest.main()

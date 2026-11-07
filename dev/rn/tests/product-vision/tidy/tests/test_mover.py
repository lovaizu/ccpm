import os
import tempfile
import unittest

from tidy.mover import move, plan  # pyrefly: ignore[missing-import]


class Mover(unittest.TestCase):
    def test_a_file_whose_name_its_folder_holds_stays(self):
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, "images"))
            for name in ("a.jpg", "images/a.jpg", "b.pdf"):
                open(os.path.join(folder, name), "w").close()
            moves, stays = plan(folder)
            self.assertEqual(moves, [("b.pdf", "documents")])
            self.assertEqual(stays, [("a.jpg", "images/a.jpg is there already")])
            move(folder, moves)
            self.assertTrue(os.path.exists(os.path.join(folder, "documents", "b.pdf")))


if __name__ == "__main__":
    unittest.main()

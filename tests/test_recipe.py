import os
import unittest


class TestRecipe(unittest.TestCase):
    RESULT_BASE_DIR = ".."

    def test_a(self):
        result_dir = os.path.abspath(os.path.join(self.RESULT_BASE_DIR,
                                                  "test_a"))
        file_1_path = os.path.join(result_dir, "test_a1.result")
        file_2_path = os.path.join(result_dir, "test_a2.result")
        file_1 = open(file_1_path).read()
        file_2 = open(file_2_path).read()

        self.assertEquals(file_1, file_2)

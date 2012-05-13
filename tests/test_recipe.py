import os
import stat
import unittest


class TestRecipe(unittest.TestCase):
    RESULT_BASE_DIR = "../../tests"

    def _file(self, filename, mode=None):
        path = os.path.abspath(os.path.join(self.RESULT_BASE_DIR, filename))
        self.assertTrue(os.path.exists(path))

        if mode:
            self.assertEquals(mode, stat.S_IMODE(os.stat(path).st_mode))

        with open(path) as fp:
            return fp.read()

    def test_jobs1(self):
        data = self._file("test_jobs1.result")
        lines = data.split("\n")
        self.assertTrue(lines[0].endswith("/tests"))
        self.assertEquals("templates/test_jobs1.jinja2", lines[1])
        self.assertTrue(lines[2].endswith(
                "tests/parts/tests/test_jobs1.result"))

    def test_jobs2(self):
        data = self._file("test_jobs2.result", mode=0777)
        lines = data.split("\n")
        self.assertTrue(lines[0].endswith("/tests"))
        self.assertEquals("templates/test_jobs1.jinja2", lines[1])
        self.assertEquals("templates/test_jobs2.jinja2", lines[2])
        self.assertEquals("0777", lines[3])

    def test_rooted_jobs(self):
        data = self._file("test_rooted_jobs.result")
        self.assertEquals("templates", data)

    def test_old1(self):
        data = self._file("test_old1.result")
        lines = data.split("\n")
        self.assertTrue(lines[0].endswith("/tests"))
        self.assertEquals("templates/test_old1.jinja2", lines[1])
        self.assertTrue(lines[2].endswith(
                "tests/parts/tests/test_old1.result"))

    def test_old2(self):
        data = self._file("test_old2.result", mode=0755)
        lines = data.split("\n")
        self.assertTrue(lines[0].endswith("/tests"))
        self.assertEquals("templates/test_old1.jinja2", lines[1])
        self.assertEquals("templates/test_old2.jinja2", lines[2])
        self.assertEquals("0755", lines[3])

    def test_rooted_old(self):
        data = self._file("test_rooted_old.result")
        self.assertEquals("Hi!", data)

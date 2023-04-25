import subprocess as sp
import unittest

from github_diff import Repository


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.repo = Repository(organization="psf", repository="requests")

    def test_can_get_diff(self):
        diff = self.repo.get_diff(base="HEAD~5", head="HEAD")
        self.assertEqual(len(diff["commits"]), 5)

    def test_can_print_diff(self):
        with self.assertLogs("github_diff", level="INFO") as cm:
            self.repo.print_diff_commit_messages(base="HEAD~5", head="HEAD")
        self.assertEqual(len(cm.output), 5)


class TestCli(unittest.TestCase):
    def test_can_print_diff(self):
        process = sp.run(
            "./github_diff.py psf requests HEAD~5 HEAD", capture_output=True, shell=True
        )
        commits = process.stderr.decode("utf-8").splitlines()
        self.assertEqual(len(commits), 5)

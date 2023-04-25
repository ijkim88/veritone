import os
import requests
import subprocess as sp
import unittest

from github_diff import AccessToken, Repository


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        self.session.auth = AccessToken(os.environ.get("GH_TOKEN"))
        self.repo = Repository(
            organization="psf", repository="requests", session=self.session
        )

    def tearDown(self):
        self.session.close()

    def test_can_get_diff(self):
        diff = self.repo.get_diff(base="HEAD~5", head="HEAD")
        self.assertEqual(len(diff["commits"]), 5)

    def test_get_diff_with_invalid_shas_raises_exception(self):
        with self.assertRaises(requests.exceptions.HTTPError):
            self.repo.get_diff(base="bogus", head="sha")

    def test_can_print_diff(self):
        with self.assertLogs("github_diff", level="INFO") as cm:
            self.repo.print_diff_commit_messages(base="HEAD~5", head="HEAD")
        self.assertEqual(len(cm.output), 5)

    def test_print_diff_with_invalid_shas_logs_error(self):
        with self.assertLogs("github_diff", level="ERROR") as cm:
            self.repo.print_diff_commit_messages(base="bogus", head="sha")
        self.assertIn("ERROR:github_diff:Failed to get commit diff", cm.output)


class TestCli(unittest.TestCase):
    def test_can_print_diff(self):
        process = sp.run(
            "./github_diff.py psf requests HEAD~5 HEAD", capture_output=True, shell=True
        )
        commits = process.stderr.decode("utf-8").splitlines()
        self.assertEqual(len(commits), 5)

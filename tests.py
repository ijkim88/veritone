import os
import requests
import subprocess as sp
import unittest

from github_compare import AccessToken, Repository


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
            organization="ijkim88", repository="veritone", session=self.session
        )

    def tearDown(self):
        self.session.close()

    def test_can_get_compare_commits(self):
        commits = self.repo.get_compare_commits(
            base="0984cda", head="71c4e08", per_page=2
        )
        self.assertEqual(len(list(commits)), 5)

    def test_get_compare_commits_with_invalid_shas_raises_exception(self):
        with self.assertRaises(requests.exceptions.HTTPError):
            list(self.repo.get_compare_commits(base="bogus", head="sha"))

    def test_can_print_compare_commit_messages(self):
        with self.assertLogs("github_compare", level="INFO") as cm:
            self.repo.print_compare_commit_messages(base="0984cda", head="71c4e08")
        self.assertEqual(len(cm.output), 5)

    def test_print_compare_commit_messages_with_invalid_shas_logs_error(self):
        with self.assertLogs("github_compare", level="ERROR") as cm:
            self.repo.print_compare_commit_messages(base="bogus", head="sha")
        self.assertIn("ERROR:github_compare:Failed to get compare commit(s)", cm.output)


class TestCli(unittest.TestCase):
    def test_can_print_compare_commit_messages(self):
        process = sp.run(
            "./github_compare.py ijkim88 veritone 0984cda 71c4e08",
            capture_output=True,
            shell=True,
        )
        commits = process.stderr.decode("utf-8").splitlines()
        self.assertEqual(len(commits), 5)

    def test_github_token_environment_variable_required(self):
        env = dict(os.environ)
        del env["GH_TOKEN"]
        with self.assertRaises(sp.CalledProcessError):
            sp.run(
                "./github_compare.py ijkim88 veritone 0984cda 71c4e08",
                check=True,
                env=env,
                shell=True,
                stderr=sp.DEVNULL,
            )

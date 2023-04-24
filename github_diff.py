#!/usr/bin/env python

import requests

from typing import Any, Dict

TOKEN = ""


class Repository:
    def __init__(self, organization: str, repository: str):
        self.organization = organization
        self.repository = repository

    def get_diff(self, base: str, head: str) -> Dict[str, Any]:
        response = requests.get(
            f"https://api.github.com/repos/{self.organization}/{self.repository}/compare/{base}...{head}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {TOKEN}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        response.raise_for_status()
        return response.json()

    def print_diff_commit_messages(self, base: str, head: str) -> None:
        diff = self.get_diff(base, head)
        for commit in diff.get("commits", []):
            sha = commit.get("sha")
            details = commit.get("commit", {})
            message = details.get("message", "")
            print(f"{sha:.10}\t{message}")


if __name__ == "__main__":
    repo = Repository(organization="psf", repository="requests")
    repo.print_diff_commit_messages("HEAD~5", "HEAD")

#!/usr/bin/env python

import logging
import os
import requests

from argparse import ArgumentParser
from requests import Session
from requests.models import PreparedRequest
from typing import Any, Dict, Iterator

log = logging.getLogger(__name__)


class AccessToken(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class Repository:
    def __init__(self, organization: str, repository: str, session: Session):
        self.organization = organization
        self.repository = repository
        self.session = session

    def get_diff_commits(
        self, base: str, head: str, per_page: int = 30
    ) -> Iterator[Dict[str, Any]]:
        page = 1
        commit_count = 0
        total_commits = None
        while (total_commits is None) or (commit_count < total_commits):
            response = self.session.get(
                f"https://api.github.com/repos/{self.organization}/{self.repository}/compare/{base}...{head}",
                params={
                    "page": page,
                    "per_page": per_page,
                },
            )
            response.raise_for_status()

            data = response.json()
            total_commits = data["total_commits"]
            commit_count = commit_count + len(data["commits"])
            for commit in data["commits"]:
                yield commit

            page = page + 1

    def print_diff_commit_messages(
        self, base: str, head: str, oneline: bool = True
    ) -> None:
        try:
            for commit in self.get_diff_commits(base, head):
                sha = commit.get("sha")
                details = commit.get("commit", {})
                message = details.get("message", "")
                if oneline:
                    message = message.splitlines()[0]
                log.info(f"{sha:.10}\t{message}")

        except Exception:
            log.error("Failed to get commit diff")
            return


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument("organization", help="GitHub Organization")
    parser.add_argument("repository", help="Repository Name")
    parser.add_argument("base", help="Base Commit")
    parser.add_argument("head", help="Head Commit")
    args = parser.parse_args()

    with requests.Session() as session:
        session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        session.auth = AccessToken(os.environ.get("GH_TOKEN"))
        repo = Repository(
            organization=args.organization, repository=args.repository, session=session
        )
        repo.print_diff_commit_messages(args.base, args.head)

#!/usr/bin/env python

import logging
import os
import requests

from argparse import ArgumentParser
from requests import Session
from requests.models import PreparedRequest
from typing import Any, Dict

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

    def get_diff(self, base: str, head: str) -> Dict[str, Any]:
        response = self.session.get(f"https://api.github.com/repos/{self.organization}/{self.repository}/compare/{base}...{head}")
        response.raise_for_status()
        return response.json()

    def print_diff_commit_messages(
        self, base: str, head: str, oneline: bool = True
    ) -> None:
        diff = self.get_diff(base, head)
        for commit in diff.get("commits", []):
            sha = commit.get("sha")
            details = commit.get("commit", {})
            message = details.get("message", "")
            if oneline:
                message = message.splitlines()[0]
            log.info(f"{sha:.10}\t{message}")


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument("organization", help="GitHub Organization")
    parser.add_argument("repository", help="Repository Name")
    parser.add_argument("base", help="Base Commit")
    parser.add_argument("head", help="Head Commit")
    args = parser.parse_args()

    with requests.Session() as session:
        session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        session.auth = AccessToken(os.environ.get("GH_TOKEN"))
        repo = Repository(organization=args.organization, repository=args.repository, session=session)
        repo.print_diff_commit_messages(args.base, args.head)

# Veritone Coding Challenge - GitHub Compare Commits

This script functions similarly to `git log --oneline BASE...HEAD` command, but uses GitHub API instead of `git`.

## Usage

```
$ ./github_compare.py -h
usage: github_compare.py [-h] organization repository base head

Set environment variable $GH_TOKEN with GitHub Personal Access Token for authentication

positional arguments:
  organization  GitHub Organization
  repository    Repository Name
  base          Base Commit
  head          Head Commit

options:
  -h, --help    show this help message and exit
```

### GitHub Personal Access Token

Create a [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) and set `$GH_TOKEN` environment variable. This is required for the script to authenticate with GitHub.

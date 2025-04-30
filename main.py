"""Sync content from source repository to translations repository.

This script is intended to be run as a GitHub Action. It will sync content
from a source repository to a translations repository, create a new branch,
open a pull request for the changes and finally merge them.
"""

import os
import traceback
from datetime import datetime
from subprocess import Popen, PIPE
from pathlib import Path
from typing import Optional, Union

from github import Github, Auth
from dotenv import load_dotenv

load_dotenv()


def run(
    cmds: list[str], cwd: Optional[Union[str, Path]] = None
) -> tuple[str, str, int]:
    """Run a command in the shell and print the standard output, error and return code.

    Parameters
    ----------
    cmds : list
        List of commands to run.
    cwd : str, optional
        Current working directory to run the command in. If None, use the current working directory.

    Returns
    -------
    out : str
        Output of the command.
    err : str
        Error of the command.
    rc : int
        Return code of the command.
    """
    p = Popen(cmds, stdout=PIPE, stderr=PIPE, cwd=cwd)
    out, err = p.communicate()
    stdout = out.decode()
    stderr = err.decode()
    print("\n\n\nCmd: \n" + " ".join(cmds))
    print("Cwd: \n", cwd or os.getcwd())
    print("Out: \n", stdout)
    print("Err: \n", stderr)
    print("Code: \n", p.returncode)
    return stdout, stderr, p.returncode


def verify_signature(
    token: str,
    repo: str,
    name: str,
    email: str,
    pr_title: str,
    branch_name: str,
    run_local: bool = False,
) -> bool:
    """Verify the signature of the pull request.

    Parameters
    ----------
    token : str
        Personal access token of the source repository.
    repo : str
        Repository name.
    name : str
        Name of the bot account.
    email : str
        Email of the bot account.
    pr_title : str
        Title of the pull request.
    branch_name : str
        Branch name of the pull request.
    run_local : bool, optional
        When runnning the script locally. disable verification. Default is `False`.
    """
    if run_local:
        return True

    auth = Auth.Token(token)
    g = Github(auth=auth)
    pulls = g.get_repo(repo).get_pulls(state="open", sort="created", direction="desc")
    pr_branch = None
    signed_by = f"{name} <{email}>"
    checks = []
    for pr in pulls:
        pr_branch = pr.head.ref
        if pr.title == pr_title and pr_branch == branch_name:
            print("\n\nFound PR try to merge it!")
            # Check if commits are signed
            for commit in pr.get_commits():
                print(
                    [
                        commit.commit.verification.verified,  # type: ignore
                        signed_by,
                        commit.commit.verification.payload,  # type: ignore
                    ]
                )
                checks.append(
                    commit.commit.verification.verified  # type: ignore
                    and signed_by in commit.commit.verification.payload  # type: ignore
                )
            break

    g.close()
    return all(checks)


def sync_website_content(
    username: str,
    token: str,
    source_repo: str,
    source_path: str,
    source_ref: str,
    translations_repo: str,
    translations_path: str,
    translations_source_path: str,
    translations_ref: str,
    auto_merge: bool,
    name: str,
    email: str,
    run_local: bool = False,
) -> None:
    """Sync content from source repository to translations repository.

    Parameters
    ----------
    username : str
        Username of the source repository.
    token : str
        Personal access token of the source repository.
    source_repo : str
        Source repository name.
    source_path : str
        Source path name.
    source_ref : str
        Source branch name.
    translations_repo : str
        Translations repository name.
    translations_path : str
        Translations path name.
    translations_source_path : str
        Path to the where the original source content is stored.
    translations_ref : str
        Translations source branch.
    name : str
        Name of the bot account.
    email : str
        Email of the bot account.
    """
    src_end = "/" if source_path.endswith("/") else ""
    trans_end = "/" if translations_source_path.endswith("/") else ""
    base_path = Path(os.getcwd())
    base_source_path = base_path / source_repo.split("/")[-1]
    if source_path in ["/", ""]:
        src_path = base_source_path
    else:
        src_path = base_source_path / source_path

    base_translations_path = base_path / translations_repo.split("/")[-1]
    trans_path = base_translations_path / translations_source_path
    print(
        "\n\n### Syncing content from source repository to translations repository.\n\n"
    )
    print("\n\nBase path:\n", base_path)
    print("\n\nBase source path:\n", base_source_path)
    print("\n\nSource path:\n", src_path)
    print("\n\nBase translations path:\n", base_translations_path)
    print("\n\nTranslations path:\n", trans_path)

    if source_ref:
        cmds = [
            "git",
            "clone",
            "--single-branch",
            "-b",
            source_ref,
            f"https://{username}:{token}@github.com/{source_repo}.git",
        ]
    else:
        cmds = [
            "git",
            "clone",
            f"https://{username}:{token}@github.com/{source_repo}.git",
        ]

    run(cmds)

    if translations_ref:
        cmds = [
            "git",
            "clone",
            "-b",
            translations_ref,
            f"https://{username}:{token}@github.com/{translations_repo}.git",
        ]
    else:
        cmds = [
            "git",
            "clone",
            f"https://{username}:{token}@github.com/{translations_repo}.git",
        ]

    run(cmds)

    for path in [base_source_path, base_translations_path]:
        run(["git", "config", "user.name", f'"{name}"'], cwd=path)
        run(["git", "config", "user.email", f'"{email}"'], cwd=path)

    date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    branch_name = f"content-sync-{date_time}"

    src = str(src_path) + src_end
    dest = str(trans_path) + trans_end

    run(["git", "checkout", "-b", branch_name], cwd=base_translations_path)
    os.makedirs(dest, exist_ok=True)
    run(["rsync", "-avr", "--delete", src, dest])

    run(["git", "status"], cwd=base_translations_path)
    run(["git", "add", "."], cwd=base_translations_path)
    _out, _err, rc = run(
        ["git", "diff", "--staged", "--quiet"], cwd=base_translations_path
    )

    pr_title = "Update content"
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if rc:
        if run_local:
            run(
                ["git", "commit", "-m", "Update content."],
                cwd=base_translations_path,
            )
        else:
            run(
                ["git", "commit", "-S", "-m", "Update content."],
                cwd=base_translations_path,
            )

        run(["git", "remote", "-v"], cwd=base_translations_path)
        run(["git", "push", "-u", "origin", branch_name], cwd=base_translations_path)

        os.environ["GITHUB_TOKEN"] = token
        run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                "main",
                "--head",
                branch_name,
                "--title",
                pr_title,
                "--body",
                "Automated content update.",
            ],
            cwd=base_translations_path,
        )
        os.environ["GITHUB_TOKEN"] = github_token

        if auto_merge:
            if verify_signature(
                token=token,
                repo=translations_repo,
                name=name,
                email=email,
                pr_title=pr_title,
                branch_name=branch_name,
                run_local=run_local,
            ):
                print("\n\nAll commits are signed, auto-merging!")
                # https://cli.github.com/manual/gh_pr_merge
                os.environ["GITHUB_TOKEN"] = token
                run(
                    [
                        "gh",
                        "pr",
                        "merge",
                        branch_name,
                        "--auto",
                        "--squash",
                    ],
                    cwd=base_translations_path,
                )
            else:
                print("\n\nNot all commits are signed, abort merge!")
    else:
        print("\n\nNo changes to commit.")


def parse_input() -> dict:
    gh_input = {
        # Automations Bot account
        "username": "scientificpythontranslations",
        # Github Personal Access Token provided by organization secrets
        "token": os.environ["TOKEN"],
        # Provided by user action input
        "source_repo": os.environ["INPUT_SOURCE-REPO"],
        "source_path": os.environ["INPUT_SOURCE-PATH"],
        "source_ref": os.environ["INPUT_SOURCE-REF"],
        "translations_repo": os.environ["INPUT_TRANSLATIONS-REPO"],
        "translations_path": os.environ["INPUT_TRANSLATIONS-PATH"],
        "translations_source_path": os.environ["INPUT_TRANSLATIONS-SOURCE-PATH"],
        "translations_ref": os.environ["INPUT_TRANSLATIONS-REF"],
        "auto_merge": os.environ["INPUT_AUTO-MERGE"].lower() == "true",
        # Provided by gpg action based on organization secrets
        "name": os.environ["GPG_NAME"],
        "email": os.environ["GPG_EMAIL"],
        "run_local": os.environ.get("RUN_LOCAL", "False").lower() == "true",
    }
    return gh_input


def main() -> None:
    try:
        gh_input = parse_input()
        sync_website_content(**gh_input)
    except Exception as e:
        print("Error: ", e)
        print(traceback.format_exc())
        raise e


if __name__ == "__main__":
    main()

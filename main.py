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

from github import Github, Auth
from dotenv import load_dotenv
load_dotenv()


def run(cmds: list[str]) -> tuple[str, str, int]:
    """Run a command in the shell and print the standard output, error and return code.

    Parameters
    ----------
    cmds : list
        List of commands to run.

    Returns
    -------
    out : str
        Output of the command.
    err : str
        Error of the command.
    rc : int
        Return code of the command.
    """
    p = Popen(cmds, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    stdout = out.decode()
    stderr = err.decode()
    print("\n\n\nCmd: \n" + " ".join(cmds))
    print("Out: \n", stdout)
    print("Err: \n", stderr)
    print("Code: \n", p.returncode)
    return stdout, stderr, p.returncode


def sync_website_content(
    username: str,
    token: str,
    source_repo: str,
    source_folder: str,
    source_ref: str,
    translations_repo: str,
    translations_folder: str,
    translations_ref: str,
    name: str,
    email: str,
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
    source_folder : str
        Source folder name.
    source_ref : str
        Source branch name.
    translations_repo : str
        Translations repository name.
    translations_folder : str
        Translations folder name.
    translations_ref : str
        Translations source branch.
    name : str
        Name of the bot account.
    email : str
        Email of the bot account.
    """
    base_folder = Path(os.getcwd())
    source_folder_path = base_folder / source_folder
    translations_folder_path = base_folder / translations_folder
    print("\n\n### Syncing content from source repository to translations repository.\n\n")
    print("Base folder: ", base_folder)
    print("Source folder: ", source_folder_path)
    print("Translation folder: ", translations_folder_path)
    run(["git", "config", "--global", "user.name", f'"{name}"'])
    run(["git", "config", "--global", "user.email", f'"{email}"'])

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

    date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    branch_name = f"content-sync-{date_time}"
    os.chdir(translations_repo.split("/")[1])
    print("\n\ngetcwd:", os.getcwd())
    run(["git", "checkout", "-b", branch_name])

    # os.chdir(translations_folder)
    # FIXME: If on the same level do this, otherwise no parent?
    run(["rsync", "-avr", "--delete", str(source_folder_path), str(translations_folder_path.parent)])
    run(["git", "status"])

    run(["git", "add", "."])
    _out, _err, rc = run(["git", "diff", "--staged", "--quiet"])

    pr_title = "Update content"
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if rc:
        run(["git", "commit", "-S", "-m", "Update content."])
        run(["git", "remote", "-v"])
        run(["git", "push", "-u", "origin", branch_name])

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
            ]
        )
        os.environ["GITHUB_TOKEN"] = github_token

        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo(translations_repo)
        pulls = repo.get_pulls(state="open", sort="created", direction="desc")
        pr_branch = None
        signed_by = f"{name} <{email}>"

        for pr in pulls:
            pr_branch = pr.head.ref
            if pr.title == pr_title and pr_branch == branch_name:
                print("\n\nFound PR try to merge it!")

                # Check if commits are signed
                checks = []
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

                # if all(checks):
                #     print("\n\nAll commits are signed, auto-merging!")
                #     # https://cli.github.com/manual/gh_pr_merge
                #     os.environ["GITHUB_TOKEN"] = token
                #     run(
                #         [
                #             "gh",
                #             "pr",
                #             "merge",
                #             branch_name,
                #             "--auto",
                #             "--squash",
                #             "--delete-branch",
                #         ]
                #     )
                # else:
                #     print("\n\nNot all commits are signed, abort merge!")

                break

        g.close()
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
        "source_folder": os.environ["INPUT_SOURCE-FOLDER"],
        "source_ref": os.environ["INPUT_SOURCE-REF"],
        "translations_repo": os.environ["INPUT_TRANSLATIONS-REPO"],
        "translations_folder": os.environ["INPUT_TRANSLATIONS-FOLDER"],
        "translations_ref": os.environ["INPUT_TRANSLATIONS-REF"],
        # Provided by gpg action based on organization secrets
        "name": os.environ["GPG_NAME"],
        "email": os.environ["GPG_EMAIL"],
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

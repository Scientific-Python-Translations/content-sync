import os
from datetime import datetime
from subprocess import Popen, PIPE

from github import Github, Auth


# Set the output value by writing to the outputs in the Environment File, mimicking the behavior defined here:
#  https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-output-parameter
def set_github_action_output(output_name, output_value):
    f = open(os.path.abspath(os.environ["GITHUB_OUTPUT"]), "a")
    f.write(f'{output_name}={output_value}')
    f.close()    


def run(cmds, with_token=False):
    p = Popen(cmds, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    print('\n\n' + ' '.join(cmds))
    print('Out: ', out.decode())
    print('Err: ', err.decode())
    print('Code: ', p.returncode)
    return out, err, p.returncode


def sync_website_content(username, token, source_repo, source_folder, source_ref, translations_repo, translations_folder, translations_ref, name, email):
    run(['git', 'config', '--global', 'user.name', f'"{name}"'])
    run(['git', 'config', '--global', 'user.email', f'"{email}"'])

    if source_ref:
        cmds = ['git', 'clone', '--single-branch', '-b', source_ref, f'https://{username}:{token}@github.com/{source_repo}.git']
    else:
        cmds = ['git', 'clone', f'https://{username}:{token}@github.com/{source_repo}.git']

    run(cmds)

    if translations_ref:
        cmds = ['git', 'clone', '-b', translations_ref, f'https://{username}:{token}@github.com/{translations_repo}.git']
    else:
        cmds = ['git', 'clone', f'https://{username}:{token}@github.com/{translations_repo}.git']

    run(cmds)
    run(['rsync', '-av', '--delete', source_folder, translations_folder])

    date_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    branch_name = f'content-sync-{date_time}'
    os.chdir(translations_repo.split('/')[1])
    print('\n\ngetcwd:', os.getcwd())
    
    run(['git', 'checkout', '-b', branch_name])
    run(['git', 'add', '.'])
    _out, _err, rc = run(['git', 'diff', '--staged', '--quiet' ])

    pr_title = "Update content"
    github_token = os.environ.get("GITHUB_TOKEN", '')
    if rc:
        run(['git', 'commit', '-S',  '-m', f"Update content."])
        run(['git', 'remote', '-v'])
        run(['git', 'push', '-u', 'origin', branch_name])

        os.environ["GITHUB_TOKEN"] = token
        run(['gh', 'pr', 'create', '--base', 'main', '--head', branch_name, '--title', pr_title, '--body', "Automated content update."])
        os.environ["GITHUB_TOKEN"] = github_token
    else:
        print("\n\nNo changes to commit.")

    auth = Auth.Token(github_token)
    g = Github(auth=auth)
    repo = g.get_repo(translations_repo)
    pulls = repo.get_pulls(state='open', sort='created', direction='desc')
    pr_branch = None
    signed_by = f"{name} <{email}>"
    for pr in pulls:
        # print(pr.number, pr.title)
        pr_branch = pr.head.ref
        if pr.title == pr_title and pr_branch == branch_name:
            print('\n\nFound PR try to merge it!')
    
        # Check if commits are signed
        checks = []
        for commit in pr.get_commits():
            print([commit.commit.verification.verified, signed_by, commit.commit.verification.payload])
            checks.append(commit.commit.verification.verified and signed_by in commit.commit.verification.payload)

        if all(checks):
            print('\n\nAll commits are signed, auto-merging!')
            # https://cli.github.com/manual/gh_pr_merge
            os.environ["GITHUB_TOKEN"] = token
            # run(['gh', 'pr', 'megre', branch_name, '--auto'])
            os.environ["GITHUB_TOKEN"] = token
        else:
            print('\n\nNot all commits are signed, abort merge!')

        break

    g.close()


def parse_input():
    gh_input = {
        'username': 'scientificpythontranslations',
        # Provided by organization secrets
        'token': os.environ["TOKEN"],
        # Provided by user action input
        'source_repo': os.environ["INPUT_SOURCE-REPO"],
        'source_folder': os.environ["INPUT_SOURCE-FOLDER"],
        'source_ref': os.environ["INPUT_SOURCE-REF"],
        'translations_repo': os.environ["INPUT_TRANSLATIONS-REPO"],
        'translations_folder': os.environ["INPUT_TRANSLATIONS-FOLDER"],
        'translations_ref': os.environ["INPUT_TRANSLATIONS-REF"],
        # Provided by gpg action based on organization secrets
        'name':os.environ["GPG_NAME"],
        'email': os.environ["GPG_EMAIL"],
    }
    return gh_input


def main():
    gh_input = parse_input()
    sync_website_content(**gh_input)


if __name__ == "__main__":
    main()

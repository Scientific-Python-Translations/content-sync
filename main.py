import os
from datetime import datetime
from subprocess import check_output, Popen, PIPE

from github import Github, Auth


# Set the output value by writing to the outputs in the Environment File, mimicking the behavior defined here:
#  https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-output-parameter
def set_github_action_output(output_name, output_value):
    f = open(os.path.abspath(os.environ["GITHUB_OUTPUT"]), "a")
    f.write(f'{output_name}={output_value}')
    f.close()    


def run(cmds):
    p = Popen(cmds, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    print('\n\n' + ' '.join(cmds))
    print('Out: ', out.decode())
    print('Err: ', err.decode())
    print('Code: ', p.returncode)
    return out, err, p.returncode


def sync_website_content(token, source_repo, source_folder, source_ref, translations_repo, translations_folder, translations_ref, name, email):
    username = 'goanpeca'
    run(['git', 'config', '--global', 'user.email', f'"{name}"'])
    run(['git', 'config', '--global', 'user.name', f'"{email}"'])

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
    print('getcwd:', os.getcwd())
    
    run(['git', 'checkout', '-b', branch_name])
    run(['git', 'add', '.'])
    _out, _err, rc = run(['git', 'diff', '--staged', '--quiet' ])

    if rc:
        run(['git', 'commit', '-S',  '-m', f"Update website content. {date_time}"])
        run(['git', 'remote', '-v'])
        run(['git', 'push', '-u', 'origin', branch_name])
    else:
        print("No changes to commit.")

    # FIXME: check other PRs and check the diff!
    # auth = Auth.Token(github_token)
    # g = Github(auth=auth)
    # repo = g.get_repo(translations_repo)
    # pulls = repo.get_pulls(state='closed', sort='created', direction='desc')
    # pr_branch = None
    # for pr in pulls:
    #     print(pr.number, pr.title)
    #     pr_branch = pr.head.ref
    #     if pr.title == "Update source content":
    #         break
    # g.close()

    # cmds = ['git', 'diff', f'{pr_branch}..{branch_name}']
    # out = check_output(cmds)
    # print(out)

    # ORIGINAL SCRIPT
    # git add .
    # # Only proceed to commit if there are changes
    # if git diff --staged --quiet; then
    # echo "No changes to commit."
    # echo "CONTENT_CHANGED=false" >> $GITHUB_ENV
    # else
    # git commit -m "Update website content"
    # echo "CONTENT_CHANGED=true" >> $GITHUB_ENV
    # git push -u origin ${{ env.BRANCH_NAME }}
    # fi

def parse_input():
    print(os.environ)
    gh_input = {
        'token': os.environ["TOKEN"],
        'source_repo': os.environ["INPUT_SOURCE-REPO"],
        'source_folder': os.environ["INPUT_SOURCE-FOLDER"],
        'source_ref': os.environ["INPUT_SOURCE-REF"],
        'translations_repo': os.environ["INPUT_TRANSLATIONS-REPO"],
        'translations_folder': os.environ["INPUT_TRANSLATIONS-FOLDER"],
        'translations_ref': os.environ["INPUT_TRANSLATIONS-REF"],
        'name':os.environ["GPG_NAME"],
        'email': os.environ["GPG_EMAIL"],
    }
    return gh_input


def main():
    gh_input = parse_input()
    sync_website_content(**gh_input)


if __name__ == "__main__":
    main()

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
    return out, err, p.returncode


def sync_website_content(github_token, source_repo, source_folder, source_ref, translations_repo, translations_folder, translations_ref):
    username = 'goanpeca'

    out, err, rc = run(['git', 'config', '--global', 'user.email', '"gonzalo.pena@quansight.com"'])
    print('git config', out, err)

    out, err, rc = run(['git', 'config', '--global', 'user.name', '"Scientific Python Translations"'])
    print('git config', out, err)

    if source_ref:
        cmds = ['git', 'clone', '--single-branch', '-b', source_ref, f'https://{username}:{github_token}@github.com/{source_repo}.git']
    else:
        cmds = ['git', 'clone', f'https://{username}:{github_token}@github.com/{source_repo}.git']

    out, err, rc = run(cmds)
    print('git clone source', out, err)

    if translations_ref:
        cmds = ['git', 'clone', '--single-branch', '-b', translations_ref, f'https://{username}:{github_token}@github.com/{translations_repo}.git']
    else:
        cmds = ['git', 'clone', f'https://{username}:{github_token}@github.com/{translations_repo}.git']

    out, err, rc = run(cmds)
    print('git clone translations', out, err)
    
    out, err, rc = run(['rsync', '-av', '--delete', source_folder, translations_folder])
    print('rsync', out, err)

    branch_name = datetime.now().strftime('content-sync-%Y-%m-%d-%H-%M-%S')
    os.chdir(translations_repo.split('/')[1])
    print('getcwd:', os.getcwd())
    
    out, err, rc = run(['git', 'checkout', '-b', branch_name])
    print('checkout', out, err)

    out, err, rc = run(['git', 'add', '.'])
    print('git add', out, err)

    out, err, rc = run(['git', 'diff', '--staged', '--quiet' ])
    print('git diff', out, err)

    if rc:
        out, err, rc = run(['git', 'commit', '-S',  '-m', "Update website content. This commit is signed!"])
        print('commit', out, err)

        out, err, rc = run(['git', 'remote', '-v'])
        print('remote', out, err)

        out, err, rc = run(['git', 'push', '-u', 'origin', branch_name])
        print('git push', out, err)
    else:
        print("No changes to commit.")

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
        'github_token': os.environ["GITHUB_TOKEN"],
        'source_repo': os.environ["INPUT_SOURCE-REPO"],
        'source_folder': os.environ["INPUT_SOURCE-FOLDER"],
        'source_ref': os.environ["INPUT_SOURCE-REF"],
        'translations_repo': os.environ["INPUT_TRANSLATIONS-REPO"],
        'translations_folder': os.environ["INPUT_TRANSLATIONS-FOLDER"],
        'translations_ref': os.environ["INPUT_TRANSLATIONS-REF"],
    }
    return gh_input


def main():
    gh_input = parse_input()
    print(gh_input)
    sync_website_content(**gh_input)


if __name__ == "__main__":
    main()

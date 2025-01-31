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


def sync_website_content(token, source_repo, source_folder, source_ref, translations_repo, translations_folder, translations_ref):
    cmds = ['git', 'clone', f'https://github.com/{source_repo}.git']
    out = check_output(cmds)
    print(out)

    cmds = ['git', 'clone', f'https://github.com/{translations_repo}.git']
    out = check_output(cmds)
    print(out)

    cmds = ['rsync', '-av', '--delete', source_folder, translations_folder]
    out = check_output(cmds)
    print(out)

    branch_name = datetime.now().strftime('updates-%Y-%m-%d-%H-%M-%S')
    os.chdir(translations_repo.split('/')[1])
    
    cmds = ['git', 'checkout', '-b', branch_name]
    out = check_output(cmds)
    print(out)

    cmds = ['git', 'config', '--global', 'user.email', '"actions@github.com"']
    out = check_output(cmds)
    print(out)

    cmds = ['git', 'config', '--global', 'user.name', '"GitHub Actions"']
    out = check_output(cmds)
    print(out)

    cmds = ['git', 'add', '.']
    out = check_output(cmds)
    print(out)

    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_repo(translations_repo)
    pulls = repo.get_pulls(state='closed', sort='created', direction='desc')
    pr_branch = None
    for pr in pulls:
        print(pr.number, pr.title)
        pr_branch = pr.head.ref
        if pr.title == "Update source content":
            break
    g.close()

    # cmds = ['git', 'diff', f'{pr_branch}..{branch_name}']
    # out = check_output(cmds)
    # print(out)

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
    github_token = os.environ["GITHUB_TOKEN"]
    source_repo = os.environ["INPUT_SOURCE-REPO"]
    source_folder = os.environ["INPUT_SOURCE-FOLDER"]
    source_ref = os.environ["INPUT_SOURCE-REF"]
    translations_repo = os.environ["INPUT_TRANSLATIONS-REPO"]
    translations_folder = os.environ["INPUT_TRANSLATIONS-FOLDER"]
    translations_ref = os.environ["INPUT_TRANSLATIONS-REF"]

    # repository = os.environ["GITHUB_REPOSITORY"]

    sync_website_content(github_token, source_repo, source_folder, source_ref, translations_repo, translations_folder, translations_ref)
    set_github_action_output('todo', 'Hello world')
    print("TESTING")


if __name__ == "__main__":
    main()

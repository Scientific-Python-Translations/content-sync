# content-sync

**A GitHub Action to synchronize translatable content from Scientific Python projects to their corresponding translation repositories.**

This action automates the process of copying source content (e.g., HTML or Markdown files) from an upstream project repository into a dedicated translations repository. It is designed to work seamlessly with the [Scientific Python Translations](https://scientific-python-translations.github.io/) infrastructure and integrates with [Crowdin](https://crowdin.com/) for managing translations.

---

## 📦 Features

- **Automated Content Syncing**: Periodically syncs specified folders from the source repository to the translations repository.
- **Customizable Configuration**: Supports specifying source repository, folder paths, branches, and more.
- **Integration with Crowdin**: Prepares content in a format suitable for Crowdin translation workflows.
- **GitHub Actions Workflow**: Easily integrate into existing CI/CD pipelines using GitHub Actions.

## 🚀 Getting Started

### Prerequisites

- A GitHub repository containing the source content you wish to translate.
- A separate translations repository set up to receive and manage translated content part of the Scientific Python Translations organization.
- GitHub Actions enabled on the translations repository.

## ⚙️ Usage

### Basic Example

Here's a sample GitHub Actions workflow that uses the `content-sync` action to sync content from the `main` branch of the `numpy/numpy.org` repository:

```yaml
name: Sync Content

on:
  schedule:
    - cron: "0 12 * * MON" # Every Monday at noon
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Sync Pandas Content
        uses: Scientific-Python-Translations/content-sync@main
        with:
          source-repo: "numpy/numpy.org"
          source-folder: "content/en/"
          source-ref: "main"
          translations-repo: "Scientific-Python-Translations/numpy.org-translations"
          translations-folder: "content/en/"
          translations-ref: "main"
          # These are provided by the Scientific Python Project and allow
          # automation with bots
          gpg_private_key: ${{ secrets.GPG_PRIVATE_KEY }}
          passphrase: ${{ secrets.PASSPHRASE }}
          token: ${{ secrets.TOKEN }}
```

### Inputs

| Input                 | Required | Default | Description                                                                |
| --------------------- | -------- | ------- | -------------------------------------------------------------------------- |
| `source-repo`         | ✅       | —       | GitHub repo with the source content (e.g., `numpy/numpy.org`).             |
| `source-folder`       | ✅       | —       | Path to the content folder in the source repo (e.g., `content/en/`).       |
| `source-ref`          | ❌       | `main`  | Branch or tag to sync from.                                                |
| `translations-repo`   | ✅       | —       | Target repo for translated content (e.g., `org/site-translations`).        |
| `translations-folder` | ✅       | -       | Path to the content folder in the translations repo (e.g., `content/en/`). |
| `translations-ref`    | ❌       | `main`  | Branch of the target translations repo.                                    |

## 🛠️ Setup Instructions

1. **Create a Translations Repository**: Set up a separate repository to hold the translated content. You can use the [translations-cookiecutter](https://github.com/Scientific-Python-Translations/translations-cookiecutter) as template for the repository.

2. **Configure Crowdin**: Integrate your translations repository with Crowdin to manage translations. Ensure that the `translations-folder` is set up correctly for Crowdin.

3. **Set Up the Workflow**: Add the above GitHub Actions workflow to your source repository (e.g., `.github/workflows/sync-content.yml`). This is created automatically if you used the `translations-cookiecutter`.

## 🔄 How It Works

1. **Checkout Source Repository**: The action checks out the specified `source-repo` and `source-ref`.

2. **Copy Content**: It copies the contents of `source-folder` from the source repository.

3. **Checkout Translations Repository**: The action checks out the specified `translations-repo` and `translations-ref`.

4. **Place Synced Content**: It places the copied content into the specified `translations-folder` within the translations repository.

5. **Commit and PR Creation**: The action commits the changes with the specified and creates a Pull Request with signed commits and performs and automatic merge.

## 🤖 Bot Activity

All synchronization pull requests and automated commits are performed by the dedicated bot account:
[@scientificpythontranslations](https://github.com/scientificpythontranslations)

This ensures consistent and traceable contributions from a centralized automation identity.
If you need to grant permissions or configure branch protection rules, make sure to allow actions and PRs from this bot.

## 🙌 Community & Support

- Join the [Scientific Python Discord](https://scientific-python.org/community/) and visit the `#translation` channel
- Browse the [Scientific Python Translations documentation](https://scientific-python-translations.github.io/docs/)
- Visit the [content-sync](https://github.com/Scientific-Python-Translations/content-sync) and [translations-sync](https://github.com/Scientific-Python-Translations/translations-sync) Github actions.

## 🤝 Contributing

Contributions are welcome! Please open an [issue](https://github.com/Scientific-Python-Translations/content-sync/issues) or submit a pull request for any enhancements or bug fixes.

## 📄 License

This project is licensed under the [MIT License](LICENSE.txt).

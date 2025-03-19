# content-sync

A Github action to sync translatable content from various Scientific python projects.

## Examples

### Example 1: Pandas content sync

```yaml
name: Sync Content
on:
  schedule:
    - cron: '0 12 * * MON'  # Every Monday at noon
  workflow_dispatch:on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Sync Pandas Content
        uses: Scientific-Python-Translations/content-sync@main
        with:
          source-repo: "pandas-dev/pandas"
          source-folder: "pandas/web/pandas/"
          source-ref: "main"
          translations-repo: "Scientific-Python-Translations/pandas-translations"
          translations-folder: "pandas-translations/content/en/"
          translations-ref: "main"
          # These are provided by the Scientific Python Project and allow
          # automation with bots
          gpg_private_key: ${{ secrets.GPG_PRIVATE_KEY }}
          passphrase: ${{ secrets.PASSPHRASE }}
          token: ${{ secrets.TOKEN }}
```

### Example 2: Scipy.org content sync

```yaml
name: Sync Content
on:
  schedule:
    - cron: '0 5 * * *'  # Daily at 5 am
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Sync Scipy Content
        uses: Scientific-Python-Translations/content-sync@main
        with:
          source-repo: "scipy/scipy.org"
          source-folder: "scipy.org/content/en/"
          source-ref: "main"
          translations-repo: "Scientific-Python-Translations/scipy.org-translations"
          translations-folder: "scipy.org-translations/content/en/"
          translations-ref: "main"
          # These are provided by the Scientific Python Project and allow
          # automation with bots
          gpg_private_key: ${{ secrets.GPG_PRIVATE_KEY }}
          passphrase: ${{ secrets.PASSPHRASE }}
          token: ${{ secrets.TOKEN }}
```

## Automations Bot (@scientificpythontranslations)

[Bot account](https://github.com/ScientificPythonTranslations).

## License

The scripts and documentation in this project are released under the [MIT License](https://github.com/Scientific-Python-Translations/translations-sync/blob/main/LICENSE.txt).

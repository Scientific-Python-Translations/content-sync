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
  sync:
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
  sync:
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

### Example 3: Networkx content sync

```yaml
name: Sync Content
on:
  schedule:
    - cron: '0 5 * * *'  # Daily at 5 am
  workflow_dispatch:
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Sync Networkx Content
        uses: Scientific-Python-Translations/content-sync@main
        with:
          source-repo: "networkx/website"
          source-folder: "website/build/"
          source-ref: "main"
          translations-repo: "Scientific-Python-Translations/networkx-website-translations"
          translations-folder: "networkx-website-translations/content/en/"
          translations-ref: "main"
          # These are provided by the Scientific Python Project and allow
          # automation with bots
          gpg_private_key: ${{ secrets.GPG_PRIVATE_KEY }}
          passphrase: ${{ secrets.PASSPHRASE }}
          token: ${{ secrets.TOKEN }}
```

### Example 4: Zarr content sync

```yaml
name: Sync Content
on:
  schedule:
    - cron: '0 5 * * *'  # Daily at 5 am
  workflow_dispatch:
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Sync Zarr Content
        uses: Scientific-Python-Translations/content-sync@main
        with:
          source-repo: "zarr-developers/zarr-developers.github.io"
          source-folder: "zarr-developers.github.io/"
          source-ref: "main"
          translations-repo: "Scientific-Python-Translations/zarr.dev-translations"
          translations-folder: "zarr.dev-translations/content/en/"
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

The scripts and documentation in this project are released under the [MIT License](https://github.com/Scientific-Python-Translations/content-sync/blob/main/LICENSE.txt).

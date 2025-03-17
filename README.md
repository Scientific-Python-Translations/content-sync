# content-sync

A Github action to sync translatable content from various Scientific python projects.

## Examples

### Example 1: Pandas content sync

```yaml
name: Sync Pandas Content
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

## Automations Bot (@scientificpythontranslations)

[Bot account](https://github.com/ScientificPythonTranslations).

## License

The scripts and documentation in this project are released under the [MIT License](https://github.com/Scientific-Python-Translations/translations-sync/blob/main/LICENSE.txt).

# Poetry release

[![CI](https://github.com/topenkoff/poetry-release/actions/workflows/tests.yml/badge.svg)](https://github.com/topenkoff/poetry-release/actions?query=workflow)

Release managment plugin for poetry

*The project is currently under development and is not ready for use in production.*

Inspired by [cargo-release](https://github.com/sunng87/cargo-release)

## Features
- [x] [Semver](https://semver.org/) support
- [x] Creating git tag and commits after release
- [x] [Changelog](https://keepachangelog.com/en/1.0.0/) support

## Installation
**Note:** Plugins work at Poetry with version 1.2.0a1 or above.
```bash
poetry add poetry-release
```

## Usage
```bash
poetry release <level>
```
Existing levels
 - major
 - minor
 - patch
 - release (default)
 - rc
 - beta
 - alpha

### Prerequisite
Your project should be managed by git.

## Config
### Replacements
Poetry-release supports two types of release replacements:
1. By Regex
You can create replacements in files using regular expressions:
```toml
release-replacements = [
    { file="CHANGELOG.md", pattern="\\[Unreleased\\]", replace="[{version}] - {date}" },
]
```
2. Message replacements

You can set the text for release messages:
| Replacement                   | Description                                      |
|-------------------------------|--------------------------------------------------|
| `release-commit-message`      | Message for release commit                       |
| `post-release-commit-message` | Message for post release commit(if it's allowed) |
| `tag-name`                    | The name of tag                                  |
| `tag-message`                 | The message for tag                              |

### Templates
Poetry-release supports templates to build releases. Templates could be used in release replacements/messages/tags. Template is indicated like `some text {package_name}`
| Template       | Description                                        |
|----------------|----------------------------------------------------|
| `package_name` | The name of this project in `pyproject.toml`       |
| `prev_version` | The project version before release                 |
| `version`      | The bumped project version                         |
| `next_version` | The version for next development iteration (alpha) |
| `date`         | The current date in `%Y-%m-%d` format              |

### Release settings
These settings allow you to disable part of the functionality. They can be set either in `pyproject.toml` or in CLI like flag.
| Settings       | Default | Description                     |
|----------------|---------|---------------------------------|
| `disable-push` | false   | Don't do git push               | 
| `disable-tag`  | false   | Don't do git tag                |
| `disable-dev`  | false   | Skip bump version after release |

#### Default git messages
* Tag name - `{version}`
* Tag message - `Released {package_name} {version}`
* Release commit - `Released {package_name} {version}`
* Post release commit - `Starting {package_name}'s next development iteration {next_version}`

### Example
```toml
[tool.poetry-release]
release-replacements = [
    { file="CHANGELOG.md", pattern="\\[Unreleased\\]", replace="[{version}] - {date}" },
    { file="CHANGELOG.md", pattern="\\(https://semver.org/spec/v2.0.0.html\\).", replace="(https://semver.org/spec/v20.0.html).\n\n## [Unreleased]"},
]
disable-push = false
disable-tag = false
disable-dev = false
release-commit-message = "Release {package_name} {version}"
post-release-commit-message = "Start next development iteration {next_version}"
tag-name = "{version}"
```

```bash
poetry release minor --disable-dev --disable-tag
```

# Poetry release

Release managment plugin for poetry
*The project is currently under development and is not ready for use in production.*
Inspired by [cargo-release](https://github.com/sunng87/cargo-release)

## Features
- [x] [Semver](https://semver.org/) support
- [x] Creating git tag and commits after release
- [x] [Changelog](https://keepachangelog.com/en/1.0.0/) support

## Installation
**Note: ** Plugins work at Poetry with version 1.2.0a1 or above.
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
Part of config is being able to set in `pyproject.toml`
```toml
[tool.poetry-release]
release-replacements = [
    { file="CHANGELOG.md", pattern="\\[Unreleased\\]", replace="[{version}] - {date}" },
    { file="CHANGELOG.md", pattern="\\(https://semver.org/spec/v2.0.0.html\\).", replace="(https://semver.org/spec/v20.0.html).\n\n## [Unreleased]"},
]
disable-push = false
disable-tag = false
disable-dev = false
release-commit-message = "Released package"
post-release-commit-message = "Next development iteration"
tag-name = "v{version}"
```
Part of config is being able to set in CLI
```bash
poetry release minor --disable-push --disable-dev --disable-tag
```

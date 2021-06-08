from dataclasses import dataclass
from typing import List, Optional

from cleo.commands.command import Command   # type: ignore

from poetry_release.changelog import Replacement


@dataclass
class ReleaseSettings:
    disable_push: bool
    disable_tag: bool
    disable_dev: bool
    tag_name: Optional[str]
    release_commit_message: Optional[str]
    post_release_commit_message: Optional[str]
    release_replacements: List[Replacement]

    def __init__(self, cmd: Command):
        pyproject_settings = cmd.application. \
            poetry.file.read()["tool"].get("poetry-release", {})
        self.disable_push = cmd.option('disable-push') \
            or pyproject_settings.get('disable-push', False) \
            or False
        self.disable_tag = cmd.option('disable-tag') \
            or pyproject_settings.get('disable-tag', False) \
            or False
        self.disable_dev = cmd.option('disable-dev') \
            or pyproject_settings.get('disable-dev', False) \
            or False
        self.tag_name = pyproject_settings.get('tag-name')
        self.release_commit_message = pyproject_settings.get(
            'release-commit-message'
        )
        self.post_release_commit_message = pyproject_settings.get(
            'post-release-commit-message'
        )

        release_replacements = pyproject_settings.get(
            'release-replacements'
        ) or []
        self.release_replacements = [
            Replacement(**r) for r in release_replacements
        ]

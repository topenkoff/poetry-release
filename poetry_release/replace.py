from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from poetry_release.config import Config


@dataclass
class Template:
    package_name: str
    prev_version: str
    version: str
    next_version: str
    date: str

    def dict(self) -> dict[str, str]:
        return self.__dict__


@dataclass
class Replacement:
    file: str
    pattern: str
    replace: str

    def update(self, template: Template) -> None:
        with open(self.file, "r") as read_changelog:
            content = read_changelog.read()
            replace = self.replace.format_map(template.dict())
            content_new = re.sub(self.pattern, replace, content, flags=re.M)
        with open(self.file, "w") as write_changelog:
            write_changelog.write(content_new)


@dataclass
class GitMessages:
    tag_name: str = field(default="{version}")
    tag_message: str = field(default="Release {package_name} {version}")
    release_commit: str = field(default="Release {package_name} {version}")
    post_release_commit: str = field(
        default=(
            "Starting {package_name}'s next development "
            "iteration {next_version}"
        )
    )

    def fill_template(self, template: Template) -> None:
        for field_name in self.__dataclass_fields__.keys():
            setattr(
                self,
                field_name,
                self.__getattribute__(field_name).format_map(template.dict()),
            )


class Replacer:
    def __init__(self, template: Template, config: Config) -> None:
        self.template = template
        self.config = config
        self.replacements = [
            Replacement(**r) for r in self.config.release_replacements
        ]

    def update_replacements(self) -> None:
        for replacement in self.replacements:
            replacement.update(self.template)

    def generate_messages(self) -> GitMessages:
        messages = GitMessages()

        if self.config.release_commit_message is not None:
            messages.release_commit = self.config.release_commit_message

        if self.config.post_release_commit_message is not None:
            messages.post_release_commit = (
                self.config.post_release_commit_message
            )

        if self.config.tag_name is not None:
            messages.tag_name = self.config.tag_name

        # changelog = self.get_changelog()
        # if changelog is not None:
        #    messages.tag_message = changelog
        if self.config.tag_message is not None:
            messages.tag_message = self.config.tag_message

        messages.fill_template(self.template)

        return messages

    # def get_changelog(self) -> Optional[str]:
    #     with open("CHANGELOG.md", "r") as read_changelog:
    #         content = read_changelog.read()
    #         version = self.template.version
    #         pattern = re.compile(
    #             "(?:##.\[%s\].-.\d{4}-\d{2}-\d{2})(\n###.*?)(\n\n##.\[|$)"
    #             % version,
    #             flags=re.S,
    #         )
    #         result = pattern.search(content)
    #         if result is not None:
    #             return result.group(1)
    #         else:
    #             return None

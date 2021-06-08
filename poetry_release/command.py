from enum import Enum
from datetime import datetime

from cleo.commands.command import Command   # type: ignore
from cleo.helpers import argument, option   # type: ignore
from poetry.core.semver.version import Version  # type: ignore
from poetry.core.version.exceptions import InvalidVersion   # type: ignore
from poetry.core.version.pep440 import ReleaseTag   # type: ignore
from poetry.poetry import Poetry    # type: ignore

from poetry_release.git import ReleaseGit
from poetry_release.exception import UpdateVersionError
from poetry_release.settings import ReleaseSettings
from poetry_release.changelog import Templates

class ReleaseLevel(str, Enum):

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    ALPHA = "alpha"
    BETA = "beta"
    RC = "rc"
    RELEASE = "release"


    @classmethod
    def parse(cls, version: str) -> "ReleaseLevel":
        if version == cls.MAJOR:
            return cls.MAJOR
        elif version == cls.MINOR:
            return cls.MINOR
        elif version == cls.PATCH:
            return cls.PATCH
        elif version == cls.ALPHA:
            return cls.ALPHA
        elif version == cls.BETA:
            return cls.BETA
        elif version == cls.RC:
            return cls.RC
        elif version == cls.RELEASE:
            return cls.RELEASE
        else:
            raise InvalidVersion(
                "Unsupported release level. Choose one of: "
                "major, minor, patch, release, rc, beta, alpha. "
                "Or set <release_level> empty"
            )


class ReleaseCommand(Command):

    name = "release"

    description = (
        "Plugin for release management in projects "
        "based on Poetry"
    )

    arguments = [
        argument(
            "level",
            description="Release level",
            optional=True,
            default=ReleaseLevel.RELEASE.value,
        )
    ]

    options = [
        option(
            "disable-push",
            description="Disable push commits and tags in repository",
            flag=True,
            value_required=False,
        ),
        option(
            "disable-tag",
            description="Disable creating git tags",
            flag=True,
            value_required=False,
        ),
        option(
            "disable-dev",
            description="Disable bump version after stable release",
            flag=True,
            value_required=False,
        )
    ]

    help = """\
  The release command helps you to control your project version.
  It allows bump version, create tags and commit and push them 
  to project repository. Supported release levels are:
     major, minor, patch, release, rc, beta, alpha
  """


    def handle(self) -> None:
        try:
            poetry = self.application.poetry
            next_release = ReleaseLevel.parse(self.argument("level"))
            settings = ReleaseSettings(self)
            git = ReleaseGit()
            if not git.repo_exists:
                self.line(
                    "<fg=yellow>Git repository not found. "
                    "Please initialize repository in your project"
                )
                return
            if git.has_modified():
                self.line(
                    "<fg=yellow>There are uncommitted changes "
                    "in the repository. Please make a commit</>"
                )
                return

            current_version = poetry.package.version
            next_version = self.increment_version(
                current_version, next_release
            )
            if not self.confirm(
                    f'Release {poetry.package.name} {next_version.text}?',
                    False, '(?i)^(y|j)'
                ):
                return

            self.set_version(poetry, next_version.text)

            templates = Templates(
                package_name=poetry.package.name,
                version=next_version.text,
                date=datetime.today().strftime("%Y-%m-%d"),
            )

            if settings.release_commit_message is None:
                commit_message = "Released {package_name} {next_version}"
            else:
                commit_message = settings.release_commit_message
            commit_message = commit_message.format_map(templates)

            if settings.tag_name is None:
                tag_name = next_version.text
            else:
                tag_name = settings.tag_name
            tag_name = tag_name.format_map(templates)
            tag_message = commit_message
            for replacement in settings.release_replacements:
                replacement.update(templates)

            git.create_commit(commit_message)
            if not settings.disable_push:
                git.push_commit()

            if next_version.is_stable():
                if not settings.disable_tag:
                    tag_message = commit_message
                    git.create_tag(tag_name, tag_message)
                    if not settings.disable_push:
                        git.push_tag(tag_name)

                if not settings.disable_dev:
                    next_version = next_version.next_patch().first_prerelease()
                    self.set_version(poetry, next_version.text)
                    next_release_message = (
                        f"Starting {poetry.package.name}'s next "
                        f"development iteration {next_version.text}"
                    )
                    git.create_commit(next_release_message)
                    if not settings.disable_push:
                        git.push_commit()

        except RuntimeError as e:
            self.line(f"<fg=red>{e}</>")
        except InvalidVersion as e:
            self.line(f"<fg=yellow>{e}</>")
        except UpdateVersionError as e:
            self.line(f"<fg=yellow>{e}</>")

    def increment_version(
            self,
            current_version: Version,
            next_release: ReleaseLevel
        ) -> Version:
        if next_release is ReleaseLevel.MAJOR:
            return current_version.next_major()

        elif next_release is ReleaseLevel.MINOR:
            return current_version.next_minor()

        elif next_release is ReleaseLevel.PATCH:
            return current_version.next_patch()

        elif next_release is ReleaseLevel.RC:
            return self.get_release_tag_version(
                current_version, next_release
            )

        elif next_release is ReleaseLevel.BETA:
            if current_version.is_unstable() \
                and current_version.pre.phase == ReleaseLevel.RC:
                raise UpdateVersionError(
                    "Prohibited to downgrade version: "
                    "major > minor > patch > release > rc > beta > alpha"
                )
            else:
                return self.get_release_tag_version(
                    current_version, next_release
                )

        elif next_release is ReleaseLevel.ALPHA:
            if current_version.is_unstable() and \
                current_version.pre.phase in (
                    ReleaseLevel.RC, ReleaseLevel.BETA
                ):
                raise UpdateVersionError(
                    "Prohibited to downgrade version: "
                    "major > minor > patch > release > rc > beta > alpha"
                )
            else:
                return self.get_release_tag_version(
                    current_version, next_release
                )
        else:
            return Version(current_version.epoch, current_version.release)

    def get_release_tag_version(
            self,
            current_version: Version,
            next_release: ReleaseLevel
        ) -> Version:
        if current_version.is_unstable() and \
                current_version.pre.phase != next_release:
            pre = ReleaseTag(next_release, 1)
        elif current_version.is_unstable():
            pre = current_version.pre.next()
        else:
            pre = ReleaseTag(next_release, 1)
        return Version(current_version.epoch, current_version.release, pre)

    def set_version(self, poetry: Poetry, version: str) -> None:
        content = poetry.file.read()
        poetry_content = content["tool"]["poetry"]
        poetry_content["version"] = version
        poetry.file.write(content)


def release_factory() -> ReleaseCommand:
    return ReleaseCommand()


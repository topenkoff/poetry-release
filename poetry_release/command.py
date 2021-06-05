from enum import Enum

from cleo.commands.command import Command
from cleo.helpers import argument
from poetry.core.semver.version import Version
from poetry.core.version.exceptions import InvalidVersion
from poetry.core.version.pep440 import ReleaseTag
from poetry.poetry import Poetry

from poetry_release.exception import UpdateVersionError


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

    description = "some_description"

    arguments = [
        argument(
            name="level",
            description="Release level",
            multiple=False,
            optional=True,
            default=ReleaseLevel.RELEASE.value,
        )
    ]

    help = "some_help"


    def handle(self) -> None:
        try:
            poetry = self.application.poetry
            package = poetry.package
            next_release = ReleaseLevel.parse(self.argument("level"))
            current_version = package.version
            next_version = self.increment_version(
                current_version, next_release
            )
            if not self.confirm(
                    f'Release {package.name} {next_version.text}?',
                    False, '(?i)^(y|j)'
                ):
                return
            self.set_version(poetry, next_version.text)
            if next_version.is_stable():
                next_version = next_version.next_patch().first_prerelease()
                self.set_version(poetry, next_version.text)

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


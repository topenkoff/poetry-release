from enum import Enum
from typing import Optional

from poetry.core.semver.version import Version
from poetry.core.version.exceptions import InvalidVersion
from poetry.core.version.pep440 import ReleaseTag

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


class ReleaseVersion:

    def __init__(
        self,
        version: Version,
        release_level: ReleaseLevel,
    ) -> None:
        self.version = version
        self.release_level = release_level

    def __increment_version(self) -> Version:
        if self.release_level is ReleaseLevel.MAJOR:
            return self.version.next_major()

        elif self.release_level is ReleaseLevel.MINOR:
            return self.version.next_minor()

        elif self.release_level is ReleaseLevel.PATCH:
            return self.version.next_patch()

        elif self.release_level is ReleaseLevel.RC:
            return self.__get_release_tag_version()

        elif self.release_level is ReleaseLevel.BETA:
            if self.version.is_unstable() \
                    and self.version.pre.phase == ReleaseLevel.RC:
                raise UpdateVersionError(
                    "Prohibited to downgrade version: "
                    "major > minor > patch > release > rc > beta > alpha"
                )
            else:
                return self.__get_release_tag_version()

        elif self.release_level is ReleaseLevel.ALPHA:
            if self.version.is_unstable() and \
                self.version.pre.phase in (
                    ReleaseLevel.RC, ReleaseLevel.BETA
            ):
                raise UpdateVersionError(
                    "Prohibited to downgrade version: "
                    "major > minor > patch > release > rc > beta > alpha"
                )
            else:
                return self.__get_release_tag_version()
        else:
            return Version(self.version.epoch, self.version.release)

    def __get_release_tag_version(self) -> Version:
        if self.version.is_unstable() and \
                self.version.pre.phase != self.release_level:
            pre = ReleaseTag(self.release_level, 1)
        elif self.version.is_unstable():
            pre = self.version.pre.next()
        else:
            pre = ReleaseTag(self.release_level, 1)
        return Version(self.version.epoch, self.version.release, pre)

    @property
    def current_version(self) -> Version:
        return self.version

    @property
    def next_version(self) -> Version:
        return self.__increment_version()

    @property
    def next_pre_version(self) -> Optional[Version]:
        next_version = self.__increment_version()
        if next_version.is_unstable():
            return None
        return next_version.next_patch().first_prerelease()

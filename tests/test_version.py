import pytest

from poetry.core.semver.version import Version

from poetry_release.version import ReleaseVersion, ReleaseLevel
from poetry_release.exception import UpdateVersionError


@pytest.mark.parametrize(
    "version,    level,                 next_version,   has_next, next_pre", [

    ("0.0.1",    ReleaseLevel.MAJOR,    "1.0.0",        False,    "1.0.1a0"),
    ("0.0.1",    ReleaseLevel.MINOR,    "0.1.0",        False,    "0.1.1a0"),
    ("0.0.1",    ReleaseLevel.PATCH,    "0.0.2",        False,    "0.0.3a0"),
    ("0.0.1",    ReleaseLevel.RELEASE,  "0.0.1",        False,    "0.0.2a0"),
    ("0.0.1",    ReleaseLevel.RC,       "0.0.1rc1",     True,     ""),
    ("0.0.1",    ReleaseLevel.BETA,     "0.0.1b1",      True,     ""),
    ("0.0.1",    ReleaseLevel.ALPHA,    "0.0.1a1",      True,     ""),
    ("0.0.1rc0", ReleaseLevel.MAJOR,    "1.0.0",        False,    "1.0.1a0",),
    ("0.0.1rc0", ReleaseLevel.MINOR,    "0.1.0",        False,    "0.1.1a0",),
    ("0.0.1rc0", ReleaseLevel.PATCH,    "0.0.1",        False,    "0.0.2a0",),
    ("0.0.1rc0", ReleaseLevel.RELEASE,  "0.0.1",        False,    "0.0.2a0",),
    ("0.0.1rc0", ReleaseLevel.RC,       "0.0.1rc1",     True,     ""),
    ("0.0.1b0",  ReleaseLevel.MAJOR,    "1.0.0",        False,    "1.0.1a0"),
    ("0.0.1b0",  ReleaseLevel.MINOR,    "0.1.0",        False,    "0.1.1a0"),
    ("0.0.1b0",  ReleaseLevel.PATCH,    "0.0.1",        False,    "0.0.2a0"),
    ("0.0.1b0",  ReleaseLevel.RELEASE,  "0.0.1",        False,    "0.0.2a0"),
    ("0.0.1b0",  ReleaseLevel.RC,       "0.0.1rc1",     True,     ""),
    ("0.0.1b0",  ReleaseLevel.BETA,     "0.0.1b1",      True,     ""),

    ("0.1.0",    ReleaseLevel.MAJOR,    "1.0.0",        False,    "1.0.1a0"),
    ("0.1.0",    ReleaseLevel.MINOR,    "0.2.0",        False,    "0.2.1a0"),
    ("0.1.0",    ReleaseLevel.PATCH,    "0.1.1",        False,    "0.1.2a0"),
    ("0.1.0",    ReleaseLevel.RELEASE,  "0.1.0",        False,    "0.1.1a0"),
    ("0.1.0",    ReleaseLevel.RC,       "0.1.0rc1",     True,     ""),
    ("0.1.0",    ReleaseLevel.BETA,     "0.1.0b1",      True,     ""),
    ("0.1.0",    ReleaseLevel.ALPHA,    "0.1.0a1",      True,     ""),
    ("0.1.0rc0", ReleaseLevel.MAJOR,    "1.0.0",        False,    "1.0.1a0"),
    ("0.1.0rc0", ReleaseLevel.MINOR,    "0.1.0",        False,    "0.1.1a0"),
    ("0.1.0rc0", ReleaseLevel.PATCH,    "0.1.0",        False,    "0.1.1a0"),
    ("0.1.0rc0", ReleaseLevel.RELEASE,  "0.1.0",        False,    "0.1.1a0"),
    ("0.1.0rc0", ReleaseLevel.RC,       "0.1.0rc1",     True,     ""),
    ("0.1.0b0", ReleaseLevel.MAJOR,     "1.0.0",        False,    "1.0.1a0"),
    ("0.1.0b0", ReleaseLevel.MINOR,     "0.1.0",        False,    "0.1.1a0"),
    ("0.1.0b0", ReleaseLevel.PATCH,     "0.1.0",        False,    "0.1.1a0"),
    ("0.1.0b0", ReleaseLevel.RELEASE,   "0.1.0",        False,    "0.1.1a0"),
    ("0.1.0b0", ReleaseLevel.RC,        "0.1.0rc1",     True,     ""),

    ("1.0.0",    ReleaseLevel.MAJOR,    "2.0.0",        False,    "2.0.1a0"),
    ("1.0.0",    ReleaseLevel.MINOR,    "1.1.0",        False,    "1.1.1a0"),
    ("1.0.0",    ReleaseLevel.PATCH,    "1.0.1",        False,    "1.0.2a0"),
    ("1.0.0",    ReleaseLevel.RELEASE,  "1.0.0",        False,    "1.0.1a0"),
    ("1.0.0",    ReleaseLevel.RC,       "1.0.0rc1",     True,     ""),
    ("1.0.0",    ReleaseLevel.BETA,     "1.0.0b1",      True,     ""),
    ("1.0.0",    ReleaseLevel.ALPHA,    "1.0.0a1",      True,     ""),

    #("1.0.0-rc.0", ReleaseLevel.MAJOR,    "2.0.0",        False,    "2.0.1a0"),
    #("1.0.0rc0", ReleaseLevel.MINOR,    "1.1.0",        False,    "1.1.1a0"),
    #("1.0.0rc0", ReleaseLevel.PATCH,    "1.0.0",        False,    "1.0.1a0"),
    #("1.0.0rc0", ReleaseLevel.RELEASE,  "1.0.0",        False,    "1.0.1a0"),
    #("1.0.0rc0", ReleaseLevel.RC,       "1.1.0rc1",     True,     ""),
    #("1.0.0b0", ReleaseLevel.MAJOR,     "2.0.0",        False,    "2.0.1a0"),
    #("1.0.0b0", ReleaseLevel.MINOR,     "1.1.0",        False,    "0.1.1a0"),
    #("1.0.0b0", ReleaseLevel.PATCH,     "1.1.0",        False,    "0.1.1a0"),
    #("1.0.0b0", ReleaseLevel.RELEASE,   "1.1.0",        False,    "0.1.1a0"),
    #("1.0.0b0", ReleaseLevel.RC,        "1.1.0rc1",     True,     ""),



])
def test_bump_version(version, level, next_version, has_next, next_pre):
    rversion = ReleaseVersion(
        Version.parse(version),
        level,
    )

    assert rversion.next_version == next_version
    assert rversion.has_next_pre_version == has_next
    if not rversion.has_next_pre_version:
        assert rversion.next_pre_version == next_pre

@pytest.mark.parametrize(
    "version,    level", [
    ("1.0.0rc0",  ReleaseLevel.ALPHA),
    ("1.0.0rc0",  ReleaseLevel.BETA),
    ("1.0.0-rc.0",  ReleaseLevel.ALPHA),
    ("1.0.0-rc.0",  ReleaseLevel.BETA),
    ("1.0.0b0",  ReleaseLevel.ALPHA),
    ("1.0.0-beta.0",  ReleaseLevel.ALPHA),
])
def test_uncorrect_bump_version(version, level):
    with pytest.raises(UpdateVersionError):
        rversion = ReleaseVersion(
            Version.parse(version),
            level,
        )
        rversion.next_version

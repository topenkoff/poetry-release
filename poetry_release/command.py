from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, cast

from cleo.helpers import argument, option
from poetry.console.commands.command import Command
from poetry.core.version.exceptions import InvalidVersion
from tomlkit.toml_document import TOMLDocument

from poetry_release import git
from poetry_release.config import Config
from poetry_release.exception import UpdateVersionError
from poetry_release.executor import Executor
from poetry_release.replace import Replacer, Template
from poetry_release.version import ReleaseLevel, ReleaseVersion

if TYPE_CHECKING:
    from typing import Any


class ReleaseCommand(Command):
    name = "release"

    description = "Plugin for release management in projects based on Poetry"

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
            description="Disable create git tags",
            flag=True,
            value_required=False,
        ),
        option(
            "disable-dev",
            description="Disable bump version after stable release",
            flag=True,
            value_required=False,
        ),
        option(
            "dry-run",
            description="Disable bump version after stable release",
            flag=True,
            value_required=False,
        ),
    ]

    help = """\
The release command helps you to control your project version.
It allows bump version, create tags and commit and push them
to project repository. Supported release levels are:
major, minor, patch, release, rc, beta, alpha.
"""

    def __init__(self) -> None:
        super().__init__()
        self.executor = Executor(
            self.io,
            self.option("dry-run"),
        )

    def handle(self) -> int:
        try:
            # Init config
            cfg = Config()

            pyproject = (
                self.poetry.file.read()
                .get("tool", {})
                .get("poetry-release", {})
            )
            pyproject_cfg = Config.from_pyproject(pyproject)
            cfg.update(pyproject_cfg)

            cli_cfg = Config.from_cli(self.option)
            cfg.update(cli_cfg)

            # Check git
            if not git.repo_exists():
                self.line(
                    "<fg=yellow>Git repository not found. "
                    "Please initialize repository in your project.</>"
                )
                return 1

            if git.has_modified():
                self.line(
                    "<fg=yellow>There are uncommitted changes "
                    "in the repository. Please make a commit.</>"
                )
                return 1

            release = ReleaseVersion(
                version=self.poetry.package.version,
                release_level=ReleaseLevel.parse(self.argument("level")),
            )

            if not self.confirm(
                (
                    f"Release {self.poetry.package.name} "
                    f"{release.next_version}?"
                ),
                False,
                "(?i)^(y|j)",
            ):
                return 1

            if release.current_version == release.next_version:
                self.line("<fg=yellow>Version doesn't changed.</>")
                return 1

            tmpl = Template(
                package_name=self.poetry.package.name,
                prev_version=release.current_version,
                version=release.next_version,
                next_version=release.next_pre_version
                if release.has_next_pre_version
                else "",
                date=datetime.today().strftime("%Y-%m-%d"),
            )

            replacer = Replacer(tmpl, cfg)
            replacer.update_replacements()
            message = replacer.generate_messages()

            # Set release version
            self.executor.add(
                lambda: self.set_version(release.next_version),
                True,
                f"Set version {tmpl.package_name} {tmpl.next_version}.",
            )
            # Create git commit
            self.executor.add(
                lambda: git.create_commit(
                    message.release_commit, cfg.sign_commit
                ),
                True,
                "Create git commit.",
            )
            # Push commit with release version
            self.executor.add(
                lambda: git.push_commit(),
                not cfg.disable_push,
                "Push commit with release version.",
            )
            # Create tag with release version
            self.executor.add(
                lambda: git.create_tag(
                    message.tag_name, message.tag_message, cfg.sign_tag
                ),
                not cfg.disable_tag,
                "Create tag with release version.",
            )
            # Push tag with release version
            self.executor.add(
                lambda: git.push_tag(message.tag_name),
                not (cfg.disable_tag or cfg.disable_push),
                f"Push tag({tmpl.version}) with release version.",
            )
            # Set next iteration version
            self.executor.add(
                lambda: self.set_version(release.next_pre_version),
                not release.has_next_pre_version,
                f"Set next version {tmpl.package_name} {tmpl.next_version}.",
            )
            # Create commit with next iteration version
            self.executor.add(
                lambda: git.create_commit(
                    message.post_release_commit, cfg.sign_commit
                ),
                not (not release.has_next_pre_version or cfg.disable_dev),
                "Create commit with next iteration version.",
            )
            # Push commit with next iteration version
            self.executor.add(
                lambda: git.push_commit(),
                not (
                    not release.has_next_pre_version
                    or cfg.disable_dev
                    or cfg.disable_push
                ),
                "Push commit with next iteration version.",
            )

        except RuntimeError as e:
            self.line(f"<fg=red>{e}</>")
            return 1
        except InvalidVersion as e:
            self.line(f"<fg=yellow>{e}</>")
            return 1
        except UpdateVersionError as e:
            self.line(f"<fg=yellow>{e}</>")
            return 1
        return 0

    def set_version(self, version: str) -> None:
        content: dict[str, Any] = self.poetry.file.read()
        poetry_content = content["tool"]["poetry"]
        poetry_content["version"] = version
        self.poetry.file.write(cast(TOMLDocument, content))

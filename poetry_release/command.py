from datetime import datetime

from cleo.commands.command import Command
from cleo.helpers import argument, option
from poetry.core.version.exceptions import InvalidVersion
from poetry.poetry import Poetry

from poetry_release.git import Git
from poetry_release.exception import UpdateVersionError
from poetry_release.replace import Template, Replacer
from poetry_release.settings import Settings
from poetry_release.version import ReleaseLevel, ReleaseVersion


class ReleaseCommand(Command):  # type: ignore

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
            settings = Settings(self)
            git = Git(settings)
            if not git.repo_exists():
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

            poetry = self.application.poetry
            next_release = ReleaseLevel.parse(self.argument("level"))
            releaser = ReleaseVersion(
                poetry.package.version,
                next_release,
            )

            if not self.confirm(
                f'Release {poetry.package.name} {releaser.next_version.text}?',
                False, '(?i)^(y|j)'
            ):
                return

            if releaser.version.text == releaser.next_version.text:
                self.line("<fg=yellow> Version doesn't changed</>")
                return

            templates = Template(
                package_name=poetry.package.name,
                prev_version=releaser.version.text,
                version=releaser.next_version.text,
                next_version=releaser.next_pre_version.text
                if releaser.next_pre_version else "",
                date=datetime.today().strftime("%Y-%m-%d"),
            )

            replacer = Replacer(templates, settings)
            replacer.update_replacements()
            message = replacer.generate_messages()
            self.set_version(poetry, releaser.next_version.text)

            # GIT RELEASE COMMIT
            git.create_commit(message.release_commit)
            if not settings.disable_push:
                git.push_commit()

            # GIT TAG
            if not settings.disable_tag:
                git.create_tag(message.tag_name, message.tag_message)
                if not settings.disable_push:
                    git.push_tag(message.tag_name)

            # GIT NEXT ITERATION COMMIT
            if not settings.disable_dev:
                pre_release = releaser.next_pre_version
                if pre_release is not None:
                    self.set_version(poetry, pre_release.text)
                    git.create_commit(message.post_release_commit)
                    if not settings.disable_push:
                        git.push_commit()

        except RuntimeError as e:
            self.line(f"<fg=red>{e}</>")
        except InvalidVersion as e:
            self.line(f"<fg=yellow>{e}</>")
        except UpdateVersionError as e:
            self.line(f"<fg=yellow>{e}</>")

    def set_version(self, poetry: Poetry, version: str) -> None:
        content = poetry.file.read()
        poetry_content = content["tool"]["poetry"]
        poetry_content["version"] = version
        poetry.file.write(content)


def release_factory() -> ReleaseCommand:
    return ReleaseCommand()

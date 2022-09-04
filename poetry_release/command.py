from datetime import datetime

from cleo.commands.command import Command
from cleo.helpers import argument, option
from poetry.core.version.exceptions import InvalidVersion
from poetry.poetry import Poetry

from poetry_release import git
from poetry_release.config import Config
from poetry_release.exception import UpdateVersionError
from poetry_release.replace import Template, Replacer
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
            description="Disable create git tags",
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

            # Init config
            cfg = Config()

            pyproject = self.application \
                .poetry.file.read().get("tool", {}).get("poetry-release", {})
            pyproject_cfg = Config(
                disable_push=pyproject.get("disable-push"),
                disable_tag=pyproject.get("disable-tag"),
                disable_dev=pyproject.get("disable_dev"),
                tag_name=pyproject.get("tag-name"),
                tag_message=pyproject.get("tag-message"),
                release_commit_message=pyproject.get("release-commit-message"),
                post_release_commit_message=pyproject.get("post-release-commit-message"),
                release_replacements=pyproject.get("release-replacements"),
                sign_commit=pyproject.get("sign-commit"),
                sign_tag=pyproject.get("sign-tag"),
            )
            cfg.update(pyproject_cfg)

            cli_cfg = Config(
                disable_push=self.option("disable-push"),
                disable_tag=self.option("disable-tag"),
                disable_dev=self.option("disable-dev"),
            )

            cfg.update(cli_cfg)

            # Check git
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

            replacer = Replacer(templates, cfg)
            replacer.update_replacements()
            message = replacer.generate_messages()
            self.set_version(poetry, releaser.next_version.text)

            # Git release commit
            git.create_commit(message.release_commit, cfg.sign_commit)
            if not cfg.disable_push:
                git.push_commit()

            # Git tag
            if not cfg.disable_tag:
                git.create_tag(
                    message.tag_name,
                    message.tag_message,
                    cfg.sign_tag,
                )
                if not cfg.disable_push:
                    git.push_tag(message.tag_name)

            # Git next iteration commit
            if not cfg.disable_dev:
                pre_release = releaser.next_pre_version
                if pre_release is not None:
                    self.set_version(poetry, pre_release.text)
                    git.create_commit(
                        message.post_release_commit,
                        cfg.sign_commit,
                    )
                    if not cfg.disable_push:
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

from dataclasses import dataclass

from cleo.commands.command import Command   # type: ignore


@dataclass
class ReleaseSettings:
    disable_push: bool
    disable_tag: bool
    disable_dev: bool

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


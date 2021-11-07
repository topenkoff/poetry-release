from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.console.application import Application
from poetry_release.command import release_factory


class ReleasePlugin(ApplicationPlugin):         # type: ignore
    def activate(self, application: Application) -> None:
        application.command_loader.register_factory("release", release_factory)

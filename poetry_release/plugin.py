from poetry.plugins.application_plugin import ApplicationPlugin    # type: ignore

from poetry_release.command import release_factory


class ReleasePlugin(ApplicationPlugin):
    def activate(self, application):
        application.command_loader.register_factory("release", release_factory)


from __future__ import annotations

from typing import Dict, List, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from cleo.commands.command import Command
    from typing import Callable, Any


class Config:
    def __init__(
        self,
        disable_push: Optional[bool] = None,
        disable_tag: Optional[bool] = None,
        disable_dev: Optional[bool] = None,
        sign_commit: Optional[bool] = None,
        sign_tag: Optional[bool] = None,
        tag_name: Optional[str] = None,
        tag_message: Optional[str] = None,
        release_commit_message: Optional[str] = None,
        post_release_commit_message: Optional[str] = None,
        release_replacements: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        self._disable_push = disable_push
        self._disable_tag = disable_tag
        self._disable_dev = disable_dev
        self._sign_commit = sign_commit
        self._sign_tag = sign_tag
        self._tag_name = tag_name
        self._tag_message = tag_message
        self._release_commit_message = release_commit_message
        self._post_release_commit_message = post_release_commit_message
        self._release_replacements = release_replacements

    @property
    def disable_push(self) -> bool:
        return self._disable_push if self._disable_push is not None else False

    @property
    def disable_tag(self) -> bool:
        return self._disable_tag if self._disable_tag is not None else False

    @property
    def disable_dev(self) -> bool:
        return self._disable_dev if self._disable_dev is not None else False

    @property
    def sign_commit(self) -> bool:
        return self._sign_commit if self._sign_commit is not None else False

    @property
    def sign_tag(self) -> bool:
        return self._sign_tag if self._sign_tag is not None else False

    @property
    def tag_name(self) -> Optional[str]:
        return self._tag_name

    @property
    def tag_message(self) -> Optional[str]:
        return self._tag_message

    @property
    def release_commit_message(self) -> Optional[str]:
        return self._release_commit_message

    @property
    def post_release_commit_message(self) -> Optional[str]:
        return self._post_release_commit_message

    @property
    def release_replacements(self) -> List[Dict[str, str]]:
        return (
            self._release_replacements
            if self._release_replacements is not None
            else []
        )

    def update(self, cfg: Config) -> None:
        for key, value in cfg.__dict__.items():
            if value is not None:
                self.__setattr__(key, value)

    @staticmethod
    def from_pyproject(pyproject: dict[str, Any]) -> Config:
        return Config(
            disable_push=pyproject.get("disable-push"),
            disable_tag=pyproject.get("disable-tag"),
            disable_dev=pyproject.get("disable_dev"),
            tag_name=pyproject.get("tag-name"),
            tag_message=pyproject.get("tag-message"),
            release_commit_message=pyproject.get("release-commit-message"),
            post_release_commit_message=pyproject.get(
                "post-release-commit-message"
            ),
            release_replacements=pyproject.get("release-replacements"),
            sign_commit=pyproject.get("sign-commit"),
            sign_tag=pyproject.get("sign-tag"),
        )

    @staticmethod
    def from_cli(cli: Callable[[str], Any]) -> Config:
        return Config(
            disable_push=cli("disable-push"),
            disable_tag=cli("disable-tag"),
            disable_dev=cli("disable-dev"),
        )

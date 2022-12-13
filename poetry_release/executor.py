from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from cleo.io.io import IO


class Handler:
    def __init__(
        self,
        func: Callable[[], None],
        execute: bool,
        msg: str,
    ) -> None:
        self.func = func
        self.execute = execute


class Executor:
    def __init__(self, io: IO) -> None:
        self._io = io
        self._handlers: list[Handler] = []

    def add(
        self,
        func: Callable[[], None],
        execute: bool,
        msg: str,
    ) -> None:
        handler = Handler(func, execute, msg)
        self._handlers.append(handler)

    def run(self) -> None:
        for handler in filter(lambda x: x.execute, self._handlers):
            # self._io.write(handler.msg)
            handler.func()

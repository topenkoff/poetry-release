from __future__ import annotations

from typing import TYPE_CHECKING

from cleo.io.outputs.output import Verbosity

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
        self.msg = msg


class Executor:
    def __init__(self, io: IO, dry_run: bool | None) -> None:
        self._io = io
        self._handlers: list[Handler] = []
        self._dry_run = dry_run

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
            text = f"<info>{handler.msg}</>"
            self._io.write_line(text, verbosity=Verbosity.NORMAL)
            if self._dry_run:
                return
            handler.func()

from typing import Any, Callable

import typer

from blue_shell.__version__ import __version__

__all__ = ["option_callback", "get_blus_version"]


def option_callback(func: Callable) -> Callable:  # type: ignore
    def wrapper(cls: Any, value: str) -> None:
        if not value:
            return
        func(cls, value)
        raise typer.Exit()

    return wrapper


@option_callback
def get_blus_version(*_args: Any) -> None:
    """Displays the current installed version of BlueShell"""
    typer.echo(f"BlueShell {__version__}")

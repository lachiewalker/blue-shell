from typing import Any, Callable

import typer

from sgpt.__version__ import __version__

__all__ = ["option_callback", "get_sgpt_version"]


def option_callback(func: Callable) -> Callable:  # type: ignore
    def wrapper(cls: Any, value: str) -> None:
        if not value:
            return
        func(cls, value)
        raise typer.Exit()

    return wrapper


@option_callback
def get_sgpt_version(*_args: Any) -> None:
    """Displays the current installed version of ShellGPT"""
    typer.echo(f"ShellGPT {__version__}")

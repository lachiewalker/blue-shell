import os
from typing import Any

import typer
from click import UsageError

from sgpt.integration import bash_integration, zsh_integration
from . import option_callback


@option_callback
def install_shell_integration(*_args: Any) -> None:
    """Install shell integration for ZSH and Bash."""
    shell = os.getenv("SHELL", "")
    if "zsh" in shell:
        typer.echo("Installing ZSH integration...")
        with open(os.path.expanduser("~/.zshrc"), "a", encoding="utf-8") as file:
            file.write(zsh_integration)
    elif "bash" in shell:
        typer.echo("Installing Bash integration...")
        with open(os.path.expanduser("~/.bashrc"), "a", encoding="utf-8") as file:
            file.write(bash_integration)
    else:
        raise UsageError("ShellGPT integrations only available for ZSH and Bash.")

    typer.echo("Done! Restart your shell to apply changes.")

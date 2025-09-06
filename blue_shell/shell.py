import os
import platform
import shlex


def is_powershell() -> bool:
    """Detect if current Windows shell is PowerShell."""
    return len(os.getenv("PSModulePath", "").split(os.pathsep)) >= 3


def get_shell() -> str:
    """Return the user's shell or a default."""
    return os.environ.get("SHELL", "/bin/sh")


def build_command(command: str) -> str:
    """Return a shell-aware command string."""
    if platform.system() == "Windows":
        return (
            f'powershell.exe -Command "{command}"'
            if is_powershell()
            else f'cmd.exe /c "{command}"'
        )
    return f"{get_shell()} -c {shlex.quote(command)}"


def run_command(command: str) -> None:
    """Run `command` in the user's shell."""
    os.system(build_command(command))

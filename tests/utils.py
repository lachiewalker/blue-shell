from datetime import datetime

import typer
from typer.testing import CliRunner


class SGPTRunner(CliRunner):
    """CliRunner providing empty stdin by default."""

    def invoke(self, *args, **kwargs):  # type: ignore[override]
        input_text = kwargs.get("input", "")
        if "__sgpt__eof__" not in input_text:
            if not input_text.endswith("\n"):
                input_text += "\n"
            input_text += "__sgpt__eof__\n"
        kwargs["input"] = input_text
        return super().invoke(*args, **kwargs)

from blue_shell import main
from blue_shell.config import cfg
from types import SimpleNamespace

runner = SGPTRunner()
app = typer.Typer()
app.command()(main)


def mock_comp(tokens_string):
    return [
        SimpleNamespace(
            id="foo",
            model=cfg.get("DEFAULT_MODEL"),
            object="chat.completion.chunk",
            choices=[
                SimpleNamespace(
                    index=0,
                    finish_reason=None,
                    delta={"content": token, "role": "assistant"},
                )
            ],
            created=int(datetime.now().timestamp()),
        )
        for token in tokens_string
    ]


def cmd_args(prompt="", **kwargs):
    arguments = [prompt]
    for key, value in kwargs.items():
        arguments.append(key)
        if isinstance(value, bool):
            continue
        arguments.append(value)
    arguments.append("--no-cache")
    arguments.append("--no-functions")
    return arguments


def comp_args(role, prompt, **kwargs):
    return {
        "messages": [
            {"role": "system", "content": role.role},
            {"role": "user", "content": prompt},
        ],
        "model": cfg.get("DEFAULT_MODEL"),
        "temperature": 0.0,
        "top_p": 1.0,
        "stream": True,
        **kwargs,
    }

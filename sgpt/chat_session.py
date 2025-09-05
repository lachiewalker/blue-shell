import json
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

from .config import cfg

CHAT_CACHE_LENGTH = int(cfg.get("CHAT_CACHE_LENGTH"))
CHAT_CACHE_PATH = Path(cfg.get("CHAT_CACHE_PATH"))


class ChatSession:
    """Decorator-based chat session manager that caches messages."""

    def __init__(self, length: int, storage_path: Path) -> None:
        self.length = length
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Generator[str, None, None]:
            chat_id = kwargs.pop("chat_id", None)
            if not kwargs.get("messages"):
                return
            if not chat_id:
                yield from func(*args, **kwargs)
                return
            previous_messages = self._read(chat_id)
            for message in kwargs["messages"]:
                previous_messages.append(message)
            kwargs["messages"] = previous_messages
            response_text = ""
            for word in func(*args, **kwargs):
                response_text += word
                yield word
            previous_messages.append({"role": "assistant", "content": response_text})
            self._write(kwargs["messages"], chat_id)

        return wrapper

    def _read(self, chat_id: str) -> List[Dict[str, str]]:
        file_path = self.storage_path / chat_id
        if not file_path.exists():
            return []
        parsed_cache = json.loads(file_path.read_text())
        return parsed_cache if isinstance(parsed_cache, list) else []

    def _write(self, messages: List[Dict[str, str]], chat_id: str) -> None:
        file_path = self.storage_path / chat_id
        truncated_messages = (
            messages[:1] + messages[1 + max(0, len(messages) - self.length) :]
        )
        json.dump(truncated_messages, file_path.open("w"))

    def invalidate(self, chat_id: str) -> None:
        file_path = self.storage_path / chat_id
        file_path.unlink(missing_ok=True)

    def get_messages(self, chat_id: str) -> List[str]:
        messages = self._read(chat_id)
        return [f"{message['role']}: {message['content']}" for message in messages]

    def exists(self, chat_id: Optional[str]) -> bool:
        return bool(chat_id and bool(self._read(chat_id)))

    def list(self) -> List[Path]:
        files = self.storage_path.glob("*")
        return sorted(files, key=lambda f: f.stat().st_mtime)


chat_session = ChatSession(CHAT_CACHE_LENGTH, CHAT_CACHE_PATH)


def initial_message(chat_id: str) -> str:
    chat_history = chat_session.get_messages(chat_id)
    return chat_history[0] if chat_history else ""


def list_chat_ids(value: bool) -> bool:
    if not value:
        return value
    for chat_id in chat_session.list():
        typer.echo(chat_id)
    raise typer.Exit()


def show_chat_messages(chat_id: str, markdown: bool) -> None:
    color = cfg.get("DEFAULT_COLOR")
    if "APPLY MARKDOWN" in initial_message(chat_id) and markdown:
        theme = cfg.get("CODE_THEME")
        for message in chat_session.get_messages(chat_id):
            if message.startswith("assistant:"):
                Console().print(Markdown(message, code_theme=theme))
            else:
                typer.secho(message, fg=color)
            typer.echo()
        return

    for index, message in enumerate(chat_session.get_messages(chat_id)):
        running_color = color if index % 2 == 0 else "green"
        typer.secho(message, fg=running_color)


def invalidate_chat(chat_id: str) -> None:
    chat_session.invalidate(chat_id)

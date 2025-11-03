import os
import warnings
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from click import UsageError
from pydantic import BaseModel


CONFIG_FOLDER = os.path.expanduser("~/.config")
SHELL_GPT_CONFIG_FOLDER = Path(CONFIG_FOLDER) / "blu-shell"
SHELL_GPT_CONFIG_PATH = SHELL_GPT_CONFIG_FOLDER / ".blusrc"
ROLE_STORAGE_PATH = SHELL_GPT_CONFIG_FOLDER / "roles"
FUNCTIONS_PATH = SHELL_GPT_CONFIG_FOLDER / "functions"
CHAT_CACHE_PATH = Path(gettempdir()) / "chat_cache"
CACHE_PATH = Path(gettempdir()) / "cache"


def get_env(key: str, default: str | None = None) -> str | None:
    """Read ``BLUS_``-prefixed environment variables.

    Legacy keys without the prefix are ignored but emit a warning to
    help users migrate.
    """

    prefixed_key = f"BLUS_{key}"
    if os.getenv(key) is not None:
        warnings.warn(
            f"Environment variable '{key}' is deprecated, use '{prefixed_key}' instead.",
            stacklevel=2,
        )
    if (value := os.getenv(prefixed_key)) is not None:
        return value
    return default


class Settings(BaseModel):
    CHAT_CACHE_PATH: str
    CACHE_PATH: str
    CHAT_CACHE_LENGTH: int
    CACHE_LENGTH: int
    REQUEST_TIMEOUT: int
    DEFAULT_MODEL: str
    DEFAULT_PROVIDER: str = "openai"
    DEFAULT_COLOR: str
    ROLE_STORAGE_PATH: str
    DEFAULT_EXECUTE_SHELL_CMD: str
    DISABLE_STREAMING: str
    CODE_THEME: str
    OPENAI_FUNCTIONS_PATH: str
    OPENAI_USE_FUNCTIONS: str
    SHOW_FUNCTIONS_OUTPUT: str
    API_BASE_URL: str
    PRETTIFY_MARKDOWN: str
    SHELL_INTERACTION: str
    OS_NAME: str
    SHELL_NAME: str
    ANTHROPIC_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    LITELLM_API_KEY: str = ""
    LITELLM_API_BASE: str = ""
    OLLAMA_API_BASE: str = "http://localhost:11434/v1"
    OLLAMA_API_KEY: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = ""
    OPENAI_API_KEY: str = ""
    MODELS: list[str] = []


DEFAULT_SETTINGS = Settings(
    CHAT_CACHE_PATH=get_env("CHAT_CACHE_PATH", str(CHAT_CACHE_PATH)),
    CACHE_PATH=get_env("CACHE_PATH", str(CACHE_PATH)),
    CHAT_CACHE_LENGTH=int(get_env("CHAT_CACHE_LENGTH", "100")),
    CACHE_LENGTH=int(get_env("CACHE_LENGTH", "100")),
    REQUEST_TIMEOUT=int(get_env("REQUEST_TIMEOUT", "60")),
    DEFAULT_MODEL=get_env("DEFAULT_MODEL", "gpt-4o"),
    DEFAULT_PROVIDER=get_env("DEFAULT_PROVIDER", "openai"),
    DEFAULT_COLOR=get_env("DEFAULT_COLOR", "magenta"),
    ROLE_STORAGE_PATH=get_env("ROLE_STORAGE_PATH", str(ROLE_STORAGE_PATH)),
    DEFAULT_EXECUTE_SHELL_CMD=get_env("DEFAULT_EXECUTE_SHELL_CMD", "false"),
    DISABLE_STREAMING=get_env("DISABLE_STREAMING", "false"),
    CODE_THEME=get_env("CODE_THEME", "dracula"),
    OPENAI_FUNCTIONS_PATH=get_env("OPENAI_FUNCTIONS_PATH", str(FUNCTIONS_PATH)),
    OPENAI_USE_FUNCTIONS=get_env("OPENAI_USE_FUNCTIONS", "true"),
    SHOW_FUNCTIONS_OUTPUT=get_env("SHOW_FUNCTIONS_OUTPUT", "false"),
    API_BASE_URL=get_env("API_BASE_URL", "default"),
    PRETTIFY_MARKDOWN=get_env("PRETTIFY_MARKDOWN", "true"),
    SHELL_INTERACTION=get_env("SHELL_INTERACTION", "true"),
    OS_NAME=get_env("OS_NAME", "auto"),
    SHELL_NAME=get_env("SHELL_NAME", "auto"),
    ANTHROPIC_API_KEY=get_env("ANTHROPIC_API_KEY", ""),
    MISTRAL_API_KEY=get_env("MISTRAL_API_KEY", ""),
    OPENROUTER_API_KEY=get_env("OPENROUTER_API_KEY", ""),
    LITELLM_API_KEY=get_env("LITELLM_API_KEY", ""),
    LITELLM_API_BASE=get_env("LITELLM_API_BASE", ""),
    OLLAMA_API_BASE=get_env("OLLAMA_API_BASE", "http://localhost:11434/v1"),
    OLLAMA_API_KEY=get_env("OLLAMA_API_KEY", ""),
    AWS_ACCESS_KEY_ID=get_env("AWS_ACCESS_KEY_ID", ""),
    AWS_SECRET_ACCESS_KEY=get_env("AWS_SECRET_ACCESS_KEY", ""),
    AWS_REGION=get_env("AWS_REGION", ""),
    OPENAI_API_KEY=get_env("OPENAI_API_KEY", ""),
)

DEFAULT_CONFIG = DEFAULT_SETTINGS.model_dump()


class Config:
    def __init__(self, config_path: Path, **defaults: Any):
        self.config_path = config_path
        self.settings = Settings(**defaults)

        if self._exists:
            self._read()
            updated = False
            for key, value in defaults.items():
                if getattr(self.settings, key, None) is None:
                    setattr(self.settings, key, value)
                    updated = True
            if updated:
                self._write()
        else:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            self._write()

    @property
    def _exists(self) -> bool:
        return self.config_path.exists()

    def _write(self) -> None:
        data = self.settings.model_dump()
        with open(self.config_path, "w", encoding="utf-8") as file:
            for key, value in data.items():
                if isinstance(value, list):
                    value = ",".join(value)
                file.write(f"{key}={value}\n")

    def _read(self) -> None:
        data: dict[str, Any] = {}
        with open(self.config_path, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    if key == "MODELS":
                        data[key] = value.split(",") if value else []
                    else:
                        data[key] = value
        self.settings = self.settings.model_copy(update=data)

    def get(self, key: str) -> str:  # type: ignore
        value = get_env(key)
        if value is None:
            value = getattr(self.settings, key)
        if value in (None, "", []):
            raise UsageError(f"Missing config key: {key}")
        if isinstance(value, list):
            return ",".join(value)
        return str(value)

    def update(self, **kwargs: Any) -> None:
        self.settings = self.settings.model_copy(update=kwargs)
        self._write()

    def add_model(self, model: str) -> None:
        models = set(self.settings.MODELS)
        models.add(model)
        self.update(MODELS=list(models))


cfg = Config(SHELL_GPT_CONFIG_PATH, **DEFAULT_CONFIG)


from abc import ABC, abstractmethod
from typing import Generator

from rich.console import Console, ConsoleOptions
from rich.live import Live
from rich.markdown import Markdown, CodeBlock
from rich.text import Text
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name
from typer import secho


class Printer(ABC):
    console = Console()

    @abstractmethod
    def live_print(self, chunks: Generator[str, None, None]) -> str:
        pass

    @abstractmethod
    def static_print(self, text: str) -> str:
        pass

    def __call__(self, chunks: Generator[str, None, None], live: bool = True) -> str:
        if live:
            return self.live_print(chunks)
        with self.console.status("[bold green]Loading..."):
            full_completion = "".join(chunks)
        self.static_print(full_completion)
        return full_completion


class _ThemedCodeBlock(CodeBlock):
    """Code block with theme background but without trailing padding."""

    def __rich_console__(self, console: Console, options: ConsoleOptions):
        code = str(self.text).rstrip()
        try:
            lexer = get_lexer_by_name(self.lexer_name)
        except Exception:
            lexer = get_lexer_by_name("text")
        highlighted = highlight(code, lexer, TerminalFormatter())
        highlighted = highlighted.replace("\x1b[39;49;00m", "\x1b[39m")
        try:
            bg = get_style_by_name(self.theme).background_color
        except Exception:
            bg = None
        if bg:
            r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
            bg_code = f"\x1b[48;2;{r};{g};{b}m"
        else:
            bg_code = ""
        lines = highlighted.rstrip("\n").splitlines()
        block = "".join(f"{bg_code} {line}\n" for line in lines)
        if bg_code:
            block += "\x1b[0m"
        yield Text.from_ansi(block)


class _ThemedMarkdown(Markdown):
    """Markdown renderer using themed code blocks."""

    elements = Markdown.elements | {
        "fence": _ThemedCodeBlock,
        "code_block": _ThemedCodeBlock,
    }


class MarkdownPrinter(Printer):
    def __init__(self, theme: str) -> None:
        self.console = Console()
        self.theme = theme

    def _markdown(self, text: str) -> Markdown:
        return _ThemedMarkdown(markup=text, code_theme=self.theme)

    def live_print(self, chunks: Generator[str, None, None]) -> str:
        full_completion = ""
        with Live(console=self.console) as live:
            for chunk in chunks:
                full_completion += chunk
                live.update(self._markdown(full_completion), refresh=True)
        return full_completion

    def static_print(self, text: str) -> str:
        self.console.print(self._markdown(text))
        return text


class TextPrinter(Printer):
    def __init__(self, color: str) -> None:
        self.color = color

    def live_print(self, chunks: Generator[str, None, None]) -> str:
        full_text = ""
        for chunk in chunks:
            full_text += chunk
            secho(chunk, fg=self.color, nl=False)
        else:
            print()  # Add new line after last chunk.
        return full_text

    def static_print(self, text: str) -> str:
        secho(text, fg=self.color)
        return text

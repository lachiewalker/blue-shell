from io import StringIO

import re
from rich.console import Console

from sgpt.printer import MarkdownPrinter


def test_markdown_printer_no_trailing_spaces():
    printer = MarkdownPrinter(theme="monokai")
    buffer = StringIO()
    printer.console = Console(file=buffer, force_terminal=True)
    code_block = """```python\nprint('hi')\n```"""
    printer.static_print(code_block)
    rendered = buffer.getvalue()
    assert re.search(r"\x1b\[(?:48;2;\d+;\d+;\d+|4\d)m", rendered)
    plain_text = re.sub(r"\x1b\[[0-9;]*m", "", rendered)
    for line in plain_text.splitlines():
        if not line.strip():
            continue
        assert line == line.rstrip()

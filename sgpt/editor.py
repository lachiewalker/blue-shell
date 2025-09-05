import os
from tempfile import NamedTemporaryFile

from click import BadParameter


def get_edited_prompt() -> str:
    """Open the user's $EDITOR to edit and return a prompt."""
    with NamedTemporaryFile(suffix=".txt", delete=False) as file:
        file_path = file.name
    editor = os.environ.get("EDITOR", "vim")
    os.system(f"{editor} {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        output = file.read()
    os.remove(file_path)
    if not output:
        raise BadParameter("Couldn't get valid PROMPT from $EDITOR")
    return output

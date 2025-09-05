from typing import Any, Dict, Generator, List

from click import BadArgumentUsage

from ..role import DefaultRoles, SystemRole
from .handler import Handler
from ..chat_session import (
    chat_session,
    initial_message,
    invalidate_chat,
)


class ChatHandler(Handler):
    chat_session = chat_session

    def __init__(self, chat_id: str, role: SystemRole, markdown: bool) -> None:
        super().__init__(role, markdown)
        self.chat_id = chat_id
        self.role = role

        if chat_id == "temp":
            invalidate_chat(chat_id)

        self.validate()

    @property
    def initiated(self) -> bool:
        return self.chat_session.exists(self.chat_id)

    @property
    def is_same_role(self) -> bool:
        # TODO: Should be optimized for REPL mode.
        return self.role.same_role(initial_message(self.chat_id))

    def validate(self) -> None:
        if self.initiated:
            chat_role_name = self.role.get_role_name(initial_message(self.chat_id))
            if not chat_role_name:
                raise BadArgumentUsage(
                    f'Could not determine chat role of "{self.chat_id}"'
                )
            if self.role.name == DefaultRoles.DEFAULT.value:
                # If user didn't pass chat mode, we will use the one that was used to initiate the chat.
                self.role = SystemRole.get(chat_role_name)
            else:
                if not self.is_same_role:
                    raise BadArgumentUsage(
                        f'Cant change chat role to "{self.role.name}" '
                        f'since it was initiated as "{chat_role_name}" chat.'
                    )

    def make_messages(self, prompt: str) -> List[Dict[str, str]]:
        messages = []
        if not self.initiated:
            messages.append({"role": "system", "content": self.role.role})
        messages.append({"role": "user", "content": prompt})
        return messages

    @chat_session
    def get_completion(self, **kwargs: Any) -> Generator[str, None, None]:
        yield from super().get_completion(**kwargs)

    def handle(self, **kwargs: Any) -> str:  # type: ignore[override]
        return super().handle(**kwargs, chat_id=self.chat_id)

import json
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from ..cache import Cache
from ..config import cfg
from ..function import get_function
from ..llm_client import LLMClient, get_llm_client
from ..printer import MarkdownPrinter, Printer, TextPrinter
from ..role import DefaultRoles, SystemRole


class Handler:
    cache = Cache(int(cfg.get("CACHE_LENGTH")), Path(cfg.get("CACHE_PATH")))

    def __init__(
        self,
        role: SystemRole,
        markdown: bool,
        client: Optional[LLMClient] = None,
    ) -> None:
        self.role = role
        self.client = client or get_llm_client()

        self.markdown = "APPLY MARKDOWN" in self.role.role and markdown
        self.code_theme, self.color = cfg.get("CODE_THEME"), cfg.get("DEFAULT_COLOR")

    @property
    def printer(self) -> Printer:
        return (
            MarkdownPrinter(self.code_theme)
            if self.markdown
            else TextPrinter(self.color)
        )

    def make_messages(self, prompt: str) -> List[Dict[str, str]]:
        raise NotImplementedError

    def handle_function_call(
        self,
        messages: List[dict[str, Any]],
        name: str,
        arguments: str,
    ) -> Generator[str, None, None]:
        messages.append(
            {
                "role": "assistant",
                "content": "",
                "function_call": {"name": name, "arguments": arguments},
            }
        )

        if messages and messages[-1]["role"] == "assistant":
            yield "\n"

        dict_args = json.loads(arguments)
        joined_args = ", ".join(f'{k}="{v}"' for k, v in dict_args.items())
        yield f"> @FunctionCall `{name}({joined_args})` \n\n"

        result = get_function(name)(**dict_args)
        if cfg.get("SHOW_FUNCTIONS_OUTPUT") == "true":
            yield f"```text\n{result}\n```\n"
        messages.append({"role": "function", "content": result, "name": name})

    @cache
    def get_completion(
        self,
        model: str,
        temperature: float,
        top_p: float,
        messages: List[Dict[str, Any]],
        functions: Optional[List[Dict[str, str]]],
    ) -> Generator[str, None, None]:
        name = arguments = ""
        is_shell_role = self.role.name == DefaultRoles.SHELL.value
        is_code_role = self.role.name == DefaultRoles.CODE.value
        is_dsc_shell_role = self.role.name == DefaultRoles.DESCRIBE_SHELL.value
        if is_shell_role or is_code_role or is_dsc_shell_role:
            functions = None

        call_kwargs: Dict[str, Any] = {}
        if functions:
            call_kwargs["tool_choice"] = "auto"
            call_kwargs["tools"] = functions
            call_kwargs["parallel_tool_calls"] = False

        response = self.client.completion(
            model=model,
            temperature=temperature,
            top_p=top_p,
            messages=messages,
            stream=True,
            **call_kwargs,
        )

        try:
            for chunk in response:
                choice = (
                    chunk["choices"][0] if isinstance(chunk, dict) else chunk.choices[0]
                )
                delta = (
                    choice.get("delta") if isinstance(choice, dict) else choice.delta
                )

                tool_calls = (
                    delta.get("tool_calls")
                    if isinstance(delta, dict)
                    else getattr(delta, "tool_calls", None)
                )
                if tool_calls:
                    for tool_call in tool_calls:
                        fn = (
                            tool_call.get("function")
                            if isinstance(tool_call, dict)
                            else tool_call.function
                        )
                        name = name or (
                            fn.get("name") if isinstance(fn, dict) else fn.name
                        )
                        args_part = (
                            fn.get("arguments")
                            if isinstance(fn, dict)
                            else fn.arguments
                        )
                        if args_part:
                            arguments += args_part
                finish_reason = (
                    choice.get("finish_reason")
                    if isinstance(choice, dict)
                    else choice.finish_reason
                )
                if finish_reason == "tool_calls":
                    yield from self.handle_function_call(messages, name, arguments)
                    yield from self.get_completion(
                        model=model,
                        temperature=temperature,
                        top_p=top_p,
                        messages=messages,
                        functions=functions,
                        caching=False,
                    )
                    return

                content = (
                    delta.get("content")
                    if isinstance(delta, dict)
                    else getattr(delta, "content", None)
                )
                yield content or ""
        except KeyboardInterrupt:
            response.close()

    def handle(
        self,
        prompt: str,
        model: str,
        temperature: float,
        top_p: float,
        caching: bool,
        functions: Optional[List[Dict[str, str]]] = None,
        **kwargs: Any,
    ) -> str:
        disable_stream = cfg.get("DISABLE_STREAMING") == "true"
        messages = self.make_messages(prompt.strip())
        generator = self.get_completion(
            model=model,
            temperature=temperature,
            top_p=top_p,
            messages=messages,
            functions=functions,
            caching=caching,
            **kwargs,
        )
        return self.printer(generator, not disable_stream)

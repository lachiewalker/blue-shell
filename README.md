# BlueShell
A command-line productivity tool powered by AI large language models (LLM). This command-line tool offers streamlined generation of **shell commands, code snippets, documentation**, eliminating the need for external resources (like Google search). Supports Linux, macOS, Windows and compatible with all major Shells like PowerShell, CMD, Bash, Zsh, etc.

https://github.com/TheR1D/blu-shell/assets/16740832/9197283c-db6a-4b46-bfea-3eb776dd9093

## Installation
```shell
pip install blu-shell
```
By default, BlueShell uses OpenAI's API and GPT-4 model. You'll need an API key, you can generate one [here](https://beta.openai.com/account/api-keys). You will be prompted for your key which will then be stored in `~/.config/blu-shell/.blusrc`. OpenAI API is not free of charge, please refer to the [OpenAI pricing](https://openai.com/pricing) for more information.

> [!TIP]
> Alternatively, you can use locally hosted open source models which are available for free. To use local models, you will need to run your own LLM backend server such as [Ollama](https://github.com/ollama/ollama). To set up BlueShell with Ollama, please follow this comprehensive [guide](https://github.com/TheR1D/blu-shell/wiki/Ollama).
>
> **❗️Note that BlueShell is not optimized for local models and may not work as expected.**

## Usage
**BlueShell** is designed to quickly analyse and retrieve information. It's useful for straightforward requests ranging from technical configurations to general knowledge.
```shell
blus "What is the fibonacci sequence"
# -> The Fibonacci sequence is a series of numbers where each number ...
```

BlueShell accepts prompt from both stdin and command line argument. Whether you prefer piping input through the terminal or specifying it directly as arguments, `blus` got you covered. For example, you can easily generate a git commit message based on a diff:
```shell
git diff | blus "Generate git commit message, for my changes"
# -> Added main feature details into README.md
```

You can analyze logs from various sources by passing them using stdin, along with a prompt. For instance, we can use it to quickly analyze logs, identify errors and get suggestions for possible solutions:
```shell
docker logs -n 20 my_app | blus "check logs, find errors, provide possible solutions"
```
```text
Error Detected: Connection timeout at line 7.
Possible Solution: Check network connectivity and firewall settings.
Error Detected: Memory allocation failed at line 12.
Possible Solution: Consider increasing memory allocation or optimizing application memory usage.
```

You can also use all kind of redirection operators to pass input:
```shell
blus "summarise" < document.txt
# -> The document discusses the impact...
blus << EOF
What is the best way to lear Golang?
Provide simple hello world example.
EOF
# -> The best way to learn Golang...
blus <<< "What is the best way to learn shell redirects?"
# -> The best way to learn shell redirects is through...
```


### Shell commands
Have you ever found yourself forgetting common shell commands, such as `find`, and needing to look up the syntax online? With `--shell` or shortcut `-s` option, you can quickly generate and execute the commands you need right in the terminal.
```shell
blus --shell "find all json files in current folder"
# -> find . -type f -name "*.json"
# -> [E]xecute, [D]escribe, [A]bort: e
```

BlueShell is aware of OS and `$SHELL` you are using, it will provide shell command for specific system you have. For instance, if you ask `blus` to update your system, it will return a command based on your OS. Here's an example using macOS:
```shell
blus -s "update my system"
# -> sudo softwareupdate -i -a
# -> [E]xecute, [D]escribe, [A]bort: e
```

The same prompt, when used on Ubuntu, will generate a different suggestion:
```shell
blus -s "update my system"
# -> sudo apt update && sudo apt upgrade -y
# -> [E]xecute, [D]escribe, [A]bort: e
```

Let's try it with Docker:
```shell
blus -s "start nginx container, mount ./index.html"
# -> docker run -d -p 80:80 -v $(pwd)/index.html:/usr/share/nginx/html/index.html nginx
# -> [E]xecute, [D]escribe, [A]bort: e
```

We can still use pipes to pass input to `blus` and generate shell commands:
```shell
blus -s "POST localhost with" < data.json
# -> curl -X POST -H "Content-Type: application/json" -d '{"a": 1, "b": 2}' http://localhost
# -> [E]xecute, [D]escribe, [A]bort: e
```

Applying additional shell magic in our prompt, in this example passing file names to `ffmpeg`:
```shell
ls
# -> 1.mp4 2.mp4 3.mp4
blus -s "ffmpeg combine $(ls -m) into one video file without audio."
# -> ffmpeg -i 1.mp4 -i 2.mp4 -i 3.mp4 -filter_complex "[0:v] [1:v] [2:v] concat=n=3:v=1 [v]" -map "[v]" out.mp4
# -> [E]xecute, [D]escribe, [A]bort: e
```

If you would like to pass generated shell command using pipe, you can use `--no-interaction` option. This will disable interactive mode and will print generated command to stdout. In this example we are using `pbcopy` to copy generated command to clipboard:
```shell
blus -s "find all json files in current folder" --no-interaction | pbcopy
```


### Shell integration
This is a **very handy feature**, which allows you to use `blus` shell completions directly in your terminal, without the need to type `blus` with prompt and arguments. Shell integration enables the use of BlueShell with hotkeys in your terminal, supported by both Bash and ZSH shells. This feature puts `blus` completions directly into terminal buffer (input line), allowing for immediate editing of suggested commands.

https://github.com/TheR1D/blu-shell/assets/16740832/bead0dab-0dd9-436d-88b7-6abfb2c556c1

To install shell integration, run `blus --install-integration` and restart your terminal to apply changes. This will add few lines to your `.bashrc` or `.zshrc` file. After that, you can use `Ctrl+l` (by default) to invoke BlueShell. When you press `Ctrl+l` it will replace you current input line (buffer) with suggested command. You can then edit it and just press `Enter` to execute.

### Generating code
By using the `--code` or `-c` parameter, you can specifically request pure code output, for instance:
```shell
blus --code "solve fizz buzz problem using python"
```

```python
for i in range(1, 101):
    if i % 3 == 0 and i % 5 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
```
Since it is valid python code, we can redirect the output to a file:  
```shell
blus --code "solve classic fizz buzz problem using Python" > fizz_buzz.py
python fizz_buzz.py
# 1
# 2
# Fizz
# 4
# Buzz
# ...
```

We can also use pipes to pass input:
```shell
cat fizz_buzz.py | blus --code "Generate comments for each line of my code"
```
```python
# Loop through numbers 1 to 100
for i in range(1, 101):
    # Check if number is divisible by both 3 and 5
    if i % 3 == 0 and i % 5 == 0:
        # Print "FizzBuzz" if number is divisible by both 3 and 5
        print("FizzBuzz")
    # Check if number is divisible by 3
    elif i % 3 == 0:
        # Print "Fizz" if number is divisible by 3
        print("Fizz")
    # Check if number is divisible by 5
    elif i % 5 == 0:
        # Print "Buzz" if number is divisible by 5
        print("Buzz")
    # If number is not divisible by 3 or 5, print the number itself
    else:
        print(i)
```

### Chat Mode 
Often it is important to preserve and recall a conversation. `blus` creates conversational dialogue with each LLM completion requested. The dialogue can develop one-by-one (chat mode) or interactively, in a REPL loop (REPL mode). Both ways rely on the same underlying object, called a chat session. The session is located at the [configurable](#runtime-configuration-file) `CHAT_CACHE_PATH`.

To start a conversation, use the `--chat` option followed by a unique session name and a prompt.
```shell
blus --chat conversation_1 "please remember my favorite number: 4"
# -> I will remember that your favorite number is 4.
blus --chat conversation_1 "what would be my favorite number + 4?"
# -> Your favorite number is 4, so if we add 4 to it, the result would be 8.
```

You can use chat sessions to iteratively improve GPT suggestions by providing additional details.  It is possible to use `--code` or `--shell` options to initiate `--chat`:
```shell
blus --chat conversation_2 --code "make a request to localhost using python"
```
```python
import requests

response = requests.get('http://localhost')
print(response.text)
```

Let's ask LLM to add caching to our request:
```shell
blus --chat conversation_2 --code "add caching"
```
```python
import requests
from cachecontrol import CacheControl

sess = requests.session()
cached_sess = CacheControl(sess)

response = cached_sess.get('http://localhost')
print(response.text)
```

Same applies for shell commands:
```shell
blus --chat conversation_3 --shell "what is in current folder"
# -> ls
blus --chat conversation_3 "Sort by name"
# -> ls | sort
blus --chat conversation_3 "Concatenate them using FFMPEG"
# -> ffmpeg -i "concat:$(ls | sort | tr '\n' '|')" -codec copy output.mp4
blus --chat conversation_3 "Convert the resulting file into an MP3"
# -> ffmpeg -i output.mp4 -vn -acodec libmp3lame -ac 2 -ab 160k -ar 48000 final_output.mp3
```

To list all the sessions from either conversational mode, use the `--list-chats` or `-lc` option:  
```shell
blus --list-chats
# .../blu-shell/chat_cache/conversation_1  
# .../blu-shell/chat_cache/conversation_2
```

To show all the messages related to a specific conversation, use the `--show-chat` option followed by the session name:
```shell
blus --show-chat conversation_1
# user: please remember my favorite number: 4
# assistant: I will remember that your favorite number is 4.
# user: what would be my favorite number + 4?
# assistant: Your favorite number is 4, so if we add 4 to it, the result would be 8.
```

### REPL Mode  
There is very handy REPL (read–eval–print loop) mode, which allows you to interactively chat with GPT models. To start a chat session in REPL mode, use the `--repl` option followed by a unique session name. You can also use "temp" as a session name to start a temporary REPL session. Note that `--chat` and `--repl` are using same underlying object, so you can use `--chat` to start a chat session and then pick it up with `--repl` to continue the conversation in REPL mode.

<p align="center">
  <img src="https://s10.gifyu.com/images/repl-demo.gif" alt="gif">
</p>

```text
blus --repl temp
Entering REPL mode, press Ctrl+C to exit.
>>> What is REPL?
REPL stands for Read-Eval-Print Loop. It is a programming environment ...
>>> How can I use Python with REPL?
To use Python with REPL, you can simply open a terminal or command prompt ...
```

REPL mode can work with `--shell` and `--code` options, which makes it very handy for interactive shell commands and code generation:
```text
blus --repl temp --shell
Entering shell REPL mode, type [e] to execute commands or press Ctrl+C to exit.
>>> What is in current folder?
ls
>>> Show file sizes
ls -lh
>>> Sort them by file sizes
ls -lhS
>>> e (enter just e to execute commands, or d to describe them)
```

To provide multiline prompt use triple quotes `"""`:
```text
blus --repl temp
Entering REPL mode, press Ctrl+C to exit.
>>> """
... Explain following code:
... import random
... print(random.randint(1, 10))
... """
It is a Python script that uses the random module to generate and print a random integer.
```

You can also enter REPL mode with initial prompt by passing it as an argument or stdin or even both:
```shell
blus --repl temp < my_app.py
```
```text
Entering REPL mode, press Ctrl+C to exit.
──────────────────────────────────── Input ────────────────────────────────────
name = input("What is your name?")
print(f"Hello {name}")
───────────────────────────────────────────────────────────────────────────────
>>> What is this code about?
The snippet of code you've provided is written in Python. It prompts the user...
>>> Follow up questions...
```

### Function calling  
[Function calls](https://platform.openai.com/docs/guides/function-calling) is a powerful feature OpenAI provides. It allows LLM to execute functions in your system, which can be used to accomplish a variety of tasks. To install [default functions](https://github.com/TheR1D/blu-shell/tree/main/sgpt/llm_functions/) run:
```shell
blus --install-functions
```

BlueShell has a convenient way to define functions and use them. In order to create your custom function, navigate to `~/.config/blu-shell/functions` and create a new .py file with the function name. Inside this file, you can define your function using the following syntax:
```python
# execute_shell_command.py
import subprocess
from pydantic import Field
from instructor import OpenAISchema


class Function(OpenAISchema):
    """
    Executes a shell command and returns the output (result).
    """
    shell_command: str = Field(..., example="ls -la", descriptions="Shell command to execute.")

    class Config:
        title = "execute_shell_command"

    @classmethod
    def execute(cls, shell_command: str) -> str:
        result = subprocess.run(shell_command.split(), capture_output=True, text=True)
        return f"Exit code: {result.returncode}, Output:\n{result.stdout}"
```

The docstring comment inside the class will be passed to OpenAI API as a description for the function, along with the `title` attribute and parameters descriptions. The `execute` function will be called if LLM decides to use your function. In this case we are allowing LLM to execute any Shell commands in our system. Since we are returning the output of the command, LLM will be able to analyze it and decide if it is a good fit for the prompt. Here is an example how the function might be executed by LLM:
```shell
blus "What are the files in /tmp folder?"
# -> @FunctionCall execute_shell_command(shell_command="ls /tmp")
# -> The /tmp folder contains the following files and directories:
# -> test.txt
# -> test.json
```

Note that if for some reason the function (execute_shell_command) will return an error, LLM might try to accomplish the task based on the output. Let's say we don't have installed `jq` in our system, and we ask LLM to parse JSON file:
```shell
blus "parse /tmp/test.json file using jq and return only email value"
# -> @FunctionCall execute_shell_command(shell_command="jq -r '.email' /tmp/test.json")
# -> It appears that jq is not installed on the system. Let me try to install it using brew.
# -> @FunctionCall execute_shell_command(shell_command="brew install jq")
# -> jq has been successfully installed. Let me try to parse the file again.
# -> @FunctionCall execute_shell_command(shell_command="jq -r '.email' /tmp/test.json")
# -> The email value in /tmp/test.json is johndoe@example.
```

It is also possible to chain multiple function calls in the prompt:
```shell
blus "Play music and open hacker news"
# -> @FunctionCall play_music()
# -> @FunctionCall open_url(url="https://news.ycombinator.com")
# -> Music is now playing, and Hacker News has been opened in your browser. Enjoy!
```

This is just a simple example of how you can use function calls. It is truly a powerful feature that can be used to accomplish a variety of complex tasks. We have dedicated [category](https://github.com/TheR1D/blu-shell/discussions/categories/functions) in GitHub Discussions for sharing and discussing functions. 
LLM might execute destructive commands, so please use it at your own risk❗️

### Roles
BlueShell allows you to create custom roles, which can be utilized to generate code, shell commands, or to fulfill your specific needs. To create a new role, use the `--create-role` option followed by the role name. You will be prompted to provide a description for the role, along with other details. This will create a JSON file in `~/.config/blu-shell/roles` with the role name. Inside this directory, you can also edit default `blus` roles, such as **shell**, **code**, and **default**. Use the `--list-roles` option to list all available roles, and the `--show-role` option to display the details of a specific role. Here's an example of a custom role:
```shell
blus --create-role json_generator
# Enter role description: Provide only valid json as response.
blus --role json_generator "random: user, password, email, address"
```
```json
{
  "user": "JohnDoe",
  "password": "p@ssw0rd",
  "email": "johndoe@example.com",
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip": "12345"
  }
}
```

If the description of the role contains the words "APPLY MARKDOWN" (case sensitive), then chats will be displayed using markdown formatting unless it is explicitly turned off with `--no-md`.

### Request cache
Control cache using `--cache` (default) and `--no-cache` options. This caching applies for all `blus` requests to OpenAI API:
```shell
blus "what are the colors of a rainbow"
# -> The colors of a rainbow are red, orange, yellow, green, blue, indigo, and violet.
```
Next time, same exact query will get results from local cache instantly. Note that `blus "what are the colors of a rainbow" --temperature 0.5` will make a new request, since we didn't provide `--temperature` (same applies to `--top-probability`) on previous request.

This is just some examples of what we can do using OpenAI GPT models, I'm sure you will find it useful for your specific use cases.

### Runtime configuration file
You can setup some parameters in runtime configuration file `~/.config/blu-shell/.blusrc`:
```text
# API key, set via BLUS_OPENAI_API_KEY env (legacy OPENAI_API_KEY is ignored).
OPENAI_API_KEY=your_api_key
# Base URL of the backend server. If "default" URL will be resolved based on --model.
API_BASE_URL=default
# Max amount of cached message per chat session.
CHAT_CACHE_LENGTH=100
# Chat cache folder.
CHAT_CACHE_PATH=/tmp/blu-shell/chat_cache
# Request cache length (amount).
CACHE_LENGTH=100
# Request cache folder.
CACHE_PATH=/tmp/blu-shell/cache
# Request timeout in seconds.
REQUEST_TIMEOUT=60
# Default OpenAI model to use.
DEFAULT_MODEL=gpt-4o
# Default color for shell and code completions.
DEFAULT_COLOR=magenta
# When in --shell mode, default to "Y" for no input.
DEFAULT_EXECUTE_SHELL_CMD=false
# Disable streaming of responses
DISABLE_STREAMING=false
# The pygment theme to view markdown (default/describe role).
CODE_THEME=default
# Path to a directory with functions.
OPENAI_FUNCTIONS_PATH=/Users/user/.config/blu-shell/functions
# Print output of functions when LLM uses them.
SHOW_FUNCTIONS_OUTPUT=false
# Allows LLM to use functions.
OPENAI_USE_FUNCTIONS=true
# Enforce LiteLLM usage (for local LLMs).
USE_LITELLM=false
```
Possible options for `DEFAULT_COLOR`: black, red, green, yellow, blue, magenta, cyan, white, bright_black, bright_red, bright_green, bright_yellow, bright_blue, bright_magenta, bright_cyan, bright_white.
Possible options for `CODE_THEME`: https://pygments.org/styles/

### Full list of arguments
```text
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────╮
│   prompt      [PROMPT]  The prompt to generate completions for.                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --model            TEXT                       Large language model to use. [default: gpt-4o]             │
│ --temperature      FLOAT RANGE [0.0<=x<=2.0]  Randomness of generated output. [default: 0.0]             │
│ --top-p            FLOAT RANGE [0.0<=x<=1.0]  Limits highest probable tokens (words). [default: 1.0]     │
│ --md             --no-md                      Prettify markdown output. [default: md]                    │
│ --editor                                      Open $EDITOR to provide a prompt. [default: no-editor]     │
│ --cache                                       Cache completion results. [default: cache]                 │
│ --version                                     Show version.                                              │
│ --help                                        Show this message and exit.                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Assistance Options ─────────────────────────────────────────────────────────────────────────────────────╮
│ --shell           -s                      Generate and execute shell commands.                           │
│ --interaction         --no-interaction    Interactive mode for --shell option. [default: interaction]    │
│ --describe-shell  -d                      Describe a shell command.                                      │
│ --code            -c                      Generate only code.                                            │
│ --functions           --no-functions      Allow function calls. [default: functions]                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Chat Options ───────────────────────────────────────────────────────────────────────────────────────────╮
│ --chat                 TEXT  Follow conversation with id, use "temp" for quick session. [default: None]  │
│ --repl                 TEXT  Start a REPL (Read–eval–print loop) session. [default: None]                │
│ --show-chat            TEXT  Show all messages from provided chat id. [default: None]                    │
│ --list-chats  -lc            List all existing chat ids.                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Role Options ───────────────────────────────────────────────────────────────────────────────────────────╮
│ --role                  TEXT  System role for GPT model. [default: None]                                 │
│ --create-role           TEXT  Create role. [default: None]                                               │
│ --show-role             TEXT  Show role. [default: None]                                                 │
│ --list-roles   -lr            List roles.                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Docker
Run the container using the `BLUS_OPENAI_API_KEY` environment variable, and a docker volume to store cache. Consider to set the environment variables `BLUS_OS_NAME` and `BLUS_SHELL_NAME` according to your preferences.
```shell
docker run --rm \
           --env BLUS_OPENAI_API_KEY=api_key \
           --env BLUS_OS_NAME=$(uname -s) \
           --env BLUS_SHELL_NAME=$(echo $SHELL) \
           --volume gpt-cache:/tmp/blu-shell \
       ghcr.io/lachiewalker/blu-shell -s "update my system"
```

Example of a conversation, using an alias and the `BLUS_OPENAI_API_KEY` environment variable:
```shell
alias blus="docker run --rm --volume gpt-cache:/tmp/blu-shell --env BLUS_OPENAI_API_KEY --env BLUS_OS_NAME=$(uname -s) --env BLUS_SHELL_NAME=$(echo $SHELL) ghcr.io/lachiewalker/blu-shell"
export BLUS_OPENAI_API_KEY="your OPENAI API key"
blus --chat rainbow "what are the colors of a rainbow"
blus --chat rainbow "inverse the list of your last answer"
blus --chat rainbow "translate your last answer in french"
```

You also can use the provided `Dockerfile` to build your own image:
```shell
docker build -t blus .
```

## Module overview
Internal helpers were split into dedicated modules:

* `sgpt.editor` – prompt editing utilities.
* `sgpt.shell` – shell detection and command execution helpers.
* `sgpt.utils.integration` – shell integration installers.

### Docker + Ollama

If you want to send your requests to an Ollama instance and run BlueShell inside a Docker container, you need to adjust the Dockerfile and build the container yourself: the litellm package is needed and env variables need to be set correctly.

Example Dockerfile:
```
FROM python:3-slim

ENV BLUS_DEFAULT_MODEL=ollama/mistral:7b-instruct-v0.2-q4_K_M
ENV BLUS_API_BASE_URL=http://10.10.10.10:11434
ENV BLUS_USE_LITELLM=true
ENV BLUS_OPENAI_API_KEY=bad_key
ENV BLUS_SHELL_INTERACTION=false
ENV BLUS_PRETTIFY_MARKDOWN=false
ENV BLUS_OS_NAME="Arch Linux"
ENV BLUS_SHELL_NAME=auto

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y gcc
RUN pip install --no-cache /app[litellm] && mkdir -p /tmp/blu-shell

VOLUME /tmp/blu-shell

ENTRYPOINT ["blus"]
```


## Additional documentation
* [Azure integration](https://github.com/TheR1D/blu-shell/wiki/Azure)
* [Ollama integration](https://github.com/TheR1D/blu-shell/wiki/Ollama)


# Ollama Code CLI

[![PyPI version](https://badge.fury.io/py/ollama-code-cli.svg)](https://badge.fury.io/py/ollama-code-cli)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Ollama Code CLI is an open-source AI agent that brings the power of local LLMs through Ollama, right in your terminal, with advanced tool-calling features.**

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Requirements](#requirements)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Interactive Mode](#interactive-mode)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- 🎨 **Elegant CLI Interface:** Rich colors and structured output
- 🤖 **Local AI Power:** Interact with local LLMs through Ollama
- 🛠️ **Tool Calling:** Execute coding-related tools (file operations, code execution, etc.)
- 🔒 **Permission Prompts:** Safety prompts before executing potentially dangerous operations
- 💬 **Interactive Mode:** Maintain conversation context for multi-turn interactions
- 📝 **Markdown Support:** Elegantly formatted responses with syntax highlighting
- 📋 **Structured Output:** Clear panels and tables for tool calls and results

---

## Installation

First, install a compatible model in Ollama:

```bash
# Choose one of these models:
ollama pull qwen3:4b
ollama pull qwen2.5:3b
```

Then install the CLI:

```bash
pip install ollama-code-cli
```

---

## Requirements

- Python 3.13+
- Ollama installed and running
- An Ollama model that supports tool calling (e.g., Qwen3, Qwen2.5, etc.)

---

## Usage

Start an interactive session:

```bash
ollama-code-cli --model qwen3:4b
```

Run a single command:

```bash
ollama-code-cli "Create a Python function to calculate factorial"
```

Use a specific model:

```bash
ollama-code-cli --model qwen3:4b "Explain how async/await works in Python"
```

Disable permission prompts (use with caution):

```bash
ollama-code-cli --no-permission "Create and run a Python script"
```

---

## Security Features

The CLI includes built-in security features to protect against potentially dangerous operations:

### Permission Prompts
By default, the CLI will ask for your permission before executing potentially dangerous operations such as:
- Writing or modifying files
- Executing code
- Running shell commands
- Running Python files

### Safe Operations
These operations are considered safe and don't require permission:
- Reading files
- Listing directory contents

### Bypassing Permission Prompts
You can disable permission prompts using the `--no-permission` flag, but this should be used with caution:

```bash
ollama-code-cli --no-permission "Your prompt here"
```

**Warning:** Disabling permission prompts allows the AI to execute operations without user confirmation. Only use this in trusted environments.

---

## Available Tools

- `read_file`: Read the contents of a file
- `write_file`: Write content to a file
- `execute_code`: Execute code in a subprocess
- `list_files`: List files in a directory
- `run_command`: Run a shell command

---

## Examples

**1. Create a Python script and save it to a file:**

```bash
ollama-code-cli "Create a Python script that calculates factorial and save it to a file named factorial.py"
```

**2. Read a file and explain its contents:**

```bash
ollama-code-cli "Read the contents of main.py and explain what it does"
```

**3. Execute a shell command:**

```bash
ollama-code-cli "List all files in the current directory"
```

---

## Interactive Mode

Launch the interactive mode for a conversational experience:

```bash
ollama-code-cli
```

In interactive mode, you can:

- Have multi-turn conversations with the AI
- See elegantly formatted responses with Markdown support
- Watch tool calls and results in real-time with visual panels
- Clear conversation history with the `clear` command
- Exit gracefully with the `exit` command

---

## Project Structure

```
ollama-code-cli/
├── ollama_code_cli/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── cli.py          # Main CLI interface
│   ├── tools/
│   │   ├── __init__.py
│   │   └── tool_manager.py # Tool implementations
├── pyproject.toml          # Project configuration
├── LICENSE
└── README.md
```

---

## Dependencies

- [Rich](https://github.com/Textualize/rich) — Elegant terminal formatting
- [Click](https://click.palletsprojects.com/) — Command-line interface
- [Ollama Python Client](https://github.com/ollama/ollama-python) — Ollama integration

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements, bug fixes, or suggestions.

---

## License

This project is licensed under the [MIT License](LICENSE).
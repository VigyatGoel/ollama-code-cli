# Ollama Code CLI

A beautiful, interactive command-line interface tool for coding tasks using local LLMs via Ollama with tool calling capabilities.

## Features

- 🎨 **Beautiful CLI Interface** - Rich colors and structured output
- 🤖 **Local AI Power** - Interact with local LLMs through Ollama
- 🛠️ **Tool Calling** - Execute coding-related tools (file operations, code execution, etc.)
- 💬 **Interactive Mode** - Maintain conversation context for multi-turn interactions
- 📝 **Markdown Support** - Beautifully formatted responses with syntax highlighting
- 📋 **Structured Output** - Clear panels and tables for tool calls and results

## Installation

```bash
pip install ollama-code-cli
```

## Usage

```bash
# Start an interactive session
ollama-code-cli

# Run a single command
ollama-code-cli "Create a Python function to calculate factorial"

# Use a specific model
ollama-code-cli --model llama3.1 "Explain how async/await works in Python"
```

## Available Tools

- `read_file`: Read the contents of a file
- `write_file`: Write content to a file
- `execute_code`: Execute code in a subprocess
- `list_files`: List files in a directory
- `run_command`: Run a shell command

## Examples

1. Create a Python script and save it to a file:
   ```bash
   ollama-code-cli "Create a Python script that calculates factorial and save it to a file named factorial.py"
   ```

2. Read a file and explain its contents:
   ```bash
   ollama-code-cli "Read the contents of main.py and explain what it does"
   ```

3. Execute a shell command:
   ```bash
   ollama-code-cli "List all files in the current directory"
   ```

## Interactive Mode

Launch the interactive mode for a conversational experience:

```bash
ollama-code-cli
```

In interactive mode, you can:
- Have multi-turn conversations with the AI
- See beautiful formatted responses with Markdown support
- Watch tool calls and results in real-time with visual panels
- Clear conversation history with the `clear` command
- Exit gracefully with the `exit` command

## Project Structure

```
ollamacode/
├── ollamacode/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── cli.py          # Main CLI interface
│   ├── tools/
│   │   ├── __init__.py
│   │   └── tool_manager.py # Tool implementations
├── pyproject.toml          # Project configuration
└── README.md
```

## Installation

First, install a compatible model in Ollama:
```bash
# Choose one of these models:
ollama pull qwen3
ollama pull llama3.1
```

Then install the CLI:
```bash
pip install ollama-code-cli
```

## Requirements

- Python 3.13+
- Ollama installed and running
- An Ollama model that supports tool calling (e.g., Qwen3, Llama3.1+)

## Dependencies

- [Rich](https://github.com/Textualize/rich) - For beautiful terminal formatting
- [Click](https://click.palletsprojects.com/) - For command-line interface
- [Ollama Python Client](https://github.com/ollama/ollama-python) - For Ollama integration
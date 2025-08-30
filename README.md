# Ollama Code CLI

A beautiful, interactive command-line interface tool for coding tasks using local LLMs via Ollama with tool calling capabilities.

## Features

- 🎨 **Beautiful CLI Interface** - Rich colors, animations, and structured output
- 🤖 **Local AI Power** - Interact with local LLMs through Ollama
- 🛠️ **Tool Calling** - Execute coding-related tools (file operations, code execution, etc.)
- 💬 **Interactive Mode** - Maintain conversation context for multi-turn interactions
- 📝 **Markdown Support** - Beautifully formatted responses with syntax highlighting
- ⏳ **Animations** - Visual feedback with spinners during processing
- 📋 **Structured Output** - Clear panels and tables for tool calls and results

## Installation

```bash
pip install ollamacode
```

## Usage

```bash
# Start an interactive session
ollama-code

# Run a single command
ollama-code "Create a Python function to calculate factorial"

# Use a specific model
ollama-code --model qwen3:1.7b "Explain how async/await works in Python"
```

## Usage

```bash
# Start an interactive session
ollama-code

# Run a single command
ollama-code "Create a Python function to calculate factorial"

# Use a specific model
ollama-code --model qwen3:1.7b "Explain how async/await works in Python"
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
   ollama-code "Create a Python script that calculates factorial and save it to a file named factorial.py"
   ```

2. Read a file and explain its contents:
   ```bash
   ollama-code "Read the contents of main.py and explain what it does"
   ```

3. Execute a shell command:
   ```bash
   ollama-code "List all files in the current directory"
   ```

## Interactive Mode

Launch the interactive mode for a conversational experience:

```bash
ollama-code
```

In interactive mode, you can:
- Have multi-turn conversations with the AI
- See beautiful formatted responses with Markdown support
- Watch tool calls and results in real-time with visual panels
- Clear conversation history with the `clear` command
- Exit gracefully with the `exit` command

## Project Structure

```
ollama_code/
├── ollama_code/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── cli.py          # Main CLI interface
│   ├── tools/
│   │   ├── __init__.py
│   │   └── tool_manager.py # Tool implementations
│   └── utils/
│       └── __init__.py
├── main.py                 # Entry point
├── pyproject.toml          # Project configuration
└── README.md
```

## Requirements

- Python 3.13+
- Ollama installed and running
- An Ollama model that supports tool calling (e.g., Qwen3, Llama3.1+)

## Dependencies

- [Rich](https://github.com/Textualize/rich) - For beautiful terminal formatting
- [Yaspin](https://github.com/pavdmyt/yaspin) - For terminal spinners
- [Click](https://click.palletsprojects.com/) - For command-line interface
- [Ollama Python Client](https://github.com/ollama/ollama-python) - For Ollama integration
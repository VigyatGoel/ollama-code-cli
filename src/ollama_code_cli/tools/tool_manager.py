"""
Tool implementations for the Ollama Code CLI.
"""

import json
import os
import subprocess
import sys
import tempfile
from typing import Dict, Any
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel


class ToolManager:
    """Manager for all available tools."""

    def __init__(self, require_permission: bool = True):
        self.tools = self._initialize_tools()
        self.require_permission = require_permission
        self.console = Console()

    def _initialize_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available tools for the LLM."""
        return {
            "read_file": {
                "function": self._read_file,
                "description": "Read the contents of a file",
                "requires_permission": False,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file to read",
                        }
                    },
                    "required": ["filepath"],
                },
            },
            "write_file": {
                "function": self._write_file,
                "description": "Write content to a file",
                "requires_permission": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file to write",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file",
                        },
                    },
                    "required": ["filepath", "content"],
                },
            },
            "execute_code": {
                "function": self._execute_code,
                "description": "Execute code in a subprocess",
                "requires_permission": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to execute"},
                        "language": {
                            "type": "string",
                            "description": "Programming language (python, javascript, etc.)",
                            "default": "python",
                        },
                    },
                    "required": ["code"],
                },
            },
            "list_files": {
                "function": self._list_files,
                "description": "List files in a directory",
                "requires_permission": False,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list files in",
                            "default": ".",
                        }
                    },
                },
            },
            "run_command": {
                "function": self._run_command,
                "description": "Run a shell command",
                "requires_permission": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to execute",
                        }
                    },
                    "required": ["command"],
                },
            },
            "run_python_file": {
                "function": self._run_python_file,
                "description": "Run an existing Python file",
                "requires_permission": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the Python file to execute",
                        }
                    },
                    "required": ["filepath"],
                },
            },
        }

    def _ask_permission(self, tool_name: str, details: str) -> bool:
        """Ask user for permission to execute a potentially dangerous operation."""
        if not self.require_permission:
            return True

        warning_panel = Panel(
            f"[bold yellow]⚠️  Permission Required[/bold yellow]\n\n"
            f"[bold]Tool:[/bold] {tool_name}\n"
            f"[bold]Action:[/bold] {details}\n\n"
            f"[dim]This operation may modify your system or files.[/dim]",
            title="🔒 Security Check",
            border_style="yellow",
        )
        self.console.print(warning_panel)

        return Confirm.ask(
            "[bold blue]Do you want to proceed?[/bold blue]", default=False
        )

    def _read_file(self, filepath: str) -> Dict[str, Any]:
        """Read a file and return its contents."""
        if not filepath or not isinstance(filepath, str):
            return {
                "status": "error",
                "message": "Invalid filepath provided",
            }

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "status": "success",
                "content": content,
                "message": f"Successfully read {filepath}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read {filepath}: {str(e)}",
            }

    def _write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        if not filepath or not isinstance(filepath, str):
            return {
                "status": "error",
                "message": "Invalid filepath provided",
            }

        if content is None or not isinstance(content, str):
            return {
                "status": "error",
                "message": "Invalid content provided",
            }

        # Ask for permission before writing file
        file_exists = os.path.exists(filepath)
        action_desc = f"{'Overwrite' if file_exists else 'Create'} file: {filepath}"
        if not self._ask_permission("write_file", action_desc):
            return {
                "status": "cancelled",
                "message": "File write operation cancelled by user",
            }

        try:
            directory = os.path.dirname(filepath) or "."
            if directory != ".":
                os.makedirs(directory, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return {"status": "success", "message": f"Successfully wrote to {filepath}"}
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to write to {filepath}: {str(e)}",
            }

    def _execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Execute code in a subprocess."""
        if not code or not isinstance(code, str):
            return {
                "status": "error",
                "message": "Invalid code provided",
            }

        if not language or not isinstance(language, str):
            return {
                "status": "error",
                "message": "Invalid language provided",
            }

        if not code.strip():
            return {
                "status": "error",
                "message": "No code provided to execute",
            }

        # Ask for permission before executing code
        code_preview = code[:100] + "..." if len(code) > 100 else code
        action_desc = f"Execute {language} code:\n{code_preview}"
        if not self._ask_permission("execute_code", action_desc):
            return {
                "status": "cancelled",
                "message": "Code execution cancelled by user",
            }

        temp_file = None
        try:
            if language == "python":
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as f:
                    f.write(code)
                    temp_file = f.name

                # Get current working directory and environment
                current_dir = os.getcwd()
                env = os.environ.copy()

                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=current_dir,
                    env=env,
                )

                return {
                    "status": "success" if result.returncode == 0 else "error",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "message": "Code executed successfully"
                    if result.returncode == 0
                    else f"Code execution failed with return code {result.returncode}",
                }
            else:
                return {
                    "status": "error",
                    "message": f"Language '{language}' not supported for execution",
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Code execution timed out (30s limit)",
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to execute code: {str(e)}"}
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass  # Ignore cleanup errors

    def _list_files(self, path: str = ".") -> Dict[str, Any]:
        """List files in a directory."""
        if not path or not isinstance(path, str):
            return {
                "status": "error",
                "message": "Invalid path provided",
            }

        try:
            files = os.listdir(path)
            return {
                "status": "success",
                "files": files,
                "message": f"Listed files in {path}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list files in {path}: {str(e)}",
            }

    def _run_command(self, command: str) -> Dict[str, Any]:
        """Run a shell command."""
        if not command or not isinstance(command, str):
            return {
                "status": "error",
                "message": "Invalid command provided",
            }

        if not command.strip():
            return {
                "status": "error",
                "message": "No command provided to execute",
            }

        # Ask for permission before running shell command
        action_desc = f"Execute shell command: {command}"
        if not self._ask_permission("run_command", action_desc):
            return {
                "status": "cancelled",
                "message": "Shell command execution cancelled by user",
            }

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command execution timed out"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to run command: {str(e)}"}

    def _run_python_file(self, filepath: str) -> Dict[str, Any]:
        """Run an existing Python file."""
        if not filepath or not isinstance(filepath, str):
            return {
                "status": "error",
                "message": "Invalid filepath provided",
            }

        if not os.path.exists(filepath):
            return {
                "status": "error",
                "message": f"File not found: {filepath}",
            }

        if not filepath.endswith(".py"):
            return {
                "status": "error",
                "message": f"File is not a Python file: {filepath}",
            }

        # Ask for permission before running Python file
        action_desc = f"Execute Python file: {filepath}"
        if not self._ask_permission("run_python_file", action_desc):
            return {
                "status": "cancelled",
                "message": "Python file execution cancelled by user",
            }

        try:
            current_dir = os.getcwd()
            env = os.environ.copy()

            result = subprocess.run(
                [sys.executable, filepath],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=current_dir,
                env=env,
            )

            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "message": f"Python file executed successfully: {filepath}"
                if result.returncode == 0
                else f"Python file execution failed with return code {result.returncode}: {filepath}",
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": f"Python file execution timed out (30s limit): {filepath}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to run Python file {filepath}: {str(e)}",
            }

    def get_tools_for_ollama(self) -> list:
        """Format tools for Ollama API."""
        tools = []
        for name, tool in self.tools.items():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": tool["description"],
                        "parameters": tool["parameters"],
                    },
                }
            )
        return tools

    def handle_tool_calls(self, tool_calls: list) -> list:
        """Handle tool calls from the LLM."""
        results = []
        for tool_call in tool_calls:
            name = tool_call.get("function", {}).get("name")
            arguments = tool_call.get("function", {}).get("arguments", {})

            # Handle case where arguments come as JSON string from LLM
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError as e:
                    results.append(
                        {
                            "role": "tool",
                            "content": json.dumps(
                                {
                                    "status": "error",
                                    "message": f"Invalid JSON arguments: {str(e)}",
                                }
                            ),
                            "name": name or "unknown",
                        }
                    )
                    continue

            # Ensure arguments is a dictionary
            if not isinstance(arguments, dict):
                results.append(
                    {
                        "role": "tool",
                        "content": json.dumps(
                            {
                                "status": "error",
                                "message": f"Arguments must be a dictionary, got {type(arguments)}",
                            }
                        ),
                        "name": name or "unknown",
                    }
                )
                continue

            if name in self.tools:
                try:
                    result = self.tools[name]["function"](**arguments)
                    results.append(
                        {"role": "tool", "content": json.dumps(result), "name": name}
                    )
                except TypeError as e:
                    # Handle case where argument names don't match function parameters
                    results.append(
                        {
                            "role": "tool",
                            "content": json.dumps(
                                {
                                    "status": "error",
                                    "message": f"Invalid arguments for {name}: {str(e)}",
                                }
                            ),
                            "name": name,
                        }
                    )
                except Exception as e:
                    results.append(
                        {
                            "role": "tool",
                            "content": json.dumps(
                                {
                                    "status": "error",
                                    "message": f"Tool execution failed: {str(e)}",
                                }
                            ),
                            "name": name,
                        }
                    )
            else:
                results.append(
                    {
                        "role": "tool",
                        "content": json.dumps(
                            {"status": "error", "message": f"Unknown tool: {name}"}
                        ),
                        "name": name or "unknown",
                    }
                )
        return results

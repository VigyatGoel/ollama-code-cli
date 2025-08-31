"""
Tool implementations for the Ollama Code CLI.
"""

import json
import os
import subprocess
import sys
import tempfile
from typing import Dict, Any


class ToolManager:
    """Manager for all available tools."""

    def __init__(self):
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available tools for the LLM."""
        return {
            "read_file": {
                "function": self._read_file,
                "description": "Read the contents of a file",
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
        }

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

        try:
            if language == "python":
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as f:
                    f.write(code)
                    temp_file = f.name

                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                os.unlink(temp_file)

                return {
                    "status": "success",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                }
            else:
                return {
                    "status": "error",
                    "message": f"Language '{language}' not supported for execution",
                }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Code execution timed out"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to execute code: {str(e)}"}

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

            if name in self.tools:
                try:
                    result = self.tools[name]["function"](**arguments)
                    results.append(
                        {"role": "tool", "content": json.dumps(result), "name": name}
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
                        "name": name,
                    }
                )
        return results

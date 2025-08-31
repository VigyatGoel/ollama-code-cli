"""
CLI interface for the Ollama Code CLI.
"""

import click
import json
import re
from typing import Optional
from ollama import Client
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from yaspin import yaspin
from ollamacode.tools.tool_manager import ToolManager


class OllamaCodeCLI:
    """Main CLI class for Ollama Code."""

    def __init__(self, model: str = "qwen3:4b"):
        self.model = model
        self.client = Client()
        self.conversation_history = []
        self.tool_manager = ToolManager()
        self.console = Console()

    def _print_welcome_message(self):
        """Print a welcome message with animation."""
        welcome_text = Text("Ollama Code CLI", style="bold blue")
        subtitle = Text("Your AI-powered coding assistant", style="italic green")

        self.console.print("\n")
        self.console.print(welcome_text, justify="center")
        self.console.print(subtitle, justify="center")

        model_panel = Panel(
            f"Using model: [bold cyan]{self.model}[/bold cyan]",
            title="Model Info",
            border_style="bright_black",
        )
        self.console.print(model_panel)

        table = Table(
            title="Available Tools", show_header=True, header_style="bold magenta"
        )
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        for name, tool in self.tool_manager.tools.items():
            table.add_row(name, tool["description"])

        self.console.print(table)
        self.console.print("\n")

    def _print_tool_call(self, tool_name: str, arguments: dict):
        """Print a tool call with animation."""
        tool_panel = Panel(
            f"[bold green]Tool:[/bold green] {tool_name}\n[bold yellow]Arguments:[/bold yellow] {json.dumps(arguments, indent=2)}",
            title="🔧 Tool Call",
            border_style="green",
        )
        self.console.print(tool_panel)

    def _print_tool_result(self, tool_name: str, result: dict):
        """Print a tool result with styling."""
        if result.get("status") == "success":
            result_panel = Panel(
                f"[bold green]✓ Success:[/bold green] {result.get('message', 'Tool executed successfully')}",
                title="✅ Tool Result",
                border_style="green",
            )
        else:
            result_panel = Panel(
                f"[bold red]✗ Error:[/bold red] {result.get('message', 'Tool execution failed')}",
                title="❌ Tool Result",
                border_style="red",
            )

        self.console.print(result_panel)
        
        # Show output for code execution tools
        if tool_name in ["execute_code", "run_python_file", "run_command"]:
            if result.get("stdout"):
                output_panel = Panel(
                    result["stdout"],
                    title="📤 Output",
                    border_style="blue",
                )
                self.console.print(output_panel)
            
            if result.get("stderr"):
                error_panel = Panel(
                    result["stderr"],
                    title="⚠️ Error Output",
                    border_style="yellow",
                )
                self.console.print(error_panel)

    def chat(self, message: str) -> str:
        """Have a conversation with the LLM."""
        self.conversation_history.append({"role": "user", "content": message})

        if len(self.conversation_history) == 1:
            self.conversation_history.insert(
                0,
                {
                    "role": "system",
                    "content": """You are an expert coding assistant that helps users with programming tasks. 
You have access to several tools that can help you perform actions on the user's computer:

1. read_file: Read the contents of a file
2. write_file: Write content to a file
3. execute_code: Execute code in a subprocess
4. list_files: List files in a directory
5. run_command: Run a shell command
6. run_python_file: Run an existing Python file

When the user asks you to perform a task that requires one of these actions, use the appropriate tool. 
For example:
- If asked to read a file, use the read_file tool
- If asked to create or modify a file, use the write_file tool
- If asked to run code, use the execute_code tool
- If asked to list files in a directory, use the list_files tool
- If asked to run a shell command, use the run_command tool

CRITICAL GUIDELINES:
1. Only use tools when explicitly asked to perform an action that requires them
2. For general conversation, greetings, or questions that don't require file operations, code execution, etc., respond directly without using any tools
3. Never use tools for simple greetings like "hello" or "how are you"
4. Always think carefully about whether a tool is needed before calling it
5. If you're not sure if a tool is needed, it's better to respond directly without using tools

Examples of when NOT to use tools:
- "Hello" -> Respond directly with a greeting
- "How are you?" -> Respond directly
- "What is Python?" -> Explain directly
- "Can you help me with this code?" -> Ask for details, don't use tools yet

Examples of when TO use tools:
- "Read the contents of file.txt" -> Use read_file tool
- "Create a Python script that prints 'Hello World'" -> Use write_file tool
- "Run this Python code: print('Hello World')" -> Use execute_code tool
- "Run the file script.py" -> Use run_python_file tool
- "List all files in the current directory" -> Use list_files tool
- "Show me the contents of my home directory" -> Use list_files tool""",
                },
            )

        tools = self.tool_manager.get_tools_for_ollama()

        with yaspin(text="Thinking...", color="yellow"):
            response = self.client.chat(
                model=self.model, messages=self.conversation_history, tools=tools
            )

        message = response.message
        cleaned_content = re.sub(
            r"<think>.*?</think>\s*", "", message.content, flags=re.DOTALL
        )
        self.conversation_history.append(
            {"role": message.role, "content": cleaned_content}
        )

        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_call_message = {
                "role": message.role,
                "content": cleaned_content,
                "tool_calls": [],
            }

            for tool_call in message.tool_calls:
                tool_call_message["tool_calls"].append(
                    {
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        }
                    }
                )

                self._print_tool_call(
                    tool_call.function.name, tool_call.function.arguments
                )

            self.conversation_history[-1] = tool_call_message

            tool_results = self.tool_manager.handle_tool_calls(
                [
                    {
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in message.tool_calls
                ]
            )

            for result in tool_results:
                try:
                    result_data = json.loads(result["content"])
                    self._print_tool_result(result["name"], result_data)
                except Exception:
                    self._print_tool_result(
                        result["name"],
                        {"status": "success", "message": result["content"]},
                    )

            self.conversation_history.extend(tool_results)

            with yaspin(text="Processing results...", color="yellow"):
                response = self.client.chat(
                    model=self.model, messages=self.conversation_history, tools=tools
                )
            message = response.message
            cleaned_content = re.sub(
                r"<think>.*?</think>\s*", "", message.content, flags=re.DOTALL
            )
            self.conversation_history.append(
                {"role": message.role, "content": cleaned_content}
            )
            return cleaned_content

        return cleaned_content

    def interactive_mode(self):
        """Start an interactive chat session."""
        self._print_welcome_message()

        self.console.print(
            "[bold blue]Interactive Mode[/bold blue] | [italic]Type 'exit' to quit, 'clear' to reset conversation[/italic]"
        )
        self.console.print("=" * 60)

        while True:
            try:
                user_input = Prompt.ask("\n[bold green]You[/bold green]")

                if user_input.lower() == "exit":
                    self.console.print("[bold red]Goodbye! 👋[/bold red]")
                    break
                elif user_input.lower() == "clear":
                    self.conversation_history = []
                    self.console.print(
                        "[bold yellow]Conversation history cleared.[/bold yellow]"
                    )
                    continue
                elif not user_input:
                    continue

                response = self.chat(user_input)

                self.console.print("\n[bold cyan]Assistant[/bold cyan] 🤖")
                try:
                    md = Markdown(response)
                    self.console.print(md)
                except Exception:
                    self.console.print(response)

            except KeyboardInterrupt:
                self.console.print("\n[bold red]Exiting... 👋[/bold red]")
                break
            except Exception as e:
                self.console.print(f"\n[bold red]Error:[/bold red] {e}")


@click.command()
@click.option("--model", default="qwen3:4b", help="Ollama model to use")
@click.argument("prompt", required=False)
def main(model: str, prompt: Optional[str]):
    """Ollama Code CLI - A command-line tool for coding tasks using local LLMs with tool calling."""
    cli = OllamaCodeCLI(model=model)

    if prompt:
        with yaspin(text="Processing...", color="yellow"):
            response = cli.chat(prompt)
        try:
            md = Markdown(response)
            cli.console.print(md)
        except Exception:
            cli.console.print(response)
    else:
        cli.interactive_mode()


if __name__ == "__main__":
    main()

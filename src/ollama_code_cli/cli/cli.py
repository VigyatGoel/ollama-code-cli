"""
CLI interface for the Ollama Code CLI.
"""

import atexit
import click
import json
import re
import subprocess
from typing import Optional
from ollama import Client
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from yaspin import yaspin
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from ollama_code_cli.tools.tool_manager import ToolManager


class OllamaCodeCLI:
    """Main CLI class for Ollama Code."""

    def __init__(self, model: str = "qwen3:4b", require_permission: bool = True):
        self.model = model
        self.client = Client()
        self.conversation_history = []
        self.tool_manager = ToolManager(require_permission=require_permission)
        self.console = Console()
        self.prompt_history = InMemoryHistory()  # Add history for prompt_toolkit

        atexit.register(self._stop_ollama_model)

    def _stop_ollama_model(self):
        """Stop the Ollama model using subprocess."""
        try:
            subprocess.run(
                ["ollama", "stop", self.model],
                check=False,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                ["ollama", "stop"], check=False, capture_output=True, text=True
            )
        except Exception:
            pass

    def _clean_message_content(self, content: str) -> str:
        """Clean message content by removing <think> tags."""
        return re.sub(r"<think>.*?</think>\s*", "", content, flags=re.DOTALL)

    def _render_response(self, response: str):
        """Render response with markdown formatting and error handling."""
        if response.strip():
            try:
                md = Markdown(response)
                self.console.print(md)
            except Exception:
                self.console.print(response)

    def _convert_tool_calls_to_dict(self, tool_calls):
        """Convert tool calls to dictionary format."""
        return [
            {
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
            }
            for tc in tool_calls
        ]

    def _print_welcome_message(self):
        """Print a welcome message with animation."""
        self.console.print("\n" * 2)

        # Header with better styling
        welcome_text = Text("Ollama Code CLI", style="bold cyan")
        subtitle = Text("Your AI-powered coding assistant", style="italic green")

        self.console.print(welcome_text, justify="center")
        self.console.print(subtitle, justify="center")
        self.console.print("\n")

        # Model info section with improved styling
        permission_status = (
            "[bold red]DISABLED[/bold red]"
            if not self.tool_manager.require_permission
            else "[bold green]ENABLED[/bold green]"
        )

        model_panel = Panel(
            f"[bold white]Using model:[/bold white] [bold cyan]{self.model}[/bold cyan]\n"
            f"[bold white]Permission prompts:[/bold white] {permission_status}",
            title="[bold blue]Model Info[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
        self.console.print(model_panel)
        self.console.print()

        # Tools table with better formatting
        table = Table(
            title="[bold magenta]Available Tools[/bold magenta]",
            show_header=True,
            header_style="bold white",
            border_style="magenta",
            title_style="bold magenta",
            padding=(0, 1),
            show_lines=True,  # Remove internal lines to fix visual issues
            box=box.ROUNDED,  # Use rounded box style
        )

        # Adjust column widths for better display
        table.add_column("Tool", style="bold cyan", no_wrap=False, width=None)
        table.add_column("Description", style="white", no_wrap=False, width=None)
        table.add_column(
            "Requires Permission", no_wrap=True, width=None, justify="center"
        )

        for name, tool in self.tool_manager.tools.items():
            requires_permission = (
                "[bold red]Yes[/bold red]"
                if tool.get("requires_permission", False)
                else "[bold green]No[/bold green]"
            )
            # Ensure tool description doesn't get too long
            description = tool["description"]
            if len(description) > 35:
                description = description[:32] + "..."

            table.add_row(name, description, requires_permission)

        self.console.print(table)
        self.console.print("\n" * 2)

    def _print_tool_call(self, tool_name: str, arguments: dict):
        """Print a tool call with improved styling."""
        args_formatted = json.dumps(arguments, indent=2)
        tool_panel = Panel(
            f"[bold green]Tool:[/bold green] [bold white]{tool_name}[/bold white]\n"
            f"[bold yellow]Arguments:[/bold yellow]\n[dim]{args_formatted}[/dim]",
            title="[bold blue]🔧 Tool Call[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
        self.console.print(tool_panel)

    def _print_tool_result(self, tool_name: str, result: dict):
        """Print a tool result with improved styling."""
        if result.get("status") == "success":
            result_panel = Panel(
                f"[bold green]✓ Success:[/bold green] {result.get('message', 'Tool executed successfully')}",
                title="[bold green]✅ Tool Result[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        elif result.get("status") == "cancelled":
            result_panel = Panel(
                f"[bold yellow]⚠️ Cancelled:[/bold yellow] {result.get('message', 'Operation cancelled by user')}",
                title="[bold yellow]🚫 Tool Cancelled[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
        else:
            result_panel = Panel(
                f"[bold red]✗ Error:[/bold red] {result.get('message', 'Tool execution failed')}",
                title="[bold red]❌ Tool Error[/bold red]",
                border_style="red",
                padding=(1, 2),
            )

        self.console.print(result_panel)

        # Show output for code execution tools with better formatting
        if tool_name in ["execute_code", "run_python_file", "run_command"]:
            if result.get("stdout"):
                output_panel = Panel(
                    f"[dim]{result['stdout']}[/dim]",
                    title="[bold blue]📤 Output[/bold blue]",
                    border_style="blue",
                    padding=(1, 2),
                )
                self.console.print(output_panel)

            if result.get("stderr"):
                error_panel = Panel(
                    f"[bold red]{result['stderr']}[/bold red]",
                    title="[bold yellow]⚠️ Error Output[/bold yellow]",
                    border_style="yellow",
                    padding=(1, 2),
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
                    "content": """You are an expert coding assistant with access to powerful tools for file operations, code execution, and system commands.

AVAILABLE TOOLS:
- read_file: Read the contents of any file
- write_file: Create or modify files (requires permission)
- execute_code: Run code in a subprocess (requires permission)
- list_files: List directory contents
- run_command: Execute shell commands (requires permission)
- run_python_file: Run existing Python files (requires permission)

IMPORTANT TOOL USAGE RULES:
1. ALWAYS use tools when the user asks for file operations, code execution, or system commands
2. When asked to "create a file", "write code to a file", or "save to a file" - IMMEDIATELY use the write_file tool
3. When asked to "run code", "execute this", or "test this code" - use the execute_code tool
4. When asked to "read a file" or "show me the contents" - use the read_file tool
5. When asked to "list files" or "show me what's in this directory" - use the list_files tool
6. When asked to run shell commands - use the run_command tool

CRITICAL: Do NOT just describe what you would do - ACTUALLY DO IT using the appropriate tools!

EXAMPLES OF CORRECT BEHAVIOR:
- User: "Create a todo app in HTML" → USE write_file tool to create the file
- User: "Run this Python code" → USE execute_code tool to run it
- User: "List files in current directory" → USE list_files tool
- User: "Read config.txt" → USE read_file tool

If you need permission for dangerous operations, the system will handle that automatically.

Always be action-oriented and use tools when requested!""",
                },
            )

        tools = self.tool_manager.get_tools_for_ollama()

        with yaspin(text="Thinking...", color="yellow"):
            response = self.client.chat(
                model=self.model, messages=self.conversation_history, tools=tools
            )

        message = response.message
        cleaned_content = self._clean_message_content(message.content)
        self.conversation_history.append(
            {"role": message.role, "content": cleaned_content}
        )

        # Enhanced response processing to detect when tools should have been called
        if hasattr(message, "tool_calls") and message.tool_calls:
            self.console.print(
                f"[dim]Processing {len(message.tool_calls)} tool call(s)[/dim]"
            )
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
                self._convert_tool_calls_to_dict(message.tool_calls)
            )

            # Check if any tool was cancelled due to permission denial
            permission_denied = False
            for result in tool_results:
                try:
                    result_data = json.loads(result["content"])
                    self._print_tool_result(result["name"], result_data)
                    # Check if user denied permission
                    if result_data.get("status") == "cancelled":
                        permission_denied = True
                except Exception:
                    result_data = {"status": "success", "message": result["content"]}
                    self._print_tool_result(result["name"], result_data)

            if permission_denied:
                return ""

            self.conversation_history.extend(tool_results)

            with yaspin(text="Processing results...", color="yellow"):
                response = self.client.chat(
                    model=self.model, messages=self.conversation_history, tools=tools
                )
            message = response.message
            cleaned_content = self._clean_message_content(message.content)
            self.conversation_history.append(
                {"role": message.role, "content": cleaned_content}
            )
            return cleaned_content

        # Check if the model should have used tools but didn't
        self._validate_tool_usage(cleaned_content)

        return cleaned_content

    def _validate_tool_usage(self, response: str):
        """Validate if tools should have been used but weren't."""
        if len(self.conversation_history) >= 2:
            user_msg = self.conversation_history[-2].get("content", "")
        else:
            return

        action_keywords = [
            "create",
            "write",
            "save",
            "make",
            "generate",
            "build",
            "run",
            "execute",
            "test",
            "read",
            "show",
            "list",
            "display",
        ]

        file_keywords = ["file", "script", "code", "html", "css", "js", "python", "txt"]

        user_lower = user_msg.lower()

        if any(action in user_lower for action in action_keywords[:5]) and any(
            file_type in user_lower for file_type in file_keywords
        ):
            if "write_file" not in response and "I'll create" not in response:
                warning_panel = Panel(
                    "It looks like you wanted me to create a file. Let me use the write_file tool to actually create it.",
                    title="[bold yellow]⚠️  Note[/bold yellow]",
                    border_style="yellow",
                    padding=(1, 2),
                )
                self.console.print(warning_panel)

    def interactive_mode(self):
        """Start an interactive chat session."""
        self._print_welcome_message()

        # Interactive mode header with better styling
        mode_panel = Panel(
            "[bold white]Interactive Mode[/bold white]\n"
            "[italic]Type 'exit' to quit, 'clear' to reset conversation[/italic]",
            title="[bold green]🚀 Ready to Start[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
        self.console.print(mode_panel)

        # Permission warning with better styling
        if self.tool_manager.require_permission:
            permission_panel = Panel(
                "[dim]You will be prompted before any potentially dangerous operations.[/dim]",
                title="[bold blue]ℹ️  Info[/bold blue]",
                border_style="blue",
                padding=(0, 2),
            )
            self.console.print(permission_panel)
        else:
            warning_panel = Panel(
                "[bold red]Permission prompts are disabled. Operations will execute without confirmation.[/bold red]",
                title="[bold red]⚠️  Warning[/bold red]",
                border_style="red",
                padding=(0, 2),
            )
            self.console.print(warning_panel)

        self.console.print()
        self.console.rule("[bold cyan]Chat Session[/bold cyan]", style="cyan")
        self.console.print()

        while True:
            try:
                # Use prompt_toolkit for better readline support with arrow keys
                self.console.print()
                user_input = pt_prompt(
                    "You: ",
                    history=self.prompt_history,
                    auto_suggest=AutoSuggestFromHistory(),
                ).strip()

                if user_input.lower() == "exit":
                    self.console.print("\n[bold cyan]Goodbye! 👋[/bold cyan]")
                    self._stop_ollama_model()  # Stop model before exiting
                    break
                elif user_input.lower() == "clear":
                    self.conversation_history = []
                    self.console.print(
                        "[bold yellow]✨ Conversation history cleared.[/bold yellow]"
                    )
                    continue
                elif not user_input:
                    continue

                response = self.chat(user_input)

                if response.strip():
                    self.console.print("\n[bold cyan]Assistant[/bold cyan] 🤖")
                    self._render_response(response)

            except KeyboardInterrupt:
                self.console.print("\n[bold cyan]Exiting... 👋[/bold cyan]")
                self._stop_ollama_model()  # Stop model before exiting
                break
            except Exception as e:
                self.console.print(f"\n[bold red]Error:[/bold red] {e}")


@click.command()
@click.option("--model", default="qwen3:4b", help="Ollama model to use")
@click.option(
    "--no-permission",
    is_flag=True,
    default=False,
    help="Skip permission prompts for dangerous operations (use with caution)",
)
@click.argument("prompt", required=False)
def main(model: str, no_permission: bool, prompt: Optional[str]):
    """Ollama Code CLI - A command-line tool for coding tasks using local LLMs with tool calling."""
    cli = OllamaCodeCLI(model=model, require_permission=not no_permission)

    if prompt:
        with yaspin(text="Processing...", color="yellow"):
            response = cli.chat(prompt)
        if response.strip():
            try:
                md = Markdown(response)
                cli.console.print(md)
            except Exception:
                cli.console.print(response)
        cli._stop_ollama_model()
    else:
        cli.interactive_mode()


if __name__ == "__main__":
    main()

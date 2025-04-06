"""
Utility functions for Claude Code Manager.
"""

import os
import time
import tempfile
import subprocess
from typing import List, Dict, Any, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


# Initialize rich console
console = Console()


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_table(title: str, data: List[Dict[str, Any]], columns: List[Dict[str, str]]) -> None:
    """
    Print a table of data.
    
    Args:
        title: Table title
        data: List of dictionaries containing data
        columns: List of column definitions with keys and headers
    """
    table = Table(title=title)
    
    # Add columns
    for column in columns:
        table.add_column(column["header"], style=column.get("style", ""))
    
    # Add rows
    for row_data in data:
        row = [str(row_data.get(col["key"], "")) for col in columns]
        table.add_row(*row)
    
    console.print(table)


def display_environment_details(env_data: Dict[str, Any], config_manager=None) -> None:
    """
    Display detailed information about an environment.
    
    Args:
        env_data: Environment data
        config_manager: Optional configuration manager to get claude.md content
    """
    console.print(Panel.fit(
        f"[bold]Environment:[/bold] {env_data.get('name', 'Unknown')}\n"
        f"[bold]Description:[/bold] {env_data.get('description', '')}\n"
        f"[bold]Created:[/bold] {env_data.get('created_at', 'Unknown')}\n"
    ))
    
    # Repositories
    if "repositories" in env_data and env_data["repositories"]:
        console.print("[bold]Repositories:[/bold]")
        for repo in env_data["repositories"]:
            console.print(f"  • {repo.get('url')} → {repo.get('path', '.')}")
    
    # Scaffold commands
    if "scaffold_commands" in env_data and env_data["scaffold_commands"]:
        console.print("[bold]Scaffold Commands:[/bold]")
        for cmd in env_data["scaffold_commands"]:
            console.print(f"  • {cmd.get('command', '')}")
    
    # Claude.md content preview
    if config_manager:
        claude_md_content = config_manager.get_claude_md_template(env_data.get('name', ''))
        if claude_md_content:
            preview = (claude_md_content[:100] + "...") if len(claude_md_content) > 100 else claude_md_content
            console.print("[bold]Claude.md Content:[/bold]")
            console.print(f"  {preview}")


def open_editor(initial_content: str = "") -> Optional[str]:
    """
    Open a text editor for the user to edit content.
    
    Args:
        initial_content: Initial content to populate the editor with
        
    Returns:
        Edited content or None if cancelled
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w+", delete=False) as temp_file:
        temp_file.write(initial_content)
        temp_path = temp_file.name
    
    try:
        # Determine which editor to use
        editor = os.environ.get("EDITOR", "vi")
        
        # Open the editor
        subprocess.run([editor, temp_path], check=True)
        
        # Read the content back
        with open(temp_path, "r") as f:
            content = f.read()
        
        return content
    except subprocess.CalledProcessError:
        print_error("Editor exited with an error")
        return None
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)


def with_spinner(message: str, func: Callable, *args, **kwargs) -> Any:
    """
    Run a function with a spinner.
    
    Args:
        message: Message to display while spinning
        func: Function to run
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The return value of the function
    """
    with console.status(message) as status:
        return func(*args, **kwargs)


def format_time_ago(timestamp: str) -> str:
    """
    Format a timestamp as a human-readable time ago.
    
    Args:
        timestamp: ISO format timestamp
        
    Returns:
        Human-readable string of time ago
    """
    try:
        # Parse timestamp
        timestamp_seconds = time.mktime(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f"))
        now = time.time()
        seconds_ago = now - timestamp_seconds
        
        # Format based on time difference
        if seconds_ago < 60:
            return "just now"
        elif seconds_ago < 3600:
            minutes = int(seconds_ago / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds_ago < 86400:
            hours = int(seconds_ago / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds_ago / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
    except (ValueError, TypeError):
        return "unknown time"
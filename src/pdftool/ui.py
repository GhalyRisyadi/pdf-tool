"""Rich Terminal UI Helper for PDFtool."""

from contextlib import contextmanager
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "primary": "bold blue",
    "dim": "bright_black",
    "accent": "magenta",
})

console = Console(theme=custom_theme)
error_console = Console(stderr=True, theme=custom_theme)


def print_banner(subtitle: str = "100% Offline & Private Document Processing"):
    """Displays modern branded banner for PDFtool."""
    banner_content = (
        "[bold cyan]  ____  ____  _____ _                 _ [/bold cyan]\n"
        "[bold cyan] |  _ \\|  _ \\|  ___| |_ ___   ___  | |[/bold cyan]\n"
        "[bold blue] | |_) | | | | |_  | __/ _ \\ / _ \\ | |[/bold blue]\n"
        "[bold blue] |  __/| |_| |  _| | || (_) | (_) || |[/bold blue]\n"
        "[bold magenta] |_|   |____/|_|    \\__\\___/ \\___/ |_|[/bold magenta]\n\n"
        f"[dim]{subtitle}[/dim]"
    )
    console.print(Panel(banner_content, border_style="cyan", expand=False, padding=(0, 2)))


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]![/bold yellow] {message}")


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    error_console.print(f"[bold red]✗[/bold red] {message}")


def print_info(message: str) -> None:
    """Print an informational message."""
    console.print(f"[bold cyan]ℹ[/bold cyan] {message}")


def print_key_value_table(title: str, data: Dict[str, Any]) -> None:
    """Print a clean key-value table."""
    table = Table(title=title, show_header=True, header_style="bold magenta", border_style="dim")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    for key, value in data.items():
        table.add_row(str(key), str(value))

    console.print(table)


@contextmanager
def status_spinner(description: str = "Processing..."):
    """Show a rich animated spinner during long operations."""
    with console.status(f"[bold cyan]{description}[/bold cyan]", spinner="dots") as status:
        yield status

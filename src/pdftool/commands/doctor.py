"""Environment diagnostics command."""

import typer

from ..dependencies import project_dependencies, system_dependencies


def doctor_cmd() -> None:
    typer.echo("pdftool environment check\n")
    typer.echo("Python packages:")
    for status in project_dependencies():
        mark = "✓" if status.installed else "✗"
        typer.echo(f"  {mark} {status.name}")

    typer.echo("\nSystem tools:")
    for status in system_dependencies():
        mark = "✓" if status.installed else "✗"
        typer.echo(f"  {mark} {status.name}")
